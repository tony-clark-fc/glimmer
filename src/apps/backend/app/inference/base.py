"""Inference provider protocol and shared result types.

PLAN:WorkstreamI.PackageI1.InferenceAbstraction
ARCH:LocalInferenceBaseline
ARCH:TargetHardwareProfile

Defines the provider contract that all inference backends must satisfy.
The protocol is designed to accommodate:
- OpenAI-compatible APIs (LM Studio, vLLM, etc.)
- Future in-process providers (mlx-lm for Gemma 4 E4B voice)
- Future embedding providers (for pgvector semantic retrieval)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol, runtime_checkable


class ProviderStatus(str, Enum):
    """Health status of an inference provider."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class ProviderHealth:
    """Health check result from an inference provider.

    TEST:LLM.Provider.HealthCheckReportsModelAvailability
    """

    status: ProviderStatus
    model_name: str | None = None
    latency_ms: float | None = None
    detail: str = ""

    @property
    def is_available(self) -> bool:
        """Whether the provider is usable for inference."""
        return self.status in (ProviderStatus.HEALTHY, ProviderStatus.DEGRADED)


@dataclass(frozen=True)
class InferenceResult:
    """Structured result of an LLM chat completion.

    TEST:LLM.Provider.ChatCompletionReturnsStructuredResult
    """

    content: str
    model: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    latency_ms: float = 0.0
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    finish_reason: str | None = None
    raw_response: dict | None = None


class InferenceError(Exception):
    """Raised when inference fails in a way that should trigger fallback.

    TEST:LLM.Provider.GracefulDegradationWhenUnavailable
    TEST:LLM.Provider.TimeoutHandledCleanly
    """

    def __init__(
        self,
        message: str,
        *,
        provider: str = "",
        is_timeout: bool = False,
        is_unavailable: bool = False,
        detail: str = "",
    ):
        super().__init__(message)
        self.provider = provider
        self.is_timeout = is_timeout
        self.is_unavailable = is_unavailable
        self.detail = detail


@runtime_checkable
class InferenceProvider(Protocol):
    """Protocol defining the contract for all inference providers.

    ARCH:LocalInferenceBaseline — clean abstraction for model backends.
    ARCH:VoiceInfrastructureDirection — must accommodate future voice provider.

    Implementations must:
    - Return InferenceResult on success
    - Raise InferenceError on failure (not crash, not silent)
    - Handle timeouts cleanly
    - Report health status accurately
    """

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        response_format: dict | None = None,
    ) -> InferenceResult:
        """Send a chat completion request to the provider.

        Args:
            messages: OpenAI-format message list [{role, content}].
            temperature: Sampling temperature (0.0 = deterministic).
            max_tokens: Maximum tokens to generate.
            response_format: Optional response format hint (e.g. {"type": "json_object"}).

        Returns:
            InferenceResult with the model's response.

        Raises:
            InferenceError: On timeout, connectivity failure, or model error.
        """
        ...

    async def health_check(self) -> ProviderHealth:
        """Check whether the provider is available and responsive.

        Returns:
            ProviderHealth indicating status, model name, and latency.
        """
        ...


