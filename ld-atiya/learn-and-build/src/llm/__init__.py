"""Provider-agnostic LLM gateway for Atiya.

Everything that needs to talk to an LLM (pricing strategist, demand
analyst, market intel agents, owner-facing explanations) goes through
`LLMGateway.generate()` - never a provider SDK directly. See
DECISIONS.md ADR-003 and learning-docs/all-topics/model-provider-abstraction/
for the design rationale.
"""

from .config import GatewayConfig, ProviderConfig
from .exceptions import (
    AllProvidersFailedError,
    LLMGatewayError,
    PermanentProviderError,
    ProviderError,
    TransientProviderError,
)
from .gateway import LLMGateway
from .types import LLMResponse, Message, Role

__all__ = [
    "AllProvidersFailedError",
    "GatewayConfig",
    "LLMGateway",
    "LLMGatewayError",
    "LLMResponse",
    "Message",
    "PermanentProviderError",
    "ProviderConfig",
    "ProviderError",
    "Role",
    "TransientProviderError",
]
