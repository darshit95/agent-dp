from __future__ import annotations

from dataclasses import dataclass, field

from cardbudget.plaid.client import PlaidClient
from cardbudget.plaid.service import PlaidService, access_token_key
from cardbudget.db.repositories import PlaidRepository, TransactionRepository


@dataclass
class FakeTransport:
    pages: list[dict] = field(default_factory=list)
    calls: list[tuple[str, dict]] = field(default_factory=list)

    def post(self, path, payload):
        self.calls.append((path, dict(payload)))
        if path == "/link/token/create":
            return {"link_token": "link-sandbox-test"}
        if path == "/item/public_token/exchange":
            return {"access_token": "access-sandbox-secret", "item_id": "item-1"}
        if path == "/item/get":
            return {"item": {"item_id": "item-1", "institution_id": "ins-test", "institution_name": "First Platypus Bank"}}
        if path == "/accounts/get":
            return {
                "accounts": [
                    {"account_id": "acct-1", "name": "Plaid Credit Card", "official_name": "Sandbox Visa", "mask": "1234", "type": "credit", "subtype": "credit card"},
                    {"account_id": "acct-ignore", "name": "Checking", "official_name": None, "mask": "0000", "type": "depository", "subtype": "checking"},
                ]
            }
        if path == "/transactions/sync":
            if self.pages:
                return self.pages.pop(0)
            return {"added": [], "modified": [], "removed": [], "next_cursor": "cursor-final", "has_more": False, "transactions_update_status": "HISTORICAL_UPDATE_COMPLETE"}
        raise AssertionError(path)


def _make_service(test_stack, transport):
    _settings, store, db, _services, _client = test_stack
    repo = PlaidRepository(db)
    tx_repo = TransactionRepository(db)

    def factory(_client_id, _secret, _environment):
        return PlaidClient(transport)

    service = PlaidService(
        secret_store=store,
        plaid_repository=repo,
        transactions=tx_repo,
        environment="sandbox",
        client_factory=factory,
    )
    service.save_credentials("client-id", "sandbox-secret")
    return service, repo, tx_repo, store


def test_exchange_stores_access_token_only_in_keychain(test_stack):
    transport = FakeTransport()
    service, repo, _tx_repo, store = _make_service(test_stack, transport)
    item_id = service.exchange_and_register("public-token")
    assert item_id == "item-1"
    assert store.get_secret(access_token_key("sandbox", "item-1")) == "access-sandbox-secret"
    assert len(repo.list_active_items()) == 1
    accounts = repo.list_accounts()
    assert {a.account_id for a in accounts} == {"acct-1", "acct-ignore"}

    # Access token must not appear in any database value.
    _settings, _store, db, _services, _client = test_stack
    with db.connection() as conn:
        for table in ("app_meta", "plaid_items", "accounts"):
            rows = conn.execute(f"SELECT * FROM {table}").fetchall()
            assert "access-sandbox-secret" not in repr(rows)


def test_sync_is_idempotent_and_ignores_unmapped_accounts(test_stack):
    page = {
        "added": [
            {
                "transaction_id": "tx-1", "account_id": "acct-1", "amount": 12.34,
                "iso_currency_code": "USD", "date": "2026-08-03", "authorized_date": "2026-08-02",
                "merchant_name": "Coffee Shop", "name": "COFFEE SHOP", "pending": False,
                "pending_transaction_id": None,
                "personal_finance_category": {"primary": "FOOD_AND_DRINK", "detailed": "FOOD_AND_DRINK_COFFEE", "confidence_level": "VERY_HIGH"},
            },
            {
                "transaction_id": "tx-ignore", "account_id": "acct-ignore", "amount": 99,
                "iso_currency_code": "USD", "date": "2026-08-03", "authorized_date": None,
                "merchant_name": "Ignored", "name": "IGNORED", "pending": False,
                "pending_transaction_id": None, "personal_finance_category": None,
            },
        ],
        "modified": [], "removed": [], "next_cursor": "cursor-1", "has_more": False,
        "transactions_update_status": "HISTORICAL_UPDATE_COMPLETE",
    }
    transport = FakeTransport(pages=[page.copy()])
    service, repo, tx_repo, _store = _make_service(test_stack, transport)
    service.exchange_and_register("public-token")
    service.map_account("acct-1", "legacy_card_key")

    first = service.sync_all()
    assert first.added == 1
    assert first.ignored_unmapped == 1
    rows = tx_repo.list_recent()
    assert len(rows) == 1
    assert rows[0].transaction_id == "tx-1"
    assert rows[0].budget_date == "2026-08-02"
    assert rows[0].card_name == "Sandbox Visa"

    second = service.sync_all()
    assert second.added == 0
    assert len(tx_repo.list_recent()) == 1
    assert repo.list_active_items()[0].sync_cursor == "cursor-final"


