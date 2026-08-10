from tests.conftest import extract_csrf


def test_change_password_invalidates_sessions(create_user):
    _settings, _store, _db, _services, client = create_user
    settings = client.get("/settings")
    token = extract_csrf(settings.text)
    response = client.post(
        "/settings/change-password",
        data={
            "current_password": "correct-horse-battery-staple",
            "new_password": "new-correct-horse-battery-staple",
            "confirm_password": "new-correct-horse-battery-staple",
            "csrf_token": token,
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/login"
    assert client.get("/", follow_redirects=False).headers["location"] == "/login"

    login = client.get("/login")
    token = extract_csrf(login.text)
    old = client.post(
        "/login",
        data={"username": "testuser", "password": "correct-horse-battery-staple", "csrf_token": token},
    )
    assert old.status_code == 401

    login = client.get("/login")
    token = extract_csrf(login.text)
    good = client.post(
        "/login",
        data={"username": "testuser", "password": "new-correct-horse-battery-staple", "csrf_token": token},
        follow_redirects=False,
    )
    assert good.status_code == 303
