from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import threading
import time
import uuid
from dataclasses import dataclass
from urllib.parse import urlencode

import httpx
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from cardbudget.categorization.provider import ProviderUnavailable
from cardbudget.db.engine import Database

ISSUER = "https://auth.openai.com"
RESOURCE = "https://api.openai.com/v1"
TOKEN_URL = f"{ISSUER}/api/accounts/oauth/token"
REVOKE_URL = f"{ISSUER}/api/accounts/oauth/revoke"
JWKS_URL = f"{ISSUER}/.well-known/jwks.json"
PLAN_SCOPE = "chatgpt.tokens.use.direct"
SCOPE = f"openid profile email offline_access resource.invoke {PLAN_SCOPE}"
CREDENTIALS = "categorization-chatgpt"
REGISTRATION = "categorization-chatgpt-registration"
DYNAMIC_CLIENT = "dynamic_agent_client"


def _encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _decode(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def _verify_id_token(token: str, keys: list[dict], *, client_id: str, nonce: str) -> dict:
    try:
        encoded_header, encoded_claims, signature = token.split(".")
        header = json.loads(_decode(encoded_header))
        if header["alg"] != "RS256":
            raise ValueError
        key = next(
            key for key in keys
            if key.get("kid") == header["kid"] and key.get("kty") == "RSA" and key.get("use", "sig") == "sig"
        )
        public_key = rsa.RSAPublicNumbers(
            int.from_bytes(_decode(key["e"]), "big"), int.from_bytes(_decode(key["n"]), "big"),
        ).public_key()
        public_key.verify(
            _decode(signature), f"{encoded_header}.{encoded_claims}".encode("ascii"),
            padding.PKCS1v15(), hashes.SHA256(),
        )
        claims = json.loads(_decode(encoded_claims))
        audience = claims["aud"]
        if (
            claims["iss"] != ISSUER
            or not (audience == client_id or (isinstance(audience, list) and client_id in audience))
            or ("azp" in claims and claims["azp"] != client_id)
            or (isinstance(audience, list) and len(audience) > 1 and claims.get("azp") != client_id)
            or type(claims["exp"]) is not int
            or claims["exp"] <= time.time()
            or not hmac.compare_digest(claims["nonce"], nonce)
            or not isinstance(claims["sub"], str)
            or not claims["sub"]
        ):
            raise ValueError
        return claims
    except (KeyError, StopIteration, TypeError, ValueError, InvalidSignature) as exc:
        raise ProviderUnavailable("ChatGPT sign-in could not be verified.", status="reconnect") from exc


@dataclass(frozen=True)
class SignIn:
    state: str
    nonce: str
    verifier: str
    redirect_uri: str
    return_url: str
    local_session_id: str
    client_id: str
    expected_sub: str
    expires: float


class ChatGPTConnection:
    def __init__(self, db: Database, *, transport=None):
        self.db = db
        self.transport = transport
        self._lock = threading.Lock()
        self._pending: SignIn | None = None

    def _http(self) -> httpx.Client:
        return httpx.Client(transport=self.transport, timeout=httpx.Timeout(12.0, connect=3.0), trust_env=False)

    def _record(self, key: str) -> dict:
        with self.db.connection() as conn:
            row = conn.execute("SELECT value FROM app_meta WHERE key = ?", (key,)).fetchone()
        return json.loads(row[0]) if row else {}

    @staticmethod
    def _store(conn, key: str, value: dict) -> None:
        conn.execute("INSERT OR REPLACE INTO app_meta(key, value) VALUES (?, ?)", (key, json.dumps(value)))

    def account(self) -> str | None:
        record = self._record(CREDENTIALS)
        if not record:
            return None
        return record.get("email") or "Connected ChatGPT account"

    def _host_id(self) -> str:
        with self.db.transaction() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO app_meta(key, value) VALUES ('chatgpt_host_id', ?)",
                (f"urn:uuid:{uuid.uuid4()}",),
            )
            return str(conn.execute("SELECT value FROM app_meta WHERE key = 'chatgpt_host_id'").fetchone()[0])

    def begin(self, *, port: int, return_url: str, local_session_id: str, new_account: bool = False) -> str:
        with self._lock:
            registration = {} if new_account else self._record(REGISTRATION)
            tokens = self._record(CREDENTIALS)
            attempt = SignIn(
                state=secrets.token_urlsafe(32), nonce=secrets.token_urlsafe(32), verifier=secrets.token_urlsafe(48),
                redirect_uri=f"http://127.0.0.1:{port}/settings/ai/chatgpt/callback",
                return_url=return_url, local_session_id=local_session_id,
                client_id=registration.get("client_id", DYNAMIC_CLIENT),
                expected_sub=registration.get("sub", ""), expires=time.monotonic() + 600,
            )
            params = {
                "client_id": attempt.client_id, "ext_agent_host_id": self._host_id(),
                "redirect_uri": attempt.redirect_uri, "scope": SCOPE, "response_type": "code",
                "state": attempt.state, "nonce": attempt.nonce, "resource": RESOURCE,
                "code_challenge": _encode(hashlib.sha256(attempt.verifier.encode("ascii")).digest()),
                "code_challenge_method": "S256",
            }
            if attempt.client_id == DYNAMIC_CLIENT:
                params["agent_name_hint"] = "PocketTrack"
            elif tokens.get("client_id") == attempt.client_id and tokens.get("id_token"):
                params["id_token_hint"] = tokens["id_token"]
            self._pending = attempt
            return f"{ISSUER}/api/accounts/authorize?{urlencode(params)}"

    def consume(self, state: str) -> SignIn | None:
        with self._lock:
            attempt = self._pending
            if not attempt or time.monotonic() >= attempt.expires or not hmac.compare_digest(attempt.state, state):
                return None
            self._pending = None
            return attempt

    @staticmethod
    def _tokens(response: httpx.Response, previous: dict) -> dict:
        if response.status_code in (400, 401, 403):
            try:
                error = response.json().get("error")
            except (ValueError, AttributeError):
                error = None
            if error in {
                "invalid_grant", "invalid_refresh_token", "token_expired", "refresh_token_expired",
                "refresh_token_invalidated", "refresh_token_reused",
            }:
                raise ProviderUnavailable("Reconnect your ChatGPT account.", status="reconnect")
            raise ProviderUnavailable("ChatGPT did not accept the sign-in request.", status="configuration")
        response.raise_for_status()
        result = response.json()
        scope = result.get("scope", previous.get("scope", ""))
        access = result["access_token"]
        refresh = result["refresh_token"]
        if (
            PLAN_SCOPE not in scope.split() or not isinstance(access, str) or not access
            or not isinstance(refresh, str) or not refresh
        ):
            raise ProviderUnavailable("Approve ChatGPT plan usage to enable this connection.", status="reconnect")
        expires_in = int(result["expires_in"])
        if expires_in <= 0:
            raise ValueError
        return {
            **previous, "access_token": access, "refresh_token": refresh, "scope": scope,
            "expires_at": time.time() + expires_in,
            "id_token": result.get("id_token") or previous.get("id_token"),
        }

    def finish(self, attempt: SignIn, *, client_id: str | None, code: str) -> None:
        if attempt.client_id == DYNAMIC_CLIENT:
            if not client_id or client_id == DYNAMIC_CLIENT:
                raise ProviderUnavailable("ChatGPT did not finish registration.", status="reconnect")
        else:
            if client_id and client_id != attempt.client_id:
                raise ProviderUnavailable("The ChatGPT registration changed.", status="reconnect")
            client_id = attempt.client_id

        with self._lock, self._http() as http:
            try:
                response = http.post(TOKEN_URL, data={
                    "grant_type": "authorization_code", "client_id": client_id, "code": code,
                    "code_verifier": attempt.verifier, "redirect_uri": attempt.redirect_uri, "resource": RESOURCE,
                })
                tokens = self._tokens(response, {})
                jwks = http.get(JWKS_URL)
                jwks.raise_for_status()
                claims = _verify_id_token(
                    tokens["id_token"], jwks.json()["keys"], client_id=client_id, nonce=attempt.nonce,
                )
                if attempt.expected_sub and claims["sub"] != attempt.expected_sub:
                    raise ProviderUnavailable("Choose the original ChatGPT account or connect another account.", status="reconnect")
            except (httpx.HTTPError, ValueError, KeyError, AttributeError, TypeError) as exc:
                raise ProviderUnavailable("The ChatGPT connection could not be completed.") from exc
            registration = {"client_id": client_id, "sub": claims["sub"]}
            with self.db.transaction() as conn:
                self._store(conn, REGISTRATION, registration)
                self._store(conn, CREDENTIALS, {**tokens, **registration, "email": claims.get("email")})

    def access_token(self) -> str:
        with self._lock:
            previous = self._record(CREDENTIALS)
            if not previous:
                raise ProviderUnavailable("Connect your ChatGPT account in Settings.", status="reconnect")
            if previous["expires_at"] > time.time() + 90:
                return previous["access_token"]
            try:
                with self._http() as http:
                    response = http.post(TOKEN_URL, data={
                        "grant_type": "refresh_token", "client_id": previous["client_id"],
                        "refresh_token": previous["refresh_token"], "resource": RESOURCE,
                    })
                    renewed = self._tokens(response, previous)
            except (httpx.HTTPError, ValueError, KeyError, AttributeError, TypeError) as exc:
                raise ProviderUnavailable("ChatGPT could not renew the connection.") from exc
            with self.db.transaction() as conn:
                self._store(conn, CREDENTIALS, renewed)
            return renewed["access_token"]

    def disconnect(self) -> bool:
        with self._lock:
            self._pending = None
            tokens = self._record(CREDENTIALS)
            with self.db.transaction() as conn:
                conn.execute("DELETE FROM app_meta WHERE key = ?", (CREDENTIALS,))
            if not tokens:
                return True
            try:
                with self._http() as http:
                    response = http.post(REVOKE_URL, data={
                        "token": tokens["refresh_token"], "token_type_hint": "refresh_token",
                        "client_id": tokens["client_id"],
                    })
                return response.status_code == 200
            except httpx.HTTPError:
                return False
