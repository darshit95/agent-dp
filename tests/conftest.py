from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from cardbudget.app import create_app
from cardbudget.config import Settings
from cardbudget.db.engine import Database
from cardbudget.security.keychain import MemorySecretStore
from cardbudget.services import bootstrap_services


@pytest.fixture
def test_stack(tmp_path: Path):
    settings = Settings(
        data_dir=tmp_path,
        session_idle_seconds=1800,
        login_max_failures=3,
        login_lockout_seconds=5,
        plaid_environment="sandbox",
    )
    store = MemorySecretStore()
    # Tests inject ordinary sqlite solely to exercise higher-level application logic.
    # Production bootstrap never selects this path.
    db = Database(
        settings.database_path,
        "ab" * 32,
        connector=sqlite3.connect,
        require_cipher=False,
    )
    services = bootstrap_services(settings, secret_store=store, database=db)
    app = create_app(settings, services=services)
    client = TestClient(app, base_url="http://localhost")
    return settings, store, db, services, client


def extract_csrf(html: str) -> str:
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match, "CSRF token not present in rendered form"
    return match.group(1)


@pytest.fixture
def create_user(test_stack):
    _settings, _store, _db, _services, client = test_stack
    page = client.get("/setup")
    token = extract_csrf(page.text)
    response = client.post(
        "/setup",
        data={
            "username": "testuser",
            "password": "correct-horse-battery-staple",
            "confirm_password": "correct-horse-battery-staple",
            "csrf_token": token,
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    return test_stack
