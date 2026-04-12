"""Sync-state tracking for connector runs.

ARCH:ConnectorSyncStateTracking
ARCH:ConnectorFailureRecovery

Manages sync checkpoints on ConnectedAccount records to support
incremental fetch, failure visibility, and diagnosable sync state.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.connectors.contracts import SyncCheckpoint
from app.models.source import ConnectedAccount


class SyncStateManager:
    """Manages sync-state metadata on ConnectedAccount records.

    After each connector run, the sync manager updates the account's
    sync_metadata with the latest checkpoint. This supports:
    - Incremental fetch (cursors, watermarks)
    - Failure visibility (error states)
    - Diagnosable sync history

    ARCH:ConnectorSyncStateTracking
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def apply_checkpoint(self, checkpoint: SyncCheckpoint) -> None:
        """Apply a sync checkpoint to the connected account.

        Updates the account's sync_metadata with checkpoint state.
        """
        account = self._session.get(
            ConnectedAccount, checkpoint.connected_account_id
        )
        if account is None:
            return

        current_metadata = account.sync_metadata or {}
        current_metadata.update(
            {
                "last_sync_at": checkpoint.last_sync_at.isoformat(),
                "last_sync_status": checkpoint.status,
                "last_sync_items_fetched": checkpoint.items_fetched,
                "sync_cursor": checkpoint.sync_cursor,
            }
        )

        if checkpoint.status == "failed":
            current_metadata["last_error_summary"] = checkpoint.error_summary
            current_metadata["last_error_at"] = checkpoint.last_sync_at.isoformat()
        else:
            # Clear error state on success
            current_metadata.pop("last_error_summary", None)
            current_metadata.pop("last_error_at", None)

        account.sync_metadata = current_metadata
        self._session.flush()

    def record_failure(
        self,
        account_id: uuid.UUID,
        error_summary: str,
    ) -> SyncCheckpoint:
        """Convenience: create and apply a failure checkpoint.

        Returns the checkpoint for reference.
        """
        checkpoint = SyncCheckpoint(
            connected_account_id=account_id,
            status="failed",
            error_summary=error_summary,
            items_fetched=0,
        )
        self.apply_checkpoint(checkpoint)
        return checkpoint

    def get_last_sync_status(self, account_id: uuid.UUID) -> Optional[dict]:
        """Get the last sync status for an account.

        Returns the sync_metadata dict or None if no sync recorded.
        """
        account = self._session.get(ConnectedAccount, account_id)
        if account is None:
            return None
        return account.sync_metadata

