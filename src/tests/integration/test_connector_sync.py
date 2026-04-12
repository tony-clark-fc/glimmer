"""Sync-state and failure visibility tests.

TEST:Connector.SyncFailure.VisibleState
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.connectors.contracts import SyncCheckpoint
from app.connectors.sync import SyncStateManager
from app.models.source import ConnectedAccount


def _make_account(db_session) -> ConnectedAccount:
    account = ConnectedAccount(
        provider_type="google",
        account_label="sync-test@example.com",
        status="active",
    )
    db_session.add(account)
    db_session.flush()
    return account


class TestSyncFailureVisibleState:
    """TEST:Connector.SyncFailure.VisibleState

    Proves sync and authorization failures are observable,
    not silently swallowed.
    """

    def test_successful_sync_updates_metadata(self, db_session) -> None:
        account = _make_account(db_session)
        manager = SyncStateManager(db_session)

        checkpoint = SyncCheckpoint(
            connected_account_id=account.id,
            status="success",
            items_fetched=42,
            sync_cursor={"historyId": "abc123"},
        )
        manager.apply_checkpoint(checkpoint)

        status = manager.get_last_sync_status(account.id)
        assert status is not None
        assert status["last_sync_status"] == "success"
        assert status["last_sync_items_fetched"] == 42
        assert status["sync_cursor"] == {"historyId": "abc123"}

    def test_failed_sync_preserves_error(self, db_session) -> None:
        account = _make_account(db_session)
        manager = SyncStateManager(db_session)

        checkpoint = SyncCheckpoint(
            connected_account_id=account.id,
            status="failed",
            error_summary="OAuth token expired — re-authorization required",
            items_fetched=0,
        )
        manager.apply_checkpoint(checkpoint)

        status = manager.get_last_sync_status(account.id)
        assert status["last_sync_status"] == "failed"
        assert "OAuth token expired" in status["last_error_summary"]
        assert "last_error_at" in status

    def test_successful_sync_clears_previous_error(self, db_session) -> None:
        account = _make_account(db_session)
        manager = SyncStateManager(db_session)

        # First: a failure
        fail_cp = SyncCheckpoint(
            connected_account_id=account.id,
            status="failed",
            error_summary="API rate limited",
        )
        manager.apply_checkpoint(fail_cp)

        # Then: success
        ok_cp = SyncCheckpoint(
            connected_account_id=account.id,
            status="success",
            items_fetched=10,
        )
        manager.apply_checkpoint(ok_cp)

        status = manager.get_last_sync_status(account.id)
        assert status["last_sync_status"] == "success"
        assert "last_error_summary" not in status
        assert "last_error_at" not in status

    def test_record_failure_convenience(self, db_session) -> None:
        account = _make_account(db_session)
        manager = SyncStateManager(db_session)

        cp = manager.record_failure(
            account.id, "Connection refused — provider API down"
        )
        assert cp.status == "failed"

        status = manager.get_last_sync_status(account.id)
        assert status["last_sync_status"] == "failed"
        assert "Connection refused" in status["last_error_summary"]

    def test_partial_sync_preserves_partial_status(self, db_session) -> None:
        account = _make_account(db_session)
        manager = SyncStateManager(db_session)

        checkpoint = SyncCheckpoint(
            connected_account_id=account.id,
            status="partial",
            items_fetched=15,
            error_summary="Timeout after 15 items — will retry",
        )
        manager.apply_checkpoint(checkpoint)

        status = manager.get_last_sync_status(account.id)
        assert status["last_sync_status"] == "partial"
        assert status["last_sync_items_fetched"] == 15

    def test_nonexistent_account_returns_none(self, db_session) -> None:
        manager = SyncStateManager(db_session)
        status = manager.get_last_sync_status(uuid.uuid4())
        assert status is None

