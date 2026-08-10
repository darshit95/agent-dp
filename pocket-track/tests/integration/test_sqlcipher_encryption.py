from pathlib import Path

import pytest

from cardbudget.db.engine import Database


sqlcipher = pytest.importorskip("sqlcipher3", reason="SQLCipher wheel is not installed in this execution sandbox")


def test_sqlcipher_db_rejects_standard_sqlite_and_wrong_key(tmp_path: Path):
    path = tmp_path / "encrypted.db"
    correct = "ab" * 32
    db = Database(path, correct, require_cipher=True)
    db.initialize()

    assert db.cipher_version()
    assert not db.has_plaintext_sqlite_header()
    assert db.standard_sqlite_is_rejected()

    from sqlcipher3 import dbapi2 as driver

    conn = driver.connect(str(path))
    try:
        conn.execute(f"PRAGMA key = \"x'{'cd' * 32}'\"")
        with pytest.raises(Exception):
            conn.execute("SELECT count(*) FROM sqlite_master").fetchone()
    finally:
        conn.close()
