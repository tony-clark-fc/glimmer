"""Domain connected-account and source-layer persistence tests.

TEST:Domain.MultiAccount.ProvenancePersistence
TEST:Domain.SourceRecords.MessagesThreadsEventsPersistSeparately
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.models.source import (
    AccountProfile,
    CalendarEvent,
    ConnectedAccount,
    ImportedSignal,
    Message,
    MessageThread,
)


# ── TEST:Domain.MultiAccount.ProvenancePersistence ───────────────────


class TestConnectedAccountProvenance:
    """Connected accounts preserve multi-account provenance."""

    def test_create_google_account(self, db_session) -> None:
        acct = ConnectedAccount(
            provider_type="google",
            account_label="Personal Gmail",
            account_address="tony@gmail.com",
        )
        db_session.add(acct)
        db_session.flush()

        fetched = db_session.get(ConnectedAccount, acct.id)
        assert fetched is not None
        assert fetched.provider_type == "google"
        assert fetched.account_address == "tony@gmail.com"

    def test_create_microsoft_account(self, db_session) -> None:
        acct = ConnectedAccount(
            provider_type="microsoft_365",
            account_label="Work O365",
            account_address="tony@contoso.com",
            tenant_context="contoso.onmicrosoft.com",
        )
        db_session.add(acct)
        db_session.flush()

        fetched = db_session.get(ConnectedAccount, acct.id)
        assert fetched is not None
        assert fetched.tenant_context == "contoso.onmicrosoft.com"

    def test_multiple_accounts_coexist(self, db_session) -> None:
        a1 = ConnectedAccount(
            provider_type="google",
            account_label="Personal",
            account_address="me@gmail.com",
        )
        a2 = ConnectedAccount(
            provider_type="microsoft_365",
            account_label="Work",
            account_address="me@work.com",
        )
        a3 = ConnectedAccount(
            provider_type="google_workspace",
            account_label="Consulting",
            account_address="me@consulting.io",
        )
        db_session.add_all([a1, a2, a3])
        db_session.flush()

        # All three have distinct IDs
        assert len({a1.id, a2.id, a3.id}) == 3

    def test_account_profile_links_to_account(self, db_session) -> None:
        acct = ConnectedAccount(
            provider_type="google",
            account_label="Main Gmail",
            account_address="tony@gmail.com",
        )
        db_session.add(acct)
        db_session.flush()

        profile = AccountProfile(
            account_id=acct.id,
            profile_type="mail",
            profile_label="Primary Inbox",
            profile_address="tony@gmail.com",
        )
        db_session.add(profile)
        db_session.flush()

        db_session.refresh(acct)
        assert len(acct.profiles) == 1
        assert acct.profiles[0].profile_type == "mail"

    def test_message_preserves_account_provenance(self, db_session) -> None:
        """A message records which connected account it came from."""
        acct = ConnectedAccount(
            provider_type="google",
            account_label="Gmail",
            account_address="tony@gmail.com",
        )
        db_session.add(acct)
        db_session.flush()

        msg = Message(
            connected_account_id=acct.id,
            source_type="gmail",
            external_message_id="msg-abc-123",
            subject="Project update",
            sender_identity="alice@example.com",
        )
        db_session.add(msg)
        db_session.flush()

        fetched = db_session.get(Message, msg.id)
        assert fetched is not None
        assert fetched.connected_account_id == acct.id
        assert fetched.source_type == "gmail"

    def test_event_preserves_account_provenance(self, db_session) -> None:
        """A calendar event records which connected account it came from."""
        acct = ConnectedAccount(
            provider_type="microsoft_365",
            account_label="Work",
            account_address="tony@contoso.com",
        )
        db_session.add(acct)
        db_session.flush()

        evt = CalendarEvent(
            connected_account_id=acct.id,
            external_event_id="evt-xyz-789",
            title="Design Review",
            start_time=datetime(2026, 5, 1, 10, 0, tzinfo=timezone.utc),
            end_time=datetime(2026, 5, 1, 11, 0, tzinfo=timezone.utc),
            source_calendar="Work Calendar",
        )
        db_session.add(evt)
        db_session.flush()

        fetched = db_session.get(CalendarEvent, evt.id)
        assert fetched is not None
        assert fetched.connected_account_id == acct.id
        assert fetched.source_calendar == "Work Calendar"


# ── TEST:Domain.SourceRecords.MessagesThreadsEventsPersistSeparately ─


class TestSourceRecordsSeparation:
    """Messages, threads, events, and signals persist as distinct entities."""

    def _make_account(self, db_session) -> ConnectedAccount:
        acct = ConnectedAccount(
            provider_type="google",
            account_label="Test Account",
            account_address="test@gmail.com",
        )
        db_session.add(acct)
        db_session.flush()
        return acct

    def test_thread_persists_independently(self, db_session) -> None:
        acct = self._make_account(db_session)
        thread = MessageThread(
            connected_account_id=acct.id,
            source_type="gmail",
            external_thread_id="thread-001",
            derived_subject="Re: Q2 roadmap",
            participant_set={"to": ["alice@ex.com"], "cc": ["bob@ex.com"]},
        )
        db_session.add(thread)
        db_session.flush()

        fetched = db_session.get(MessageThread, thread.id)
        assert fetched is not None
        assert fetched.external_thread_id == "thread-001"
        assert fetched.participant_set["to"] == ["alice@ex.com"]

    def test_message_links_to_thread(self, db_session) -> None:
        acct = self._make_account(db_session)
        thread = MessageThread(
            connected_account_id=acct.id,
            source_type="gmail",
            external_thread_id="thread-002",
        )
        db_session.add(thread)
        db_session.flush()

        msg = Message(
            connected_account_id=acct.id,
            thread_id=thread.id,
            source_type="gmail",
            external_message_id="msg-in-thread-002",
            external_thread_id="thread-002",
            subject="Re: Budget",
        )
        db_session.add(msg)
        db_session.flush()

        db_session.refresh(thread)
        assert len(thread.messages) == 1
        assert thread.messages[0].external_message_id == "msg-in-thread-002"

    def test_message_exists_without_thread(self, db_session) -> None:
        """A message can exist without a thread reference."""
        acct = self._make_account(db_session)
        msg = Message(
            connected_account_id=acct.id,
            source_type="gmail",
            external_message_id="standalone-msg",
            subject="No thread",
        )
        db_session.add(msg)
        db_session.flush()

        fetched = db_session.get(Message, msg.id)
        assert fetched is not None
        assert fetched.thread_id is None

    def test_calendar_event_persists_separately(self, db_session) -> None:
        acct = self._make_account(db_session)
        evt = CalendarEvent(
            connected_account_id=acct.id,
            external_event_id="cal-evt-001",
            title="Sprint Planning",
            start_time=datetime(2026, 5, 5, 9, 0, tzinfo=timezone.utc),
            end_time=datetime(2026, 5, 5, 10, 0, tzinfo=timezone.utc),
            participants={"attendees": ["alice@ex.com", "bob@ex.com"]},
            location_or_link="https://meet.google.com/abc",
        )
        db_session.add(evt)
        db_session.flush()

        fetched = db_session.get(CalendarEvent, evt.id)
        assert fetched is not None
        assert fetched.title == "Sprint Planning"
        assert "alice@ex.com" in fetched.participants["attendees"]

    def test_imported_signal_persists_separately(self, db_session) -> None:
        acct = self._make_account(db_session)
        sig = ImportedSignal(
            connected_account_id=acct.id,
            signal_type="manual_paste",
            source_label="WhatsApp export",
            content="Hey, here's that update you asked about...",
            raw_metadata={"source": "whatsapp", "chat_name": "Project Alpha"},
        )
        db_session.add(sig)
        db_session.flush()

        fetched = db_session.get(ImportedSignal, sig.id)
        assert fetched is not None
        assert fetched.signal_type == "manual_paste"
        assert fetched.raw_metadata["chat_name"] == "Project Alpha"

    def test_imported_signal_without_account(self, db_session) -> None:
        """An imported signal can exist without a connected account."""
        sig = ImportedSignal(
            signal_type="voice_transcript",
            content="Voice memo content here",
        )
        db_session.add(sig)
        db_session.flush()

        fetched = db_session.get(ImportedSignal, sig.id)
        assert fetched is not None
        assert fetched.connected_account_id is None

    def test_message_full_provenance_chain(self, db_session) -> None:
        """Message with full provenance: account→profile→thread→message."""
        acct = self._make_account(db_session)
        profile = AccountProfile(
            account_id=acct.id,
            profile_type="mail",
            profile_label="Primary",
        )
        db_session.add(profile)
        db_session.flush()

        thread = MessageThread(
            connected_account_id=acct.id,
            source_type="gmail",
            external_thread_id="full-chain-thread",
        )
        db_session.add(thread)
        db_session.flush()

        msg = Message(
            connected_account_id=acct.id,
            account_profile_id=profile.id,
            thread_id=thread.id,
            source_type="gmail",
            external_message_id="full-chain-msg",
            subject="Full provenance",
            body_text="This message has complete provenance.",
            sent_at=datetime(2026, 4, 13, 12, 0, tzinfo=timezone.utc),
            sender_identity="alice@example.com",
            recipient_identities={"to": ["tony@gmail.com"]},
            import_metadata={"sync_batch": "batch-42"},
        )
        db_session.add(msg)
        db_session.flush()

        fetched = db_session.get(Message, msg.id)
        assert fetched is not None
        assert fetched.connected_account_id == acct.id
        assert fetched.account_profile_id == profile.id
        assert fetched.thread_id == thread.id
        assert fetched.import_metadata["sync_batch"] == "batch-42"

