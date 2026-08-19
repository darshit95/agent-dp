from cardbudget.security.local_presence import FakeLocalPresence
from tests.conftest import extract_csrf


def test_forgot_password_resets_when_local_presence_confirmed_and_invalidates_sessions(create_user):
    _settings, _store, _db, services, client = create_user
    # Still logged in from setup - resetting must kill this session too.
    assert client.get("/").status_code == 200

    forgot = client.get("/forgot-password")
    forgot_token = extract_csrf(forgot.text)
    reset = client.post(
        "/forgot-password",
        data={
            "username": "testuser",
            "new_password": "new-correct-horse-battery-staple",
            "confirm_password": "new-correct-horse-battery-staple",
            "csrf_token": forgot_token,
        },
        follow_redirects=False,
    )
    assert reset.status_code == 303
    assert reset.headers["location"].startswith("/login?message=")

    # The session that was still active before the reset is now dead.
    assert client.get("/", follow_redirects=False).headers["location"] == "/login"

    # Old password no longer works.
    login = client.get("/login")
    login_token = extract_csrf(login.text)
    old_password_attempt = client.post(
        "/login",
        data={"username": "testuser", "password": "correct-horse-battery-staple", "csrf_token": login_token},
    )
    assert old_password_attempt.status_code == 401

    # New password works.
    login = client.get("/login")
    login_token = extract_csrf(login.text)
    good = client.post(
        "/login",
        data={"username": "testuser", "password": "new-correct-horse-battery-staple", "csrf_token": login_token},
        follow_redirects=False,
    )
    assert good.status_code == 303


def test_forgot_password_denied_local_presence_is_generic_and_throttled(create_user):
    _settings, _store, _db, services, client = create_user
    services.auth.local_presence = FakeLocalPresence(succeed=False)

    for _ in range(3):
        forgot = client.get("/forgot-password")
        forgot_token = extract_csrf(forgot.text)
        failed = client.post(
            "/forgot-password",
            data={
                "username": "testuser",
                "new_password": "irrelevant-new-password",
                "confirm_password": "irrelevant-new-password",
                "csrf_token": forgot_token,
            },
        )
        assert failed.status_code == 400
        assert "Could not confirm" in failed.text

    forgot = client.get("/forgot-password")
    forgot_token = extract_csrf(forgot.text)
    throttled = client.post(
        "/forgot-password",
        data={
            "username": "testuser",
            "new_password": "irrelevant-new-password",
            "confirm_password": "irrelevant-new-password",
            "csrf_token": forgot_token,
        },
    )
    assert throttled.status_code == 429
    assert "Retry-After" in throttled.headers


def test_forgot_password_unavailable_shows_clear_message_and_is_not_throttled(create_user):
    _settings, _store, _db, services, client = create_user
    fake = FakeLocalPresence(available=False)
    services.auth.local_presence = fake

    for _ in range(5):
        forgot = client.get("/forgot-password")
        forgot_token = extract_csrf(forgot.text)
        response = client.post(
            "/forgot-password",
            data={
                "username": "testuser",
                "new_password": "irrelevant-new-password",
                "confirm_password": "irrelevant-new-password",
                "csrf_token": forgot_token,
            },
        )
        # Not available is not a failed attempt - it should never hit the
        # login_max_failures=3 throttle configured on test_stack.
        assert response.status_code == 400
        assert "available on this system" in response.text


def test_forgot_password_unknown_username_never_triggers_the_os_prompt(create_user):
    _settings, _store, _db, services, client = create_user
    fake = FakeLocalPresence(succeed=True)
    services.auth.local_presence = fake

    forgot = client.get("/forgot-password")
    forgot_token = extract_csrf(forgot.text)
    response = client.post(
        "/forgot-password",
        data={
            "username": "no-such-user",
            "new_password": "irrelevant-new-password",
            "confirm_password": "irrelevant-new-password",
            "csrf_token": forgot_token,
        },
    )
    assert response.status_code == 400
    assert "Could not confirm" in response.text
    # A mistyped/unknown username shouldn't bother the user with a real
    # Touch ID/Windows Hello prompt - there's nothing to confirm identity for.
    assert fake.calls == []


def test_forgot_password_weak_new_password_is_not_throttled(create_user):
    _settings, _store, _db, services, client = create_user
    forgot = client.get("/forgot-password")
    forgot_token = extract_csrf(forgot.text)
    response = client.post(
        "/forgot-password",
        data={
            "username": "testuser",
            "new_password": "too-short",
            "confirm_password": "too-short",
            "csrf_token": forgot_token,
        },
    )
    assert response.status_code == 400
    assert "at least" in response.text

    # Confirm this didn't count against the throttle (login_max_failures=3
    # on test_stack) - a correctly-confirmed reset should still work right after.
    forgot = client.get("/forgot-password")
    forgot_token = extract_csrf(forgot.text)
    good = client.post(
        "/forgot-password",
        data={
            "username": "testuser",
            "new_password": "new-correct-horse-battery-staple",
            "confirm_password": "new-correct-horse-battery-staple",
            "csrf_token": forgot_token,
        },
        follow_redirects=False,
    )
    assert good.status_code == 303
