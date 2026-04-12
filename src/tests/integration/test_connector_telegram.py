"""Telegram intake normalization tests.

TEST:Connector.Telegram.InboundBecomesBoundedSignal
"""

from __future__ import annotations

import uuid

from app.connectors.contracts import ConnectorExecutionContext
from app.connectors.telegram.intake import TelegramIntakeConnector


def _make_context(**kwargs) -> ConnectorExecutionContext:
    defaults = {
        "connected_account_id": uuid.uuid4(),
        "provider_type": "telegram",
        "account_label": "glimmer_bot",
    }
    defaults.update(kwargs)
    return ConnectorExecutionContext(**defaults)


TELEGRAM_UPDATE_FIXTURE = {
    "update_id": 123456789,
    "message": {
        "message_id": 42,
        "date": 1744540800,
        "chat": {
            "id": 99887766,
            "type": "private",
        },
        "from": {
            "id": 11223344,
            "first_name": "Tony",
            "username": "tonyoperator",
        },
        "text": "What's on my plate for today?",
    },
}


class TestTelegramIntake:
    """TEST:Connector.Telegram.InboundBecomesBoundedSignal

    Proves Telegram does not bypass the core intake model.
    Inbound messages become bounded ImportedSignal records.
    """

    def test_signal_type_is_telegram_import(self) -> None:
        ctx = _make_context()
        signal = TelegramIntakeConnector.normalize_telegram_message(
            TELEGRAM_UPDATE_FIXTURE, ctx
        )
        assert signal.signal_type == "telegram_import"

    def test_content_preserves_message_text(self) -> None:
        ctx = _make_context()
        signal = TelegramIntakeConnector.normalize_telegram_message(
            TELEGRAM_UPDATE_FIXTURE, ctx
        )
        assert signal.content == "What's on my plate for today?"

    def test_source_label_includes_chat_id(self) -> None:
        ctx = _make_context()
        signal = TelegramIntakeConnector.normalize_telegram_message(
            TELEGRAM_UPDATE_FIXTURE, ctx
        )
        assert "99887766" in signal.source_label

    def test_metadata_preserves_telegram_identifiers(self) -> None:
        ctx = _make_context()
        signal = TelegramIntakeConnector.normalize_telegram_message(
            TELEGRAM_UPDATE_FIXTURE, ctx
        )
        meta = signal.raw_metadata
        assert meta["telegram_update_id"] == 123456789
        assert meta["telegram_message_id"] == 42
        assert meta["telegram_chat_id"] == 99887766
        assert meta["telegram_sender_id"] == 11223344

    def test_metadata_preserves_sender_identity(self) -> None:
        ctx = _make_context()
        signal = TelegramIntakeConnector.normalize_telegram_message(
            TELEGRAM_UPDATE_FIXTURE, ctx
        )
        meta = signal.raw_metadata
        assert meta["telegram_sender_username"] == "tonyoperator"
        assert meta["telegram_sender_name"] == "Tony"

    def test_metadata_preserves_provider_label(self) -> None:
        ctx = _make_context()
        signal = TelegramIntakeConnector.normalize_telegram_message(
            TELEGRAM_UPDATE_FIXTURE, ctx
        )
        assert signal.raw_metadata["provider"] == "telegram"

