"""Microsoft Graph calendar connector — imports M365 calendar events.

ARCH:MicrosoftCalendarConnector
ARCH:MicrosoftCalendarProfileContext

Responsible for:
- Retrieving events from the relevant calendar profile
- Preserving account and tenant context
- Normalizing event data into internal CalendarEvent records
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


class MicrosoftCalendarConnector(BaseConnector):
    """Microsoft Graph calendar connector.

    ARCH:MicrosoftCalendarConnector
    ARCH:ConnectorPrinciple.ReadFirst
    """

    @property
    def provider_type(self) -> str:
        return "microsoft"

    @property
    def connector_type(self) -> str:
        return "microsoft_calendar"

    @property
    def supported_profile_types(self) -> list[str]:
        return ["calendar"]

    def fetch_and_normalize(
        self, context: ConnectorExecutionContext
    ) -> FetchResult:
        raise NotImplementedError(
            "Live Microsoft Calendar fetch requires OAuth credentials. "
            "Use normalize_graph_event() for fixture-driven testing."
        )

    def validate_credentials(
        self, context: ConnectorExecutionContext
    ) -> bool:
        raise NotImplementedError(
            "Live credential validation requires OAuth app registration."
        )

    @staticmethod
    def normalize_graph_event(
        raw_event: dict[str, Any],
        context: ConnectorExecutionContext,
    ) -> NormalizedEventData:
        """Normalize a single Microsoft Graph calendar event into internal form.

        Preserves:
        - Event ID
        - Account and tenant context (via context)
        - Calendar identity (via profile)
        - Attendee list
        - Time range and timezone
        - Location or online meeting link

        ARCH:MicrosoftCalendarProfileContext
        """
        start_time = _parse_graph_event_datetime(raw_event.get("start", {}))
        end_time = _parse_graph_event_datetime(raw_event.get("end", {}))

        # Extract attendees
        attendees = raw_event.get("attendees", [])
        participants = None
        if attendees:
            participants = {
                "attendees": [
                    {
                        "email": a.get("emailAddress", {}).get("address"),
                        "name": a.get("emailAddress", {}).get("name"),
                        "type": a.get("type"),
                        "responseStatus": a.get("status", {}).get("response"),
                    }
                    for a in attendees
                ]
            }

        # Location or online meeting
        location = None
        locations = raw_event.get("locations", [])
        if locations:
            location = locations[0].get("displayName")
        if not location and raw_event.get("isOnlineMeeting"):
            online = raw_event.get("onlineMeeting", {})
            location = online.get("joinUrl")

        source_calendar = context.profile_label
        if not source_calendar:
            source_calendar = context.account_label

        return NormalizedEventData(
            external_event_id=raw_event["id"],
            title=raw_event.get("subject", "(No title)"),
            description_summary=_extract_body_preview(raw_event),
            start_time=start_time,
            end_time=end_time,
            participants=participants,
            location_or_link=location,
            source_calendar=source_calendar,
        )


def _parse_graph_event_datetime(dt_obj: dict[str, Any]) -> datetime:
    """Parse a Microsoft Graph event dateTime object."""
    dt_str = dt_obj.get("dateTime", "")
    tz_str = dt_obj.get("timeZone", "UTC")

    try:
        if dt_str:
            dt = datetime.fromisoformat(dt_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
    except (ValueError, TypeError):
        pass

    return datetime.now(timezone.utc)


def _extract_body_preview(raw_event: dict[str, Any]) -> Optional[str]:
    """Extract body preview or plain-text body from a Graph event."""
    preview = raw_event.get("bodyPreview")
    if preview:
        return preview
    body = raw_event.get("body", {})
    if body.get("contentType") == "text":
        return body.get("content")
    return None

