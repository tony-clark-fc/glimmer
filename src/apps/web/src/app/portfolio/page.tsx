"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchProjects } from "@/lib/api-client";
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
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
        Portfolio
      </h1>
      <p className="mt-2 text-zinc-600 dark:text-zinc-400">
        Compare active projects across urgency, health, and attention demand.
      </p>

      {state === "loading" && (
        <div data-testid="portfolio-loading" className="mt-8 text-sm text-zinc-500">
          Loading projects…
        </div>
      )}

      {state === "error" && (
        <div
          data-testid="portfolio-error"
          className="mt-8 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-300"
        >
          {error}
        </div>
      )}

      {state === "empty" && (
        <div
          data-testid="portfolio-empty-state"
          className="mt-8 rounded-lg border border-dashed border-zinc-300 p-8 text-center text-sm text-zinc-500 dark:border-zinc-700 dark:text-zinc-500"
        >
          No projects yet. Create your first project to start building your
          portfolio view.
        </div>
      )}

      {state === "loaded" && (
        <div
          data-testid="portfolio-project-list"
          className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
        >
          {projects.map((p) => (
            <Link
              key={p.id}
              href={`/projects/${p.id}`}
              data-testid={`portfolio-project-${p.id}`}
              className="block rounded-lg border border-zinc-200 bg-white p-4 transition-shadow hover:shadow-md dark:border-zinc-700 dark:bg-zinc-900"
            >
              <div className="flex items-center justify-between">
                <h2 className="font-medium text-zinc-900 dark:text-zinc-100 truncate">
                  {p.name}
                </h2>
                <StatusBadge status={p.status} />
              </div>

              {p.short_summary && (
                <p className="mt-1 text-sm text-zinc-500 line-clamp-2">
                  {p.short_summary}
                </p>
              )}

              <div className="mt-3 flex gap-3 text-xs text-zinc-500">
                <AttentionSignal
                  label="Open items"
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
  const colors: Record<string, string> = {
    active:
      "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
    paused:
      "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
    completed:
      "bg-zinc-100 text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400",
  };

  return (
    <span
      className={`rounded-full px-2 py-0.5 text-xs font-medium ${colors[status] ?? "bg-zinc-100 text-zinc-500"}`}
    >
      {status}
    </span>
  );
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
      className={count > 0 && alert ? "text-red-600 dark:text-red-400 font-medium" : ""}
    >
      {count} {label}
    </span>
  );
}
