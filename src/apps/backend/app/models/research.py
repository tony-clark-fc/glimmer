"""Research and expert advice domain models.

ARCH:ResearchRunModel
ARCH:ResearchFindingModel
ARCH:ResearchSourceReferenceModel
ARCH:ResearchSummaryArtifactModel
ARCH:ExpertAdviceExchangeModel

These entities form the deep-research and expert-advice capability layer.
Research runs model long-running Gemini Deep Research interactions.
Expert advice exchanges model synchronous Gemini chat consultations.
Both preserve full provenance and enter workflows as interpreted candidates.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _genuuid() -> uuid.UUID:
    return uuid.uuid4()


# ── Research Run ─────────────────────────────────────────────────────


class ResearchRun(Base):
    """A single bounded execution of the deep-research capability.

    Represents an async, long-running Gemini Deep Research interaction
    that produces a Google Docs artifact and structured findings.

    TEST:Research.Invocation.StartsBoundedResearchRun
    TEST:Research.Provenance.RunAndSourceTrailPersisted
    """

    __tablename__ = "research_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    invocation_origin: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # operator_request, orchestration_escalation, policy_routing
    triggering_context: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )  # linked workflow, project, message, or task identifiers
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
    )
    research_query: Mapped[str] = mapped_column(Text, nullable=False)
    document_name: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True
    )  # requested Google Doc filename
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending"
    )  # pending, in_progress, completed, completed_with_warning, failed, degraded, rate_limited
    completion_signal: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # success, partial, timeout, browser_unavailable, error
    document_url: Mapped[Optional[str]] = mapped_column(
        String(2048), nullable=True
    )  # URL of the exported Google Doc
    document_renamed: Mapped[Optional[bool]] = mapped_column(
        nullable=True
    )  # whether the doc rename succeeded
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    # Relationships
    findings: Mapped[list["ResearchFinding"]] = relationship(
        back_populates="research_run", cascade="all, delete-orphan"
    )
    source_references: Mapped[list["ResearchSourceReference"]] = relationship(
        back_populates="research_run", cascade="all, delete-orphan"
    )
    summary_artifact: Mapped[Optional["ResearchSummaryArtifact"]] = relationship(
        back_populates="research_run", cascade="all, delete-orphan", uselist=False
    )

    def __repr__(self) -> str:
        return (
            f"<ResearchRun {self.id!s:.8} status={self.status!r} "
            f"origin={self.invocation_origin!r}>"
        )


# ── Research Finding ─────────────────────────────────────────────────


class ResearchFinding(Base):
    """An individual structured finding or evidence point from a research run.

    TEST:Research.Provenance.RunAndSourceTrailPersisted
    """

    __tablename__ = "research_findings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    research_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("research_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    finding_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # evidence_point, summary_claim, extracted_fact, decision_support, reasoning_note
    content: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_signal: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # high, medium, low, unassessed
    source_url: Mapped[Optional[str]] = mapped_column(
        String(2048), nullable=True
    )
    ordering: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # relevance/order within the run
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    # Relationships
    research_run: Mapped["ResearchRun"] = relationship(
        back_populates="findings"
    )

    def __repr__(self) -> str:
        return (
            f"<ResearchFinding {self.id!s:.8} type={self.finding_type!r} "
            f"run={self.research_run_id!s:.8}>"
        )


# ── Research Source Reference ────────────────────────────────────────


class ResearchSourceReference(Base):
    """Provenance about external sources consulted during a research run.

    TEST:Research.Provenance.RunAndSourceTrailPersisted
    """

    __tablename__ = "research_source_references"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    research_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("research_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_url: Mapped[Optional[str]] = mapped_column(
        String(2048), nullable=True
    )
    source_title: Mapped[Optional[str]] = mapped_column(
        String(1024), nullable=True
    )
    source_description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    accessed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    relevance_notes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    # Relationships
    research_run: Mapped["ResearchRun"] = relationship(
        back_populates="source_references"
    )

    def __repr__(self) -> str:
        return (
            f"<ResearchSourceReference {self.id!s:.8} "
            f"url={self.source_url!r:.40}>"
        )


# ── Research Summary Artifact ────────────────────────────────────────


class ResearchSummaryArtifact(Base):
    """The structured summary output of a research run.

    TEST:Research.Output.ResultsReenterWorkflowSafely
    """

    __tablename__ = "research_summary_artifacts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    research_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("research_runs.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    summary_text: Mapped[str] = mapped_column(Text, nullable=False)
    key_findings_refs: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )  # list of finding IDs or structured references
    linked_project_ids: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )  # list of project UUIDs
    review_state: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending_review"
    )  # pending_review, accepted, rejected
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    # Relationships
    research_run: Mapped["ResearchRun"] = relationship(
        back_populates="summary_artifact"
    )

    def __repr__(self) -> str:
        return (
            f"<ResearchSummaryArtifact {self.id!s:.8} "
            f"review={self.review_state!r}>"
        )


# ── Expert Advice Exchange ───────────────────────────────────────────


class ExpertAdviceExchange(Base):
    """A single synchronous consultation with Gemini through the expert-advice path.

    This is architecturally distinct from ResearchRun — it is a single
    prompt-response pair completed in seconds to minutes, not a multi-step
    research investigation.

    Responses enter Glimmer as interpreted candidates, not accepted truth.

    TEST:ExpertAdvice.Invocation.SendsPromptAndReturnsResponse
    TEST:ExpertAdvice.Provenance.ExchangeRecordPersisted
    TEST:ExpertAdvice.ModeSelection.FastThinkingProRespected
    """

    __tablename__ = "expert_advice_exchanges"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    invocation_origin: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # operator_request, orchestration_escalation, workflow_trigger
    triggering_context: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )  # linked workflow, project, message, or task identifiers
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
    )
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    gemini_mode: Mapped[str] = mapped_column(
        String(20), nullable=False, default="Pro"
    )  # Fast, Thinking, Pro
    response_text: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    duration_ms: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # wall-clock duration in milliseconds
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending"
    )  # pending, in_progress, completed, failed, timeout, browser_unavailable
    error_message: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    review_state: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending_review"
    )  # pending_review, accepted, rejected
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def __repr__(self) -> str:
        return (
            f"<ExpertAdviceExchange {self.id!s:.8} mode={self.gemini_mode!r} "
            f"status={self.status!r}>"
        )


