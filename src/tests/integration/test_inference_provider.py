"""Unit tests for the inference abstraction layer — base types and protocol.

TEST:LLM.Provider.HealthCheckReportsModelAvailability
TEST:LLM.Provider.GracefulDegradationWhenUnavailable
TEST:LLM.Provider.TimeoutHandledCleanly
TEST:LLM.Provider.ChatCompletionReturnsStructuredResult

These tests validate the inference types, protocol conformance, and
error handling without requiring a live LLM provider. The provider
is tested through mocking/patching of the openai SDK.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.inference.base import (
    InferenceError,
    InferenceProvider,
    InferenceResult,
    ProviderHealth,
    ProviderStatus,
)
from app.inference.config import InferenceSettings
from app.inference.openai_compat import OpenAICompatibleProvider


# ── Result type tests ────────────────────────────────────────────────


class TestInferenceResult:
    """Verify InferenceResult structure and defaults."""

    def test_result_fields(self) -> None:
        result = InferenceResult(
            content='{"project": "Alpha"}',
            model="google/gemma-4-31b",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            latency_ms=1234.5,
            finish_reason="stop",
        )
        assert result.content == '{"project": "Alpha"}'
        assert result.model == "google/gemma-4-31b"
        assert result.prompt_tokens == 100
        assert result.completion_tokens == 50
        assert result.total_tokens == 150
        assert result.latency_ms == 1234.5
        assert result.finish_reason == "stop"
        assert result.request_id  # auto-generated UUID

    def test_result_defaults(self) -> None:
        result = InferenceResult(content="hello", model="test")
        assert result.prompt_tokens is None
        assert result.completion_tokens is None
        assert result.total_tokens is None
        assert result.latency_ms == 0.0
        assert result.finish_reason is None
        assert result.raw_response is None

    def test_result_is_frozen(self) -> None:
        result = InferenceResult(content="test", model="test")
        with pytest.raises(AttributeError):
            result.content = "modified"  # type: ignore[misc]


# ── ProviderHealth tests ─────────────────────────────────────────────


class TestProviderHealth:
    """TEST:LLM.Provider.HealthCheckReportsModelAvailability"""

    def test_healthy_is_available(self) -> None:
        health = ProviderHealth(
            status=ProviderStatus.HEALTHY,
            model_name="google/gemma-4-31b",
            latency_ms=42.0,
        )
        assert health.is_available
        assert health.model_name == "google/gemma-4-31b"

    def test_degraded_is_available(self) -> None:
        health = ProviderHealth(
            status=ProviderStatus.DEGRADED,
            detail="Target model not loaded",
        )
        assert health.is_available

    def test_unavailable_is_not_available(self) -> None:
        health = ProviderHealth(
            status=ProviderStatus.UNAVAILABLE,
            detail="Connection refused",
        )
        assert not health.is_available

    def test_health_is_frozen(self) -> None:
        health = ProviderHealth(status=ProviderStatus.HEALTHY)
        with pytest.raises(AttributeError):
            health.status = ProviderStatus.UNAVAILABLE  # type: ignore[misc]


# ── InferenceError tests ─────────────────────────────────────────────


class TestInferenceError:
    """TEST:LLM.Provider.GracefulDegradationWhenUnavailable
    TEST:LLM.Provider.TimeoutHandledCleanly
    """

    def test_timeout_error(self) -> None:
        err = InferenceError(
            "Request timed out",
            provider="test",
            is_timeout=True,
        )
        assert err.is_timeout
        assert not err.is_unavailable
        assert err.provider == "test"
        assert str(err) == "Request timed out"

    def test_unavailable_error(self) -> None:
        err = InferenceError(
            "Connection refused",
            provider="test",
            is_unavailable=True,
        )
        assert err.is_unavailable
        assert not err.is_timeout

    def test_generic_error(self) -> None:
        err = InferenceError("Something broke", detail="traceback here")
        assert not err.is_timeout
        assert not err.is_unavailable
        assert err.detail == "traceback here"


# ── Protocol conformance ─────────────────────────────────────────────


class TestProtocolConformance:
    """Verify OpenAICompatibleProvider satisfies InferenceProvider protocol."""

    def test_provider_is_protocol_instance(self) -> None:
        settings = InferenceSettings(base_url="http://localhost:9999/v1")
        provider = OpenAICompatibleProvider(settings)
        assert isinstance(provider, InferenceProvider)

    def test_provider_name_reflects_endpoint(self) -> None:
        settings = InferenceSettings(base_url="http://127.0.0.1:1234/v1")
        provider = OpenAICompatibleProvider(settings)
        assert "127.0.0.1:1234" in provider.provider_name


# ── Config tests ─────────────────────────────────────────────────────


class TestInferenceSettings:
    """Verify InferenceSettings defaults and overrides."""

    def test_default_settings(self) -> None:
        settings = InferenceSettings()
        assert settings.base_url == "http://127.0.0.1:1234/v1"
        assert settings.api_key == "lm-studio"
        assert settings.model_name == "google/gemma-4-31b"
        assert settings.default_temperature == 0.3
        assert settings.default_max_tokens == 2000
        assert settings.connect_timeout_seconds == 5.0
        assert settings.read_timeout_seconds == 120.0
        assert settings.health_timeout_seconds == 5.0
        assert settings.prefer_json_mode is True
        assert settings.max_retries == 1

    def test_settings_override(self) -> None:
        settings = InferenceSettings(
            base_url="http://10.0.0.5:8080/v1",
            model_name="custom/model",
            default_temperature=0.7,
            read_timeout_seconds=60.0,
        )
        assert settings.base_url == "http://10.0.0.5:8080/v1"
        assert settings.model_name == "custom/model"
        assert settings.default_temperature == 0.7
        assert settings.read_timeout_seconds == 60.0


# ── Provider chat_completion mocked tests ────────────────────────────


def _mock_chat_response(
    content: str = '{"result": "ok"}',
    model: str = "google/gemma-4-31b",
    finish_reason: str = "stop",
    prompt_tokens: int = 50,
    completion_tokens: int = 30,
) -> MagicMock:
    """Build a mock OpenAI ChatCompletion response."""
    usage = MagicMock()
    usage.prompt_tokens = prompt_tokens
    usage.completion_tokens = completion_tokens
    usage.total_tokens = prompt_tokens + completion_tokens

    message = MagicMock()
    message.content = content

    choice = MagicMock()
    choice.message = message
    choice.finish_reason = finish_reason

    response = MagicMock()
    response.choices = [choice]
    response.model = model
    response.usage = usage
    response.model_dump.return_value = {"id": "test", "object": "chat.completion"}

    return response


class TestProviderChatCompletion:
    """TEST:LLM.Provider.ChatCompletionReturnsStructuredResult"""

    @pytest.mark.asyncio
    async def test_successful_completion(self) -> None:
        """A successful chat completion returns a well-formed InferenceResult."""
        settings = InferenceSettings(base_url="http://localhost:9999/v1")
        provider = OpenAICompatibleProvider(settings)

        mock_response = _mock_chat_response(
            content='{"classification": "Alpha Project"}',
            prompt_tokens=100,
            completion_tokens=50,
        )

        with patch.object(
            provider._client.chat.completions, "create",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            result = await provider.chat_completion(
                messages=[{"role": "user", "content": "Classify this message"}],
                temperature=0.0,
                max_tokens=500,
            )

        assert isinstance(result, InferenceResult)
        assert result.content == '{"classification": "Alpha Project"}'
        assert result.model == "google/gemma-4-31b"
        assert result.prompt_tokens == 100
        assert result.completion_tokens == 50
        assert result.total_tokens == 150
        assert result.finish_reason == "stop"
        assert result.latency_ms > 0
        assert result.request_id  # UUID generated

    @pytest.mark.asyncio
    async def test_uses_default_temperature_and_tokens(self) -> None:
        """When no overrides given, uses settings defaults."""
        settings = InferenceSettings(
            base_url="http://localhost:9999/v1",
            default_temperature=0.5,
            default_max_tokens=1000,
        )
        provider = OpenAICompatibleProvider(settings)

        mock_create = AsyncMock(return_value=_mock_chat_response())

        with patch.object(
            provider._client.chat.completions, "create", mock_create
        ):
            await provider.chat_completion(
                messages=[{"role": "user", "content": "test"}],
            )

        call_kwargs = mock_create.call_args.kwargs
        assert call_kwargs["temperature"] == 0.5
        assert call_kwargs["max_tokens"] == 1000

    @pytest.mark.asyncio
    async def test_response_format_passed_through(self) -> None:
        """response_format is forwarded to the API."""
        settings = InferenceSettings(base_url="http://localhost:9999/v1")
        provider = OpenAICompatibleProvider(settings)

        mock_create = AsyncMock(return_value=_mock_chat_response())

        with patch.object(
            provider._client.chat.completions, "create", mock_create
        ):
            await provider.chat_completion(
                messages=[{"role": "user", "content": "test"}],
                response_format={"type": "json_object"},
            )

        call_kwargs = mock_create.call_args.kwargs
        assert call_kwargs["response_format"] == {"type": "json_object"}


# ── Provider error handling tests ────────────────────────────────────


class TestProviderErrorHandling:
    """TEST:LLM.Provider.GracefulDegradationWhenUnavailable
    TEST:LLM.Provider.TimeoutHandledCleanly
    """

    @pytest.mark.asyncio
    async def test_connection_error_raises_inference_error(self) -> None:
        """Connection failure → InferenceError with is_unavailable=True."""
        settings = InferenceSettings(base_url="http://localhost:9999/v1")
        provider = OpenAICompatibleProvider(settings)

        with patch.object(
            provider._client.chat.completions,
            "create",
            new_callable=AsyncMock,
            side_effect=__import__("openai").APIConnectionError(
                request=MagicMock()
            ),
        ):
            with pytest.raises(InferenceError) as exc_info:
                await provider.chat_completion(
                    messages=[{"role": "user", "content": "test"}],
                )

        assert exc_info.value.is_unavailable
        assert not exc_info.value.is_timeout

    @pytest.mark.asyncio
    async def test_timeout_error_raises_inference_error(self) -> None:
        """Timeout → InferenceError with is_timeout=True."""
        settings = InferenceSettings(base_url="http://localhost:9999/v1")
        provider = OpenAICompatibleProvider(settings)

        with patch.object(
            provider._client.chat.completions,
            "create",
            new_callable=AsyncMock,
            side_effect=__import__("openai").APITimeoutError(
                request=MagicMock()
            ),
        ):
            with pytest.raises(InferenceError) as exc_info:
                await provider.chat_completion(
                    messages=[{"role": "user", "content": "test"}],
                )

        assert exc_info.value.is_timeout
        assert not exc_info.value.is_unavailable

    @pytest.mark.asyncio
    async def test_api_status_error_raises_inference_error(self) -> None:
        """HTTP error (e.g. 500) → InferenceError with detail."""
        settings = InferenceSettings(base_url="http://localhost:9999/v1")
        provider = OpenAICompatibleProvider(settings)

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.headers = {}
        mock_response.json.return_value = {"error": {"message": "Internal error"}}

        with patch.object(
            provider._client.chat.completions,
            "create",
            new_callable=AsyncMock,
            side_effect=__import__("openai").InternalServerError(
                message="Internal error",
                response=mock_response,
                body={"error": {"message": "Internal error"}},
            ),
        ):
            with pytest.raises(InferenceError) as exc_info:
                await provider.chat_completion(
                    messages=[{"role": "user", "content": "test"}],
                )

        assert not exc_info.value.is_timeout
        assert not exc_info.value.is_unavailable

    @pytest.mark.asyncio
    async def test_unexpected_error_raises_inference_error(self) -> None:
        """Unexpected exceptions are wrapped in InferenceError."""
        settings = InferenceSettings(base_url="http://localhost:9999/v1")
        provider = OpenAICompatibleProvider(settings)

        with patch.object(
            provider._client.chat.completions,
            "create",
            new_callable=AsyncMock,
            side_effect=RuntimeError("surprise"),
        ):
            with pytest.raises(InferenceError) as exc_info:
                await provider.chat_completion(
                    messages=[{"role": "user", "content": "test"}],
                )

        assert "surprise" in exc_info.value.detail


# ── Provider health check mocked tests ───────────────────────────────


def _mock_models_response(model_ids: list[str]) -> MagicMock:
    """Build a mock OpenAI models.list() response."""
    models = []
    for mid in model_ids:
        m = MagicMock()
        m.id = mid
        models.append(m)

    response = MagicMock()
    response.data = models
    return response


class TestProviderHealthCheck:
    """TEST:LLM.Provider.HealthCheckReportsModelAvailability"""

    @pytest.mark.asyncio
    async def test_healthy_when_target_model_loaded(self) -> None:
        """Target model present → HEALTHY."""
        settings = InferenceSettings(
            base_url="http://localhost:9999/v1",
            model_name="google/gemma-4-31b",
        )
        provider = OpenAICompatibleProvider(settings)

        mock_list = AsyncMock(
            return_value=_mock_models_response(["google/gemma-4-31b", "other/model"])
        )

        with patch("app.inference.openai_compat.AsyncOpenAI") as MockClient:
            instance = MockClient.return_value
            instance.models.list = mock_list
            health = await provider.health_check()

        assert health.status == ProviderStatus.HEALTHY
        assert health.model_name == "google/gemma-4-31b"
        assert health.is_available

    @pytest.mark.asyncio
    async def test_degraded_when_target_model_not_loaded(self) -> None:
        """Provider up but target model missing → DEGRADED."""
        settings = InferenceSettings(
            base_url="http://localhost:9999/v1",
            model_name="google/gemma-4-31b",
        )
        provider = OpenAICompatibleProvider(settings)

        mock_list = AsyncMock(
            return_value=_mock_models_response(["other/model-7b"])
        )

        with patch("app.inference.openai_compat.AsyncOpenAI") as MockClient:
            instance = MockClient.return_value
            instance.models.list = mock_list
            health = await provider.health_check()

        assert health.status == ProviderStatus.DEGRADED
        assert health.is_available
        assert "gemma-4-31b" in health.detail

    @pytest.mark.asyncio
    async def test_degraded_when_no_models_loaded(self) -> None:
        """Provider up but empty model list → DEGRADED."""
        settings = InferenceSettings(base_url="http://localhost:9999/v1")
        provider = OpenAICompatibleProvider(settings)

        mock_list = AsyncMock(return_value=_mock_models_response([]))

        with patch("app.inference.openai_compat.AsyncOpenAI") as MockClient:
            instance = MockClient.return_value
            instance.models.list = mock_list
            health = await provider.health_check()

        assert health.status == ProviderStatus.DEGRADED
        assert health.is_available
        assert "no models" in health.detail.lower()

    @pytest.mark.asyncio
    async def test_unavailable_on_connection_error(self) -> None:
        """Cannot reach provider → UNAVAILABLE."""
        settings = InferenceSettings(base_url="http://localhost:9999/v1")
        provider = OpenAICompatibleProvider(settings)

        mock_list = AsyncMock(
            side_effect=__import__("openai").APIConnectionError(
                request=MagicMock()
            )
        )

        with patch("app.inference.openai_compat.AsyncOpenAI") as MockClient:
            instance = MockClient.return_value
            instance.models.list = mock_list
            health = await provider.health_check()

        assert health.status == ProviderStatus.UNAVAILABLE
        assert not health.is_available

    @pytest.mark.asyncio
    async def test_unavailable_on_timeout(self) -> None:
        """Health check timeout → UNAVAILABLE."""
        settings = InferenceSettings(base_url="http://localhost:9999/v1")
        provider = OpenAICompatibleProvider(settings)

        mock_list = AsyncMock(
            side_effect=__import__("openai").APITimeoutError(
                request=MagicMock()
            )
        )

        with patch("app.inference.openai_compat.AsyncOpenAI") as MockClient:
            instance = MockClient.return_value
            instance.models.list = mock_list
            health = await provider.health_check()

        assert health.status == ProviderStatus.UNAVAILABLE
        assert not health.is_available



