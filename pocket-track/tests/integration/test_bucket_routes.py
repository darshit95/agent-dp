from __future__ import annotations

from tests.conftest import extract_csrf


def _dashboard(client, **params):
    response = client.get("/", params=params or None)
    assert response.status_code == 200
    return response.text


def _csrf(client) -> str:
    return extract_csrf(_dashboard(client))


def _bucket_page(client, bucket_id, month="2026-08", **params):
    response = client.get(f"/buckets/{bucket_id}", params={"month": month, **params})
    assert response.status_code == 200
    return response.text


def test_dashboard_renders_an_icon_for_every_bucket(create_user):
    _settings, _store, _db, services, client = create_user
    html = _dashboard(client)
    for bucket in services.buckets.list_active():
        assert bucket.name in html
    # Default buckets resolve to their keyword icons.
    assert 'href="#i-grocery"' in html
    assert 'href="#i-car"' in html
    assert 'href="#i-repeat"' in html


def test_create_bucket_with_a_chosen_icon(create_user):
    _settings, _store, _db, services, client = create_user
    response = client.post(
        "/buckets",
        data={"name": "Dining", "monthly_budget": "400", "icon": "dining",
              "csrf_token": _csrf(client), "return_month": "2026-08"},
        follow_redirects=False,
    )
    assert response.status_code == 303

    created = next(b for b in services.buckets.list_active() if b.name == "Dining")
    assert created.icon == "dining"
    assert created.default_budget_cents == 40000
    assert 'href="#i-dining"' in _dashboard(client, month="2026-08")


def test_auto_icon_is_stored_as_null_so_it_follows_renames(create_user):
    _settings, _store, _db, services, client = create_user
    client.post(
        "/buckets",
        data={"name": "Coffee runs", "monthly_budget": "", "icon": "auto",
              "csrf_token": _csrf(client), "return_month": "2026-08"},
        follow_redirects=False,
    )
    created = next(b for b in services.buckets.list_active() if b.name == "Coffee runs")
    assert created.icon is None
    assert 'href="#i-coffee"' in _dashboard(client, month="2026-08")


def test_unknown_icon_value_is_ignored_rather_than_rendered(create_user):
    _settings, _store, _db, services, client = create_user
    client.post(
        "/buckets",
        data={"name": "Grocery run", "monthly_budget": "", "icon": "../../evil",
              "csrf_token": _csrf(client), "return_month": "2026-08"},
        follow_redirects=False,
    )
    created = next(b for b in services.buckets.list_active() if b.name == "Grocery run")
    assert created.icon is None
    html = _dashboard(client, month="2026-08")
    assert "evil" not in html


