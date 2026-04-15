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

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

from app.connectors.base import BaseConnector
from app.connectors.contracts import (
    ConnectorExecutionContext,
    FetchResult,
    NormalizedMessageData,
    NormalizedThreadData,
    SyncCheckpoint,
)

logger = logging.getLogger(__name__)


class MicrosoftMailConnector(BaseConnector):
    """Microsoft Graph mail connector.

    ARCH:MicrosoftGraphConnector
    ARCH:ConnectorPrinciple.ReadFirst
    """

    GRAPH_BASE = "https://graph.microsoft.com/v1.0"

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
        """Fetch and normalize Microsoft Graph mail messages.

        ARCH:MicrosoftGraphConnector
        ARCH:ConnectorPrinciple.ReadFirst

        Fetches recent messages from the last 24 hours.
        """
        access_token = (context.sync_metadata or {}).get("_access_token")
        if not access_token:
            raise NotImplementedError(
                "Live Microsoft mail fetch requires OAuth credentials. "
                "Use normalize_graph_message() for fixture-driven testing."
            )

        import httpx

        headers = {"Authorization": f"Bearer {access_token}"}

        # Fetch recent messages (last 24h or since last sync)
        since = (datetime.now(timezone.utc) - timedelta(days=1)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        params = {
            "$top": "50",
            "$orderby": "receivedDateTime desc",
            "$filter": f"receivedDateTime ge {since}",
            "$select": "id,conversationId,subject,from,toRecipients,ccRecipients,"
                       "body,sentDateTime,receivedDateTime,parentFolderId,"
                       "importance,isRead",
        }

        response = httpx.get(
            f"{self.GRAPH_BASE}/me/messages",
            headers=headers,
            params=params,
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()

        raw_messages = data.get("value", [])
        normalized_messages: list[NormalizedMessageData] = []
        normalized_threads: list[NormalizedThreadData] = []
        conversation_messages: dict[str, list[dict]] = {}

        for raw_msg in raw_messages:
            try:
                normalized = self.normalize_graph_message(raw_msg, context)
                normalized_messages.append(normalized)

                # Group by conversation for thread normalization
                conv_id = raw_msg.get("conversationId")
                if conv_id:
                    if conv_id not in conversation_messages:
                        conversation_messages[conv_id] = []
                    conversation_messages[conv_id].append(raw_msg)

            except Exception as exc:
                logger.warning(
                    "Microsoft Mail: failed to normalize message %s: %s",
                    raw_msg.get("id"),
                    exc,
                )

        # Build thread records from conversations
        for conv_id, conv_msgs in conversation_messages.items():
            try:
                thread = self.normalize_graph_thread(conv_id, conv_msgs, context)
                normalized_threads.append(thread)
            except Exception as exc:
                logger.warning(
                    "Microsoft Mail: failed to normalize thread %s: %s",
                    conv_id,
                    exc,
                )

        checkpoint = SyncCheckpoint(
            connected_account_id=context.connected_account_id,
            status="success",
            items_fetched=len(normalized_messages),
        )

        return FetchResult(
            messages=normalized_messages,
            threads=normalized_threads,
            checkpoint=checkpoint,
        )

    def validate_credentials(
        self, context: ConnectorExecutionContext
    ) -> bool:
        """Validate Microsoft Graph credentials with a lightweight call."""
        access_token = (context.sync_metadata or {}).get("_access_token")
        if not access_token:
            return False

        try:
            import httpx

            headers = {"Authorization": f"Bearer {access_token}"}
            response = httpx.get(
                f"{self.GRAPH_BASE}/me",
                headers=headers,
                timeout=10.0,
            )
            return response.status_code == 200
        except Exception:
            return False

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

