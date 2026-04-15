"""Connector-to-intake bounded handoff service.

ARCH:ConnectorToIntakeHandoff
ARCH:HandoffPayloadPosture
ARCH:NormalizationOutputBoundary

This module persists normalized source records and creates bounded
intake references for downstream orchestration. This is the critical
boundary between connector code and assistant-core code.

Connectors produce normalized data. This service persists it as source-layer
entities and returns references that downstream graphs can use to load
persisted records, not raw provider payloads.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy.orm import Session

from app.connectors.contracts import (
    ConnectorExecutionContext,
    FetchResult,
    IntakeReference,
    NormalizedEventData,
    NormalizedMessageData,
    NormalizedSignalData,
    NormalizedThreadData,
)
from app.models.source import (
    CalendarEvent,
    ImportedSignal,
    Message,
    MessageThread,
)

logger = logging.getLogger(__name__)


# ── Dispatch Result ──────────────────────────────────────────────────


@dataclass
class IntakeDispatchOutcome:
    """Result of dispatching a single IntakeReference to the intake graph."""

    reference: IntakeReference
    success: bool = False
    triage_classification_ids: list[uuid.UUID] = field(default_factory=list)
    triage_extraction_ids: list[uuid.UUID] = field(default_factory=list)
    triage_needs_review: bool = False
    triage_review_reasons: list[str] = field(default_factory=list)
    triage_records_processed: int = 0
    error: Optional[str] = None


@dataclass
class ConnectorDispatchResult:
    """Aggregate result of persisting and dispatching through the intake graph.

    ARCH:ConnectorToIntakeHandoff
    """

    references: list[IntakeReference] = field(default_factory=list)
    outcomes: list[IntakeDispatchOutcome] = field(default_factory=list)
    total_dispatched: int = 0
    total_succeeded: int = 0
    total_failed: int = 0
    needs_review: bool = False
    review_reasons: list[str] = field(default_factory=list)


# ── Dispatch Function ────────────────────────────────────────────────


def dispatch_to_intake_graph(
    references: list[IntakeReference],
) -> ConnectorDispatchResult:
    """Dispatch IntakeReferences to the intake graph for triage.

    ARCH:ConnectorToIntakeHandoff
    ARCH:IntakeGraph
    TEST:Connector.IntakeDispatch.ReferencesInvokeIntakeGraph

    For each IntakeReference, builds an IntakeState and invokes the
    compiled intake graph.  Errors on one reference do not block others.

    The intake graph handles its own DB session for triage work
    (triage_handoff creates a session internally), so this function
    does not need a session parameter.
    """
    from app.graphs.intake import get_intake_graph

    result = ConnectorDispatchResult(references=list(references))

    if not references:
        return result

    graph = get_intake_graph()

    for ref in references:
        outcome = IntakeDispatchOutcome(reference=ref)
        result.total_dispatched += 1

        try:
            # Build IntakeState from the reference
            intake_state = _reference_to_intake_state(ref)

            # Invoke the intake graph
            graph_output = graph.invoke(intake_state)

            # Extract triage results from graph output
            outcome.success = True
            outcome.triage_classification_ids = graph_output.get(
                "triage_classification_ids", []
            )
            outcome.triage_extraction_ids = graph_output.get(
                "triage_extraction_ids", []
            )
            outcome.triage_needs_review = graph_output.get(
                "triage_needs_review", False
            )
            outcome.triage_review_reasons = graph_output.get(
                "triage_review_reasons", []
            )
            outcome.triage_records_processed = graph_output.get(
                "triage_records_processed", 0
            )

            if outcome.triage_needs_review:
                result.needs_review = True
                result.review_reasons.extend(outcome.triage_review_reasons)

            result.total_succeeded += 1

            logger.info(
                "dispatch_to_intake_graph: ref=%s type=%s processed=%d review=%s",
                ref.record_type,
                ref.provider_type,
                outcome.triage_records_processed,
                outcome.triage_needs_review,
            )

        except Exception as exc:
            outcome.error = str(exc)
            result.total_failed += 1
            logger.warning(
                "dispatch_to_intake_graph: failed for ref type=%s — %s",
                ref.record_type,
                exc,
            )

        result.outcomes.append(outcome)

    return result


def _reference_to_intake_state(ref: IntakeReference) -> dict:
    """Convert an IntakeReference to an IntakeState dict for graph invocation.

    ARCH:HandoffPayloadPosture — references carry IDs, not payloads.
    """
    return {
        "source_record_ids": ref.source_record_ids,
        "record_type": ref.record_type,
        "connected_account_id": ref.connected_account_id,
        "provider_type": ref.provider_type,
        "profile_id": ref.profile_id,
        "channel": "api",
    }


class IntakeHandoffService:
    """Persists normalized records and creates bounded intake references.

    This service is the final step in the connector pipeline:
    1. Connector fetches and normalizes → FetchResult
    2. IntakeHandoffService persists source records → DB entities
    3. IntakeHandoffService returns IntakeReference → bounded handoff
    4. (Optional) dispatch_to_intake_graph() invokes the intake graph

    ARCH:NormalizationOutputBoundary
    ARCH:ConnectorToIntakeHandoff
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def persist_and_handoff(
        self,
        context: ConnectorExecutionContext,
        result: FetchResult,
    ) -> list[IntakeReference]:
        """Persist normalized records and return intake references.

        Source records are persisted BEFORE any interpretation or
        classification can begin. This is a load-bearing design rule.

        ARCH:NormalizationOutputBoundary
        """
        references: list[IntakeReference] = []

        # Persist threads first (messages may reference them)
        if result.threads:
            thread_ids = self._persist_threads(context, result.threads)
            if thread_ids:
                references.append(
                    IntakeReference(
                        source_record_ids=thread_ids,
                        record_type="thread",
                        connected_account_id=context.connected_account_id,
                        provider_type=context.provider_type,
                        profile_id=context.profile_id,
                    )
                )

        # Persist messages
        if result.messages:
            msg_ids = self._persist_messages(context, result.messages)
            if msg_ids:
                references.append(
                    IntakeReference(
                        source_record_ids=msg_ids,
                        record_type="message",
                        connected_account_id=context.connected_account_id,
                        provider_type=context.provider_type,
                        profile_id=context.profile_id,
                    )
                )

        # Persist calendar events
        if result.events:
            event_ids = self._persist_events(context, result.events)
            if event_ids:
                references.append(
                    IntakeReference(
                        source_record_ids=event_ids,
                        record_type="calendar_event",
                        connected_account_id=context.connected_account_id,
                        provider_type=context.provider_type,
                        profile_id=context.profile_id,
                    )
                )

        # Persist imported signals
        if result.signals:
            signal_ids = self._persist_signals(context, result.signals)
            if signal_ids:
                references.append(
                    IntakeReference(
                        source_record_ids=signal_ids,
                        record_type="imported_signal",
                        connected_account_id=context.connected_account_id,
                        provider_type=context.provider_type,
                        profile_id=context.profile_id,
                    )
                )

        self._session.flush()
        return references

    def persist_and_dispatch(
        self,
        context: ConnectorExecutionContext,
        result: FetchResult,
    ) -> ConnectorDispatchResult:
        """Persist normalized records and dispatch through the intake graph.

        ARCH:ConnectorToIntakeHandoff
        ARCH:NormalizationOutputBoundary
        TEST:Connector.IntakeDispatch.FullPipelineConnectorToTriage

        Combines persist_and_handoff() with dispatch_to_intake_graph()
        into a single convenience call.  The session is flushed (not
        committed) after persistence — the caller controls the commit
        boundary.

        The intake graph's triage_handoff node opens its own DB session
        so the triage work happens in a separate transaction.  This means
        the caller MUST commit the persistence session before calling this
        method if the triage pipeline needs to see the persisted records.
        """
        self._session.flush()
        references = self.persist_and_handoff(context, result)
        self._session.commit()  # Commit so triage_handoff can see persisted records

        dispatch_result = dispatch_to_intake_graph(references)
        return dispatch_result

    def _persist_threads(
        self,
        context: ConnectorExecutionContext,
        threads: list[NormalizedThreadData],
    ) -> list[uuid.UUID]:
        """Persist normalized thread records."""
        ids: list[uuid.UUID] = []
        for thread_data in threads:
            thread = MessageThread(
                connected_account_id=context.connected_account_id,
                source_type=thread_data.source_type,
                external_thread_id=thread_data.external_thread_id,
                derived_subject=thread_data.derived_subject,
                participant_set=thread_data.participant_set,
                last_activity_at=thread_data.last_activity_at,
            )
            self._session.add(thread)
            self._session.flush()
            ids.append(thread.id)
        return ids

    def _persist_messages(
        self,
        context: ConnectorExecutionContext,
        messages: list[NormalizedMessageData],
    ) -> list[uuid.UUID]:
        """Persist normalized message records."""
        ids: list[uuid.UUID] = []
        for msg_data in messages:
            message = Message(
                connected_account_id=context.connected_account_id,
                account_profile_id=context.profile_id,
                source_type=msg_data.source_type,
                external_message_id=msg_data.external_message_id,
                external_thread_id=msg_data.external_thread_id,
                subject=msg_data.subject,
                body_text=msg_data.body_text,
                sent_at=msg_data.sent_at,
                received_at=msg_data.received_at,
                sender_identity=msg_data.sender_identity,
                recipient_identities=msg_data.recipient_identities,
                import_metadata=msg_data.import_metadata,
            )
            self._session.add(message)
            self._session.flush()
            ids.append(message.id)
        return ids

    def _persist_events(
        self,
        context: ConnectorExecutionContext,
        events: list[NormalizedEventData],
    ) -> list[uuid.UUID]:
        """Persist normalized calendar event records."""
        ids: list[uuid.UUID] = []
        for event_data in events:
            event = CalendarEvent(
                connected_account_id=context.connected_account_id,
                external_event_id=event_data.external_event_id,
                title=event_data.title,
                description_summary=event_data.description_summary,
                start_time=event_data.start_time,
                end_time=event_data.end_time,
                participants=event_data.participants,
                location_or_link=event_data.location_or_link,
                source_calendar=event_data.source_calendar,
            )
            self._session.add(event)
            self._session.flush()
            ids.append(event.id)
        return ids

    def _persist_signals(
        self,
        context: ConnectorExecutionContext,
        signals: list[NormalizedSignalData],
    ) -> list[uuid.UUID]:
        """Persist normalized imported signal records."""
        ids: list[uuid.UUID] = []
        for signal_data in signals:
            signal = ImportedSignal(
                connected_account_id=context.connected_account_id,
                signal_type=signal_data.signal_type,
                source_label=signal_data.source_label,
                content=signal_data.content,
                raw_metadata=signal_data.raw_metadata,
            )
            self._session.add(signal)
            self._session.flush()
            ids.append(signal.id)
        return ids

