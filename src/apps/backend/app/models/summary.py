"""Summary, refresh, and lineage domain models.

ARCH:ProjectSummaryModel
ARCH:ProjectMemoryRefresh

Summaries are explicit derived artifacts with lineage,
not magic rewrites of history.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _genuuid() -> uuid.UUID:
    return uuid.uuid4()


class ProjectSummary(Base):
    """Derived artifact: current synthesized understanding of a project.

    Stored as a first-class record with lineage, not regenerated invisibly.
    """

    __tablename__ = "project_summaries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    summary_text: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    source_scope_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )  # what inputs were used to create this summary
    version_marker: Mapped[int] = mapped_column(Integer, default=1)
    confidence_indicator: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    supersedes_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("project_summaries.id", ondelete="SET NULL"),
        nullable=True,
    )  # lineage: which older summary this one replaces
    is_current: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    def __repr__(self) -> str:
        return (
            f"<ProjectSummary {self.id!s:.8} "
            f"project={self.project_id!s:.8} v{self.version_marker}>"
        )


class RefreshEvent(Base):
    """Records a memory refresh cycle — when and what was refreshed."""

    __tablename__ = "refresh_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
    )
    refresh_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # summary_refresh, full_memory_refresh, incremental_update
    triggered_by: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )  # operator, scheduler, connector_sync
    input_scope: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )  # what data range / sources were included
    output_artifact_ids: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )  # IDs of summaries / artifacts produced
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="in_progress"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    def __repr__(self) -> str:
        return (
            f"<RefreshEvent {self.id!s:.8} "
            f"type={self.refresh_type!r} status={self.status!r}>"
        )

