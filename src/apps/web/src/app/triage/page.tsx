"use client";

import { useEffect, useState, useCallback } from "react";
import {
  fetchReviewQueue,
  reviewClassification,
  reviewAction,
} from "@/lib/api-client";
import type { ReviewQueue, ClassificationItem, ExtractedActionItem } from "@/lib/types";

type LoadState = "loading" | "loaded" | "empty" | "error";

export default function TriagePage() {
  const [queue, setQueue] = useState<ReviewQueue | null>(null);
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    setState("loading");
    fetchReviewQueue()
      .then((data) => {
        setQueue(data);
        setState(data.total_pending > 0 ? "loaded" : "empty");
      })
      .catch((err) => {
        setError(err.message ?? "Failed to load triage queue");
        setState("error");
      });
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleReviewClassification = async (
    id: string,
    action: "accepted" | "rejected" | "amended",
  ) => {
    try {
      await reviewClassification(id, action);
      load();
    } catch {
      // Reload to show current state
      load();
    }
  };

  const handleReviewAction = async (
    id: string,
    action: "accepted" | "rejected" | "amended",
  ) => {
    try {
      await reviewAction(id, action);
      load();
    } catch {
      load();
    }
  };

  return (
    <div data-testid="page-triage">
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
        Triage
      </h1>
      <p className="mt-2 text-zinc-600 dark:text-zinc-400">
        Incoming signals, proposed classifications, and items awaiting review.
      </p>

      {state === "loading" && (
        <div data-testid="triage-loading" className="mt-8 text-sm text-zinc-500">
          Loading triage queue…
        </div>
      )}

      {state === "error" && (
        <div
          data-testid="triage-error"
          className="mt-8 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-300"
        >
          {error}
        </div>
      )}

      {state === "empty" && (
        <div
          data-testid="triage-empty-state"
          className="mt-8 rounded-lg border border-dashed border-zinc-300 p-8 text-center text-sm text-zinc-500 dark:border-zinc-700 dark:text-zinc-500"
        >
          No triage items yet. Signals will appear here once connectors are
          active.
        </div>
      )}

      {state === "loaded" && queue && (
        <div className="mt-6 space-y-8">
          {/* Pending classifications */}
          {queue.classifications.length > 0 && (
            <section data-testid="triage-classifications">
              <h2 className="text-lg font-medium text-zinc-800 dark:text-zinc-200">
                Classifications Pending Review ({queue.classifications.length})
              </h2>
              <ul className="mt-3 space-y-3">
                {queue.classifications.map((c) => (
                  <ClassificationCard
                    key={c.id}
                    item={c}
                    onReview={handleReviewClassification}
                  />
                ))}
              </ul>
            </section>
          )}

          {/* Pending actions */}
          {queue.actions.length > 0 && (
            <section data-testid="triage-actions">
              <h2 className="text-lg font-medium text-zinc-800 dark:text-zinc-200">
                Extracted Actions Pending Review ({queue.actions.length})
              </h2>
              <ul className="mt-3 space-y-3">
                {queue.actions.map((a) => (
                  <ActionCard
                    key={a.id}
                    item={a}
                    onReview={handleReviewAction}
                  />
                ))}
              </ul>
            </section>
          )}
        </div>
      )}
    </div>
  );
}

// ── Classification card ─────────────────────────────────────────

function ClassificationCard({
  item,
  onReview,
}: {
  item: ClassificationItem;
  onReview: (id: string, action: "accepted" | "rejected" | "amended") => void;
}) {
  return (
    <li
      data-testid={`triage-classification-${item.id}`}
      className="rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-700 dark:bg-zinc-900"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          {/* Provenance */}
          <div
            data-testid="triage-provenance"
            className="flex gap-2 text-xs text-zinc-400"
          >
            <span>Source: {item.source_record_type}</span>
            <span className="font-mono">{item.source_record_id.slice(0, 8)}…</span>
          </div>

          {/* Classification details */}
          <div className="mt-2">
            {item.classification_rationale && (
              <p className="text-sm text-zinc-700 dark:text-zinc-300">
                {item.classification_rationale}
              </p>
            )}
            <div className="mt-1 flex gap-3 text-xs text-zinc-500">
              {item.confidence !== null && (
                <span data-testid="triage-confidence">
                  Confidence: {(item.confidence * 100).toFixed(0)}%
                </span>
              )}
              {item.ambiguity_flag && (
                <span
                  data-testid="triage-ambiguity"
                  className="text-amber-600 dark:text-amber-400 font-medium"
                >
                  ⚠ Ambiguous
                </span>
              )}
              <span data-testid="triage-review-state">
                State: {item.review_state}
              </span>
            </div>
          </div>
        </div>

        {/* Review actions */}
        <ReviewActions onReview={(action) => onReview(item.id, action)} />
      </div>
    </li>
  );
}

// ── Action card ─────────────────────────────────────────────────

function ActionCard({
  item,
  onReview,
}: {
  item: ExtractedActionItem;
  onReview: (id: string, action: "accepted" | "rejected" | "amended") => void;
}) {
  return (
    <li
      data-testid={`triage-action-${item.id}`}
      className="rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-700 dark:bg-zinc-900"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          {/* Provenance */}
          <div
            data-testid="triage-provenance"
            className="flex gap-2 text-xs text-zinc-400"
          >
            <span>Source: {item.source_record_type}</span>
            <span className="font-mono">{item.source_record_id.slice(0, 8)}…</span>
          </div>

          <p className="mt-2 text-sm text-zinc-800 dark:text-zinc-200">
            {item.action_text}
          </p>

          <div className="mt-1 flex gap-3 text-xs text-zinc-500">
            {item.urgency_signal && (
              <span data-testid="triage-urgency">
                Urgency: {item.urgency_signal}
              </span>
            )}
            <span data-testid="triage-review-state">
              State: {item.review_state}
            </span>
          </div>
        </div>

        <ReviewActions onReview={(action) => onReview(item.id, action)} />
      </div>
    </li>
  );
}

// ── Review action buttons ───────────────────────────────────────

function ReviewActions({
  onReview,
}: {
  onReview: (action: "accepted" | "rejected" | "amended") => void;
}) {
  return (
    <div
      data-testid="triage-review-controls"
      className="flex flex-col gap-1"
    >
      <button
        data-testid="review-accept"
        onClick={() => onReview("accepted")}
        className="rounded-md bg-green-100 px-3 py-1 text-xs font-medium text-green-700 hover:bg-green-200 dark:bg-green-900 dark:text-green-300 dark:hover:bg-green-800"
      >
        Accept
      </button>
      <button
        data-testid="review-reject"
        onClick={() => onReview("rejected")}
        className="rounded-md bg-red-100 px-3 py-1 text-xs font-medium text-red-700 hover:bg-red-200 dark:bg-red-900 dark:text-red-300 dark:hover:bg-red-800"
      >
        Reject
      </button>
    </div>
  );
}

