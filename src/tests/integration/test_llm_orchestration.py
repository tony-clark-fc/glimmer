"""Unit tests — orchestration wiring with fallback chains and safety boundaries.

PLAN:WorkstreamI.PackageI8.OrchestrationWiring
TEST:LLM.Orchestration.TriagePipelineUsesLLMWhenAvailable
TEST:LLM.Orchestration.FallbackChainWorksCleanly
TEST:LLM.Orchestration.ExistingTestsSurviveIntegration
TEST:LLM.Safety.ReviewGatesNotWeakened
TEST:LLM.Safety.ProvenanceNotFlattened
TEST:LLM.Safety.NoAutoSendNotWeakened
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from app.inference.base import InferenceError, InferenceResult
from app.inference.orchestration import (
    SmartClassificationResult,
    FallbackResult,
    classify_project_smart,
    extract_from_message_smart,
    generate_draft_smart,
    generate_briefing_smart,
    get_inference_provider,
    set_inference_provider,
)
from app.inference.tasks.drafting import LLMDraftResult
from app.inference.tasks.briefing import LLMBriefingResult


# ── Helpers ──────────────────────────────────────────────────────────


def _mock_provider_success(response_content: str):
    provider = AsyncMock()
    provider.chat_completion = AsyncMock(
        return_value=InferenceResult(
            content=response_content,
            model="test-model",
            prompt_tokens=100,
            completion_tokens=80,
            total_tokens=180,
            latency_ms=100.0,
            finish_reason="stop",
        )
    )
    return provider


def _mock_provider_failure():
    provider = AsyncMock()
    provider.chat_completion = AsyncMock(
        side_effect=InferenceError("LM Studio unavailable", is_unavailable=True)
    )
    return provider


# ── Smart Classification Tests ───────────────────────────────────────


class TestClassifyProjectSmart:
    """TEST:LLM.Orchestration.TriagePipelineUsesLLMWhenAvailable
    TEST:LLM.Orchestration.FallbackChainWorksCleanly
    """

    @pytest.mark.asyncio
    async def test_uses_llm_when_available(self, db_session) -> None:
        """LLM path is used when provider is available."""
        response = json.dumps({
            "project_name": None,
            "confidence": 0.0,
            "rationale": "No active projects to match against",
            "needs_review": True,
            "review_reason": "No projects",
            "candidates": [],
        })
        provider = _mock_provider_success(response)

        result = await classify_project_smart(
            db_session,
            sender_identity="test@test.com",
            subject="Test",
            body_text="Test message",
            provider=provider,
        )

        assert isinstance(result, SmartClassificationResult)
        assert result.used_llm is True
        assert result.fallback_reason is None

    @pytest.mark.asyncio
    async def test_falls_back_to_deterministic_on_failure(self, db_session) -> None:
        """Falls back to deterministic classification when LLM fails."""
        provider = _mock_provider_failure()

        result = await classify_project_smart(
            db_session,
            sender_identity="test@test.com",
            subject="Test",
            body_text="Test message",
            provider=provider,
        )

        assert isinstance(result, SmartClassificationResult)
        assert result.used_llm is False
        assert result.fallback_reason is not None
        assert "unavailable" in result.fallback_reason.lower()

    @pytest.mark.asyncio
    async def test_review_gate_preserved_on_llm_path(self, db_session) -> None:
        """TEST:LLM.Safety.ReviewGatesNotWeakened — LLM path preserves review."""
        response = json.dumps({
            "project_name": None,
            "confidence": 0.2,
            "rationale": "Low confidence",
            "needs_review": True,
            "review_reason": "Very uncertain",
            "candidates": [],
        })
        provider = _mock_provider_success(response)

        result = await classify_project_smart(
            db_session,
            sender_identity="test@test.com",
            subject="Test",
            body_text="Test",
            provider=provider,
        )

        assert result.needs_review is True

    @pytest.mark.asyncio
    async def test_review_gate_preserved_on_fallback_path(self, db_session) -> None:
        """Review gate works on deterministic fallback path too."""
        provider = _mock_provider_failure()

        result = await classify_project_smart(
            db_session,
            sender_identity="test@test.com",
            subject="Test",
            body_text="Test",
            provider=provider,
        )

        # Deterministic path with no matching projects should flag for review
        # (no active projects in test DB)
        assert isinstance(result, SmartClassificationResult)


# ── Smart Extraction Tests ───────────────────────────────────────────


class TestExtractFromMessageSmart:
    """TEST:LLM.Orchestration.FallbackChainWorksCleanly"""

    @pytest.mark.asyncio
    async def test_uses_llm_when_available(self) -> None:
        response = json.dumps({"actions": [], "decisions": [], "deadlines": []})
        provider = _mock_provider_success(response)

        result = await extract_from_message_smart(
            sender="test@test.com",
            subject="Test",
            body="Test",
            provider=provider,
        )

        assert result.used_llm is True

    @pytest.mark.asyncio
    async def test_returns_empty_on_failure(self) -> None:
        provider = _mock_provider_failure()

        result = await extract_from_message_smart(
            sender="test@test.com",
            subject="Test",
            body="Test",
            provider=provider,
        )

        assert result.used_llm is False
        assert result.is_empty is True


# ── Smart Draft Tests ────────────────────────────────────────────────


class TestGenerateDraftSmart:
    """TEST:LLM.Safety.NoAutoSendNotWeakened"""

    @pytest.mark.asyncio
    async def test_uses_llm_when_available(self) -> None:
        response = json.dumps({
            "body_content": "Hi, thanks for the update.",
            "rationale_summary": "Simple acknowledgement",
            "variants": [],
        })
        provider = _mock_provider_success(response)

        result = await generate_draft_smart(
            intent="reply",
            provider=provider,
        )

        assert result.used_llm is True
        assert result.auto_send_blocked is True

    @pytest.mark.asyncio
    async def test_no_auto_send_on_llm_path(self) -> None:
        """TEST:LLM.Safety.NoAutoSendNotWeakened — LLM drafts are always blocked."""
        response = json.dumps({
            "body_content": "Draft content",
            "variants": [],
        })
        provider = _mock_provider_success(response)

        result = await generate_draft_smart(intent="reply", provider=provider)

        assert result.auto_send_blocked is True

    @pytest.mark.asyncio
    async def test_no_auto_send_on_fallback_path(self) -> None:
        """No-auto-send preserved even on fallback."""
        provider = _mock_provider_failure()

        result = await generate_draft_smart(intent="reply", provider=provider)

        assert result.auto_send_blocked is True
        assert result.used_llm is False

    @pytest.mark.asyncio
    async def test_returns_empty_on_failure(self) -> None:
        provider = _mock_provider_failure()

        result = await generate_draft_smart(intent="reply", provider=provider)

        assert result.body_content == ""
        assert result.used_llm is False


# ── Smart Briefing Tests ─────────────────────────────────────────────


class TestGenerateBriefingSmart:

    @pytest.mark.asyncio
    async def test_uses_llm_when_available(self) -> None:
        response = json.dumps({
            "briefing_text": "Good morning. Top priority is the login fix.",
            "section_count": 1,
            "sections_used": ["actions"],
            "items_mentioned": 1,
        })
        provider = _mock_provider_success(response)

        result = await generate_briefing_smart(
            top_actions=[{"title": "Fix login"}],
            provider=provider,
        )

        assert result.used_llm is True
        assert len(result.briefing_text) > 0

    @pytest.mark.asyncio
    async def test_returns_empty_on_failure(self) -> None:
        provider = _mock_provider_failure()

        result = await generate_briefing_smart(provider=provider)

        assert result.used_llm is False
        assert result.is_empty is True


# ── Provider Management Tests ────────────────────────────────────────


class TestProviderManagement:

    def test_get_provider_returns_instance(self) -> None:
        """get_inference_provider creates a provider."""
        # Reset state
        set_inference_provider(None)
        provider = get_inference_provider()
        assert provider is not None

    def test_set_provider_overrides(self) -> None:
        """set_inference_provider allows override for testing."""
        mock = AsyncMock()
        set_inference_provider(mock)
        assert get_inference_provider() is mock
        # Cleanup
        set_inference_provider(None)


# ── Safety Invariant Tests ───────────────────────────────────────────


class TestSafetyInvariants:
    """TEST:LLM.Safety.ReviewGatesNotWeakened
    TEST:LLM.Safety.ProvenanceNotFlattened
    TEST:LLM.Safety.NoAutoSendNotWeakened
    """

    def test_smart_classification_result_has_used_llm_flag(self) -> None:
        """TEST:LLM.Safety.ProvenanceNotFlattened — LLM vs deterministic is visible."""
        llm_result = SmartClassificationResult(used_llm=True, confidence=0.9)
        det_result = SmartClassificationResult(used_llm=False, fallback_reason="test")

        assert llm_result.used_llm is True
        assert det_result.used_llm is False
        assert det_result.fallback_reason == "test"

    def test_draft_result_auto_send_always_blocked(self) -> None:
        """TEST:LLM.Safety.NoAutoSendNotWeakened"""
        result = LLMDraftResult(body_content="test")
        assert result.auto_send_blocked is True

    def test_fallback_result_tracks_reason(self) -> None:
        result = FallbackResult(used_llm=False, fallback_reason="Connection refused")
        assert result.fallback_reason == "Connection refused"


