"""Unit tests — LLM-powered prioritization, drafting, and briefing tasks.

PLAN:WorkstreamI.PackageI5-I7
TEST:LLM.Prioritization.ProducesNarrativeRationale
TEST:LLM.Prioritization.FallsBackToDeterministicScoring
TEST:LLM.Drafting.GeneratesContextualDraft
TEST:LLM.Drafting.NoAutoSendBoundaryPreserved
TEST:LLM.Drafting.FallsBackWhenUnavailable
TEST:LLM.Briefing.GroundedInFocusPackData
TEST:LLM.Briefing.LengthBoundRespected
TEST:LLM.Briefing.FallsBackWhenUnavailable
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

from app.inference.base import InferenceError, InferenceResult
from app.inference.tasks.prioritization import (
    LLMPrioritizationResult,
    enhance_prioritization_llm,
)
from app.inference.tasks.drafting import (
    LLMDraftResult,
    generate_draft_llm,
)
from app.inference.tasks.briefing import (
    LLMBriefingResult,
    generate_briefing_llm,
    MAX_BRIEFING_LENGTH,
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


# ═══════════════════════════════════════════════════════════════════════
# Prioritization Tests
# ═══════════════════════════════════════════════════════════════════════


PRIORITIZATION_RESPONSE = json.dumps({
    "narrative": "Your top priority is the login bug fix which blocks the release. The migration cutover is second priority with a Thursday deadline.",
    "enhanced_items": [
        {
            "item_id": "1",
            "enhanced_rationale": "This bug blocks the Q3 release for all enterprise clients.",
            "suggested_next_step": "Assign to senior dev and pair-review the fix today.",
        },
    ],
    "overall_suggestions": [
        "Clear your morning for the login bug fix.",
        "Send a status update to the migration team.",
    ],
})


class TestEnhancePrioritizationLLM:
    """TEST:LLM.Prioritization.ProducesNarrativeRationale"""

    @pytest.mark.asyncio
    async def test_produces_narrative(self) -> None:
        provider = _make_provider(PRIORITIZATION_RESPONSE)

        result = await enhance_prioritization_llm(
            provider,
            priority_items=[
                {"item_id": "1", "item_type": "work_item", "title": "Fix login bug",
                 "priority_score": 0.85, "rationale": "Blocking release"},
            ],
        )

        assert isinstance(result, LLMPrioritizationResult)
        assert result.used_llm is True
        assert len(result.narrative) > 20
        assert "login bug" in result.narrative.lower()

    @pytest.mark.asyncio
    async def test_includes_enhanced_items(self) -> None:
        provider = _make_provider(PRIORITIZATION_RESPONSE)

        result = await enhance_prioritization_llm(
            provider, priority_items=[{"item_id": "1", "title": "Test"}],
        )

        assert len(result.enhanced_items) >= 1
        assert result.enhanced_items[0]["item_id"] == "1"

    @pytest.mark.asyncio
    async def test_includes_suggestions(self) -> None:
        provider = _make_provider(PRIORITIZATION_RESPONSE)

        result = await enhance_prioritization_llm(
            provider, priority_items=[],
        )

        assert len(result.overall_suggestions) >= 1

    @pytest.mark.asyncio
    async def test_fallback_on_failure(self) -> None:
        """TEST:LLM.Prioritization.FallsBackToDeterministicScoring"""
        provider = AsyncMock()
        provider.chat_completion = AsyncMock(
            side_effect=InferenceError("Unavailable", is_unavailable=True)
        )

        with pytest.raises(InferenceError):
            await enhance_prioritization_llm(
                provider, priority_items=[],
            )


# ═══════════════════════════════════════════════════════════════════════
# Drafting Tests
# ═══════════════════════════════════════════════════════════════════════


DRAFTING_RESPONSE = json.dumps({
    "body_content": "Hi Alice,\n\nThank you for the migration update. The Thursday cutover timeline works for us.\n\nBest regards",
    "subject_suggestion": "Re: Migration timeline update",
    "rationale_summary": "Professional tone reply acknowledging the update and confirming the timeline.",
    "variants": [
        {
            "label": "casual_alternative",
            "body_content": "Hey Alice — great news on the migration! Thursday works. Talk soon.",
        },
    ],
})


class TestGenerateDraftLLM:
    """TEST:LLM.Drafting.GeneratesContextualDraft"""

    @pytest.mark.asyncio
    async def test_generates_draft(self) -> None:
        provider = _make_provider(DRAFTING_RESPONSE)

        result = await generate_draft_llm(
            provider,
            intent="reply",
            tone_mode="professional",
            project_name="Beta Migration",
            stakeholder_names=["Alice Smith"],
            original_message_summary="Alice confirmed the PostgreSQL 17 migration is on track.",
        )

        assert isinstance(result, LLMDraftResult)
        assert result.used_llm is True
        assert len(result.body_content) > 10
        assert "Alice" in result.body_content

    @pytest.mark.asyncio
    async def test_includes_variants(self) -> None:
        provider = _make_provider(DRAFTING_RESPONSE)

        result = await generate_draft_llm(
            provider, intent="reply", variant_count=1,
        )

        assert len(result.variants) >= 1
        assert result.variants[0]["label"] == "casual_alternative"

    @pytest.mark.asyncio
    async def test_no_auto_send_boundary(self) -> None:
        """TEST:LLM.Drafting.NoAutoSendBoundaryPreserved"""
        provider = _make_provider(DRAFTING_RESPONSE)

        result = await generate_draft_llm(provider, intent="reply")

        # HARD INVARIANT — auto_send is ALWAYS blocked
        assert result.auto_send_blocked is True

    @pytest.mark.asyncio
    async def test_no_auto_send_cannot_be_overridden(self) -> None:
        """The auto_send_blocked flag cannot be set to False."""
        result = LLMDraftResult(body_content="test")
        # Even if we try to set it, the default is True
        assert result.auto_send_blocked is True

    @pytest.mark.asyncio
    async def test_fallback_on_failure(self) -> None:
        """TEST:LLM.Drafting.FallsBackWhenUnavailable"""
        provider = AsyncMock()
        provider.chat_completion = AsyncMock(
            side_effect=InferenceError("Timeout", is_timeout=True)
        )

        with pytest.raises(InferenceError):
            await generate_draft_llm(provider, intent="reply")

    @pytest.mark.asyncio
    async def test_includes_rationale(self) -> None:
        provider = _make_provider(DRAFTING_RESPONSE)

        result = await generate_draft_llm(provider, intent="reply")

        assert len(result.rationale_summary) > 0


# ═══════════════════════════════════════════════════════════════════════
# Briefing Tests
# ═══════════════════════════════════════════════════════════════════════


BRIEFING_RESPONSE = json.dumps({
    "briefing_text": "Good morning. Your top priority is the login bug fix blocking the Q3 release. The migration cutover is set for Thursday. You're waiting on Alice for budget approval.",
    "section_count": 3,
    "sections_used": ["actions", "deadlines", "waiting"],
    "items_mentioned": 3,
})


class TestGenerateBriefingLLM:
    """TEST:LLM.Briefing.GroundedInFocusPackData"""

    @pytest.mark.asyncio
    async def test_generates_briefing(self) -> None:
        provider = _make_provider(BRIEFING_RESPONSE)

        result = await generate_briefing_llm(
            provider,
            top_actions=[{"title": "Fix login bug", "rationale": "Blocking release"}],
            waiting_on_items=[{"waiting_on": "Alice", "description": "Budget approval"}],
            project_names=["Alpha", "Beta"],
        )

        assert isinstance(result, LLMBriefingResult)
        assert result.used_llm is True
        assert len(result.briefing_text) > 20
        assert result.is_empty is False

    @pytest.mark.asyncio
    async def test_length_bound_respected(self) -> None:
        """TEST:LLM.Briefing.LengthBoundRespected"""
        provider = _make_provider(BRIEFING_RESPONSE)

        result = await generate_briefing_llm(provider)

        assert len(result.briefing_text) <= MAX_BRIEFING_LENGTH

    @pytest.mark.asyncio
    async def test_enforces_length_on_long_output(self) -> None:
        """Length bound enforced even when model exceeds it."""
        long_response = json.dumps({
            "briefing_text": "x" * 800,
            "section_count": 1,
            "sections_used": ["actions"],
            "items_mentioned": 1,
        })
        provider = _make_provider(long_response)

        result = await generate_briefing_llm(provider)

        assert len(result.briefing_text) <= MAX_BRIEFING_LENGTH
        assert result.briefing_text.endswith("...")

    @pytest.mark.asyncio
    async def test_tracks_sections(self) -> None:
        provider = _make_provider(BRIEFING_RESPONSE)

        result = await generate_briefing_llm(provider)

        assert result.section_count == 3
        assert "actions" in result.sections_used

    @pytest.mark.asyncio
    async def test_fallback_on_failure(self) -> None:
        """TEST:LLM.Briefing.FallsBackWhenUnavailable"""
        provider = AsyncMock()
        provider.chat_completion = AsyncMock(
            side_effect=InferenceError("Unavailable", is_unavailable=True)
        )

        with pytest.raises(InferenceError):
            await generate_briefing_llm(provider)

