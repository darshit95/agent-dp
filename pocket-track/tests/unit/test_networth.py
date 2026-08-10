from __future__ import annotations

from cardbudget.db.schema import ASSET_BUCKETS


def test_networth_assets_liabilities_and_allocation(test_stack):
    _settings, _store, _db, services, _client = test_stack
    repo = services.networth_repository
    repo.create_asset(name="Emergency Funds", institution="Example Bank", value_cents=3000000, asset_bucket="Cash & Cash Equivalents", include=True)
    repo.create_asset(name="Brokerage", institution="Fidelity", value_cents=22000000, asset_bucket="Taxable Investments", include=True)
    repo.create_asset(name="ETF subtotal", institution="Fidelity", value_cents=10000000, asset_bucket="Taxable Investments", include=False)
    repo.create_liability(name="Auto loan", institution="Bank", balance_cents=500000, include=True)
    assets, liabilities, net = repo.totals()
    assert assets == 25000000
    assert liabilities == 500000
    assert net == 24500000
    allocation = {row.asset_bucket: row.value_cents for row in repo.allocation()}
    assert allocation["Cash & Cash Equivalents"] == 3000000
    assert allocation["Taxable Investments"] == 22000000


def test_asset_classifier_uses_manual_rule_without_llm(test_stack):
    _settings, _store, _db, services, _client = test_stack
    repo = services.networth_repository
    repo.upsert_rule("HSA|FIDELITY", "HSA", "Retirement & Health")
    result = services.networth.classify("HSA", "Fidelity")
    assert result.asset_bucket == "Retirement & Health"
    assert result.source == "saved_rule"
    assert result.asset_bucket in ASSET_BUCKETS
