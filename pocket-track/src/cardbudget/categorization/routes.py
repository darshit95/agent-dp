from __future__ import annotations

from urllib.parse import quote_plus

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from cardbudget.categorization.profiles import API_KEYS, CategorizationProfile
from cardbudget.categorization.provider import ProviderUnavailable
from cardbudget.categorization.worker import JOB_MESSAGES
from cardbudget.db.repositories import utc_now
from cardbudget.plaid.routes import _require_csrf, _services

router = APIRouter(prefix="/settings/ai")
DEFAULT_MODELS = {
    "chatgpt": "gpt-6.2-sol",
    "openai": "gpt-5-mini",
}


@router.get("/status")
def classification_status(request: Request):
    services = _services(request)
    session_id = request.cookies.get(services.settings.session_cookie_name)
    session = services.sessions.repository.get(session_id) if session_id else None
    if session is None or session.expires_at <= utc_now():
        raise HTTPException(status_code=401, detail="Authentication required.")
    status = services.categorization_worker.status()
    return {"status": status, "message": JOB_MESSAGES.get(status, "")}


def _redirect(message: str, base: str = "/settings") -> RedirectResponse:
    return RedirectResponse(f"{base}?message={quote_plus(message)}#ai-connections", status_code=303)


@router.post("/provider")
def save_provider(
    request: Request,
    csrf_token: str = Form(...),
    provider: str = Form(...),
    model: str = Form(""),
    endpoint: str = Form(""),
    cloud_consent: bool = Form(False),
    scheduled_cloud: bool = Form(False),
    cloud_assets: bool = Form(False),
):
    _require_csrf(request, csrf_token)
    services = _services(request)
    current = services.providers.get()
    cloud = provider in {"chatgpt", "openai", "anthropic"}
    if cloud and provider != current.provider and not cloud_consent:
        return _redirect("Approve cloud categorization before selecting this provider.")
    new_model = model.strip() or (current.model if provider == current.provider else "")
    default_model = services.settings.ollama_model if provider == "ollama" else DEFAULT_MODELS.get(provider, "")
    new_model = new_model or default_model
    new_endpoint = endpoint.strip().rstrip("/") or (current.endpoint if provider == current.provider else "")
    try:
        profile = CategorizationProfile(
            provider=provider, model=new_model if provider != "rules" else "",
            endpoint=new_endpoint if provider == "local" else "",
            scheduled_cloud=cloud and scheduled_cloud, cloud_assets=cloud and cloud_assets,
            paused=current.paused if provider == current.provider else False,
        )
    except ValidationError as exc:
        message = exc.errors(include_input=False)[0]["msg"]
        return _redirect(message.removeprefix("Value error, "))
    services.providers.save(profile)
    services.categorization_worker.request()
    return _redirect("Categorization settings saved.")


@router.post("/key")
def save_key(request: Request, csrf_token: str = Form(...), api_key: str = Form(...)):
    _require_csrf(request, csrf_token)
    services = _services(request)
    profile = services.providers.get()
    if profile.provider not in API_KEYS:
        return _redirect("Choose an API-key provider first.")
    try:
        services.providers.save_api_key(profile.provider, api_key)
    except ValueError as exc:
        return _redirect(str(exc))
    services.providers.set_last_test(profile, None)
    return _redirect("API key saved to your OS credential store.")


@router.post("/test")
def test_connection(request: Request, csrf_token: str = Form(...)):
    _require_csrf(request, csrf_token)
    try:
        _services(request).categorization_worker.test_connection()
    except ProviderUnavailable as exc:
        return _redirect(str(exc))
    return _redirect("Connection test succeeded using synthetic data.")


@router.post("/pause")
def pause_connection(request: Request, csrf_token: str = Form(...), paused: bool = Form(...)):
    _require_csrf(request, csrf_token)
    services = _services(request)
    profile = services.providers.get()
    if profile.provider == "rules":
        return _redirect("Rules-only mode is active.")
    services.providers.save(profile.model_copy(update={"paused": paused}))
    return _redirect("Model classification paused." if paused else "Model classification resumed.")


@router.post("/disconnect")
def disconnect(request: Request, csrf_token: str = Form(...)):
    _require_csrf(request, csrf_token)
    services = _services(request)
    profile = services.providers.get()
    services.providers.save(CategorizationProfile())
    if profile.provider == "chatgpt" and not services.chatgpt.disconnect():
        return _redirect("Disconnected locally. Open ChatGPT settings to confirm remote revocation.")
    if profile.provider in API_KEYS:
        services.secret_store.delete_secret(API_KEYS[profile.provider])
    return _redirect("Model disconnected. Rules-only mode is active.")


@router.post("/categorize")
def queue_classification(request: Request, csrf_token: str = Form(...)):
    _require_csrf(request, csrf_token)
    services = _services(request)
    profile = services.providers.get()
    if profile.provider == "rules" or profile.paused:
        return _redirect("Choose and enable a model provider first.")
    services.categorization_worker.request(manual=True)
    return _redirect("AI categorization queued.")


@router.post("/retry-legacy")
def retry_legacy(request: Request, csrf_token: str = Form(...)):
    _require_csrf(request, csrf_token)
    services = _services(request)
    count = services.transactions.requeue_legacy_unknown()
    services.categorization_worker.request()
    return _redirect(f"Queued {count} older automatic Unknown transactions for review.")


@router.post("/chatgpt/connect")
def connect_chatgpt(request: Request, csrf_token: str = Form(...), new_account: bool = Form(False)):
    context = _require_csrf(request, csrf_token)
    services = _services(request)
    if services.providers.get().provider != "chatgpt":
        return _redirect("Choose ChatGPT plan first.")
    host = request.url.hostname
    if host == "my-pocket-track":
        base = "https://my-pocket-track/settings"
    else:
        base = f"http://{'localhost' if host == 'localhost' else '127.0.0.1'}:{services.settings.port}/settings"
    if new_account and services.chatgpt.account():
        return _redirect("Disconnect the current ChatGPT account before using another one.")
    url = services.chatgpt.begin(
        port=services.settings.port, return_url=base, local_session_id=context.id, new_account=new_account,
    )
    return RedirectResponse(url, status_code=303)


@router.get("/chatgpt/callback")
def chatgpt_callback(request: Request):
    if request.url.hostname != "127.0.0.1" or request.url.scheme != "http":
        raise HTTPException(status_code=400, detail="Use the local ChatGPT callback address.")
    state = request.query_params.get("state", "")
    code = request.query_params.get("code", "")
    client_id = request.query_params.get("client_id")
    error = request.query_params.get("error")
    if len(state) > 128 or len(code) > 2048 or (client_id and len(client_id) > 256):
        raise HTTPException(status_code=400, detail="Invalid ChatGPT callback.")
    services = _services(request)
    attempt = services.chatgpt.consume(state)
    if not attempt:
        raise HTTPException(status_code=400, detail="ChatGPT sign-in expired or was already used.")
    session = services.sessions.repository.get(attempt.local_session_id)
    if session is None or session.expires_at <= utc_now():
        return _redirect("Sign in to PocketTrack before connecting ChatGPT.", attempt.return_url)
    profile = services.providers.get()
    if profile.provider != "chatgpt" or error or not code:
        return _redirect("ChatGPT plan connection was not completed.", attempt.return_url)
    try:
        services.chatgpt.finish(attempt, client_id=client_id, code=code)
    except ProviderUnavailable as exc:
        return _redirect(str(exc), attempt.return_url)
    services.providers.set_last_test(profile, None)
    return _redirect("ChatGPT plan connected. Test the connection before categorizing.", attempt.return_url)
