"""Google Calendar connector — imports events from Google accounts.

ARCH:GoogleCalendarConnector
ARCH:GoogleCalendarProfileContext

Responsible for:
- Retrieving upcoming and relevant calendar events
- Preserving source calendar identity
- Preserving account linkage
- Mapping event payloads into normalized CalendarEvent records
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from app.connectors.base import BaseConnector
from app.connectors.contracts import (
    ConnectorExecutionContext,
    FetchResult,
    NormalizedEventData,
)


class GoogleCalendarConnector(BaseConnector):
    """Google Calendar connector.

    ARCH:GoogleCalendarConnector
    ARCH:ConnectorPrinciple.ReadFirst
    """

    @property
    def provider_type(self) -> str:
        return "google"

    @property
    def connector_type(self) -> str:
        return "google_calendar"

    @property
    def supported_profile_types(self) -> list[str]:
        return ["calendar", "sub_calendar"]

    def fetch_and_normalize(
        self, context: ConnectorExecutionContext
    ) -> FetchResult:
        """Fetch and normalize Google Calendar events."""
        raise NotImplementedError(
            "Live Google Calendar fetch requires OAuth credentials. "
            "Use normalize_gcal_event() for fixture-driven testing."
        )

    def validate_credentials(
        self, context: ConnectorExecutionContext
    ) -> bool:
        raise NotImplementedError(
            "Live credential validation requires OAuth app registration."
        )

    @staticmethod
    def normalize_gcal_event(
        raw_event: dict[str, Any],
        context: ConnectorExecutionContext,
    ) -> NormalizedEventData:
        """Normalize a single Google Calendar API event into internal form.

        Preserves:
        - Event ID
        - Calendar identity (via context profile or source_calendar)
        - Account provenance (via context)
        - Participant list
        - Time range
        - Location or conferencing link

        ARCH:GoogleCalendarProfileContext
        """
        # Parse start/end times
        start_time = _parse_gcal_datetime(raw_event.get("start", {}))
        end_time = _parse_gcal_datetime(raw_event.get("end", {}))

        # Extract participants
        attendees = raw_event.get("attendees", [])
        participants = None
        if attendees:
            participants = {
                "attendees": [
                    {
                        "email": a.get("email"),
                        "displayName": a.get("displayName"),
                        "responseStatus": a.get("responseStatus"),
                        "organizer": a.get("organizer", False),
                    }
                    for a in attendees
                ]
            }

        # Extract location or conferencing link
        location = raw_event.get("location")
        if not location:
            conf = raw_event.get("conferenceData", {})
            entry_points = conf.get("entryPoints", [])
            for ep in entry_points:
                if ep.get("entryPointType") == "video":
                    location = ep.get("uri")
                    break

        # Determine source calendar label
        source_calendar = context.profile_label
        if not source_calendar:
            source_calendar = raw_event.get("organizer", {}).get("email")

        return NormalizedEventData(
            external_event_id=raw_event["id"],
            title=raw_event.get("summary", "(No title)"),
            description_summary=raw_event.get("description"),
            start_time=start_time,
            end_time=end_time,
            participants=participants,
            location_or_link=location,
            source_calendar=source_calendar,
        )


def _parse_gcal_datetime(dt_obj: dict[str, Any]) -> datetime:
    """Parse a Google Calendar dateTime or date field."""
    if "dateTime" in dt_obj:
        return datetime.fromisoformat(dt_obj["dateTime"])
    elif "date" in dt_obj:
        # All-day event — use midnight UTC
        return datetime.fromisoformat(dt_obj["date"] + "T00:00:00+00:00")
    else:
        return datetime.now(timezone.utc)

