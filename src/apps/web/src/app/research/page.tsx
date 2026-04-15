"use client";

import { useEffect, useState, useCallback } from "react";
import {
  fetchResearchRuns,
  fetchExchanges,
  fetchResearchRun,
  reviewResearchSummary,
  reviewExchange,
} from "@/lib/api-client";
import {
  PageHeader,
  SectionCard,
  CardSkeleton,
  EmptyState,
  ErrorState,
  Badge,
  ActionButton,
  ItemCard,
} from "@/components/ui";
import type {
  ResearchRunSummary,
  ResearchRunDetail,
  ExpertAdviceExchange,
} from "@/lib/types";

type LoadState = "loading" | "loaded" | "empty" | "error";
type Tab = "runs" | "exchanges";
type DetailView =
  | { type: "run"; data: ResearchRunDetail }
  | { type: "exchange"; data: ExpertAdviceExchange }
  | null;

export default function ResearchPage() {
  const [tab, setTab] = useState<Tab>("runs");
  const [runs, setRuns] = useState<ResearchRunSummary[]>([]);
  const [exchanges, setExchanges] = useState<ExpertAdviceExchange[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);
  const [detail, setDetail] = useState<DetailView>(null);

  const loadRuns = useCallback(() => {
    setState("loading");
    fetchResearchRuns()
      .then((data) => {
        setRuns(data);
        setState(data.length > 0 ? "loaded" : "empty");
      })
      .catch((err) => {
        setError(err.message ?? "Failed to load research runs");
        setState("error");
      });
  }, []);

  const loadExchanges = useCallback(() => {
    setState("loading");
    fetchExchanges()
      .then((data) => {
        setExchanges(data);
        setState(data.length > 0 ? "loaded" : "empty");
      })
      .catch((err) => {
        setError(err.message ?? "Failed to load exchanges");
        setState("error");
      });
  }, []);

  useEffect(() => {
    if (tab === "runs") loadRuns();
    else loadExchanges();
  }, [tab, loadRuns, loadExchanges]);

  const openRunDetail = async (id: string) => {
    try {
      const data = await fetchResearchRun(id);
      setDetail({ type: "run", data });
    } catch {
      /* silent — detail load fail */
    }
  };

  const openExchangeDetail = (exchange: ExpertAdviceExchange) => {
    setDetail({ type: "exchange", data: exchange });
  };

  const handleReviewSummary = async (runId: string, action: "accepted" | "rejected") => {
    try {
      await reviewResearchSummary(runId, action);
      const updated = await fetchResearchRun(runId);
      setDetail({ type: "run", data: updated });
      loadRuns();
    } catch {
      /* silent */
    }
  };

  const handleReviewExchange = async (exchangeId: string, action: "accepted" | "rejected") => {
    try {
      await reviewExchange(exchangeId, action);
      loadExchanges();
      setDetail(null);
    } catch {
      /* silent */
    }
  };

  return (
    <div data-testid="page-research">
      <PageHeader
        title="Research & Expert Advice"
        description="Deep research runs, expert advice consultations, and their review status."
      />

      {/* Tab bar — pill-shaped segmented control */}
      <div className="flex gap-1 mb-8 bg-[#121215] rounded-full p-1 w-fit border border-outline-variant/30">
        <TabButton
          label="Research Runs"
          active={tab === "runs"}
          onClick={() => { setTab("runs"); setDetail(null); }}
          testId="tab-runs"
        />
        <TabButton
          label="Expert Advice"
          active={tab === "exchanges"}
          onClick={() => { setTab("exchanges"); setDetail(null); }}
          testId="tab-exchanges"
        />
      </div>

      {state === "loading" && (
        <CardSkeleton testId="research-loading" count={3} />
      )}

      {state === "error" && (
        <ErrorState testId="research-error" message={error ?? "Failed to load"} />
      )}

      {state === "empty" && (
        <EmptyState
          testId="research-empty"
          icon="🔍"
          message={
            tab === "runs"
              ? "No research runs yet. Research runs appear when Glimmer escalates a task to Gemini Deep Research."
              : "No expert advice exchanges yet. Exchanges appear when Glimmer consults Gemini for expert advice."
          }
        />
      )}

      {state === "loaded" && !detail && tab === "runs" && (
        <ul data-testid="research-runs-list" className="space-y-3">
          {runs.map((r) => (
            <ResearchRunCard key={r.id} run={r} onSelect={openRunDetail} />
          ))}
        </ul>
      )}

      {state === "loaded" && !detail && tab === "exchanges" && (
        <ul data-testid="exchanges-list" className="space-y-3">
          {exchanges.map((e) => (
            <ExchangeCard key={e.id} exchange={e} onSelect={openExchangeDetail} />
          ))}
        </ul>
      )}

      {/* Detail panels */}
      {detail?.type === "run" && (
        <RunDetailPanel
          run={detail.data}
          onBack={() => setDetail(null)}
          onReview={handleReviewSummary}
        />
      )}

      {detail?.type === "exchange" && (
        <ExchangeDetailPanel
          exchange={detail.data}
          onBack={() => setDetail(null)}
          onReview={handleReviewExchange}
        />
      )}
    </div>
  );
}

