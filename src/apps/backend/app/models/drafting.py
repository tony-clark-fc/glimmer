"""Drafting, briefing, and focus artifact domain models.

ARCH:DraftModel
ARCH:DraftVariantModel
ARCH:BriefingArtifactModel
ARCH:FocusPackModel

These are first-class records, not ad hoc blobs.
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


class Draft(Base):
    """A proposed outgoing response prepared by Glimmer for operator review."""

    __tablename__ = "drafts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    source_message_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )  # FK-free: may point at messages or imported_signals
    source_record_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )
    linked_project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
    )
    linked_stakeholder_ids: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )
    channel_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # email, telegram, etc.
    tone_mode: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # concise, warm, firm, executive
    body_content: Mapped[str] = mapped_column(Text, nullable=False)
    rationale_summary: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    version_number: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="draft"
    )  # draft, reviewed, discarded, sent_by_operator
    intent_label: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    # Relationships
    variants: Mapped[list["DraftVariant"]] = relationship(
        back_populates="draft", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Draft {self.id!s:.8} status={self.status!r}>"


class DraftVariant(Base):
    """Alternate wording/version linked to a common drafting intent."""

    __tablename__ = "draft_variants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    draft_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("drafts.id", ondelete="CASCADE"),
        nullable=False,
    )
    variant_label: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # concise, fuller, firmer, warmer, executive
    body_content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    # Relationships
    draft: Mapped["Draft"] = relationship(back_populates="variants")

    def __repr__(self) -> str:
        return (
            f"<DraftVariant {self.id!s:.8} label={self.variant_label!r}>"
        )


class BriefingArtifact(Base):
    """A generated briefing output used to prepare the operator."""

    __tablename__ = "briefing_artifacts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    linked_project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
    )
    briefing_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # daily_focus, meeting_prep, weekly_review, telegram_summary
    content: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    source_scope_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    def __repr__(self) -> str:
        return (
            f"<BriefingArtifact {self.id!s:.8} "
            f"type={self.briefing_type!r}>"
        )


class FocusPack(Base):
    """Specialized briefing — summarizes what matters now."""

    __tablename__ = "focus_packs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    top_actions: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )
    high_risk_items: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )
    waiting_on_items: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )
    reply_debt_summary: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    calendar_pressure_summary: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    def __repr__(self) -> str:
        return f"<FocusPack {self.id!s:.8}>"

