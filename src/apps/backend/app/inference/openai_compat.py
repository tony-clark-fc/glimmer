"""OpenAI-compatible inference provider — targets LM Studio and similar.

PLAN:WorkstreamI.PackageI1.InferenceAbstraction
ARCH:LocalInferenceBaseline
ARCH:TargetHardwareProfile

Implements the InferenceProvider protocol using the `openai` Python SDK
pointed at a local OpenAI-compatible endpoint (LM Studio by default).

Design decisions:
- Uses the official `openai` SDK for maximum compatibility
- Async-only (AsyncOpenAI) — Glimmer's backend is async throughout
- Structured error mapping: SDK exceptions → InferenceError
- Latency tracking on every call for operational visibility
- Health check uses /v1/models endpoint to verify availability
"""

from __future__ import annotations

import logging
import time
from typing import Any

import openai
from openai import AsyncOpenAI

from app.inference.base import (
    InferenceError,
    InferenceResult,
    ProviderHealth,
    ProviderStatus,
)
from app.inference.config import InferenceSettings

logger = logging.getLogger(__name__)


class OpenAICompatibleProvider:
    """LLM inference provider using an OpenAI-compatible API.

    TEST:LLM.Provider.OpenAICompatibleConnectsToLMStudio
    TEST:LLM.Provider.HealthCheckReportsModelAvailability
    TEST:LLM.Provider.GracefulDegradationWhenUnavailable
    TEST:LLM.Provider.TimeoutHandledCleanly
    TEST:LLM.Provider.ChatCompletionReturnsStructuredResult
    """

    def __init__(self, settings: InferenceSettings | None = None) -> None:
        self._settings = settings or InferenceSettings()
        self._client = AsyncOpenAI(
            base_url=self._settings.base_url,
            api_key=self._settings.api_key,
            timeout=openai.Timeout(
                connect=self._settings.connect_timeout_seconds,
                read=self._settings.read_timeout_seconds,
                write=30.0,
                pool=10.0,
            ),
            max_retries=self._settings.max_retries,
        )
        self._provider_name = f"openai_compat:{self._settings.base_url}"

    @property
    def provider_name(self) -> str:
        """Human-readable name of this provider instance."""
        return self._provider_name

    @property
    def settings(self) -> InferenceSettings:
        """The configuration this provider was created with."""
        return self._settings

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        response_format: dict | None = None,
    ) -> InferenceResult:
        """Send a chat completion request to the provider.

        Raises InferenceError on any failure — the caller must handle
        fallback to deterministic logic.
        """
        temp = temperature if temperature is not None else self._settings.default_temperature
        tokens = max_tokens if max_tokens is not None else self._settings.default_max_tokens

        kwargs: dict[str, Any] = {
            "model": self._settings.model_name,
            "messages": messages,
            "temperature": temp,
            "max_tokens": tokens,
        }

        if response_format is not None:
            kwargs["response_format"] = response_format
        elif self._settings.prefer_json_mode:
            # Only request JSON mode when the system prompt asks for JSON
            # to avoid confusing models that don't support it well.
            # Callers should pass response_format explicitly when needed.
            pass

        start = time.monotonic()
        try:
            response = await self._client.chat.completions.create(**kwargs)
        except openai.APITimeoutError as exc:
            latency = (time.monotonic() - start) * 1000
            logger.warning(
                "Inference timeout after %.0fms: %s", latency, exc
            )
            raise InferenceError(
                f"Inference request timed out after {self._settings.read_timeout_seconds}s",
                provider=self._provider_name,
                is_timeout=True,
                detail=str(exc),
            ) from exc
        except openai.APIConnectionError as exc:
            latency = (time.monotonic() - start) * 1000
            logger.warning(
                "Inference connection failed (%.0fms): %s", latency, exc
            )
            raise InferenceError(
                f"Cannot connect to inference provider at {self._settings.base_url}",
                provider=self._provider_name,
                is_unavailable=True,
                detail=str(exc),
            ) from exc
        except openai.APIStatusError as exc:
            latency = (time.monotonic() - start) * 1000
            logger.warning(
                "Inference API error (%.0fms): %s %s",
                latency,
                exc.status_code,
                exc.message,
            )
            raise InferenceError(
                f"Inference API error: {exc.status_code} {exc.message}",
                provider=self._provider_name,
                detail=str(exc),
            ) from exc
        except Exception as exc:
            latency = (time.monotonic() - start) * 1000
            logger.error(
                "Unexpected inference error (%.0fms): %s", latency, exc
            )
            raise InferenceError(
                f"Unexpected inference error: {exc}",
                provider=self._provider_name,
                detail=str(exc),
            ) from exc

        latency_ms = (time.monotonic() - start) * 1000

        choice = response.choices[0] if response.choices else None
        content = choice.message.content if choice and choice.message else ""
        finish_reason = choice.finish_reason if choice else None

        usage = response.usage
        result = InferenceResult(
            content=content or "",
            model=response.model or self._settings.model_name,
            prompt_tokens=usage.prompt_tokens if usage else None,
            completion_tokens=usage.completion_tokens if usage else None,
            total_tokens=usage.total_tokens if usage else None,
            latency_ms=latency_ms,
            finish_reason=finish_reason,
            raw_response=response.model_dump() if response else None,
        )

        logger.info(
            "Inference complete: model=%s tokens=%s latency=%.0fms finish=%s",
            result.model,
            result.total_tokens,
            result.latency_ms,
            result.finish_reason,
        )

        return result

    async def health_check(self) -> ProviderHealth:
        """Check provider availability by listing models.

        Uses a short timeout separate from the generation timeout.
        """
        start = time.monotonic()
        try:
            # Create a short-timeout client for health probing
            health_client = AsyncOpenAI(
                base_url=self._settings.base_url,
                api_key=self._settings.api_key,
                timeout=openai.Timeout(
                    connect=self._settings.health_timeout_seconds,
                    read=self._settings.health_timeout_seconds,
                    write=5.0,
                    pool=5.0,
                ),
                max_retries=0,
            )
            models_response = await health_client.models.list()
            latency_ms = (time.monotonic() - start) * 1000

            model_ids = [m.id for m in models_response.data]
            target_loaded = self._settings.model_name in model_ids

            if target_loaded:
                return ProviderHealth(
                    status=ProviderStatus.HEALTHY,
                    model_name=self._settings.model_name,
                    latency_ms=latency_ms,
                    detail=f"Model loaded. {len(model_ids)} model(s) available.",
                )
            elif model_ids:
                # Provider is up but target model not loaded
                return ProviderHealth(
                    status=ProviderStatus.DEGRADED,
                    model_name=model_ids[0],
                    latency_ms=latency_ms,
                    detail=(
                        f"Target model '{self._settings.model_name}' not found. "
                        f"Available: {model_ids}"
                    ),
                )
            else:
                return ProviderHealth(
                    status=ProviderStatus.DEGRADED,
                    latency_ms=latency_ms,
                    detail="Provider responded but no models loaded.",
                )

        except (openai.APIConnectionError, openai.APITimeoutError) as exc:
            latency_ms = (time.monotonic() - start) * 1000
            logger.info("Health check: provider unavailable (%.0fms)", latency_ms)
            return ProviderHealth(
                status=ProviderStatus.UNAVAILABLE,
                latency_ms=latency_ms,
                detail=f"Cannot reach provider: {exc}",
            )
        except Exception as exc:
            latency_ms = (time.monotonic() - start) * 1000
            logger.warning("Health check unexpected error: %s", exc)
            return ProviderHealth(
                status=ProviderStatus.UNAVAILABLE,
                latency_ms=latency_ms,
                detail=f"Unexpected error: {exc}",
            )


