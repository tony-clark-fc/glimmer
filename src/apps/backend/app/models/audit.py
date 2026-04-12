"""Audit and trace domain models.

ARCH:AuditAndTraceLayer

Meaningful state mutation creates traceable records —
not just generic logs.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _genuuid() -> uuid.UUID:
    return uuid.uuid4()


class AuditRecord(Base):
    """Durable audit/trace record for meaningful memory evolution.

    Records who/what changed what entity, when, and why.
    """

    __tablename__ = "audit_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    entity_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # project, work_item, stakeholder, draft, etc.
    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    action: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # created, updated, accepted, rejected, promoted, archived, deleted
    actor: Mapped[str] = mapped_column(
        String(100), nullable=False, default="operator"
    )  # operator, system, graph_node_name
    change_summary: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    previous_state: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )
    new_state: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )
    context_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )  # additional context: session_id, graph_run_id, etc.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    def __repr__(self) -> str:
        return (
            f"<AuditRecord {self.id!s:.8} "
            f"{self.action} {self.entity_type}:{self.entity_id!s:.8}>"
        )