def test_edit_bucket_updates_name_budget_and_icon(create_user):
    _settings, _store, _db, services, client = create_user
    target = next(b for b in services.buckets.list_active() if b.name == "Shopping")

    response = client.post(
        f"/buckets/{target.id}",
        data={"name": "Retail therapy", "monthly_budget": "250.50", "icon": "gift",
              "csrf_token": _csrf(client), "return_month": "2026-08"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"].startswith(f"/buckets/{target.id}?")

    updated = services.buckets.get(target.id)
    assert (updated.name, updated.default_budget_cents, updated.icon) == ("Retail therapy", 25050, "gift")


def test_edit_form_is_rendered_on_the_bucket_page_with_edit_flag(create_user):
    _settings, _store, _db, services, client = create_user
    target = next(b for b in services.buckets.list_active() if b.name == "Grocery")

    plain = _bucket_page(client, target.id)
    assert 'name="monthly_budget"' not in plain, "the editor stays closed until asked for"

    editing = _bucket_page(client, target.id, edit="1")
    assert f'action="/buckets/{target.id}"' in editing
    assert 'name="icon"' in editing
    assert 'name="monthly_budget"' in editing


def test_duplicate_name_returns_the_user_to_the_dashboard_with_an_error(create_user):
    _settings, _store, _db, _services, client = create_user
    response = client.post(
        "/buckets",
        data={"name": "Grocery", "monthly_budget": "", "icon": "auto",
              "csrf_token": _csrf(client), "return_month": "2026-08"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert "error=" in response.headers["location"]

    html = client.get(response.headers["location"]).text
    assert "already exists" in html


def test_invalid_budget_returns_an_error_not_a_server_error(create_user):
    _settings, _store, _db, _services, client = create_user
    response = client.post(
        "/buckets",
        data={"name": "Nonsense budget", "monthly_budget": "abc", "icon": "auto",
              "csrf_token": _csrf(client), "return_month": "2026-08"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert "error=" in response.headers["location"]


def test_delete_bucket_removes_it_from_the_dashboard(create_user):
    _settings, _store, _db, services, client = create_user
    target = next(b for b in services.buckets.list_active() if b.name == "Shopping")

    response = client.post(
        f"/buckets/{target.id}/delete",
        data={"csrf_token": _csrf(client), "return_month": "2026-08"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert "bucket=" not in response.headers["location"], "the deleted bucket must not stay open"

    assert services.buckets.get(target.id) is None
    # Match the card title specifically; "Shopping" is also an icon-picker label.
    assert '<span class="bucket-title">Shopping</span>' not in _dashboard(client, month="2026-08")


def test_deleting_the_unknown_bucket_is_refused(create_user):
    _settings, _store, _db, services, client = create_user
    unknown = next(b for b in services.buckets.list_active() if b.name == "Unknown")

    response = client.post(
        f"/buckets/{unknown.id}/delete",
        data={"csrf_token": _csrf(client), "return_month": "2026-08"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert "error=" in response.headers["location"]
    assert services.buckets.get(unknown.id) is not None


def test_bucket_mutations_require_a_valid_csrf_token(create_user):
    _settings, _store, _db, services, client = create_user
    target = next(b for b in services.buckets.list_active() if b.name == "Grocery")

    assert client.post("/buckets", data={"name": "X", "csrf_token": "bogus"}).status_code == 403
    assert client.post(f"/buckets/{target.id}", data={"name": "X", "csrf_token": "bogus"}).status_code == 403
    assert client.post(f"/buckets/{target.id}/delete", data={"csrf_token": "bogus"}).status_code == 403
    assert services.buckets.get(target.id).name == "Grocery"


def test_dashboard_cards_link_into_the_bucket_page(create_user):
    _settings, _store, _db, services, client = create_user
    target = next(b for b in services.buckets.list_active() if b.name == "Grocery")

    html = _dashboard(client, month="2026-08")
    assert f'href="/buckets/{target.id}?month=2026-08"' in html
    # Transactions live on their own page now, not inline on the dashboard.
    assert 'id="bucket-detail"' not in html


def test_bucket_page_offers_a_way_back_to_the_dashboard(create_user):
    _settings, _store, _db, services, client = create_user
    target = next(b for b in services.buckets.list_active() if b.name == "Grocery")

    html = _bucket_page(client, target.id)
    assert html.count('href="/?month=2026-08"') >= 2, "expected a back link in the header and the footer"
    assert "All buckets" in html
    assert "Back to all buckets" in html


def test_each_card_exposes_edit_and_delete_actions(create_user):
    _settings, _store, _db, services, client = create_user
    grocery = next(b for b in services.buckets.list_active() if b.name == "Grocery")

    html = _dashboard(client, month="2026-08")
    assert f'href="/buckets/{grocery.id}?month=2026-08&edit=1"' in html
    assert f'action="/buckets/{grocery.id}/delete"' in html
    assert f'aria-label="Delete Grocery"' in html


def test_unknown_bucket_card_has_no_delete_action(create_user):
    _settings, _store, _db, services, client = create_user
    unknown = next(b for b in services.buckets.list_active() if b.name == "Unknown")

    html = _dashboard(client, month="2026-08")
    assert f'href="/buckets/{unknown.id}?month=2026-08&edit=1"' in html, "it can still be edited"
    assert f'action="/buckets/{unknown.id}/delete"' not in html


def test_legacy_inline_bucket_link_redirects_to_the_bucket_page(create_user):
    _settings, _store, _db, services, client = create_user
    target = next(b for b in services.buckets.list_active() if b.name == "Grocery")

    response = client.get("/", params={"month": "2026-08", "bucket": target.id}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == f"/buckets/{target.id}?month=2026-08"


def test_unknown_bucket_id_in_the_url_returns_to_the_dashboard(create_user):
    _settings, _store, _db, _services, client = create_user
    response = client.get("/buckets/987654", params={"month": "2026-08"}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"].startswith("/?month=2026-08&error=")


def test_renaming_the_unknown_bucket_is_refused(create_user):
    _settings, _store, _db, services, client = create_user
    unknown = next(b for b in services.buckets.list_active() if b.name == "Unknown")

    response = client.post(
        f"/buckets/{unknown.id}",
        data={"name": "Miscellaneous", "monthly_budget": "", "icon": "auto",
              "csrf_token": _csrf(client), "return_month": "2026-08"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert "error=" in response.headers["location"]
    assert services.buckets.get(unknown.id).name == "Unknown"


def test_unknown_bucket_name_field_is_readonly(create_user):
    _settings, _store, _db, services, client = create_user
    unknown = next(b for b in services.buckets.list_active() if b.name == "Unknown")
    html = _bucket_page(client, unknown.id, edit="1")
    assert "readonly" in html
    assert f'action="/buckets/{unknown.id}/delete"' not in html


def test_zero_budget_renders_a_valid_meter(create_user):
    """A $0 budget is valid input, but <progress max="0"> is not valid HTML."""
    _settings, _store, _db, services, client = create_user
    services.buckets.create("No spend", 0, None)
    assert 'max="0"' not in _dashboard(client, month="2026-08")
