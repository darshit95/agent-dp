from __future__ import annotations

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from cardbudget.plaid.client import PlaidAPIError
from cardbudget.scheduler import macos as macos_scheduler

router = APIRouter()


def _services(request: Request):
    return request.app.state.services


def _session(request: Request):
    services = _services(request)
    return services.sessions.resolve(request.cookies.get(services.settings.session_cookie_name))


def _require_session(request: Request):
    context = _session(request)
    if not context:
        raise HTTPException(status_code=401, detail="Authentication required.")
    return context


def _require_csrf(request: Request, supplied: str | None):
    services = _services(request)
    context = _require_session(request)
    if not services.sessions.validate_csrf(context, supplied):
        raise HTTPException(status_code=403, detail="Invalid CSRF token.")
    return context


@router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request):
    services = _services(request)
    context = _session(request)
    if not services.auth.is_initialized():
        return RedirectResponse("/setup", status_code=303)
    if not context:
        return RedirectResponse("/login", status_code=303)
    ollama_reachable, ollama_model_installed = services.ollama.status()
    items = services.plaid_repository.list_active_items(services.plaid.environment)
    accounts = services.plaid_repository.list_accounts(services.plaid.environment)
    bank_groups = []
    for item in items:
        cards = [account for account in accounts if account.item_id == item.item_id and account.account_type == "credit"]
        bank_groups.append({"item": item, "cards": cards, "tracked_count": sum(1 for card in cards if card.enabled)})
    return request.app.state.templates.TemplateResponse(
        request,
        "settings.html",
        {
            "csrf_token": context.csrf_token,
            "plaid_environment": services.plaid.environment,
            "credentials_configured": services.plaid.credentials_configured(),
            "bank_groups": bank_groups,
            "message": request.query_params.get("message"),
            "ollama_reachable": ollama_reachable,
            "ollama_model_installed": ollama_model_installed,
            "ollama_model": services.settings.ollama_model,
            "scheduler_status": macos_scheduler.status(),
            "minimum_password_length": services.settings.password_min_length,
        },
    )


@router.post("/settings/plaid/credentials")
def save_credentials(
    request: Request,
    client_id: str = Form(...),
    secret: str = Form(...),
    csrf_token: str = Form(...),
):
    services = _services(request)
    _require_csrf(request, csrf_token)
    try:
        services.plaid.save_credentials(client_id, secret)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    services.audit.record("plaid_credentials_updated")
    label = "Sandbox" if services.plaid.environment == "sandbox" else "Production"
    return RedirectResponse(f"/settings?message=Plaid+{label}+credentials+saved", status_code=303)


@router.post("/plaid/link-token")
def create_link_token(request: Request):
    services = _services(request)
    context = _require_csrf(request, request.headers.get("X-CSRF-Token"))
    try:
        token = services.plaid.create_link_token(context.user_id)
    except (ValueError, PlaidAPIError) as exc:
        status = 400 if isinstance(exc, ValueError) else 502
        raise HTTPException(status_code=status, detail=str(exc)) from exc
    return JSONResponse({"link_token": token})


@router.post("/plaid/items/{item_id}/update-link-token")
def create_update_link_token(item_id: str, request: Request):
    services = _services(request)
    context = _require_csrf(request, request.headers.get("X-CSRF-Token"))
    try:
        token = services.plaid.create_update_link_token(context.user_id, item_id)
    except (ValueError, PlaidAPIError) as exc:
        status = 400 if isinstance(exc, ValueError) else 502
        raise HTTPException(status_code=status, detail=str(exc)) from exc
    return JSONResponse({"link_token": token})


@router.post("/plaid/items/{item_id}/update-complete")
def update_item_complete(item_id: str, request: Request):
    services = _services(request)
    _require_csrf(request, request.headers.get("X-CSRF-Token"))
    try:
        services.plaid.refresh_item_accounts(item_id)
    except (ValueError, PlaidAPIError) as exc:
        status = 400 if isinstance(exc, ValueError) else 502
        raise HTTPException(status_code=status, detail=str(exc)) from exc
    return JSONResponse({"ok": True})


