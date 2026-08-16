"""Exceptions raised by the LLM gateway.

Failures are classified into two categories (see
learning-docs/all-topics/model-provider-abstraction/complete-learning.md,
"Failure Modes"):

- Transient: rate limits, timeouts, 5xx - retried with backoff, then the
  gateway falls back to the next provider.
- Permanent: bad API key, unknown model, content policy violation - the
  gateway skips straight to the next provider without retrying.

`AllProvidersFailedError` is raised only once every provider in the
fallback chain has been exhausted (or skipped because its circuit is
open / its API key is missing).
"""

from __future__ import annotations


class LLMGatewayError(Exception):
    """Base class for all gateway errors."""


class ProviderError(LLMGatewayError):
    """A single provider call failed."""

    def __init__(self, provider: str, message: str, *, transient: bool) -> None:
        self.provider = provider
        self.transient = transient
        super().__init__(f"[{provider}] {message}")


class TransientProviderError(ProviderError):
    """Rate limit, timeout, or 5xx - worth retrying / falling back."""

    def __init__(self, provider: str, message: str) -> None:
        super().__init__(provider, message, transient=True)


class PermanentProviderError(ProviderError):
    """Bad API key, unknown model, content policy - retrying is pointless."""

    def __init__(self, provider: str, message: str) -> None:
        super().__init__(provider, message, transient=False)


class AllProvidersFailedError(LLMGatewayError):
    """Every provider in the fallback chain was exhausted.

    Per REQUIREMENTS.md "Cost Protection Strategy" this is a terminal
    failure, not a trigger to fall back to a paid tier - callers should
    surface a "service busy, try again shortly" message rather than
    retrying immediately.
    """

    def __init__(self, providers_tried: list[str], errors: list[ProviderError]) -> None:
        self.providers_tried = providers_tried
        self.errors = errors
        detail = "; ".join(str(error) for error in errors) if errors else "no provider was callable"
        super().__init__(f"All providers failed ({', '.join(providers_tried) or 'none tried'}): {detail}")
