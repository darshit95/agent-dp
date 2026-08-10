from tests.conftest import extract_csrf


def test_finance_shell_not_visible_before_auth(test_stack):
    _settings, _store, _db, _services, client = test_stack
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/setup"
    assert "Foundation is running securely" not in response.text


def test_first_run_setup_protects_dashboard(test_stack):
    _settings, _store, _db, services, client = test_stack
    setup = client.get("/setup")
    token = extract_csrf(setup.text)
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
    cookie = response.headers["set-cookie"].lower()
    assert "httponly" in cookie
    assert "samesite=strict" in cookie

    dashboard = client.get("/")
    assert dashboard.status_code == 200
    assert "Monthly spend" in dashboard.text
    assert "Spending buckets" in dashboard.text
    assert "Unknown" in dashboard.text
    assert [b.name for b in services.buckets.list_active()] == [
        "Subscriptions",
        "Shopping",
        "Gas + Car Wash",
        "Grocery",
        "Unknown",
    ]


def test_logout_requires_csrf(create_user):
    _settings, _store, _db, _services, client = create_user
    no_csrf = client.post("/logout", data={"csrf_token": "wrong"}, follow_redirects=False)
    assert no_csrf.status_code == 403

    dashboard = client.get("/")
    token = extract_csrf(dashboard.text)
    logged_out = client.post("/logout", data={"csrf_token": token}, follow_redirects=False)
    assert logged_out.status_code == 303
    assert logged_out.headers["location"] == "/login"
    assert client.get("/", follow_redirects=False).headers["location"] == "/login"


def test_login_error_is_generic_and_throttled(test_stack):
    _settings, _store, _db, _services, client = test_stack
    setup = client.get("/setup")
    token = extract_csrf(setup.text)
    client.post(
        "/setup",
        data={
            "username": "testuser",
            "password": "correct-horse-battery-staple",
            "confirm_password": "correct-horse-battery-staple",
            "csrf_token": token,
        },
    )
    dashboard = client.get("/")
    logout_token = extract_csrf(dashboard.text)
    client.post("/logout", data={"csrf_token": logout_token})

    for _ in range(3):
        login = client.get("/login")
        login_token = extract_csrf(login.text)
        failed = client.post(
            "/login",
            data={"username": "testuser", "password": "wrong-wrong-wrong", "csrf_token": login_token},
        )
        assert failed.status_code == 401
        assert "Invalid username or password." in failed.text

    login = client.get("/login")
    login_token = extract_csrf(login.text)
    throttled = client.post(
        "/login",
        data={"username": "testuser", "password": "wrong-wrong-wrong", "csrf_token": login_token},
    )
    assert throttled.status_code == 429
    assert "Retry-After" in throttled.headers


def test_security_headers_and_docs_disabled(test_stack):
    _settings, _store, _db, _services, client = test_stack
    response = client.get("/login", follow_redirects=False)
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404


def test_untrusted_host_is_rejected(test_stack):
    settings, _store, _db, services, _client = test_stack
    from fastapi.testclient import TestClient
    from cardbudget.app import create_app

    attacker_client = TestClient(create_app(settings, services=services), base_url="http://evil.example")
    assert attacker_client.get("/health/local").status_code == 400


def test_empty_month_does_not_leak_other_month_data(create_user):
    _settings, _store, db, services, client = create_user
    # Seed the minimum bank/account rows and an August transaction.
    services.plaid_repository.upsert_item(
        item_id="item-x", institution_id="ins", institution_name="Bank", environment="sandbox"
    )
    services.plaid_repository.replace_accounts("item-x", [{
        "account_id":"acct-x", "name":"Card", "official_name":None, "mask":"1234", "type":"credit", "subtype":"credit card"
    }])
    services.plaid.map_account("acct-x", "legacy_card_key")
    services.transactions.apply_backfill_batch([{
        "transaction_id":"aug-only", "account_id":"acct-x", "amount_cents":9999, "iso_currency_code":"USD",
        "posted_date":"2026-08-03", "authorized_date":"2026-08-03", "budget_date":"2026-08-03",
        "merchant_name":"August Store", "description":"AUGUST STORE", "pending":False, "pending_transaction_id":None,
        "pfc_primary":None, "pfc_detailed":None, "pfc_confidence":None,
    }])
    august = client.get("/?month=2026-08")
    assert "$99.99" in august.text
    july = client.get("/?month=2026-07")
    assert "No posted spending stored for 2026-07" in july.text
    assert "$99.99" not in july.text
