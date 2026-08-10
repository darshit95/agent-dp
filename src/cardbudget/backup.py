from __future__ import annotations

import base64
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from cardbudget.db.engine import Database

BACKUP_MAGIC = b"POCKETTRACK-BACKUP-v1\n"
PBKDF2_ITERATIONS = 600_000

# Logical backup only. Secrets remain in OS Keychain and are intentionally excluded.
BACKUP_TABLES: tuple[str, ...] = (
    "users",
    "buckets",
    "plaid_items",
    "accounts",
    "transactions",
    "deleted_transactions",
    "merchant_rules",
    "assets",
    "liabilities",
    "asset_rules",
)

DELETE_ORDER: tuple[str, ...] = (
    "sessions",
    "merchant_rules",
    "transactions",
    "deleted_transactions",
    "accounts",
    "plaid_items",
    "asset_rules",
    "assets",
    "liabilities",
    "buckets",
    "users",
)

INSERT_ORDER = BACKUP_TABLES


class BackupError(RuntimeError):
    pass


def _derive_key(password: str, salt: bytes) -> bytes:
    if len(password) < 12:
        raise BackupError("Backup password must be at least 12 characters.")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))


def _table_rows(conn, table: str) -> list[dict[str, Any]]:
    columns = [str(row[1]) for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    if not columns:
        return []
    rows = conn.execute(f"SELECT * FROM {table}").fetchall()
    return [{columns[i]: row[i] for i in range(len(columns))} for row in rows]


class BackupService:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, output_path: Path, password: str) -> Path:
        output_path = output_path.expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = {
            "format": "PocketTrack logical backup",
            "version": 1,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "tables": {},
        }
        with self.database.connection() as conn:
            for table in BACKUP_TABLES:
                payload["tables"][table] = _table_rows(conn, table)

        raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        salt = os.urandom(16)
        encrypted = Fernet(_derive_key(password, salt)).encrypt(raw)
        tmp = output_path.with_suffix(output_path.suffix + ".tmp")
        tmp.write_bytes(BACKUP_MAGIC + base64.urlsafe_b64encode(salt) + b"\n" + encrypted)
        if os.name == "posix":
            os.chmod(tmp, 0o600)
        tmp.replace(output_path)
        return output_path

    def restore(self, input_path: Path, password: str) -> None:
        input_path = input_path.expanduser().resolve()
        try:
            blob = input_path.read_bytes()
        except OSError as exc:
            raise BackupError("Backup file could not be read.") from exc
        if not blob.startswith(BACKUP_MAGIC):
            raise BackupError("This is not a supported PocketTrack backup file.")
        try:
            rest = blob[len(BACKUP_MAGIC):]
            encoded_salt, encrypted = rest.split(b"\n", 1)
            salt = base64.urlsafe_b64decode(encoded_salt)
            raw = Fernet(_derive_key(password, salt)).decrypt(encrypted)
            payload = json.loads(raw)
        except (ValueError, InvalidToken, json.JSONDecodeError) as exc:
            raise BackupError("Backup password is incorrect or the backup is damaged.") from exc
        if payload.get("version") != 1 or not isinstance(payload.get("tables"), dict):
            raise BackupError("Unsupported PocketTrack backup version.")
        tables: dict[str, list[dict[str, Any]]] = payload["tables"]

        with self.database.transaction() as conn:
            for table in DELETE_ORDER:
                conn.execute(f"DELETE FROM {table}")
            for table in INSERT_ORDER:
                rows = tables.get(table) or []
                for row in rows:
                    if not isinstance(row, dict) or not row:
                        continue
                    columns = list(row.keys())
                    placeholders = ",".join("?" for _ in columns)
                    column_sql = ",".join(columns)
                    conn.execute(
                        f"INSERT INTO {table}({column_sql}) VALUES ({placeholders})",
                        tuple(row[column] for column in columns),
                    )
