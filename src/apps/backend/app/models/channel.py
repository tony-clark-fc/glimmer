"""Channel-session continuity domain models.

ARCH:ChannelSessionModel
ARCH:TelegramConversationStateModel
ARCH:VoiceSessionStateModel

Durable state for Telegram and voice continuity without becoming
a hidden shadow-memory system.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _genuuid() -> uuid.UUID:
    return uuid.uuid4()


class ChannelSession(Base):
    """An ongoing interaction context over a companion/interaction channel."""

    __tablename__ = "channel_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    channel_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # telegram, voice, web
    channel_identity: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )  # chat_id, session_id, etc.
    session_state: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active"
    )
    last_interaction_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    linked_summary_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )  # optional link to a conversation summary
    session_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    def __repr__(self) -> str:
        return (
            f"<ChannelSession {self.id!s:.8} "
            f"type={self.channel_type!r} state={self.session_state!r}>"
        )


class TelegramConversationState(Base):
    """Telegram-specific channel-session extension.

    Holds channel-local state: pending clarification, current topic,
    last referenced project, temporary reply mode.
    """

    __tablename__ = "telegram_conversation_states"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    channel_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("channel_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    telegram_chat_id: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    current_topic: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    last_referenced_project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="SET NULL"),
        nullable=True,
    )
    pending_clarification: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    temporary_reply_mode: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )
    state_data: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    def __repr__(self) -> str:
        return (
            f"<TelegramConversationState {self.id!s:.8} "
            f"chat={self.telegram_chat_id!r}>"
        )


class VoiceSessionState(Base):
    """Active or recent voice interaction state.

    Supports transcript continuity, summary continuity,
    action extraction lineage, and session recovery.
    """

    __tablename__ = "voice_session_states"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    channel_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("channel_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    transcript_content: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    summary_content: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    extracted_action_ids: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )
    session_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="in_progress"
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    state_data: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )

    def __repr__(self) -> str:
        return (
            f"<VoiceSessionState {self.id!s:.8} "
            f"status={self.session_status!r}>"
        )

