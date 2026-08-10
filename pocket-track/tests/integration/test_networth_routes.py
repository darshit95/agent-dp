from tests.conftest import extract_csrf


def test_networth_page_create_update_delete_asset(create_user):
    _settings, _store, _db, services, client = create_user
    page = client.get("/net-worth")
    assert page.status_code == 200
    assert "Net worth" in page.text
    token = extract_csrf(page.text)
    created = client.post(
        "/net-worth/assets",
        data={
            "name": "Luxury HYSA",
            "institution": "Example Bank",
            "current_value": "50000",
            "asset_bucket": "Cash & Cash Equivalents",
            "include_in_net_worth": "on",
            "csrf_token": token,
        },
        follow_redirects=False,
    )
    assert created.status_code == 303
    assets = services.networth_repository.list_assets()
    assert len(assets) == 1
    assert assets[0].asset_bucket == "Cash & Cash Equivalents"

    page = client.get("/net-worth")
    token = extract_csrf(page.text)
    updated = client.post(
        f"/net-worth/assets/{assets[0].id}",
        data={
            "name": "Luxury HYSA",
            "institution": "Example Bank",
            "current_value": "51000",
            "asset_bucket": "Cash & Cash Equivalents",
            "include_in_net_worth": "on",
            "csrf_token": token,
        },
        follow_redirects=False,
    )
    assert updated.status_code == 303
    assert services.networth_repository.get_asset(assets[0].id).current_value_cents == 5100000

    page = client.get("/net-worth")
    token = extract_csrf(page.text)
    deleted = client.post(
        f"/net-worth/assets/{assets[0].id}/delete",
        data={"csrf_token": token},
        follow_redirects=False,
    )
    assert deleted.status_code == 303
    assert services.networth_repository.list_assets() == []


def test_asset_inline_fields_save_without_edit_drawer(create_user):
    _settings, _store, _db, services, client = create_user
    asset = services.networth_repository.create_asset(
        name="Emergency Funds",
        institution="Example Bank",
        value_cents=5000000,
        asset_bucket="Cash & Cash Equivalents",
        include=True,
    )
    page = client.get("/net-worth")
    token = extract_csrf(page.text)

    changed = client.post(
        f"/net-worth/assets/{asset.id}/inline",
        headers={"X-CSRF-Token": token},
        json={"field": "current_value", "value": "50342.25"},
    )
    assert changed.status_code == 200
    assert changed.json()["asset"]["current_value"] == "50342.25"
    assert changed.json()["totals"]["assets"] == 5034225

    renamed = client.post(
        f"/net-worth/assets/{asset.id}/inline",
        headers={"X-CSRF-Token": token},
        json={"field": "name", "value": "Emergency Reserve"},
    )
    assert renamed.status_code == 200
    assert services.networth_repository.get_asset(asset.id).name == "Emergency Reserve"



def test_liability_inline_fields_save_without_edit_drawer(create_user):
    _settings, _store, _db, services, client = create_user

    liability = (
        services.networth_repository.create_liability(
            name="Mortgage",
            institution="Example Bank",
            balance_cents=25000000,
            include=True,
        )
    )

    page = client.get("/net-worth")
    token = extract_csrf(page.text)

    changed = client.post(
        f"/net-worth/liabilities/{liability.id}/inline",
        headers={"X-CSRF-Token": token},
        json={
            "field": "current_balance",
            "value": "249500.25",
        },
    )

    assert changed.status_code == 200

    payload = changed.json()

    assert (
        payload["liability"]["current_balance"]
        == "249500.25"
    )

    assert (
        services.networth_repository
        .get_liability(liability.id)
        .current_balance_cents
        == 24950025
    )

    renamed = client.post(
        f"/net-worth/liabilities/{liability.id}/inline",
        headers={"X-CSRF-Token": token},
        json={
            "field": "name",
            "value": "Primary Mortgage",
        },
    )

    assert renamed.status_code == 200

    assert (
        services.networth_repository
        .get_liability(liability.id)
        .name
        == "Primary Mortgage"
    )

    institution = client.post(
        f"/net-worth/liabilities/{liability.id}/inline",
        headers={"X-CSRF-Token": token},
        json={
            "field": "institution",
            "value": "New Bank",
        },
    )

    assert institution.status_code == 200

    assert (
        services.networth_repository
        .get_liability(liability.id)
        .institution
        == "New Bank"
    )


def test_networth_page_always_exposes_csrf_token(create_user):
    """Net Worth must always render a CSRF token, even with no assets/liabilities."""
    _settings, _store, _db, _services, client = create_user

    page = client.get("/net-worth")

    assert page.status_code == 200
    assert 'name="csrf_token"' in page.text
    assert 'value="' in page.text

