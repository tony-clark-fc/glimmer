"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { fetchProject, ApiError } from "@/lib/api-client";
import type { ProjectDetail } from "@/lib/types";

type LoadState = "loading" | "loaded" | "not-found" | "error";

export default function ProjectPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;

  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    fetchProject(id)
      .then((p) => {
        if (!cancelled) {
          setProject(p);
          setState("loaded");
        }
      })
      .catch((err) => {
        if (cancelled) return;
        if (err instanceof ApiError && err.status === 404) {
          setState("not-found");
        } else {
          setError(err.message ?? "Failed to load project");
          setState("error");
        }
      });
    return () => {
      cancelled = true;
    };
  }, [id]);

  return (
    <div data-testid="page-project">
      <div className="mb-4">
        <Link
          href="/portfolio"
          className="text-sm text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300"
        >
          ← Portfolio
        </Link>
      </div>

      {state === "loading" && (
        <div data-testid="project-loading" className="text-sm text-zinc-500">
          Loading project…
        </div>
      )}

      {state === "not-found" && (
        <div
          data-testid="project-not-found"
          className="rounded-lg border border-dashed border-zinc-300 p-8 text-center text-sm text-zinc-500 dark:border-zinc-700"
        >
          Project not found.
        </div>
      )}

      {state === "error" && (
        <div
          data-testid="project-error"
          className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-300"
        >
          {error}
        </div>
      )}

      {state === "loaded" && project && (
        <>
          <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
            {project.name}
          </h1>

          <div className="mt-2 flex items-center gap-3 text-sm text-zinc-500">
            <span data-testid="project-status" className="capitalize">
              {project.status}
            </span>
            {project.phase && (
              <span data-testid="project-phase">Phase: {project.phase}</span>
            )}
            {project.priority_band && (
              <span data-testid="project-priority-band">
                Priority: {project.priority_band}
              </span>
            )}
          </div>

          {project.objective && (
            <p
              data-testid="project-objective"
              className="mt-3 text-zinc-700 dark:text-zinc-300"
            >
              {project.objective}
            </p>
          )}

          {project.short_summary && (
            <p
              data-testid="project-summary"
              className="mt-2 text-sm text-zinc-500"
            >
              {project.short_summary}
            </p>
          )}

          <div className="mt-8 grid gap-6 lg:grid-cols-2">
            {/* Open items */}
            <ContextPanel
              testId="project-open-items"
              title="Open Items"
              emptyText="No open items."
            >
              {project.open_items.map((item) => (
                <li
                  key={item.id}
                  className="flex items-start justify-between gap-2 rounded-md border border-zinc-200 bg-white p-3 dark:border-zinc-700 dark:bg-zinc-900"
                >
                  <div>
                    <span className="text-sm text-zinc-800 dark:text-zinc-200">
                      {item.title}
                    </span>
                    <span className="ml-2 text-xs text-zinc-400 capitalize">
                      {item.status}
                    </span>
                  </div>
                  {item.due_date && (
                    <span className="text-xs text-zinc-400 whitespace-nowrap">
                      Due {new Date(item.due_date).toLocaleDateString()}
                    </span>
                  )}
                </li>
              ))}
            </ContextPanel>

            {/* Blockers */}
            <ContextPanel
              testId="project-blockers"
              title="Active Blockers"
              emptyText="No active blockers."
              alert
            >
              {project.blockers.map((b) => (
                <li
                  key={b.id}
                  className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-300"
                >
                  {b.summary}
                </li>
              ))}
            </ContextPanel>

            {/* Waiting on */}
            <ContextPanel
              testId="project-waiting-on"
              title="Waiting On"
              emptyText="Not waiting on anything."
            >
              {project.waiting_on.map((w) => (
                <li
                  key={w.id}
                  className="rounded-md border border-zinc-200 bg-white p-3 dark:border-zinc-700 dark:bg-zinc-900"
                >
                  <span className="text-sm font-medium text-zinc-800 dark:text-zinc-200">
                    {w.waiting_on}
                  </span>
                  <p className="text-xs text-zinc-500 mt-1">{w.description}</p>
                </li>
              ))}
            </ContextPanel>

            {/* Pending actions */}
            <ContextPanel
              testId="project-pending-actions"
              title="Pending Actions (Review Required)"
              emptyText="No actions pending review."
            >
              {project.pending_actions.map((a) => (
                <li
                  key={a.id}
                  className="rounded-md border border-amber-200 bg-amber-50 p-3 dark:border-amber-800 dark:bg-amber-950"
                >
                  <span className="text-sm text-amber-800 dark:text-amber-200">
                    {a.action_text}
                  </span>
                  {a.urgency && (
                    <span className="ml-2 text-xs text-amber-600 dark:text-amber-400">
                      Urgency: {a.urgency}
                    </span>
                  )}
                </li>
              ))}
            </ContextPanel>
          </div>
        </>
      )}
    </div>
  );
}

// ── Context panel helper ────────────────────────────────────────

function ContextPanel({
  testId,
  title,
  emptyText,
  alert,
  children,
}: {
  testId: string;
  title: string;
  emptyText: string;
  alert?: boolean;
  children: React.ReactNode;
}) {
  const items = Array.isArray(children) ? children : children ? [children] : [];
  const hasItems = items.length > 0;

  return (
    <div data-testid={testId}>
      <h2
        className={`text-lg font-medium ${
          alert && hasItems
            ? "text-red-700 dark:text-red-300"
            : "text-zinc-800 dark:text-zinc-200"
        }`}
      >
        {title}
      </h2>
      {!hasItems ? (
        <p className="mt-2 text-sm text-zinc-500">{emptyText}</p>
      ) : (
        <ul className="mt-2 space-y-2">{children}</ul>
      )}
    </div>
  );
}
