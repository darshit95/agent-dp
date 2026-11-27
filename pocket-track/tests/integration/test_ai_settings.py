from __future__ import annotations

from urllib.parse import parse_qs, urlsplit

from tests.conftest import extract_csrf


def test_categorization_settings_require_consent_and_keep_keys_out_of_pages(create_user):
    _settings, store, db, services, client = create_user
    page = client.get("/settings")
    csrf = extract_csrf(page.text)
    assert "Rules only" in page.text

    path = "/settings/ai/provider"
    payload = {"provider": "openai", "model": "example"}
    assert client.post(path, data={**payload, "csrf_token": "wrong"}).status_code == 403
    assert client.post(path, data={**payload, "csrf_token": csrf}, follow_redirects=False).status_code == 303
    assert services.providers.get().provider == "rules"
    client.post(path, data={**payload, "csrf_token": csrf, "cloud_consent": "true"}, follow_redirects=False)
    assert services.providers.get().provider == "openai"
    assert services.providers.get().scheduled_cloud is False

    client.post("/settings/ai/key", data={"csrf_token": csrf, "api_key": "example-sensitive-key"}, follow_redirects=False)
    assert store.get_secret("categorization-openai-key") == "example-sensitive-key"
    assert "example-sensitive-key" not in client.get("/settings").text
    with db.connection() as conn:
        assert not conn.execute("SELECT 1 FROM app_meta WHERE value LIKE '%example-sensitive-key%'").fetchone()
    client.post("/settings/ai/disconnect", data={"csrf_token": csrf}, follow_redirects=False)
    assert services.providers.get().provider == "rules"
    assert store.get_secret("categorization-openai-key") is None


def test_chatgpt_connect_redirect_and_forged_callback(create_user):
    _settings, _store, _db, _services, client = create_user
    csrf = extract_csrf(client.get("/settings").text)
    client.post("/settings/ai/provider", data={
        "csrf_token": csrf, "provider": "chatgpt", "cloud_consent": "true",
    }, follow_redirects=False)
    response = client.post("/settings/ai/chatgpt/connect", data={"csrf_token": csrf}, follow_redirects=False)
    assert response.status_code == 303
    url = urlsplit(response.headers["location"])
    params = parse_qs(url.query)
    assert url.netloc == "auth.openai.com"
    assert "chatgpt.tokens.use.direct" in params["scope"][0]
    assert params["redirect_uri"] == ["http://127.0.0.1:8000/settings/ai/chatgpt/callback"]
    callback = "/settings/ai/chatgpt/callback"
    assert client.get(callback, params={"state": "forged"}, headers={"Host": "127.0.0.1:8000"}).status_code == 400
    response = client.get(
        callback, params={"state": params["state"][0], "error": "access_denied"},
        headers={"Host": "127.0.0.1:8000"}, follow_redirects=False,
    )
    assert response.status_code == 303
    assert "ChatGPT+plan+connection+was+not+completed" in response.headers["location"]
