from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Settings(BaseModel):
    """Runtime settings. The application server itself is always loopback-only."""

    model_config = ConfigDict(frozen=True)

    host: Literal["127.0.0.1"] = "127.0.0.1"
    port: int = Field(default=8000, ge=1024, le=65535)
    data_dir: Path = Field(default_factory=lambda: Path.home() / ".pockettrack")
    database_filename: str = "pockettrack.db"
    keychain_service: str = "pockettrack"
    session_cookie_name: str = "pockettrack_session"
    session_idle_seconds: int = Field(default=1800, ge=60, le=86400)
    form_token_ttl_seconds: int = Field(default=600, ge=60, le=3600)
    login_attempt_window_seconds: int = Field(default=300, ge=30, le=3600)
    login_max_failures: int = Field(default=5, ge=2, le=20)
    login_lockout_seconds: int = Field(default=30, ge=1, le=600)
    password_min_length: int = Field(default=12, ge=10, le=64)
    plaid_environment: Literal["sandbox", "production"] = "production"
    ollama_model: str = Field(default="qwen3.5:4b", min_length=1, max_length=100, pattern=r"^[A-Za-z0-9._:/-]+$")

    @field_validator("data_dir", mode="before")
    @classmethod
    def _expand_data_dir(cls, value: object) -> Path:
        return Path(value).expanduser().resolve()

    @property
    def database_path(self) -> Path:
        return self.data_dir / self.database_filename

    @property
    def preferences_path(self) -> Path:
        return self.data_dir / "preferences.json"

    def persist_preferences(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if os.name == "posix":
            os.chmod(self.data_dir, 0o700)
        tmp = self.preferences_path.with_suffix(".json.tmp")
        tmp.write_text(
            json.dumps(
                {
                    "plaid_environment": self.plaid_environment,
                    "ollama_model": self.ollama_model,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )
        if os.name == "posix":
            os.chmod(tmp, 0o600)
        tmp.replace(self.preferences_path)

    @classmethod
    def from_env(cls) -> "Settings":
        values: dict[str, object] = {}

        # New PocketTrack names are primary. Legacy CardBudget names remain accepted
        # so older local installations can migrate without exporting secrets/data.
        data_env = os.environ.get("POCKETTRACK_DATA_DIR") or os.environ.get("CARDBUDGET_DATA_DIR")
        if data_env:
            values["data_dir"] = data_env
        data_dir = Path(values.get("data_dir", Path.home() / ".pockettrack")).expanduser().resolve()
        prefs = data_dir / "preferences.json"
        if prefs.exists():
            try:
                payload = json.loads(prefs.read_text())
                if payload.get("plaid_environment") in {"sandbox", "production"}:
                    values["plaid_environment"] = payload["plaid_environment"]
                model = payload.get("ollama_model")
                if isinstance(model, str) and model:
                    values["ollama_model"] = model
            except (OSError, ValueError, TypeError):
                pass

        pairs = (
            ("POCKETTRACK_HOST", "CARDBUDGET_HOST", "host"),
            ("POCKETTRACK_PORT", "CARDBUDGET_PORT", "port"),
            ("POCKETTRACK_DATA_DIR", "CARDBUDGET_DATA_DIR", "data_dir"),
            ("POCKETTRACK_SESSION_IDLE_SECONDS", "CARDBUDGET_SESSION_IDLE_SECONDS", "session_idle_seconds"),
            ("POCKETTRACK_PLAID_ENVIRONMENT", "CARDBUDGET_PLAID_ENVIRONMENT", "plaid_environment"),
            ("POCKETTRACK_OLLAMA_MODEL", "CARDBUDGET_OLLAMA_MODEL", "ollama_model"),
        )
        for current, legacy, field_name in pairs:
            if current in os.environ:
                values[field_name] = os.environ[current]
            elif legacy in os.environ:
                values[field_name] = os.environ[legacy]
        settings = cls(**values)
        settings.persist_preferences()
        return settings
