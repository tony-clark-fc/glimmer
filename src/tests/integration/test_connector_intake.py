"""Connector normalization persist-before-interpretation and intake handoff tests.

TEST:Connector.Normalization.PersistBeforeInterpretation
TEST:Connector.IntakeHandoff.BoundedReferenceFlow
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from app.connectors.contracts import (
    ConnectorExecutionContext,
    FetchResult,
    NormalizedEventData,
    NormalizedMessageData,
    NormalizedSignalData,
    NormalizedThreadData,
)
from app.connectors.intake import IntakeHandoffService
from app.models.source import (
    CalendarEvent,
    ImportedSignal,
    Message,
    MessageThread,
    ConnectedAccount,
)


def _make_account(db_session) -> ConnectedAccount:
    account = ConnectedAccount(
        provider_type="google",
        account_label="test@example.com",
        status="active",
    )
    db_session.add(account)
    db_session.flush()
    return account


def _make_context(account: ConnectedAccount) -> ConnectorExecutionContext:
    return ConnectorExecutionContext(
        connected_account_id=account.id,
        provider_type=account.provider_type,
        account_label=account.account_label,
    )


class TestPersistBeforeInterpretation:
    """TEST:Connector.Normalization.PersistBeforeInterpretation

    Proves source truth exists as a durable layer before
    classification/planning begins.
    """

    def test_messages_persisted_before_handoff(self, db_session) -> None:
        """Normalized messages are persisted as Message records."""
        account = _make_account(db_session)
        ctx = _make_context(account)

        result = FetchResult(
            messages=[
                NormalizedMessageData(
                    source_type="gmail",
                    external_message_id="msg_001",
                    external_thread_id="thread_001",
                    subject="Test Subject",
                    body_text="Test body",
                    sender_identity="alice@example.com",
                ),
            ]
        )

        service = IntakeHandoffService(db_session)
        refs = service.persist_and_handoff(ctx, result)

        # Records are persisted in DB
        messages = db_session.execute(
            select(Message).where(Message.connected_account_id == account.id)
        ).scalars().all()
        assert len(messages) == 1
        assert messages[0].external_message_id == "msg_001"
        assert messages[0].subject == "Test Subject"

    def test_threads_persisted_before_handoff(self, db_session) -> None:
        account = _make_account(db_session)
        ctx = _make_context(account)

        result = FetchResult(
            threads=[
                NormalizedThreadData(
                    source_type="gmail",
                    external_thread_id="thread_001",
                    derived_subject="Test Thread",
                ),
            ]
        )

        service = IntakeHandoffService(db_session)
        refs = service.persist_and_handoff(ctx, result)

        threads = db_session.execute(
            select(MessageThread).where(
                MessageThread.connected_account_id == account.id
            )
        ).scalars().all()
        assert len(threads) == 1
        assert threads[0].external_thread_id == "thread_001"

    def test_events_persisted_before_handoff(self, db_session) -> None:
        account = _make_account(db_session)
        ctx = _make_context(account)

        result = FetchResult(
            events=[
                NormalizedEventData(
                    external_event_id="evt_001",
                    title="Test Meeting",
                    start_time=datetime(2026, 4, 14, 10, 0, tzinfo=timezone.utc),
                    end_time=datetime(2026, 4, 14, 11, 0, tzinfo=timezone.utc),
                    source_calendar="Work Calendar",
                ),
            ]
        )

        service = IntakeHandoffService(db_session)
        refs = service.persist_and_handoff(ctx, result)

        events = db_session.execute(
            select(CalendarEvent).where(
                CalendarEvent.connected_account_id == account.id
            )
        ).scalars().all()
        assert len(events) == 1
        assert events[0].title == "Test Meeting"
        assert events[0].source_calendar == "Work Calendar"

    def test_signals_persisted_before_handoff(self, db_session) -> None:
        account = _make_account(db_session)
        ctx = _make_context(account)

        result = FetchResult(
            signals=[
                NormalizedSignalData(
                    signal_type="manual_paste",
                    source_label="WhatsApp",
                    content="Manual import test",
                ),
            ]
        )

        service = IntakeHandoffService(db_session)
        refs = service.persist_and_handoff(ctx, result)

        signals = db_session.execute(
            select(ImportedSignal).where(
                ImportedSignal.connected_account_id == account.id
            )
        ).scalars().all()
        assert len(signals) == 1
        assert signals[0].content == "Manual import test"

    def test_provenance_preserved_through_persistence(self, db_session) -> None:
        """Source records retain account provenance after persistence."""
        account = _make_account(db_session)
        ctx = _make_context(account)

        result = FetchResult(
            messages=[
                NormalizedMessageData(
                    source_type="gmail",
                    external_message_id="prov_msg",
                    sender_identity="sender@example.com",
                ),
            ]
        )

        service = IntakeHandoffService(db_session)
        service.persist_and_handoff(ctx, result)

        msg = db_session.execute(
            select(Message).where(Message.external_message_id == "prov_msg")
        ).scalar_one()
        assert msg.connected_account_id == account.id
        assert msg.source_type == "gmail"
        assert msg.sender_identity == "sender@example.com"


class TestIntakeHandoffBoundedReference:
    """TEST:Connector.IntakeHandoff.BoundedReferenceFlow

    Proves integration code hands off cleanly without becoming
    an orchestration shortcut. References contain IDs, not payloads.
    """

    def test_handoff_returns_references_with_record_ids(self, db_session) -> None:
        account = _make_account(db_session)
        ctx = _make_context(account)

        result = FetchResult(
            messages=[
                NormalizedMessageData(
                    source_type="gmail",
                    external_message_id="ref_msg_001",
                ),
                NormalizedMessageData(
                    source_type="gmail",
                    external_message_id="ref_msg_002",
                ),
            ]
        )

        service = IntakeHandoffService(db_session)
        refs = service.persist_and_handoff(ctx, result)

        assert len(refs) == 1  # One reference per record type
        msg_ref = refs[0]
        assert msg_ref.record_type == "message"
        assert len(msg_ref.source_record_ids) == 2
        # IDs are real UUIDs from persisted records
        for rid in msg_ref.source_record_ids:
            assert isinstance(rid, uuid.UUID)

    def test_handoff_references_include_provenance(self, db_session) -> None:
        account = _make_account(db_session)
        ctx = _make_context(account)

        result = FetchResult(
            messages=[
                NormalizedMessageData(
                    source_type="gmail",
                    external_message_id="ref_prov",
                ),
            ]
        )

        service = IntakeHandoffService(db_session)
        refs = service.persist_and_handoff(ctx, result)

        ref = refs[0]
        assert ref.connected_account_id == account.id
        assert ref.provider_type == "google"

    def test_handoff_returns_separate_refs_per_record_type(self, db_session) -> None:
        """Mixed record types get separate intake references."""
        account = _make_account(db_session)
        ctx = _make_context(account)

        result = FetchResult(
            messages=[
                NormalizedMessageData(
                    source_type="gmail",
                    external_message_id="mix_msg",
                ),
            ],
            events=[
                NormalizedEventData(
                    external_event_id="mix_evt",
                    title="Mixed",
                    start_time=datetime(2026, 4, 14, 10, 0, tzinfo=timezone.utc),
                    end_time=datetime(2026, 4, 14, 11, 0, tzinfo=timezone.utc),
                ),
            ],
        )

        service = IntakeHandoffService(db_session)
        refs = service.persist_and_handoff(ctx, result)

        types = {r.record_type for r in refs}
        assert "message" in types
        assert "calendar_event" in types

    def test_empty_fetch_returns_no_references(self, db_session) -> None:
        account = _make_account(db_session)
        ctx = _make_context(account)

        result = FetchResult()
        service = IntakeHandoffService(db_session)
        refs = service.persist_and_handoff(ctx, result)

        assert refs == []

