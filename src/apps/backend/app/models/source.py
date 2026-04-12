"""Connected account and source-layer domain models.

ARCH:ConnectedAccountModel
ARCH:AccountProfileModel
ARCH:AccountProvenanceConcept
ARCH:MessageModel
ARCH:MessageThreadModel
ARCH:CalendarEventModel
ARCH:ImportedSignalModel

These entities form the provenance-bearing source layer that connectors
will write into and that the interpretation layer will read from.
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


# ── Connected Account Layer ──────────────────────────────────────────


class ConnectedAccount(Base):
    """One connected external communication or calendar account."""

    __tablename__ = "connected_accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    provider_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # google, google_workspace, microsoft_365
    account_label: Mapped[str] = mapped_column(String(255), nullable=False)
    account_address: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True
    )  # mailbox / principal address
    tenant_context: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )  # MS tenant, Google workspace domain, etc.
    purpose_label: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active"
    )
    auth_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )  # non-secret auth metadata (scopes, consent state, etc.)
    sync_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )  # last sync cursors, watermarks
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    # Relationships
    profiles: Mapped[list["AccountProfile"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )
    messages: Mapped[list["Message"]] = relationship(
        back_populates="connected_account", cascade="all, delete-orphan"
    )
    threads: Mapped[list["MessageThread"]] = relationship(
        back_populates="connected_account", cascade="all, delete-orphan"
    )
    calendar_events: Mapped[list["CalendarEvent"]] = relationship(
        back_populates="connected_account", cascade="all, delete-orphan"
    )
    imported_signals: Mapped[list["ImportedSignal"]] = relationship(
        back_populates="connected_account", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<ConnectedAccount {self.id!s:.8} "
            f"{self.provider_type}:{self.account_label!r}>"
        )


class AccountProfile(Base):
    """A specific logical profile under a connected account.

    Examples: mail profile, calendar profile, sub-calendar, inbox context.
    """

    __tablename__ = "account_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("connected_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    profile_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # mail, calendar, sub_calendar
    profile_label: Mapped[str] = mapped_column(String(255), nullable=False)
    profile_address: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True
    )
    profile_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    # Relationships
    account: Mapped["ConnectedAccount"] = relationship(
        back_populates="profiles"
    )

    def __repr__(self) -> str:
        return (
            f"<AccountProfile {self.id!s:.8} "
            f"{self.profile_type}:{self.profile_label!r}>"
        )


# ── Source-Layer Records ─────────────────────────────────────────────


class MessageThread(Base):
    """A grouped communication thread where threading semantics exist."""

    __tablename__ = "message_threads"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    connected_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("connected_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # gmail, microsoft_mail, etc.
    external_thread_id: Mapped[str] = mapped_column(
        String(512), nullable=False
    )
    derived_subject: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True
    )
    participant_set: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    # Relationships
    connected_account: Mapped["ConnectedAccount"] = relationship(
        back_populates="threads"
    )
    messages: Mapped[list["Message"]] = relationship(
        back_populates="thread"
    )

    def __repr__(self) -> str:
        return f"<MessageThread {self.id!s:.8} ext={self.external_thread_id!r}>"


class Message(Base):
    """Normalized internal representation of an imported communication unit."""

    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    connected_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("connected_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    account_profile_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("account_profiles.id", ondelete="SET NULL"),
        nullable=True,
    )
    thread_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("message_threads.id", ondelete="SET NULL"),
        nullable=True,
    )
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    external_message_id: Mapped[str] = mapped_column(
        String(512), nullable=False
    )
    external_thread_id: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True
    )
    subject: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    body_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    received_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sender_identity: Mapped[Optional[str]] = mapped_column(
        String(512), nullable=True
    )
    recipient_identities: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )
    import_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    # Relationships
    connected_account: Mapped["ConnectedAccount"] = relationship(
        back_populates="messages"
    )
    thread: Mapped[Optional["MessageThread"]] = relationship(
        back_populates="messages"
    )

    def __repr__(self) -> str:
        return f"<Message {self.id!s:.8} ext={self.external_message_id!r}>"


class CalendarEvent(Base):
    """Normalized internal representation of an imported calendar item."""

    __tablename__ = "calendar_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    connected_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("connected_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    external_event_id: Mapped[str] = mapped_column(
        String(512), nullable=False
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description_summary: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    participants: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )
    location_or_link: Mapped[Optional[str]] = mapped_column(
        String(1024), nullable=True
    )
    source_calendar: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    # Relationships
    connected_account: Mapped["ConnectedAccount"] = relationship(
        back_populates="calendar_events"
    )

    def __repr__(self) -> str:
        return f"<CalendarEvent {self.id!s:.8} title={self.title!r}>"


class ImportedSignal(Base):
    """Raw or semi-structured imported input that may not fit message/event.

    Examples: manual paste, Telegram transcript, voice transcript segment.
    """

    __tablename__ = "imported_signals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_genuuid
    )
    connected_account_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("connected_accounts.id", ondelete="SET NULL"),
        nullable=True,
    )
    signal_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # manual_paste, telegram_import, voice_transcript
    source_label: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    raw_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True
    )
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    # Relationships
    connected_account: Mapped[Optional["ConnectedAccount"]] = relationship(
        back_populates="imported_signals"
    )

    def __repr__(self) -> str:
        return f"<ImportedSignal {self.id!s:.8} type={self.signal_type!r}>"


