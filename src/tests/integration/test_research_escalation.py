"""Tests for the Research Escalation Graph and routing policy.

TEST:Research.Escalation.RoutesWhenTaskRequiresDeepResearch
TEST:ExpertAdvice.Routing.EscalationDistinguishesResearchFromAdvice
TEST:ExpertAdvice.Output.ResponseEntersAsInterpretedCandidate
TEST:Research.Output.ResultsReenterWorkflowSafely
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy.orm import Session

from app.graphs.research import (
    EscalationResult,
    determine_escalation_mode,
)
from app.models.research import (
    ExpertAdviceExchange,
    ResearchRun,
    ResearchSummaryArtifact,
)
from app.models.portfolio import Project
from app.models.operator import PrimaryOperator
from app.models.audit import AuditRecord


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture()
def operator(db_session: Session) -> PrimaryOperator:
    op = PrimaryOperator(display_name="Test Operator")
    db_session.add(op)
    db_session.flush()
    return op


@pytest.fixture()
def project(db_session: Session, operator: PrimaryOperator) -> Project:
    proj = Project(
        name="Test Project",
        short_summary="Test",
        operator_id=operator.id,
    )
    db_session.add(proj)
    db_session.flush()
    return proj


# ── Routing Policy Tests (H8) ────────────────────────────────────────


class TestDetermineEscalationMode:
    """TEST:ExpertAdvice.Routing.EscalationDistinguishesResearchFromAdvice"""

    def test_explicit_research_mode(self) -> None:
        """Explicit 'research' override wins."""
        assert determine_escalation_mode("quick question", explicit_mode="research") == "research"

    def test_explicit_deep_research_mode(self) -> None:
        """Explicit 'deep_research' override wins."""
        assert determine_escalation_mode("quick question", explicit_mode="deep_research") == "research"

    def test_explicit_advice_mode(self) -> None:
        """Explicit 'advice' override wins."""
        result = determine_escalation_mode(
            "Research and investigate everything comprehensively",
            explicit_mode="advice",
        )
        assert result == "advice"

    def test_explicit_chat_mode(self) -> None:
        """'chat' maps to advice."""
        assert determine_escalation_mode("test", explicit_mode="chat") == "advice"

    def test_explicit_expert_advice_mode(self) -> None:
        """'expert_advice' maps to advice."""
        assert determine_escalation_mode("test", explicit_mode="expert_advice") == "advice"

    def test_heuristic_research_keywords(self) -> None:
        """Multiple research keywords trigger research mode."""
        result = determine_escalation_mode(
            "Please research and investigate the comprehensive benchmark data"
        )
        assert result == "research"

    def test_heuristic_single_keyword_defaults_advice(self) -> None:
        """A single research keyword isn't enough — defaults to advice."""
        result = determine_escalation_mode(
            "What does the research say about this?"
        )
        assert result == "advice"

    def test_heuristic_long_prompt_triggers_research(self) -> None:
        """A very long prompt suggests research."""
        long_prompt = "Please help me understand " + "the topic " * 60
        assert len(long_prompt) > 500
        result = determine_escalation_mode(long_prompt)
        assert result == "research"

    def test_default_is_advice(self) -> None:
        """Short simple questions default to advice."""
        assert determine_escalation_mode("What is 2+2?") == "advice"

    def test_no_explicit_mode_is_none(self) -> None:
        """None explicit_mode uses heuristic."""
        result = determine_escalation_mode("Tell me about X", explicit_mode=None)
        assert result == "advice"


# ── Escalation Result Tests ──────────────────────────────────────────


class TestEscalationResult:
    def test_research_result_shape(self) -> None:
        r = EscalationResult(
            mode="research",
            status="completed",
            research_run_id=uuid.uuid4(),
            document_url="https://docs.google.com/document/d/1abc",
        )
        assert r.mode == "research"
        assert r.status == "completed"
        assert r.document_url is not None

    def test_advice_result_shape(self) -> None:
        r = EscalationResult(
            mode="advice",
            status="completed",
            expert_advice_exchange_id=uuid.uuid4(),
            response_text="The answer is 42.",
        )
        assert r.mode == "advice"
        assert r.response_text == "The answer is 42."

    def test_failed_result_shape(self) -> None:
        r = EscalationResult(
            mode="research",
            status="failed",
            research_run_id=uuid.uuid4(),
            error_message="Chrome not available",
        )
        assert r.status == "failed"
        assert r.error_message is not None


