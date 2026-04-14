"""Live integration tests — LLM provider against running LM Studio.

TEST:LLM.Provider.OpenAICompatibleConnectsToLMStudio
TEST:LLM.Provider.HealthCheckReportsModelAvailability
TEST:LLM.Provider.ChatCompletionReturnsStructuredResult

These tests require LM Studio to be running at http://127.0.0.1:1234
with a model loaded.  They are excluded from the normal test suite and
run explicitly:

    cd src/apps/backend
    python -m pytest ../../tests/live/test_live_llm_connection.py -v -s

Equivalent to the WS-H live browser tests in execution model.
"""

from __future__ import annotations

import logging
import json

import pytest

from app.inference.base import InferenceResult, ProviderHealth, ProviderStatus
from app.inference.config import InferenceSettings
from app.inference.openai_compat import OpenAICompatibleProvider

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)

logger = logging.getLogger(__name__)


# ── Fixtures ─────────────────────────────────────────────────────────


@pytest.fixture()
def provider() -> OpenAICompatibleProvider:
    """Create a provider pointing at the local LM Studio instance."""
    settings = InferenceSettings(
        # Use defaults — LM Studio at 127.0.0.1:1234
        connect_timeout_seconds=10.0,
        read_timeout_seconds=120.0,
        health_timeout_seconds=10.0,
    )
    return OpenAICompatibleProvider(settings)


# ── Health Check ─────────────────────────────────────────────────────


class TestLiveHealthCheck:
    """TEST:LLM.Provider.HealthCheckReportsModelAvailability"""

    @pytest.mark.asyncio
    @pytest.mark.manual_only
    async def test_health_check_reports_status(self, provider: OpenAICompatibleProvider) -> None:
        """Health check should report available with a model loaded."""
        health = await provider.health_check()

        logger.info("Health status: %s", health.status)
        logger.info("Model: %s", health.model_name)
        logger.info("Latency: %.0fms", health.latency_ms or 0)
        logger.info("Detail: %s", health.detail)

        assert health.is_available, f"Provider not available: {health.detail}"
        assert health.latency_ms is not None
        assert health.latency_ms < 5000, "Health check took >5s — too slow"


# ── Basic Chat Completion ────────────────────────────────────────────


class TestLiveChatCompletion:
    """TEST:LLM.Provider.OpenAICompatibleConnectsToLMStudio
    TEST:LLM.Provider.ChatCompletionReturnsStructuredResult
    """

    @pytest.mark.asyncio
    @pytest.mark.manual_only
    async def test_simple_completion(self, provider: OpenAICompatibleProvider) -> None:
        """Provider can send a prompt and receive a text response."""
        result = await provider.chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Respond briefly."},
                {"role": "user", "content": "What is 2 + 2? Answer with just the number."},
            ],
            temperature=0.0,
            max_tokens=50,
        )

        logger.info("Response: %s", result.content)
        logger.info("Model: %s", result.model)
        logger.info("Tokens: %s (prompt=%s, completion=%s)",
                     result.total_tokens, result.prompt_tokens, result.completion_tokens)
        logger.info("Latency: %.0fms", result.latency_ms)
        logger.info("Finish reason: %s", result.finish_reason)

        assert isinstance(result, InferenceResult)
        assert result.content  # non-empty response
        assert "4" in result.content
        assert result.latency_ms > 0

    @pytest.mark.asyncio
    @pytest.mark.manual_only
    async def test_json_mode_completion(self, provider: OpenAICompatibleProvider) -> None:
        """Provider can return structured JSON via prompt engineering.

        Note: LM Studio requires response_format.type = 'json_schema' (not
        'json_object'). For maximum portability, Glimmer relies on prompt
        engineering to elicit JSON output rather than provider-specific
        structured output modes. This test validates that approach.
        """
        result = await provider.chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a classification assistant. "
                        "You MUST respond with ONLY valid JSON, no other text. "
                        "Use this exact format: "
                        '{"category": "string", "confidence": 0.0}'
                    ),
                },
                {
                    "role": "user",
                    "content": "Classify this message: 'The Q3 launch deadline is next Friday'",
                },
            ],
            temperature=0.0,
            max_tokens=200,
        )

        logger.info("JSON response: %s", result.content)
        logger.info("Latency: %.0fms", result.latency_ms)

        assert result.content
        # Validate it's actually JSON — strip markdown fences if present
        content = result.content.strip()
        if content.startswith("```"):
            # Strip ```json ... ``` wrapper
            lines = content.split("\n")
            content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        parsed = json.loads(content)
        assert isinstance(parsed, dict)
        logger.info("Parsed JSON: %s", parsed)

    @pytest.mark.asyncio
    @pytest.mark.manual_only
    async def test_multi_turn_conversation(self, provider: OpenAICompatibleProvider) -> None:
        """Provider handles multi-turn conversation context."""
        result = await provider.chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Be brief."},
                {"role": "user", "content": "My name is Tony."},
                {"role": "assistant", "content": "Hello Tony! How can I help you?"},
                {"role": "user", "content": "What's my name?"},
            ],
            temperature=0.0,
            max_tokens=50,
        )

        logger.info("Response: %s", result.content)
        assert "Tony" in result.content


# ── Latency Profiling ────────────────────────────────────────────────


class TestLiveLatencyProfile:
    """Operational profiling — not a pass/fail test, but useful data."""

    @pytest.mark.asyncio
    @pytest.mark.manual_only
    async def test_classification_latency(self, provider: OpenAICompatibleProvider) -> None:
        """Measure typical classification prompt latency."""
        result = await provider.chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Glimmer, an AI project assistant. "
                        "Given a message and a list of active projects, "
                        "classify which project the message relates to. "
                        "You MUST respond with ONLY valid JSON, no other text. "
                        "Use this exact format: "
                        '{"project": "name", "confidence": 0.0, "rationale": "why"}'
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Active projects:\n"
                        "1. Alpha Launch — Q3 product launch for enterprise clients\n"
                        "2. Beta Migration — Database migration to PostgreSQL 17\n"
                        "3. Gamma Research — Market research for APAC expansion\n\n"
                        "Message from alice@corp.com:\n"
                        "Subject: Re: Migration timeline update\n"
                        "Body: The PostgreSQL 17 upgrade is on track. "
                        "We've completed the schema validation and the test suite passes. "
                        "Planning to do the production cutover next Thursday."
                    ),
                },
            ],
            temperature=0.0,
            max_tokens=300,
        )

        logger.info("Classification response: %s", result.content)
        logger.info(
            "Latency: %.0fms (%.1f seconds)", result.latency_ms, result.latency_ms / 1000
        )
        logger.info("Tokens: prompt=%s completion=%s",
                     result.prompt_tokens, result.completion_tokens)

        # Operational target: classification should complete in <30s
        assert result.latency_ms < 30_000, (
            f"Classification took {result.latency_ms/1000:.1f}s — exceeds 30s target"
        )

        # Validate JSON structure — strip markdown fences if present
        content = result.content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        parsed = json.loads(content)
        assert "project" in parsed or "Project" in parsed or "name" in parsed
        logger.info("Parsed classification: %s", parsed)

