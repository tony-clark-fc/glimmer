"""Connector execution context resolution tests.

TEST:Connector.AccountProfiles.ExecutionUsesCorrectProfile
"""

from __future__ import annotations

import uuid

import pytest

from app.connectors.context import (
    AccountInactiveError,
    AccountNotFoundError,
    ConnectorContextResolver,
    ProfileNotFoundError,
)
from app.models.source import ConnectedAccount, AccountProfile


class TestExecutionContextResolution:
    """TEST:Connector.AccountProfiles.ExecutionUsesCorrectProfile

    Proves multi-account separation is real in execution, not
    merely stored metadata.
    """

    def test_resolve_active_account(self, db_session) -> None:
        """Resolves context from an active connected account."""
        account = ConnectedAccount(
            provider_type="google",
            account_label="work@example.com",
            account_address="work@example.com",
            tenant_context="example.com",
            status="active",
            sync_metadata={"last_sync_at": "2026-04-13T10:00:00Z"},
        )
        db_session.add(account)
        db_session.flush()

        resolver = ConnectorContextResolver(db_session)
        ctx = resolver.resolve(account.id)

        assert ctx.connected_account_id == account.id
        assert ctx.provider_type == "google"
        assert ctx.account_label == "work@example.com"
        assert ctx.account_address == "work@example.com"
        assert ctx.tenant_context == "example.com"
        assert ctx.sync_metadata is not None

    def test_resolve_with_profile(self, db_session) -> None:
        """Resolves context with a specific account profile."""
        account = ConnectedAccount(
            provider_type="google",
            account_label="personal@gmail.com",
            status="active",
        )
        db_session.add(account)
        db_session.flush()

        profile = AccountProfile(
            account_id=account.id,
            profile_type="calendar",
            profile_label="Work Calendar",
            profile_address="work-cal@group.calendar.google.com",
        )
        db_session.add(profile)
        db_session.flush()

        resolver = ConnectorContextResolver(db_session)
        ctx = resolver.resolve(account.id, profile_id=profile.id)

        assert ctx.connected_account_id == account.id
        assert ctx.profile_id == profile.id
        assert ctx.profile_type == "calendar"
        assert ctx.profile_label == "Work Calendar"

    def test_resolve_different_accounts_return_different_contexts(self, db_session) -> None:
        """Two different accounts produce distinct execution contexts."""
        google_acct = ConnectedAccount(
            provider_type="google",
            account_label="me@gmail.com",
            status="active",
        )
        ms_acct = ConnectedAccount(
            provider_type="microsoft_365",
            account_label="me@company.com",
            tenant_context="company.onmicrosoft.com",
            status="active",
        )
        db_session.add_all([google_acct, ms_acct])
        db_session.flush()

        resolver = ConnectorContextResolver(db_session)
        ctx_g = resolver.resolve(google_acct.id)
        ctx_m = resolver.resolve(ms_acct.id)

        assert ctx_g.connected_account_id != ctx_m.connected_account_id
        assert ctx_g.provider_type == "google"
        assert ctx_m.provider_type == "microsoft_365"
        assert ctx_m.tenant_context == "company.onmicrosoft.com"

    def test_resolve_nonexistent_account_raises(self, db_session) -> None:
        """Resolving a non-existent account raises AccountNotFoundError."""
        resolver = ConnectorContextResolver(db_session)
        with pytest.raises(AccountNotFoundError):
            resolver.resolve(uuid.uuid4())

    def test_resolve_inactive_account_raises(self, db_session) -> None:
        """Resolving a suspended account raises AccountInactiveError."""
        account = ConnectedAccount(
            provider_type="google",
            account_label="suspended@example.com",
            status="suspended",
        )
        db_session.add(account)
        db_session.flush()

        resolver = ConnectorContextResolver(db_session)
        with pytest.raises(AccountInactiveError) as exc_info:
            resolver.resolve(account.id)
        assert exc_info.value.status == "suspended"

    def test_resolve_profile_not_found_raises(self, db_session) -> None:
        """Resolving a non-existent profile raises ProfileNotFoundError."""
        account = ConnectedAccount(
            provider_type="google",
            account_label="test@example.com",
            status="active",
        )
        db_session.add(account)
        db_session.flush()

        resolver = ConnectorContextResolver(db_session)
        with pytest.raises(ProfileNotFoundError):
            resolver.resolve(account.id, profile_id=uuid.uuid4())

    def test_resolve_profile_from_wrong_account_raises(self, db_session) -> None:
        """A profile from another account is rejected."""
        acct1 = ConnectedAccount(
            provider_type="google", account_label="a@example.com", status="active"
        )
        acct2 = ConnectedAccount(
            provider_type="google", account_label="b@example.com", status="active"
        )
        db_session.add_all([acct1, acct2])
        db_session.flush()

        profile = AccountProfile(
            account_id=acct2.id, profile_type="mail", profile_label="Mail"
        )
        db_session.add(profile)
        db_session.flush()

        resolver = ConnectorContextResolver(db_session)
        with pytest.raises(ProfileNotFoundError):
            resolver.resolve(acct1.id, profile_id=profile.id)

    def test_resolve_all_profiles(self, db_session) -> None:
        """resolve_all_profiles returns one context per profile."""
        account = ConnectedAccount(
            provider_type="google",
            account_label="multi@example.com",
            status="active",
        )
        db_session.add(account)
        db_session.flush()

        p1 = AccountProfile(
            account_id=account.id, profile_type="mail", profile_label="Inbox"
        )
        p2 = AccountProfile(
            account_id=account.id, profile_type="calendar", profile_label="Work Cal"
        )
        db_session.add_all([p1, p2])
        db_session.flush()

        resolver = ConnectorContextResolver(db_session)
        contexts = resolver.resolve_all_profiles(account.id)

        assert len(contexts) == 2
        profile_labels = {c.profile_label for c in contexts}
        assert "Inbox" in profile_labels
        assert "Work Cal" in profile_labels
        # All share the same account
        for ctx in contexts:
            assert ctx.connected_account_id == account.id

    def test_list_active_accounts(self, db_session) -> None:
        """list_active_accounts returns only active accounts."""
        active = ConnectedAccount(
            provider_type="google", account_label="active@example.com", status="active"
        )
        inactive = ConnectedAccount(
            provider_type="google", account_label="gone@example.com", status="revoked"
        )
        db_session.add_all([active, inactive])
        db_session.flush()

        resolver = ConnectorContextResolver(db_session)
        accounts = resolver.list_active_accounts()

        labels = {a.account_label for a in accounts}
        assert "active@example.com" in labels
        assert "gone@example.com" not in labels

    def test_list_active_accounts_filter_by_provider(self, db_session) -> None:
        """list_active_accounts can filter by provider type."""
        google = ConnectedAccount(
            provider_type="google", account_label="g@example.com", status="active"
        )
        ms = ConnectedAccount(
            provider_type="microsoft_365", account_label="m@example.com", status="active"
        )
        db_session.add_all([google, ms])
        db_session.flush()

        resolver = ConnectorContextResolver(db_session)
        google_only = resolver.list_active_accounts(provider_type="google")

        labels = {a.account_label for a in google_only}
        assert "g@example.com" in labels
        assert "m@example.com" not in labels

