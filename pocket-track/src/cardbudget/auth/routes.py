from __future__ import annotations

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from cardbudget.security.local_presence import LocalPresenceUnavailable
from cardbudget.security.passwords import PasswordPolicyError

router = APIRouter()


def _templates(request: Request):
    return request.app.state.templates


def _services(request: Request):
    return request.app.state.services


def _remote_addr(request: Request) -> str:
    return request.client.host if request.client else "local"


def _set_session_cookie(response: RedirectResponse, request: Request, session_id: str) -> None:
    settings = _services(request).settings
    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_id,
        max_age=settings.session_idle_seconds,
        httponly=True,
        samesite="strict",
        secure=(request.url.scheme == "https" or request.headers.get("x-forwarded-proto", "").lower() == "https"),
        path="/",
    )


def _current_session(request: Request):
    services = _services(request)
    session_id = request.cookies.get(services.settings.session_cookie_name)
    return services.sessions.resolve(session_id)


@router.get("/setup", response_class=HTMLResponse)
def setup_page(request: Request):
    services = _services(request)
    if services.auth.is_initialized():
        return RedirectResponse("/login", status_code=303)
    return _templates(request).TemplateResponse(
        request,
        "setup.html",
        {
            "csrf_token": services.form_tokens.issue("setup"),
            "error": None,
            "minimum_password_length": services.settings.password_min_length,
        },
    )


@router.post("/setup", response_class=HTMLResponse)
def setup_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    csrf_token: str = Form(...),
):
    services = _services(request)
    if services.auth.is_initialized():
        return RedirectResponse("/login", status_code=303)
    if not services.form_tokens.validate(csrf_token, "setup"):
        raise HTTPException(status_code=403, detail="Invalid form token.")

    error: str | None = None
    if password != confirm_password:
        error = "Passwords do not match."
    else:
        try:
            user = services.auth.setup_user(username, password)
        except (PasswordPolicyError, ValueError) as exc:
            error = str(exc)
        else:
            services.audit.record("setup_complete", _remote_addr(request))
            session = services.sessions.create(user.id)
            response = RedirectResponse("/", status_code=303)
            _set_session_cookie(response, request, session.id)
            return response

    return _templates(request).TemplateResponse(
        request,
        "setup.html",
        {
            "csrf_token": services.form_tokens.issue("setup"),
            "error": error,
            "minimum_password_length": services.settings.password_min_length,
            "username": username,
        },
        status_code=400,
    )


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    services = _services(request)
    if not services.auth.is_initialized():
        return RedirectResponse("/setup", status_code=303)
    if _current_session(request):
        return RedirectResponse("/", status_code=303)
    return _templates(request).TemplateResponse(
        request,
        "login.html",
        {
            "csrf_token": services.form_tokens.issue("login"),
            "error": None,
            "message": request.query_params.get("message"),
        },
    )


@router.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
):
    services = _services(request)
    if not services.auth.is_initialized():
        return RedirectResponse("/setup", status_code=303)
    if not services.form_tokens.validate(csrf_token, "login"):
        raise HTTPException(status_code=403, detail="Invalid form token.")

    remote = _remote_addr(request)
    decision = services.throttle.check(username, remote)
    if not decision.allowed:
        response = _templates(request).TemplateResponse(
            request,
            "login.html",
            {
                "csrf_token": services.form_tokens.issue("login"),
                "error": "Too many failed attempts. Try again shortly.",
                "message": None,
            },
            status_code=429,
        )
        response.headers["Retry-After"] = str(decision.retry_after_seconds)
        return response

    result = services.auth.authenticate(username, password)
    if not result.valid or not result.user:
        services.throttle.record_failure(username, remote)
        services.audit.record("login_failure", remote)
        return _templates(request).TemplateResponse(
            request,
            "login.html",
            {
                "csrf_token": services.form_tokens.issue("login"),
                "error": "Invalid username or password.",
                "message": None,
            },
            status_code=401,
        )

    services.throttle.record_success(username, remote)
    services.audit.record("login_success", remote)
    old_session_id = request.cookies.get(services.settings.session_cookie_name)
    if old_session_id:
        services.sessions.destroy(old_session_id)
    session = services.sessions.create(result.user.id)
    response = RedirectResponse("/", status_code=303)
    _set_session_cookie(response, request, session.id)
    return response


