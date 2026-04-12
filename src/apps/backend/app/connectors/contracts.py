"""Connector contracts — typed DTOs for the connector framework.

ARCH:ConnectorIsolation
ARCH:NormalizationPipeline
ARCH:AccountProvenanceModel
ARCH:ConnectorToIntakeHandoff

These contracts define the data shapes that flow through the connector layer:
- Execution context (resolved account/profile for a connector run)
- Normalized record data (ready for persistence as source-layer entities)
- Sync checkpoints (sync-state tracking per account)
- Intake references (bounded handoff from connectors to orchestration)
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── Connector Execution Context ──────────────────────────────────────


class ConnectorExecutionContext(BaseModel):
    """Resolved execution context for a single connector run.

    Built by the context resolver from a ConnectedAccount + optional
    AccountProfile. This is the provenance-bearing identity that the
    connector uses for authentication and normalization.

    ARCH:ConnectedAccountModel
    ARCH:AccountProfileConnectorSupport
    """

    connected_account_id: uuid.UUID
    provider_type: str
    account_label: str
    account_address: Optional[str] = None
    tenant_context: Optional[str] = None

    # Optional resolved profile
    profile_id: Optional[uuid.UUID] = None
    profile_type: Optional[str] = None
    profile_label: Optional[str] = None

    # Sync state from last run (for incremental fetch)
    sync_metadata: Optional[dict] = None


# ── Normalized Record Data ───────────────────────────────────────────


class NormalizedMessageData(BaseModel):
    """Normalized message payload — ready for Message persistence.

    ARCH:NormalizationPipeline
    """

    source_type: str  # gmail, microsoft_mail
    external_message_id: str
    external_thread_id: Optional[str] = None
    subject: Optional[str] = None
    body_text: Optional[str] = None
    sent_at: Optional[datetime] = None
    received_at: Optional[datetime] = None
    sender_identity: Optional[str] = None
    recipient_identities: Optional[dict] = None
    import_metadata: Optional[dict] = None


class NormalizedThreadData(BaseModel):
    """Normalized thread payload — ready for MessageThread persistence.

    ARCH:NormalizationPipeline
    """

    source_type: str
    external_thread_id: str
    derived_subject: Optional[str] = None
    participant_set: Optional[dict] = None
    last_activity_at: Optional[datetime] = None


class NormalizedEventData(BaseModel):
    """Normalized calendar event payload — ready for CalendarEvent persistence.

    ARCH:NormalizationPipeline
    """

    external_event_id: str
    title: str
    description_summary: Optional[str] = None
    start_time: datetime
    end_time: datetime
    participants: Optional[dict] = None
    location_or_link: Optional[str] = None
    source_calendar: Optional[str] = None


class NormalizedSignalData(BaseModel):
    """Normalized imported signal payload — ready for ImportedSignal persistence.

    ARCH:NormalizationPipeline
    """

    signal_type: str  # manual_paste, telegram_import, voice_transcript
    source_label: Optional[str] = None
    content: str
    raw_metadata: Optional[dict] = None


# ── Sync Checkpoint ──────────────────────────────────────────────────


class SyncCheckpoint(BaseModel):
    """Sync-state checkpoint after a connector run.

    ARCH:ConnectorSyncStateTracking
    """

    connected_account_id: uuid.UUID
    last_sync_at: datetime = Field(default_factory=_utcnow)
    sync_cursor: Optional[dict] = None
    status: str = "success"  # success, partial, failed
    error_summary: Optional[str] = None
    items_fetched: int = 0


# ── Intake Reference ─────────────────────────────────────────────────


class IntakeReference(BaseModel):
    """Bounded reference for connector-to-intake handoff.

    After normalization and persistence, the connector hands off
    references (not raw provider payloads) to the intake boundary.

    ARCH:ConnectorToIntakeHandoff
    ARCH:HandoffPayloadPosture
    """

    source_record_ids: list[uuid.UUID]
    record_type: str  # message, thread, calendar_event, imported_signal
    connected_account_id: uuid.UUID
    provider_type: str
    profile_id: Optional[uuid.UUID] = None
    created_at: datetime = Field(default_factory=_utcnow)


# ── Fetch Result ─────────────────────────────────────────────────────


class FetchResult(BaseModel):
    """Result of a connector fetch operation.

    Contains normalized records ready for persistence plus sync checkpoint.
    """

    messages: list[NormalizedMessageData] = Field(default_factory=list)
    threads: list[NormalizedThreadData] = Field(default_factory=list)
    events: list[NormalizedEventData] = Field(default_factory=list)
    signals: list[NormalizedSignalData] = Field(default_factory=list)
    checkpoint: Optional[SyncCheckpoint] = None

