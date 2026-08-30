from cardbudget.security.keychain import (
    MemorySecretStore,
    db_key_exists,
    ensure_db_key,
    ensure_session_secret,
)


def test_secret_bootstrap_is_stable():
    store = MemorySecretStore()
    first_db = ensure_db_key(store)
    first_session = ensure_session_secret(store)
    assert len(first_db) == 64
    assert ensure_db_key(store) == first_db
    assert ensure_session_secret(store) == first_session
    assert first_db not in first_session


def test_db_key_exists_reports_absence_without_creating():
    store = MemorySecretStore()
    assert db_key_exists(store) is False
    # Probing must not mint a key, otherwise the orphaned-database check that
    # depends on it can never fire.
    assert store.values == {}
    ensure_db_key(store)
    assert db_key_exists(store) is True