// ── Tab button ──────────────────────────────────────────────────

function TabButton({
  label,
  active,
  onClick,
  testId,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
  testId: string;
}) {
  return (
    <button
      data-testid={testId}
      onClick={onClick}
      className={`px-5 py-2 text-sm font-semibold rounded-full transition-all duration-200 ${
        active
          ? "bg-primary/20 text-primary"
          : "text-on-surface-variant hover:bg-white/5"
      }`}
    >
      {label}
    </button>
  );
}

// ── Research run list card ───────────────────────────────────────

function ResearchRunCard({
  run,
  onSelect,
}: {
  run: ResearchRunSummary;
  onSelect: (id: string) => void;
}) {
  return (
    <li>
      <ItemCard
        testId={`run-${run.id}`}
        onClick={() => onSelect(run.id)}
        hoverable
      >
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <StatusBadge status={run.status} />
              <ReviewStateBadge state={run.summary_review_state} />
            </div>
            <p className="mt-2 text-sm text-foreground line-clamp-2 leading-relaxed">
              {run.research_query}
            </p>
            <div className="mt-2 flex flex-wrap gap-3 text-xs text-muted-light">
              <span>{run.invocation_origin.replace(/_/g, " ")}</span>
              <span>{run.findings_count} findings</span>
              <span>{run.sources_count} sources</span>
              {run.document_name && <span>📄 {run.document_name}</span>}
            </div>
          </div>
          <time className="text-xs text-muted-light whitespace-nowrap">
            {new Date(run.created_at).toLocaleDateString()}
          </time>
        </div>
      </ItemCard>
    </li>
  );
}

// ── Exchange list card ──────────────────────────────────────────

function ExchangeCard({
  exchange,
  onSelect,
}: {
  exchange: ExpertAdviceExchange;
  onSelect: (e: ExpertAdviceExchange) => void;
}) {
  return (
    <li>
      <ItemCard
        testId={`exchange-${exchange.id}`}
        onClick={() => onSelect(exchange)}
        hoverable
      >
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <StatusBadge status={exchange.status} />
              <ReviewStateBadge state={exchange.review_state} />
              <Badge variant="neutral">{exchange.gemini_mode}</Badge>
            </div>
            <p className="mt-2 text-sm text-foreground line-clamp-2 leading-relaxed">
              {exchange.prompt}
            </p>
            <div className="mt-2 flex gap-3 text-xs text-muted-light">
              <span>{exchange.invocation_origin.replace(/_/g, " ")}</span>
              {exchange.duration_ms !== null && (
                <span>{(exchange.duration_ms / 1000).toFixed(1)}s</span>
              )}
            </div>
          </div>
          <time className="text-xs text-muted-light whitespace-nowrap">
            {new Date(exchange.created_at).toLocaleDateString()}
          </time>
        </div>
      </ItemCard>
    </li>
  );
}

// ── Run detail panel ────────────────────────────────────────────