@router.post("/logout")
def logout(request: Request, csrf_token: str = Form(...)):
    services = _services(request)
    context = _current_session(request)
    if not context:
        return RedirectResponse("/login", status_code=303)
    if not services.sessions.validate_csrf(context, csrf_token):
        raise HTTPException(status_code=403, detail="Invalid CSRF token.")
    services.sessions.destroy(context.id)
    services.audit.record("logout", _remote_addr(request))
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(services.settings.session_cookie_name, path="/")
    return response


@router.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_page(request: Request):
    services = _services(request)
    if not services.auth.is_initialized():
        return RedirectResponse("/setup", status_code=303)
    return _templates(request).TemplateResponse(
        request,
        "forgot-password.html",
        {
            "csrf_token": services.form_tokens.issue("forgot_password"),
            "error": None,
            "minimum_password_length": services.settings.password_min_length,
        },
    )


@router.post("/forgot-password", response_class=HTMLResponse)
def forgot_password_submit(
    request: Request,
    username: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    csrf_token: str = Form(...),
):
    services = _services(request)
    if not services.auth.is_initialized():
        return RedirectResponse("/setup", status_code=303)
    if not services.form_tokens.validate(csrf_token, "forgot_password"):
        raise HTTPException(status_code=403, detail="Invalid form token.")

    remote = _remote_addr(request)
    decision = services.recovery_throttle.check(username, remote)
    if not decision.allowed:
        response = _templates(request).TemplateResponse(
            request,
            "forgot-password.html",
            {
                "csrf_token": services.form_tokens.issue("forgot_password"),
                "error": "Too many attempts. Try again shortly.",
                "minimum_password_length": services.settings.password_min_length,
            },
            status_code=429,
        )
        response.headers["Retry-After"] = str(decision.retry_after_seconds)
        return response

    error: str | None = None
    if new_password != confirm_password:
        error = "Passwords do not match."
    else:
        try:
            user = services.auth.reset_password_via_local_presence(username, new_password)
        except PasswordPolicyError as exc:
            # A weak new password is not a credential-guessing signal - don't throttle it.
            error = str(exc)
        except LocalPresenceUnavailable:
            # Not a failed attempt - the machine/platform simply can't do this
            # check at all, so don't count it against the throttle.
            error = (
                "Password recovery isn't available on this system (local device "
                "authentication - Touch ID/Windows Hello - could not be performed here)."
            )
        except ValueError:
            services.recovery_throttle.record_failure(username, remote)
            services.audit.record("password_reset_failed", remote)
            error = "Could not confirm it's you. Make sure the username is correct and complete the Touch ID/Windows Hello/password prompt."
        else:
            services.recovery_throttle.record_success(username, remote)
            services.audit.record("password_reset_via_local_presence", remote)
            # A password reset invalidates every existing session, same as a
            # settings-page change-password does - including any session the
            # forgetful user is still (unexpectedly) logged in under.
            services.sessions.repository.delete_all_for_user(user.id)
            from urllib.parse import quote_plus

            message = quote_plus("Password reset. Sign in with your new password.")
            return RedirectResponse(f"/login?message={message}", status_code=303)

    return _templates(request).TemplateResponse(
        request,
        "forgot-password.html",
        {
            "csrf_token": services.form_tokens.issue("forgot_password"),
            "error": error,
            "minimum_password_length": services.settings.password_min_length,
            "username": username,
        },
        status_code=400,
    )
