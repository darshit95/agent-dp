from cardbudget.security.keychain import MemorySecretStore, ensure_db_key, ensure_session_secret


def test_secret_bootstrap_is_stable():
    store = MemorySecretStore()
    first_db = ensure_db_key(store)
    first_session = ensure_session_secret(store)
    assert len(first_db) == 64
    assert ensure_db_key(store) == first_db
    assert ensure_session_secret(store) == first_session
    assert first_db not in first_session
