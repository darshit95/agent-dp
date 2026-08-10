from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import time


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _unb64(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


class FormTokenService:
    """Short-lived HMAC tokens for unauthenticated setup/login forms."""

    def __init__(self, secret: str, ttl_seconds: int = 600) -> None:
        self._secret = secret.encode("utf-8")
        self.ttl_seconds = ttl_seconds

    def issue(self, purpose: str, now: int | None = None) -> str:
        timestamp = int(time.time() if now is None else now)
        payload = f"{purpose}|{timestamp}|{secrets.token_urlsafe(18)}".encode("utf-8")
        signature = hmac.new(self._secret, payload, hashlib.sha256).digest()
        return f"{_b64(payload)}.{_b64(signature)}"

    def validate(self, token: str, purpose: str, now: int | None = None) -> bool:
        try:
            payload_encoded, signature_encoded = token.split(".", 1)
            payload = _unb64(payload_encoded)
            supplied_signature = _unb64(signature_encoded)
            expected_signature = hmac.new(self._secret, payload, hashlib.sha256).digest()
            if not hmac.compare_digest(supplied_signature, expected_signature):
                return False
            decoded = payload.decode("utf-8")
            token_purpose, timestamp_text, _nonce = decoded.split("|", 2)
            if token_purpose != purpose:
                return False
            timestamp = int(timestamp_text)
            current = int(time.time() if now is None else now)
            age = current - timestamp
            return -30 <= age <= self.ttl_seconds
        except (ValueError, TypeError, UnicodeDecodeError):
            return False
