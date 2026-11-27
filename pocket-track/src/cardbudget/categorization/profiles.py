from __future__ import annotations

from typing import Literal
from urllib.parse import urlsplit

import httpx
from pydantic import BaseModel, ConfigDict, Field, model_validator

from cardbudget.categorization.ollama import OllamaClassifierClient
from cardbudget.categorization.provider import Classifier, HTTPClassifier, ProviderUnavailable
from cardbudget.config import Settings
from cardbudget.db.engine import Database
from cardbudget.security.keychain import SecretStore

PROVIDER_LABELS = {
    "rules": "Rules only",
    "ollama": "Ollama",
    "local": "Local OpenAI-compatible endpoint",
    "chatgpt": "ChatGPT plan",
    "openai": "OpenAI API key",
    "anthropic": "Claude API key",
}
API_KEYS = {"openai": "categorization-openai-key", "anthropic": "categorization-anthropic-key"}
PREFS_KEY = "categorization_profile"
TEST_KEY = "categorization_last_test"


class CategorizationProfile(BaseModel):
    model_config = ConfigDict(frozen=True)

    provider: Literal["rules", "ollama", "local", "chatgpt", "openai", "anthropic"] = "rules"
    model: str = Field(default="", max_length=160, pattern=r"^[A-Za-z0-9._:/-]*$")
    endpoint: str = Field(default="", max_length=80)
    scheduled_cloud: bool = False
    cloud_assets: bool = False
    paused: bool = False

    @property
    def is_cloud(self) -> bool:
        return self.provider in {"chatgpt", "openai", "anthropic"}

    @model_validator(mode="after")
    def validate_provider(self) -> "CategorizationProfile":
        if self.provider != "rules" and not self.model:
            raise ValueError("Enter the provider's model ID.")
        if self.provider == "local":
            try:
                url = urlsplit(self.endpoint)
                if (
                    url.scheme != "http" or url.hostname != "127.0.0.1" or url.port is None
                    or url.path != "/v1" or url.query or url.fragment
                    or url.netloc != f"127.0.0.1:{url.port}"
                ):
                    raise ValueError
            except ValueError as exc:
                raise ValueError("Enter a local endpoint such as http://127.0.0.1:8080/v1.") from exc
        return self


class ProviderProfiles:
    def __init__(self, db: Database, secrets: SecretStore, settings: Settings, ollama: OllamaClassifierClient):
        self.db = db
        self.secrets = secrets
        self.ollama = ollama
        self.default = CategorizationProfile(
            provider=settings.categorization_default,
            model=settings.ollama_model if settings.categorization_default == "ollama" else "",
        )

    def get(self) -> CategorizationProfile:
        with self.db.connection() as conn:
            row = conn.execute("SELECT value FROM app_meta WHERE key = ?", (PREFS_KEY,)).fetchone()
        return CategorizationProfile.model_validate_json(row[0]) if row else self.default

    def save(self, profile: CategorizationProfile) -> None:
        with self.db.transaction() as conn:
            old = conn.execute("SELECT value FROM app_meta WHERE key = ?", (PREFS_KEY,)).fetchone()
            current = CategorizationProfile.model_validate_json(old[0]) if old else self.default
            if (current.provider, current.model, current.endpoint) != (profile.provider, profile.model, profile.endpoint):
                conn.execute("DELETE FROM app_meta WHERE key = ?", (TEST_KEY,))
            if current != profile:
                conn.execute("UPDATE categorization_work SET requested = MIN(requested, 1), running = MIN(running, 1) WHERE id = 1")
            conn.execute("INSERT OR REPLACE INTO app_meta(key, value) VALUES (?, ?)", (PREFS_KEY, profile.model_dump_json()))

    def last_test(self) -> str | None:
        with self.db.connection() as conn:
            row = conn.execute("SELECT value FROM app_meta WHERE key = ?", (TEST_KEY,)).fetchone()
        return str(row[0]) if row else None

    def set_last_test(self, profile: CategorizationProfile, timestamp: str | None) -> None:
        with self.db.transaction() as conn:
            saved = conn.execute("SELECT value FROM app_meta WHERE key = ?", (PREFS_KEY,)).fetchone()
            current = CategorizationProfile.model_validate_json(saved[0]) if saved else self.default
            if current != profile:
                return
            if timestamp is None:
                conn.execute("DELETE FROM app_meta WHERE key = ?", (TEST_KEY,))
            else:
                conn.execute("INSERT OR REPLACE INTO app_meta(key, value) VALUES (?, ?)", (TEST_KEY, timestamp))

    def api_key(self, provider: str) -> str:
        value = self.secrets.get_secret(API_KEYS[provider])
        if not value:
            raise ProviderUnavailable("Connect an API key for this provider.", status="reconnect")
        return value

    def save_api_key(self, provider: str, value: str) -> None:
        value = value.strip()
        if not value or len(value) > 512 or any(not 33 <= ord(character) <= 126 for character in value):
            raise ValueError("Enter a valid API key.")
        self.secrets.set_secret(API_KEYS[provider], value)

    def client(self, profile: CategorizationProfile, http: httpx.Client, chatgpt) -> Classifier:
        if profile.provider == "ollama":
            if profile.model == self.ollama.model:
                return self.ollama
            return OllamaClassifierClient(model=profile.model)
        if profile.provider == "chatgpt":
            credential = chatgpt.access_token
        elif profile.provider in API_KEYS:
            credential = lambda: self.api_key(profile.provider)
        elif profile.provider == "local":
            credential = lambda: ""
        else:
            raise ProviderUnavailable("Rules only has no model connection.", status="configuration")
        return HTTPClassifier(profile.provider, profile.model, credential, http, profile.endpoint)
