from __future__ import annotations

import calendar
import re
import threading
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from cardbudget.db.repositories import PlaidRepository, TransactionRepository, utc_now
from cardbudget.plaid.client import HTTPPlaidTransport, PlaidAPIError, PlaidClient
from cardbudget.security.keychain import SecretStore

PLAID_CLIENT_ID = "plaid-client-id"
PLAID_SECRET = "plaid-secret"  # legacy Sandbox key name


def plaid_secret_key(environment: str) -> str:
    return f"plaid-secret:{environment}"



def access_token_key(environment: str, item_id: str) -> str:
    return f"plaid-access-token:{environment}:{item_id}"


def _amount_to_cents(value: Any) -> int:
    amount = Decimal(str(value or "0"))
    return int((amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _date_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    date.fromisoformat(text)
    return text


_PAYMENT_TEXT_PATTERNS = (
    re.compile(r"\bAUTO\s*PAY\b", re.I),
    re.compile(r"\bAUTOPAY\b", re.I),
    re.compile(r"\bAUTOPAY\b.*\bPAYMENT\b", re.I),
    re.compile(r"\bAUTOMATIC\b.*\bPAYMENT\b", re.I),
    re.compile(r"\bPAYMENT\b.*\bTHANK\s*YOU\b", re.I),
    re.compile(r"\bONLINE\b.*\bPAYMENT\b", re.I),
    re.compile(r"\bMOBILE\b.*\bPAY(?:MENT|MT)\b", re.I),
    re.compile(r"\bPAYMENT\s+RECEIVED\b", re.I),
    re.compile(r"\bCARD\s+PAYMENT\b", re.I),
)


def ignore_reason(tx: dict[str, Any]) -> str | None:
    """Return why a raw Plaid transaction should not enter the spending store.

    PocketTrack is intentionally a spending monitor, not a statement ledger. Pending
    rows and credit-card payment/autopay rows are therefore ignored. Refunds remain
    visible because they reduce net spend for the month.
    """
    if bool(tx.get("pending")):
        return "pending"

    pfc = tx.get("personal_finance_category") or {}
    primary = str(pfc.get("primary") or "").upper()
    detailed = str(pfc.get("detailed") or "").upper()
    transaction_code = str(tx.get("transaction_code") or "").strip().lower()
    description = " ".join(
        str(value or "") for value in (tx.get("name"), tx.get("merchant_name"), tx.get("original_description"))
    )

    if "CREDIT_CARD_PAYMENT" in detailed:
        return "payment"
    if primary.startswith("TRANSFER") and ("ACCOUNT_TRANSFER" in detailed or "PAYMENT" in detailed):
        return "payment"
    if transaction_code in {"payment", "bill payment", "transfer"}:
        # Only treat generic transaction codes as a payment when the description
        # also resembles a card payment; this avoids hiding purchases made through
        # payment services such as PayPal/Venmo.
        if any(pattern.search(description) for pattern in _PAYMENT_TEXT_PATTERNS):
            return "payment"
    if any(pattern.search(description) for pattern in _PAYMENT_TEXT_PATTERNS):
        return "payment"
    return None


@dataclass(frozen=True)
class SyncResult:
    items_synced: int
    failed_items: int
    added: int
    modified: int
    removed: int
    ignored_unmapped: int
    ignored_pending: int = 0
    ignored_payments: int = 0
    ignored_deleted: int = 0


@dataclass(frozen=True)
class BackfillResult:
    month: str
    items_synced: int
    failed_items: int
    imported: int
    ignored_unmapped: int
    ignored_pending: int
    ignored_payments: int
    ignored_deleted: int


class PlaidService:
    def __init__(
        self,
        *,
        secret_store: SecretStore,
        plaid_repository: PlaidRepository,
        transactions: TransactionRepository,
        environment: str = "sandbox",
        client_factory=None,
    ) -> None:
        self.secret_store = secret_store
        self.plaid_repository = plaid_repository
        self.transactions = transactions
        self.environment = environment
        self._client_factory = client_factory
        self._sync_lock = threading.Lock()

    def credentials_configured(self) -> bool:
        return bool(self.secret_store.get_secret(PLAID_CLIENT_ID) and self._get_environment_secret())

    def save_credentials(self, client_id: str, secret: str) -> None:
        client_id = client_id.strip()
        secret = secret.strip()
        if not client_id or len(client_id) > 256:
            raise ValueError("Plaid client ID is required.")
        if not secret or len(secret) > 512:
            raise ValueError("Plaid secret is required.")
        self.secret_store.set_secret(PLAID_CLIENT_ID, client_id)
        self.secret_store.set_secret(plaid_secret_key(self.environment), secret)

    def _get_environment_secret(self) -> str | None:
        secret = self.secret_store.get_secret(plaid_secret_key(self.environment))
        if not secret and self.environment == "sandbox":
            secret = self.secret_store.get_secret(PLAID_SECRET)
            if secret:
                self.secret_store.set_secret(plaid_secret_key("sandbox"), secret)
        return secret

    def _client(self) -> PlaidClient:
        client_id = self.secret_store.get_secret(PLAID_CLIENT_ID)
        secret = self._get_environment_secret()
        if not client_id or not secret:
            raise ValueError("Plaid credentials are not configured.")
        if self._client_factory:
            return self._client_factory(client_id, secret, self.environment)
        return PlaidClient(HTTPPlaidTransport(client_id, secret, self.environment))

    def create_link_token(self, user_id: int) -> str:
        return self._client().create_link_token(client_user_id=f"pockettrack-user-{user_id}")

    def create_update_link_token(self, user_id: int, item_id: str) -> str:
        item = self.plaid_repository.get_item(item_id, self.environment)
        if not item:
            raise ValueError("Unknown Plaid connection.")
        access_token = self.secret_store.get_secret(access_token_key(self.environment, item_id))
        if not access_token:
            raise ValueError("Plaid access token is missing from the OS keychain.")
        return self._client().create_update_link_token(
            client_user_id=f"pockettrack-user-{user_id}", access_token=access_token
        )

    def refresh_item_accounts(self, item_id: str) -> None:
        item = self.plaid_repository.get_item(item_id, self.environment)
        if not item:
            raise ValueError("Unknown Plaid connection.")
        access_token = self.secret_store.get_secret(access_token_key(self.environment, item_id))
        if not access_token:
            raise ValueError("Plaid access token is missing from the OS keychain.")
        client = self._client()
        item_response = client.get_item(access_token)
        remote_item = item_response.get("item") or {}
        self.plaid_repository.upsert_item(
            item_id=item_id,
            institution_id=(remote_item.get("institution_id") or item.institution_id),
            institution_name=item.institution_name,
            environment=self.environment,
        )
        self.plaid_repository.replace_accounts(item_id, client.get_accounts(access_token))

    def exchange_and_register(
        self,
        public_token: str,
        *,
        link_institution_id: str | None = None,
        link_institution_name: str | None = None,
    ) -> str:
        if not public_token or len(public_token) > 2048:
            raise ValueError("Invalid public token.")
        client = self._client()
        access_token, item_id = client.exchange_public_token(public_token)
        key = access_token_key(self.environment, item_id)
        self.secret_store.set_secret(key, access_token)
        try:
            item_response = client.get_item(access_token)
            item = item_response.get("item") or {}
            institution_id = item.get("institution_id") or link_institution_id
            institution_name = item.get("institution_name") or link_institution_name
            if institution_id is not None and len(str(institution_id)) > 160:
                institution_id = None
            if institution_name is not None and len(str(institution_name)) > 160:
                institution_name = None
            self.plaid_repository.upsert_item(
                item_id=item_id,
                institution_id=None if institution_id is None else str(institution_id),
                institution_name=None if institution_name is None else str(institution_name),
                environment=self.environment,
            )
            self.plaid_repository.replace_accounts(item_id, client.get_accounts(access_token))
        except Exception:
            self.secret_store.delete_secret(key)
            raise
        return item_id

    def set_account_enabled(self, account_id: str, enabled: bool) -> None:
        account = self.plaid_repository.get_account(account_id, self.environment)
        if not account:
            raise ValueError("Unknown Plaid account.")
        if account.account_type != "credit":
            raise ValueError("PocketTrack can only track credit-card accounts.")
        if not enabled:
            self.plaid_repository.map_account(account_id, None, None, False)
            return
        display_name = (account.official_name or account.name or "Credit card").strip()
        # account_id is used only as a stable internal key. The user-visible card
        # name comes directly from Plaid, so PocketTrack works for any issuer/card.
        self.plaid_repository.map_account(account_id, account_id, display_name, True)

    def map_account(self, account_id: str, card_key: str | None) -> None:
        """Compatibility wrapper for older CardBudget/PocketTrack installs."""
        self.set_account_enabled(account_id, card_key not in {"", "ignore", None})

    def disconnect_item(self, item_id: str) -> None:
        self.secret_store.delete_secret(access_token_key(self.environment, item_id))
        self.plaid_repository.disable_item(item_id)

    def sync_all(self) -> SyncResult:
        if not self._sync_lock.acquire(blocking=False):
            raise RuntimeError("A transaction sync is already running.")
        totals = {
            "items_synced": 0,
            "failed_items": 0,
            "added": 0,
            "modified": 0,
            "removed": 0,
            "ignored_unmapped": 0,
            "ignored_pending": 0,
            "ignored_payments": 0,
            "ignored_deleted": 0,
        }
        try:
            for item in self.plaid_repository.list_active_items(self.environment):
                try:
                    result = self._sync_item(item.item_id, item.sync_cursor)
                except PlaidAPIError:
                    totals["failed_items"] += 1
                    continue
                if result.get("missing_access_token"):
                    totals["failed_items"] += 1
                    continue
                totals["items_synced"] += 1
                for key in totals:
                    if key not in {"items_synced", "failed_items"}:
                        totals[key] += int(result.get(key, 0))
            return SyncResult(**totals)
        finally:
            self._sync_lock.release()

    def _sync_item(self, item_id: str, starting_cursor: str | None) -> dict[str, int]:
        access_token = self.secret_store.get_secret(access_token_key(self.environment, item_id))
        if not access_token:
            self.plaid_repository.record_sync_error(item_id, "MISSING_ACCESS_TOKEN")
            return {"missing_access_token": 1}

        client = self._client()
        cursor = starting_cursor
        all_added: list[dict[str, Any]] = []
        all_modified: list[dict[str, Any]] = []
        all_removed: list[dict[str, Any]] = []
        update_status: str | None = None
        try:
            while True:
                response = client.sync_transactions(access_token, cursor)
                all_added.extend(response.get("added") or [])
                all_modified.extend(response.get("modified") or [])
                all_removed.extend(response.get("removed") or [])
                cursor = str(response.get("next_cursor") or "")
                update_status = str(response.get("transactions_update_status") or "") or None
                if not response.get("has_more"):
                    break
        except PlaidAPIError as exc:
            self.plaid_repository.record_sync_error(item_id, exc.error_code)
            raise

        mapped_ids = self.plaid_repository.mapped_account_ids(item_id)
        counters = {"ignored_unmapped": 0, "ignored_pending": 0, "ignored_payments": 0, "ignored_deleted": 0}
        normalized_added: list[dict[str, Any]] = []
        normalized_modified: list[dict[str, Any]] = []
        filtered_existing_ids: list[str] = []

        for source, destination in ((all_added, normalized_added), (all_modified, normalized_modified)):
            for tx in source:
                account_id = str(tx.get("account_id") or "")
                if account_id not in mapped_ids:
                    counters["ignored_unmapped"] += 1
                    continue
                transaction_id = str(tx.get("transaction_id") or "")
                if transaction_id and self.transactions.is_user_deleted(transaction_id):
                    counters["ignored_deleted"] += 1
                    continue
                reason = ignore_reason(tx)
                if reason:
                    counters[f"ignored_{'pending' if reason == 'pending' else 'payments'}"] += 1
                    if source is all_modified and transaction_id:
                        filtered_existing_ids.append(transaction_id)
                    continue
                destination.append(self._normalize_transaction(tx))

        removed_ids = [
            str(row.get("transaction_id"))
            for row in all_removed
            if str(row.get("account_id") or "") in mapped_ids and row.get("transaction_id")
        ]
        removed_ids.extend(filtered_existing_ids)

        self.transactions.apply_sync_batch(
            item_id=item_id,
            added=normalized_added,
            modified=normalized_modified,
            removed_transaction_ids=list(dict.fromkeys(removed_ids)),
            next_cursor=cursor,
            update_status=update_status,
            synced_at=utc_now(),
        )
        return {
            "added": len(normalized_added),
            "modified": len(normalized_modified),
            "removed": len(set(removed_ids)),
            **counters,
        }

    def backfill_month(self, month: str) -> BackfillResult:
        try:
            parsed = datetime.strptime(month, "%Y-%m")
        except ValueError as exc:
            raise ValueError("Month must use YYYY-MM format.") from exc
        start_date = date(parsed.year, parsed.month, 1)
        end_date = date(parsed.year, parsed.month, calendar.monthrange(parsed.year, parsed.month)[1])

        if not self._sync_lock.acquire(blocking=False):
            raise RuntimeError("A transaction sync is already running.")
        totals = {
            "items_synced": 0,
            "failed_items": 0,
            "imported": 0,
            "ignored_unmapped": 0,
            "ignored_pending": 0,
            "ignored_payments": 0,
            "ignored_deleted": 0,
        }
        try:
            client = self._client()
            for item in self.plaid_repository.list_active_items(self.environment):
                access_token = self.secret_store.get_secret(access_token_key(self.environment, item.item_id))
                if not access_token:
                    totals["failed_items"] += 1
                    continue
                mapped_ids = self.plaid_repository.mapped_account_ids(item.item_id)
                offset = 0
                normalized: list[dict[str, Any]] = []
                try:
                    while True:
                        response = client.get_transactions(
                            access_token,
                            start_date.isoformat(),
                            end_date.isoformat(),
                            offset=offset,
                            count=500,
                        )
                        rows = list(response.get("transactions") or [])
                        for tx in rows:
                            account_id = str(tx.get("account_id") or "")
                            if account_id not in mapped_ids:
                                totals["ignored_unmapped"] += 1
                                continue
                            transaction_id = str(tx.get("transaction_id") or "")
                            if transaction_id and self.transactions.is_user_deleted(transaction_id):
                                totals["ignored_deleted"] += 1
                                continue
                            reason = ignore_reason(tx)
                            if reason == "pending":
                                totals["ignored_pending"] += 1
                                continue
                            if reason == "payment":
                                totals["ignored_payments"] += 1
                                continue
                            normalized.append(self._normalize_transaction(tx))
                        total = int(response.get("total_transactions") or len(rows))
                        offset += len(rows)
                        if not rows or offset >= total:
                            break
                except PlaidAPIError:
                    totals["failed_items"] += 1
                    continue
                self.transactions.apply_backfill_batch(normalized)
                totals["imported"] += len(normalized)
                totals["items_synced"] += 1
            return BackfillResult(month=month, **totals)
        finally:
            self._sync_lock.release()

    @staticmethod
    def _normalize_transaction(tx: dict[str, Any]) -> dict[str, Any]:
        pfc = tx.get("personal_finance_category") or {}
        posted_date = _date_text(tx.get("date"))
        authorized_date = _date_text(tx.get("authorized_date"))
        return {
            "transaction_id": str(tx["transaction_id"]),
            "account_id": str(tx["account_id"]),
            "amount_cents": _amount_to_cents(tx.get("amount")),
            "iso_currency_code": str(tx.get("iso_currency_code") or tx.get("unofficial_currency_code") or "USD"),
            "posted_date": posted_date,
            "authorized_date": authorized_date,
            "budget_date": authorized_date or posted_date,
            "merchant_name": None if tx.get("merchant_name") is None else str(tx.get("merchant_name")),
            "description": str(tx.get("name") or ""),
            "pending": False,
            "pending_transaction_id": None if tx.get("pending_transaction_id") is None else str(tx.get("pending_transaction_id")),
            "pfc_primary": None if pfc.get("primary") is None else str(pfc.get("primary")),
            "pfc_detailed": None if pfc.get("detailed") is None else str(pfc.get("detailed")),
            "pfc_confidence": None if pfc.get("confidence_level") is None else str(pfc.get("confidence_level")),
        }
