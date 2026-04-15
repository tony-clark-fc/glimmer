"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchProjects } from "@/lib/api-client";
import {
  PageHeader,
  CardSkeleton,
  EmptyState,
  ErrorState,
  Badge,
} from "@/components/ui";
import type { ProjectSummary } from "@/lib/types";

type LoadState = "loading" | "loaded" | "empty" | "error";

export default function PortfolioPage() {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchProjects()
      .then((data) => {
        if (cancelled) return;
        setProjects(data);
        setState(data.length > 0 ? "loaded" : "empty");
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err.message ?? "Failed to load projects");
        setState("error");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div data-testid="page-portfolio">
      <PageHeader
        title="Portfolio"
        description="Compare active projects across urgency, health, and attention demand."
      />

      {state === "loading" && (
        <CardSkeleton testId="portfolio-loading" count={3} />
      )}

      {state === "error" && (
        <ErrorState testId="portfolio-error" message={error ?? "Failed to load projects"} />
      )}

      {state === "empty" && (
        <EmptyState
          testId="portfolio-empty-state"
          icon="◫"
          message="No projects yet. Create your first project to start building your portfolio view."
        />
      )}

      {state === "loaded" && (
        <div
          data-testid="portfolio-project-list"
          className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3"
        >
          {projects.map((p) => (
            <Link
              key={p.id}
              href={`/projects/${p.id}`}
              data-testid={`portfolio-project-${p.id}`}
              className="group block luminous-card rounded-2xl p-6 cursor-pointer"
            >
              <div className="flex items-center justify-between gap-2">
                <h2 className="font-headline font-bold text-foreground truncate group-hover:text-primary transition-colors">
                  {p.name}
                </h2>
                <StatusBadge status={p.status} />
              </div>

              {p.short_summary && (
                <p className="mt-3 text-sm text-on-surface-variant line-clamp-2 leading-relaxed">
                  {p.short_summary}
                </p>
              )}

              <div className="mt-5 flex gap-4 text-xs">
                <AttentionSignal
                  label="Open"
                  count={p.open_items}
                  testId={`project-open-${p.id}`}
                />
                <AttentionSignal
                  label="Blockers"
                  count={p.active_blockers}
                  testId={`project-blockers-${p.id}`}
                  alert
                />
                <AttentionSignal
                  label="Pending"
                  count={p.pending_actions}
                  testId={`project-pending-${p.id}`}
                />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Helpers ──────────────────────────────────────────────────────

function StatusBadge({ status }: { status: string }) {
  const variant =
    status === "active" ? "info" : status === "paused" ? "neutral" : "neutral";
  return <Badge variant={variant}>{status.toUpperCase()}</Badge>;
}

function AttentionSignal({
  label,
  count,
  testId,
  alert,
}: {
  label: string;
  count: number;
  testId: string;
  alert?: boolean;
}) {
  return (
    <span
      data-testid={testId}
      className={`flex items-center gap-1 ${
        count > 0 && alert
          ? "text-error font-bold"
          : "text-muted-light"
      }`}
    >
      <span className="tabular-nums font-bold">{count}</span>
      {label}
    </span>
  );
}
