from __future__ import annotations

from dataclasses import dataclass

from cardbudget.categorization.ollama import LLMClassification
from cardbudget.categorization.service import CategorizationService, merchant_key
from cardbudget.db.repositories import MerchantRuleRepository, TransactionRepository, to_iso, utc_now


@dataclass
class FakeLLM:
    bucket: str | None = "Shopping"
    confidence: float = 0.91
    calls: int = 0

    def classify(self, **_kwargs):
        self.calls += 1
        return LLMClassification(self.bucket, self.confidence)


def _seed_account_and_transactions(db) -> None:
    now = to_iso(utc_now())
    with db.transaction() as conn:
        conn.execute(
            """
            INSERT INTO plaid_items(item_id, institution_name, environment, active, created_at, updated_at)
            VALUES ('item-1', 'Test Bank', 'sandbox', 1, ?, ?)
            """,
            (now, now),
        )
        conn.execute(
            """
            INSERT INTO accounts(account_id, item_id, name, account_type, subtype, card_key, card_name, enabled, created_at, updated_at)
            VALUES ('acct-1', 'item-1', 'Credit', 'credit', 'credit card', 'legacy_card_key', 'Example Rewards Card', 1, ?, ?)
            """,
            (now, now),
        )
        common = (
            "acct-1", 10000, "USD", "2026-08-02", "2026-08-02", "2026-08-02",
            "Amazon", "AMAZON MKTPLACE", None, "GENERAL_MERCHANDISE", "GENERAL_MERCHANDISE_ONLINE_MARKETPLACES", now, now,
        )
        conn.execute(
            """
            INSERT INTO transactions(
                transaction_id, account_id, amount_cents, iso_currency_code, posted_date,
                authorized_date, budget_date, merchant_name, description, pending,
                pending_transaction_id, pfc_primary, pfc_detailed, is_removed, created_at, updated_at
            ) VALUES ('tx-posted', ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, 0, ?, ?)
            """,
            common,
        )
        conn.execute(
            """
            INSERT INTO transactions(
                transaction_id, account_id, amount_cents, iso_currency_code, posted_date,
                authorized_date, budget_date, merchant_name, description, pending,
                pending_transaction_id, pfc_primary, pfc_detailed, is_removed, created_at, updated_at
            ) VALUES ('tx-pending', ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, 0, ?, ?)
            """,
            common,
        )


def test_local_llm_categorizes_posted_but_not_pending(test_stack):
    _settings, _store, db, services, _client = test_stack
    _seed_account_and_transactions(db)
    tx_repo = TransactionRepository(db)
    rules = MerchantRuleRepository(db)
    fake = FakeLLM()
    categorizer = CategorizationService(
        transactions=tx_repo,
        buckets=services.buckets,
        merchant_rules=rules,
        llm=fake,
    )

    result = categorizer.categorize_unassigned()
    assert result.llm_applied == 1
    assert fake.calls == 1
    assert tx_repo.get("tx-posted").bucket_name == "Shopping"
    assert tx_repo.get("tx-pending").bucket_id is None


def test_remember_merchant_rule_overrides_llm_for_future_transaction(test_stack):
    _settings, _store, db, services, _client = test_stack
    _seed_account_and_transactions(db)
    tx_repo = TransactionRepository(db)
    rules = MerchantRuleRepository(db)
    grocery = next(b for b in services.buckets.list_active() if b.name == "Grocery")
    fake = FakeLLM(bucket="Shopping")
    categorizer = CategorizationService(
        transactions=tx_repo,
        buckets=services.buckets,
        merchant_rules=rules,
        llm=fake,
    )

    categorizer.manual_assign("tx-posted", grocery.id, remember_merchant=True)
    assert rules.get_by_key(merchant_key("Amazon", "AMAZON MKTPLACE")).bucket_name == "Grocery"

    now = to_iso(utc_now())
    with db.transaction() as conn:
        conn.execute(
            """
            INSERT INTO transactions(
                transaction_id, account_id, amount_cents, iso_currency_code, posted_date,
                authorized_date, budget_date, merchant_name, description, pending,
                pfc_primary, is_removed, created_at, updated_at
            ) VALUES ('tx-future', 'acct-1', 2500, 'USD', '2026-08-10', '2026-08-10',
                      '2026-08-10', 'Amazon', 'AMAZON MKTPLACE', 0, 'GENERAL_MERCHANDISE', 0, ?, ?)
            """,
            (now, now),
        )

    result = categorizer.categorize_unassigned()
    assert result.rule_applied == 1
    assert fake.calls == 0
    assert tx_repo.get("tx-future").bucket_name == "Grocery"


