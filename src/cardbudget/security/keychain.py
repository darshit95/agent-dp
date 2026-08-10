from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from typing import Callable, Protocol

from cardbudget.errors import KeychainUnavailable, SecurityBootstrapError

DB_KEY_NAME = "db-key"
SESSION_SECRET_NAME = "session-secret"


class SecretStore(Protocol):
    def get_secret(self, name: str) -> str | None: ...

    def set_secret(self, name: str, value: str) -> None: ...

    def delete_secret(self, name: str) -> None: ...


class OSKeychain:
    """Thin wrapper around Python keyring. Imports lazily so tests need no OS backend."""

    def __init__(self, service_name: str = "cardbudget") -> None:
        self.service_name = service_name
        try:
            import keyring

            backend = keyring.get_keyring()
            priority = getattr(backend, "priority", 0)
            if callable(priority):
                priority = priority()
            if priority is not None and priority <= 0:
                raise KeychainUnavailable("No usable OS keychain backend is configured.")
            self._keyring = keyring
        except KeychainUnavailable:
            raise
        except Exception as exc:  # pragma: no cover - depends on host keychain
            raise KeychainUnavailable(
                "OS keychain is unavailable. PocketTrack refuses to fall back to a plaintext secret store."
            ) from exc

    def get_secret(self, name: str) -> str | None:
        try:
            return self._keyring.get_password(self.service_name, name)
        except Exception as exc:  # pragma: no cover - host-specific
            raise KeychainUnavailable(f"Unable to read keychain entry {name!r}.") from exc

    def set_secret(self, name: str, value: str) -> None:
        try:
            self._keyring.set_password(self.service_name, name, value)
        except Exception as exc:  # pragma: no cover - host-specific
            raise KeychainUnavailable(f"Unable to write keychain entry {name!r}.") from exc

    def delete_secret(self, name: str) -> None:
        try:
            self._keyring.delete_password(self.service_name, name)
        except Exception as exc:  # pragma: no cover - host-specific
            # Deleting a missing key is not security-sensitive, but backend failures are.
            error_name = exc.__class__.__name__
            if error_name != "PasswordDeleteError":
                raise KeychainUnavailable(f"Unable to delete keychain entry {name!r}.") from exc


@dataclass
class MemorySecretStore:
    """In-memory implementation used only by tests."""

    values: dict[str, str] = field(default_factory=dict)

    def get_secret(self, name: str) -> str | None:
        return self.values.get(name)

    def set_secret(self, name: str, value: str) -> None:
        self.values[name] = value

    def delete_secret(self, name: str) -> None:
        self.values.pop(name, None)


def ensure_secret(store: SecretStore, name: str, generator: Callable[[], str]) -> str:
    existing = store.get_secret(name)
    if existing:
        return existing
    value = generator()
    store.set_secret(name, value)
    round_trip = store.get_secret(name)
    if round_trip != value:
        raise SecurityBootstrapError(f"Secret {name!r} could not be verified after keychain write.")
    return value


def ensure_db_key(store: SecretStore) -> str:
    value = ensure_secret(store, DB_KEY_NAME, lambda: secrets.token_hex(32))
    if len(value) != 64:
        raise SecurityBootstrapError("Database key in keychain has an invalid length.")
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise SecurityBootstrapError("Database key in keychain is not valid hex.") from exc
    return value


def ensure_session_secret(store: SecretStore) -> str:
    value = ensure_secret(store, SESSION_SECRET_NAME, lambda: secrets.token_urlsafe(48))
    if len(value) < 40:
        raise SecurityBootstrapError("Session secret in keychain is unexpectedly short.")
    return value