# ── Persistence Integration Tests ─────────────────────────────────────


class TestResearchRunPersistenceForGraph:
    """TEST:Research.Output.ResultsReenterWorkflowSafely"""

    def test_research_run_completed_with_summary(
        self, db_session: Session, project: Project
    ) -> None:
        """A completed research run has a summary artifact with pending_review."""
        run = ResearchRun(
            invocation_origin="orchestration_escalation",
            project_id=project.id,
            research_query="Test research query",
            document_name="Test-Doc",
            status="completed",
            completion_signal="success",
            document_url="https://docs.google.com/document/d/1abc",
        )
        db_session.add(run)
        db_session.flush()

        summary = ResearchSummaryArtifact(
            research_run_id=run.id,
            summary_text="Research completed",
            review_state="pending_review",
        )
        db_session.add(summary)

        audit = AuditRecord(
            entity_type="research_run",
            entity_id=run.id,
            action="completed",
            actor="orchestration_escalation",
            change_summary="Deep research completed",
        )
        db_session.add(audit)
        db_session.flush()

        # Verify chain
        fetched = db_session.get(ResearchRun, run.id)
        assert fetched.summary_artifact is not None
        assert fetched.summary_artifact.review_state == "pending_review"

    def test_failed_research_run_records_error(
        self, db_session: Session
    ) -> None:
        """A failed research run records the error message."""
        run = ResearchRun(
            invocation_origin="operator_request",
            research_query="Test",
            status="failed",
            completion_signal="error",
            error_message="Chrome is not available",
        )
        db_session.add(run)
        db_session.flush()

        assert run.status == "failed"
        assert run.error_message == "Chrome is not available"


class TestExpertAdvicePersistenceForGraph:
    """TEST:ExpertAdvice.Output.ResponseEntersAsInterpretedCandidate"""

    def test_exchange_completed_as_pending_review(
        self, db_session: Session, project: Project
    ) -> None:
        """A completed exchange enters as pending_review."""
        exchange = ExpertAdviceExchange(
            invocation_origin="operator_request",
            project_id=project.id,
            prompt="What are the implications?",
            gemini_mode="Pro",
            response_text="The implications are...",
            status="completed",
            review_state="pending_review",
            duration_ms=5000,
        )
        db_session.add(exchange)
        db_session.flush()

        audit = AuditRecord(
            entity_type="expert_advice_exchange",
            entity_id=exchange.id,
            action="completed",
            actor="operator_request",
            change_summary="Expert advice completed",
        )
        db_session.add(audit)
        db_session.flush()

        fetched = db_session.get(ExpertAdviceExchange, exchange.id)
        assert fetched.review_state == "pending_review"
        assert fetched.response_text is not None

    def test_exchange_failed_records_error(
        self, db_session: Session
    ) -> None:
        """A failed exchange records the error."""
        exchange = ExpertAdviceExchange(
            invocation_origin="operator_request",
            prompt="Test",
            gemini_mode="Fast",
            status="failed",
            error_message="Browser unavailable",
        )
        db_session.add(exchange)
        db_session.flush()

        assert exchange.status == "failed"
        assert exchange.error_message is not None

    def test_exchange_audit_trail(
        self, db_session: Session
    ) -> None:
        """Audit records are created for exchange lifecycle events."""
        exchange = ExpertAdviceExchange(
            invocation_origin="orchestration_escalation",
            prompt="Complex question",
            gemini_mode="Thinking",
            status="completed",
            response_text="Answer",
        )
        db_session.add(exchange)
        db_session.flush()

        audit = AuditRecord(
            entity_type="expert_advice_exchange",
            entity_id=exchange.id,
            action="completed",
            actor="orchestration_escalation",
            change_summary="Expert advice — Thinking mode — 5000ms",
        )
        db_session.add(audit)
        db_session.flush()

        assert audit.entity_id == exchange.id
        assert audit.entity_type == "expert_advice_exchange"


