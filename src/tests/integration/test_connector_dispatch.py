"""Connector-to-intake dispatch integration tests.

TEST:Connector.IntakeDispatch.ReferencesInvokeIntakeGraph
TEST:Connector.IntakeDispatch.FullPipelineConnectorToTriage
TEST:Connector.IntakeDispatch.GracefulDegradationOnError
TEST:Release.Connector.ConnectorToTriageChainWorks

Proves the final wiring gap: connector persistence → intake graph
invocation → triage pipeline → classification + extraction.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import select, text

from app.connectors.contracts import (
    ConnectorExecutionContext,
    FetchResult,
    IntakeReference,
    NormalizedEventData,
    NormalizedMessageData,
    NormalizedSignalData,
)
from app.connectors.intake import (
    ConnectorDispatchResult,
    IntakeHandoffService,
    _reference_to_intake_state,
    dispatch_to_intake_graph,
)
from app.db import get_session
from app.models.source import (
    CalendarEvent,
    ConnectedAccount,
    ImportedSignal,
    Message,
)
from app.models.portfolio import Project


# ── Helpers ──────────────────────────────────────────────────────────


def _make_account_live(session) -> ConnectedAccount:
    """Create a ConnectedAccount using a live session (not transactional test session)."""
    account = ConnectedAccount(
        provider_type="google",
        account_label="dispatch-test@example.com",
        status="active",
    )
    session.add(account)
    session.flush()
    return account


def _make_account(db_session) -> ConnectedAccount:
    account = ConnectedAccount(
        provider_type="google",
        account_label="dispatch-test@example.com",
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


def _make_project_live(session, name: str = "Alpha Project") -> Project:
    project = Project(name=name, status="active")
    session.add(project)
    session.flush()
    return project


# ── Cleanup for live-DB full-pipeline tests ──────────────────────────

_CLEANUP_TABLES = [
    "message_classifications",
    "extracted_actions",
    "extracted_decisions",
    "extracted_deadline_signals",
    "messages",
    "calendar_events",
    "imported_signals",
    "message_threads",
    "projects",
    "connected_accounts",
    "audit_records",
]


@pytest.fixture()
def live_session():
    """Provide a live DB session for full-pipeline tests.

    triage_handoff creates its own session via get_session(), so
    full-pipeline tests must use the same DB.  We clean up afterward.
    """
    session = get_session()
    # Pre-clean
    for table in _CLEANUP_TABLES:
        session.execute(text(f"DELETE FROM {table}"))
    session.commit()
    yield session
    # Post-clean
    for table in _CLEANUP_TABLES:
        session.execute(text(f"DELETE FROM {table}"))
    session.commit()
    session.close()


# ── Reference-to-State Mapping Tests ─────────────────────────────────


class TestReferenceToIntakeState:
    """TEST:Connector.IntakeDispatch.ReferenceMapping"""

    def test_message_reference_maps_to_state(self) -> None:
        """IntakeReference fields map correctly to IntakeState dict."""
        account_id = uuid.uuid4()
        record_ids = [uuid.uuid4(), uuid.uuid4()]

        ref = IntakeReference(
            source_record_ids=record_ids,
            record_type="message",
            connected_account_id=account_id,
            provider_type="google",
            profile_id=None,
        )

        state = _reference_to_intake_state(ref)

        assert state["source_record_ids"] == record_ids
        assert state["record_type"] == "message"
        assert state["connected_account_id"] == account_id
        assert state["provider_type"] == "google"
        assert state["profile_id"] is None
        assert state["channel"] == "api"

    def test_event_reference_preserves_type(self) -> None:
        """Calendar event reference preserves record_type through mapping."""
        ref = IntakeReference(
            source_record_ids=[uuid.uuid4()],
            record_type="calendar_event",
            connected_account_id=uuid.uuid4(),
            provider_type="microsoft",
        )

        state = _reference_to_intake_state(ref)
        assert state["record_type"] == "calendar_event"
        assert state["provider_type"] == "microsoft"

    def test_profile_id_preserved_when_present(self) -> None:
        """Profile ID carried through to state when present."""
        profile_id = uuid.uuid4()
        ref = IntakeReference(
            source_record_ids=[uuid.uuid4()],
            record_type="message",
            connected_account_id=uuid.uuid4(),
            provider_type="google",
            profile_id=profile_id,
        )

        state = _reference_to_intake_state(ref)
        assert state["profile_id"] == profile_id


# ── Dispatch Function Tests (mocked graph) ───────────────────────────


class TestDispatchToIntakeGraph:
    """TEST:Connector.IntakeDispatch.ReferencesInvokeIntakeGraph"""

    def test_empty_references_returns_empty_result(self) -> None:
        """Empty reference list returns clean empty result."""
        result = dispatch_to_intake_graph([])

        assert isinstance(result, ConnectorDispatchResult)
        assert result.total_dispatched == 0
        assert result.total_succeeded == 0
        assert result.total_failed == 0
        assert result.outcomes == []
        assert not result.needs_review

    def test_dispatch_invokes_graph_per_reference(self) -> None:
        """Each reference triggers one graph invocation."""
        refs = [
            IntakeReference(
                source_record_ids=[uuid.uuid4()],
                record_type="message",
                connected_account_id=uuid.uuid4(),
                provider_type="google",
            ),
            IntakeReference(
                source_record_ids=[uuid.uuid4()],
                record_type="calendar_event",
                connected_account_id=uuid.uuid4(),
                provider_type="microsoft",
            ),
        ]

        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {
            "current_step": "triage_handoff_complete",
            "triage_classification_ids": [],
            "triage_extraction_ids": [],
            "triage_needs_review": False,
            "triage_review_reasons": [],
            "triage_records_processed": 1,
        }

        with patch(
            "app.graphs.intake.get_intake_graph", return_value=mock_graph
        ):
            result = dispatch_to_intake_graph(refs)

        assert result.total_dispatched == 2
        assert result.total_succeeded == 2
        assert result.total_failed == 0
        assert mock_graph.invoke.call_count == 2

    def test_dispatch_captures_triage_results(self) -> None:
        """Triage classification IDs flow from graph output to dispatch result."""
        cls_id = uuid.uuid4()
        ref = IntakeReference(
            source_record_ids=[uuid.uuid4()],
            record_type="message",
            connected_account_id=uuid.uuid4(),
            provider_type="google",
        )

        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {
            "current_step": "triage_handoff_complete",
            "triage_classification_ids": [cls_id],
            "triage_extraction_ids": [],
            "triage_needs_review": True,
            "triage_review_reasons": ["Low confidence"],
            "triage_records_processed": 1,
        }

        with patch(
            "app.graphs.intake.get_intake_graph", return_value=mock_graph
        ):
            result = dispatch_to_intake_graph([ref])

        assert result.total_succeeded == 1
        outcome = result.outcomes[0]
        assert outcome.success is True
        assert outcome.triage_classification_ids == [cls_id]
        assert outcome.triage_needs_review is True
        assert result.needs_review is True
        assert "Low confidence" in result.review_reasons

    def test_dispatch_handles_graph_error_gracefully(self) -> None:
        """If the graph raises, the dispatch records the error and continues."""
        refs = [
            IntakeReference(
                source_record_ids=[uuid.uuid4()],
                record_type="message",
                connected_account_id=uuid.uuid4(),
                provider_type="google",
            ),
            IntakeReference(
                source_record_ids=[uuid.uuid4()],
                record_type="message",
                connected_account_id=uuid.uuid4(),
                provider_type="google",
            ),
        ]

        mock_graph = MagicMock()
        mock_graph.invoke.side_effect = [
            RuntimeError("DB connection lost"),
            {
                "current_step": "triage_handoff_complete",
                "triage_records_processed": 1,
            },
        ]

        with patch(
            "app.graphs.intake.get_intake_graph", return_value=mock_graph
        ):
            result = dispatch_to_intake_graph(refs)

        assert result.total_dispatched == 2
        assert result.total_failed == 1
        assert result.total_succeeded == 1
        # First outcome failed
        assert result.outcomes[0].success is False
        assert "DB connection lost" in result.outcomes[0].error
        # Second outcome succeeded
        assert result.outcomes[1].success is True

    def test_dispatch_records_processed_count(self) -> None:
        """Records processed count captured from graph output."""
        ref = IntakeReference(
            source_record_ids=[uuid.uuid4(), uuid.uuid4(), uuid.uuid4()],
            record_type="message",
            connected_account_id=uuid.uuid4(),
            provider_type="google",
        )

        mock_graph = MagicMock()
        mock_graph.invoke.return_value = {
            "current_step": "triage_handoff_complete",
            "triage_records_processed": 3,
        }

        with patch(
            "app.graphs.intake.get_intake_graph", return_value=mock_graph
        ):
            result = dispatch_to_intake_graph([ref])

        assert result.outcomes[0].triage_records_processed == 3


# ── Full Pipeline Integration Tests (live DB) ────────────────────────


class TestFullPipelineConnectorToTriage:
    """TEST:Connector.IntakeDispatch.FullPipelineConnectorToTriage

    End-to-end: persist normalized message → dispatch to intake graph →
    triage classifies and extracts.  Uses live DB session because
    triage_handoff creates its own session via get_session().
    """

    def test_message_persisted_and_classified(self, live_session) -> None:
        """Connector message flows through persist → graph → triage classification."""
        account = _make_account_live(live_session)
        _make_project_live(live_session, "Beta Migration")
        live_session.commit()

        ctx = _make_context(account)
        fetch = FetchResult(
            messages=[
                NormalizedMessageData(
                    source_type="gmail",
                    external_message_id="dispatch_msg_001",
                    subject="Beta Migration timeline update",
                    body_text="The PostgreSQL 17 migration needs another week.",
                    sender_identity="dev@example.com",
                ),
            ]
        )

        service = IntakeHandoffService(live_session)
        dispatch_result = service.persist_and_dispatch(ctx, fetch)

        # Persistence happened
        msgs = live_session.execute(
            select(Message).where(Message.connected_account_id == account.id)
        ).scalars().all()
        assert len(msgs) == 1
        assert msgs[0].subject == "Beta Migration timeline update"

        # Graph invoked and succeeded
        assert dispatch_result.total_dispatched == 1
        assert dispatch_result.total_succeeded == 1
        assert dispatch_result.total_failed == 0

        # Triage produced a classification (deterministic path with LLM disabled)
        outcome = dispatch_result.outcomes[0]
        assert outcome.success is True
        assert outcome.triage_records_processed == 1

    def test_calendar_event_persisted_and_dispatched(self, live_session) -> None:
        """Calendar event flows through the full pipeline."""
        account = _make_account_live(live_session)
        live_session.commit()

        ctx = _make_context(account)
        fetch = FetchResult(
            events=[
                NormalizedEventData(
                    external_event_id="dispatch_evt_001",
                    title="Sprint Planning",
                    start_time=datetime(2026, 4, 15, 10, 0, tzinfo=timezone.utc),
                    end_time=datetime(2026, 4, 15, 11, 0, tzinfo=timezone.utc),
                    source_calendar="Work",
                ),
            ]
        )

        service = IntakeHandoffService(live_session)
        dispatch_result = service.persist_and_dispatch(ctx, fetch)

        events = live_session.execute(
            select(CalendarEvent).where(
                CalendarEvent.connected_account_id == account.id
            )
        ).scalars().all()
        assert len(events) == 1

        assert dispatch_result.total_dispatched == 1
        assert dispatch_result.total_succeeded == 1
        outcome = dispatch_result.outcomes[0]
        assert outcome.success is True

    def test_imported_signal_persisted_and_dispatched(self, live_session) -> None:
        """Imported signal flows through the full pipeline."""
        account = _make_account_live(live_session)
        live_session.commit()

        ctx = _make_context(account)
        fetch = FetchResult(
            signals=[
                NormalizedSignalData(
                    signal_type="manual_paste",
                    source_label="Slack",
                    content="Important update from Slack channel.",
                ),
            ]
        )

        service = IntakeHandoffService(live_session)
        dispatch_result = service.persist_and_dispatch(ctx, fetch)

        signals = live_session.execute(
            select(ImportedSignal).where(
                ImportedSignal.connected_account_id == account.id
            )
        ).scalars().all()
        assert len(signals) == 1

        assert dispatch_result.total_dispatched == 1
        assert dispatch_result.total_succeeded == 1

    def test_mixed_record_types_each_dispatched(self, live_session) -> None:
        """Mixed messages + events get separate references, each dispatched."""
        account = _make_account_live(live_session)
        live_session.commit()

        ctx = _make_context(account)
        fetch = FetchResult(
            messages=[
                NormalizedMessageData(
                    source_type="gmail",
                    external_message_id="mix_dispatch_msg",
                    subject="Mix test",
                    body_text="Mixed content.",
                ),
            ],
            events=[
                NormalizedEventData(
                    external_event_id="mix_dispatch_evt",
                    title="Mix Meeting",
                    start_time=datetime(2026, 4, 15, 14, 0, tzinfo=timezone.utc),
                    end_time=datetime(2026, 4, 15, 15, 0, tzinfo=timezone.utc),
                ),
            ],
        )

        service = IntakeHandoffService(live_session)
        dispatch_result = service.persist_and_dispatch(ctx, fetch)

        # Two references: one message, one event
        assert len(dispatch_result.references) == 2
        assert dispatch_result.total_dispatched == 2
        assert dispatch_result.total_succeeded == 2
        ref_types = {r.record_type for r in dispatch_result.references}
        assert "message" in ref_types
        assert "calendar_event" in ref_types

    def test_empty_fetch_produces_no_dispatch(self, live_session) -> None:
        """Empty FetchResult produces zero references and zero dispatches."""
        account = _make_account_live(live_session)
        live_session.commit()

        ctx = _make_context(account)
        fetch = FetchResult()

        service = IntakeHandoffService(live_session)
        dispatch_result = service.persist_and_dispatch(ctx, fetch)

        assert dispatch_result.total_dispatched == 0
        assert dispatch_result.total_succeeded == 0
        assert len(dispatch_result.references) == 0

    def test_provenance_preserved_through_full_chain(self, live_session) -> None:
        """Account provenance survives from connector → persist → dispatch."""
        account = _make_account_live(live_session)
        live_session.commit()

        ctx = _make_context(account)
        fetch = FetchResult(
            messages=[
                NormalizedMessageData(
                    source_type="microsoft_mail",
                    external_message_id="prov_dispatch_msg",
                    sender_identity="sender@corp.com",
                ),
            ]
        )

        service = IntakeHandoffService(live_session)
        dispatch_result = service.persist_and_dispatch(ctx, fetch)

        # Reference carries provenance
        ref = dispatch_result.references[0]
        assert ref.connected_account_id == account.id
        assert ref.provider_type == "google"

        # Persisted message carries provenance
        msg = live_session.execute(
            select(Message).where(
                Message.external_message_id == "prov_dispatch_msg"
            )
        ).scalar_one()
        assert msg.connected_account_id == account.id
        assert msg.source_type == "microsoft_mail"

    def test_dispatch_outcome_reference_matches_input(self, live_session) -> None:
        """Each outcome references the same IntakeReference that was dispatched."""
        account = _make_account_live(live_session)
        live_session.commit()

        ctx = _make_context(account)
        fetch = FetchResult(
            messages=[
                NormalizedMessageData(
                    source_type="gmail",
                    external_message_id="outcome_ref_msg",
                ),
            ]
        )

        service = IntakeHandoffService(live_session)
        dispatch_result = service.persist_and_dispatch(ctx, fetch)

        assert len(dispatch_result.outcomes) == 1
        outcome = dispatch_result.outcomes[0]
        assert outcome.reference.record_type == "message"
        assert outcome.reference.connected_account_id == account.id


# ── Graceful Degradation Tests (mocked graph) ───────────────────────


class TestDispatchGracefulDegradation:
    """TEST:Connector.IntakeDispatch.GracefulDegradationOnError"""

    def test_graph_exception_does_not_crash_dispatch(self) -> None:
        """Graph exception captured in outcome, dispatch continues."""
        ref = IntakeReference(
            source_record_ids=[uuid.uuid4()],
            record_type="message",
            connected_account_id=uuid.uuid4(),
            provider_type="google",
        )

        mock_graph = MagicMock()
        mock_graph.invoke.side_effect = Exception("Unexpected graph error")

        with patch(
            "app.graphs.intake.get_intake_graph", return_value=mock_graph
        ):
            result = dispatch_to_intake_graph([ref])

        assert result.total_failed == 1
        assert result.total_succeeded == 0
        assert result.outcomes[0].success is False
        assert "Unexpected graph error" in result.outcomes[0].error

    def test_partial_failure_in_batch(self) -> None:
        """If one reference fails, others still succeed."""
        refs = [
            IntakeReference(
                source_record_ids=[uuid.uuid4()],
                record_type="message",
                connected_account_id=uuid.uuid4(),
                provider_type="google",
            )
            for _ in range(3)
        ]

        mock_graph = MagicMock()
        mock_graph.invoke.side_effect = [
            {"current_step": "complete", "triage_records_processed": 1},
            RuntimeError("Second ref fails"),
            {"current_step": "complete", "triage_records_processed": 1},
        ]

        with patch(
            "app.graphs.intake.get_intake_graph", return_value=mock_graph
        ):
            result = dispatch_to_intake_graph(refs)

        assert result.total_dispatched == 3
        assert result.total_succeeded == 2
        assert result.total_failed == 1
        assert result.outcomes[0].success is True
        assert result.outcomes[1].success is False
        assert result.outcomes[2].success is True

    def test_review_reasons_aggregated_across_references(self) -> None:
        """Review reasons from multiple references aggregated in dispatch result."""
        refs = [
            IntakeReference(
                source_record_ids=[uuid.uuid4()],
                record_type="message",
                connected_account_id=uuid.uuid4(),
                provider_type="google",
            )
            for _ in range(2)
        ]

        mock_graph = MagicMock()
        mock_graph.invoke.side_effect = [
            {
                "current_step": "complete",
                "triage_needs_review": True,
                "triage_review_reasons": ["Ambiguous sender"],
                "triage_records_processed": 1,
            },
            {
                "current_step": "complete",
                "triage_needs_review": True,
                "triage_review_reasons": ["Low confidence match"],
                "triage_records_processed": 1,
            },
        ]

        with patch(
            "app.graphs.intake.get_intake_graph", return_value=mock_graph
        ):
            result = dispatch_to_intake_graph(refs)

        assert result.needs_review is True
        assert "Ambiguous sender" in result.review_reasons
        assert "Low confidence match" in result.review_reasons



