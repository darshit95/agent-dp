"""Unified, provider-agnostic LLM gateway.

Wraps LiteLLM so the rest of Atiya calls a single `LLMGateway.generate()`
and never talks to a provider SDK directly (ADR-003). Gemini is tried
first; Groq is the fallback used only when Gemini is rate-limited,
erroring, or its circuit breaker is open. Both are $0 free-tier
providers - REQUIREMENTS.md "Cost Protection Strategy" is explicit that
the paid tier is never auto-enabled, so once every configured provider
is exhausted this raises `AllProvidersFailedError` instead of silently
upgrading to a paid model.
"""

from __future__ import annotations

import logging
import os
import random
import time
from typing import Sequence

import litellm

from .circuit_breaker import CircuitBreaker
from .config import GatewayConfig, ProviderConfig
from .exceptions import (
    AllProvidersFailedError,
    PermanentProviderError,
    ProviderError,
    TransientProviderError,
)
from .types import LLMResponse, Message

logger = logging.getLogger("atiya.llm.gateway")

# litellm normalizes every provider's SDK exceptions into these
# OpenAI-compatible types, regardless of which provider actually served
# (or failed to serve) the request.
_TRANSIENT_EXCEPTIONS = (
    litellm.RateLimitError,
    litellm.Timeout,
    litellm.APIConnectionError,
    litellm.ServiceUnavailableError,
    litellm.InternalServerError,
)
_PERMANENT_EXCEPTIONS = (
    litellm.AuthenticationError,
    litellm.BadRequestError,
    litellm.NotFoundError,
    litellm.ContentPolicyViolationError,
    litellm.PermissionDeniedError,
)

# Avoid litellm's own stdout debug/telemetry banners; we do our own logging.
litellm.suppress_debug_info = True


class LLMGateway:
    """Fallback-chain gateway with retry, circuit breaking, and cost/latency tracking."""

    def __init__(self, config: GatewayConfig | None = None) -> None:
        self._config = config or GatewayConfig.from_env()
        self._breakers: dict[str, CircuitBreaker] = {
            provider.name: CircuitBreaker(
                failure_threshold=self._config.circuit_failure_threshold,
                reset_timeout_s=self._config.circuit_reset_timeout_s,
            )
            for provider in self._config.providers
        }

    def generate(
        self,
        messages: Sequence[Message],
        *,
        temperature: float = 0.3,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Send `messages` to the first available provider in the fallback chain.

        Providers are tried in configured order (Gemini, then Groq).
        Within a single provider, transient errors are retried with
        exponential backoff up to `max_retries`; permanent errors skip
        straight to the next provider. A provider whose circuit breaker
        is open, or whose API key isn't set, is skipped without being
        called at all.

        Raises:
            AllProvidersFailedError: every provider was exhausted, skipped,
                or unavailable.
        """
        payload = [message.to_dict() for message in messages]
        providers_tried: list[str] = []
        errors: list[ProviderError] = []
        start = time.monotonic()

        for index, provider in enumerate(self._config.providers):
            breaker = self._breakers[provider.name]
            if not breaker.allow_request():
                logger.warning("llm.provider_skipped_circuit_open", extra={"provider": provider.name})
                continue
            if not os.environ.get(provider.api_key_env):
                logger.warning(
                    "llm.provider_skipped_no_api_key",
                    extra={"provider": provider.name, "env_var": provider.api_key_env},
                )
                continue

            providers_tried.append(provider.name)
            try:
                raw_response = self._call_with_retry(
                    provider, payload, temperature=temperature, max_tokens=max_tokens
                )
            except ProviderError as exc:
                errors.append(exc)
                breaker.record_failure()
                logger.warning(
                    "llm.provider_failed",
                    extra={"provider": provider.name, "transient": exc.transient, "error": str(exc)},
                )
                continue

            breaker.record_success()
            latency_ms = (time.monotonic() - start) * 1000
            response = self._to_llm_response(
                raw_response,
                provider=provider,
                latency_ms=latency_ms,
                fallback_used=index > 0,
                providers_tried=tuple(providers_tried),
            )
            logger.info(
                "llm.request_completed",
                extra={
                    "provider": response.provider,
                    "model": response.model,
                    "tokens_total": response.tokens_total,
                    "cost_usd": response.cost_usd,
                    "latency_ms": response.latency_ms,
                    "fallback_used": response.fallback_used,
                },
            )
            return response

        logger.error("llm.all_providers_failed", extra={"providers_tried": providers_tried})
        raise AllProvidersFailedError(providers_tried, errors)

    def _call_with_retry(
        self,
        provider: ProviderConfig,
        payload: list[dict[str, str]],
        *,
        temperature: float,
        max_tokens: int | None,
    ):
        """Retry transient failures with exponential backoff + jitter; raise immediately on permanent ones."""
        last_error: ProviderError | None = None
        for attempt in range(self._config.max_retries):
            try:
                return litellm.completion(
                    model=provider.model,
                    messages=payload,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=self._config.timeout_s,
                )
            except _PERMANENT_EXCEPTIONS as exc:
                raise PermanentProviderError(provider.name, str(exc)) from exc
            except _TRANSIENT_EXCEPTIONS as exc:
                last_error = TransientProviderError(provider.name, str(exc))
            except Exception as exc:  # noqa: BLE001 - unclassified provider failure, treat as transient
                last_error = TransientProviderError(provider.name, str(exc))

            if attempt < self._config.max_retries - 1:
                self._sleep_backoff(attempt)

        assert last_error is not None  # loop always runs at least once
        raise last_error

    def _sleep_backoff(self, attempt: int) -> None:
        delay = min(self._config.backoff_base_s * (2**attempt), self._config.backoff_max_s)
        delay *= 0.5 + random.random()  # +/-50% jitter to avoid synchronized retries
        time.sleep(delay)

    def _to_llm_response(
        self,
        raw_response,
        *,
        provider: ProviderConfig,
        latency_ms: float,
        fallback_used: bool,
        providers_tried: tuple[str, ...],
    ) -> LLMResponse:
        usage = getattr(raw_response, "usage", None)
        tokens_prompt = getattr(usage, "prompt_tokens", 0) or 0
        tokens_completion = getattr(usage, "completion_tokens", 0) or 0
        try:
            cost_usd = litellm.completion_cost(completion_response=raw_response)
        except Exception:  # noqa: BLE001 - unknown pricing for this model shouldn't fail the request
            logger.warning("llm.cost_lookup_failed", extra={"model": provider.model})
            cost_usd = 0.0

        return LLMResponse(
            content=raw_response.choices[0].message.content or "",
            model=provider.model,
            provider=provider.name,
            tokens_prompt=tokens_prompt,
            tokens_completion=tokens_completion,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            fallback_used=fallback_used,
            providers_tried=providers_tried,
        )
