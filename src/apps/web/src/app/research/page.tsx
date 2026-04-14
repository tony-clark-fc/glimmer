"use client";

import { useEffect, useState, useCallback } from "react";
import {
  fetchResearchRuns,
  fetchExchanges,
  fetchResearchRun,
  reviewResearchSummary,
  reviewExchange,
} from "@/lib/api-client";
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
      // Refresh detail and list
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
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
        Research &amp; Expert Advice
      </h1>
      <p className="mt-2 text-zinc-600 dark:text-zinc-400">
        Deep research runs, expert advice consultations, and their review status.
      </p>

      {/* Tab bar */}
      <div className="mt-6 flex gap-2 border-b border-zinc-200 dark:border-zinc-800">
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
        <div data-testid="research-loading" className="mt-6 text-sm text-zinc-500">
          Loading…
        </div>
      )}

      {state === "error" && (
        <div
          data-testid="research-error"
          className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-300"
        >
          {error}
        </div>
      )}

      {state === "empty" && (
        <div
          data-testid="research-empty"
          className="mt-6 rounded-lg border border-dashed border-zinc-300 p-8 text-center text-sm text-zinc-500 dark:border-zinc-700"
        >
          {tab === "runs"
            ? "No research runs yet. Research runs appear when Glimmer escalates a task to Gemini Deep Research."
            : "No expert advice exchanges yet. Exchanges appear when Glimmer consults Gemini for expert advice."}
        </div>
      )}

      {state === "loaded" && !detail && tab === "runs" && (
        <ul data-testid="research-runs-list" className="mt-4 space-y-3">
          {runs.map((r) => (
            <ResearchRunCard key={r.id} run={r} onSelect={openRunDetail} />
          ))}
        </ul>
      )}

      {state === "loaded" && !detail && tab === "exchanges" && (
        <ul data-testid="exchanges-list" className="mt-4 space-y-3">
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
      className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors -mb-px ${
        active
          ? "border-zinc-900 text-zinc-900 dark:border-zinc-100 dark:text-zinc-100"
          : "border-transparent text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300"
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
    <li
      data-testid={`run-${run.id}`}
      className="cursor-pointer rounded-lg border border-zinc-200 bg-white p-4 hover:border-zinc-400 dark:border-zinc-700 dark:bg-zinc-900 dark:hover:border-zinc-500"
      onClick={() => onSelect(run.id)}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <StatusBadge status={run.status} />
            <ReviewStateBadge state={run.summary_review_state} />
          </div>
          <p className="mt-2 text-sm text-zinc-800 dark:text-zinc-200 line-clamp-2">
            {run.research_query}
          </p>
          <div className="mt-2 flex gap-3 text-xs text-zinc-500">
            <span>{run.invocation_origin.replace(/_/g, " ")}</span>
            <span>{run.findings_count} findings</span>
            <span>{run.sources_count} sources</span>
            {run.document_name && <span>📄 {run.document_name}</span>}
          </div>
        </div>
        <time className="text-xs text-zinc-400 whitespace-nowrap">
          {new Date(run.created_at).toLocaleDateString()}
        </time>
      </div>
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
    <li
      data-testid={`exchange-${exchange.id}`}
      className="cursor-pointer rounded-lg border border-zinc-200 bg-white p-4 hover:border-zinc-400 dark:border-zinc-700 dark:bg-zinc-900 dark:hover:border-zinc-500"
      onClick={() => onSelect(exchange)}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <StatusBadge status={exchange.status} />
            <ReviewStateBadge state={exchange.review_state} />
            <span className="text-xs font-mono text-zinc-400">{exchange.gemini_mode}</span>
          </div>
          <p className="mt-2 text-sm text-zinc-800 dark:text-zinc-200 line-clamp-2">
            {exchange.prompt}
          </p>
          <div className="mt-2 flex gap-3 text-xs text-zinc-500">
            <span>{exchange.invocation_origin.replace(/_/g, " ")}</span>
            {exchange.duration_ms !== null && (
              <span>{(exchange.duration_ms / 1000).toFixed(1)}s</span>
            )}
          </div>
        </div>
        <time className="text-xs text-zinc-400 whitespace-nowrap">
          {new Date(exchange.created_at).toLocaleDateString()}
        </time>
      </div>
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
    <div data-testid="run-detail" className="mt-4">
      <button
        onClick={onBack}
        data-testid="detail-back"
        className="text-sm text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300"
      >
        ← Back to list
      </button>

      <div className="mt-4 space-y-4">
        {/* Header */}
        <div className="flex items-center gap-2">
          <StatusBadge status={run.status} />
          <ReviewStateBadge state={run.summary_review_state} />
        </div>

        <h2 className="text-lg font-medium text-zinc-900 dark:text-zinc-100">
          Research Run
        </h2>

        {/* Provenance */}
        <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
          <dt className="text-zinc-500">Origin</dt>
          <dd className="text-zinc-800 dark:text-zinc-200">{run.invocation_origin.replace(/_/g, " ")}</dd>
          <dt className="text-zinc-500">Query</dt>
          <dd className="text-zinc-800 dark:text-zinc-200">{run.research_query}</dd>
          {run.document_name && (
            <>
              <dt className="text-zinc-500">Document</dt>
              <dd className="text-zinc-800 dark:text-zinc-200">{run.document_name}</dd>
            </>
          )}
          {run.document_url && (
            <>
              <dt className="text-zinc-500">Google Doc</dt>
              <dd>
                <a
                  href={run.document_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 underline dark:text-blue-400"
                >
                  Open Document
                </a>
              </dd>
            </>
          )}
          {run.error_message && (
            <>
              <dt className="text-zinc-500">Error</dt>
              <dd className="text-red-600 dark:text-red-400">{run.error_message}</dd>
            </>
          )}
        </dl>

        {/* Summary + review controls */}
        {run.summary && (
          <section data-testid="run-summary" className="rounded-lg border border-zinc-200 bg-zinc-50 p-4 dark:border-zinc-700 dark:bg-zinc-900">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-zinc-700 dark:text-zinc-300">Summary</h3>
              <ReviewStateBadge state={run.summary.review_state} />
            </div>
            <p className="mt-2 text-sm text-zinc-700 dark:text-zinc-300 whitespace-pre-wrap">
              {run.summary.summary_text}
            </p>
            {run.summary.review_state === "pending_review" && (
              <div className="mt-3 flex gap-2">
                <button
                  data-testid="review-btn-accept"
                  onClick={() => onReview(run.id, "accepted")}
                  className="rounded-md bg-green-100 px-3 py-1 text-xs font-medium text-green-700 hover:bg-green-200 dark:bg-green-900 dark:text-green-300"
                >
                  Accept
                </button>
                <button
                  data-testid="review-btn-reject"
                  onClick={() => onReview(run.id, "rejected")}
                  className="rounded-md bg-red-100 px-3 py-1 text-xs font-medium text-red-700 hover:bg-red-200 dark:bg-red-900 dark:text-red-300"
                >
                  Reject
                </button>
              </div>
            )}
          </section>
        )}

        {/* Findings */}
        {run.findings.length > 0 && (
          <section data-testid="run-findings">
            <h3 className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
              Findings ({run.findings.length})
            </h3>
            <ul className="mt-2 space-y-2">
              {run.findings.map((f) => (
                <li
                  key={f.id}
                  className="rounded-md border border-zinc-200 bg-white p-3 text-sm dark:border-zinc-700 dark:bg-zinc-900"
                >
                  <div className="flex items-center gap-2 text-xs text-zinc-500">
                    <span className="font-mono">{f.finding_type}</span>
                    {f.confidence_signal && <span>confidence: {f.confidence_signal}</span>}
                  </div>
                  <p className="mt-1 text-zinc-800 dark:text-zinc-200 whitespace-pre-wrap">
                    {f.content}
                  </p>
                  {f.source_url && (
                    <a
                      href={f.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-1 block text-xs text-blue-600 dark:text-blue-400"
                    >
                      {f.source_url}
                    </a>
                  )}
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* Sources */}
        {run.sources.length > 0 && (
          <section data-testid="run-sources">
            <h3 className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
              Sources ({run.sources.length})
            </h3>
            <ul className="mt-2 space-y-2">
              {run.sources.map((s) => (
                <li
                  key={s.id}
                  className="rounded-md border border-zinc-200 bg-white p-3 text-sm dark:border-zinc-700 dark:bg-zinc-900"
                >
                  {s.source_title && (
                    <p className="font-medium text-zinc-800 dark:text-zinc-200">
                      {s.source_title}
                    </p>
                  )}
                  {s.source_description && (
                    <p className="mt-1 text-zinc-600 dark:text-zinc-400">
                      {s.source_description}
                    </p>
                  )}
                  {s.source_url && (
                    <a
                      href={s.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-1 block text-xs text-blue-600 dark:text-blue-400"
                    >
                      {s.source_url}
                    </a>
                  )}
                  {s.relevance_notes && (
                    <p className="mt-1 text-xs text-zinc-500">{s.relevance_notes}</p>
                  )}
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>
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
    <div data-testid="exchange-detail" className="mt-4">
      <button
        onClick={onBack}
        data-testid="detail-back"
        className="text-sm text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300"
      >
        ← Back to list
      </button>

      <div className="mt-4 space-y-4">
        <div className="flex items-center gap-2">
          <StatusBadge status={exchange.status} />
          <ReviewStateBadge state={exchange.review_state} />
          <span className="text-xs font-mono text-zinc-400">{exchange.gemini_mode}</span>
        </div>

        <h2 className="text-lg font-medium text-zinc-900 dark:text-zinc-100">
          Expert Advice Exchange
        </h2>

        {/* Provenance */}
        <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
          <dt className="text-zinc-500">Origin</dt>
          <dd className="text-zinc-800 dark:text-zinc-200">{exchange.invocation_origin.replace(/_/g, " ")}</dd>
          {exchange.duration_ms !== null && (
            <>
              <dt className="text-zinc-500">Duration</dt>
              <dd className="text-zinc-800 dark:text-zinc-200">{(exchange.duration_ms / 1000).toFixed(1)}s</dd>
            </>
          )}
          {exchange.error_message && (
            <>
              <dt className="text-zinc-500">Error</dt>
              <dd className="text-red-600 dark:text-red-400">{exchange.error_message}</dd>
            </>
          )}
        </dl>

        {/* Prompt */}
        <section>
          <h3 className="text-sm font-medium text-zinc-700 dark:text-zinc-300">Prompt</h3>
          <div className="mt-1 rounded-md border border-zinc-200 bg-zinc-50 p-3 text-sm text-zinc-800 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-200 whitespace-pre-wrap">
            {exchange.prompt}
          </div>
        </section>

        {/* Response + review controls */}
        {exchange.response_text && (
          <section data-testid="exchange-response">
            <h3 className="text-sm font-medium text-zinc-700 dark:text-zinc-300">Response</h3>
            <div className="mt-1 rounded-md border border-zinc-200 bg-white p-3 text-sm text-zinc-800 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-200 whitespace-pre-wrap">
              {exchange.response_text}
            </div>
          </section>
        )}

        {exchange.review_state === "pending_review" && (
          <div className="flex gap-2">
            <button
              data-testid="review-btn-accept"
              onClick={() => onReview(exchange.id, "accepted")}
              className="rounded-md bg-green-100 px-3 py-1 text-xs font-medium text-green-700 hover:bg-green-200 dark:bg-green-900 dark:text-green-300"
            >
              Accept
            </button>
            <button
              data-testid="review-btn-reject"
              onClick={() => onReview(exchange.id, "rejected")}
              className="rounded-md bg-red-100 px-3 py-1 text-xs font-medium text-red-700 hover:bg-red-200 dark:bg-red-900 dark:text-red-300"
            >
              Reject
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Shared UI helpers ───────────────────────────────────────────

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    completed: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
    in_progress: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
    pending: "bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400",
    failed: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
    degraded: "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300",
  };
  const cls = colors[status] ?? colors.pending;
  return (
    <span
      data-testid="status-badge"
      className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${cls}`}
    >
      {status.replace(/_/g, " ")}
    </span>
  );
}

function ReviewStateBadge({ state }: { state: string | null }) {
  if (!state) return null;
  const colors: Record<string, string> = {
    pending_review: "bg-amber-200 text-amber-800 dark:bg-amber-800 dark:text-amber-200",
    accepted: "bg-green-200 text-green-800 dark:bg-green-800 dark:text-green-200",
    rejected: "bg-red-200 text-red-800 dark:bg-red-800 dark:text-red-200",
  };
  const cls = colors[state] ?? colors.pending_review;
  return (
    <span
      data-testid="review-state-badge"
      className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${cls}`}
    >
      {state.replace(/_/g, " ")}
    </span>
  );
}

