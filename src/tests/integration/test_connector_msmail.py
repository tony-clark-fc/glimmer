"""Microsoft mail normalization tests.

TEST:Connector.MicrosoftMail.NormalizationPreservesMailboxAndThread
"""

from __future__ import annotations

import uuid

from app.connectors.contracts import ConnectorExecutionContext
from app.connectors.microsoft.mail import MicrosoftMailConnector


def _make_context(**kwargs) -> ConnectorExecutionContext:
    defaults = {
        "connected_account_id": uuid.uuid4(),
        "provider_type": "microsoft",
        "account_label": "operator@company.com",
        "account_address": "operator@company.com",
        "tenant_context": "company.onmicrosoft.com",
    }
    defaults.update(kwargs)
    return ConnectorExecutionContext(**defaults)


GRAPH_MESSAGE_FIXTURE = {
    "id": "AAMkAGI2THMSG001",
    "conversationId": "AAQkAGI2THCONV001",
    "subject": "Budget Review - Q3",
    "from": {
        "emailAddress": {
            "name": "Bob Finance",
            "address": "bob@company.com",
        }
    },
    "toRecipients": [
        {"emailAddress": {"address": "operator@company.com"}},
        {"emailAddress": {"address": "cfo@company.com"}},
    ],
    "ccRecipients": [
        {"emailAddress": {"address": "assistant@company.com"}},
    ],
    "sentDateTime": "2026-04-13T14:30:00Z",
    "receivedDateTime": "2026-04-13T14:30:05Z",
    "body": {
        "contentType": "text",
        "content": "Please review the attached Q3 budget proposal.",
    },
    "parentFolderId": "inbox-folder-id",
    "importance": "high",
    "isRead": False,
}

GRAPH_CONVERSATION_FIXTURE = [
    {
        "id": "msg1",
        "conversationId": "AAQkAGI2THCONV001",
        "subject": "Budget Review - Q3",
        "from": {"emailAddress": {"address": "bob@company.com"}},
        "toRecipients": [{"emailAddress": {"address": "operator@company.com"}}],
        "receivedDateTime": "2026-04-13T14:30:05Z",
    },
    {
        "id": "msg2",
        "conversationId": "AAQkAGI2THCONV001",
        "subject": "Re: Budget Review - Q3",
        "from": {"emailAddress": {"address": "operator@company.com"}},
        "toRecipients": [{"emailAddress": {"address": "bob@company.com"}}],
        "receivedDateTime": "2026-04-13T15:00:00Z",
    },
]


class TestMicrosoftMailNormalization:
    """TEST:Connector.MicrosoftMail.NormalizationPreservesMailboxAndThread"""

    def test_message_preserves_message_id(self) -> None:
        ctx = _make_context()
        msg = MicrosoftMailConnector.normalize_graph_message(GRAPH_MESSAGE_FIXTURE, ctx)
        assert msg.external_message_id == "AAMkAGI2THMSG001"

    def test_message_preserves_conversation_id_as_thread(self) -> None:
        ctx = _make_context()
        msg = MicrosoftMailConnector.normalize_graph_message(GRAPH_MESSAGE_FIXTURE, ctx)
        assert msg.external_thread_id == "AAQkAGI2THCONV001"

    def test_message_source_type_is_microsoft_mail(self) -> None:
        ctx = _make_context()
        msg = MicrosoftMailConnector.normalize_graph_message(GRAPH_MESSAGE_FIXTURE, ctx)
        assert msg.source_type == "microsoft_mail"

    def test_message_preserves_subject(self) -> None:
        ctx = _make_context()
        msg = MicrosoftMailConnector.normalize_graph_message(GRAPH_MESSAGE_FIXTURE, ctx)
        assert msg.subject == "Budget Review - Q3"

    def test_message_preserves_sender_with_name(self) -> None:
        ctx = _make_context()
        msg = MicrosoftMailConnector.normalize_graph_message(GRAPH_MESSAGE_FIXTURE, ctx)
        assert "Bob Finance" in msg.sender_identity
        assert "bob@company.com" in msg.sender_identity

    def test_message_preserves_recipients(self) -> None:
        ctx = _make_context()
        msg = MicrosoftMailConnector.normalize_graph_message(GRAPH_MESSAGE_FIXTURE, ctx)
        assert "to" in msg.recipient_identities
        assert "operator@company.com" in msg.recipient_identities["to"]
        assert "cc" in msg.recipient_identities
        assert "assistant@company.com" in msg.recipient_identities["cc"]

    def test_message_extracts_text_body(self) -> None:
        ctx = _make_context()
        msg = MicrosoftMailConnector.normalize_graph_message(GRAPH_MESSAGE_FIXTURE, ctx)
        assert msg.body_text is not None
        assert "Q3 budget proposal" in msg.body_text

    def test_message_preserves_tenant_context_in_metadata(self) -> None:
        """ARCH:MicrosoftTenantMailboxContext"""
        ctx = _make_context(tenant_context="acme.onmicrosoft.com")
        msg = MicrosoftMailConnector.normalize_graph_message(GRAPH_MESSAGE_FIXTURE, ctx)
        assert msg.import_metadata["tenant_context"] == "acme.onmicrosoft.com"
        assert msg.import_metadata["provider"] == "microsoft_graph"

    def test_message_preserves_folder_context(self) -> None:
        ctx = _make_context()
        msg = MicrosoftMailConnector.normalize_graph_message(GRAPH_MESSAGE_FIXTURE, ctx)
        assert msg.import_metadata["folder"] == "inbox-folder-id"

    def test_message_parses_timestamps(self) -> None:
        ctx = _make_context()
        msg = MicrosoftMailConnector.normalize_graph_message(GRAPH_MESSAGE_FIXTURE, ctx)
        assert msg.sent_at is not None
        assert msg.received_at is not None
        assert msg.received_at.tzinfo is not None

    def test_thread_preserves_conversation_id(self) -> None:
        ctx = _make_context()
        thread = MicrosoftMailConnector.normalize_graph_thread(
            "AAQkAGI2THCONV001", GRAPH_CONVERSATION_FIXTURE, ctx
        )
        assert thread.external_thread_id == "AAQkAGI2THCONV001"

    def test_thread_source_type_is_microsoft_mail(self) -> None:
        ctx = _make_context()
        thread = MicrosoftMailConnector.normalize_graph_thread(
            "AAQkAGI2THCONV001", GRAPH_CONVERSATION_FIXTURE, ctx
        )
        assert thread.source_type == "microsoft_mail"

    def test_thread_collects_participants(self) -> None:
        ctx = _make_context()
        thread = MicrosoftMailConnector.normalize_graph_thread(
            "AAQkAGI2THCONV001", GRAPH_CONVERSATION_FIXTURE, ctx
        )
        addrs = thread.participant_set["addresses"]
        assert "bob@company.com" in addrs
        assert "operator@company.com" in addrs

