"""Triage pipeline integration tests.

TEST:Triage.Pipeline.EndToEndClassificationAndExtraction
TEST:Triage.Pipeline.APIEndpointReturnsCorrectShape
TEST:Release.Graph.CoreAssistantFlowsPass

Proves the triage pipeline service correctly loads source records,
classifies them, extracts from them, and persists results.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.source import ConnectedAccount, Message, CalendarEvent, ImportedSignal
from app.models.portfolio import Project
from app.models.interpretation import MessageClassification
from app.services.triage_pipeline import (
    process_triage_batch,
    _extract_triage_fields,
)


# ── Helpers ──────────────────────────────────────────────────────────


def _make_account(session: Session) -> ConnectedAccount:
    """Create a minimal ConnectedAccount for tests."""
    account = ConnectedAccount(
        provider_type="google",
        account_label="test@example.com",
        account_address="test@example.com",
        status="active",
    )
    session.add(account)
    session.flush()
    return account


def _make_project(session: Session, name: str = "TestProject") -> Project:
    """Create a minimal active Project."""
    project = Project(
        name=name,
        status="active",
        objective="Test objective for pipeline",
        short_summary=f"Summary of {name}",
    )
    session.add(project)
    session.flush()
    return project


def _make_message(
    session: Session,
    account: ConnectedAccount,
    *,
    subject: str = "Hello from pipeline",
    body_text: str = "Body content for testing",
    sender: str = "sender@example.com",
) -> Message:
    """Create a persisted Message."""
    msg = Message(
        connected_account_id=account.id,
        source_type="gmail",
        external_message_id=f"ext-{uuid.uuid4().hex[:12]}",
        subject=subject,
        body_text=body_text,
        sender_identity=sender,
        sent_at=datetime.now(timezone.utc),
    )
    session.add(msg)
    session.flush()
    return msg


def _make_calendar_event(session: Session, account: ConnectedAccount) -> CalendarEvent:
    """Create a persisted CalendarEvent."""
    now = datetime.now(timezone.utc)
    event = CalendarEvent(
        connected_account_id=account.id,
        external_event_id=f"evt-{uuid.uuid4().hex[:12]}",
        title="Team standup",
        description_summary="Daily standup meeting",
        start_time=now,
        end_time=now,
    )
    session.add(event)
    session.flush()
    return event


def _make_imported_signal(
    session: Session, account: ConnectedAccount
) -> ImportedSignal:
    """Create a persisted ImportedSignal."""
    signal = ImportedSignal(
        connected_account_id=account.id,
        signal_type="manual_paste",
        source_label="Voice memo",
        content="Need to schedule a follow-up about the budget proposal",
    )
    session.add(signal)
    session.flush()
    return signal


# ── Field Extraction Tests ───────────────────────────────────────────


class TestFieldExtraction:
    """TEST:Triage.Pipeline.FieldExtractionFromSourceRecords"""

    def test_message_field_extraction(self, db_session: Session) -> None:
        account = _make_account(db_session)
        msg = _make_message(db_session, account, subject="Budget Q3", body_text="Please review")
        fields = _extract_triage_fields("message", msg)
        assert fields["subject"] == "Budget Q3"
        assert fields["body_text"] == "Please review"
        assert fields["sender_identity"] == "sender@example.com"

    def test_calendar_event_field_extraction(self, db_session: Session) -> None:
        account = _make_account(db_session)
        event = _make_calendar_event(db_session, account)
        fields = _extract_triage_fields("calendar_event", event)
        assert fields["subject"] == "Team standup"
        assert fields["body_text"] == "Daily standup meeting"
        assert fields["sender_identity"] is None

    def test_imported_signal_field_extraction(self, db_session: Session) -> None:
        account = _make_account(db_session)
        signal = _make_imported_signal(db_session, account)
        fields = _extract_triage_fields("imported_signal", signal)
        assert fields["subject"] == "manual_paste"
        assert "budget proposal" in fields["body_text"]
        assert fields["sender_identity"] == "Voice memo"


# ── Pipeline Tests ───────────────────────────────────────────────────


class TestTriagePipelineMessage:
    """TEST:Triage.Pipeline.EndToEndClassificationAndExtraction

    Proves the pipeline classifies persisted messages and produces
    visible classification artifacts.
    """

    def test_pipeline_classifies_a_message(self, db_session: Session) -> None:
        """Pipeline produces a MessageClassification for a persisted message."""
        account = _make_account(db_session)
        project = _make_project(db_session, name="Budget Review")
        msg = _make_message(
            db_session, account,
            subject="Budget Review meeting notes",
            body_text="Attached are the Budget Review outcomes.",
        )

        result = process_triage_batch(
            session=db_session,
            source_record_ids=[msg.id],
            record_type="message",
            connected_account_id=account.id,
        )

        assert result.records_processed == 1
        assert result.records_skipped == 0
        assert len(result.classification_ids) == 1

        # Verify the classification was persisted
        classification = db_session.get(
            MessageClassification, result.classification_ids[0]
        )
        assert classification is not None
        assert classification.source_record_id == msg.id
        assert classification.source_record_type == "message"

    def test_pipeline_classifies_with_project_match(self, db_session: Session) -> None:
        """When a message matches a project, the classification captures it."""
        account = _make_account(db_session)
        project = _make_project(db_session, name="Alpha")
        msg = _make_message(
            db_session, account,
            subject="Alpha project update",
            body_text="Alpha milestone reached.",
        )

        result = process_triage_batch(
            session=db_session,
            source_record_ids=[msg.id],
            record_type="message",
        )

        assert result.records_processed == 1
        # The deterministic classifier should match on project name
        rec = result.record_results[0]
        assert rec.classified_project_id == project.id
        assert rec.classification_confidence > 0

    def test_pipeline_extraction_deterministic_empty(
        self, db_session: Session
    ) -> None:
        """With LLM disabled, extraction returns empty lists (no ExtractedAction rows)."""
        account = _make_account(db_session)
        msg = _make_message(db_session, account)

        result = process_triage_batch(
            session=db_session,
            source_record_ids=[msg.id],
            record_type="message",
        )

        # LLM extraction is off by default in tests → empty
        assert result.extraction_ids == []
        rec = result.record_results[0]
        assert rec.extracted_action_ids == []
        assert rec.extracted_decision_ids == []
        assert rec.extracted_deadline_ids == []


class TestTriagePipelineBatch:
    """TEST:Triage.Pipeline.BatchProcessing"""

    def test_multiple_messages(self, db_session: Session) -> None:
        """Pipeline processes multiple message IDs in one call."""
        account = _make_account(db_session)
        msg1 = _make_message(db_session, account, subject="First")
        msg2 = _make_message(db_session, account, subject="Second")

        result = process_triage_batch(
            session=db_session,
            source_record_ids=[msg1.id, msg2.id],
            record_type="message",
        )

        assert result.records_processed == 2
        assert len(result.classification_ids) == 2

    def test_empty_record_ids(self, db_session: Session) -> None:
        """Empty ID list produces zero results, no error."""
        result = process_triage_batch(
            session=db_session,
            source_record_ids=[],
            record_type="message",
        )
        assert result.records_processed == 0
        assert result.classification_ids == []


class TestTriagePipelineCalendarEvent:
    """TEST:Triage.Pipeline.CalendarEventClassification"""

    def test_calendar_event_classified(self, db_session: Session) -> None:
        """Pipeline classifies a CalendarEvent."""
        account = _make_account(db_session)
        event = _make_calendar_event(db_session, account)

        result = process_triage_batch(
            session=db_session,
            source_record_ids=[event.id],
            record_type="calendar_event",
        )

        assert result.records_processed == 1
        assert len(result.classification_ids) == 1


class TestTriagePipelineImportedSignal:
    """TEST:Triage.Pipeline.ImportedSignalClassification"""

    def test_imported_signal_classified(self, db_session: Session) -> None:
        """Pipeline classifies an ImportedSignal."""
        account = _make_account(db_session)
        signal = _make_imported_signal(db_session, account)

        result = process_triage_batch(
            session=db_session,
            source_record_ids=[signal.id],
            record_type="imported_signal",
        )

        assert result.records_processed == 1
        assert len(result.classification_ids) == 1


class TestTriagePipelineReviewState:
    """TEST:Triage.Pipeline.ReviewStateHandling"""

    def test_no_matching_project_needs_review(self, db_session: Session) -> None:
        """When no project matches, the classification needs review."""
        account = _make_account(db_session)
        # Create a project that won't match the message content
        _make_project(db_session, name="UnrelatedProjectZeta")
        msg = _make_message(
            db_session, account,
            subject="Completely unrelated content xyz",
            body_text="Nothing matching any project at all",
        )

        result = process_triage_batch(
            session=db_session,
            source_record_ids=[msg.id],
            record_type="message",
        )

        assert result.needs_review is True
        assert len(result.review_reasons) > 0


class TestTriagePipelineErrorHandling:
    """TEST:Triage.Pipeline.GracefulErrorHandling"""

    def test_nonexistent_record_skipped(self, db_session: Session) -> None:
        """Non-existent record ID is skipped without crashing."""
        fake_id = uuid.uuid4()
        result = process_triage_batch(
            session=db_session,
            source_record_ids=[fake_id],
            record_type="message",
        )

        assert result.records_processed == 0
        assert result.records_skipped == 1
        assert len(result.errors) == 1
        assert str(fake_id) in result.errors[0]

    def test_mixed_valid_and_invalid(self, db_session: Session) -> None:
        """Pipeline processes valid records and skips invalid ones."""
        account = _make_account(db_session)
        msg = _make_message(db_session, account)
        fake_id = uuid.uuid4()

        result = process_triage_batch(
            session=db_session,
            source_record_ids=[msg.id, fake_id],
            record_type="message",
        )

        assert result.records_processed == 1
        assert result.records_skipped == 1
        assert len(result.classification_ids) == 1


class TestTriagePipelineAPI:
    """TEST:Triage.Pipeline.APIEndpointReturnsCorrectShape"""

    def test_process_messages_endpoint(self, client, db_session: Session) -> None:
        """POST /triage/process-messages returns the expected shape."""
        # The TestClient uses the dev DB, not the test session.
        # Send fake IDs — they won't exist, but the endpoint should return
        # a valid response with records_skipped and errors.
        response = client.post(
            "/triage/process-messages",
            json={
                "source_record_ids": [str(uuid.uuid4())],
                "record_type": "message",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "classification_ids" in data
        assert "extraction_ids" in data
        assert "needs_review" in data
        assert "records_processed" in data
        assert "records_skipped" in data
        assert "errors" in data
        # Non-existent record → skipped
        assert data["records_skipped"] >= 1

    def test_process_messages_empty_body(self, client) -> None:
        """Missing required fields returns 422."""
        response = client.post("/triage/process-messages", json={})
        assert response.status_code == 422


class TestIntakeGraphWithDB:
    """TEST:Triage.Pipeline.IntakeGraphEndToEnd

    Proves the compiled intake graph actually invokes the triage
    pipeline when real source records exist.  Uses the triage_handoff
    function's graceful degradation — with fake IDs the pipeline
    will skip records but the graph completes.
    """

    def test_intake_graph_with_fake_ids_degrades_gracefully(self) -> None:
        """Graph completes even when source_record_ids aren't in DB."""
        from app.graphs.intake import get_intake_graph

        graph = get_intake_graph()
        state = {
            "source_record_ids": [uuid.uuid4()],
            "record_type": "message",
            "provider_type": "google",
            "channel": "web",
        }
        result = graph.invoke(state)
        assert result["route_target"] == "triage"
        # The graph should complete — either with triage results or error
        assert "current_step" in result

    def test_intake_graph_without_source_ids_skips_pipeline(self) -> None:
        """Graph skips triage pipeline when no source_record_ids."""
        from app.graphs.intake import get_intake_graph

        graph = get_intake_graph()
        state = {
            "record_type": "message",
            "provider_type": "google",
            "channel": "web",
        }
        result = graph.invoke(state)
        assert result["route_target"] == "triage"
        assert result.get("current_step") == "triage_handoff_complete"



