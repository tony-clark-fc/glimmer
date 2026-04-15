/**
 * MindMapToolbar — confirm/discard controls for the mind-map working state.
 *
 * ARCH:PersonaPage.StagedPersistence
 * ARCH:StateOwnershipBoundaries
 * PLAN:WorkstreamE.PackageE14.PersonaPageStagedPersistence
 * REQ:PersonaPageStagedPersistence
 *
 * Shows:
 * - Pending / accepted / discarded counts
 * - Accept All button
 * - Confirm & Save button (commits to database)
 * - Discard All button (abandons session)
 * - Saving indicator
 * - Unsaved changes warning
 */

"use client";

import { useCallback, useState } from "react";
import type { WorkingStateActions } from "./use-working-state";

interface MindMapToolbarProps {
  actions: WorkingStateActions;
}

export function MindMapToolbar({ actions }: MindMapToolbarProps) {
  const [showDiscardConfirm, setShowDiscardConfirm] = useState(false);
  const [confirmResult, setConfirmResult] = useState<{
    count: number;
  } | null>(null);

  const handleConfirm = useCallback(async () => {
    // Must have accepted nodes
    if (actions.acceptedCount === 0) return;
    const result = await actions.confirmAll();
    if (result) {
      setConfirmResult({ count: result.persisted_count });
    }
  }, [actions]);

  const handleDiscard = useCallback(async () => {
    await actions.discardAll();
    setShowDiscardConfirm(false);
  }, [actions]);

  // Terminal states
  if (actions.isConfirmed) {
    return (
      <div
        className="flex items-center gap-3 px-4 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20"
        data-testid="mindmap-toolbar-confirmed"
      >
        <span className="text-emerald-400 text-xs font-bold">✓ Confirmed</span>
        {confirmResult && (
          <span className="text-[10px] text-muted-light">
            {confirmResult.count} entities saved to database
          </span>
        )}
      </div>
    );
  }

  if (actions.isDiscarded) {
    return (
      <div
        className="flex items-center gap-3 px-4 py-2 rounded-xl bg-error/10 border border-error/20"
        data-testid="mindmap-toolbar-discarded"
      >
        <span className="text-error text-xs font-bold">✗ Discarded</span>
        <span className="text-[10px] text-muted-light">
          Working state abandoned — nothing was persisted
        </span>
      </div>
    );
  }

  const totalNodes =
    actions.pendingCount + actions.acceptedCount + actions.discardedCount;

  return (
    <div
      className="flex items-center gap-3 flex-wrap"
      data-testid="mindmap-toolbar"
    >
      {/* Counts */}
      <div className="flex items-center gap-2 text-[10px]">
        {actions.pendingCount > 0 && (
          <span
            className="px-2 py-0.5 rounded-full bg-tertiary/20 text-tertiary font-bold"
            data-testid="mindmap-count-pending"
          >
            {actions.pendingCount} pending
          </span>
        )}
        {actions.acceptedCount > 0 && (
          <span
            className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-bold"
            data-testid="mindmap-count-accepted"
          >
            {actions.acceptedCount} accepted
          </span>
        )}
        {actions.discardedCount > 0 && (
          <span
            className="px-2 py-0.5 rounded-full bg-error/20 text-error font-bold"
            data-testid="mindmap-count-discarded"
          >
            {actions.discardedCount} discarded
          </span>
        )}
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Saving indicator */}
      {actions.isSaving && (
        <span className="text-[10px] text-muted-light animate-pulse">
          Saving…
        </span>
      )}

      {/* Unsaved changes indicator */}
      {actions.hasUnsavedChanges && !actions.isSaving && (
        <span
          className="text-[10px] text-tertiary"
          data-testid="mindmap-unsaved"
        >
          ● Unsaved changes
        </span>
      )}

      {/* Accept All */}
      {actions.pendingCount > 0 && (
        <button
          onClick={actions.acceptAll}
          className="px-3 py-1 text-[10px] font-bold rounded-lg bg-primary/10 text-primary border border-primary/20 hover:bg-primary/20 transition-colors"
          data-testid="mindmap-accept-all"
        >
          Accept All ({actions.pendingCount})
        </button>
      )}

      {/* Confirm & Save */}
      <button
        onClick={handleConfirm}
        disabled={actions.acceptedCount === 0 || actions.isSaving}
        className="px-3 py-1 text-[10px] font-bold rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/30 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        data-testid="mindmap-confirm-save"
      >
        Confirm & Save ({actions.acceptedCount})
      </button>

      {/* Discard */}
      {totalNodes > 0 && !showDiscardConfirm && (
        <button
          onClick={() => setShowDiscardConfirm(true)}
          className="px-3 py-1 text-[10px] font-bold rounded-lg bg-error/10 text-error border border-error/20 hover:bg-error/20 transition-colors"
          data-testid="mindmap-discard-btn"
        >
          Discard
        </button>
      )}

      {/* Discard confirmation */}
      {showDiscardConfirm && (
        <div className="flex items-center gap-2 px-3 py-1 rounded-lg bg-error/10 border border-error/20">
          <span className="text-[10px] text-error font-bold">
            Discard all work?
          </span>
          <button
            onClick={handleDiscard}
            className="px-2 py-0.5 text-[10px] font-bold rounded bg-error/20 text-error hover:bg-error/30"
            data-testid="mindmap-discard-confirm"
          >
            Yes, discard
          </button>
          <button
            onClick={() => setShowDiscardConfirm(false)}
            className="px-2 py-0.5 text-[10px] font-bold rounded bg-surface-container text-muted-light hover:text-foreground"
          >
            Cancel
          </button>
        </div>
      )}
    </div>
  );
}

