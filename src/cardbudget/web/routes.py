from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from urllib.parse import quote_plus

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from cardbudget.db.schema import ASSET_BUCKETS
from cardbudget.plaid.client import PlaidAPIError

router = APIRouter()

REAUTH_ERROR_CODES = {
    "ITEM_LOGIN_REQUIRED",
    "INVALID_CREDENTIALS",
    "ACCESS_NOT_GRANTED",
    "ITEM_LOCKED",
    "ITEM_NOT_SUPPORTED",
    "MFA_NOT_SUPPORTED",
    "NO_ACCOUNTS",
    "MISSING_ACCESS_TOKEN",
}


def _services(request: Request):
    return request.app.state.services


def _session(request: Request):
    services = _services(request)
    return services.sessions.resolve(request.cookies.get(services.settings.session_cookie_name))


def _require_authenticated_page(request: Request):
    services = _services(request)
    if not services.auth.is_initialized():
        return None, RedirectResponse("/setup", status_code=303)
    context = _session(request)
    if not context:
        return None, RedirectResponse("/login", status_code=303)
    return context, None


def _require_csrf(request: Request, token: str):
    services = _services(request)
    context = _session(request)
    if not context:
        raise HTTPException(status_code=401, detail="Authentication required.")
    if not services.sessions.validate_csrf(context, token):
        raise HTTPException(status_code=403, detail="Invalid CSRF token.")
    return context


def _month_or_current(value: str | None) -> str:
    if not value:
        return date.today().strftime("%Y-%m")
    try:
        datetime.strptime(value, "%Y-%m")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Month must use YYYY-MM format.") from exc
    return value


def _money_to_cents(value: str, *, field_name: str, maximum: Decimal = Decimal("10000000000")) -> int:
    clean = value.strip().replace("$", "").replace(",", "")
    if clean == "":
        raise ValueError(f"{field_name} is required.")
    try:
        amount = Decimal(clean)
    except InvalidOperation as exc:
        raise ValueError(f"{field_name} must be a valid dollar amount.") from exc
    if amount < 0 or amount > maximum:
        raise ValueError(f"{field_name} must be between $0 and ${maximum:,.0f}.")
    return int((amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _optional_budget_to_cents(value: str) -> int | None:
    clean = value.strip().replace("$", "").replace(",", "")
    if clean == "":
        return None
    return _money_to_cents(clean, field_name="Budget", maximum=Decimal("1000000"))


def _home_url(month: str, bucket_id: int | None = None, message: str | None = None) -> str:
    parts = [f"month={quote_plus(month)}"]
    if bucket_id is not None:
        parts.append(f"bucket={bucket_id}")
    if message:
        parts.append(f"message={quote_plus(message)}")
    return "/?" + "&".join(parts)


def _format_last_refresh(value):
    if not value:
        return "Never"
    try:
        return value.astimezone().strftime("%b %-d, %Y · %-I:%M %p")
    except ValueError:  # pragma: no cover - platform strftime variant
        return value.astimezone().strftime("%b %d, %Y · %I:%M %p").replace(" 0", " ")


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, month: str | None = None, bucket: int | None = None):
    services = _services(request)
    context, redirect = _require_authenticated_page(request)
    if redirect:
        return redirect
    selected_month = _month_or_current(month)
    summary = services.buckets.monthly_summary(selected_month)
    total_spent = sum(row.spent_cents for row in summary)
    accounts = services.plaid_repository.list_accounts(services.plaid.environment)
    mapped = [a for a in accounts if a.enabled]

    selected_bucket = services.buckets.get(bucket) if bucket is not None else None
    if selected_bucket and not selected_bucket.active:
        selected_bucket = None
    selected_transactions = (
        services.transactions.list_for_bucket(selected_bucket.id, selected_month, 500)
        if selected_bucket
        else []
    )
    item_errors = services.plaid_repository.items_with_errors(services.plaid.environment)
    reauth_items = [item for item in item_errors if (item.last_sync_error_code or "") in REAUTH_ERROR_CODES]
    last_refresh = services.plaid_repository.latest_sync_at(services.plaid.environment)

    return request.app.state.templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "csrf_token": context.csrf_token,
            "budget_summary": summary,
            "selected_month": selected_month,
            "total_spent_cents": total_spent,
            "mapped_cards": mapped,
            "mapped_cards_count": len(mapped),
            "selected_bucket": selected_bucket,
            "selected_transactions": selected_transactions,
            "buckets": services.buckets.list_active(),
            "has_transactions": services.transactions.count_for_month(selected_month) > 0,
            "credentials_configured": services.plaid.credentials_configured(),
            "message": request.query_params.get("message"),
            "last_refreshed": _format_last_refresh(last_refresh),
            "reauth_items": reauth_items,
        },
    )


