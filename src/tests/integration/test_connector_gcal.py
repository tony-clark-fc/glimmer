"""Google Calendar normalization tests.

TEST:Connector.GoogleCalendar.NormalizationPreservesCalendarContext
"""

from __future__ import annotations

import uuid

from app.connectors.contracts import ConnectorExecutionContext
from app.connectors.google.calendar import GoogleCalendarConnector


def _make_context(**kwargs) -> ConnectorExecutionContext:
    defaults = {
        "connected_account_id": uuid.uuid4(),
        "provider_type": "google",
        "account_label": "operator@gmail.com",
        "profile_id": uuid.uuid4(),
        "profile_type": "calendar",
        "profile_label": "Work Calendar",
    }
    defaults.update(kwargs)
    return ConnectorExecutionContext(**defaults)


GCAL_EVENT_FIXTURE = {
    "id": "evt_gcal_001",
    "summary": "Q3 Planning Review",
    "description": "Review milestones and blockers for Q3 delivery.",
    "start": {"dateTime": "2026-04-14T10:00:00+01:00"},
    "end": {"dateTime": "2026-04-14T11:30:00+01:00"},
    "attendees": [
        {
            "email": "operator@gmail.com",
            "displayName": "Operator",
            "responseStatus": "accepted",
            "organizer": True,
        },
        {
            "email": "alice@example.com",
            "displayName": "Alice",
            "responseStatus": "tentative",
        },
    ],
    "location": "Meeting Room 3",
    "organizer": {"email": "operator@gmail.com"},
}

GCAL_ALLDAY_EVENT_FIXTURE = {
    "id": "evt_gcal_002",
    "summary": "Company Offsite",
    "start": {"date": "2026-04-20"},
    "end": {"date": "2026-04-21"},
    "organizer": {"email": "hr@company.com"},
}

GCAL_ONLINE_EVENT_FIXTURE = {
    "id": "evt_gcal_003",
    "summary": "Sprint Standup",
    "start": {"dateTime": "2026-04-14T09:00:00+00:00"},
    "end": {"dateTime": "2026-04-14T09:15:00+00:00"},
    "conferenceData": {
        "entryPoints": [
            {"entryPointType": "video", "uri": "https://meet.google.com/abc-def-ghi"},
        ]
    },
    "organizer": {"email": "team@company.com"},
}


class TestGoogleCalendarNormalization:
    """TEST:Connector.GoogleCalendar.NormalizationPreservesCalendarContext"""

    def test_event_preserves_event_id(self) -> None:
        ctx = _make_context()
        event = GoogleCalendarConnector.normalize_gcal_event(GCAL_EVENT_FIXTURE, ctx)
        assert event.external_event_id == "evt_gcal_001"

    def test_event_preserves_title(self) -> None:
        ctx = _make_context()
        event = GoogleCalendarConnector.normalize_gcal_event(GCAL_EVENT_FIXTURE, ctx)
        assert event.title == "Q3 Planning Review"

    def test_event_preserves_description(self) -> None:
        ctx = _make_context()
        event = GoogleCalendarConnector.normalize_gcal_event(GCAL_EVENT_FIXTURE, ctx)
        assert "milestones and blockers" in event.description_summary

    def test_event_preserves_time_range(self) -> None:
        ctx = _make_context()
        event = GoogleCalendarConnector.normalize_gcal_event(GCAL_EVENT_FIXTURE, ctx)
        assert event.start_time is not None
        assert event.end_time is not None
        assert event.end_time > event.start_time

    def test_event_preserves_participants(self) -> None:
        ctx = _make_context()
        event = GoogleCalendarConnector.normalize_gcal_event(GCAL_EVENT_FIXTURE, ctx)
        assert event.participants is not None
        emails = [a["email"] for a in event.participants["attendees"]]
        assert "operator@gmail.com" in emails
        assert "alice@example.com" in emails

    def test_event_preserves_location(self) -> None:
        ctx = _make_context()
        event = GoogleCalendarConnector.normalize_gcal_event(GCAL_EVENT_FIXTURE, ctx)
        assert event.location_or_link == "Meeting Room 3"

    def test_event_preserves_source_calendar_from_profile(self) -> None:
        """Source calendar label comes from the resolved profile context."""
        ctx = _make_context(profile_label="Personal Calendar")
        event = GoogleCalendarConnector.normalize_gcal_event(GCAL_EVENT_FIXTURE, ctx)
        assert event.source_calendar == "Personal Calendar"

    def test_allday_event_normalizes(self) -> None:
        ctx = _make_context()
        event = GoogleCalendarConnector.normalize_gcal_event(GCAL_ALLDAY_EVENT_FIXTURE, ctx)
        assert event.title == "Company Offsite"
        assert event.start_time is not None

    def test_online_event_extracts_meeting_link(self) -> None:
        ctx = _make_context()
        event = GoogleCalendarConnector.normalize_gcal_event(GCAL_ONLINE_EVENT_FIXTURE, ctx)
        assert event.location_or_link is not None
        assert "meet.google.com" in event.location_or_link

