"""Channel-session continuity domain models.

ARCH:ChannelSessionModel
ARCH:TelegramConversationStateModel
ARCH:VoiceSessionStateModel
ARCH:PersonaPageSessionModel

Durable state for Telegram, voice, and web persona-page continuity
without becoming a hidden shadow-memory system.
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


class ChannelSession(Base):
    """An ongoing interaction context over a companion/interaction channel."""

    __tablename__ = "channel_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    operator_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("primary_operators.id", ondelete="SET NULL"),
        nullable=True,
    )  # nullable for backward compat; single-operator MVP
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


class PersonaPageSession(Base):
    """Web persona-page conversation session state.

    ARCH:PersonaPageSessionModel
    ARCH:PersonaPage.ConversationModel
    REQ:GlimmerPersonaPage

    Tracks the lifecycle of a single persona-page conversation.
    Links to ChannelSession as a web-channel subtype.
    """

    __tablename__ = "persona_page_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    channel_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("channel_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active"
    )  # active, paused, confirmed, abandoned
    workspace_mode: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # idea, plan, report, debrief, update
    summary_intent: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # derived or operator-labeled summary of conversation intent
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    messages: Mapped[list["PersonaPageMessage"]] = relationship(
        back_populates="session",
        order_by="PersonaPageMessage.ordering",
        cascade="all, delete-orphan",
    )
    working_state: Mapped[Optional["MindMapWorkingState"]] = relationship(
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<PersonaPageSession {self.id!s:.8} "
            f"status={self.session_status!r}>"
        )


class MindMapWorkingState(Base):
    """Server-side backup of the mind-map working state for a persona-page session.

    ARCH:MindMapWorkingStateModel
    ARCH:PersonaPage.StagedPersistence
    REQ:PersonaPageStagedPersistence

    Holds the serialized candidate nodes and edges for session backup/resumption.
    The primary working state lives in client-side React state. This record
    exists to allow resumption if the operator navigates away without confirming.

    Nothing in the working state reaches the operational database until the
    operator explicitly confirms via the staged-persistence endpoint.
    """

    __tablename__ = "mindmap_working_states"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("persona_page_sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    candidate_nodes: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )  # Serialized list of MindMapCandidateNode data
    candidate_edges: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )  # Serialized list of MindMapCandidateEdge data
    state_version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    session: Mapped["PersonaPageSession"] = relationship(
        back_populates="working_state",
    )

    def __repr__(self) -> str:
        return (
            f"<MindMapWorkingState {self.id!s:.8} "
            f"session={self.session_id!s:.8} v{self.state_version}>"
        )


class PersonaPageMessage(Base):
    """A single message within a persona-page conversation.

    ARCH:PersonaPage.ConversationModel

    Persists chat history for session continuity and audit.
    """

    __tablename__ = "persona_page_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("persona_page_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # user, glimmer
    content: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    ordering: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    workspace_mode: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )
    inference_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )  # latency, model, used_llm, tokens, etc.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    session: Mapped["PersonaPageSession"] = relationship(
        back_populates="messages",
    )

    def __repr__(self) -> str:
        return (
            f"<PersonaPageMessage {self.id!s:.8} "
            f"role={self.role!r} order={self.ordering}>"
        )
