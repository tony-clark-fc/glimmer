"use client";

import { useEffect, useState, useCallback } from "react";
import {
  fetchReviewQueue,
  reviewClassification,
  reviewAction,
} from "@/lib/api-client";
import type { ReviewQueue, ClassificationItem, ExtractedActionItem } from "@/lib/types";

type LoadState = "loading" | "loaded" | "empty" | "error";

export default function ReviewPage() {
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
        setError(err.message ?? "Failed to load review queue");
        setState("error");
      });
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleClassificationAction = async (
    id: string,
    action: "accepted" | "rejected" | "amended",
  ) => {
    try {
      await reviewClassification(id, action);
      load();
    } catch {
      load();
    }
  };

  const handleActionReview = async (
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
    <div data-testid="page-review">
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
        Review
      </h1>
      <p className="mt-2 text-zinc-600 dark:text-zinc-400">
        Items requiring your judgment — ambiguous classifications, memory
        updates, and approval-gated actions.
      </p>

      {state === "loading" && (
        <div data-testid="review-loading" className="mt-8 text-sm text-zinc-500">
          Loading review queue…
        </div>
      )}

      {state === "error" && (
        <div
          data-testid="review-error"
          className="mt-8 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-300"
        >
          {error}
        </div>
      )}

      {state === "empty" && (
        <div
          data-testid="review-empty-state"
          className="mt-8 rounded-lg border border-dashed border-zinc-300 p-8 text-center text-sm text-zinc-500 dark:border-zinc-700 dark:text-zinc-500"
        >
          Nothing to review right now. Review items will appear when the
          assistant encounters ambiguity or proposes meaningful changes.
        </div>
      )}

      {state === "loaded" && queue && (
        <div className="mt-6 space-y-6">
          {/* Pending count banner */}
          <div
            data-testid="review-pending-count"
            className="rounded-md bg-amber-50 border border-amber-200 px-4 py-2 text-sm text-amber-800 dark:bg-amber-950 dark:border-amber-800 dark:text-amber-200"
          >
            <strong>{queue.total_pending}</strong> item{queue.total_pending !== 1 ? "s" : ""}{" "}
            pending review
          </div>

          {/* Classifications */}
          {queue.classifications.length > 0 && (
            <section data-testid="review-classifications">
              <h2 className="text-lg font-medium text-zinc-800 dark:text-zinc-200">
                Pending Classifications
              </h2>
              <ul className="mt-3 space-y-3">
                {queue.classifications.map((c) => (
                  <ReviewClassificationCard
                    key={c.id}
                    item={c}
                    onAction={handleClassificationAction}
                  />
                ))}
              </ul>
            </section>
          )}

          {/* Extracted actions */}
          {queue.actions.length > 0 && (
            <section data-testid="review-actions">
              <h2 className="text-lg font-medium text-zinc-800 dark:text-zinc-200">
                Pending Extracted Actions
              </h2>
              <ul className="mt-3 space-y-3">
                {queue.actions.map((a) => (
                  <ReviewActionCard
                    key={a.id}
                    item={a}
                    onAction={handleActionReview}
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

// ── Review classification card ──────────────────────────────────

function ReviewClassificationCard({
  item,
  onAction,
}: {
  item: ClassificationItem;
  onAction: (id: string, action: "accepted" | "rejected" | "amended") => void;
}) {
  return (
    <li
      data-testid={`review-classification-${item.id}`}
      className="rounded-lg border border-amber-200 bg-amber-50 p-4 dark:border-amber-800 dark:bg-amber-950"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          {/* Pending badge */}
          <span
            data-testid="review-state-badge"
            className="inline-block rounded-full bg-amber-200 px-2 py-0.5 text-xs font-medium text-amber-800 dark:bg-amber-800 dark:text-amber-200"
          >
            Pending
          </span>

          {/* Provenance */}
          <div className="mt-2 flex gap-2 text-xs text-zinc-500">
            <span>Source: {item.source_record_type}</span>
            <span className="font-mono">{item.source_record_id.slice(0, 8)}…</span>
          </div>

          {item.classification_rationale && (
            <p className="mt-2 text-sm text-zinc-700 dark:text-zinc-300">
              {item.classification_rationale}
            </p>
          )}

          <div className="mt-1 flex gap-3 text-xs text-zinc-500">
            {item.confidence !== null && (
              <span>Confidence: {(item.confidence * 100).toFixed(0)}%</span>
            )}
            {item.ambiguity_flag && (
              <span className="text-amber-600 dark:text-amber-400 font-medium">
                ⚠ Ambiguous
              </span>
            )}
          </div>
        </div>

        <div className="flex flex-col gap-1">
          <button
            data-testid="review-btn-accept"
            onClick={() => onAction(item.id, "accepted")}
            className="rounded-md bg-green-100 px-3 py-1 text-xs font-medium text-green-700 hover:bg-green-200 dark:bg-green-900 dark:text-green-300"
          >
            Accept
          </button>
          <button
            data-testid="review-btn-reject"
            onClick={() => onAction(item.id, "rejected")}
            className="rounded-md bg-red-100 px-3 py-1 text-xs font-medium text-red-700 hover:bg-red-200 dark:bg-red-900 dark:text-red-300"
          >
            Reject
          </button>
        </div>
      </div>
    </li>
  );
}

// ── Review action card ──────────────────────────────────────────

function ReviewActionCard({
  item,
  onAction,
}: {
  item: ExtractedActionItem;
  onAction: (id: string, action: "accepted" | "rejected" | "amended") => void;
}) {
  return (
    <li
      data-testid={`review-action-${item.id}`}
      className="rounded-lg border border-amber-200 bg-amber-50 p-4 dark:border-amber-800 dark:bg-amber-950"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <span
            data-testid="review-state-badge"
            className="inline-block rounded-full bg-amber-200 px-2 py-0.5 text-xs font-medium text-amber-800 dark:bg-amber-800 dark:text-amber-200"
          >
            Pending
          </span>

          <div className="mt-2 flex gap-2 text-xs text-zinc-500">
            <span>Source: {item.source_record_type}</span>
            <span className="font-mono">{item.source_record_id.slice(0, 8)}…</span>
          </div>

          <p className="mt-2 text-sm text-zinc-800 dark:text-zinc-200">
            {item.action_text}
          </p>

          {item.urgency_signal && (
            <span className="text-xs text-zinc-500">
              Urgency: {item.urgency_signal}
            </span>
          )}
        </div>

        <div className="flex flex-col gap-1">
          <button
            data-testid="review-btn-accept"
            onClick={() => onAction(item.id, "accepted")}
            className="rounded-md bg-green-100 px-3 py-1 text-xs font-medium text-green-700 hover:bg-green-200 dark:bg-green-900 dark:text-green-300"
          >
            Accept
          </button>
          <button
            data-testid="review-btn-reject"
            onClick={() => onAction(item.id, "rejected")}
            className="rounded-md bg-red-100 px-3 py-1 text-xs font-medium text-red-700 hover:bg-red-200 dark:bg-red-900 dark:text-red-300"
          >
            Reject
          </button>
        </div>
      </div>
    </li>
  );
}
