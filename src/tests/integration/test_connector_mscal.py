"""Microsoft calendar normalization tests.

TEST:Connector.MicrosoftCalendar.NormalizationPreservesEventContext
"""

from __future__ import annotations

import uuid

from app.connectors.contracts import ConnectorExecutionContext
from app.connectors.microsoft.calendar import MicrosoftCalendarConnector


def _make_context(**kwargs) -> ConnectorExecutionContext:
    defaults = {
        "connected_account_id": uuid.uuid4(),
        "provider_type": "microsoft",
        "account_label": "operator@company.com",
        "tenant_context": "company.onmicrosoft.com",
        "profile_id": uuid.uuid4(),
        "profile_type": "calendar",
        "profile_label": "Company Calendar",
    }
    defaults.update(kwargs)
    return ConnectorExecutionContext(**defaults)


GRAPH_EVENT_FIXTURE = {
    "id": "AAMkAGI2EVT001",
    "subject": "Board Meeting",
    "bodyPreview": "Quarterly board review with full financials.",
    "start": {"dateTime": "2026-04-15T09:00:00.0000000", "timeZone": "UTC"},
    "end": {"dateTime": "2026-04-15T11:00:00.0000000", "timeZone": "UTC"},
    "attendees": [
        {
            "emailAddress": {"address": "ceo@company.com", "name": "CEO"},
            "type": "required",
            "status": {"response": "accepted"},
        },
        {
            "emailAddress": {"address": "cfo@company.com", "name": "CFO"},
            "type": "required",
            "status": {"response": "tentativelyAccepted"},
        },
    ],
    "locations": [{"displayName": "Boardroom A"}],
    "isOnlineMeeting": False,
}

GRAPH_ONLINE_EVENT_FIXTURE = {
    "id": "AAMkAGI2EVT002",
    "subject": "Remote Standup",
    "start": {"dateTime": "2026-04-15T09:00:00", "timeZone": "UTC"},
    "end": {"dateTime": "2026-04-15T09:15:00", "timeZone": "UTC"},
    "isOnlineMeeting": True,
    "onlineMeeting": {"joinUrl": "https://teams.microsoft.com/l/meetup-join/abc123"},
    "attendees": [],
}


class TestMicrosoftCalendarNormalization:
    """TEST:Connector.MicrosoftCalendar.NormalizationPreservesEventContext"""

    def test_event_preserves_event_id(self) -> None:
        ctx = _make_context()
        event = MicrosoftCalendarConnector.normalize_graph_event(GRAPH_EVENT_FIXTURE, ctx)
        assert event.external_event_id == "AAMkAGI2EVT001"

    def test_event_preserves_title(self) -> None:
        ctx = _make_context()
        event = MicrosoftCalendarConnector.normalize_graph_event(GRAPH_EVENT_FIXTURE, ctx)
        assert event.title == "Board Meeting"

    def test_event_preserves_body_preview(self) -> None:
        ctx = _make_context()
        event = MicrosoftCalendarConnector.normalize_graph_event(GRAPH_EVENT_FIXTURE, ctx)
        assert "quarterly board review" in event.description_summary.lower()

    def test_event_preserves_time_range(self) -> None:
        ctx = _make_context()
        event = MicrosoftCalendarConnector.normalize_graph_event(GRAPH_EVENT_FIXTURE, ctx)
        assert event.start_time is not None
        assert event.end_time is not None
        assert event.end_time > event.start_time

    def test_event_preserves_attendees(self) -> None:
        ctx = _make_context()
        event = MicrosoftCalendarConnector.normalize_graph_event(GRAPH_EVENT_FIXTURE, ctx)
        assert event.participants is not None
        emails = [a["email"] for a in event.participants["attendees"]]
        assert "ceo@company.com" in emails
        assert "cfo@company.com" in emails

    def test_event_preserves_physical_location(self) -> None:
        ctx = _make_context()
        event = MicrosoftCalendarConnector.normalize_graph_event(GRAPH_EVENT_FIXTURE, ctx)
        assert event.location_or_link == "Boardroom A"

    def test_event_preserves_source_calendar_from_profile(self) -> None:
        ctx = _make_context(profile_label="Personal MS Calendar")
        event = MicrosoftCalendarConnector.normalize_graph_event(GRAPH_EVENT_FIXTURE, ctx)
        assert event.source_calendar == "Personal MS Calendar"

    def test_online_event_extracts_teams_link(self) -> None:
        ctx = _make_context()
        event = MicrosoftCalendarConnector.normalize_graph_event(GRAPH_ONLINE_EVENT_FIXTURE, ctx)
        assert event.location_or_link is not None
        assert "teams.microsoft.com" in event.location_or_link

