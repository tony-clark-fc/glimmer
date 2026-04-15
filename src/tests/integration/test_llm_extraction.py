"""Unit tests — LLM-powered extraction task.

PLAN:WorkstreamI.PackageI4.LLMExtraction
TEST:LLM.Extraction.ProducesValidStructuredActions
TEST:LLM.Extraction.ConfidencePerExtractionPresent
TEST:LLM.Extraction.NoHallucinationFromEmptyContent
TEST:LLM.Extraction.FallsBackWhenUnavailable
TEST:LLM.Extraction.OutputCompatibleWithPersistenceLayer

Tests the extraction task module with a mocked provider.
Live tests against real LM Studio are in tests/live/.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from app.inference.base import InferenceError, InferenceResult
from app.inference.tasks.extraction import (
    LLMExtractionResult,
    extract_from_message_llm,
    _clamp_confidence,
    _normalize_actions,
    _normalize_decisions,
    _normalize_deadlines,
)


# ── Helpers ──────────────────────────────────────────────────────────


def _make_provider(response_content: str, latency_ms: float = 100.0):
    """Create a mock provider that returns the given content."""
    provider = AsyncMock()
    provider.chat_completion = AsyncMock(
        return_value=InferenceResult(
            content=response_content,
            model="test-model",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            latency_ms=latency_ms,
            finish_reason="stop",
        )
    )
    return provider


def _make_failing_provider(error: Exception):
    """Create a mock provider that raises an error."""
    provider = AsyncMock()
    provider.chat_completion = AsyncMock(side_effect=error)
    return provider


FULL_EXTRACTION_RESPONSE = {
    "actions": [
        {
            "description": "Schedule migration dry-run for Friday",
            "proposed_owner": "Alice",
            "due_date_signal": "Friday",
            "urgency_signal": "high",
            "confidence": 0.9,
        },
        {
            "description": "Update runbook with rollback steps",
            "proposed_owner": None,
            "due_date_signal": None,
            "urgency_signal": "medium",
            "confidence": 0.75,
        },
    ],
    "decisions": [
        {
            "description": "Team agreed to use PostgreSQL 17 for production",
            "rationale": "Better performance and JSON support",
            "confidence": 0.95,
        },
    ],
    "deadlines": [
        {
            "description": "Migration must complete before Q3 freeze",
            "inferred_date": "2026-06-30",
            "confidence": 0.8,
        },
    ],
}


# ── Extraction Result Tests ──────────────────────────────────────────


class TestExtractFromMessageLLM:
    """TEST:LLM.Extraction.ProducesValidStructuredActions"""

    @pytest.mark.asyncio
    async def test_full_extraction_produces_valid_result(self) -> None:
        """Full extraction with actions, decisions, and deadlines."""
        provider = _make_provider(json.dumps(FULL_EXTRACTION_RESPONSE))

        result = await extract_from_message_llm(
            provider,
            sender="alice@corp.com",
            subject="Migration update",
            body="Let's schedule the dry-run for Friday. We agreed on PG17. Needs to be done before Q3 freeze.",
        )

        assert isinstance(result, LLMExtractionResult)
        assert len(result.actions) == 2
        assert len(result.decisions) == 1
        assert len(result.deadlines) == 1
        assert result.total_items == 4
        assert result.is_empty is False
        assert result.used_llm is True

    @pytest.mark.asyncio
    async def test_confidence_per_extraction_present(self) -> None:
        """TEST:LLM.Extraction.ConfidencePerExtractionPresent — each item has confidence."""
        provider = _make_provider(json.dumps(FULL_EXTRACTION_RESPONSE))

        result = await extract_from_message_llm(
            provider,
            sender="alice@corp.com",
            subject="Update",
            body="Some update.",
        )

        for action in result.actions:
            assert "confidence" in action
            assert 0.0 <= action["confidence"] <= 1.0
        for decision in result.decisions:
            assert "confidence" in decision
            assert 0.0 <= decision["confidence"] <= 1.0
        for deadline in result.deadlines:
            assert "confidence" in deadline
            assert 0.0 <= deadline["confidence"] <= 1.0

    @pytest.mark.asyncio
    async def test_empty_message_returns_empty_extraction(self) -> None:
        """TEST:LLM.Extraction.NoHallucinationFromEmptyContent — no hallucinated items."""
        response = json.dumps({"actions": [], "decisions": [], "deadlines": []})
        provider = _make_provider(response)

        result = await extract_from_message_llm(
            provider,
            sender="nobody@test.com",
            subject="",
            body=None,
        )

        assert result.is_empty is True
        assert result.total_items == 0
        assert result.actions == []
        assert result.decisions == []
        assert result.deadlines == []
        assert result.used_llm is True

    @pytest.mark.asyncio
    async def test_handles_fenced_json_response(self) -> None:
        """Parser handles Gemma-style fenced JSON wrapping."""
        fenced_response = (
            "```json\n"
            + json.dumps(FULL_EXTRACTION_RESPONSE)
            + "\n```"
        )
        provider = _make_provider(fenced_response)

        result = await extract_from_message_llm(
            provider,
            sender="test@test.com",
            subject="Test",
            body="Some message with actions.",
        )

        assert result.total_items == 4
        assert result.used_llm is True

    @pytest.mark.asyncio
    async def test_partial_extraction_only_actions(self) -> None:
        """Extraction can return items in only some categories."""
        response = json.dumps({
            "actions": [
                {"description": "Send report", "proposed_owner": "Bob", "confidence": 0.8},
            ],
            "decisions": [],
            "deadlines": [],
        })
        provider = _make_provider(response)

        result = await extract_from_message_llm(
            provider,
            sender="test@test.com",
            subject="Report needed",
            body="Please send the report.",
        )

        assert len(result.actions) == 1
        assert len(result.decisions) == 0
        assert len(result.deadlines) == 0
        assert result.total_items == 1

    @pytest.mark.asyncio
    async def test_project_context_included_in_prompt(self) -> None:
        """Project context is passed to the prompt when provided."""
        response = json.dumps({"actions": [], "decisions": [], "deadlines": []})
        provider = _make_provider(response)

        await extract_from_message_llm(
            provider,
            sender="test@test.com",
            subject="Update",
            body="Test message",
            project_name="Beta Migration",
            project_objective="PostgreSQL 17 migration",
        )

        call_args = provider.chat_completion.call_args
        messages = call_args.args[0] if call_args.args else call_args.kwargs.get("messages", [])
        user_msg = messages[1]["content"]
        assert "Beta Migration" in user_msg
        assert "PostgreSQL 17 migration" in user_msg

    @pytest.mark.asyncio
    async def test_records_latency(self) -> None:
        """Result includes inference latency from the provider."""
        response = json.dumps({"actions": [], "decisions": [], "deadlines": []})
        provider = _make_provider(response, latency_ms=2345.6)

        result = await extract_from_message_llm(
            provider,
            sender="test@test.com",
            subject="Test",
            body="Test",
        )

        assert result.inference_latency_ms == 2345.6

    @pytest.mark.asyncio
    async def test_raw_llm_response_captured(self) -> None:
        """Result captures the raw LLM response text."""
        raw = json.dumps({"actions": [], "decisions": [], "deadlines": []})
        provider = _make_provider(raw)

        result = await extract_from_message_llm(
            provider,
            sender="test@test.com",
            subject="Test",
            body="Test",
        )

        assert result.raw_llm_response == raw


class TestExtractionFallback:
    """TEST:LLM.Extraction.FallsBackWhenUnavailable"""

    @pytest.mark.asyncio
    async def test_raises_inference_error_on_provider_failure(self) -> None:
        """Provider failure raises InferenceError for fallback handling."""
        provider = _make_failing_provider(
            InferenceError("Connection refused", is_unavailable=True)
        )

        with pytest.raises(InferenceError) as exc_info:
            await extract_from_message_llm(
                provider,
                sender="test@test.com",
                subject="Test",
                body="Test message",
            )

        assert exc_info.value.is_unavailable is True

    @pytest.mark.asyncio
    async def test_raises_inference_error_on_timeout(self) -> None:
        """Timeout raises InferenceError with is_timeout flag."""
        provider = _make_failing_provider(
            InferenceError("Timeout", is_timeout=True)
        )

        with pytest.raises(InferenceError) as exc_info:
            await extract_from_message_llm(
                provider,
                sender="test@test.com",
                subject="Test",
                body="Test message",
            )

        assert exc_info.value.is_timeout is True

    @pytest.mark.asyncio
    async def test_raises_on_unparseable_response(self) -> None:
        """Unparseable LLM response raises InferenceError."""
        provider = _make_provider("This is not valid JSON output at all.")

        with pytest.raises(InferenceError) as exc_info:
            await extract_from_message_llm(
                provider,
                sender="test@test.com",
                subject="Test",
                body="Test message",
            )

        assert "parse" in str(exc_info.value).lower()


class TestExtractionNormalization:
    """Tests for normalization helpers ensuring persistence compatibility.

    TEST:LLM.Extraction.OutputCompatibleWithPersistenceLayer
    """

    def test_actions_filter_empty_descriptions(self) -> None:
        """Actions with empty descriptions are filtered out."""
        raw = [
            {"description": "Valid action", "confidence": 0.8},
            {"description": "", "confidence": 0.5},
            {"description": "   ", "confidence": 0.6},
        ]
        result = _normalize_actions(raw)
        assert len(result) == 1
        assert result[0]["description"] == "Valid action"

    def test_actions_filter_non_dict_items(self) -> None:
        """Non-dict items in the array are filtered out."""
        raw = [
            {"description": "Valid", "confidence": 0.8},
            "just a string",
            42,
            None,
        ]
        result = _normalize_actions(raw)
        assert len(result) == 1

    def test_decisions_normalize_correctly(self) -> None:
        """Decisions retain description, rationale, and clamped confidence."""
        raw = [
            {"description": "Chose PG17", "rationale": "Better perf", "confidence": 0.9},
        ]
        result = _normalize_decisions(raw)
        assert len(result) == 1
        assert result[0]["description"] == "Chose PG17"
        assert result[0]["rationale"] == "Better perf"
        assert result[0]["confidence"] == 0.9

    def test_deadlines_normalize_correctly(self) -> None:
        """Deadlines retain description, inferred_date, and clamped confidence."""
        raw = [
            {"description": "Q3 freeze", "inferred_date": "2026-06-30", "confidence": 0.85},
        ]
        result = _normalize_deadlines(raw)
        assert len(result) == 1
        assert result[0]["description"] == "Q3 freeze"
        assert result[0]["inferred_date"] == "2026-06-30"
        assert result[0]["confidence"] == 0.85

    def test_confidence_clamping(self) -> None:
        """Confidence values are clamped to [0.0, 1.0]."""
        assert _clamp_confidence(1.5) == 1.0
        assert _clamp_confidence(-0.3) == 0.0
        assert _clamp_confidence(0.7) == 0.7
        assert _clamp_confidence("not a number") == 0.5
        assert _clamp_confidence(None) == 0.5

