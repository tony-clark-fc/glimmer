"""Telegram companion intake connector.

ARCH:TelegramConnector
ARCH:TelegramConnectorScope
ARCH:TelegramIdentitySessionBinding

Responsible for:
- Receiving inbound operator messages from Telegram
- Mapping Telegram identity/chat context into ChannelSession/TelegramConversationState
- Normalizing inbound text into ImportedSignal records
- Handing off to the Telegram Companion Graph

Scope limits: This is NOT the full web application surface.
It supports conversational access, lightweight retrieval, note capture,
and short-turn interaction.
"""

from __future__ import annotations

from typing import Any, Optional

from app.connectors.base import BaseConnector
from app.connectors.contracts import (
    ConnectorExecutionContext,
    FetchResult,
    NormalizedSignalData,
)


class TelegramIntakeConnector(BaseConnector):
    """Telegram companion intake connector.

    ARCH:TelegramConnector
    ARCH:ConnectorPrinciple.ChannelAdapters
    """

    @property
    def provider_type(self) -> str:
        return "telegram"

    @property
    def connector_type(self) -> str:
        return "telegram_intake"

    @property
    def supported_profile_types(self) -> list[str]:
        return ["telegram_chat"]

    def fetch_and_normalize(
        self, context: ConnectorExecutionContext
    ) -> FetchResult:
        """Telegram is event-driven (webhook), not poll-based."""
        raise NotImplementedError(
            "Telegram uses webhook-based intake, not fetch. "
            "Use normalize_telegram_message() for individual messages."
        )

    def validate_credentials(
        self, context: ConnectorExecutionContext
    ) -> bool:
        raise NotImplementedError(
            "Telegram bot validation requires bot token provisioning."
        )

    @staticmethod
    def normalize_telegram_message(
        update: dict[str, Any],
        context: ConnectorExecutionContext,
    ) -> NormalizedSignalData:
        """Normalize a single Telegram update into an ImportedSignal.

        Preserves:
        - Telegram chat ID and message ID
        - Sender identity (username, first_name)
        - Message text
        - Timestamp

        ARCH:TelegramIdentitySessionBinding
        """
        message = update.get("message", {})
        chat = message.get("chat", {})
        from_user = message.get("from", {})

        sender = from_user.get("username") or from_user.get("first_name", "unknown")

        return NormalizedSignalData(
            signal_type="telegram_import",
            source_label=f"telegram:{chat.get('id', 'unknown')}",
            content=message.get("text", ""),
            raw_metadata={
                "telegram_update_id": update.get("update_id"),
                "telegram_message_id": message.get("message_id"),
                "telegram_chat_id": chat.get("id"),
                "telegram_chat_type": chat.get("type"),
                "telegram_sender_id": from_user.get("id"),
                "telegram_sender_username": from_user.get("username"),
                "telegram_sender_name": from_user.get("first_name"),
                "telegram_date": message.get("date"),
                "provider": "telegram",
                "account_label": context.account_label,
            },
        )

