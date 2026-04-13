"""Primary operator domain model.

ARCH:PrimaryOperatorModel

The operator entity anchors project ownership, connected account
ownership, channel identity, and personalisation context.  MVP assumes
a single operator but preserves an explicit identity so the system is
not built on anonymous local state.
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


class PrimaryOperator(Base):
    """The person using Glimmer.

    In MVP there is exactly one operator.  The entity exists to anchor
    ownership and preferences rather than scattering them across
    anonymous configuration.
    """

    __tablename__ = "primary_operators"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    display_name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    preferred_timezone: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )  # e.g. "Europe/London"
    preferred_working_hours: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )  # human-readable or structured, e.g. "09:00-18:00 Mon-Fri"
    preferred_language: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # e.g. "en-GB"
    tone_preferences: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # free-form tone/style guidance
    channel_preferences: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )  # e.g. {"telegram_enabled": true, "voice_enabled": true}
    summary_preferences: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )  # e.g. {"daily_focus_pack": true, "weekly_review": true}
    escalation_preferences: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )  # e.g. {"interrupt_for_urgent": true, "research_auto_escalate": false}
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    def __repr__(self) -> str:
        return (
            f"<PrimaryOperator {self.id!s:.8} "
            f"name={self.display_name!r}>"
        )