def test_pending_is_ignored_then_posted_is_stored(test_stack):
    pending = {
        "added": [{
            "transaction_id": "pending-1", "account_id": "acct-1", "amount": 42,
            "iso_currency_code": "USD", "date": "2026-08-31", "authorized_date": "2026-08-31",
            "merchant_name": "Store", "name": "STORE", "pending": True,
            "pending_transaction_id": None, "personal_finance_category": None,
        }],
        "modified": [], "removed": [], "next_cursor": "c1", "has_more": False,
        "transactions_update_status": "INITIAL_UPDATE_COMPLETE",
    }
    posted = {
        "added": [{
            "transaction_id": "posted-1", "account_id": "acct-1", "amount": 42,
            "iso_currency_code": "USD", "date": "2026-09-02", "authorized_date": "2026-08-31",
            "merchant_name": "Store", "name": "STORE", "pending": False,
            "pending_transaction_id": "pending-1", "personal_finance_category": None,
        }],
        "modified": [], "removed": [{"transaction_id": "pending-1", "account_id": "acct-1"}],
        "next_cursor": "c2", "has_more": False, "transactions_update_status": "HISTORICAL_UPDATE_COMPLETE",
    }
    transport = FakeTransport(pages=[pending, posted])
    service, _repo, tx_repo, _store = _make_service(test_stack, transport)
    service.exchange_and_register("public-token")
    service.map_account("acct-1", "legacy_card_key")
    first = service.sync_all()
    assert first.ignored_pending == 1
    assert tx_repo.list_recent() == []

    service.sync_all()
    rows = tx_repo.list_recent()
    assert len(rows) == 1
    assert rows[0].transaction_id == "posted-1"
    assert rows[0].pending is False
    assert rows[0].budget_date == "2026-08-31"


def test_payment_and_autopay_are_ignored(test_stack):
    page = {
        "added": [
            {
                "transaction_id": "payment-1", "account_id": "acct-1", "amount": -500,
                "iso_currency_code": "USD", "date": "2026-08-05", "authorized_date": "2026-08-05",
                "merchant_name": None, "name": "AUTOPAY PAYMENT - THANK YOU", "pending": False,
                "pending_transaction_id": None,
                "personal_finance_category": {"primary": "TRANSFER_IN", "detailed": "TRANSFER_IN_ACCOUNT_TRANSFER", "confidence_level": "HIGH"},
            },
            {
                "transaction_id": "purchase-1", "account_id": "acct-1", "amount": 23.50,
                "iso_currency_code": "USD", "date": "2026-08-06", "authorized_date": "2026-08-06",
                "merchant_name": "Target", "name": "TARGET", "pending": False,
                "pending_transaction_id": None,
                "personal_finance_category": {"primary": "GENERAL_MERCHANDISE", "detailed": "GENERAL_MERCHANDISE_OTHER_GENERAL_MERCHANDISE", "confidence_level": "HIGH"},
            },
        ],
        "modified": [], "removed": [], "next_cursor": "c-pay", "has_more": False,
        "transactions_update_status": "HISTORICAL_UPDATE_COMPLETE",
    }
    transport = FakeTransport(pages=[page])
    service, _repo, tx_repo, _store = _make_service(test_stack, transport)
    service.exchange_and_register("public-token")
    service.map_account("acct-1", "legacy_card_key")
    result = service.sync_all()
    assert result.ignored_payments == 1
    rows = tx_repo.list_recent()
    assert [row.transaction_id for row in rows] == ["purchase-1"]


