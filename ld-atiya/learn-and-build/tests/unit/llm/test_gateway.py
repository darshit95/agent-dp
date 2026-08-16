from types import SimpleNamespace
from unittest.mock import Mock

import litellm
import pytest

from llm import gateway as gateway_module
from llm.config import GatewayConfig, ProviderConfig
from llm.exceptions import AllProvidersFailedError
from llm.gateway import LLMGateway
from llm.types import Message, Role


def make_config(**overrides) -> GatewayConfig:
    defaults = dict(
        providers=(
            ProviderConfig(name="gemini", model="gemini/gemini-3.6-flash", api_key_env="GEMINI_API_KEY"),
            ProviderConfig(name="groq", model="groq/llama-3.3-70b-versatile", api_key_env="GROQ_API_KEY"),
        ),
        timeout_s=5.0,
        max_retries=2,
        backoff_base_s=0.001,
        backoff_max_s=0.002,
        circuit_failure_threshold=3,
        circuit_reset_timeout_s=60.0,
    )
    defaults.update(overrides)
    return GatewayConfig(**defaults)


def fake_response(content: str = "Recommend $149", prompt_tokens: int = 120, completion_tokens: int = 40):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))],
        usage=SimpleNamespace(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens),
    )


@pytest.fixture(autouse=True)
def api_keys(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")


@pytest.fixture
def messages():
    return [
        Message(Role.SYSTEM, "You are Atiya's pricing strategist."),
        Message(Role.USER, "What should tonight's rate be?"),
    ]


def test_generate_success_on_primary_provider(monkeypatch, messages):
    monkeypatch.setattr(gateway_module.litellm, "completion", Mock(return_value=fake_response()))
    monkeypatch.setattr(gateway_module.litellm, "completion_cost", Mock(return_value=0.0012))

    gw = LLMGateway(make_config())
    result = gw.generate(messages)

    assert result.content == "Recommend $149"
    assert result.provider == "gemini"
    assert result.model == "gemini/gemini-3.6-flash"
    assert result.tokens_prompt == 120
    assert result.tokens_completion == 40
    assert result.tokens_total == 160
    assert result.cost_usd == 0.0012
    assert result.fallback_used is False
    assert result.providers_tried == ("gemini",)
    assert result.latency_ms >= 0


def test_generate_falls_back_to_groq_on_transient_gemini_error(monkeypatch, messages):
    def side_effect(*, model, **kwargs):
        if model.startswith("gemini"):
            raise litellm.RateLimitError("rate limited", llm_provider="gemini", model=model)
        return fake_response(content="Recommend $139")

    monkeypatch.setattr(gateway_module.litellm, "completion", Mock(side_effect=side_effect))
    monkeypatch.setattr(gateway_module.litellm, "completion_cost", Mock(return_value=0.0005))

    gw = LLMGateway(make_config())
    result = gw.generate(messages)

    assert result.provider == "groq"
    assert result.content == "Recommend $139"
    assert result.fallback_used is True
    assert result.providers_tried == ("gemini", "groq")


def test_generate_skips_permanent_error_without_retry(monkeypatch, messages):
    call_count = {"gemini": 0, "groq": 0}

    def side_effect(*, model, **kwargs):
        if model.startswith("gemini"):
            call_count["gemini"] += 1
            raise litellm.AuthenticationError("bad key", llm_provider="gemini", model=model)
        call_count["groq"] += 1
        return fake_response()

    monkeypatch.setattr(gateway_module.litellm, "completion", Mock(side_effect=side_effect))
    monkeypatch.setattr(gateway_module.litellm, "completion_cost", Mock(return_value=0.0))

    gw = LLMGateway(make_config(max_retries=3))
    result = gw.generate(messages)

    assert call_count["gemini"] == 1  # no retries for a permanent error
    assert call_count["groq"] == 1
    assert result.fallback_used is True


def test_generate_raises_when_all_providers_fail(monkeypatch, messages):
    monkeypatch.setattr(
        gateway_module.litellm,
        "completion",
        Mock(side_effect=litellm.ServiceUnavailableError("down", llm_provider="x", model="x")),
    )

    gw = LLMGateway(make_config(max_retries=1))
    with pytest.raises(AllProvidersFailedError) as excinfo:
        gw.generate(messages)

    assert excinfo.value.providers_tried == ["gemini", "groq"]
    assert len(excinfo.value.errors) == 2


def test_generate_skips_provider_missing_api_key(monkeypatch, messages):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setattr(
        gateway_module.litellm,
        "completion",
        Mock(side_effect=litellm.RateLimitError("rate limited", llm_provider="gemini", model="gemini")),
    )

    gw = LLMGateway(make_config(max_retries=1))
    with pytest.raises(AllProvidersFailedError) as excinfo:
        gw.generate(messages)

    # groq was skipped (no key), not "tried and failed"
    assert excinfo.value.providers_tried == ["gemini"]


def test_generate_skips_provider_with_open_circuit(monkeypatch, messages):
    monkeypatch.setattr(gateway_module.litellm, "completion", Mock(return_value=fake_response()))
    monkeypatch.setattr(gateway_module.litellm, "completion_cost", Mock(return_value=0.0))

    gw = LLMGateway(make_config(circuit_failure_threshold=1))
    gw._breakers["gemini"].record_failure()  # force circuit open
    assert gw._breakers["gemini"].allow_request() is False

    result = gw.generate(messages)

    assert result.provider == "groq"
    assert result.providers_tried == ("groq",)


def test_retries_transient_error_before_succeeding_on_same_provider(monkeypatch, messages):
    attempts = {"count": 0}

    def side_effect(*, model, **kwargs):
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise litellm.Timeout("timed out", model=model, llm_provider="gemini")
        return fake_response()

    monkeypatch.setattr(gateway_module.litellm, "completion", Mock(side_effect=side_effect))
    monkeypatch.setattr(gateway_module.litellm, "completion_cost", Mock(return_value=0.0))

    gw = LLMGateway(make_config(max_retries=3))
    result = gw.generate(messages)

    assert attempts["count"] == 3
    assert result.provider == "gemini"
    assert result.fallback_used is False


def test_cost_lookup_failure_defaults_to_zero(monkeypatch, messages):
    monkeypatch.setattr(gateway_module.litellm, "completion", Mock(return_value=fake_response()))
    monkeypatch.setattr(gateway_module.litellm, "completion_cost", Mock(side_effect=Exception("no pricing data")))

    gw = LLMGateway(make_config())
    result = gw.generate(messages)

    assert result.cost_usd == 0.0
