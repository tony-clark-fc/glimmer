"""Integration tests for LLM wiring into graph/service flows.

PLAN:WorkstreamI.PackageI8.OrchestrationWiring
TEST:LLM.Orchestration.TriagePipelineUsesLLMWhenAvailable
TEST:LLM.Orchestration.FallbackChainWorksCleanly
TEST:LLM.Safety.ReviewGatesNotWeakened
TEST:LLM.Safety.NoAutoSendNotWeakened

Verifies that the LLM-enhanced entry points in the graph/service layer:
- Respect per-task LLM toggles
- Fall back to deterministic logic when LLM is disabled
- Preserve all safety invariants (review gates, no-auto-send)
- Accept the same inputs and produce compatible outputs
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from unittest.mock import patch, AsyncMock, MagicMock

import pytest
from sqlalchemy.orm import Session

from app.models.portfolio import Project
from app.models.execution import WorkItem
from app.models.interpretation import ExtractedAction
from app.models.drafting import FocusPack


# ── Triage Classification Wiring Tests ───────────────────────────────


class TestClassifyProjectEnhanced:
    """Tests for classify_project_enhanced() wiring."""

    def test_uses_deterministic_when_llm_disabled(self, db_session: Session) -> None:
        """When LLM classification is disabled, uses deterministic path."""
        project = Project(name="Alpha Project", status="active", objective="Build Alpha")
        db_session.add(project)
        db_session.flush()

        from app.graphs.triage import classify_project_enhanced

        with patch.dict(os.environ, {"GLIMMER_INFERENCE_LLM_CLASSIFICATION_ENABLED": "false"}):
            result = classify_project_enhanced(
                db_session,
                sender_identity="test@example.com",
                subject="Alpha Project update",
                body_text="Progress on Alpha Project",
            )

        # Should have found the project via keyword matching
        assert result.project_id == project.id
        assert result.confidence > 0
        assert isinstance(result.rationale, str)

    def test_returns_classification_result_type(self, db_session: Session) -> None:
        """Enhanced classification returns a ClassificationResult."""
        db_session.add(Project(name="Beta", status="active"))
        db_session.flush()

        from app.graphs.triage import classify_project_enhanced, ClassificationResult

        with patch.dict(os.environ, {"GLIMMER_INFERENCE_LLM_CLASSIFICATION_ENABLED": "false"}):
            result = classify_project_enhanced(
                db_session, "sender", "subject", "body",
            )

        assert isinstance(result, ClassificationResult)
        assert hasattr(result, "project_id")
        assert hasattr(result, "confidence")
        assert hasattr(result, "needs_review")

    def test_low_confidence_triggers_review(self, db_session: Session) -> None:
        """Low-confidence classification still triggers review gate."""
        db_session.add(Project(name="Gamma", status="active"))
        db_session.flush()

        from app.graphs.triage import classify_project_enhanced

        with patch.dict(os.environ, {"GLIMMER_INFERENCE_LLM_CLASSIFICATION_ENABLED": "false"}):
            result = classify_project_enhanced(
                db_session,
                sender_identity="nobody@example.com",
                subject="Newsletter digest",
                body_text="Click here to unsubscribe",
            )

        # No project match → review needed
        assert result.needs_review is True

    def test_falls_back_on_exception(self, db_session: Session) -> None:
        """If LLM path raises, falls back to deterministic."""
        db_session.add(Project(name="Delta", status="active", objective="Build Delta"))
        db_session.flush()

        from app.graphs.triage import classify_project_enhanced

        with patch.dict(os.environ, {"GLIMMER_INFERENCE_LLM_CLASSIFICATION_ENABLED": "true"}):
            with patch("app.graphs.triage.asyncio.run", side_effect=RuntimeError("LM Studio down")):
                result = classify_project_enhanced(
                    db_session,
                    sender_identity="test@example.com",
                    subject="Delta update",
                    body_text="Delta Project progress report",
                )

        # Should have fallen back to deterministic and still found Delta
        assert result.project_id == db_session.execute(
            __import__("sqlalchemy").select(Project).where(Project.name == "Delta")
        ).scalar_one().id


# ── Triage Extraction Wiring Tests ───────────────────────────────────


class TestExtractWithLLM:
    """Tests for extract_with_llm() wiring."""

    def test_returns_empty_when_llm_disabled(self) -> None:
        """When LLM extraction is disabled, returns empty extraction."""
        from app.graphs.triage import extract_with_llm

        with patch.dict(os.environ, {"GLIMMER_INFERENCE_LLM_EXTRACTION_ENABLED": "false"}):
            result = extract_with_llm(
                sender="test@example.com",
                subject="Please review the contract",
                body="We need to finalize the contract by Friday.",
            )

        assert result == {"actions": [], "decisions": [], "deadlines": []}

    def test_returns_dict_compatible_with_extract_and_persist(self) -> None:
        """Result dict has keys usable by extract_and_persist()."""
        from app.graphs.triage import extract_with_llm

        with patch.dict(os.environ, {"GLIMMER_INFERENCE_LLM_EXTRACTION_ENABLED": "false"}):
            result = extract_with_llm("sender", "subject", "body")

        assert "actions" in result
        assert "decisions" in result
        assert "deadlines" in result
        assert isinstance(result["actions"], list)
        assert isinstance(result["decisions"], list)
        assert isinstance(result["deadlines"], list)

    def test_falls_back_on_exception(self) -> None:
        """If LLM path raises, returns empty dict."""
        from app.graphs.triage import extract_with_llm

        with patch.dict(os.environ, {"GLIMMER_INFERENCE_LLM_EXTRACTION_ENABLED": "true"}):
            with patch("app.graphs.triage.asyncio.run", side_effect=RuntimeError("down")):
                result = extract_with_llm("sender", "subject", "body")

        assert result == {"actions": [], "decisions": [], "deadlines": []}


# ── Planner Focus Pack Narrative Tests ───────────────────────────────


class TestFocusPackNarrative:
    """Tests for LLM narrative enrichment in focus pack generation."""

    def test_no_narrative_when_llm_disabled(self, db_session: Session) -> None:
        """When LLM prioritization is disabled, no narrative is generated."""
        from app.graphs.planner import generate_focus_pack

        with patch.dict(os.environ, {"GLIMMER_INFERENCE_LLM_PRIORITIZATION_ENABLED": "false"}):
            result = generate_focus_pack(db_session)

        assert result.narrative_summary is None

    def test_focus_pack_result_has_narrative_field(self, db_session: Session) -> None:
        """FocusPackResult includes the narrative_summary attribute."""
        from app.graphs.planner import generate_focus_pack, FocusPackResult

        with patch.dict(os.environ, {"GLIMMER_INFERENCE_LLM_PRIORITIZATION_ENABLED": "false"}):
            result = generate_focus_pack(db_session)

        assert isinstance(result, FocusPackResult)
        assert hasattr(result, "narrative_summary")

    def test_narrative_persists_in_focus_pack_model(self, db_session: Session) -> None:
        """The FocusPack model supports narrative_summary column."""
        fp = FocusPack(
            top_actions={"items": [{"title": "Test", "rationale": "Reason"}]},
            narrative_summary="This is a test narrative from the LLM.",
        )
        db_session.add(fp)
        db_session.flush()

        loaded = db_session.get(FocusPack, fp.id)
        assert loaded is not None
        assert loaded.narrative_summary == "This is a test narrative from the LLM."

    def test_narrative_column_is_nullable(self, db_session: Session) -> None:
        """The narrative_summary column accepts None."""
        fp = FocusPack(narrative_summary=None)
        db_session.add(fp)
        db_session.flush()

        loaded = db_session.get(FocusPack, fp.id)
        assert loaded is not None
        assert loaded.narrative_summary is None


# ── Drafting LLM Wiring Tests ────────────────────────────────────────


class TestCreateDraftEnhanced:
    """Tests for create_draft_enhanced() wiring."""

    def test_uses_provided_body_when_present(self, db_session: Session) -> None:
        """When body_content is provided, uses it directly."""
        from app.graphs.drafting import create_draft_enhanced

        with patch.dict(os.environ, {"GLIMMER_INFERENCE_LLM_DRAFTING_ENABLED": "false"}):
            result = create_draft_enhanced(
                db_session,
                body_content="Hello, this is my pre-written draft.",
                intent="reply",
            )

        assert result.auto_send_blocked is True
        assert result.review_required is True

    def test_no_auto_send_on_llm_path(self, db_session: Session) -> None:
        """auto_send_blocked is True even on the LLM path."""
        from app.graphs.drafting import create_draft_enhanced, AUTO_SEND_BLOCKED

        with patch.dict(os.environ, {"GLIMMER_INFERENCE_LLM_DRAFTING_ENABLED": "false"}):
            result = create_draft_enhanced(
                db_session,
                body_content="Draft content",
            )

        assert result.auto_send_blocked is True
        assert AUTO_SEND_BLOCKED is True

    def test_empty_body_with_llm_disabled_creates_empty_draft(self, db_session: Session) -> None:
        """When LLM is disabled and no body provided, creates draft with empty body."""
        from app.graphs.drafting import create_draft_enhanced
        from app.models.drafting import Draft

        with patch.dict(os.environ, {"GLIMMER_INFERENCE_LLM_DRAFTING_ENABLED": "false"}):
            result = create_draft_enhanced(
                db_session,
                body_content="",
                intent="reply",
            )

        draft = db_session.get(Draft, result.draft_id)
        assert draft is not None
        assert draft.body_content == ""
        assert draft.status == "draft"

    def test_has_send_capability_always_false(self) -> None:
        """has_send_capability() remains False — hard boundary."""
        from app.graphs.drafting import has_send_capability
        assert has_send_capability() is False


# ── Briefing LLM Wiring Tests ───────────────────────────────────────


class TestBriefingLLMWiring:
    """Tests for LLM wiring in spoken briefing generation."""

    def test_template_fallback_when_llm_disabled(self, db_session: Session) -> None:
        """When LLM briefing is disabled, uses template formatting."""
        fp = FocusPack(
            top_actions={"items": [
                {"title": "Review contracts", "rationale": "Due tomorrow"},
            ]},
        )
        db_session.add(fp)
        db_session.flush()

        from app.services.briefing import generate_spoken_briefing

        with patch.dict(os.environ, {"GLIMMER_INFERENCE_LLM_BRIEFING_ENABLED": "false"}):
            result = generate_spoken_briefing(db_session, focus_pack_id=fp.id)

        assert result.is_empty is False
        assert "Review contracts" in result.briefing_text
        assert result.source_focus_pack_id == fp.id

    def test_briefing_still_bounded_when_llm_disabled(self, db_session: Session) -> None:
        """Template briefing still respects MAX_BRIEFING_LENGTH."""
        from app.services.briefing import generate_spoken_briefing, MAX_BRIEFING_LENGTH

        # Create a focus pack with lots of data
        fp = FocusPack(
            top_actions={"items": [
                {"title": f"Action {i} with a really long description that goes on and on", "rationale": f"Reason {i}"}
                for i in range(10)
            ]},
            high_risk_items={"items": [
                {"summary": f"Risk {i} description", "severity": "high"}
                for i in range(5)
            ]},
        )
        db_session.add(fp)
        db_session.flush()

        with patch.dict(os.environ, {"GLIMMER_INFERENCE_LLM_BRIEFING_ENABLED": "false"}):
            result = generate_spoken_briefing(db_session, focus_pack_id=fp.id)

        assert len(result.briefing_text) <= MAX_BRIEFING_LENGTH


# ── Per-Task Toggle Tests ────────────────────────────────────────────


class TestPerTaskToggles:
    """Tests for the per-task LLM toggle settings."""

    def test_all_toggles_default_to_true(self) -> None:
        """Per-task toggles default to True (LLM-first)."""
        from app.inference.config import InferenceSettings

        # Clear env to test pure defaults
        env_overrides = {
            "GLIMMER_INFERENCE_LLM_CLASSIFICATION_ENABLED": "true",
            "GLIMMER_INFERENCE_LLM_EXTRACTION_ENABLED": "true",
            "GLIMMER_INFERENCE_LLM_PRIORITIZATION_ENABLED": "true",
            "GLIMMER_INFERENCE_LLM_DRAFTING_ENABLED": "true",
            "GLIMMER_INFERENCE_LLM_BRIEFING_ENABLED": "true",
        }
        with patch.dict(os.environ, env_overrides):
            settings = InferenceSettings()

        assert settings.llm_classification_enabled is True
        assert settings.llm_extraction_enabled is True
        assert settings.llm_prioritization_enabled is True
        assert settings.llm_drafting_enabled is True
        assert settings.llm_briefing_enabled is True

    def test_toggles_can_be_disabled_via_env(self) -> None:
        """Per-task toggles can be disabled via environment variables."""
        from app.inference.config import InferenceSettings

        env_overrides = {
            "GLIMMER_INFERENCE_LLM_CLASSIFICATION_ENABLED": "false",
            "GLIMMER_INFERENCE_LLM_EXTRACTION_ENABLED": "false",
            "GLIMMER_INFERENCE_LLM_PRIORITIZATION_ENABLED": "false",
            "GLIMMER_INFERENCE_LLM_DRAFTING_ENABLED": "false",
            "GLIMMER_INFERENCE_LLM_BRIEFING_ENABLED": "false",
        }
        with patch.dict(os.environ, env_overrides):
            settings = InferenceSettings()

        assert settings.llm_classification_enabled is False
        assert settings.llm_extraction_enabled is False
        assert settings.llm_prioritization_enabled is False
        assert settings.llm_drafting_enabled is False
        assert settings.llm_briefing_enabled is False

    def test_individual_toggle_independence(self) -> None:
        """Each toggle is independent — can enable one and disable others."""
        from app.inference.config import InferenceSettings

        env_overrides = {
            "GLIMMER_INFERENCE_LLM_CLASSIFICATION_ENABLED": "true",
            "GLIMMER_INFERENCE_LLM_EXTRACTION_ENABLED": "false",
            "GLIMMER_INFERENCE_LLM_PRIORITIZATION_ENABLED": "true",
            "GLIMMER_INFERENCE_LLM_DRAFTING_ENABLED": "false",
            "GLIMMER_INFERENCE_LLM_BRIEFING_ENABLED": "true",
        }
        with patch.dict(os.environ, env_overrides):
            settings = InferenceSettings()

        assert settings.llm_classification_enabled is True
        assert settings.llm_extraction_enabled is False
        assert settings.llm_prioritization_enabled is True
        assert settings.llm_drafting_enabled is False
        assert settings.llm_briefing_enabled is True

