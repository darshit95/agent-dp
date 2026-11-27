from __future__ import annotations

from dataclasses import dataclass

import pytest

from cardbudget.categorization.profiles import CategorizationProfile
from cardbudget.categorization.provider import LLMClassification, ProviderUnavailable
from cardbudget.categorization.worker import CategorizationWorker
from cardbudget.config import Settings

from tests.unit.test_categorization_and_budgets import _seed_account_and_transactions


def test_rules_only_classifies_high_confidence_without_model(test_stack, monkeypatch):
    _settings, _store, db, services, _client = test_stack
    _seed_account_and_transactions(db)
    with db.transaction() as conn:
        conn.execute("UPDATE transactions SET pfc_confidence = 'HIGH' WHERE transaction_id = 'tx-posted'")

    def unexpected_model(*args):
        pytest.fail("Rules-only categorization attempted to construct a model client")

    monkeypatch.setattr(services.providers, "client", unexpected_model)
    services.categorization_worker.request()
    assert services.categorization_worker.run_once()
    row = services.transactions.get("tx-posted")
    assert (row.bucket_name, row.classification_source) == ("Shopping", "plaid_rule")
    assert services.transactions.get("tx-pending").bucket_id is None
    assert services.categorization_worker.status() == "complete"


def test_memory_pause_is_retryable_and_late_write_respects_manual_edit(test_stack, monkeypatch):
    _settings, _store, db, services, _client = test_stack
    _seed_account_and_transactions(db)
    services.providers.save(CategorizationProfile(provider="ollama", model="example"))
    grocery = next(bucket for bucket in services.buckets.list_active() if bucket.name == "Grocery")

    class ConcurrentEdit:
        def classify(self, **kwargs):
            services.categorization.manual_assign("tx-posted", grocery.id, False)
            return LLMClassification("Shopping", 1.0)

    monkeypatch.setattr(services.providers, "client", lambda *args: ConcurrentEdit())
    monkeypatch.setattr("cardbudget.categorization.service._memory_is_tight", lambda: True)
    services.categorization_worker.request()
    assert services.categorization_worker.run_once()
    assert services.categorization_worker.status() == "memory_paused"
    assert services.transactions.get("tx-posted").classification_source == "rules_unmatched"

    monkeypatch.setattr("cardbudget.categorization.service._memory_is_tight", lambda: False)
    services.categorization_worker.request()
    assert services.categorization_worker.run_once()
    row = services.transactions.get("tx-posted")
    assert (row.bucket_name, row.classification_source) == ("Grocery", "manual")


def test_cloud_selection_is_manual_and_deduplicates_shared_inputs(test_stack, monkeypatch):
    _settings, _store, db, services, _client = test_stack
    _seed_account_and_transactions(db)
    with db.transaction() as conn:
        conn.execute("UPDATE transactions SET pending = 0 WHERE transaction_id = 'tx-pending'")
        conn.execute("UPDATE transactions SET description = 'card number never sent' WHERE transaction_id = 'tx-pending'")
    services.providers.save(CategorizationProfile(provider="openai", model="example"))

    @dataclass
    class Outage:
        calls: int = 0

        def classify(self, **kwargs):
            self.calls += 1
            if self.calls == 1:
                raise ProviderUnavailable(status="limit_reached")
            assert kwargs["description"] == ""
            return LLMClassification("Shopping", 1)

    model = Outage()
    monkeypatch.setattr(services.providers, "client", lambda *args: model)
    worker = services.categorization_worker
    worker.request()
    assert worker.run_once() and model.calls == 0
    worker.request(manual=True)
    assert worker.run_once() and model.calls == 1
    assert worker.status() == "limit_reached"
    assert len(services.transactions.list_for_categorization(10, model=True)) == 2

    worker.request(manual=True)
    assert worker.run_once() and model.calls == 2
    assert services.transactions.get("tx-posted").classification_source == "cloud_llm"
    assert services.transactions.get("tx-pending").classification_source == "cloud_llm"


def test_new_provider_cannot_use_an_earlier_manual_request(test_stack, monkeypatch):
    _settings, _store, db, services, _client = test_stack
    _seed_account_and_transactions(db)
    services.providers.save(CategorizationProfile(provider="openai", model="example"))
    services.categorization_worker.request(manual=True)
    services.providers.save(CategorizationProfile(provider="anthropic", model="example"))
    monkeypatch.setattr(services.providers, "client", lambda *args: pytest.fail("Unrequested cloud inference"))
    assert services.categorization_worker.run_once()


def test_worker_claim_survives_restart_and_serializes_processes(test_stack):
    _settings, _store, db, services, _client = test_stack
    _seed_account_and_transactions(db)
    first = services.categorization_worker
    second = CategorizationWorker(
        services.categorization, services.providers, services.networth_repository, services.chatgpt,
    )
    first.request(manual=True)
    assert first._claim() is not None
    assert not second.run_once()
    with db.transaction() as conn:
        conn.execute("UPDATE categorization_work SET expires_at = 0")
    assert second.run_once()
    assert second.status() == "complete"
    assert services.transactions.get("tx-posted").classification_source == "rules_unmatched"


def test_ai_asset_result_does_not_overwrite_new_manual_category(test_stack, monkeypatch):
    _settings, _store, _db, services, _client = test_stack
    services.providers.save(CategorizationProfile(provider="ollama", model="example"))
    record, _ = services.networth.create_asset(
        name="Example Fund", institution="", value_cents=100, requested_bucket=None, include=True,
    )

    class Model:
        def classify_asset(self, **kwargs):
            services.networth.update_asset(
                record.id, name=record.name, institution="", value_cents=200,
                asset_bucket="Other Assets", include=True,
            )
            return LLMClassification("Taxable Investments", 1)

    monkeypatch.setattr(services.providers, "client", lambda *args: Model())
    monkeypatch.setattr("cardbudget.categorization.service._memory_is_tight", lambda: False)
    assert services.categorization_worker.run_once()
    current = services.networth_repository.get_asset(record.id)
    assert (current.asset_bucket, current.current_value_cents, current.classification_pending) == ("Other Assets", 200, False)


def test_legacy_ollama_model_is_preserved_without_enabling_the_provider(tmp_path, monkeypatch):
    monkeypatch.setenv("POCKETTRACK_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("POCKETTRACK_OLLAMA_MODEL", raising=False)
    monkeypatch.delenv("CARDBUDGET_OLLAMA_MODEL", raising=False)
    assert Settings.from_env().categorization_default == "rules"
    assert Settings.from_env().categorization_default == "rules"
    (tmp_path / "preferences.json").write_text(
        '{"ollama_model":"custom:small","plaid_environment":"sandbox","categorization_default":"ollama"}'
    )
    upgraded = Settings.from_env()
    assert (upgraded.categorization_default, upgraded.ollama_model) == ("rules", "custom:small")
    monkeypatch.setenv("POCKETTRACK_OLLAMA_MODEL", "environment:small")
    overridden = Settings.from_env()
    assert (overridden.categorization_default, overridden.ollama_model) == ("rules", "environment:small")