def test_categorization_stops_calling_the_llm_under_memory_pressure(test_stack, monkeypatch):
    """A tight-memory machine should never be pushed further by a long run of
    local LLM calls: once memory is tight, remaining unassigned transactions
    fall back to Unknown (like the existing Ollama-unavailable path) instead
    of continuing to call the model."""
    _settings, _store, db, services, _client = test_stack
    _seed_account_and_transactions(db)
    tx_repo = TransactionRepository(db)
    rules = MerchantRuleRepository(db)

    now = to_iso(utc_now())
    with db.transaction() as conn:
        conn.execute(
            """
            INSERT INTO transactions(
                transaction_id, account_id, amount_cents, iso_currency_code, posted_date,
                authorized_date, budget_date, merchant_name, description, pending,
                pfc_primary, is_removed, created_at, updated_at
            ) VALUES ('tx-posted-2', 'acct-1', 1500, 'USD', '2026-08-11', '2026-08-11',
                      '2026-08-11', 'Coffee Shop', 'COFFEE SHOP PURCHASE', 0, 'FOOD_AND_DRINK', 0, ?, ?)
            """,
            (now, now),
        )

    monkeypatch.setattr("cardbudget.categorization.service._memory_is_tight", lambda: True)
    fake = FakeLLM()
    categorizer = CategorizationService(
        transactions=tx_repo,
        buckets=services.buckets,
        merchant_rules=rules,
        llm=fake,
    )

    result = categorizer.categorize_unassigned()
    assert fake.calls == 0
    assert result.llm_applied == 0
    assert result.left_uncategorized == 2
    assert result.memory_paused is True
    assert tx_repo.get("tx-posted").bucket_name == "Unknown"
    assert tx_repo.get("tx-posted-2").bucket_name == "Unknown"


def test_budget_summary_excludes_pending_and_applies_refunds(test_stack):
    _settings, _store, db, services, _client = test_stack
    _seed_account_and_transactions(db)
    shopping = next(b for b in services.buckets.list_active() if b.name == "Shopping")
    services.buckets.update(shopping.id, shopping.name, 12000)
    tx_repo = TransactionRepository(db)
    tx_repo.assign_bucket("tx-posted", shopping.id, source="manual", confidence=1.0)
    tx_repo.assign_bucket("tx-pending", shopping.id, source="manual", confidence=1.0)

    now = to_iso(utc_now())
    with db.transaction() as conn:
        conn.execute(
            """
            INSERT INTO transactions(
                transaction_id, account_id, amount_cents, iso_currency_code, posted_date,
                authorized_date, budget_date, merchant_name, description, pending,
                bucket_id, classification_source, classification_confidence, is_removed,
                created_at, updated_at
            ) VALUES ('refund', 'acct-1', -2000, 'USD', '2026-08-12', '2026-08-12',
                      '2026-08-12', 'Amazon', 'REFUND', 0, ?, 'manual', 1, 0, ?, ?)
            """,
            (shopping.id, now, now),
        )

    row = next(r for r in services.buckets.monthly_summary("2026-08") if r.bucket_name == "Shopping")
    assert row.spent_cents == 8000
    assert row.budget_cents == 12000
