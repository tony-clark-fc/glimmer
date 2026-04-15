"use client";

import { useEffect, useState } from "react";
import { fetchLatestFocusPack, fetchResearchHealth, ApiError } from "@/lib/api-client";
import { PersonaAvatar } from "@/components/persona-avatar";
import {
  PageHeader,
  SectionCard,
  CardSkeleton,
  EmptyState,
  ErrorState,
  Badge,
  InfoBanner,
} from "@/components/ui";
import type {
  FocusPack,
  FocusPackActionItem,
  FocusPackRiskItem,
  FocusPackWaitingItem,
  ResearchHealth,
} from "@/lib/types";

type LoadState = "loading" | "loaded" | "empty" | "error";

export default function TodayPage() {
  const [focusPack, setFocusPack] = useState<FocusPack | null>(null);
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);
  const [researchHealth, setResearchHealth] = useState<ResearchHealth | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchLatestFocusPack()
      .then((fp) => {
        if (!cancelled) {
          setFocusPack(fp);
          setState("loaded");
        }
      })
      .catch((err) => {
        if (cancelled) return;
        if (err instanceof ApiError && err.status === 404) {
          setState("empty");
        } else {
          setError(err.message ?? "Failed to load focus pack");
          setState("error");
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // Poll research/Chrome health every 30 seconds
  useEffect(() => {
    let cancelled = false;

    const checkHealth = () => {
      fetchResearchHealth()
        .then((h) => {
          if (!cancelled) setResearchHealth(h);
        })
        .catch(() => {
          // Silently ignore — health check may fail if backend is starting
        });
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30_000);

    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  return (
    <div data-testid="page-today" className="atmospheric-glow">
      <div className="flex items-start gap-4 mb-10">
        <PersonaAvatar context="today" size="md" />
        <PageHeader
          title="Today"
          description="Your daily operating brief — priorities, deadlines, and what needs attention now."
        >
          {researchHealth && <ResearchStatusChip health={researchHealth} />}
        </PageHeader>
      </div>

      {state === "loading" && (
        <CardSkeleton testId="today-loading" count={3} />
      )}

      {state === "error" && (
        <ErrorState testId="today-error" message={error ?? "Failed to load focus pack"} />
      )}

      {state === "empty" && (
        <EmptyState
          testId="today-empty-state"
          icon="☀"
          message="No priorities yet. Connect accounts and ingest signals to populate your daily brief."
        />
      )}

      {state === "loaded" && focusPack && (
        <div data-testid="today-focus-pack" className="space-y-8">
          {/* Narrative summary — Glimmer persona banner */}
          {focusPack.narrative_summary && (
            <InfoBanner testId="focus-narrative" variant="accent">
              {focusPack.narrative_summary}
            </InfoBanner>
          )}

          {/* Dashboard grid */}
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Top actions — full width */}
            <div className="lg:col-span-2">
              <TopActionsSection items={focusPack.top_actions?.items ?? []} />
            </div>

            {/* High risk items */}
            <HighRiskSection items={focusPack.high_risk_items?.items ?? []} />

            {/* Waiting on */}
            <WaitingOnSection items={focusPack.waiting_on_items?.items ?? []} />
          </div>

          {/* Pressure indicators */}
          {(focusPack.reply_debt_summary || focusPack.calendar_pressure_summary) && (
            <div className="grid gap-4 sm:grid-cols-2">
              {focusPack.reply_debt_summary && (
                <div data-testid="focus-reply-debt" className="rounded-2xl bg-surface-container-low p-5 ghost-border">
                  <h3 className="text-xs font-bold text-muted-light uppercase tracking-widest mb-2 font-headline">Reply Debt</h3>
                  <p className="text-sm text-foreground leading-relaxed">{focusPack.reply_debt_summary}</p>
                </div>
              )}
              {focusPack.calendar_pressure_summary && (
                <div data-testid="focus-calendar-pressure" className="rounded-2xl bg-surface-container-low p-5 ghost-border">
                  <h3 className="text-xs font-bold text-muted-light uppercase tracking-widest mb-2 font-headline">Calendar Pressure</h3>
                  <p className="text-sm text-foreground leading-relaxed">{focusPack.calendar_pressure_summary}</p>
                </div>
              )}
            </div>
          )}

          <p className="text-xs text-muted-light">
            Generated{" "}
            {new Date(focusPack.generated_at).toLocaleString()}
          </p>
        </div>
      )}
    </div>
  );
}

// ── Top Actions section ─────────────────────────────────────────

function TopActionsSection({ items }: { items: FocusPackActionItem[] }) {
  return (
    <SectionCard testId="focus-top-actions" title="Top Actions" count={items.length}>
      {items.length === 0 ? (
        <p className="text-sm text-muted-light">No top actions right now.</p>
      ) : (
        <ul className="space-y-3">
          {items.map((item, i) => (
            <li
              key={item.item_id}
              data-testid={`focus-action-${item.item_id}`}
              className="flex items-start gap-4 rounded-2xl bg-surface-container-lowest p-4 ghost-border hover:border-primary/20 transition-all"
            >
              {/* Rank number */}
              <span className="flex items-center justify-center h-7 w-7 rounded-full bg-primary/10 text-primary text-xs font-bold shrink-0 border border-primary/20">
                {i + 1}
              </span>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold text-foreground">
                  {item.title}
                </p>
                <p className="mt-1 text-xs text-on-surface-variant leading-relaxed">
                  {item.rationale}
                </p>
              </div>
              <div className="flex shrink-0 items-center gap-2">
                <ItemTypeBadge type={item.item_type} />
                <PriorityIndicator score={item.priority_score} />
              </div>
            </li>
          ))}
        </ul>
      )}
    </SectionCard>
  );
}

// ── High Risk section ───────────────────────────────────────────

function HighRiskSection({ items }: { items: FocusPackRiskItem[] }) {
  return (
    <SectionCard testId="focus-high-risk" title="High Risk" count={items.length} variant="danger">
      {items.length === 0 ? (
        <p className="text-sm text-muted-light">No high-risk items flagged.</p>
      ) : (
        <ul className="space-y-2">
          {items.map((item) => (
            <li
              key={item.risk_id}
              data-testid={`focus-risk-${item.risk_id}`}
              className="flex items-start justify-between gap-3 rounded-2xl bg-red-500/5 p-4 border border-error/10"
            >
              <p className="text-sm text-error">
                {item.summary}
              </p>
              <SeverityBadge severity={item.severity} />
            </li>
          ))}
        </ul>
      )}
    </SectionCard>
  );
}

// ── Waiting On section ──────────────────────────────────────────

function WaitingOnSection({ items }: { items: FocusPackWaitingItem[] }) {
  return (
    <SectionCard testId="focus-waiting-on" title="Waiting On" count={items.length} variant="warning">
      {items.length === 0 ? (
        <p className="text-sm text-muted-light">
          Nothing waiting on external responses.
        </p>
      ) : (
        <ul className="space-y-2">
          {items.map((item) => (
            <li
              key={item.waiting_id}
              data-testid={`focus-waiting-${item.waiting_id}`}
              className="rounded-2xl bg-tertiary-container/5 p-4 border border-tertiary/10"
            >
              <p className="text-sm font-semibold text-tertiary">
                {item.waiting_on}
              </p>
              <p className="mt-1 text-xs text-on-surface-variant">
                {item.description}
              </p>
              {item.expected_by && (
                <p className="mt-1 text-xs text-muted-light">
                  Expected by{" "}
                  {new Date(item.expected_by).toLocaleDateString()}
                </p>
              )}
            </li>
          ))}
        </ul>
      )}
    </SectionCard>
  );
}

// ── Shared helper components ────────────────────────────────────

function ItemTypeBadge({ type }: { type: string }) {
  return (
    <Badge variant={type === "work_item" ? "accent" : "warning"}>
      {type === "work_item" ? "Work Item" : "Pending Action"}
    </Badge>
  );
}

function PriorityIndicator({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color =
    score >= 0.7
      ? "bg-error"
      : score >= 0.4
        ? "bg-tertiary"
        : "bg-outline";

  const glow =
    score >= 0.7
      ? "shadow-[0_0_8px_rgba(255,180,171,0.6)]"
      : score >= 0.4
        ? "shadow-[0_0_8px_rgba(255,183,131,0.4)]"
        : "";

  return (
    <div className="flex items-center gap-1.5" title={`Priority: ${pct}%`}>
      <div className="h-1 w-12 rounded-full bg-surface-container-highest/50 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${color} ${glow}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-xs tabular-nums font-bold text-muted-light">{pct}</span>
    </div>
  );
}

function SeverityBadge({ severity }: { severity: string }) {
  const variant =
    severity === "high" ? "danger" : severity === "medium" ? "warning" : "neutral";
  return <Badge variant={variant}>{severity}</Badge>;
}

// ── Research status chip ────────────────────────────────────────

function ResearchStatusChip({ health }: { health: ResearchHealth }) {
  const isOnline = health.chrome_status === "available";
  const isUnknown = health.chrome_status === "unknown";

  const label = isOnline
    ? "Research: Online"
    : isUnknown
      ? "Research: Checking…"
      : "Research: Offline";

  const dotColor = isOnline
    ? "bg-emerald-500"
    : isUnknown
      ? "bg-outline"
      : "bg-tertiary";

  const chipColor = isOnline
    ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
    : isUnknown
      ? "border-outline-variant/30 bg-surface-container-highest/40 text-muted-light"
      : "border-tertiary/20 bg-tertiary-container/10 text-tertiary";

  return (
    <div
      data-testid="research-status"
      className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-bold ${chipColor}`}
    >
      <span className={`inline-block h-2 w-2 rounded-full ${dotColor}`} />
      {label}
    </div>
  );
}
