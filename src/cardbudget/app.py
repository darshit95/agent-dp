from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.trustedhost import TrustedHostMiddleware

from cardbudget.auth.routes import router as auth_router
from cardbudget.config import Settings
from cardbudget.plaid.routes import router as plaid_router
from cardbudget.services import ApplicationServices, bootstrap_services
from cardbudget.web.routes import router as web_router


async def _security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if request.url.scheme == "https" or request.headers.get("x-forwarded-proto", "").lower() == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000"

    # Plaid Link must load its web SDK directly from cdn.plaid.com. Keep the
    # exception narrow: only Settings/Link endpoints get the Plaid CSP grants.
    if request.url.path.startswith("/settings") or request.url.path.startswith("/plaid"):
        plaid_api = (
            "https://sandbox.plaid.com" if request.app.state.services.settings.plaid_environment == "sandbox"
            else "https://production.plaid.com"
        )
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https://cdn.plaid.com; "
            "script-src 'self' https://cdn.plaid.com/link/v2/stable/link-initialize.js; "
            "frame-src https://cdn.plaid.com; "
            f"connect-src 'self' {plaid_api}; "
            "form-action 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'none'"
        )
    else:
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "style-src 'self'; "
            "img-src 'self'; "
            "script-src 'self'; "
            "connect-src 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'none'"
        )
    if request.url.path not in {"/static/app.css", "/static/app.js", "/static/plaid.js"}:
        response.headers["Cache-Control"] = "no-store"
    return response


def create_app(
    settings: Settings | None = None,
    *,
    services: ApplicationServices | None = None,
) -> FastAPI:
    resolved_settings = settings or Settings.from_env()
    resolved_services = services or bootstrap_services(resolved_settings)

    app = FastAPI(
        title="PocketTrack",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.services = resolved_services

    package_dir = Path(__file__).resolve().parent
    template_dir = package_dir / "web" / "templates"
    static_dir = package_dir / "web" / "static"
    app.state.templates = Jinja2Templates(directory=str(template_dir))

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["127.0.0.1", "localhost", "my-pocket-track"],
    )
    app.middleware("http")(_security_headers)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    app.include_router(auth_router)
    app.include_router(plaid_router)
    app.include_router(web_router)
    return app
