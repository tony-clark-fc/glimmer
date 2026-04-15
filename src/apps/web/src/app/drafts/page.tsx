"use client";

import { useEffect, useState } from "react";
import { fetchDrafts } from "@/lib/api-client";
import { PersonaAvatar } from "@/components/persona-avatar";
import {
  PageHeader,
  CardSkeleton,
  EmptyState,
  ErrorState,
  Badge,
  InfoBanner,
  ActionButton,
} from "@/components/ui";
import type { DraftSummary } from "@/lib/types";

type LoadState = "loading" | "loaded" | "empty" | "error";

export default function DraftsPage() {
  const [drafts, setDrafts] = useState<DraftSummary[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchDrafts()
      .then((data) => {
        if (cancelled) return;
        setDrafts(data);
        setState(data.length > 0 ? "loaded" : "empty");
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err.message ?? "Failed to load drafts");
        setState("error");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const handleCopy = async (draft: DraftSummary) => {
    try {
      await navigator.clipboard.writeText(draft.body_content);
      setCopiedId(draft.id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch {
      // clipboard may not be available in all contexts
    }
  };

  return (
    <div data-testid="page-drafts">
      <div className="flex items-start gap-4 mb-10">
        <PersonaAvatar context="draft" size="sm" />
        <PageHeader
          title="Drafts"
          description="Review and refine communication drafts — context, variants, and copy-ready output."
        />
      </div>

      {/* No-auto-send notice — glass effect banner */}
      <div className="mb-8">
        <InfoBanner testId="drafts-no-auto-send" variant="info">
          🔒 Drafts are review-only. Copy and send manually — Glimmer never sends
          on your behalf.
        </InfoBanner>
      </div>

      {state === "loading" && <CardSkeleton testId="drafts-loading" count={3} />}

      {state === "error" && (
        <ErrorState
          testId="drafts-error"
          message={error ?? "Failed to load drafts"}
        />
      )}

      {state === "empty" && (
        <EmptyState
          testId="drafts-empty-state"
          icon="✎"
          message="No drafts yet. Drafts are generated from triage and planner workflows."
        />
      )}

      {state === "loaded" && (
        <div data-testid="drafts-list" className="space-y-4">
          {drafts.map((draft) => (
            <div
              key={draft.id}
              data-testid={`draft-card-${draft.id}`}
              className="luminous-card rounded-2xl p-6"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  {/* Header with intent and metadata */}
                  <div className="flex flex-wrap items-center gap-2">
                    {draft.intent_label && (
                      <span className="font-headline font-bold text-foreground">
                        {draft.intent_label}
                      </span>
                    )}
                    <DraftStatusBadge status={draft.status} />
                    {draft.channel_type && (
                      <Badge variant="neutral">{draft.channel_type}</Badge>
                    )}
                    {draft.tone_mode && (
                      <span
                        data-testid="draft-tone"
                        className="text-xs text-muted-light"
                      >
                        Tone: {draft.tone_mode}
                      </span>
                    )}
                  </div>

                  {/* Draft body preview — inset panel */}
                  <p
                    data-testid="draft-body-preview"
                    className="mt-4 text-sm text-foreground whitespace-pre-wrap line-clamp-4 leading-relaxed bg-surface-container-lowest rounded-2xl p-4 ghost-border"
                  >
                    {draft.body_content}
                  </p>

                  {/* Rationale */}
                  {draft.rationale_summary && (
                    <p
                      data-testid="draft-rationale"
                      className="mt-3 text-xs text-muted-light italic"
                    >
                      Rationale: {draft.rationale_summary}
                    </p>
                  )}

                  <p className="mt-2 text-xs text-muted-light">
                    Created {new Date(draft.created_at).toLocaleString()}
                  </p>
                </div>

                {/* Copy button — review-only, no send */}
                <ActionButton
                  testId="draft-copy"
                  variant={copiedId === draft.id ? "success" : "primary"}
                  onClick={() => handleCopy(draft)}
                >
                  {copiedId === draft.id ? "Copied ✓" : "Copy Draft"}
                </ActionButton>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Helpers ──────────────────────────────────────────────────────

function DraftStatusBadge({ status }: { status: string }) {
  const variant =
    status === "draft"
      ? "warning"
      : status === "reviewed"
      ? "success"
      : status === "sent_by_operator"
      ? "info"
      : "neutral";

  return (
    <Badge testId="draft-status" variant={variant}>
      {status.replace(/_/g, " ")}
    </Badge>
  );
}
