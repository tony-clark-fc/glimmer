"""Tests for research and expert advice domain models.

TEST:Research.Provenance.RunAndSourceTrailPersisted
TEST:ExpertAdvice.Provenance.ExchangeRecordPersisted
TEST:ExpertAdvice.ModeSelection.FastThinkingProRespected

These tests verify that research runs, findings, source references,
summary artifacts, and expert advice exchanges persist correctly
with full provenance.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy.orm import Session

from app.models.research import (
    ExpertAdviceExchange,
    ResearchFinding,
    ResearchRun,
    ResearchSourceReference,
    ResearchSummaryArtifact,
)
from app.models.portfolio import Project
from app.models.operator import PrimaryOperator


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture()
def operator(db_session: Session) -> PrimaryOperator:
    """Create a test operator."""
    op = PrimaryOperator(display_name="Test Operator")
    db_session.add(op)
    db_session.flush()
    return op


@pytest.fixture()
def project(db_session: Session, operator: PrimaryOperator) -> Project:
    """Create a test project."""
    proj = Project(
        name="Test Project",
        short_summary="A test project for research tests",
        operator_id=operator.id,
    )
    db_session.add(proj)
    db_session.flush()
    return proj


# ── ResearchRun tests ─────────────────────────────────────────────────


class TestResearchRun:
    """TEST:Research.Invocation.StartsBoundedResearchRun"""

    def test_create_research_run(self, db_session: Session) -> None:
        """A research run can be created with required fields."""
        run = ResearchRun(
            invocation_origin="operator_request",
            research_query="Research soil carbon benchmarks",
            document_name="SOC-Research-20260414",
        )
        db_session.add(run)
        db_session.flush()

        assert run.id is not None
        assert run.status == "pending"
        assert run.invocation_origin == "operator_request"
        assert run.research_query == "Research soil carbon benchmarks"
        assert run.created_at is not None

    def test_research_run_provenance_preserved(
        self, db_session: Session, project: Project
    ) -> None:
        """TEST:Research.Provenance.RunAndSourceTrailPersisted —
        A research run preserves invocation origin, project linkage,
        and triggering context."""
        run = ResearchRun(
            invocation_origin="orchestration_escalation",
            triggering_context={
                "workflow": "triage_graph",
                "message_id": str(uuid.uuid4()),
            },
            project_id=project.id,
            research_query="Research Australian grassland ecology",
            document_name="AUS-TGP-20260414",
        )
        db_session.add(run)
        db_session.flush()

        fetched = db_session.get(ResearchRun, run.id)
        assert fetched is not None
        assert fetched.invocation_origin == "orchestration_escalation"
        assert fetched.triggering_context["workflow"] == "triage_graph"
        assert fetched.project_id == project.id

    def test_research_run_status_lifecycle(
        self, db_session: Session
    ) -> None:
        """Research run progresses through status states correctly."""
        run = ResearchRun(
            invocation_origin="operator_request",
            research_query="Test query",
        )
        db_session.add(run)
        db_session.flush()
        assert run.status == "pending"

        run.status = "in_progress"
        run.started_at = datetime.now(timezone.utc)
        db_session.flush()
        assert run.status == "in_progress"
        assert run.started_at is not None

        run.status = "completed"
        run.completed_at = datetime.now(timezone.utc)
        run.document_url = "https://docs.google.com/document/d/1abc"
        run.document_renamed = True
        run.completion_signal = "success"
        db_session.flush()
        assert run.status == "completed"
        assert run.document_url is not None

    def test_research_run_failed_state(self, db_session: Session) -> None:
        """Research run records failure information."""
        run = ResearchRun(
            invocation_origin="operator_request",
            research_query="Test query",
            status="failed",
            error_message="Chrome is not available",
            completion_signal="browser_unavailable",
        )
        db_session.add(run)
        db_session.flush()

        assert run.status == "failed"
        assert run.error_message == "Chrome is not available"
        assert run.completion_signal == "browser_unavailable"


# ── ResearchFinding tests ─────────────────────────────────────────────


class TestResearchFinding:
    """TEST:Research.Provenance.RunAndSourceTrailPersisted"""

    def test_create_finding_linked_to_run(
        self, db_session: Session
    ) -> None:
        """A finding is linked to its parent research run."""
        run = ResearchRun(
            invocation_origin="operator_request",
            research_query="Test query",
        )
        db_session.add(run)
        db_session.flush()

        finding = ResearchFinding(
            research_run_id=run.id,
            finding_type="evidence_point",
            content="SOC levels average 2.5% in tropical grasslands",
            confidence_signal="medium",
            source_url="https://example.com/paper",
            ordering=1,
        )
        db_session.add(finding)
        db_session.flush()

        assert finding.id is not None
        assert finding.research_run_id == run.id
        assert finding.finding_type == "evidence_point"

    def test_cascade_delete_findings(self, db_session: Session) -> None:
        """Deleting a research run cascades to its findings."""
        run = ResearchRun(
            invocation_origin="operator_request",
            research_query="Test",
        )
        f1 = ResearchFinding(
            finding_type="evidence_point",
            content="Finding 1",
        )
        f2 = ResearchFinding(
            finding_type="summary_claim",
            content="Finding 2",
        )
        run.findings = [f1, f2]
        db_session.add(run)
        db_session.flush()

        f1_id, f2_id = f1.id, f2.id
        db_session.delete(run)
        db_session.flush()

        assert db_session.get(ResearchFinding, f1_id) is None
        assert db_session.get(ResearchFinding, f2_id) is None


# ── ResearchSourceReference tests ─────────────────────────────────────


class TestResearchSourceReference:
    def test_create_source_reference(self, db_session: Session) -> None:
        """A source reference is linked to its parent research run."""
        run = ResearchRun(
            invocation_origin="operator_request",
            research_query="Test",
        )
        db_session.add(run)
        db_session.flush()

        ref = ResearchSourceReference(
            research_run_id=run.id,
            source_url="https://example.com/paper",
            source_title="Soil Carbon Review 2026",
            accessed_at=datetime.now(timezone.utc),
        )
        db_session.add(ref)
        db_session.flush()

        assert ref.id is not None
        assert ref.research_run_id == run.id


# ── ResearchSummaryArtifact tests ─────────────────────────────────────


class TestResearchSummaryArtifact:
    """TEST:Research.Output.ResultsReenterWorkflowSafely"""

    def test_create_summary_artifact(self, db_session: Session) -> None:
        """A summary artifact is linked to its research run."""
        run = ResearchRun(
            invocation_origin="operator_request",
            research_query="Test",
        )
        db_session.add(run)
        db_session.flush()

        summary = ResearchSummaryArtifact(
            research_run_id=run.id,
            summary_text="Key findings: SOC levels...",
            review_state="pending_review",
        )
        db_session.add(summary)
        db_session.flush()

        assert summary.id is not None
        assert summary.review_state == "pending_review"

    def test_summary_review_state_transitions(
        self, db_session: Session
    ) -> None:
        """Summary artifacts support review state transitions."""
        run = ResearchRun(
            invocation_origin="operator_request",
            research_query="Test",
        )
        db_session.add(run)
        db_session.flush()

        summary = ResearchSummaryArtifact(
            research_run_id=run.id,
            summary_text="Summary text",
        )
        db_session.add(summary)
        db_session.flush()
        assert summary.review_state == "pending_review"

        summary.review_state = "accepted"
        db_session.flush()
        assert summary.review_state == "accepted"


# ── ExpertAdviceExchange tests ────────────────────────────────────────


class TestExpertAdviceExchange:
    """TEST:ExpertAdvice.Provenance.ExchangeRecordPersisted
    TEST:ExpertAdvice.ModeSelection.FastThinkingProRespected"""

    def test_create_exchange(self, db_session: Session) -> None:
        """An expert advice exchange can be created with required fields."""
        exchange = ExpertAdviceExchange(
            invocation_origin="operator_request",
            prompt="What is the capital of Australia?",
            gemini_mode="Fast",
        )
        db_session.add(exchange)
        db_session.flush()

        assert exchange.id is not None
        assert exchange.status == "pending"
        assert exchange.gemini_mode == "Fast"
        assert exchange.review_state == "pending_review"
        assert exchange.created_at is not None

    def test_exchange_provenance_preserved(
        self, db_session: Session, project: Project
    ) -> None:
        """TEST:ExpertAdvice.Provenance.ExchangeRecordPersisted —
        Exchange preserves invocation origin, project linkage, mode,
        prompt, response, and duration."""
        exchange = ExpertAdviceExchange(
            invocation_origin="orchestration_escalation",
            triggering_context={
                "workflow": "planner_graph",
                "task_id": str(uuid.uuid4()),
            },
            project_id=project.id,
            prompt="Explain the implications of soil carbon credits",
            gemini_mode="Pro",
            response_text="Soil carbon credits represent...",
            duration_ms=15400,
            status="completed",
            completed_at=datetime.now(timezone.utc),
        )
        db_session.add(exchange)
        db_session.flush()

        fetched = db_session.get(ExpertAdviceExchange, exchange.id)
        assert fetched is not None
        assert fetched.invocation_origin == "orchestration_escalation"
        assert fetched.triggering_context["workflow"] == "planner_graph"
        assert fetched.project_id == project.id
        assert fetched.prompt == "Explain the implications of soil carbon credits"
        assert fetched.gemini_mode == "Pro"
        assert fetched.response_text == "Soil carbon credits represent..."
        assert fetched.duration_ms == 15400
        assert fetched.status == "completed"

    def test_exchange_mode_selection_fast(
        self, db_session: Session
    ) -> None:
        """TEST:ExpertAdvice.ModeSelection.FastThinkingProRespected —
        Fast mode is recorded correctly."""
        exchange = ExpertAdviceExchange(
            invocation_origin="operator_request",
            prompt="Quick question",
            gemini_mode="Fast",
        )
        db_session.add(exchange)
        db_session.flush()
        assert exchange.gemini_mode == "Fast"

    def test_exchange_mode_selection_thinking(
        self, db_session: Session
    ) -> None:
        """TEST:ExpertAdvice.ModeSelection.FastThinkingProRespected —
        Thinking mode is recorded correctly."""
        exchange = ExpertAdviceExchange(
            invocation_origin="operator_request",
            prompt="Complex reasoning task",
            gemini_mode="Thinking",
        )
        db_session.add(exchange)
        db_session.flush()
        assert exchange.gemini_mode == "Thinking"

    def test_exchange_mode_selection_pro(
        self, db_session: Session
    ) -> None:
        """TEST:ExpertAdvice.ModeSelection.FastThinkingProRespected —
        Pro mode is the default."""
        exchange = ExpertAdviceExchange(
            invocation_origin="operator_request",
            prompt="Expert consultation",
        )
        db_session.add(exchange)
        db_session.flush()
        assert exchange.gemini_mode == "Pro"

    def test_exchange_review_state_transitions(
        self, db_session: Session
    ) -> None:
        """TEST:ExpertAdvice.Output.ResponseEntersAsInterpretedCandidate —
        Exchange responses are interpreted candidates, supporting
        pending_review → accepted or rejected."""
        exchange = ExpertAdviceExchange(
            invocation_origin="operator_request",
            prompt="Test prompt",
            gemini_mode="Pro",
            response_text="Test response",
            status="completed",
        )
        db_session.add(exchange)
        db_session.flush()
        assert exchange.review_state == "pending_review"

        exchange.review_state = "accepted"
        db_session.flush()
        assert exchange.review_state == "accepted"

    def test_exchange_failure_state(self, db_session: Session) -> None:
        """TEST:ExpertAdvice.Failure.GeminiUnavailableHandledSafely —
        Exchange records failure information."""
        exchange = ExpertAdviceExchange(
            invocation_origin="operator_request",
            prompt="Test prompt",
            gemini_mode="Pro",
            status="browser_unavailable",
            error_message="Chrome is not available",
        )
        db_session.add(exchange)
        db_session.flush()

        assert exchange.status == "browser_unavailable"
        assert exchange.error_message == "Chrome is not available"
        assert exchange.response_text is None


# ── Full provenance chain tests ───────────────────────────────────────


class TestResearchProvenanceChain:
    """TEST:Research.Provenance.RunAndSourceTrailPersisted —
    End-to-end provenance from run to findings to sources to summary."""

    def test_full_research_artifact_chain(
        self, db_session: Session, project: Project
    ) -> None:
        """A complete research run with findings, sources, and summary
        preserves the full provenance chain."""
        run = ResearchRun(
            invocation_origin="orchestration_escalation",
            triggering_context={"workflow": "triage_graph"},
            project_id=project.id,
            research_query="Research Australian grassland ecology",
            document_name="AUS-TGP-20260414",
            status="completed",
            completion_signal="success",
            document_url="https://docs.google.com/document/d/1abc",
            document_renamed=True,
        )

        finding1 = ResearchFinding(
            finding_type="evidence_point",
            content="Finding 1",
            ordering=1,
        )
        finding2 = ResearchFinding(
            finding_type="summary_claim",
            content="Finding 2",
            ordering=2,
        )
        run.findings = [finding1, finding2]

        source_ref = ResearchSourceReference(
            source_url="https://example.com/paper",
            source_title="Ecology Review 2026",
        )
        run.source_references = [source_ref]

        summary = ResearchSummaryArtifact(
            summary_text="Key findings from the research run...",
            review_state="pending_review",
        )
        run.summary_artifact = summary

        db_session.add(run)
        db_session.flush()

        # Verify chain
        fetched_run = db_session.get(ResearchRun, run.id)
        assert fetched_run is not None
        assert len(fetched_run.findings) == 2
        assert len(fetched_run.source_references) == 1
        assert fetched_run.summary_artifact is not None
        assert fetched_run.summary_artifact.review_state == "pending_review"
        assert fetched_run.project_id == project.id


