"""Unit tests — LLM-powered classification task.

PLAN:WorkstreamI.PackageI3.LLMClassification
TEST:LLM.Classification.ProducesValidClassificationResult
TEST:LLM.Classification.ConfidenceAndRationalePresent
TEST:LLM.Classification.LowConfidenceTriggersReviewGate
TEST:LLM.Classification.FallsBackToDeterministicWhenUnavailable

Tests the classification task module with a mocked provider.
Live tests against real LM Studio are in tests/live/.
"""

from __future__ import annotations

import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.inference.base import InferenceError, InferenceResult
from app.inference.tasks.classification import (
    LLMClassificationResult,
    classify_project_llm,
    CONFIDENCE_REVIEW_THRESHOLD,
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


SAMPLE_PROJECTS = [
    {"id": str(uuid.uuid4()), "name": "Alpha Launch", "objective": "Q3 product launch"},
    {"id": str(uuid.uuid4()), "name": "Beta Migration", "objective": "PostgreSQL 17 migration"},
    {"id": str(uuid.uuid4()), "name": "Gamma Research", "objective": "APAC market research"},
]


# ── Classification Result Tests ──────────────────────────────────────


class TestClassifyProjectLLM:
    """TEST:LLM.Classification.ProducesValidClassificationResult"""

    @pytest.mark.asyncio
    async def test_high_confidence_classification(self) -> None:
        """High-confidence classification produces valid result without review."""
        response = json.dumps({
            "project_name": "Beta Migration",
            "project_id": SAMPLE_PROJECTS[1]["id"],
            "confidence": 0.95,
            "rationale": "Message explicitly mentions PostgreSQL 17 upgrade",
            "needs_review": False,
            "review_reason": None,
            "candidates": [
                {"project_id": SAMPLE_PROJECTS[1]["id"], "project_name": "Beta Migration", "score": 0.95, "reason": "Direct match"},
            ],
        })
        provider = _make_provider(response)

        result = await classify_project_llm(
            provider,
            projects=SAMPLE_PROJECTS,
            sender="alice@corp.com",
            subject="Migration update",
            body="PostgreSQL 17 upgrade is on track.",
        )

        assert isinstance(result, LLMClassificationResult)
        assert result.project_name == "Beta Migration"
        assert result.confidence == 0.95
        assert result.rationale == "Message explicitly mentions PostgreSQL 17 upgrade"
        assert result.needs_review is False
        assert result.used_llm is True
        assert result.inference_latency_ms == 100.0

    @pytest.mark.asyncio
    async def test_confidence_and_rationale_always_present(self) -> None:
        """TEST:LLM.Classification.ConfidenceAndRationalePresent"""
        response = json.dumps({
            "project_name": "Alpha Launch",
            "confidence": 0.7,
            "rationale": "Launch-related keywords found",
            "needs_review": False,
            "candidates": [],
        })
        provider = _make_provider(response)

        result = await classify_project_llm(
            provider,
            projects=SAMPLE_PROJECTS,
            sender="test@test.com",
            subject="Launch update",
            body="Launch timeline looks good.",
        )

        assert result.confidence == 0.7
        assert len(result.rationale) > 0

    @pytest.mark.asyncio
    async def test_low_confidence_forces_review(self) -> None:
        """TEST:LLM.Classification.LowConfidenceTriggersReviewGate"""
        response = json.dumps({
            "project_name": "Alpha Launch",
            "confidence": 0.3,
            "rationale": "Weak keyword match",
            "needs_review": False,  # Model says no review, but we override
            "candidates": [],
        })
        provider = _make_provider(response)

        result = await classify_project_llm(
            provider,
            projects=SAMPLE_PROJECTS,
            sender="test@test.com",
            subject="Hello",
            body="Generic message",
        )

        # Low confidence MUST trigger review regardless of model's opinion
        assert result.needs_review is True
        assert result.confidence < CONFIDENCE_REVIEW_THRESHOLD

    @pytest.mark.asyncio
    async def test_no_match_returns_null_project(self) -> None:
        """Classification returns null project when no match."""
        response = json.dumps({
            "project_name": None,
            "project_id": None,
            "confidence": 0.1,
            "rationale": "Message doesn't relate to any active project",
            "needs_review": True,
            "review_reason": "No project match found",
            "candidates": [],
        })
        provider = _make_provider(response)

        result = await classify_project_llm(
            provider,
            projects=SAMPLE_PROJECTS,
            sender="random@external.com",
            subject="Newsletter",
            body="Weekly tech digest",
        )

        assert result.project_id is None
        assert result.project_name is None
        assert result.needs_review is True

    @pytest.mark.asyncio
    async def test_handles_fenced_json_response(self) -> None:
        """Parser handles Gemma-style fenced JSON."""
        fenced_response = (
            '```json\n'
            '{"project_name": "Beta Migration", "confidence": 0.9, '
            '"rationale": "PostgreSQL mentioned", "needs_review": false, "candidates": []}\n'
            '```'
        )
        provider = _make_provider(fenced_response)

        result = await classify_project_llm(
            provider,
            projects=SAMPLE_PROJECTS,
            sender="test@test.com",
            subject="DB update",
            body="PostgreSQL migration complete.",
        )

        assert result.project_name == "Beta Migration"
        assert result.confidence == 0.9

    @pytest.mark.asyncio
    async def test_resolves_project_id_from_map(self) -> None:
        """Resolves project UUID when project_id_map is provided."""
        target_id = uuid.uuid4()
        response = json.dumps({
            "project_name": "Alpha Launch",
            "confidence": 0.8,
            "rationale": "Launch keywords match",
            "needs_review": False,
            "candidates": [],
        })
        provider = _make_provider(response)

        result = await classify_project_llm(
            provider,
            projects=SAMPLE_PROJECTS,
            sender="test@test.com",
            subject="Launch",
            body="Launch update",
            project_id_map={"Alpha Launch": target_id},
        )

        assert result.project_id == target_id

    @pytest.mark.asyncio
    async def test_resolves_project_id_from_response(self) -> None:
        """Uses project_id from LLM response when it's a valid UUID."""
        target_id = uuid.uuid4()
        response = json.dumps({
            "project_name": "Alpha Launch",
            "project_id": str(target_id),
            "confidence": 0.85,
            "rationale": "Direct match",
            "needs_review": False,
            "candidates": [],
        })
        provider = _make_provider(response)

        result = await classify_project_llm(
            provider,
            projects=SAMPLE_PROJECTS,
            sender="test@test.com",
            subject="Launch",
            body="Launch update",
        )

        assert result.project_id == target_id


class TestClassificationFallback:
    """TEST:LLM.Classification.FallsBackToDeterministicWhenUnavailable"""

    @pytest.mark.asyncio
    async def test_raises_inference_error_on_provider_failure(self) -> None:
        """Provider failure raises InferenceError for fallback handling."""
        provider = _make_failing_provider(
            InferenceError("Connection refused", is_unavailable=True)
        )

        with pytest.raises(InferenceError) as exc_info:
            await classify_project_llm(
                provider,
                projects=SAMPLE_PROJECTS,
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
            await classify_project_llm(
                provider,
                projects=SAMPLE_PROJECTS,
                sender="test@test.com",
                subject="Test",
                body="Test message",
            )

        assert exc_info.value.is_timeout is True

    @pytest.mark.asyncio
    async def test_raises_on_unparseable_response(self) -> None:
        """Unparseable LLM response raises InferenceError."""
        provider = _make_provider("This is not JSON at all, just rambling text.")

        with pytest.raises(InferenceError) as exc_info:
            await classify_project_llm(
                provider,
                projects=SAMPLE_PROJECTS,
                sender="test@test.com",
                subject="Test",
                body="Test message",
            )

        assert "parse" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_raises_on_missing_required_fields(self) -> None:
        """Response missing required fields raises InferenceError."""
        # Missing 'confidence' and 'rationale'
        provider = _make_provider(json.dumps({"project_name": "Alpha"}))

        with pytest.raises(InferenceError):
            await classify_project_llm(
                provider,
                projects=SAMPLE_PROJECTS,
                sender="test@test.com",
                subject="Test",
                body="Test",
            )


class TestClassificationPromptAssembly:
    """Verify the classification task assembles prompts correctly."""

    @pytest.mark.asyncio
    async def test_passes_projects_to_prompt(self) -> None:
        """Projects are included in the prompt sent to the provider."""
        response = json.dumps({
            "project_name": "Alpha Launch",
            "confidence": 0.7,
            "rationale": "Match",
            "needs_review": False,
            "candidates": [],
        })
        provider = _make_provider(response)

        await classify_project_llm(
            provider,
            projects=SAMPLE_PROJECTS,
            sender="test@test.com",
            subject="Launch",
            body="Test",
        )

        # Verify the provider was called with messages containing project info
        call_args = provider.chat_completion.call_args
        messages = call_args.args[0] if call_args.args else call_args.kwargs.get("messages", [])
        user_msg = messages[1]["content"]
        assert "Alpha Launch" in user_msg
        assert "Beta Migration" in user_msg

    @pytest.mark.asyncio
    async def test_uses_low_temperature(self) -> None:
        """Classification uses low temperature for consistency."""
        response = json.dumps({
            "project_name": None,
            "confidence": 0.0,
            "rationale": "No match",
            "needs_review": True,
            "candidates": [],
        })
        provider = _make_provider(response)

        await classify_project_llm(
            provider,
            projects=[],
            sender="test@test.com",
            subject="Test",
            body="Test",
        )

        call_kwargs = provider.chat_completion.call_args.kwargs
        assert call_kwargs.get("temperature", 1.0) <= 0.2

    @pytest.mark.asyncio
    async def test_records_latency(self) -> None:
        """Result includes inference latency."""
        response = json.dumps({
            "project_name": "Alpha",
            "confidence": 0.8,
            "rationale": "Match",
            "needs_review": False,
            "candidates": [],
        })
        provider = _make_provider(response, latency_ms=5432.1)

        result = await classify_project_llm(
            provider,
            projects=SAMPLE_PROJECTS,
            sender="test@test.com",
            subject="Test",
            body="Test",
        )

        assert result.inference_latency_ms == 5432.1

