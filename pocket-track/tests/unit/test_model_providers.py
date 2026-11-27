from __future__ import annotations

import json
import time
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from pydantic import ValidationError

from cardbudget.categorization.chatgpt import (
    CREDENTIALS, ISSUER, PLAN_SCOPE, ChatGPTConnection, _encode,
)
from cardbudget.categorization.profiles import CategorizationProfile
from cardbudget.categorization.provider import HTTPClassifier, ProviderUnavailable


@pytest.mark.parametrize("kind", ["openai", "anthropic", "chatgpt"])
def test_cloud_provider_sends_minimal_fields_and_checks_output(kind):
    def respond(request):
        body = json.loads(request.content)
        assert "PRIVATE BANK DESCRIPTION" not in request.content.decode()
        assert "EXAMPLE STORE" in request.content.decode()
        assert "tools" not in body
        result = '{"bucket":"Shopping","confidence":0.9}'
        if kind == "anthropic":
            assert request.headers["x-api-key"] == "test-key"
            assert body["output_config"]["format"]["type"] == "json_schema"
            return httpx.Response(200, json={"stop_reason": "end_turn", "content": [{"type": "text", "text": result}]})
        assert request.headers["authorization"] == "Bearer test-key"
        assert body["store"] is False
        if kind == "chatgpt":
            assert body["stream"] and "background" not in body
            events = [{"type": "response.output_text.delta", "delta": result}, {"type": "response.completed"}]
            return httpx.Response(200, text="".join(f"data: {json.dumps(event)}\n\n" for event in events))
        assert body["text"]["format"]["strict"]
        return httpx.Response(200, json={
            "status": "completed", "output": [{"type": "message", "content": [{"type": "output_text", "text": result}]}],
        })

    with httpx.Client(transport=httpx.MockTransport(respond)) as http:
        classifier = HTTPClassifier(kind, "example", lambda: "test-key", http)
        result = classifier.classify(
            merchant="EXAMPLE STORE", description="PRIVATE BANK DESCRIPTION",
            pfc_primary=None, pfc_detailed=None, buckets=["Shopping"],
        )
        assert result.bucket_name == "Shopping"


def test_plan_only_accepts_completed_stream_and_handles_quota():
    events = [
        {"type": "response.output_text.delta", "delta": '{"bucket":"Shopping","confidence":0.9}'},
        {"type": "response.failed", "response": {"error": {"code": "subscription_sharing_usage_limit_exceeded"}}},
    ]
    content = "".join(f"data: {json.dumps(event)}\n\n" for event in events)
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, text=content))) as http:
        classifier = HTTPClassifier("chatgpt", "example", lambda: "token", http)
        with pytest.raises(ProviderUnavailable) as error:
            classifier.classify(merchant="Example", description="", pfc_primary=None, pfc_detailed=None, buckets=["Shopping"])
    assert error.value.status == "limit_reached"


@pytest.mark.parametrize("url", ["https://example.org/v1", "http://127.0.0.1:80/v1?x=1", "http://127.0.0.1:80@evil.test/v1"])
def test_user_supplied_local_endpoint_stays_on_loopback(url):
    with pytest.raises(ValidationError):
        CategorizationProfile(provider="local", model="example", endpoint=url)


def test_chatgpt_validates_oidc_exchanges_and_rotates_credentials(test_stack):
    _settings, _store, db, _services, _client = test_stack
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    numbers = key.public_key().public_numbers()

    def encoded_number(number):
        return _encode(number.to_bytes((number.bit_length() + 7) // 8, "big"))

    def sign(claims):
        header = _encode(json.dumps({"alg": "RS256", "kid": "test-key"}).encode())
        payload = _encode(json.dumps(claims).encode())
        content = f"{header}.{payload}"
        signature = key.sign(content.encode(), padding.PKCS1v15(), hashes.SHA256())
        return f"{content}.{_encode(signature)}"

    calls = []
    authorization = {}

    def respond(request):
        calls.append(request.url.path)
        if request.url.path.endswith("/jwks.json"):
            return httpx.Response(200, json={
                "keys": [{"kid": "test-key", "kty": "RSA", "n": encoded_number(numbers.n), "e": encoded_number(numbers.e)}],
            })
        params = parse_qs(request.content.decode())
        assert params["client_id"] == ["issued-client"]
        if request.url.path.endswith("/revoke"):
            assert params["token"] == ["rotated-refresh"]
            return httpx.Response(200)
        if params["grant_type"] == ["refresh_token"]:
            assert params["refresh_token"] == ["initial-refresh"]
            return httpx.Response(200, json={
                "access_token": "renewed", "refresh_token": "rotated-refresh", "expires_in": 3600,
            })
        assert params["code"] == ["test-code"]
        assert params["redirect_uri"] == ["http://127.0.0.1:8000/settings/ai/chatgpt/callback"]
        return httpx.Response(200, json={
            "access_token": "initial", "refresh_token": "initial-refresh", "expires_in": 1, "scope": PLAN_SCOPE,
            "id_token": sign({
                "aud": "issued-client", "iss": ISSUER, "sub": "test-account", "exp": int(time.time()) + 3600,
                "nonce": authorization["nonce"][0], "email": "example@example.test",
            }),
        })

    connection = ChatGPTConnection(db, transport=httpx.MockTransport(respond))
    url = connection.begin(port=8000, return_url="/settings", local_session_id="session")
    authorization = parse_qs(urlsplit(url).query)
    assert authorization["client_id"] == ["dynamic_agent_client"]
    assert authorization["code_challenge_method"] == ["S256"]
    assert connection.consume("forged") is None
    attempt = connection.consume(authorization["state"][0])
    assert attempt is not None
    assert connection.consume(authorization["state"][0]) is None
    connection.finish(attempt, client_id="issued-client", code="test-code")
    assert connection.account() == "example@example.test"
    assert connection.access_token() == "renewed"
    assert connection.access_token() == "renewed"
    assert connection.disconnect()
    with db.connection() as conn:
        assert conn.execute("SELECT 1 FROM app_meta WHERE key = ?", (CREDENTIALS,)).fetchone() is None
    assert len(calls) == 4
