"""Environment-driven configuration for the LLM gateway.

Loaded once and immutable, so a misconfigured deployment fails at
startup rather than surfacing a confusing error deep inside a request.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    return float(raw) if raw else default


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    return int(raw) if raw else default


@dataclass(frozen=True, slots=True)
class ProviderConfig:
    name: str
    model: str
    api_key_env: str


@dataclass(frozen=True, slots=True)
class GatewayConfig:
    """Fallback chain plus reliability knobs.

    ADR-003: Gemini is primary (best free-tier model for agentic
    reasoning), Groq is the fallback used only when Gemini is
    rate-limited or erroring. Both are $0 free-tier providers - the
    paid tier is never auto-enabled (REQUIREMENTS.md "Cost Protection
    Strategy").
    """

    providers: tuple[ProviderConfig, ...]
    timeout_s: float = 30.0
    max_retries: int = 3
    backoff_base_s: float = 0.5
    backoff_max_s: float = 8.0
    circuit_failure_threshold: int = 5
    circuit_reset_timeout_s: float = 60.0

    @classmethod
    def from_env(cls) -> "GatewayConfig":
        gemini_model = os.environ.get("ATIYA_GEMINI_MODEL", "gemini/gemini-3.6-flash")
        groq_model = os.environ.get("ATIYA_GROQ_MODEL", "groq/llama-3.3-70b-versatile")
        return cls(
            providers=(
                ProviderConfig(name="gemini", model=gemini_model, api_key_env="GEMINI_API_KEY"),
                ProviderConfig(name="groq", model=groq_model, api_key_env="GROQ_API_KEY"),
            ),
            timeout_s=_env_float("ATIYA_LLM_TIMEOUT_S", 30.0),
            max_retries=_env_int("ATIYA_LLM_MAX_RETRIES", 3),
            backoff_base_s=_env_float("ATIYA_LLM_BACKOFF_BASE_S", 0.5),
            backoff_max_s=_env_float("ATIYA_LLM_BACKOFF_MAX_S", 8.0),
            circuit_failure_threshold=_env_int("ATIYA_LLM_CIRCUIT_FAILURE_THRESHOLD", 5),
            circuit_reset_timeout_s=_env_float("ATIYA_LLM_CIRCUIT_RESET_TIMEOUT_S", 60.0),
        )
