"""Microsoft Graph mail connector — imports Outlook/M365 mail.

ARCH:MicrosoftGraphConnector
ARCH:MicrosoftTenantMailboxContext

Responsible for:
- Authenticating against connected Microsoft 365 accounts
- Importing message metadata and body content
- Preserving Microsoft message and conversation/thread identifiers
- Preserving account/folder/tenant context
- Mapping into normalized internal message records
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


class MicrosoftMailConnector(BaseConnector):
    """Microsoft Graph mail connector.

    ARCH:MicrosoftGraphConnector
    ARCH:ConnectorPrinciple.ReadFirst
    """

    @property
    def provider_type(self) -> str:
        return "microsoft"

    @property
    def connector_type(self) -> str:
        return "microsoft_mail"

    @property
    def supported_profile_types(self) -> list[str]:
        return ["mail"]

    def fetch_and_normalize(
        self, context: ConnectorExecutionContext
    ) -> FetchResult:
        raise NotImplementedError(
            "Live Microsoft mail fetch requires OAuth credentials. "
            "Use normalize_graph_message() for fixture-driven testing."
        )

    def validate_credentials(
        self, context: ConnectorExecutionContext
    ) -> bool:
        raise NotImplementedError(
            "Live credential validation requires OAuth app registration."
        )

    @staticmethod
    def normalize_graph_message(
        raw_message: dict[str, Any],
        context: ConnectorExecutionContext,
    ) -> NormalizedMessageData:
        """Normalize a single Microsoft Graph mail message into internal form.

        Preserves:
        - Microsoft message ID
        - Conversation ID (thread equivalent)
        - Account and tenant context (via context)
        - Sender/recipient identity
        - Subject and body text
        - Sent/received timestamps
        - Folder context as import metadata

        ARCH:MicrosoftTenantMailboxContext
        """
        # Extract sender
        sender_data = raw_message.get("from", {}).get("emailAddress", {})
        sender = sender_data.get("address")
        if sender_data.get("name"):
            sender = f"{sender_data['name']} <{sender}>"

        # Extract recipients
        recipients: dict[str, list[str]] = {}
        for field, key in [("toRecipients", "to"), ("ccRecipients", "cc")]:
            addrs = raw_message.get(field, [])
            if addrs:
                recipients[key] = [
                    r.get("emailAddress", {}).get("address", "")
                    for r in addrs
                ]

        # Parse timestamps
        sent_at = _parse_graph_datetime(raw_message.get("sentDateTime"))
        received_at = _parse_graph_datetime(raw_message.get("receivedDateTime"))

        # Extract body
        body = raw_message.get("body", {})
        body_text = body.get("content") if body.get("contentType") == "text" else None

        return NormalizedMessageData(
            source_type="microsoft_mail",
            external_message_id=raw_message["id"],
            external_thread_id=raw_message.get("conversationId"),
            subject=raw_message.get("subject"),
            body_text=body_text,
            sent_at=sent_at,
            received_at=received_at,
            sender_identity=sender,
            recipient_identities=recipients if recipients else None,
            import_metadata={
                "provider": "microsoft_graph",
                "account_label": context.account_label,
                "tenant_context": context.tenant_context,
                "folder": raw_message.get("parentFolderId"),
                "importance": raw_message.get("importance"),
                "is_read": raw_message.get("isRead"),
            },
        )

    @staticmethod
    def normalize_graph_thread(
        conversation_id: str,
        messages: list[dict[str, Any]],
        context: ConnectorExecutionContext,
    ) -> NormalizedThreadData:
        """Normalize a Microsoft Graph conversation into a thread record."""
        participants: set[str] = set()
        for msg in messages:
            sender = msg.get("from", {}).get("emailAddress", {}).get("address")
            if sender:
                participants.add(sender)
            for r in msg.get("toRecipients", []):
                addr = r.get("emailAddress", {}).get("address")
                if addr:
                    participants.add(addr)

        subject = messages[0].get("subject") if messages else None
        last_activity = None
        if messages:
            last_activity = _parse_graph_datetime(
                messages[-1].get("receivedDateTime")
            )

        return NormalizedThreadData(
            source_type="microsoft_mail",
            external_thread_id=conversation_id,
            derived_subject=subject,
            participant_set={"addresses": sorted(participants)} if participants else None,
            last_activity_at=last_activity,
        )


def _parse_graph_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Parse a Microsoft Graph ISO 8601 datetime string."""
    if not dt_str:
        return None
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        return None