def test_user_delete_tombstone_prevents_reimport(test_stack):
    page = {
        "added": [{
            "transaction_id": "tx-delete", "account_id": "acct-1", "amount": 11,
            "iso_currency_code": "USD", "date": "2026-08-06", "authorized_date": "2026-08-06",
            "merchant_name": "Store", "name": "STORE", "pending": False, "pending_transaction_id": None,
            "personal_finance_category": None,
        }],
        "modified": [], "removed": [], "next_cursor": "c1", "has_more": False,
        "transactions_update_status": "HISTORICAL_UPDATE_COMPLETE",
    }
    repeat = dict(page)
    repeat["added"] = []
    repeat["modified"] = page["added"]
    repeat["next_cursor"] = "c2"
    transport = FakeTransport(pages=[page, repeat])
    service, _repo, tx_repo, _store = _make_service(test_stack, transport)
    service.exchange_and_register("public-token")
    service.map_account("acct-1", "legacy_card_key")
    service.sync_all()
    tx_repo.delete_by_user("tx-delete")
    assert tx_repo.list_recent() == []
    result = service.sync_all()
    assert result.ignored_deleted == 1
    assert tx_repo.list_recent() == []


def test_backfill_july_imports_only_posted_spend(test_stack):
    class HistoricalTransport(FakeTransport):
        def post(self, path, payload):
            if path == "/transactions/get":
                self.calls.append((path, dict(payload)))
                return {
                    "transactions": [
                        {
                            "transaction_id": "july-purchase", "account_id": "acct-1", "amount": 44.20,
                            "iso_currency_code": "USD", "date": "2026-07-14", "authorized_date": "2026-07-14",
                            "merchant_name": "Safeway", "name": "SAFEWAY", "pending": False,
                            "pending_transaction_id": None,
                            "personal_finance_category": {"primary": "FOOD_AND_DRINK", "detailed": "FOOD_AND_DRINK_GROCERIES", "confidence_level": "HIGH"},
                        },
                        {
                            "transaction_id": "july-pending", "account_id": "acct-1", "amount": 15,
                            "iso_currency_code": "USD", "date": "2026-07-31", "authorized_date": "2026-07-31",
                            "merchant_name": "Store", "name": "STORE", "pending": True,
                            "pending_transaction_id": None, "personal_finance_category": None,
                        },
                        {
                            "transaction_id": "july-payment", "account_id": "acct-1", "amount": -1000,
                            "iso_currency_code": "USD", "date": "2026-07-20", "authorized_date": "2026-07-20",
                            "merchant_name": None, "name": "AUTOPAY PAYMENT - THANK YOU", "pending": False,
                            "pending_transaction_id": None,
                            "personal_finance_category": {"primary": "TRANSFER_IN", "detailed": "TRANSFER_IN_ACCOUNT_TRANSFER", "confidence_level": "HIGH"},
                        },
                    ],
                    "total_transactions": 3,
                }
            return super().post(path, payload)

    transport = HistoricalTransport()
    service, _repo, tx_repo, _store = _make_service(test_stack, transport)
    service.exchange_and_register("public-token")
    service.map_account("acct-1", "legacy_card_key")
    result = service.backfill_month("2026-07")
    assert result.imported == 1
    assert result.ignored_pending == 1
    assert result.ignored_payments == 1
    rows = tx_repo.list_recent(month="2026-07")
    assert [r.transaction_id for r in rows] == ["july-purchase"]
    get_call = next(call for call in transport.calls if call[0] == "/transactions/get")
    assert get_call[1]["start_date"] == "2026-07-01"
    assert get_call[1]["end_date"] == "2026-07-31"
