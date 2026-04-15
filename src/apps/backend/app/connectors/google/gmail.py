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

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from app.connectors.base import BaseConnector
from app.connectors.contracts import (
    ConnectorExecutionContext,
    FetchResult,
    NormalizedMessageData,
    NormalizedThreadData,
)

logger = logging.getLogger(__name__)


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
        """Fetch and normalize Gmail messages using the Gmail API.

        ARCH:GmailConnector
        ARCH:ConnectorPrinciple.ReadFirst

        Requires valid OAuth tokens in context.sync_metadata._access_token.
        Falls back to NotImplementedError if no tokens are available.
        """
        access_token = (context.sync_metadata or {}).get("_access_token")
        if not access_token:
            raise NotImplementedError(
                "Live Gmail fetch requires OAuth credentials. "
                "Use normalize_gmail_payload() for fixture-driven testing."
            )

        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        credentials = Credentials(token=access_token)
        service = build("gmail", "v1", credentials=credentials)

        # Determine query — incremental from last sync or recent messages
        sync_metadata = context.sync_metadata or {}
        query = "newer_than:1d"
        if sync_metadata.get("sync_cursor", {}).get("gmail_history_id"):
            # Use history-based incremental (future enhancement)
            query = "newer_than:1d"

        # Fetch message list (read-only)
        results = service.users().messages().list(
            userId="me",
            q=query,
            maxResults=50,
        ).execute()

        messages_list = results.get("messages", [])

        normalized_messages: list[NormalizedMessageData] = []
        normalized_threads: list[NormalizedThreadData] = []
        seen_thread_ids: set[str] = set()

        for msg_stub in messages_list:
            try:
                # Fetch full message
                raw_message = service.users().messages().get(
                    userId="me",
                    id=msg_stub["id"],
                    format="full",
                ).execute()

                normalized = self.normalize_gmail_payload(raw_message, context)
                normalized_messages.append(normalized)

                # Track thread for thread normalization
                thread_id = raw_message.get("threadId")
                if thread_id and thread_id not in seen_thread_ids:
                    seen_thread_ids.add(thread_id)

            except Exception as exc:
                logger.warning(
                    "Gmail: failed to fetch message %s: %s",
                    msg_stub.get("id"),
                    exc,
                )

        # Fetch thread data for unique threads
        for thread_id in seen_thread_ids:
            try:
                raw_thread = service.users().threads().get(
                    userId="me",
                    id=thread_id,
                    format="metadata",
                    metadataHeaders=["From", "To", "Subject", "Date"],
                ).execute()
                thread_data = self.normalize_gmail_thread(raw_thread, context)
                normalized_threads.append(thread_data)
            except Exception as exc:
                logger.warning("Gmail: failed to fetch thread %s: %s", thread_id, exc)

        # Build sync checkpoint
        history_id = None
        if messages_list:
            # Get the latest historyId for future incremental sync
            try:
                profile = service.users().getProfile(userId="me").execute()
                history_id = profile.get("historyId")
            except Exception:
                pass

        from app.connectors.contracts import SyncCheckpoint
        checkpoint = SyncCheckpoint(
            connected_account_id=context.connected_account_id,
            status="success",
            items_fetched=len(normalized_messages),
            sync_cursor={"gmail_history_id": history_id} if history_id else None,
        )

        return FetchResult(
            messages=normalized_messages,
            threads=normalized_threads,
            checkpoint=checkpoint,
        )

    def validate_credentials(
        self, context: ConnectorExecutionContext
    ) -> bool:
        """Validate Gmail OAuth credentials with a lightweight API call."""
        access_token = (context.sync_metadata or {}).get("_access_token")
        if not access_token:
            return False

        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build

            credentials = Credentials(token=access_token)
            service = build("gmail", "v1", credentials=credentials)
            service.users().getProfile(userId="me").execute()
            return True
        except Exception:
            return False

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

