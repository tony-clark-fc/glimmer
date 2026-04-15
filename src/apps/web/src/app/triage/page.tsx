"use client";

import { useEffect, useState, useCallback } from "react";
import {
  fetchReviewQueue,
  reviewClassification,
  reviewAction,
} from "@/lib/api-client";
import {
  PageHeader,
  SectionCard,
  CardSkeleton,
  EmptyState,
  ErrorState,
  Badge,
  ActionButton,
} from "@/components/ui";
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
      <PageHeader
        title="Triage"
        description="Incoming signals, proposed classifications, and items awaiting review."
      />

      {state === "loading" && (
        <CardSkeleton testId="triage-loading" count={3} />
      )}

      {state === "error" && (
        <ErrorState testId="triage-error" message={error ?? "Failed to load triage queue"} />
      )}

      {state === "empty" && (
        <EmptyState
          testId="triage-empty-state"
          icon="⚡"
          message="No triage items yet. Signals will appear here once connectors are active."
        />
      )}

      {state === "loaded" && queue && (
        <div className="space-y-8">
          {/* Pending classifications */}
          {queue.classifications.length > 0 && (
            <SectionCard
              testId="triage-classifications"
              title="Classifications Pending Review"
              count={queue.classifications.length}
            >
              <ul className="space-y-3">
                {queue.classifications.map((c) => (
                  <ClassificationCard
                    key={c.id}
                    item={c}
                    onReview={handleReviewClassification}
                  />
                ))}
              </ul>
            </SectionCard>
          )}

          {/* Pending actions */}
          {queue.actions.length > 0 && (
            <SectionCard
              testId="triage-actions"
              title="Extracted Actions Pending Review"
              count={queue.actions.length}
            >
              <ul className="space-y-3">
                {queue.actions.map((a) => (
                  <ActionCard
                    key={a.id}
                    item={a}
                    onReview={handleReviewAction}
                  />
                ))}
              </ul>
            </SectionCard>
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
      className="rounded-2xl bg-surface-container-lowest p-5 ghost-border"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          {/* Provenance */}
          <div
            data-testid="triage-provenance"
            className="flex items-center gap-2 text-xs text-muted-light"
          >
            <Badge variant="neutral">{item.source_record_type}</Badge>
            <span className="font-mono">{item.source_record_id.slice(0, 8)}…</span>
          </div>

          {/* Classification details */}
          <div className="mt-3">
            {item.classification_rationale && (
              <p className="text-sm text-foreground leading-relaxed italic text-indigo-100/90">
                {item.classification_rationale}
              </p>
            )}
            <div className="mt-3 flex flex-wrap gap-2 text-xs">
              {item.confidence !== null && (
                <ConfidenceIndicator confidence={item.confidence} />
              )}
              {item.ambiguity_flag && (
                <Badge
                  testId="triage-ambiguity"
                  variant="warning"
                >
                  ⚠ Ambiguous
                </Badge>
              )}
              <span data-testid="triage-review-state" className="text-muted-light">
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
      className="rounded-2xl bg-surface-container-lowest p-5 ghost-border"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          {/* Provenance */}
          <div
            data-testid="triage-provenance"
            className="flex items-center gap-2 text-xs text-muted-light"
          >
            <Badge variant="neutral">{item.source_record_type}</Badge>
            <span className="font-mono">{item.source_record_id.slice(0, 8)}…</span>
          </div>

          <p className="mt-3 text-sm text-foreground leading-relaxed">
            {item.action_text}
          </p>

          <div className="mt-2 flex gap-3 text-xs">
            {item.urgency_signal && (
              <span data-testid="triage-urgency" className="text-muted-light">
                Urgency: {item.urgency_signal}
              </span>
            )}
            <span data-testid="triage-review-state" className="text-muted-light">
              State: {item.review_state}
            </span>
          </div>
        </div>

        <ReviewActions onReview={(action) => onReview(item.id, action)} />
      </div>
    </li>
  );
}

// ── Confidence indicator ────────────────────────────────────────

function ConfidenceIndicator({ confidence }: { confidence: number }) {
  const pct = (confidence * 100).toFixed(0);
  return (
    <div data-testid="triage-confidence" className="flex items-center gap-2">
      <span className="text-xs font-bold text-muted-light uppercase tracking-widest">Confidence</span>
      <span className="text-primary font-headline font-bold text-sm drop-shadow-[0_0_8px_rgba(129,140,248,0.4)]">
        {pct}%
      </span>
    </div>
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
      className="flex gap-1 bg-[#121215] p-1 rounded-full border border-outline-variant/30"
    >
      <ActionButton
        variant="success"
        testId="review-accept"
        onClick={() => onReview("accepted")}
      >
        Accept
      </ActionButton>
      <ActionButton
        variant="danger"
        testId="review-reject"
        onClick={() => onReview("rejected")}
      >
        Reject
      </ActionButton>
    </div>
  );
}
