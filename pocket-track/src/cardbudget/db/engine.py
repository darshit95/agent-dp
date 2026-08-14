from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator

from cardbudget.db.schema import ADDED_COLUMNS, CORE_SCHEMA_SQL, DEFAULT_BUCKETS, SCHEMA_VERSION
from cardbudget.errors import DatabaseOpenError, EncryptionUnavailable

Connector = Callable[[str], Any]


def ensure_private_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    if os.name == "posix":
        os.chmod(path, 0o700)


def _utc_now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


class Database:
    """SQLCipher database wrapper.

    Production defaults to SQLCipher and fails closed if it is unavailable. Tests
    can inject sqlite3.connect with require_cipher=False; that path is never chosen
    by application bootstrap.
    """

    def __init__(
        self,
        path: Path,
        key_hex: str,
        *,
        connector: Connector | None = None,
        require_cipher: bool = True,
    ) -> None:
        self.path = path
        self.key_hex = key_hex
        self.require_cipher = require_cipher
        self._connector = connector

    def _default_connector(self) -> Connector:
        try:
            from sqlcipher3 import dbapi2 as sqlcipher
        except Exception as exc:  # pragma: no cover - depends on installed package
            raise EncryptionUnavailable(
                "SQLCipher Python binding is unavailable. Install project dependencies; "
                "PocketTrack will not use plaintext SQLite as a fallback."
            ) from exc
        return sqlcipher.connect

    def _connect_raw(self):
        connector = self._connector or self._default_connector()
        try:
            conn = connector(str(self.path))
        except TypeError:
            # Some DB-API connectors prefer Path-like objects.
            conn = connector(self.path)

        try:
            if self.require_cipher:
                if len(self.key_hex) != 64:
                    raise DatabaseOpenError("SQLCipher key has an invalid length.")
                bytes.fromhex(self.key_hex)
                conn.execute(f"PRAGMA key = \"x'{self.key_hex}'\"")
                version_row = conn.execute("PRAGMA cipher_version").fetchone()
                version = version_row[0] if version_row else None
                if not version:
                    raise EncryptionUnavailable(
                        "Database driver does not report SQLCipher support; refusing plaintext mode."
                    )
                conn.execute("PRAGMA cipher_memory_security = ON")
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA secure_delete = ON")
            conn.execute("PRAGMA journal_mode = DELETE")
            conn.execute("PRAGMA busy_timeout = 5000")
            # This forces SQLCipher to actually read/decrypt page 1. A wrong key
            # should fail here rather than later during a request.
            conn.execute("SELECT count(*) FROM sqlite_master").fetchone()
            return conn
        except Exception as exc:
            try:
                conn.close()
            except Exception:
                pass
            if isinstance(exc, EncryptionUnavailable):
                raise
            if isinstance(exc, DatabaseOpenError):
                raise
            raise DatabaseOpenError(
                "Encrypted database could not be opened. The original file was left untouched."
            ) from exc

    @contextmanager
    def connection(self) -> Iterator[Any]:
        conn = self._connect_raw()
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def transaction(self) -> Iterator[Any]:
        with self.connection() as conn:
            try:
                conn.execute("BEGIN IMMEDIATE")
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise

    def initialize(self) -> None:
        ensure_private_directory(self.path.parent)
        existed = self.path.exists()
        with self.transaction() as conn:
            conn.executescript(CORE_SCHEMA_SQL)
            self._add_missing_columns(conn)
            now = _utc_now_iso()
            conn.execute(
                "INSERT OR REPLACE INTO app_meta(key, value) VALUES ('schema_version', ?)",
                (str(SCHEMA_VERSION),),
            )
            for bucket_name in DEFAULT_BUCKETS:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO buckets(name, default_budget_cents, active, created_at, updated_at)
                    VALUES (?, NULL, 1, ?, ?)
                    """,
                    (bucket_name, now, now),
                )

            # v0.3 intentionally does not display/store pending transactions.
            # Remove any pending rows imported by earlier releases.
            conn.execute("DELETE FROM transactions WHERE pending = 1")

            # Hide obvious credit-card payment/autopay rows imported by earlier
            # releases. Future syncs filter these before they reach the DB.
            conn.execute(
                """
                UPDATE transactions
                   SET is_removed = 1, updated_at = ?
                 WHERE is_removed = 0
                   AND (
                       UPPER(COALESCE(pfc_detailed, '')) LIKE '%CREDIT_CARD_PAYMENT%'
                       OR (UPPER(COALESCE(pfc_primary, '')) LIKE 'TRANSFER%'
                           AND UPPER(COALESCE(pfc_detailed, '')) LIKE '%ACCOUNT_TRANSFER%')
                       OR UPPER(description) LIKE '%AUTOPAY%PAYMENT%'
                       OR UPPER(description) LIKE '%AUTOMATIC%PAYMENT%'
                       OR UPPER(description) LIKE '%PAYMENT%THANK%YOU%'
                       OR UPPER(description) LIKE '%ONLINE%PAYMENT%'
                       OR UPPER(description) LIKE '%MOBILE%PYMT%'
                       OR UPPER(description) LIKE '%MOBILE%PAYMENT%'
                   )
                """,
                (now,),
            )
        if os.name == "posix" and self.path.exists():
            os.chmod(self.path, 0o600)
        if not existed and self.require_cipher and self.has_plaintext_sqlite_header():
            raise EncryptionUnavailable(
                "New database has a plaintext SQLite header; refusing to continue."
            )

    @staticmethod
    def _add_missing_columns(conn) -> None:
        """Bring an existing database up to date with columns added post-release."""
        for table, column, definition in ADDED_COLUMNS:
            existing = {str(row[1]) for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
            if not existing or column in existing:
                continue
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def cipher_version(self) -> str | None:
        if not self.require_cipher:
            return None
        with self.connection() as conn:
            row = conn.execute("PRAGMA cipher_version").fetchone()
            return str(row[0]) if row and row[0] else None

    def integrity_check(self) -> bool:
        with self.connection() as conn:
            row = conn.execute("PRAGMA integrity_check").fetchone()
            return bool(row and str(row[0]).lower() == "ok")

    def has_plaintext_sqlite_header(self) -> bool:
        if not self.path.exists() or self.path.stat().st_size < 16:
            return False
        with self.path.open("rb") as fh:
            return fh.read(16) == b"SQLite format 3\x00"

    def standard_sqlite_is_rejected(self) -> bool:
        """Return True only when standard SQLite cannot read sqlite_master."""
        if not self.path.exists():
            return False
        try:
            conn = sqlite3.connect(f"file:{self.path}?mode=ro", uri=True)
            try:
                conn.execute("SELECT count(*) FROM sqlite_master").fetchone()
                return False
            finally:
                conn.close()
        except sqlite3.DatabaseError:
            return True
