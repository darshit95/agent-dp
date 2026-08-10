from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone

from cardbudget.db.engine import Database


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def to_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()


def from_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class UserRecord:
    id: int
    username: str
    password_hash: str


@dataclass(frozen=True)
class SessionRecord:
    id: str
    user_id: int
    csrf_token: str
    created_at: datetime
    last_seen_at: datetime
    expires_at: datetime


@dataclass(frozen=True)
class BucketRecord:
    id: int
    name: str
    default_budget_cents: int | None
    active: bool


@dataclass(frozen=True)
class PlaidItemRecord:
    item_id: str
    institution_id: str | None
    institution_name: str | None
    environment: str
    sync_cursor: str | None
    transactions_update_status: str | None
    last_synced_at: datetime | None
    last_sync_error_code: str | None


@dataclass(frozen=True)
class AccountRecord:
    account_id: str
    item_id: str
    institution_name: str | None
    name: str
    official_name: str | None
    mask: str | None
    account_type: str
    subtype: str | None
    card_key: str | None
    card_name: str | None
    enabled: bool


@dataclass(frozen=True)
class TransactionRecord:
    transaction_id: str
    account_id: str
    card_name: str | None
    amount_cents: int
    iso_currency_code: str
    posted_date: str | None
    authorized_date: str | None
    budget_date: str | None
    merchant_name: str | None
    description: str
    pending: bool
    pfc_primary: str | None
    pfc_detailed: str | None
    bucket_id: int | None
    bucket_name: str | None
    classification_source: str | None
    classification_confidence: float | None


@dataclass(frozen=True)
class MerchantRuleRecord:
    id: int
    merchant_key: str
    display_name: str
    bucket_id: int
    bucket_name: str


@dataclass(frozen=True)
class BudgetSummaryRecord:
    bucket_id: int
    bucket_name: str
    budget_cents: int | None
    spent_cents: int


class UserRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def count(self) -> int:
        with self.db.connection() as conn:
            row = conn.execute("SELECT count(*) FROM users").fetchone()
            return int(row[0])

    def get_by_username(self, username: str) -> UserRecord | None:
        with self.db.connection() as conn:
            row = conn.execute(
                "SELECT id, username, password_hash FROM users WHERE username = ? COLLATE NOCASE",
                (username,),
            ).fetchone()
        if not row:
            return None
        return UserRecord(int(row[0]), str(row[1]), str(row[2]))

    def get_by_id(self, user_id: int) -> UserRecord | None:
        with self.db.connection() as conn:
            row = conn.execute(
                "SELECT id, username, password_hash FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        if not row:
            return None
        return UserRecord(int(row[0]), str(row[1]), str(row[2]))

    def create_single_user(self, username: str, password_hash: str) -> UserRecord:
        now = to_iso(utc_now())
        with self.db.transaction() as conn:
            existing = conn.execute("SELECT count(*) FROM users").fetchone()[0]
            if existing:
                raise ValueError("Application user already exists.")
            conn.execute(
                """
                INSERT INTO users(id, username, password_hash, created_at, updated_at)
                VALUES (1, ?, ?, ?, ?)
                """,
                (username, password_hash, now, now),
            )
        return UserRecord(1, username, password_hash)

    def update_password_hash(self, user_id: int, password_hash: str) -> None:
        with self.db.transaction() as conn:
            conn.execute(
                "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
                (password_hash, to_iso(utc_now()), user_id),
            )


class SessionRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def create(self, record: SessionRecord) -> None:
        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO sessions(id, user_id, csrf_token, created_at, last_seen_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.user_id,
                    record.csrf_token,
                    to_iso(record.created_at),
                    to_iso(record.last_seen_at),
                    to_iso(record.expires_at),
                ),
            )

    def get(self, session_id: str) -> SessionRecord | None:
        with self.db.connection() as conn:
            row = conn.execute(
                """
                SELECT id, user_id, csrf_token, created_at, last_seen_at, expires_at
                FROM sessions WHERE id = ?
                """,
                (session_id,),
            ).fetchone()
        if not row:
            return None
        return SessionRecord(
            id=str(row[0]),
            user_id=int(row[1]),
            csrf_token=str(row[2]),
            created_at=from_iso(str(row[3])),
            last_seen_at=from_iso(str(row[4])),
            expires_at=from_iso(str(row[5])),
        )

    def touch(self, session_id: str, last_seen_at: datetime, expires_at: datetime) -> None:
        with self.db.transaction() as conn:
            conn.execute(
                "UPDATE sessions SET last_seen_at = ?, expires_at = ? WHERE id = ?",
                (to_iso(last_seen_at), to_iso(expires_at), session_id),
            )

    def delete(self, session_id: str) -> None:
        with self.db.transaction() as conn:
            conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))

    def delete_all_for_user(self, user_id: int) -> None:
        with self.db.transaction() as conn:
            conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))

    def delete_expired(self, now: datetime) -> int:
        with self.db.transaction() as conn:
            cursor = conn.execute("DELETE FROM sessions WHERE expires_at <= ?", (to_iso(now),))
            return int(cursor.rowcount if cursor.rowcount is not None else 0)


class BucketRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    @staticmethod
    def _record(row) -> BucketRecord:
        return BucketRecord(
            id=int(row[0]),
            name=str(row[1]),
            default_budget_cents=None if row[2] is None else int(row[2]),
            active=bool(row[3]),
        )

    def list_active(self) -> list[BucketRecord]:
        with self.db.connection() as conn:
            rows = conn.execute(
                "SELECT id, name, default_budget_cents, active FROM buckets WHERE active = 1 ORDER BY id"
            ).fetchall()
        return [self._record(row) for row in rows]

    def list_all(self) -> list[BucketRecord]:
        with self.db.connection() as conn:
            rows = conn.execute(
                "SELECT id, name, default_budget_cents, active FROM buckets ORDER BY active DESC, id"
            ).fetchall()
        return [self._record(row) for row in rows]

    def get(self, bucket_id: int) -> BucketRecord | None:
        with self.db.connection() as conn:
            row = conn.execute(
                "SELECT id, name, default_budget_cents, active FROM buckets WHERE id = ?",
                (bucket_id,),
            ).fetchone()
        return None if not row else self._record(row)

    def create(self, name: str, budget_cents: int | None) -> BucketRecord:
        clean = " ".join(name.strip().split())
        if not clean or len(clean) > 80:
            raise ValueError("Bucket name must be between 1 and 80 characters.")
        if budget_cents is not None and budget_cents < 0:
            raise ValueError("Budget cannot be negative.")
        now = to_iso(utc_now())
        try:
            with self.db.transaction() as conn:
                cur = conn.execute(
                    "INSERT INTO buckets(name, default_budget_cents, active, created_at, updated_at) VALUES (?, ?, 1, ?, ?)",
                    (clean, budget_cents, now, now),
                )
                bucket_id = int(cur.lastrowid)
        except Exception as exc:
            if "UNIQUE" in str(exc).upper():
                raise ValueError("A bucket with that name already exists.") from exc
            raise
        return self.get(bucket_id)  # type: ignore[return-value]

    def update(self, bucket_id: int, name: str, budget_cents: int | None, active: bool = True) -> None:
        clean = " ".join(name.strip().split())
        if not clean or len(clean) > 80:
            raise ValueError("Bucket name must be between 1 and 80 characters.")
        if budget_cents is not None and budget_cents < 0:
            raise ValueError("Budget cannot be negative.")
        try:
            with self.db.transaction() as conn:
                cur = conn.execute(
                    "UPDATE buckets SET name = ?, default_budget_cents = ?, active = ?, updated_at = ? WHERE id = ?",
                    (clean, budget_cents, 1 if active else 0, to_iso(utc_now()), bucket_id),
                )
                if cur.rowcount == 0:
                    raise ValueError("Unknown bucket.")
        except Exception as exc:
            if isinstance(exc, ValueError):
                raise
            if "UNIQUE" in str(exc).upper():
                raise ValueError("A bucket with that name already exists.") from exc
            raise

    def deactivate(self, bucket_id: int) -> None:
        with self.db.transaction() as conn:
            cur = conn.execute(
                "UPDATE buckets SET active = 0, updated_at = ? WHERE id = ?",
                (to_iso(utc_now()), bucket_id),
            )
            if cur.rowcount == 0:
                raise ValueError("Unknown bucket.")

    def monthly_summary(self, month: str) -> list[BudgetSummaryRecord]:
        # Validate YYYY-MM without importing locale/timezone concerns.
        datetime.strptime(month, "%Y-%m")
        with self.db.connection() as conn:
            rows = conn.execute(
                """
                SELECT b.id, b.name, b.default_budget_cents,
                       COALESCE(SUM(CASE WHEN t.pending = 0 AND t.is_removed = 0 THEN t.amount_cents ELSE 0 END), 0)
                FROM buckets b
                LEFT JOIN transactions t
                  ON (t.bucket_id = b.id OR (t.bucket_id IS NULL AND b.name = 'Unknown' COLLATE NOCASE))
                 AND t.budget_date LIKE ?
                WHERE b.active = 1
                GROUP BY b.id, b.name, b.default_budget_cents
                ORDER BY b.id
                """,
                (f"{month}-%",),
            ).fetchall()
        return [
            BudgetSummaryRecord(int(r[0]), str(r[1]), None if r[2] is None else int(r[2]), int(r[3]))
            for r in rows
        ]


