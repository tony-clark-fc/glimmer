"""Persona asset and classification domain models.

ARCH:PersonaAssetModel
ARCH:PersonaClassificationModel
ARCH:PersonaSelectionEventModel

Managed UX assets, not ad hoc static images.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _genuuid() -> uuid.UUID:
    return uuid.uuid4()


class PersonaAsset(Base):
    """One approved Glimmer image or visual persona asset."""

    __tablename__ = "persona_assets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_path: Mapped[str] = mapped_column(
        String(1024), nullable=False
    )  # storage path or reference
    asset_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # image, avatar, icon
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    # Relationships
    classifications: Mapped[list["PersonaClassification"]] = relationship(
        back_populates="asset", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<PersonaAsset {self.id!s:.8} label={self.label!r}>"


class PersonaClassification(Base):
    """Labeling of a persona asset for UX selection."""

    __tablename__ = "persona_classifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("persona_assets.id", ondelete="CASCADE"),
        nullable=False,
    )
    classification_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # mood, tone, mode, suitability
    classification_value: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # focused, warm, supportive, executive
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    # Relationships
    asset: Mapped["PersonaAsset"] = relationship(
        back_populates="classifications"
    )

    def __repr__(self) -> str:
        return (
            f"<PersonaClassification {self.id!s:.8} "
            f"{self.classification_type}={self.classification_value!r}>"
        )


class PersonaSelectionEvent(Base):
    """Runtime selection of a persona asset for an interaction context."""

    __tablename__ = "persona_selection_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("persona_assets.id", ondelete="SET NULL"),
        nullable=True,
    )
    interaction_context: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )  # briefing, draft, voice_greeting, etc.
    selection_reason: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    selected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    def __repr__(self) -> str:
        return f"<PersonaSelectionEvent {self.id!s:.8}>"



