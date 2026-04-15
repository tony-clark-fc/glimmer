"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { fetchProjects } from "@/lib/api-client";
import {
  PageHeader,
  CardSkeleton,
  EmptyState,
  ErrorState,
  Badge,
  ActionButton,
} from "@/components/ui";
import { ProjectFormModal } from "@/components/project-form-modal";
import type { ProjectSummary, ProjectDetail } from "@/lib/types";

type LoadState = "loading" | "loaded" | "empty" | "error";

export default function PortfolioPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [showArchived, setShowArchived] = useState(false);

  const loadProjects = useCallback(() => {
    setState("loading");
    fetchProjects()
      .then((data) => {
        setProjects(data);
        setState(data.length > 0 ? "loaded" : "empty");
      })
      .catch((err) => {
        setError(err.message ?? "Failed to load projects");
        setState("error");
      });
  }, []);

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  const handleProjectCreated = useCallback(
    (project: ProjectDetail) => {
      setShowModal(false);
      router.push(`/projects/${project.id}`);
    },
    [router],
  );

  // Filter archived projects on the client based on toggle
  const visibleProjects = showArchived
    ? projects
    : projects.filter((p) => !p.archived);

  return (
    <div data-testid="page-portfolio">
      <PageHeader
        title="Portfolio"
        description="Compare active projects across urgency, health, and attention demand."
      >
        <ActionButton
          testId="portfolio-new-project"
          variant="primary"
          size="md"
          onClick={() => setShowModal(true)}
        >
          + New Project
        </ActionButton>
      </PageHeader>

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
        <>
          {/* Show archived toggle */}
          {projects.some((p) => p.archived) && (
            <div className="flex items-center gap-2 mb-4">
              <label className="flex items-center gap-2 text-sm text-muted-light cursor-pointer">
                <input
                  type="checkbox"
                  data-testid="portfolio-show-archived"
                  checked={showArchived}
                  onChange={(e) => setShowArchived(e.target.checked)}
                  className="rounded border-outline-variant/30"
                />
                Show archived
              </label>
            </div>
          )}

          <div
            data-testid="portfolio-project-list"
            className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3"
          >
            {visibleProjects.map((p) => (
              <Link
                key={p.id}
                href={`/projects/${p.id}`}
                data-testid={`portfolio-project-${p.id}`}
                className={`group block luminous-card rounded-2xl p-6 cursor-pointer ${
                  p.archived ? "opacity-50" : ""
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <h2 className="font-headline font-bold text-foreground truncate group-hover:text-primary transition-colors">
                    {p.name}
                  </h2>
                  <StatusBadge status={p.status} archived={p.archived} />
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
        </>
      )}

      <ProjectFormModal
        open={showModal}
        onClose={() => setShowModal(false)}
        onSuccess={handleProjectCreated}
      />
    </div>
  );
}

// ── Helpers ──────────────────────────────────────────────────────

function StatusBadge({ status, archived }: { status: string; archived?: boolean }) {
  if (archived) {
    return <Badge variant="neutral">ARCHIVED</Badge>;
  }
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