class AuditRepository:
    ALLOWED_EVENTS = {
        "setup_complete",
        "login_success",
        "login_failure",
        "logout",
        "password_changed",
        "plaid_credentials_updated",
        "plaid_item_connected",
        "account_mapping_updated",
        "transactions_synced",
        "transaction_category_updated",
        "transaction_deleted",
        "historical_backfill",
        "bucket_created",
        "bucket_updated",
        "bucket_deactivated",
        "categorization_run",
        "merchant_rule_deleted",
        "asset_created",
        "asset_updated",
        "asset_deleted",
        "liability_created",
        "liability_updated",
        "liability_deleted",
        "backup_created",
        "backup_restored",
    }

    def __init__(self, db: Database) -> None:
        self.db = db

    def record(self, event_type: str, remote_addr: str | None = None, details: dict | None = None) -> None:
        if event_type not in self.ALLOWED_EVENTS:
            raise ValueError("Unsupported audit event type.")
        payload = json.dumps(details or {}, separators=(",", ":"), sort_keys=True)
        if len(payload) > 1024:
            raise ValueError("Audit event details are too large.")
        with self.db.transaction() as conn:
            conn.execute(
                "INSERT INTO audit_events(event_type, remote_addr, details_json, created_at) VALUES (?, ?, ?, ?)",
                (event_type, remote_addr, payload, to_iso(utc_now())),
            )


class PlaidRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def upsert_item(
        self,
        *,
        item_id: str,
        institution_id: str | None,
        institution_name: str | None,
        environment: str,
    ) -> None:
        now = to_iso(utc_now())
        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO plaid_items(
                    item_id, institution_id, institution_name, environment, active,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, 1, ?, ?)
                ON CONFLICT(item_id) DO UPDATE SET
                    institution_id = excluded.institution_id,
                    institution_name = excluded.institution_name,
                    environment = excluded.environment,
                    active = 1,
                    updated_at = excluded.updated_at
                """,
                (item_id, institution_id, institution_name, environment, now, now),
            )

    def replace_accounts(self, item_id: str, accounts: list[dict]) -> None:
        now = to_iso(utc_now())
        with self.db.transaction() as conn:
            seen: set[str] = set()
            for account in accounts:
                account_id = str(account["account_id"])
                seen.add(account_id)
                conn.execute(
                    """
                    INSERT INTO accounts(
                        account_id, item_id, name, official_name, mask, account_type,
                        subtype, enabled, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
                    ON CONFLICT(account_id) DO UPDATE SET
                        item_id = excluded.item_id,
                        name = excluded.name,
                        official_name = excluded.official_name,
                        mask = excluded.mask,
                        account_type = excluded.account_type,
                        subtype = excluded.subtype,
                        updated_at = excluded.updated_at
                    """,
                    (
                        account_id,
                        item_id,
                        str(account.get("name") or "Account"),
                        None if account.get("official_name") is None else str(account.get("official_name")),
                        None if account.get("mask") is None else str(account.get("mask")),
                        str(account.get("type") or "unknown"),
                        None if account.get("subtype") is None else str(account.get("subtype")),
                        now,
                        now,
                    ),
                )
            rows = conn.execute("SELECT account_id FROM accounts WHERE item_id = ?", (item_id,)).fetchall()
            for row in rows:
                if str(row[0]) not in seen:
                    conn.execute(
                        "UPDATE accounts SET enabled = 0, card_key = NULL, card_name = NULL, updated_at = ? WHERE account_id = ?",
                        (now, str(row[0])),
                    )

    def get_item(self, item_id: str, environment: str | None = None) -> PlaidItemRecord | None:
        with self.db.connection() as conn:
            if environment:
                row = conn.execute(
                    """
                    SELECT item_id, institution_id, institution_name, environment, sync_cursor,
                           transactions_update_status, last_synced_at, last_sync_error_code
                    FROM plaid_items WHERE item_id = ? AND active = 1 AND environment = ?
                    """,
                    (item_id, environment),
                ).fetchone()
            else:
                row = conn.execute(
                    """
                    SELECT item_id, institution_id, institution_name, environment, sync_cursor,
                           transactions_update_status, last_synced_at, last_sync_error_code
                    FROM plaid_items WHERE item_id = ? AND active = 1
                    """,
                    (item_id,),
                ).fetchone()
        if not row:
            return None
        return PlaidItemRecord(
            item_id=str(row[0]), institution_id=None if row[1] is None else str(row[1]),
            institution_name=None if row[2] is None else str(row[2]), environment=str(row[3]),
            sync_cursor=None if row[4] is None else str(row[4]),
            transactions_update_status=None if row[5] is None else str(row[5]),
            last_synced_at=None if row[6] is None else from_iso(str(row[6])),
            last_sync_error_code=None if row[7] is None else str(row[7]),
        )

    def list_active_items(self, environment: str | None = None) -> list[PlaidItemRecord]:
        with self.db.connection() as conn:
            if environment:
                rows = conn.execute(
                    """
                    SELECT item_id, institution_id, institution_name, environment, sync_cursor,
                           transactions_update_status, last_synced_at, last_sync_error_code
                    FROM plaid_items WHERE active = 1 AND environment = ? ORDER BY created_at
                    """,
                    (environment,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT item_id, institution_id, institution_name, environment, sync_cursor,
                           transactions_update_status, last_synced_at, last_sync_error_code
                    FROM plaid_items WHERE active = 1 ORDER BY created_at
                    """
                ).fetchall()
        return [
            PlaidItemRecord(
                item_id=str(r[0]), institution_id=None if r[1] is None else str(r[1]),
                institution_name=None if r[2] is None else str(r[2]), environment=str(r[3]),
                sync_cursor=None if r[4] is None else str(r[4]),
                transactions_update_status=None if r[5] is None else str(r[5]),
                last_synced_at=None if r[6] is None else from_iso(str(r[6])),
                last_sync_error_code=None if r[7] is None else str(r[7]),
            ) for r in rows
        ]

    def get_account(self, account_id: str, environment: str | None = None) -> AccountRecord | None:
        with self.db.connection() as conn:
            if environment:
                row = conn.execute(
                    """
                    SELECT a.account_id, a.item_id, p.institution_name, a.name, a.official_name,
                           a.mask, a.account_type, a.subtype, a.card_key, a.card_name, a.enabled
                    FROM accounts a JOIN plaid_items p ON p.item_id = a.item_id
                    WHERE a.account_id = ? AND p.active = 1 AND p.environment = ?
                    """,
                    (account_id, environment),
                ).fetchone()
            else:
                row = conn.execute(
                    """
                    SELECT a.account_id, a.item_id, p.institution_name, a.name, a.official_name,
                           a.mask, a.account_type, a.subtype, a.card_key, a.card_name, a.enabled
                    FROM accounts a JOIN plaid_items p ON p.item_id = a.item_id
                    WHERE a.account_id = ? AND p.active = 1
                    """,
                    (account_id,),
                ).fetchone()
        if not row:
            return None
        return AccountRecord(
            account_id=str(row[0]), item_id=str(row[1]), institution_name=None if row[2] is None else str(row[2]),
            name=str(row[3]), official_name=None if row[4] is None else str(row[4]),
            mask=None if row[5] is None else str(row[5]), account_type=str(row[6]),
            subtype=None if row[7] is None else str(row[7]), card_key=None if row[8] is None else str(row[8]),
            card_name=None if row[9] is None else str(row[9]), enabled=bool(row[10]),
        )

    def list_accounts(self, environment: str | None = None) -> list[AccountRecord]:
        with self.db.connection() as conn:
            if environment:
                rows = conn.execute(
                    """
                    SELECT a.account_id, a.item_id, p.institution_name, a.name, a.official_name,
                           a.mask, a.account_type, a.subtype, a.card_key, a.card_name, a.enabled
                    FROM accounts a JOIN plaid_items p ON p.item_id = a.item_id
                    WHERE p.active = 1 AND p.environment = ?
                    ORDER BY p.created_at, a.created_at
                    """,
                    (environment,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT a.account_id, a.item_id, p.institution_name, a.name, a.official_name,
                           a.mask, a.account_type, a.subtype, a.card_key, a.card_name, a.enabled
                    FROM accounts a JOIN plaid_items p ON p.item_id = a.item_id
                    WHERE p.active = 1
                    ORDER BY p.created_at, a.created_at
                    """
                ).fetchall()
        return [
            AccountRecord(
                account_id=str(r[0]), item_id=str(r[1]), institution_name=None if r[2] is None else str(r[2]),
                name=str(r[3]), official_name=None if r[4] is None else str(r[4]),
                mask=None if r[5] is None else str(r[5]), account_type=str(r[6]),
                subtype=None if r[7] is None else str(r[7]), card_key=None if r[8] is None else str(r[8]),
                card_name=None if r[9] is None else str(r[9]), enabled=bool(r[10]),
            ) for r in rows
        ]

    def map_account(self, account_id: str, card_key: str | None, card_name: str | None, enabled: bool) -> None:
        now = to_iso(utc_now())
        with self.db.transaction() as conn:
            exists = conn.execute("SELECT 1 FROM accounts WHERE account_id = ?", (account_id,)).fetchone()
            if not exists:
                raise ValueError("Unknown Plaid account.")
            if card_key:
                conn.execute(
                    "UPDATE accounts SET card_key = NULL, card_name = NULL, enabled = 0, updated_at = ? WHERE card_key = ? AND account_id <> ?",
                    (now, card_key, account_id),
                )
            conn.execute(
                "UPDATE accounts SET card_key = ?, card_name = ?, enabled = ?, updated_at = ? WHERE account_id = ?",
                (card_key, card_name, 1 if enabled else 0, now, account_id),
            )

    def mapped_account_ids(self, item_id: str) -> set[str]:
        with self.db.connection() as conn:
            rows = conn.execute(
                "SELECT account_id FROM accounts WHERE item_id = ? AND enabled = 1",
                (item_id,),
            ).fetchall()
        return {str(r[0]) for r in rows}

    def record_sync_error(self, item_id: str, error_code: str) -> None:
        with self.db.transaction() as conn:
            conn.execute(
                "UPDATE plaid_items SET last_sync_error_code = ?, updated_at = ? WHERE item_id = ?",
                (error_code[:128], to_iso(utc_now()), item_id),
            )

    def disable_item(self, item_id: str) -> None:
        now = to_iso(utc_now())
        with self.db.transaction() as conn:
            conn.execute("UPDATE plaid_items SET active = 0, updated_at = ? WHERE item_id = ?", (now, item_id))
            conn.execute(
                "UPDATE accounts SET enabled = 0, card_key = NULL, card_name = NULL, updated_at = ? WHERE item_id = ?",
                (now, item_id),
            )


    def latest_sync_at(self, environment: str | None = None) -> datetime | None:
        with self.db.connection() as conn:
            if environment:
                row = conn.execute(
                    "SELECT MAX(last_synced_at) FROM plaid_items WHERE active = 1 AND environment = ?",
                    (environment,),
                ).fetchone()
            else:
                row = conn.execute("SELECT MAX(last_synced_at) FROM plaid_items WHERE active = 1").fetchone()
        return None if not row or row[0] is None else from_iso(str(row[0]))

    def items_with_errors(self, environment: str | None = None) -> list[PlaidItemRecord]:
        return [item for item in self.list_active_items(environment) if item.last_sync_error_code]


class TransactionRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def is_user_deleted(self, transaction_id: str) -> bool:
        with self.db.connection() as conn:
            row = conn.execute(
                "SELECT 1 FROM deleted_transactions WHERE transaction_id = ?",
                (transaction_id,),
            ).fetchone()
        return bool(row)

    def delete_by_user(self, transaction_id: str) -> None:
        now = to_iso(utc_now())
        with self.db.transaction() as conn:
            row = conn.execute(
                "SELECT 1 FROM transactions WHERE transaction_id = ? AND is_removed = 0",
                (transaction_id,),
            ).fetchone()
            if not row:
                raise ValueError("Unknown transaction.")
            conn.execute(
                "INSERT OR REPLACE INTO deleted_transactions(transaction_id, deleted_at) VALUES (?, ?)",
                (transaction_id, now),
            )
            conn.execute("DELETE FROM transactions WHERE transaction_id = ?", (transaction_id,))

    @staticmethod
    def _upsert(conn, row: dict) -> None:
        now = to_iso(utc_now())
        conn.execute(
            """
            INSERT INTO transactions(
                transaction_id, account_id, amount_cents, iso_currency_code,
                posted_date, authorized_date, budget_date, merchant_name, description,
                pending, pending_transaction_id, pfc_primary, pfc_detailed, pfc_confidence,
                is_removed, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
            ON CONFLICT(transaction_id) DO UPDATE SET
                account_id = excluded.account_id,
                amount_cents = excluded.amount_cents,
                iso_currency_code = excluded.iso_currency_code,
                posted_date = excluded.posted_date,
                authorized_date = excluded.authorized_date,
                budget_date = excluded.budget_date,
                merchant_name = excluded.merchant_name,
                description = excluded.description,
                pending = excluded.pending,
                pending_transaction_id = excluded.pending_transaction_id,
                pfc_primary = excluded.pfc_primary,
                pfc_detailed = excluded.pfc_detailed,
                pfc_confidence = excluded.pfc_confidence,
                is_removed = 0,
                updated_at = excluded.updated_at
            """,
            (
                row["transaction_id"], row["account_id"], row["amount_cents"], row["iso_currency_code"],
                row["posted_date"], row["authorized_date"], row["budget_date"], row["merchant_name"],
                row["description"], 1 if row["pending"] else 0, row["pending_transaction_id"],
                row["pfc_primary"], row["pfc_detailed"], row["pfc_confidence"], now, now,
            ),
        )
        pending_id = row.get("pending_transaction_id")
        if pending_id and not row["pending"]:
            conn.execute(
                "UPDATE transactions SET is_removed = 1, updated_at = ? WHERE transaction_id = ?",
                (now, pending_id),
            )

    def apply_sync_batch(
        self,
        *,
        item_id: str,
        added: list[dict],
        modified: list[dict],
        removed_transaction_ids: list[str],
        next_cursor: str,
        update_status: str | None,
        synced_at: datetime,
    ) -> None:
        now = to_iso(utc_now())
        with self.db.transaction() as conn:
            for row in added:
                self._upsert(conn, row)
            for row in modified:
                self._upsert(conn, row)
            for transaction_id in removed_transaction_ids:
                conn.execute(
                    "UPDATE transactions SET is_removed = 1, updated_at = ? WHERE transaction_id = ?",
                    (now, transaction_id),
                )
            conn.execute(
                """
                UPDATE plaid_items
                SET sync_cursor = ?, transactions_update_status = ?, last_synced_at = ?,
                    last_sync_error_code = NULL, updated_at = ?
                WHERE item_id = ?
                """,
                (next_cursor, update_status, to_iso(synced_at), now, item_id),
            )

    def apply_backfill_batch(self, rows: list[dict]) -> None:
        with self.db.transaction() as conn:
            for row in rows:
                deleted = conn.execute(
                    "SELECT 1 FROM deleted_transactions WHERE transaction_id = ?",
                    (row["transaction_id"],),
                ).fetchone()
                if deleted:
                    continue
                self._upsert(conn, row)

    @staticmethod
    def _record(row) -> TransactionRecord:
        return TransactionRecord(
            transaction_id=str(row[0]), account_id=str(row[1]),
            card_name=None if row[2] is None else str(row[2]), amount_cents=int(row[3]),
            iso_currency_code=str(row[4]), posted_date=None if row[5] is None else str(row[5]),
            authorized_date=None if row[6] is None else str(row[6]), budget_date=None if row[7] is None else str(row[7]),
            merchant_name=None if row[8] is None else str(row[8]), description=str(row[9]),
            pending=bool(row[10]), pfc_primary=None if row[11] is None else str(row[11]),
            pfc_detailed=None if row[12] is None else str(row[12]), bucket_id=None if row[13] is None else int(row[13]),
            bucket_name=None if row[14] is None else str(row[14]),
            classification_source=None if row[15] is None else str(row[15]),
            classification_confidence=None if row[16] is None else float(row[16]),
        )

    def _select(self, where: str = "", params: tuple = (), limit: int = 100) -> list[TransactionRecord]:
        safe_limit = min(max(int(limit), 1), 500)
        sql = """
            SELECT t.transaction_id, t.account_id, a.card_name, t.amount_cents,
                   t.iso_currency_code, t.posted_date, t.authorized_date, t.budget_date,
                   t.merchant_name, t.description, t.pending, t.pfc_primary, t.pfc_detailed,
                   t.bucket_id, b.name, t.classification_source, t.classification_confidence
            FROM transactions t
            JOIN accounts a ON a.account_id = t.account_id
            LEFT JOIN buckets b ON b.id = t.bucket_id
            WHERE t.is_removed = 0
        """ + where + " ORDER BY COALESCE(t.budget_date, t.posted_date) DESC, t.created_at DESC LIMIT ?"
        with self.db.connection() as conn:
            rows = conn.execute(sql, (*params, safe_limit)).fetchall()
        return [self._record(r) for r in rows]

    def list_recent(self, limit: int = 100, month: str | None = None) -> list[TransactionRecord]:
        if month:
            datetime.strptime(month, "%Y-%m")
            return self._select(" AND t.budget_date LIKE ?", (f"{month}-%",), limit)
        return self._select(limit=limit)

    def list_for_bucket(self, bucket_id: int, month: str, limit: int = 500) -> list[TransactionRecord]:
        datetime.strptime(month, "%Y-%m")
        bucket = None
        with self.db.connection() as conn:
            bucket = conn.execute("SELECT name FROM buckets WHERE id = ?", (bucket_id,)).fetchone()
        if bucket and str(bucket[0]).lower() == "unknown":
            return self._select(
                " AND (t.bucket_id = ? OR t.bucket_id IS NULL) AND t.budget_date LIKE ? AND t.pending = 0",
                (bucket_id, f"{month}-%"),
                limit,
            )
        return self._select(
            " AND t.bucket_id = ? AND t.budget_date LIKE ? AND t.pending = 0",
            (bucket_id, f"{month}-%"),
            limit,
        )

    def count_for_month(self, month: str) -> int:
        datetime.strptime(month, "%Y-%m")
        with self.db.connection() as conn:
            row = conn.execute(
                "SELECT count(*) FROM transactions WHERE is_removed = 0 AND pending = 0 AND budget_date LIKE ?",
                (f"{month}-%",),
            ).fetchone()
        return int(row[0])

    def list_unassigned(self, limit: int = 200) -> list[TransactionRecord]:
        return self._select(" AND t.bucket_id IS NULL AND t.pending = 0 AND t.classification_source IS NULL", (), limit)

    def get(self, transaction_id: str) -> TransactionRecord | None:
        rows = self._select(" AND t.transaction_id = ?", (transaction_id,), 1)
        return rows[0] if rows else None

    def assign_bucket(self, transaction_id: str, bucket_id: int | None, *, source: str, confidence: float) -> None:
        with self.db.transaction() as conn:
            cur = conn.execute(
                "UPDATE transactions SET bucket_id = ?, classification_source = ?, classification_confidence = ?, updated_at = ? WHERE transaction_id = ? AND is_removed = 0",
                (bucket_id, source[:40], max(0.0, min(1.0, confidence)), to_iso(utc_now()), transaction_id),
            )
            if cur.rowcount == 0:
                raise ValueError("Unknown transaction.")

    def mark_uncategorized(self, transaction_id: str, *, source: str) -> None:
        with self.db.transaction() as conn:
            conn.execute(
                "UPDATE transactions SET bucket_id = NULL, classification_source = ?, classification_confidence = 0, updated_at = ? WHERE transaction_id = ?",
                (source[:40], to_iso(utc_now()), transaction_id),
            )

    def uncategorized_count(self, month: str | None = None) -> int:
        params: tuple = ()
        month_clause = ""
        if month:
            datetime.strptime(month, "%Y-%m")
            month_clause = " AND budget_date LIKE ?"
            params = (f"{month}-%",)
        with self.db.connection() as conn:
            row = conn.execute(
                "SELECT count(*) FROM transactions WHERE is_removed = 0 AND pending = 0 AND bucket_id IS NULL" + month_clause,
                params,
            ).fetchone()
        return int(row[0])


class MerchantRuleRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def get_by_key(self, key: str) -> MerchantRuleRecord | None:
        with self.db.connection() as conn:
            row = conn.execute(
                """
                SELECT m.id, m.merchant_key, m.display_name, m.bucket_id, b.name
                FROM merchant_rules m JOIN buckets b ON b.id = m.bucket_id
                WHERE m.merchant_key = ? AND b.active = 1
                """,
                (key,),
            ).fetchone()
        if not row:
            return None
        return MerchantRuleRecord(int(row[0]), str(row[1]), str(row[2]), int(row[3]), str(row[4]))

    def upsert(self, key: str, display_name: str, bucket_id: int) -> None:
        now = to_iso(utc_now())
        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO merchant_rules(merchant_key, display_name, bucket_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(merchant_key) DO UPDATE SET
                    display_name = excluded.display_name,
                    bucket_id = excluded.bucket_id,
                    updated_at = excluded.updated_at
                """,
                (key, display_name[:160], bucket_id, now, now),
            )

    def delete(self, rule_id: int) -> None:
        with self.db.transaction() as conn:
            cur = conn.execute("DELETE FROM merchant_rules WHERE id = ?", (rule_id,))
            if cur.rowcount == 0:
                raise ValueError("Unknown merchant rule.")

    def list_all(self) -> list[MerchantRuleRecord]:
        with self.db.connection() as conn:
            rows = conn.execute(
                """
                SELECT m.id, m.merchant_key, m.display_name, m.bucket_id, b.name
                FROM merchant_rules m JOIN buckets b ON b.id = m.bucket_id
                ORDER BY m.display_name COLLATE NOCASE
                """
            ).fetchall()
        return [MerchantRuleRecord(int(r[0]), str(r[1]), str(r[2]), int(r[3]), str(r[4])) for r in rows]


@dataclass(frozen=True)
class AssetRecord:
    id: int
    name: str
    institution: str | None
    current_value_cents: int
    asset_bucket: str
    include_in_net_worth: bool


@dataclass(frozen=True)
class LiabilityRecord:
    id: int
    name: str
    institution: str | None
    current_balance_cents: int
    include_in_net_worth: bool


@dataclass(frozen=True)
class AssetAllocationRecord:
    asset_bucket: str
    value_cents: int


class NetWorthRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    @staticmethod
    def _clean_text(value: str, *, required: bool, max_length: int = 120) -> str | None:
        clean = " ".join((value or "").strip().split())
        if required and not clean:
            raise ValueError("Name is required.")
        if len(clean) > max_length:
            raise ValueError(f"Value must be {max_length} characters or fewer.")
        return clean or None

    @staticmethod
    def _asset_record(row) -> AssetRecord:
        return AssetRecord(
            id=int(row[0]), name=str(row[1]), institution=None if row[2] is None else str(row[2]),
            current_value_cents=int(row[3]), asset_bucket=str(row[4]), include_in_net_worth=bool(row[5]),
        )

    @staticmethod
    def _liability_record(row) -> LiabilityRecord:
        return LiabilityRecord(
            id=int(row[0]), name=str(row[1]), institution=None if row[2] is None else str(row[2]),
            current_balance_cents=int(row[3]), include_in_net_worth=bool(row[4]),
        )

    def list_assets(self) -> list[AssetRecord]:
        with self.db.connection() as conn:
            rows = conn.execute(
                "SELECT id, name, institution, current_value_cents, asset_bucket, include_in_net_worth FROM assets ORDER BY id"
            ).fetchall()
        return [self._asset_record(row) for row in rows]

    def get_asset(self, asset_id: int) -> AssetRecord | None:
        with self.db.connection() as conn:
            row = conn.execute(
                "SELECT id, name, institution, current_value_cents, asset_bucket, include_in_net_worth FROM assets WHERE id = ?",
                (asset_id,),
            ).fetchone()
        return None if not row else self._asset_record(row)

    def create_asset(self, *, name: str, institution: str, value_cents: int, asset_bucket: str, include: bool) -> AssetRecord:
        from cardbudget.db.schema import ASSET_BUCKETS
        clean_name = self._clean_text(name, required=True)
        clean_institution = self._clean_text(institution, required=False)
        if value_cents < 0:
            raise ValueError("Asset value cannot be negative.")
        if asset_bucket not in ASSET_BUCKETS:
            raise ValueError("Unknown asset category.")
        now = to_iso(utc_now())
        with self.db.transaction() as conn:
            cur = conn.execute(
                "INSERT INTO assets(name, institution, current_value_cents, asset_bucket, include_in_net_worth, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (clean_name, clean_institution, value_cents, asset_bucket, 1 if include else 0, now, now),
            )
            asset_id = int(cur.lastrowid)
        return self.get_asset(asset_id)  # type: ignore[return-value]

    def update_asset(self, asset_id: int, *, name: str, institution: str, value_cents: int, asset_bucket: str, include: bool) -> None:
        from cardbudget.db.schema import ASSET_BUCKETS
        clean_name = self._clean_text(name, required=True)
        clean_institution = self._clean_text(institution, required=False)
        if value_cents < 0:
            raise ValueError("Asset value cannot be negative.")
        if asset_bucket not in ASSET_BUCKETS:
            raise ValueError("Unknown asset category.")
        with self.db.transaction() as conn:
            cur = conn.execute(
                "UPDATE assets SET name = ?, institution = ?, current_value_cents = ?, asset_bucket = ?, include_in_net_worth = ?, updated_at = ? WHERE id = ?",
                (clean_name, clean_institution, value_cents, asset_bucket, 1 if include else 0, to_iso(utc_now()), asset_id),
            )
            if cur.rowcount == 0:
                raise ValueError("Unknown asset.")

    def delete_asset(self, asset_id: int) -> None:
        with self.db.transaction() as conn:
            cur = conn.execute("DELETE FROM assets WHERE id = ?", (asset_id,))
            if cur.rowcount == 0:
                raise ValueError("Unknown asset.")

    def list_liabilities(self) -> list[LiabilityRecord]:
        with self.db.connection() as conn:
            rows = conn.execute(
                "SELECT id, name, institution, current_balance_cents, include_in_net_worth FROM liabilities ORDER BY id"
            ).fetchall()
        return [self._liability_record(row) for row in rows]

    def get_liability(self, liability_id: int) -> LiabilityRecord | None:
        with self.db.connection() as conn:
            row = conn.execute(
                "SELECT id, name, institution, current_balance_cents, include_in_net_worth FROM liabilities WHERE id = ?",
                (liability_id,),
            ).fetchone()
        return None if not row else self._liability_record(row)

    def create_liability(self, *, name: str, institution: str, balance_cents: int, include: bool) -> LiabilityRecord:
        clean_name = self._clean_text(name, required=True)
        clean_institution = self._clean_text(institution, required=False)
        if balance_cents < 0:
            raise ValueError("Liability balance cannot be negative.")
        now = to_iso(utc_now())
        with self.db.transaction() as conn:
            cur = conn.execute(
                "INSERT INTO liabilities(name, institution, current_balance_cents, include_in_net_worth, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (clean_name, clean_institution, balance_cents, 1 if include else 0, now, now),
            )
            liability_id = int(cur.lastrowid)
        return self.get_liability(liability_id)  # type: ignore[return-value]

    def update_liability(self, liability_id: int, *, name: str, institution: str, balance_cents: int, include: bool) -> None:
        clean_name = self._clean_text(name, required=True)
        clean_institution = self._clean_text(institution, required=False)
        if balance_cents < 0:
            raise ValueError("Liability balance cannot be negative.")
        with self.db.transaction() as conn:
            cur = conn.execute(
                "UPDATE liabilities SET name = ?, institution = ?, current_balance_cents = ?, include_in_net_worth = ?, updated_at = ? WHERE id = ?",
                (clean_name, clean_institution, balance_cents, 1 if include else 0, to_iso(utc_now()), liability_id),
            )
            if cur.rowcount == 0:
                raise ValueError("Unknown liability.")

    def delete_liability(self, liability_id: int) -> None:
        with self.db.transaction() as conn:
            cur = conn.execute("DELETE FROM liabilities WHERE id = ?", (liability_id,))
            if cur.rowcount == 0:
                raise ValueError("Unknown liability.")

    def totals(self) -> tuple[int, int, int]:
        with self.db.connection() as conn:
            assets = int(conn.execute("SELECT COALESCE(SUM(current_value_cents), 0) FROM assets WHERE include_in_net_worth = 1").fetchone()[0])
            liabilities = int(conn.execute("SELECT COALESCE(SUM(current_balance_cents), 0) FROM liabilities WHERE include_in_net_worth = 1").fetchone()[0])
        return assets, liabilities, assets - liabilities

    def allocation(self) -> list[AssetAllocationRecord]:
        with self.db.connection() as conn:
            rows = conn.execute(
                "SELECT asset_bucket, COALESCE(SUM(current_value_cents), 0) FROM assets WHERE include_in_net_worth = 1 GROUP BY asset_bucket ORDER BY asset_bucket"
            ).fetchall()
        return [AssetAllocationRecord(str(row[0]), int(row[1])) for row in rows]

    def get_rule(self, asset_key: str) -> str | None:
        with self.db.connection() as conn:
            row = conn.execute("SELECT asset_bucket FROM asset_rules WHERE asset_key = ?", (asset_key,)).fetchone()
        return None if not row else str(row[0])

    def upsert_rule(self, asset_key: str, display_name: str, asset_bucket: str) -> None:
        from cardbudget.db.schema import ASSET_BUCKETS
        if asset_bucket not in ASSET_BUCKETS:
            raise ValueError("Unknown asset category.")
        now = to_iso(utc_now())
        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO asset_rules(asset_key, display_name, asset_bucket, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(asset_key) DO UPDATE SET display_name = excluded.display_name, asset_bucket = excluded.asset_bucket, updated_at = excluded.updated_at
                """,
                (asset_key[:200], display_name[:160], asset_bucket, now, now),
            )
