"""Live integration tests — LLM classification against real LM Studio.

TEST:LLM.Classification.ProducesValidClassificationResult
TEST:LLM.Classification.ConfidenceAndRationalePresent
TEST:LLM.Classification.BetterThanKeywordBaseline

These tests require LM Studio to be running at http://127.0.0.1:1234
with a model loaded.  Run explicitly:

    cd src/apps/backend
    python -m pytest ../../tests/live/test_live_llm_classification.py -v -s -o asyncio_mode=auto --confcutdir=../../tests/live
"""

from __future__ import annotations

import logging

import pytest

from app.inference.config import InferenceSettings
from app.inference.openai_compat import OpenAICompatibleProvider
from app.inference.tasks.classification import (
    LLMClassificationResult,
    classify_project_llm,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ── Fixtures ─────────────────────────────────────────────────────────

SAMPLE_PROJECTS = [
    {
        "id": "11111111-1111-1111-1111-111111111111",
        "name": "Alpha Launch",
        "objective": "Q3 product launch for enterprise clients",
        "short_summary": "Enterprise SaaS product launch targeting Q3",
    },
    {
        "id": "22222222-2222-2222-2222-222222222222",
        "name": "Beta Migration",
        "objective": "Database migration to PostgreSQL 17",
        "short_summary": "Migrate production database from MySQL to PostgreSQL 17",
    },
    {
        "id": "33333333-3333-3333-3333-333333333333",
        "name": "Gamma Research",
        "objective": "Market research for APAC expansion",
        "short_summary": "Evaluate market opportunity in Southeast Asia and Australia",
    },
]


@pytest.fixture()
def provider() -> OpenAICompatibleProvider:
    """Create a provider pointing at the local LM Studio instance."""
    settings = InferenceSettings(
        connect_timeout_seconds=10.0,
        read_timeout_seconds=120.0,
    )
    return OpenAICompatibleProvider(settings)


# ── Classification Quality Tests ─────────────────────────────────────


class TestLiveClassification:
    """TEST:LLM.Classification.ProducesValidClassificationResult
    TEST:LLM.Classification.BetterThanKeywordBaseline
    """

    @pytest.mark.asyncio
    @pytest.mark.manual_only
    async def test_clear_project_match(self, provider: OpenAICompatibleProvider) -> None:
        """LLM correctly classifies a message with clear project signals."""
        result = await classify_project_llm(
            provider,
            projects=SAMPLE_PROJECTS,
            sender="alice@corp.com",
            subject="Re: Migration timeline update",
            body=(
                "The PostgreSQL 17 upgrade is on track. "
                "We've completed the schema validation and the test suite passes. "
                "Planning to do the production cutover next Thursday."
            ),
        )

        logger.info("Classification: %s (confidence: %.2f)", result.project_name, result.confidence)
        logger.info("Rationale: %s", result.rationale)
        logger.info("Latency: %.0fms", result.inference_latency_ms)

        assert isinstance(result, LLMClassificationResult)
        assert result.used_llm is True
        assert result.project_name == "Beta Migration"
        assert result.confidence >= 0.8
        assert len(result.rationale) > 10
        assert result.inference_latency_ms < 60_000  # 60s bound (includes cold-start)

    @pytest.mark.asyncio
    @pytest.mark.manual_only
    async def test_ambiguous_message(self, provider: OpenAICompatibleProvider) -> None:
        """LLM handles an ambiguous message that could match multiple projects."""
        result = await classify_project_llm(
            provider,
            projects=SAMPLE_PROJECTS,
            sender="bob@corp.com",
            subject="Timeline concerns",
            body=(
                "I'm worried about the timeline. We need to make sure "
                "everything is ready before the deadline. Can we schedule "
                "a call to discuss the status?"
            ),
        )

        logger.info("Classification: %s (confidence: %.2f)", result.project_name, result.confidence)
        logger.info("Rationale: %s", result.rationale)
        logger.info("Needs review: %s (reason: %s)", result.needs_review, result.review_reason)

        assert isinstance(result, LLMClassificationResult)
        # Ambiguous message should have lower confidence or needs_review
        # The LLM should recognize this is generic
        assert result.confidence < 0.9 or result.needs_review is True
        assert len(result.rationale) > 10

    @pytest.mark.asyncio
    @pytest.mark.manual_only
    async def test_no_project_match(self, provider: OpenAICompatibleProvider) -> None:
        """LLM correctly identifies a message that doesn't match any project."""
        result = await classify_project_llm(
            provider,
            projects=SAMPLE_PROJECTS,
            sender="newsletter@techdigest.com",
            subject="Weekly Tech Newsletter #247",
            body=(
                "Top stories this week: AI breakthroughs in robotics, "
                "new JavaScript framework gains traction, cloud computing "
                "costs continue to drop. Subscribe for more updates."
            ),
        )

        logger.info("Classification: %s (confidence: %.2f)", result.project_name, result.confidence)
        logger.info("Rationale: %s", result.rationale)
        logger.info("Needs review: %s", result.needs_review)

        assert isinstance(result, LLMClassificationResult)
        # Should recognize this is a newsletter, not project-related
        assert result.confidence < 0.5 or result.project_name is None
        assert result.needs_review is True

    @pytest.mark.asyncio
    @pytest.mark.manual_only
    async def test_implicit_project_reference(self, provider: OpenAICompatibleProvider) -> None:
        """LLM detects implicit project references that keyword matching would miss.

        TEST:LLM.Classification.BetterThanKeywordBaseline — this is the
        key test demonstrating LLM advantage over keywords.
        """
        result = await classify_project_llm(
            provider,
            projects=SAMPLE_PROJECTS,
            sender="carol@partner.com.au",
            subject="Singapore office visit",
            body=(
                "Hi, I'll be visiting the Singapore office next month. "
                "Would love to discuss the expansion plans and review "
                "the consumer research data we collected from the Jakarta survey. "
                "The Australian market analysis is also ready for review."
            ),
        )

        logger.info("Classification: %s (confidence: %.2f)", result.project_name, result.confidence)
        logger.info("Rationale: %s", result.rationale)

        assert isinstance(result, LLMClassificationResult)
        # LLM should recognize APAC expansion context
        # Keywords "Singapore", "expansion", "Jakarta", "Australian market"
        # should map to "Gamma Research" (APAC expansion)
        # A keyword matcher would likely miss this (no exact "Gamma Research" in text)
        assert result.project_name == "Gamma Research"
        assert result.confidence >= 0.6
        logger.info(
            "✓ LLM correctly identified Gamma Research from implicit APAC references "
            "(keyword matcher would likely miss this)"
        )


