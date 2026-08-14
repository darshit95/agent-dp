from __future__ import annotations

import sqlite3

import pytest

from cardbudget.db.engine import Database
from cardbudget.db.repositories import BucketRepository, MerchantRuleRepository, TransactionRepository, to_iso, utc_now


def _seed_transaction(db, transaction_id: str, bucket_id: int | None) -> None:
    now = to_iso(utc_now())
    with db.transaction() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO plaid_items(item_id, institution_name, environment, active, created_at, updated_at)
            VALUES ('item-1', 'Test Bank', 'sandbox', 1, ?, ?)
            """,
            (now, now),
        )
        conn.execute(
            """
            INSERT OR IGNORE INTO accounts(account_id, item_id, name, account_type, enabled, created_at, updated_at)
            VALUES ('acct-1', 'item-1', 'Credit', 'credit', 1, ?, ?)
            """,
            (now, now),
        )
        conn.execute(
            """
            INSERT INTO transactions(
                transaction_id, account_id, amount_cents, iso_currency_code, posted_date,
                authorized_date, budget_date, merchant_name, description, pending,
                bucket_id, is_removed, created_at, updated_at
            ) VALUES (?, 'acct-1', 4200, 'USD', '2026-08-04', '2026-08-04', '2026-08-04',
                      'Cafe', 'CAFE PURCHASE', 0, ?, 0, ?, ?)
            """,
            (transaction_id, bucket_id, now, now),
        )


def test_create_and_update_bucket_icon(test_stack):
    _settings, _store, _db, services, _client = test_stack
    created = services.buckets.create("Dining", 40000, "dining")
    assert created.icon == "dining"

    services.buckets.update(created.id, "Dining out", 45000, icon="coffee")
    reloaded = services.buckets.get(created.id)
    assert (reloaded.name, reloaded.default_budget_cents, reloaded.icon) == ("Dining out", 45000, "coffee")


def test_icon_defaults_to_none_so_it_follows_the_name(test_stack):
    _settings, _store, _db, services, _client = test_stack
    created = services.buckets.create("Travel", None)
    assert created.icon is None
    # Clearing the stored icon is how a bucket goes back to name-derived icons.
    services.buckets.update(created.id, "Travel", None, icon=None)
    assert services.buckets.get(created.id).icon is None


def test_monthly_summary_carries_the_icon(test_stack):
    _settings, _store, _db, services, _client = test_stack
    created = services.buckets.create("Pets", 5000, "pet")
    row = next(r for r in services.buckets.monthly_summary("2026-08") if r.bucket_id == created.id)
    assert row.icon == "pet"


def test_delete_bucket_keeps_transactions_and_moves_them_to_unknown(test_stack):
    _settings, _store, db, services, _client = test_stack
    created = services.buckets.create("Hobbies", 10000, None)
    _seed_transaction(db, "tx-hobby", created.id)

    assert services.buckets.delete(created.id) == "Hobbies"

    assert services.buckets.get(created.id) is None
    transactions = TransactionRepository(db)
    survivor = transactions.get("tx-hobby")
    assert survivor is not None, "deleting a bucket must not delete its spending"
    assert survivor.bucket_id is None

    # A NULL bucket_id is what the summary counts as Unknown.
    unknown = next(r for r in services.buckets.monthly_summary("2026-08") if r.bucket_name == "Unknown")
    assert unknown.spent_cents == 4200


def test_delete_bucket_removes_its_merchant_rules(test_stack):
    _settings, _store, db, services, _client = test_stack
    created = services.buckets.create("Hobbies", None, None)
    rules = MerchantRuleRepository(db)
    rules.upsert("HOBBY SHOP", "Hobby Shop", created.id)

    services.buckets.delete(created.id)

    assert rules.get_by_key("HOBBY SHOP") is None
    assert rules.list_all() == []


def test_unknown_bucket_cannot_be_deleted(test_stack):
    _settings, _store, _db, services, _client = test_stack
    unknown = next(b for b in services.buckets.list_active() if b.name == "Unknown")
    with pytest.raises(ValueError, match="cannot be deleted"):
        services.buckets.delete(unknown.id)
    assert services.buckets.get(unknown.id) is not None


def test_unknown_bucket_cannot_be_renamed(test_stack):
    """monthly_summary and the categorization fallback both match it by name."""
    _settings, _store, _db, services, _client = test_stack
    unknown = next(b for b in services.buckets.list_active() if b.name == "Unknown")
    with pytest.raises(ValueError, match="cannot be renamed"):
        services.buckets.update(unknown.id, "Misc", None)
    assert services.buckets.get(unknown.id).name == "Unknown"


def test_unknown_bucket_can_still_have_its_budget_and_icon_changed(test_stack):
    _settings, _store, _db, services, _client = test_stack
    unknown = next(b for b in services.buckets.list_active() if b.name == "Unknown")
    services.buckets.update(unknown.id, "Unknown", 15000, icon="box")
    refreshed = services.buckets.get(unknown.id)
    assert (refreshed.default_budget_cents, refreshed.icon) == (15000, "box")


def test_update_without_an_icon_argument_keeps_the_stored_icon(test_stack):
    """Callers that only touch the budget must not silently clear the icon."""
    _settings, _store, _db, services, _client = test_stack
    created = services.buckets.create("Dining", 10000, "dining")
    services.buckets.update(created.id, "Dining", 20000)
    assert services.buckets.get(created.id).icon == "dining"


def test_update_can_clear_the_icon_explicitly(test_stack):
    _settings, _store, _db, services, _client = test_stack
    created = services.buckets.create("Dining", None, "gift")
    services.buckets.update(created.id, "Dining", None, icon=None)
    assert services.buckets.get(created.id).icon is None


def test_deleting_missing_bucket_raises(test_stack):
    _settings, _store, _db, services, _client = test_stack
    with pytest.raises(ValueError, match="Unknown bucket"):
        services.buckets.delete(98765)


def test_duplicate_bucket_name_is_rejected(test_stack):
    _settings, _store, _db, services, _client = test_stack
    services.buckets.create("Dining", None)
    with pytest.raises(ValueError, match="already exists"):
        services.buckets.create("dining", None)


def test_icon_column_is_added_to_an_existing_database(tmp_path):
    """Databases created before the icon column must migrate in place."""
    path = tmp_path / "legacy.db"
    legacy = sqlite3.connect(path)
    legacy.executescript(
        """
        CREATE TABLE buckets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE COLLATE NOCASE,
            default_budget_cents INTEGER NULL,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        INSERT INTO buckets(name, default_budget_cents, active, created_at, updated_at)
        VALUES ('Grocery', 30000, 1, '2026-01-01', '2026-01-01');
        """
    )
    legacy.commit()
    legacy.close()

    db = Database(path, "ab" * 32, connector=sqlite3.connect, require_cipher=False)
    db.initialize()

    buckets = BucketRepository(db)
    existing = next(b for b in buckets.list_active() if b.name == "Grocery")
    assert existing.default_budget_cents == 30000, "existing rows must survive the migration"
    assert existing.icon is None

    buckets.update(existing.id, existing.name, existing.default_budget_cents, icon="grocery")
    assert buckets.get(existing.id).icon == "grocery"


def test_initialize_is_idempotent(test_stack):
    _settings, _store, db, _services, _client = test_stack
    db.initialize()
    db.initialize()
    with db.connection() as conn:
        columns = [str(row[1]) for row in conn.execute("PRAGMA table_info(buckets)").fetchall()]
    assert columns.count("icon") == 1
