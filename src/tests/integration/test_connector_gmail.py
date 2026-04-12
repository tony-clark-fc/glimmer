"""Gmail normalization tests.

TEST:Connector.GoogleMail.NormalizationPreservesThreadAndAccount
"""

from __future__ import annotations

import base64
import uuid

from app.connectors.contracts import ConnectorExecutionContext
from app.connectors.google.gmail import GmailConnector


def _make_context(**kwargs) -> ConnectorExecutionContext:
    defaults = {
        "connected_account_id": uuid.uuid4(),
        "provider_type": "google",
        "account_label": "operator@gmail.com",
        "account_address": "operator@gmail.com",
    }
    defaults.update(kwargs)
    return ConnectorExecutionContext(**defaults)


def _encode_body(text: str) -> str:
    return base64.urlsafe_b64encode(text.encode()).decode()


# Fixtures: realistic Gmail API payloads
GMAIL_MESSAGE_FIXTURE = {
    "id": "msg_abc123",
    "threadId": "thread_xyz789",
    "labelIds": ["INBOX", "IMPORTANT"],
    "snippet": "Hey, regarding the Q3 milestone...",
    "internalDate": "1744540800000",  # epoch millis
    "payload": {
        "mimeType": "multipart/alternative",
        "headers": [
            {"name": "From", "value": "alice@example.com"},
            {"name": "To", "value": "operator@gmail.com, bob@example.com"},
            {"name": "Cc", "value": "carol@example.com"},
            {"name": "Subject", "value": "Q3 Milestone Update"},
            {"name": "Date", "value": "Sun, 13 Apr 2025 12:00:00 +0000"},
        ],
        "parts": [
            {
                "mimeType": "text/plain",
                "body": {"data": _encode_body("Hey, regarding the Q3 milestone...")},
            },
            {
                "mimeType": "text/html",
                "body": {"data": _encode_body("<p>Hey, regarding the Q3 milestone...</p>")},
            },
        ],
    },
}

GMAIL_THREAD_FIXTURE = {
    "id": "thread_xyz789",
    "messages": [
        {
            "id": "msg_abc123",
            "threadId": "thread_xyz789",
            "internalDate": "1744540800000",
            "payload": {
                "headers": [
                    {"name": "From", "value": "alice@example.com"},
                    {"name": "To", "value": "operator@gmail.com"},
                    {"name": "Subject", "value": "Q3 Milestone Update"},
                ],
            },
        },
        {
            "id": "msg_def456",
            "threadId": "thread_xyz789",
            "internalDate": "1744627200000",
            "payload": {
                "headers": [
                    {"name": "From", "value": "operator@gmail.com"},
                    {"name": "To", "value": "alice@example.com"},
                    {"name": "Subject", "value": "Re: Q3 Milestone Update"},
                ],
            },
        },
    ],
}


class TestGmailNormalization:
    """TEST:Connector.GoogleMail.NormalizationPreservesThreadAndAccount"""

    def test_message_preserves_gmail_message_id(self) -> None:
        ctx = _make_context()
        msg = GmailConnector.normalize_gmail_payload(GMAIL_MESSAGE_FIXTURE, ctx)
        assert msg.external_message_id == "msg_abc123"

    def test_message_preserves_thread_id(self) -> None:
        ctx = _make_context()
        msg = GmailConnector.normalize_gmail_payload(GMAIL_MESSAGE_FIXTURE, ctx)
        assert msg.external_thread_id == "thread_xyz789"

    def test_message_source_type_is_gmail(self) -> None:
        ctx = _make_context()
        msg = GmailConnector.normalize_gmail_payload(GMAIL_MESSAGE_FIXTURE, ctx)
        assert msg.source_type == "gmail"

    def test_message_preserves_subject(self) -> None:
        ctx = _make_context()
        msg = GmailConnector.normalize_gmail_payload(GMAIL_MESSAGE_FIXTURE, ctx)
        assert msg.subject == "Q3 Milestone Update"

    def test_message_preserves_sender(self) -> None:
        ctx = _make_context()
        msg = GmailConnector.normalize_gmail_payload(GMAIL_MESSAGE_FIXTURE, ctx)
        assert msg.sender_identity == "alice@example.com"

    def test_message_preserves_recipients(self) -> None:
        ctx = _make_context()
        msg = GmailConnector.normalize_gmail_payload(GMAIL_MESSAGE_FIXTURE, ctx)
        assert "to" in msg.recipient_identities
        assert "operator@gmail.com" in msg.recipient_identities["to"]
        assert "cc" in msg.recipient_identities
        assert "carol@example.com" in msg.recipient_identities["cc"]

    def test_message_extracts_body_text(self) -> None:
        ctx = _make_context()
        msg = GmailConnector.normalize_gmail_payload(GMAIL_MESSAGE_FIXTURE, ctx)
        assert msg.body_text is not None
        assert "Q3 milestone" in msg.body_text

    def test_message_preserves_account_label_in_metadata(self) -> None:
        ctx = _make_context(account_label="mywork@gmail.com")
        msg = GmailConnector.normalize_gmail_payload(GMAIL_MESSAGE_FIXTURE, ctx)
        assert msg.import_metadata["account_label"] == "mywork@gmail.com"
        assert msg.import_metadata["provider"] == "gmail"

    def test_message_preserves_gmail_labels(self) -> None:
        ctx = _make_context()
        msg = GmailConnector.normalize_gmail_payload(GMAIL_MESSAGE_FIXTURE, ctx)
        assert "INBOX" in msg.import_metadata["gmail_labels"]
        assert "IMPORTANT" in msg.import_metadata["gmail_labels"]

    def test_message_parses_received_at(self) -> None:
        ctx = _make_context()
        msg = GmailConnector.normalize_gmail_payload(GMAIL_MESSAGE_FIXTURE, ctx)
        assert msg.received_at is not None
        assert msg.received_at.tzinfo is not None

    def test_thread_preserves_thread_id(self) -> None:
        ctx = _make_context()
        thread = GmailConnector.normalize_gmail_thread(GMAIL_THREAD_FIXTURE, ctx)
        assert thread.external_thread_id == "thread_xyz789"

    def test_thread_source_type_is_gmail(self) -> None:
        ctx = _make_context()
        thread = GmailConnector.normalize_gmail_thread(GMAIL_THREAD_FIXTURE, ctx)
        assert thread.source_type == "gmail"

    def test_thread_derives_subject(self) -> None:
        ctx = _make_context()
        thread = GmailConnector.normalize_gmail_thread(GMAIL_THREAD_FIXTURE, ctx)
        assert thread.derived_subject == "Q3 Milestone Update"

    def test_thread_collects_participants(self) -> None:
        ctx = _make_context()
        thread = GmailConnector.normalize_gmail_thread(GMAIL_THREAD_FIXTURE, ctx)
        assert thread.participant_set is not None
        addrs = thread.participant_set["addresses"]
        assert "alice@example.com" in addrs
        assert "operator@gmail.com" in addrs

    def test_thread_has_last_activity(self) -> None:
        ctx = _make_context()
        thread = GmailConnector.normalize_gmail_thread(GMAIL_THREAD_FIXTURE, ctx)
        assert thread.last_activity_at is not None

