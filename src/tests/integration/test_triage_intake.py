"""Intake graph routing tests.

TEST:Triage.Intake.SourceRoutesCorrectly
TEST:Release.Graph.CoreAssistantFlowsPass
"""

from __future__ import annotations

import uuid

from app.graphs.intake import get_intake_graph, classify_source


class TestIntakeRouting:
    """TEST:Triage.Intake.SourceRoutesCorrectly

    Proves intake graph correctly routes different source types
    to the appropriate triage path.
    """

    def test_gmail_message_routes_to_triage(self) -> None:
        state = {
            "source_record_ids": [uuid.uuid4()],
            "record_type": "message",
            "connected_account_id": uuid.uuid4(),
            "provider_type": "google",
            "channel": "web",
        }
        result = classify_source(state)
        assert result["route_target"] == "triage"
        assert "google" in result["route_reason"]

    def test_microsoft_message_routes_to_triage(self) -> None:
        state = {
            "source_record_ids": [uuid.uuid4()],
            "record_type": "message",
            "provider_type": "microsoft",
            "channel": "web",
        }
        result = classify_source(state)
        assert result["route_target"] == "triage"

    def test_calendar_event_routes_to_triage(self) -> None:
        state = {
            "source_record_ids": [uuid.uuid4()],
            "record_type": "calendar_event",
            "provider_type": "google",
            "channel": "web",
        }
        result = classify_source(state)
        assert result["route_target"] == "triage"
        assert "calendar" in result["route_reason"].lower()

    def test_imported_signal_routes_to_triage(self) -> None:
        state = {
            "source_record_ids": [uuid.uuid4()],
            "record_type": "imported_signal",
            "provider_type": "manual",
            "channel": "web",
        }
        result = classify_source(state)
        assert result["route_target"] == "triage"

    def test_routing_assigns_workflow_id(self) -> None:
        state = {
            "record_type": "message",
            "provider_type": "google",
        }
        result = classify_source(state)
        assert "workflow_id" in result
        assert len(result["workflow_id"]) > 0

    def test_routing_assigns_timestamp(self) -> None:
        state = {
            "record_type": "message",
            "provider_type": "google",
        }
        result = classify_source(state)
        assert "initiated_at" in result

    def test_compiled_graph_executes(self) -> None:
        """The compiled intake graph runs end-to-end."""
        graph = get_intake_graph()
        state = {
            "source_record_ids": [uuid.uuid4()],
            "record_type": "message",
            "connected_account_id": uuid.uuid4(),
            "provider_type": "google",
            "channel": "web",
        }
        result = graph.invoke(state)
        assert result["route_target"] == "triage"

    def test_unknown_record_type_defaults_to_triage(self) -> None:
        state = {
            "record_type": "something_new",
            "provider_type": "unknown",
        }
        result = classify_source(state)
        assert result["route_target"] == "triage"

