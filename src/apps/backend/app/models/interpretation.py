"""Interpretation-layer domain models and review-state semantics.

ARCH:MessageClassificationModel
ARCH:ExtractedActionModel
ARCH:ExtractedDecisionModel
ARCH:ExtractedDeadlineSignalModel
ARCH:InterpretationReviewState

These entities are reviewable candidate artifacts — they must never
silently become accepted truth.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Float, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _genuuid() -> uuid.UUID:
    return uuid.uuid4()


# ── Review-state values ─────────────────────────────────────────────
# pending_review | accepted | amended | rejected | superseded

VALID_REVIEW_STATES = frozenset(
    {"pending_review", "accepted", "amended", "rejected", "superseded"}
)


class MessageClassification(Base):
    """Structured interpretation of a message or signal — project relevance,
    stakeholder extraction, and confidence scoring."""

    __tablename__ = "message_classifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    source_record_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )  # FK-free: may point at messages, imported_signals, etc.
    source_record_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # message, imported_signal, calendar_event
    candidate_project_ids: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )
    selected_project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
    )
    confidence: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    ambiguity_flag: Mapped[bool] = mapped_column(default=False)
    classification_rationale: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    extracted_stakeholder_ids: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )
    review_state: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending_review"
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    def __repr__(self) -> str:
        return (
            f"<MessageClassification {self.id!s:.8} "
            f"review={self.review_state!r}>"
        )


class ExtractedAction(Base):
    """A candidate follow-up or requested action detected from a source record."""

    __tablename__ = "extracted_actions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    source_record_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    source_record_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    linked_project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
    )
    proposed_owner: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    action_text: Mapped[str] = mapped_column(Text, nullable=False)
    due_date_signal: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    urgency_signal: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )
    review_state: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending_review"
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    def __repr__(self) -> str:
        return (
            f"<ExtractedAction {self.id!s:.8} "
            f"review={self.review_state!r}>"
        )


class ExtractedDecision(Base):
    """A decision inferred from a communication or briefing artifact."""

    __tablename__ = "extracted_decisions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    source_record_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    source_record_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    linked_project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
    )
    decision_text: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    review_state: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending_review"
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    def __repr__(self) -> str:
        return (
            f"<ExtractedDecision {self.id!s:.8} "
            f"review={self.review_state!r}>"
        )


class ExtractedDeadlineSignal(Base):
    """A time-bound obligation or inferred deadline reference."""

    __tablename__ = "extracted_deadline_signals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    source_record_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    source_record_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    linked_project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
    )
    deadline_text: Mapped[str] = mapped_column(Text, nullable=False)
    inferred_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    confidence: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    review_state: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending_review"
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    def __repr__(self) -> str:
        return (
            f"<ExtractedDeadlineSignal {self.id!s:.8} "
            f"review={self.review_state!r}>"
        )

