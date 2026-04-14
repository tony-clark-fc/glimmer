"""Unit tests — LLM-powered extraction task.

PLAN:WorkstreamI.PackageI4.LLMExtraction
TEST:LLM.Extraction.ProducesValidStructuredActions
TEST:LLM.Extraction.ConfidencePerExtractionPresent
TEST:LLM.Extraction.NoHallucinationFromEmptyContent
TEST:LLM.Extraction.FallsBackWhenUnavailable
TEST:LLM.Extraction.OutputCompatibleWithPersistenceLayer
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from app.inference.base import InferenceError, InferenceResult
from app.inference.tasks.extraction import (
    LLMExtractionResult,
    extract_from_message_llm,
    _normalize_actions,
    _normalize_decisions,
    _normalize_deadlines,
    _clamp_confidence,
)


def _make_provider(response_content: str, latency_ms: float = 100.0):
    provider = AsyncMock()
    provider.chat_completion = AsyncMock(
        return_value=InferenceResult(
            content=response_content,
            model="test-model",
            prompt_tokens=100,
            completion_tokens=80,
            total_tokens=180,
            latency_ms=latency_ms,
            finish_reason="stop",
        )
    )
    return provider


FULL_EXTRACTION_RESPONSE = json.dumps({
    "actions": [
        {
            "description": "Complete the production cutover",
            "proposed_owner": "Alice",
            "due_date_signal": "next Thursday",
            "urgency_signal": "high",
            "confidence": 0.9,
        },
        {
            "description": "Run final regression test suite",
            "proposed_owner": None,
            "due_date_signal": "before cutover",
            "urgency_signal": "medium",
            "confidence": 0.7,
        },
    ],
    "decisions": [
        {
            "description": "Schema validation approach approved",
            "rationale": "Test suite passes, validation complete",
            "confidence": 0.85,
        },
    ],
    "deadlines": [
        {
            "description": "Production cutover",
            "inferred_date": "2026-04-23",
            "confidence": 0.8,
        },
    ],
})


class TestExtractFromMessageLLM:
    """TEST:LLM.Extraction.ProducesValidStructuredActions"""

    @pytest.mark.asyncio
    async def test_full_extraction(self) -> None:
        """Extracts actions, decisions, and deadlines from a rich message."""
        provider = _make_provider(FULL_EXTRACTION_RESPONSE)

        result = await extract_from_message_llm(
            provider,
            sender="alice@corp.com",
            subject="Migration update",
            body="PostgreSQL 17 upgrade is on track. Production cutover next Thursday.",
            project_name="Beta Migration",
        )

        assert isinstance(result, LLMExtractionResult)
        assert result.used_llm is True
        assert len(result.actions) == 2
        assert len(result.decisions) == 1
        assert len(result.deadlines) == 1
        assert result.total_items == 4
        assert result.is_empty is False

    @pytest.mark.asyncio
    async def test_confidence_per_extraction(self) -> None:
        """TEST:LLM.Extraction.ConfidencePerExtractionPresent"""
        provider = _make_provider(FULL_EXTRACTION_RESPONSE)

        result = await extract_from_message_llm(
            provider,
            sender="test@test.com",
            subject="Test",
            body="Test body",
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
    async def test_empty_extraction(self) -> None:
        """TEST:LLM.Extraction.NoHallucinationFromEmptyContent"""
        response = json.dumps({"actions": [], "decisions": [], "deadlines": []})
        provider = _make_provider(response)

        result = await extract_from_message_llm(
            provider,
            sender="test@test.com",
            subject="Hey",
            body="Just checking in. Nothing specific to discuss.",
        )

        assert result.is_empty is True
        assert result.total_items == 0
        assert result.used_llm is True

    @pytest.mark.asyncio
    async def test_handles_fenced_json(self) -> None:
        fenced = f"```json\n{FULL_EXTRACTION_RESPONSE}\n```"
        provider = _make_provider(fenced)

        result = await extract_from_message_llm(
            provider,
            sender="test@test.com",
            subject="Test",
            body="Test",
        )

        assert result.total_items == 4

    @pytest.mark.asyncio
    async def test_records_latency(self) -> None:
        provider = _make_provider(
            json.dumps({"actions": [], "decisions": [], "deadlines": []}),
            latency_ms=12345.6,
        )

        result = await extract_from_message_llm(
            provider, sender="test@test.com", subject="Test", body="Test",
        )

        assert result.inference_latency_ms == 12345.6

    @pytest.mark.asyncio
    async def test_includes_project_context_in_prompt(self) -> None:
        provider = _make_provider(
            json.dumps({"actions": [], "decisions": [], "deadlines": []})
        )

        await extract_from_message_llm(
            provider,
            sender="test@test.com",
            subject="Test",
            body="Test",
            project_name="Alpha Launch",
            project_objective="Q3 product launch",
        )

        call_args = provider.chat_completion.call_args
        messages = call_args.args[0] if call_args.args else call_args.kwargs.get("messages", [])
        user_msg = messages[1]["content"]
        assert "Alpha Launch" in user_msg


class TestExtractionFallback:
    """TEST:LLM.Extraction.FallsBackWhenUnavailable"""

    @pytest.mark.asyncio
    async def test_raises_on_provider_failure(self) -> None:
        provider = AsyncMock()
        provider.chat_completion = AsyncMock(
            side_effect=InferenceError("Connection refused", is_unavailable=True)
        )

        with pytest.raises(InferenceError) as exc_info:
            await extract_from_message_llm(
                provider, sender="test@test.com", subject="Test", body="Test",
            )
        assert exc_info.value.is_unavailable is True

    @pytest.mark.asyncio
    async def test_raises_on_unparseable_response(self) -> None:
        provider = _make_provider("This is not JSON")

        with pytest.raises(InferenceError):
            await extract_from_message_llm(
                provider, sender="test@test.com", subject="Test", body="Test",
            )

    @pytest.mark.asyncio
    async def test_raises_on_missing_required_fields(self) -> None:
        provider = _make_provider(json.dumps({"actions": []}))

        with pytest.raises(InferenceError):
            await extract_from_message_llm(
                provider, sender="test@test.com", subject="Test", body="Test",
            )


class TestExtractionOutputCompatibility:
    """TEST:LLM.Extraction.OutputCompatibleWithPersistenceLayer"""

    @pytest.mark.asyncio
    async def test_actions_have_persistence_fields(self) -> None:
        """Action dicts are compatible with extract_and_persist()."""
        provider = _make_provider(FULL_EXTRACTION_RESPONSE)

        result = await extract_from_message_llm(
            provider, sender="test@test.com", subject="Test", body="Test",
        )

        for action in result.actions:
            assert "description" in action
            assert "proposed_owner" in action
            assert "due_date_signal" in action
            assert "urgency_signal" in action
            assert "confidence" in action

    @pytest.mark.asyncio
    async def test_decisions_have_persistence_fields(self) -> None:
        provider = _make_provider(FULL_EXTRACTION_RESPONSE)

        result = await extract_from_message_llm(
            provider, sender="test@test.com", subject="Test", body="Test",
        )

        for decision in result.decisions:
            assert "description" in decision
            assert "rationale" in decision
            assert "confidence" in decision

    @pytest.mark.asyncio
    async def test_deadlines_have_persistence_fields(self) -> None:
        provider = _make_provider(FULL_EXTRACTION_RESPONSE)

        result = await extract_from_message_llm(
            provider, sender="test@test.com", subject="Test", body="Test",
        )

        for deadline in result.deadlines:
            assert "description" in deadline
            assert "inferred_date" in deadline
            assert "confidence" in deadline


class TestNormalizationHelpers:
    """Normalization edge cases."""

    def test_skips_empty_description(self) -> None:
        raw = [{"description": "", "confidence": 0.9}]
        assert _normalize_actions(raw) == []

    def test_skips_non_dict_items(self) -> None:
        assert _normalize_actions(["not a dict"]) == []
        assert _normalize_decisions([42]) == []
        assert _normalize_deadlines([None]) == []

    def test_clamp_confidence_bounds(self) -> None:
        assert _clamp_confidence(1.5) == 1.0
        assert _clamp_confidence(-0.3) == 0.0
        assert _clamp_confidence(0.7) == 0.7

    def test_clamp_confidence_invalid(self) -> None:
        assert _clamp_confidence("not a number") == 0.5
        assert _clamp_confidence(None) == 0.5

    def test_strips_whitespace_from_description(self) -> None:
        raw = [{"description": "  do something  ", "confidence": 0.8}]
        result = _normalize_actions(raw)
        assert result[0]["description"] == "do something"

