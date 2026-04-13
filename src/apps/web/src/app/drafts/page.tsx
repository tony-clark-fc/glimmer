"use client";

import { useEffect, useState } from "react";
import { fetchDrafts } from "@/lib/api-client";
import { PersonaAvatar } from "@/components/persona-avatar";
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
      <div className="flex items-center gap-3">
        <PersonaAvatar context="draft" size="sm" />
        <div>
          <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
            Drafts
          </h1>
          <p className="mt-1 text-zinc-600 dark:text-zinc-400">
            Review and refine communication drafts — context, variants, and
            copy-ready output.
          </p>
        </div>
      </div>

      {/* No-auto-send notice */}
      <div
        data-testid="drafts-no-auto-send"
        className="mt-4 rounded-md bg-blue-50 border border-blue-200 px-4 py-2 text-xs text-blue-700 dark:bg-blue-950 dark:border-blue-800 dark:text-blue-300"
      >
        Drafts are review-only. Copy and send manually — Glimmer never sends
        on your behalf.
      </div>

      {state === "loading" && (
        <div data-testid="drafts-loading" className="mt-8 text-sm text-zinc-500">
          Loading drafts…
        </div>
      )}

      {state === "error" && (
        <div
          data-testid="drafts-error"
          className="mt-8 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-300"
        >
          {error}
        </div>
      )}

      {state === "empty" && (
        <div
          data-testid="drafts-empty-state"
          className="mt-8 rounded-lg border border-dashed border-zinc-300 p-8 text-center text-sm text-zinc-500 dark:border-zinc-700 dark:text-zinc-500"
        >
          No drafts yet. Drafts are generated from triage and planner
          workflows.
        </div>
      )}

      {state === "loaded" && (
        <div data-testid="drafts-list" className="mt-6 space-y-4">
          {drafts.map((draft) => (
            <div
              key={draft.id}
              data-testid={`draft-card-${draft.id}`}
              className="rounded-lg border border-zinc-200 bg-white p-4 dark:border-zinc-700 dark:bg-zinc-900"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  {/* Header with intent and metadata */}
                  <div className="flex items-center gap-2">
                    {draft.intent_label && (
                      <span className="font-medium text-zinc-800 dark:text-zinc-200">
                        {draft.intent_label}
                      </span>
                    )}
                    <DraftStatusBadge status={draft.status} />
                    {draft.channel_type && (
                      <span className="text-xs text-zinc-400">
                        {draft.channel_type}
                      </span>
                    )}
                    {draft.tone_mode && (
                      <span
                        data-testid="draft-tone"
                        className="text-xs text-zinc-400"
                      >
                        Tone: {draft.tone_mode}
                      </span>
                    )}
                  </div>

                  {/* Draft body preview */}
                  <p
                    data-testid="draft-body-preview"
                    className="mt-2 text-sm text-zinc-700 dark:text-zinc-300 whitespace-pre-wrap line-clamp-4"
                  >
                    {draft.body_content}
                  </p>

                  {/* Rationale */}
                  {draft.rationale_summary && (
                    <p
                      data-testid="draft-rationale"
                      className="mt-2 text-xs text-zinc-500 italic"
                    >
                      Rationale: {draft.rationale_summary}
                    </p>
                  )}

                  <p className="mt-2 text-xs text-zinc-400">
                    Created {new Date(draft.created_at).toLocaleString()}
                  </p>
                </div>

                {/* Copy button — review-only, no send */}
                <button
                  data-testid="draft-copy"
                  onClick={() => handleCopy(draft)}
                  className="rounded-md bg-zinc-100 px-3 py-1.5 text-xs font-medium text-zinc-700 hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-700 whitespace-nowrap"
                >
                  {copiedId === draft.id ? "Copied ✓" : "Copy Draft"}
                </button>
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
  const colors: Record<string, string> = {
    draft: "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300",
    reviewed:
      "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
    discarded:
      "bg-zinc-100 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400",
    sent_by_operator:
      "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
  };

  return (
    <span
      data-testid="draft-status"
      className={`rounded-full px-2 py-0.5 text-xs font-medium ${colors[status] ?? "bg-zinc-100 text-zinc-500"}`}
    >
      {status}
    </span>
  );
}
