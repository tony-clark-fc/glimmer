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
  InfoBanner,
  ActionButton,
} from "@/components/ui";
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
      <PageHeader
        title="Review"
        description="Items requiring your judgment — ambiguous classifications, memory updates, and approval-gated actions."
      />

      {state === "loading" && (
        <CardSkeleton testId="review-loading" count={3} />
      )}

      {state === "error" && (
        <ErrorState testId="review-error" message={error ?? "Failed to load review queue"} />
      )}

      {state === "empty" && (
        <EmptyState
          testId="review-empty-state"
          icon="✓"
          message="Nothing to review right now. Review items will appear when the assistant encounters ambiguity or proposes meaningful changes."
        />
      )}

      {state === "loaded" && queue && (
        <div className="space-y-8">
          {/* Pending count banner */}
          <InfoBanner testId="review-pending-count" variant="warning">
            <strong className="font-headline text-lg">{queue.total_pending}</strong>&nbsp;item{queue.total_pending !== 1 ? "s" : ""}{" "}
            pending review
          </InfoBanner>

          {/* Classifications */}
          {queue.classifications.length > 0 && (
            <SectionCard
              testId="review-classifications"
              title="Pending Classifications"
              count={queue.classifications.length}
              variant="warning"
            >
              <ul className="space-y-3">
                {queue.classifications.map((c) => (
                  <ReviewClassificationCard
                    key={c.id}
                    item={c}
                    onAction={handleClassificationAction}
                  />
                ))}
              </ul>
            </SectionCard>
          )}

          {/* Extracted actions */}
          {queue.actions.length > 0 && (
            <SectionCard
              testId="review-actions"
              title="Pending Extracted Actions"
              count={queue.actions.length}
              variant="warning"
            >
              <ul className="space-y-3">
                {queue.actions.map((a) => (
                  <ReviewActionCard
                    key={a.id}
                    item={a}
                    onAction={handleActionReview}
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
      className="rounded-2xl bg-tertiary-container/5 p-5 border border-tertiary/10"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          {/* Pending badge */}
          <Badge testId="review-state-badge" variant="warning">Pending</Badge>

          {/* Provenance */}
          <div className="mt-2 flex items-center gap-2 text-xs text-muted-light">
            <Badge variant="neutral">{item.source_record_type}</Badge>
            <span className="font-mono">{item.source_record_id.slice(0, 8)}…</span>
          </div>

          {item.classification_rationale && (
            <p className="mt-3 text-sm text-foreground leading-relaxed">
              {item.classification_rationale}
            </p>
          )}

          <div className="mt-2 flex flex-wrap gap-2 text-xs">
            {item.confidence !== null && (
              <span className="text-muted-light">Confidence: {(item.confidence * 100).toFixed(0)}%</span>
            )}
            {item.ambiguity_flag && (
              <Badge variant="warning">⚠ Ambiguous</Badge>
            )}
          </div>
        </div>

        <div className="flex gap-1 bg-[#121215] p-1 rounded-full border border-outline-variant/30">
          <ActionButton
            variant="success"
            testId="review-btn-accept"
            onClick={() => onAction(item.id, "accepted")}
          >
            Accept
          </ActionButton>
          <ActionButton
            variant="danger"
            testId="review-btn-reject"
            onClick={() => onAction(item.id, "rejected")}
          >
            Reject
          </ActionButton>
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
      className="rounded-2xl bg-tertiary-container/5 p-5 border border-tertiary/10"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <Badge testId="review-state-badge" variant="warning">Pending</Badge>

          <div className="mt-2 flex items-center gap-2 text-xs text-muted-light">
            <Badge variant="neutral">{item.source_record_type}</Badge>
            <span className="font-mono">{item.source_record_id.slice(0, 8)}…</span>
          </div>

          <p className="mt-3 text-sm text-foreground leading-relaxed">
            {item.action_text}
          </p>

          {item.urgency_signal && (
            <span className="text-xs text-muted-light mt-1 inline-block">
              Urgency: {item.urgency_signal}
            </span>
          )}
        </div>

        <div className="flex gap-1 bg-[#121215] p-1 rounded-full border border-outline-variant/30">
          <ActionButton
            variant="success"
            testId="review-btn-accept"
            onClick={() => onAction(item.id, "accepted")}
          >
            Accept
          </ActionButton>
          <ActionButton
            variant="danger"
            testId="review-btn-reject"
            onClick={() => onAction(item.id, "rejected")}
          >
            Reject
          </ActionButton>
        </div>
      </div>
    </li>
  );
}
