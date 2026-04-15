"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { fetchProject, ApiError } from "@/lib/api-client";
import {
  SectionCard,
  CardSkeleton,
  EmptyState,
  ErrorState,
  Badge,
} from "@/components/ui";
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
      <div className="mb-8">
        <Link
          href="/portfolio"
          className="inline-flex items-center gap-1 text-sm text-muted-light hover:text-primary transition-colors"
        >
          ← Portfolio
        </Link>
      </div>

      {state === "loading" && (
        <CardSkeleton testId="project-loading" count={2} />
      )}

      {state === "not-found" && (
        <EmptyState
          testId="project-not-found"
          icon="🔍"
          message="Project not found."
        />
      )}

      {state === "error" && (
        <ErrorState testId="project-error" message={error ?? "Failed to load project"} />
      )}

      {state === "loaded" && project && (
        <>
          {/* Project header */}
          <div className="mb-10 atmospheric-glow">
            <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-foreground font-headline">
              {project.name}
            </h1>

            <div className="mt-4 flex flex-wrap items-center gap-2">
              <Badge
                testId="project-status"
                variant={project.status === "active" ? "info" : project.status === "paused" ? "neutral" : "neutral"}
              >
                {project.status.toUpperCase()}
              </Badge>
              {project.phase && (
                <Badge testId="project-phase" variant="accent">Phase: {project.phase}</Badge>
              )}
              {project.priority_band && (
                <Badge testId="project-priority-band" variant="info">Priority: {project.priority_band}</Badge>
              )}
            </div>

            {project.objective && (
              <p
                data-testid="project-objective"
                className="mt-5 text-foreground leading-relaxed"
              >
                {project.objective}
              </p>
            )}

            {project.short_summary && (
              <p
                data-testid="project-summary"
                className="mt-2 text-sm text-on-surface-variant"
              >
                {project.short_summary}
              </p>
            )}
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            {/* Open items */}
            <SectionCard
              testId="project-open-items"
              title="Open Items"
              count={project.open_items.length}
            >
              {project.open_items.length === 0 ? (
                <p className="text-sm text-muted-light">No open items.</p>
              ) : (
                <ul className="space-y-2">
                  {project.open_items.map((item) => (
                    <li
                      key={item.id}
                      className="flex items-start justify-between gap-2 rounded-2xl bg-surface-container-lowest p-4 ghost-border"
                    >
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-foreground">
                          {item.title}
                        </span>
                        <Badge variant="neutral">{item.status}</Badge>
                      </div>
                      {item.due_date && (
                        <span className="text-xs text-muted-light whitespace-nowrap">
                          Due {new Date(item.due_date).toLocaleDateString()}
                        </span>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </SectionCard>

            {/* Blockers */}
            <SectionCard
              testId="project-blockers"
              title="Active Blockers"
              count={project.blockers.length}
              variant="danger"
            >
              {project.blockers.length === 0 ? (
                <p className="text-sm text-muted-light">No active blockers.</p>
              ) : (
                <ul className="space-y-2">
                  {project.blockers.map((b) => (
                    <li
                      key={b.id}
                      className="rounded-2xl bg-red-500/5 p-4 text-sm text-error border border-error/10"
                    >
                      {b.summary}
                    </li>
                  ))}
                </ul>
              )}
            </SectionCard>

            {/* Waiting on */}
            <SectionCard
              testId="project-waiting-on"
              title="Waiting On"
              count={project.waiting_on.length}
              variant="warning"
            >
              {project.waiting_on.length === 0 ? (
                <p className="text-sm text-muted-light">Not waiting on anything.</p>
              ) : (
                <ul className="space-y-2">
                  {project.waiting_on.map((w) => (
                    <li
                      key={w.id}
                      className="rounded-2xl bg-surface-container-lowest p-4 ghost-border"
                    >
                      <span className="text-sm font-semibold text-tertiary">
                        {w.waiting_on}
                      </span>
                      <p className="text-xs text-on-surface-variant mt-1">{w.description}</p>
                    </li>
                  ))}
                </ul>
              )}
            </SectionCard>

            {/* Pending actions */}
            <SectionCard
              testId="project-pending-actions"
              title="Pending Actions (Review Required)"
              count={project.pending_actions.length}
              variant="warning"
            >
              {project.pending_actions.length === 0 ? (
                <p className="text-sm text-muted-light">No actions pending review.</p>
              ) : (
                <ul className="space-y-2">
                  {project.pending_actions.map((a) => (
                    <li
                      key={a.id}
                      className="rounded-2xl bg-tertiary-container/5 p-4 border border-tertiary/10"
                    >
                      <span className="text-sm text-foreground">
                        {a.action_text}
                      </span>
                      {a.urgency && (
                        <Badge variant="warning">{a.urgency}</Badge>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </SectionCard>
          </div>
        </>
      )}
    </div>
  );
}