function RunDetailPanel({
  run,
  onBack,
  onReview,
}: {
  run: ResearchRunDetail;
  onBack: () => void;
  onReview: (runId: string, action: "accepted" | "rejected") => void;
}) {
  return (
    <div data-testid="run-detail" className="space-y-6">
      <ActionButton
        variant="ghost"
        testId="detail-back"
        onClick={onBack}
      >
        ← Back to list
      </ActionButton>

      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <StatusBadge status={run.status} />
          <ReviewStateBadge state={run.summary_review_state} />
        </div>
        <h2 className="text-xl font-bold text-foreground font-headline">Research Run</h2>
      </div>

      {/* Provenance */}
      <div className="luminous-card rounded-2xl p-5">
        <dl className="grid grid-cols-[auto_1fr] gap-x-6 gap-y-3 text-sm">
          <dt className="text-muted-light font-medium">Origin</dt>
          <dd className="text-foreground">{run.invocation_origin.replace(/_/g, " ")}</dd>
          <dt className="text-muted-light font-medium">Query</dt>
          <dd className="text-foreground">{run.research_query}</dd>
          {run.document_name && (
            <>
              <dt className="text-muted-light font-medium">Document</dt>
              <dd className="text-foreground">{run.document_name}</dd>
            </>
          )}
          {run.document_url && (
            <>
              <dt className="text-muted-light font-medium">Google Doc</dt>
              <dd>
                <a
                  href={run.document_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:text-accent-text hover:underline"
                >
                  Open Document ↗
                </a>
              </dd>
            </>
          )}
          {run.error_message && (
            <>
              <dt className="text-muted-light font-medium">Error</dt>
              <dd className="text-error">{run.error_message}</dd>
            </>
          )}
        </dl>
      </div>

      {/* Summary + review controls */}
      {run.summary && (
        <SectionCard testId="run-summary" title="Summary" variant="accent">
          <div className="flex items-center justify-between mb-3">
            <ReviewStateBadge state={run.summary.review_state} />
          </div>
          <p className="text-sm text-foreground whitespace-pre-wrap leading-relaxed">
            {run.summary.summary_text}
          </p>
          {run.summary.review_state === "pending_review" && (
            <div className="mt-4 flex gap-1 bg-[#121215] p-1 rounded-full border border-outline-variant/30 w-fit">
              <ActionButton
                variant="success"
                testId="review-btn-accept"
                onClick={() => onReview(run.id, "accepted")}
              >
                Accept
              </ActionButton>
              <ActionButton
                variant="danger"
                testId="review-btn-reject"
                onClick={() => onReview(run.id, "rejected")}
              >
                Reject
              </ActionButton>
            </div>
          )}
        </SectionCard>
      )}

      {/* Findings */}
      {run.findings.length > 0 && (
        <SectionCard testId="run-findings" title="Findings" count={run.findings.length}>
          <ul className="space-y-3">
            {run.findings.map((f) => (
              <li
                key={f.id}
                className="rounded-2xl bg-surface-container-lowest p-4 ghost-border text-sm"
              >
                <div className="flex items-center gap-2 text-xs text-muted-light mb-2">
                  <Badge variant="neutral">{f.finding_type}</Badge>
                  {f.confidence_signal && <span>confidence: {f.confidence_signal}</span>}
                </div>
                <p className="text-foreground whitespace-pre-wrap leading-relaxed">
                  {f.content}
                </p>
                {f.source_url && (
                  <a
                    href={f.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-2 block text-xs text-primary hover:underline"
                  >
                    {f.source_url}
                  </a>
                )}
              </li>
            ))}
          </ul>
        </SectionCard>
      )}

      {/* Sources */}
      {run.sources.length > 0 && (
        <SectionCard testId="run-sources" title="Sources" count={run.sources.length}>
          <ul className="space-y-3">
            {run.sources.map((s) => (
              <li
                key={s.id}
                className="rounded-2xl bg-surface-container-lowest p-4 ghost-border text-sm"
              >
                {s.source_title && (
                  <p className="font-medium text-foreground">{s.source_title}</p>
                )}
                {s.source_description && (
                  <p className="mt-1 text-on-surface-variant">{s.source_description}</p>
                )}
                {s.source_url && (
                  <a
                    href={s.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-2 block text-xs text-primary hover:underline"
                  >
                    {s.source_url}
                  </a>
                )}
                {s.relevance_notes && (
                  <p className="mt-1 text-xs text-muted-light">{s.relevance_notes}</p>
                )}
              </li>
            ))}
          </ul>
        </SectionCard>
      )}
    </div>
  );
}

// ── Exchange detail panel ───────────────────────────────────────

function ExchangeDetailPanel({
  exchange,
  onBack,
  onReview,
}: {
  exchange: ExpertAdviceExchange;
  onBack: () => void;
  onReview: (id: string, action: "accepted" | "rejected") => void;
}) {
  return (
    <div data-testid="exchange-detail" className="space-y-6">
      <ActionButton
        variant="ghost"
        testId="detail-back"
        onClick={onBack}
      >
        ← Back to list
      </ActionButton>

      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <StatusBadge status={exchange.status} />
          <ReviewStateBadge state={exchange.review_state} />
          <Badge variant="neutral">{exchange.gemini_mode}</Badge>
        </div>
        <h2 className="text-xl font-bold text-foreground font-headline">
          Expert Advice Exchange
        </h2>
      </div>

      {/* Provenance */}
      <div className="luminous-card rounded-2xl p-5">
        <dl className="grid grid-cols-[auto_1fr] gap-x-6 gap-y-3 text-sm">
          <dt className="text-muted-light font-medium">Origin</dt>
          <dd className="text-foreground">{exchange.invocation_origin.replace(/_/g, " ")}</dd>
          {exchange.duration_ms !== null && (
            <>
              <dt className="text-muted-light font-medium">Duration</dt>
              <dd className="text-foreground">{(exchange.duration_ms / 1000).toFixed(1)}s</dd>
            </>
          )}
          {exchange.error_message && (
            <>
              <dt className="text-muted-light font-medium">Error</dt>
              <dd className="text-error">{exchange.error_message}</dd>
            </>
          )}
        </dl>
      </div>

      {/* Prompt */}
      <SectionCard title="Prompt">
        <div className="text-sm text-foreground whitespace-pre-wrap leading-relaxed bg-surface-container-lowest rounded-2xl p-4 ghost-border">
          {exchange.prompt}
        </div>
      </SectionCard>

      {/* Response + review controls */}
      {exchange.response_text && (
        <SectionCard testId="exchange-response" title="Response" variant="accent">
          <div className="text-sm text-foreground whitespace-pre-wrap leading-relaxed bg-surface-container-lowest rounded-2xl p-4 ghost-border">
            {exchange.response_text}
          </div>
        </SectionCard>
      )}

      {exchange.review_state === "pending_review" && (
        <div className="flex gap-1 bg-[#121215] p-1 rounded-full border border-outline-variant/30 w-fit">
          <ActionButton
            variant="success"
            testId="review-btn-accept"
            onClick={() => onReview(exchange.id, "accepted")}
          >
            Accept
          </ActionButton>
          <ActionButton
            variant="danger"
            testId="review-btn-reject"
            onClick={() => onReview(exchange.id, "rejected")}
          >
            Reject
          </ActionButton>
        </div>
      )}
    </div>
  );
}

// ── Shared UI helpers ───────────────────────────────────────────

function StatusBadge({ status }: { status: string }) {
  const variant =
    status === "completed" ? "success"
    : status === "in_progress" ? "info"
    : status === "failed" ? "danger"
    : status === "degraded" ? "warning"
    : "neutral";
  return (
    <Badge testId="status-badge" variant={variant}>
      {status.replace(/_/g, " ")}
    </Badge>
  );
}

function ReviewStateBadge({ state }: { state: string | null }) {
  if (!state) return null;
  const variant =
    state === "accepted" ? "success"
    : state === "rejected" ? "danger"
    : "warning";
  return (
    <Badge testId="review-state-badge" variant={variant}>
      {state.replace(/_/g, " ")}
    </Badge>
  );
}
