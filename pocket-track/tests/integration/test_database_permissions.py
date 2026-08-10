import os
import sqlite3

from cardbudget.db.engine import Database


def test_db_file_permissions_are_user_only(tmp_path):
    path = tmp_path / "data" / "cardbudget.db"
    db = Database(path, "ab" * 32, connector=sqlite3.connect, require_cipher=False)
    db.initialize()
    if os.name == "posix":
        assert oct(path.stat().st_mode & 0o777) == "0o600"
        assert oct(path.parent.stat().st_mode & 0o777) == "0o700"
