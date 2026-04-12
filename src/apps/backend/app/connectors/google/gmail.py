"""Gmail connector — imports mail from Google accounts.

ARCH:GmailConnector
ARCH:GmailThreadContext

Responsible for:
- Authenticating against connected Google accounts
- Retrieving message metadata and body content
- Preserving Gmail message and thread identifiers
- Preserving account and label context
- Mapping into normalized Message and MessageThread forms
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from app.connectors.base import BaseConnector
from app.connectors.contracts import (
    ConnectorExecutionContext,
    FetchResult,
    NormalizedMessageData,
    NormalizedThreadData,
)


class GmailConnector(BaseConnector):
    """Gmail / Google Workspace mail connector.

    ARCH:GmailConnector
    ARCH:ConnectorPrinciple.ReadFirst
    """

    @property
    def provider_type(self) -> str:
        return "google"

    @property
    def connector_type(self) -> str:
        return "gmail"

    @property
    def supported_profile_types(self) -> list[str]:
        return ["mail"]

    def fetch_and_normalize(
        self, context: ConnectorExecutionContext
    ) -> FetchResult:
        """Fetch and normalize Gmail messages.

        In production, this will use the Gmail API. For now, this is
        the structural boundary — live provider integration requires
        OAuth app registration (human dependency).
        """
        raise NotImplementedError(
            "Live Gmail fetch requires OAuth credentials. "
            "Use normalize_gmail_payload() for fixture-driven testing."
        )

    def validate_credentials(
        self, context: ConnectorExecutionContext
    ) -> bool:
        """Validate Gmail OAuth credentials."""
        raise NotImplementedError(
            "Live credential validation requires OAuth app registration."
        )

    @staticmethod
    def normalize_gmail_payload(
        raw_message: dict[str, Any],
        context: ConnectorExecutionContext,
    ) -> NormalizedMessageData:
        """Normalize a single Gmail API message payload into internal form.

        This is the normalization logic that can be tested with fixtures
        without live API access.

        Preserves:
        - Gmail message ID
        - Gmail thread ID (ARCH:GmailThreadContext)
        - Account provenance (via context)
        - Sender/recipient identity
        - Subject and body text
        - Sent/received timestamps
        - Label context as import metadata
        """
        headers = {
            h["name"].lower(): h["value"]
            for h in raw_message.get("payload", {}).get("headers", [])
        }

        # Extract body text from payload
        body_text = _extract_body_text(raw_message.get("payload", {}))

        # Parse timestamps
        sent_at = _parse_timestamp(headers.get("date"))
        received_at = _parse_internal_date(raw_message.get("internalDate"))

        # Build recipient list
        recipients = {}
        if "to" in headers:
            recipients["to"] = [
                addr.strip() for addr in headers["to"].split(",")
            ]
        if "cc" in headers:
            recipients["cc"] = [
                addr.strip() for addr in headers["cc"].split(",")
            ]

        return NormalizedMessageData(
            source_type="gmail",
            external_message_id=raw_message["id"],
            external_thread_id=raw_message.get("threadId"),
            subject=headers.get("subject"),
            body_text=body_text,
            sent_at=sent_at,
            received_at=received_at,
            sender_identity=headers.get("from"),
            recipient_identities=recipients if recipients else None,
            import_metadata={
                "gmail_labels": raw_message.get("labelIds", []),
                "gmail_snippet": raw_message.get("snippet"),
                "provider": "gmail",
                "account_label": context.account_label,
            },
        )

    @staticmethod
    def normalize_gmail_thread(
        raw_thread: dict[str, Any],
        context: ConnectorExecutionContext,
    ) -> NormalizedThreadData:
        """Normalize a Gmail thread envelope into internal form."""
        messages = raw_thread.get("messages", [])
        headers = {}
        if messages:
            first_msg = messages[0]
            headers = {
                h["name"].lower(): h["value"]
                for h in first_msg.get("payload", {}).get("headers", [])
            }

        # Collect participants from all messages in thread
        participants: set[str] = set()
        for msg in messages:
            msg_headers = {
                h["name"].lower(): h["value"]
                for h in msg.get("payload", {}).get("headers", [])
            }
            if "from" in msg_headers:
                participants.add(msg_headers["from"])
            if "to" in msg_headers:
                for addr in msg_headers["to"].split(","):
                    participants.add(addr.strip())

        last_activity = None
        if messages:
            last_msg = messages[-1]
            last_activity = _parse_internal_date(last_msg.get("internalDate"))

        return NormalizedThreadData(
            source_type="gmail",
            external_thread_id=raw_thread["id"],
            derived_subject=headers.get("subject"),
            participant_set={"addresses": sorted(participants)} if participants else None,
            last_activity_at=last_activity,
        )


def _extract_body_text(payload: dict[str, Any]) -> Optional[str]:
    """Extract plain text body from Gmail message payload."""
    if payload.get("mimeType") == "text/plain" and "body" in payload:
        import base64
        data = payload["body"].get("data", "")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    # Check parts for multipart messages
    for part in payload.get("parts", []):
        if part.get("mimeType") == "text/plain" and "body" in part:
            import base64
            data = part["body"].get("data", "")
            if data:
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    return None


def _parse_timestamp(date_str: Optional[str]) -> Optional[datetime]:
    """Parse an email Date header into a timezone-aware datetime."""
    if not date_str:
        return None
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_str)
    except (ValueError, TypeError):
        return None


def _parse_internal_date(internal_date: Optional[str]) -> Optional[datetime]:
    """Parse Gmail internalDate (epoch millis string) to datetime."""
    if not internal_date:
        return None
    try:
        epoch_ms = int(internal_date)
        return datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc)
    except (ValueError, TypeError):
        return None