@router.post("/plaid/exchange")
async def exchange_public_token(request: Request):
    services = _services(request)
    context = _require_csrf(request, request.headers.get("X-CSRF-Token"))
    payload = await request.json()
    public_token = str(payload.get("public_token") or "")
    institution_id = payload.get("institution_id")
    institution_name = payload.get("institution_name")
    try:
        item_id = services.plaid.exchange_and_register(
            public_token,
            link_institution_id=None if institution_id is None else str(institution_id),
            link_institution_name=None if institution_name is None else str(institution_name),
        )
    except (ValueError, PlaidAPIError) as exc:
        status = 400 if isinstance(exc, ValueError) else 502
        raise HTTPException(status_code=status, detail=str(exc)) from exc
    services.audit.record("plaid_item_connected")
    return JSONResponse({"ok": True, "item_id": item_id})


@router.post("/settings/accounts/{account_id}/enabled")
def set_account_enabled(
    account_id: str,
    request: Request,
    enabled: str | None = Form(None),
    csrf_token: str = Form(...),
):
    services = _services(request)
    _require_csrf(request, csrf_token)
    try:
        services.plaid.set_account_enabled(account_id, enabled == "on")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    services.audit.record("account_mapping_updated")
    account = services.plaid_repository.get_account(account_id, services.plaid.environment)
    if request.headers.get("X-Requested-With") == "fetch":
        return JSONResponse({
            "saved": True,
            "account_id": account_id,
            "enabled": bool(account and account.enabled),
            "card_name": None if not account else (account.card_name or account.official_name or account.name),
        })
    return RedirectResponse("/settings?message=Card+preference+saved", status_code=303)


@router.post("/settings/accounts/{account_id}/mapping")
def legacy_map_account(
    account_id: str,
    request: Request,
    card_key: str = Form("ignore"),
    csrf_token: str = Form(...),
):
    """Backward-compatible endpoint for old clients; no predefined card names are used."""
    services = _services(request)
    _require_csrf(request, csrf_token)
    try:
        services.plaid.set_account_enabled(account_id, card_key not in {"", "ignore"})
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    services.audit.record("account_mapping_updated")
    account = services.plaid_repository.get_account(account_id, services.plaid.environment)
    if request.headers.get("X-Requested-With") == "fetch":
        return JSONResponse({"saved": True, "account_id": account_id, "enabled": bool(account and account.enabled)})
    return RedirectResponse("/settings?message=Card+preference+saved", status_code=303)


@router.post("/settings/sync")
def sync_now(request: Request, csrf_token: str = Form(...)):
    services = _services(request)
    _require_csrf(request, csrf_token)
    try:
        result = services.plaid.sync_all()
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except PlaidAPIError as exc:
        raise HTTPException(status_code=502, detail=f"Plaid sync failed: {exc.error_code}") from exc
    services.audit.record("transactions_synced")
    categorized = services.categorization.categorize_unassigned(300)
    services.audit.record("categorization_run")
    message = (
        f"Sync complete: {result.added} added, {result.modified} modified, {result.removed} removed"
        + (f", {result.failed_items} connection(s) need attention" if result.failed_items else "")
        + "; "
        f"categorized {categorized.rule_applied + categorized.llm_applied}"
    )
    if categorized.ollama_unavailable:
        message += "; Ollama unavailable"
    from urllib.parse import quote_plus
    return RedirectResponse(f"/settings?message={quote_plus(message)}", status_code=303)


@router.post("/settings/change-password")
def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    csrf_token: str = Form(...),
):
    services = _services(request)
    context = _require_csrf(request, csrf_token)
    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="New passwords do not match.")
    try:
        services.auth.change_password(context.user_id, current_password, new_password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    services.audit.record("password_changed")
    services.sessions.repository.delete_all_for_user(context.user_id)
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(services.settings.session_cookie_name, path="/")
    return response
