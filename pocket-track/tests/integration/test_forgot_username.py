from cardbudget.security.local_presence import FakeLocalPresence
from tests.conftest import extract_csrf


def test_forgot_username_reveals_name_when_local_presence_confirmed(create_user):
    _settings, _store, _db, services, client = create_user
    presence = FakeLocalPresence(succeed=True)
    services.auth.local_presence = presence

    page = client.get("/forgot-username")
    assert page.status_code == 200
    # The form must not ask for the username it exists to recover.
    assert 'name="username"' not in page.text

    revealed = client.post("/forgot-username", data={"csrf_token": extract_csrf(page.text)})
    assert revealed.status_code == 200
    assert "testuser" in revealed.text
    # The OS prompt is the authorization, so it must actually have been shown.
    assert presence.calls == ["Show your PocketTrack username"]


def test_forgot_username_does_not_sign_the_visitor_in(create_user):
    _settings, _store, _db, services, client = create_user
    services.auth.local_presence = FakeLocalPresence(succeed=True)

    # Drop the session created by setup so this is a signed-out visitor.
    client.cookies.clear()

    page = client.get("/forgot-username")
    client.post("/forgot-username", data={"csrf_token": extract_csrf(page.text)})

    # Learning the username grants no access without the password.
    assert client.get("/", follow_redirects=False).headers["location"] == "/login"


def test_forgot_username_withholds_name_when_presence_declined(create_user):
    _settings, _store, _db, services, client = create_user
    services.auth.local_presence = FakeLocalPresence(succeed=False)

    page = client.get("/forgot-username")
    declined = client.post("/forgot-username", data={"csrf_token": extract_csrf(page.text)})

    assert declined.status_code == 400
    assert "testuser" not in declined.text


def test_forgot_username_reports_unavailable_platform_distinctly(create_user):
    _settings, _store, _db, services, client = create_user
    services.auth.local_presence = FakeLocalPresence(available=False)

    page = client.get("/forgot-username")
    unavailable = client.post("/forgot-username", data={"csrf_token": extract_csrf(page.text)})

    assert unavailable.status_code == 400
    assert "testuser" not in unavailable.text
    # "Can't check here" must read differently from "the check failed".
    assert "available on this system" in unavailable.text


def test_forgot_username_rejects_bad_csrf_token(create_user):
    _settings, _store, _db, services, client = create_user
    services.auth.local_presence = FakeLocalPresence(succeed=True)

    rejected = client.post("/forgot-username", data={"csrf_token": "not-a-real-token"})
    assert rejected.status_code == 403


def test_login_page_offers_username_recovery(create_user):
    _settings, _store, _db, _services, client = create_user
    # Signed-out, otherwise /login redirects to the dashboard.
    client.cookies.clear()
    assert "/forgot-username" in client.get("/login").text