@router.get("/transactions")
def transactions_redirect(month: str | None = None):
    return RedirectResponse(_home_url(_month_or_current(month)), status_code=303)


@router.get("/buckets")
def buckets_redirect():
    return RedirectResponse("/", status_code=303)


@router.post("/transactions/{transaction_id}/bucket")
def assign_transaction_bucket(
    transaction_id: str,
    request: Request,
    bucket_id: str = Form(""),
    remember_merchant: str | None = Form(None),
    csrf_token: str = Form(...),
    return_month: str = Form(""),
    return_bucket: str = Form(""),
):
    services = _services(request)
    _require_csrf(request, csrf_token)
    month = _month_or_current(return_month or None)
    try:
        parsed_bucket = None if bucket_id in {"", "uncategorized"} else int(bucket_id)
        services.categorization.manual_assign(transaction_id, parsed_bucket, remember_merchant == "on")
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    services.audit.record("transaction_category_updated")
    selected_bucket = int(return_bucket) if return_bucket.isdigit() else parsed_bucket
    return RedirectResponse(_home_url(month, selected_bucket), status_code=303)


@router.post("/transactions/{transaction_id}/delete")
def delete_transaction(
    transaction_id: str,
    request: Request,
    csrf_token: str = Form(...),
    return_month: str = Form(""),
    return_bucket: str = Form(""),
):
    services = _services(request)
    _require_csrf(request, csrf_token)
    month = _month_or_current(return_month or None)
    try:
        services.transactions.delete_by_user(transaction_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    services.audit.record("transaction_deleted")
    bucket_id = int(return_bucket) if return_bucket.isdigit() else None
    return RedirectResponse(_home_url(month, bucket_id, "Transaction deleted"), status_code=303)


@router.post("/buckets")
def create_bucket(
    request: Request,
    name: str = Form(...),
    monthly_budget: str = Form(""),
    csrf_token: str = Form(...),
    return_month: str = Form(""),
):
    services = _services(request)
    _require_csrf(request, csrf_token)
    month = _month_or_current(return_month or None)
    try:
        created = services.buckets.create(name, _optional_budget_to_cents(monthly_budget))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    services.audit.record("bucket_created")
    return RedirectResponse(_home_url(month, created.id, "Bucket created"), status_code=303)


@router.post("/buckets/{bucket_id}/budget")
def update_bucket_budget(
    bucket_id: int,
    request: Request,
    monthly_budget: str = Form(""),
    csrf_token: str = Form(...),
    return_month: str = Form(""),
):
    services = _services(request)
    _require_csrf(request, csrf_token)
    month = _month_or_current(return_month or None)
    bucket = services.buckets.get(bucket_id)
    if not bucket:
        raise HTTPException(status_code=404, detail="Unknown bucket.")
    try:
        services.buckets.update(bucket_id, bucket.name, _optional_budget_to_cents(monthly_budget), active=True)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    services.audit.record("bucket_updated")
    return RedirectResponse(_home_url(month, bucket_id, "Budget saved"), status_code=303)


@router.post("/refresh-month")
def refresh_month(request: Request, month: str = Form(...), csrf_token: str = Form(...)):
    services = _services(request)
    _require_csrf(request, csrf_token)
    selected_month = _month_or_current(month)
    try:
        result = services.plaid.backfill_month(selected_month)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except PlaidAPIError as exc:
        raise HTTPException(status_code=502, detail=f"Plaid refresh failed: {exc.error_code}") from exc
    services.audit.record("historical_backfill")
    services.categorization.categorize_unassigned(1000)
    message = (
        f"Refreshed {selected_month}: {result.imported} posted transactions loaded; "
        f"ignored {result.ignored_pending} pending and {result.ignored_payments} payment/autopay"
    )
    return RedirectResponse(_home_url(selected_month, message=message), status_code=303)


# --------------------------- Net Worth Tracker ---------------------------


def _networth_url(message: str | None = None) -> str:
    return "/net-worth" + (f"?message={quote_plus(message)}" if message else "")


def _allocation_segments(allocation):
    total = sum(row.value_cents for row in allocation)
    by_bucket = {row.asset_bucket: row.value_cents for row in allocation}
    segments = []
    offset = 0.0
    for index, bucket_name in enumerate(ASSET_BUCKETS):
        value = int(by_bucket.get(bucket_name, 0))
        pct = (value / total) * 100.0 if total > 0 else 0.0
        segments.append(
            {
                "bucket": bucket_name,
                "value_cents": value,
                "percent": pct,
                "dash": f"{pct:.4f} {100.0 - pct:.4f}",
                "offset": f"{-offset:.4f}",
                "class_name": f"allocation-{index}",
            }
        )
        offset += pct
    return segments


@router.get("/net-worth", response_class=HTMLResponse)
def net_worth_page(request: Request):
    services = _services(request)
    context, redirect = _require_authenticated_page(request)
    if redirect:
        return redirect
    assets = services.networth_repository.list_assets()
    liabilities = services.networth_repository.list_liabilities()
    total_assets, total_liabilities, net_worth = services.networth_repository.totals()
    allocation = services.networth_repository.allocation()
    return request.app.state.templates.TemplateResponse(
        request,
        "networth.html",
        {
            "csrf_token": context.csrf_token,
            "assets": assets,
            "liabilities": liabilities,
            "total_assets_cents": total_assets,
            "total_liabilities_cents": total_liabilities,
            "net_worth_cents": net_worth,
            "asset_buckets": ASSET_BUCKETS,
            "allocation_segments": _allocation_segments(allocation),
            "message": request.query_params.get("message"),
        },
    )


@router.post("/net-worth/assets")
def create_asset(
    request: Request,
    name: str = Form(...),
    institution: str = Form(""),
    current_value: str = Form(...),
    asset_bucket: str = Form("auto"),
    include_in_net_worth: str | None = Form(None),
    csrf_token: str = Form(...),
):
    services = _services(request)
    _require_csrf(request, csrf_token)
    try:
        value_cents = _money_to_cents(current_value, field_name="Asset value")
        record, classification = services.networth.create_asset(
            name=name,
            institution=institution,
            value_cents=value_cents,
            requested_bucket=None if asset_bucket == "auto" else asset_bucket,
            include=include_in_net_worth == "on",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    services.audit.record("asset_created")
    return RedirectResponse(
        _networth_url(f"Added {record.name} to {classification.asset_bucket}"), status_code=303
    )


@router.post("/net-worth/assets/{asset_id}")
def update_asset(
    asset_id: int,
    request: Request,
    name: str = Form(...),
    institution: str = Form(""),
    current_value: str = Form(...),
    asset_bucket: str = Form(...),
    include_in_net_worth: str | None = Form(None),
    csrf_token: str = Form(...),
):
    services = _services(request)
    _require_csrf(request, csrf_token)
    try:
        services.networth.update_asset(
            asset_id,
            name=name,
            institution=institution,
            value_cents=_money_to_cents(current_value, field_name="Asset value"),
            asset_bucket=asset_bucket,
            include=include_in_net_worth == "on",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    services.audit.record("asset_updated")
    return RedirectResponse(_networth_url("Asset updated"), status_code=303)


@router.post("/net-worth/assets/{asset_id}/inline")
async def inline_update_asset(asset_id: int, request: Request):
    services = _services(request)
    context = _session(request)
    if not context:
        raise HTTPException(status_code=401, detail="Authentication required.")
    csrf = request.headers.get("X-CSRF-Token", "")
    _require_csrf(request, csrf)
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid request body.") from exc
    field = str(payload.get("field") or "")
    if field not in {"name", "institution", "current_value"}:
        raise HTTPException(status_code=400, detail="Unsupported asset field.")
    asset = services.networth_repository.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Unknown asset.")

    name = asset.name
    institution = asset.institution or ""
    value_cents = asset.current_value_cents
    raw_value = str(payload.get("value") or "")
    if field == "name":
        name = raw_value
    elif field == "institution":
        institution = raw_value
    else:
        try:
            value_cents = _money_to_cents(raw_value, field_name="Asset value")
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    try:
        services.networth.update_asset(
            asset_id, name=name, institution=institution, value_cents=value_cents,
            asset_bucket=asset.asset_bucket, include=asset.include_in_net_worth,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    services.audit.record("asset_updated")
    updated = services.networth_repository.get_asset(asset_id)
    total_assets, total_liabilities, net_worth = services.networth_repository.totals()
    segments = _allocation_segments(services.networth_repository.allocation())
    return JSONResponse({
        "ok": True,
        "asset": {
            "id": asset_id,
            "name": updated.name if updated else name,
            "institution": (updated.institution or "") if updated else institution,
            "current_value": f"{((updated.current_value_cents if updated else value_cents) / 100):.2f}",
        },
        "totals": {
            "assets": total_assets,
            "liabilities": total_liabilities,
            "net_worth": net_worth,
        },
        "allocation": segments,
    })


@router.post("/net-worth/assets/{asset_id}/delete")
def delete_asset(asset_id: int, request: Request, csrf_token: str = Form(...)):
    services = _services(request)
    _require_csrf(request, csrf_token)
    try:
        services.networth_repository.delete_asset(asset_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    services.audit.record("asset_deleted")
    return RedirectResponse(_networth_url("Asset deleted"), status_code=303)


@router.post("/net-worth/liabilities")
def create_liability(
    request: Request,
    name: str = Form(...),
    institution: str = Form(""),
    current_balance: str = Form(...),
    include_in_net_worth: str | None = Form(None),
    csrf_token: str = Form(...),
):
    services = _services(request)
    _require_csrf(request, csrf_token)
    try:
        services.networth_repository.create_liability(
            name=name,
            institution=institution,
            balance_cents=_money_to_cents(current_balance, field_name="Liability balance"),
            include=include_in_net_worth == "on",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    services.audit.record("liability_created")
    return RedirectResponse(_networth_url("Liability added"), status_code=303)


@router.post("/net-worth/liabilities/{liability_id}")
def update_liability(
    liability_id: int,
    request: Request,
    name: str = Form(...),
    institution: str = Form(""),
    current_balance: str = Form(...),
    include_in_net_worth: str | None = Form(None),
    csrf_token: str = Form(...),
):
    services = _services(request)
    _require_csrf(request, csrf_token)
    try:
        services.networth_repository.update_liability(
            liability_id,
            name=name,
            institution=institution,
            balance_cents=_money_to_cents(current_balance, field_name="Liability balance"),
            include=include_in_net_worth == "on",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    services.audit.record("liability_updated")
    return RedirectResponse(_networth_url("Liability updated"), status_code=303)


@router.post("/net-worth/liabilities/{liability_id}/inline")
async def inline_update_liability(liability_id: int, request: Request):
    services = _services(request)

    context = _session(request)
    if not context:
        raise HTTPException(
            status_code=401,
            detail="Authentication required.",
        )

    csrf = request.headers.get("X-CSRF-Token", "")
    _require_csrf(request, csrf)

    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid request body.",
        ) from exc

    field = str(payload.get("field") or "")

    if field not in {
        "name",
        "institution",
        "current_balance",
    }:
        raise HTTPException(
            status_code=400,
            detail="Unsupported liability field.",
        )

    liability = services.networth_repository.get_liability(
        liability_id
    )

    if not liability:
        raise HTTPException(
            status_code=404,
            detail="Unknown liability.",
        )

    name = liability.name
    institution = liability.institution or ""
    balance_cents = liability.current_balance_cents

    raw_value = str(payload.get("value") or "")

    if field == "name":
        name = raw_value

    elif field == "institution":
        institution = raw_value

    else:
        try:
            balance_cents = _money_to_cents(
                raw_value,
                field_name="Liability balance",
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail=str(exc),
            ) from exc

    try:
        services.networth_repository.update_liability(
            liability_id,
            name=name,
            institution=institution,
            balance_cents=balance_cents,
            include=liability.include_in_net_worth,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    services.audit.record("liability_updated")

    updated = services.networth_repository.get_liability(
        liability_id
    )

    total_assets, total_liabilities, net_worth = (
        services.networth_repository.totals()
    )

    segments = _allocation_segments(
        services.networth_repository.allocation()
    )

    return JSONResponse(
        {
            "ok": True,
            "liability": {
                "id": liability_id,
                "name": (
                    updated.name if updated else name
                ),
                "institution": (
                    (updated.institution or "")
                    if updated
                    else institution
                ),
                "current_balance": (
                    f"{((updated.current_balance_cents if updated else balance_cents) / 100):.2f}"
                ),
            },
            "totals": {
                "assets": total_assets,
                "liabilities": total_liabilities,
                "net_worth": net_worth,
            },
            "allocation": segments,
        }
    )



@router.post("/net-worth/liabilities/{liability_id}/delete")
def delete_liability(liability_id: int, request: Request, csrf_token: str = Form(...)):
    services = _services(request)
    _require_csrf(request, csrf_token)
    try:
        services.networth_repository.delete_liability(liability_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    services.audit.record("liability_deleted")
    return RedirectResponse(_networth_url("Liability deleted"), status_code=303)


@router.get("/health/local")
def local_health(request: Request):
    services = _services(request)
    return JSONResponse(
        {
            "status": "ok",
            "loopback_only": services.settings.host == "127.0.0.1",
            "encrypted_database": services.database.require_cipher
            and not services.database.has_plaintext_sqlite_header(),
        }
    )
