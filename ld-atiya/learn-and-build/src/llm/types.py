"""Data contracts for the LLM gateway.

Every provider response is normalized into `LLMResponse` before it leaves
the gateway, so callers never branch on which provider actually served
the request.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass(frozen=True, slots=True)
class Message:
    role: Role
    content: str

    def to_dict(self) -> dict[str, str]:
        return {"role": self.role.value, "content": self.content}


@dataclass(frozen=True, slots=True)
class LLMResponse:
    """Unified response shape - identical regardless of which provider served it.

    See learning-docs/all-topics/model-provider-abstraction/complete-learning.md,
    "Core Mechanics > 4. Unified Response".
    """

    content: str
    model: str
    provider: str
    tokens_prompt: int
    tokens_completion: int
    cost_usd: float
    latency_ms: float
    fallback_used: bool
    providers_tried: tuple[str, ...]

    @property
    def tokens_total(self) -> int:
        return self.tokens_prompt + self.tokens_completion
