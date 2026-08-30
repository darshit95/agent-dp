from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from cardbudget.config import Settings
from cardbudget.db.engine import Database
from cardbudget.errors import DatabaseKeyMissing, DatabaseOpenError
from cardbudget.security.keychain import DB_KEY_NAME, MemorySecretStore
from cardbudget.services import bootstrap_services


class _UnopenableDatabase(Database):
    """Stands in for a real SQLCipher database whose key no longer decrypts it.

    Tests never load sqlcipher3, so the wrong-key failure is simulated at the
    same boundary the real one surfaces from: initialize().
    """

    def initialize(self) -> None:
        raise DatabaseOpenError(
            "Encrypted database could not be opened. The original file was left untouched."
        )


def _settings(tmp_path: Path) -> Settings:
    return Settings(data_dir=tmp_path, plaid_environment="sandbox")


def _unopenable(settings: Settings) -> _UnopenableDatabase:
    return _UnopenableDatabase(
        settings.database_path, "ab" * 32, connector=sqlite3.connect, require_cipher=False
    )


def test_existing_database_with_no_key_raises_key_missing(tmp_path: Path):
    settings = _settings(tmp_path)
    settings.database_path.write_bytes(b"encrypted-under-a-key-that-is-gone")
    store = MemorySecretStore()  # keychain entry absent, as after a lost login keychain

    with pytest.raises(DatabaseKeyMissing) as excinfo:
        bootstrap_services(settings, secret_store=store, database=_unopenable(settings))

    message = str(excinfo.value)
    # The message has to name where the key lives and give a way forward; a bare
    # "could not be opened" is what sent a user hunting for a nonexistent env var.
    assert settings.keychain_service in message
    assert DB_KEY_NAME in message
    assert str(settings.database_path) in message


def test_open_failure_with_key_present_keeps_generic_error(tmp_path: Path):
    settings = _settings(tmp_path)
    settings.database_path.write_bytes(b"corrupt")
    store = MemorySecretStore(values={DB_KEY_NAME: "ab" * 32})

    # The key is present, so this is ordinary corruption - not the orphaned-key
    # case - and must not be reported as a missing key.
    with pytest.raises(DatabaseOpenError) as excinfo:
        bootstrap_services(settings, secret_store=store, database=_unopenable(settings))
    assert not isinstance(excinfo.value, DatabaseKeyMissing)


def test_first_run_with_no_database_is_not_key_missing(tmp_path: Path):
    settings = _settings(tmp_path)
    store = MemorySecretStore()

    # No database file yet: a genuine first run, which must surface as the
    # underlying error rather than a misleading "your key is gone".
    with pytest.raises(DatabaseOpenError) as excinfo:
        bootstrap_services(settings, secret_store=store, database=_unopenable(settings))
    assert not isinstance(excinfo.value, DatabaseKeyMissing)
