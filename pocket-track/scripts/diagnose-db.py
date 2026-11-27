"""Read-only diagnosis of a PocketTrack 'database could not be opened' failure.
Touches nothing: no writes, no key creation, no file moves."""
import sys
from pathlib import Path

from cardbudget.config import Settings
from cardbudget.security.keychain import DB_KEY_NAME, OSKeychain, db_key_exists

s = Settings.from_env()
db_path = s.database_path
print(f"data dir : {s.data_dir}")
print(f"database : {db_path}")
print(f"exists   : {db_path.exists()}  size={db_path.stat().st_size if db_path.exists() else 0}")

if db_path.exists():
    head = db_path.open('rb').read(16)
    print(f"header   : {'PLAINTEXT SQLite' if head.startswith(b'SQLite format 3') else 'encrypted/unknown'}")

store = OSKeychain(s.keychain_service)
print(f"keychain service : {s.keychain_service!r}  account {DB_KEY_NAME!r}")
try:
    present = db_key_exists(store)
    print(f"db key present   : {present}")
    if present:
        key = store.get_secret(DB_KEY_NAME)
        print(f"db key length    : {len(key)} (expected 64)")
        try:
            bytes.fromhex(key)
            print("db key hex valid : True")
        except ValueError:
            print("db key hex valid : False  <-- key is corrupt")
except Exception as exc:
    print(f"keychain ERROR   : {type(exc).__name__}: {exc}")
    sys.exit(1)

if db_path.exists() and present:
    try:
        import sqlcipher3.dbapi2 as sq
    except ImportError:
        print("sqlcipher3 not importable")
        sys.exit(1)
    conn = sq.connect(str(db_path))
    conn.execute(f"PRAGMA key = \"x'{key}'\"")
    print(f"cipher_version   : {conn.execute('PRAGMA cipher_version').fetchone()}")
    try:
        conn.execute("SELECT count(*) FROM sqlite_master").fetchone()
        print("DECRYPT          : SUCCESS (key matches this database)")
    except Exception as exc:
        print(f"DECRYPT          : FAILED -> {type(exc).__name__}: {exc}")
        for compat in (4, 3):
            try:
                c2 = sq.connect(str(db_path))
                c2.execute(f"PRAGMA key = \"x'{key}'\"")
                c2.execute(f"PRAGMA cipher_compatibility = {compat}")
                c2.execute("SELECT count(*) FROM sqlite_master").fetchone()
                print(f"  -> opens with cipher_compatibility = {compat} (SQLCipher version mismatch)")
                break
            except Exception:
                pass
        else:
            print("  -> not a SQLCipher version mismatch; the key does not match this file")
