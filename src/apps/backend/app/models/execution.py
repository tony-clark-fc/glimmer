"""Accepted operational artifact domain models.

ARCH:WorkItemModel
ARCH:DecisionRecordModel
ARCH:RiskRecordModel
ARCH:BlockerRecordModel
ARCH:WaitingOnRecordModel

These are the durable accepted-state records — distinct from
interpreted candidate artifacts.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _genuuid() -> uuid.UUID:
    return uuid.uuid4()


class WorkItem(Base):
    """Canonical actionable execution record in the project."""

    __tablename__ = "work_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    workstream_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("project_workstreams.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    item_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="task"
    )  # task, follow_up, reminder
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="open"
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    owner_hint: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    source_provenance: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )  # origin linkage: extracted_action_id, message_id, etc.
    priority_indicators: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    def __repr__(self) -> str:
        return f"<WorkItem {self.id!s:.8} title={self.title!r}>"


class DecisionRecord(Base):
    """Accepted canonical project decision — distinct from ExtractedDecision."""

    __tablename__ = "decision_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    decision_text: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    decided_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    source_provenance: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    def __repr__(self) -> str:
        return f"<DecisionRecord {self.id!s:.8} title={self.title!r}>"


class RiskRecord(Base):
    """A recognized project risk."""

    __tablename__ = "risk_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    severity_signal: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )
    likelihood_signal: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )
    mitigation_notes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="open"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    def __repr__(self) -> str:
        return f"<RiskRecord {self.id!s:.8}>"


class BlockerRecord(Base):
    """An active impediment to project execution."""

    __tablename__ = "blocker_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    blocking_what: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    owner_hint: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    def __repr__(self) -> str:
        return f"<BlockerRecord {self.id!s:.8}>"


class WaitingOnRecord(Base):
    """Something pending from another person, team, or external dependency."""

    __tablename__ = "waiting_on_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    waiting_on_whom: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    expected_by: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="waiting"
    )
    source_provenance: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    def __repr__(self) -> str:
        return f"<WaitingOnRecord {self.id!s:.8} on={self.waiting_on_whom!r}>"

