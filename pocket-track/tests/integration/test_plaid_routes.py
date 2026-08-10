from __future__ import annotations

from cardbudget.plaid.client import PlaidClient
from tests.conftest import extract_csrf


class RouteFakeTransport:
    def post(self, path, payload):
        if path == "/link/token/create":
            return {"link_token": "link-route-test"}
        raise AssertionError(path)


def test_plaid_link_token_requires_auth_and_csrf(create_user):
    _settings, store, _db, services, client = create_user
    services.plaid._client_factory = lambda _a, _b, _c: PlaidClient(RouteFakeTransport())
    services.plaid.save_credentials("client", "secret")

    assert client.post("/plaid/link-token").status_code == 403
    dashboard = client.get("/")
    csrf = extract_csrf(dashboard.text)
    response = client.post("/plaid/link-token", headers={"X-CSRF-Token": csrf})
    assert response.status_code == 200
    assert response.json() == {"link_token": "link-route-test"}
    assert "link-route-test" not in repr(store.values)  # link tokens are never persisted


def test_settings_does_not_echo_plaid_secrets(create_user):
    _settings, _store, _db, services, client = create_user
    page = client.get("/settings")
    csrf = extract_csrf(page.text)
    response = client.post(
        "/settings/plaid/credentials",
        data={"client_id": "very-private-client-id", "secret": "very-private-secret", "csrf_token": csrf},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "very-private-client-id" not in response.text
    assert "very-private-secret" not in response.text
    assert services.plaid.credentials_configured()


def test_mapping_save_can_return_json_without_page_refresh(create_user):
    _settings, _store, _db, services, client = create_user
    services.plaid_repository.upsert_item(
        item_id="item-map", institution_id="ins", institution_name="Bank", environment="sandbox"
    )
    services.plaid_repository.replace_accounts("item-map", [{
        "account_id":"acct-map", "name":"Card", "official_name":None, "mask":"1234", "type":"credit", "subtype":"credit card"
    }])
    page = client.get("/settings")
    csrf = extract_csrf(page.text)
    response = client.post(
        "/settings/accounts/acct-map/enabled",
        data={"enabled":"on", "csrf_token":csrf},
        headers={"X-Requested-With":"fetch"},
    )
    assert response.status_code == 200
    assert response.json()["saved"] is True
    assert response.json()["enabled"] is True
    assert response.json()["card_name"] == "Card"


def test_settings_uses_plaid_card_names_and_track_toggle(create_user):
    _settings, _store, _db, services, client = create_user
    services.plaid_repository.upsert_item(
        item_id="item-generic", institution_id="ins", institution_name="Example Bank", environment="sandbox"
    )
    services.plaid_repository.replace_accounts("item-generic", [{
        "account_id":"acct-generic", "name":"Everyday Rewards", "official_name":"Example Platinum Card",
        "mask":"7788", "type":"credit", "subtype":"credit card"
    }])
    page = client.get("/settings")
    assert "Example Platinum Card" in page.text
    assert "Example Rewards Card" not in page.text
    csrf = extract_csrf(page.text)
    response = client.post(
        "/settings/accounts/acct-generic/enabled",
        data={"enabled":"on", "csrf_token":csrf},
        headers={"X-Requested-With":"fetch"},
    )
    assert response.status_code == 200
    assert response.json()["enabled"] is True
    assert response.json()["card_name"] == "Example Platinum Card"
