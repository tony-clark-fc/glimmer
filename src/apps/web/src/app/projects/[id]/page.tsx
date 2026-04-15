"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { fetchProject, updateProject, archiveProject, ApiError } from "@/lib/api-client";
import {
  SectionCard,
  CardSkeleton,
  EmptyState,
  ErrorState,
  Badge,
  ActionButton,
} from "@/components/ui";
import type { ProjectDetail } from "@/lib/types";

type LoadState = "loading" | "loaded" | "not-found" | "error";

export default function ProjectPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;

  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);

  // ── Edit mode state ────────────────────────────────────────────
  const [editing, setEditing] = useState(false);
  const [editName, setEditName] = useState("");
  const [editObjective, setEditObjective] = useState("");
  const [editSummary, setEditSummary] = useState("");
  const [editPhase, setEditPhase] = useState("");
  const [editPriorityBand, setEditPriorityBand] = useState("");
  const [editStatus, setEditStatus] = useState("");
  const [saving, setSaving] = useState(false);
  const [archiving, setArchiving] = useState(false);
  const [showArchiveConfirm, setShowArchiveConfirm] = useState(false);

  const loadProject = useCallback(() => {
    if (!id) return;
    setState("loading");
    fetchProject(id)
      .then((p) => {
        setProject(p);
        setState("loaded");
      })
      .catch((err) => {
        if (err instanceof ApiError && err.status === 404) {
          setState("not-found");
        } else {
          setError(err.message ?? "Failed to load project");
          setState("error");
        }
      });
  }, [id]);

  useEffect(() => {
    loadProject();
  }, [loadProject]);

  const startEditing = useCallback(() => {
    if (!project) return;
    setEditName(project.name);
    setEditObjective(project.objective ?? "");
    setEditSummary(project.short_summary ?? "");
    setEditPhase(project.phase ?? "");
    setEditPriorityBand(project.priority_band ?? "");
    setEditStatus(project.status);
    setEditing(true);
  }, [project]);

  const cancelEditing = useCallback(() => {
    setEditing(false);
  }, []);

  const saveEdits = useCallback(async () => {
    if (!id || !project) return;
    const trimmedName = editName.trim();
    if (!trimmedName) return;

    setSaving(true);
    try {
      const updated = await updateProject(id, {
        name: trimmedName,
        objective: editObjective.trim() || undefined,
        short_summary: editSummary.trim() || undefined,
        phase: editPhase.trim() || undefined,
        priority_band: editPriorityBand || undefined,
        status: editStatus || undefined,
      });
      setProject(updated);
      setEditing(false);
    } catch {
      // Keep edit mode open on error
    } finally {
      setSaving(false);
    }
  }, [id, project, editName, editObjective, editSummary, editPhase, editPriorityBand, editStatus]);

  const handleArchive = useCallback(async () => {
    if (!id) return;
    setArchiving(true);
    try {
      const updated = await archiveProject(id);
      setProject(updated);
      setShowArchiveConfirm(false);
    } catch {
      // silent
    } finally {
      setArchiving(false);
    }
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
            {editing ? (
              /* ── Edit mode ──────────────────────────── */
              <div data-testid="project-edit-form" className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-primary tracking-wide uppercase mb-1">Name</label>
                  <input
                    data-testid="project-edit-name"
                    type="text"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    className="w-full rounded-xl bg-surface-container-lowest border border-outline-variant/30 px-4 py-2.5 text-lg font-bold text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40"
                  />
                </div>
                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <label className="block text-xs font-bold text-primary tracking-wide uppercase mb-1">Status</label>
                    <select
                      data-testid="project-edit-status"
                      value={editStatus}
                      onChange={(e) => setEditStatus(e.target.value)}
                      className="w-full rounded-xl bg-surface-container-lowest border border-outline-variant/30 px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40"
                    >
                      <option value="active">Active</option>
                      <option value="planning">Planning</option>
                      <option value="paused">Paused</option>
                      <option value="completed">Completed</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-primary tracking-wide uppercase mb-1">Phase</label>
                    <input
                      data-testid="project-edit-phase"
                      type="text"
                      value={editPhase}
                      onChange={(e) => setEditPhase(e.target.value)}
                      className="w-full rounded-xl bg-surface-container-lowest border border-outline-variant/30 px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-primary tracking-wide uppercase mb-1">Priority</label>
                    <select
                      data-testid="project-edit-priority"
                      value={editPriorityBand}
                      onChange={(e) => setEditPriorityBand(e.target.value)}
                      className="w-full rounded-xl bg-surface-container-lowest border border-outline-variant/30 px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40"
                    >
                      <option value="">Not set</option>
                      <option value="critical">Critical</option>
                      <option value="high">High</option>
                      <option value="medium">Medium</option>
                      <option value="low">Low</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-bold text-primary tracking-wide uppercase mb-1">Objective</label>
                  <textarea
                    data-testid="project-edit-objective"
                    value={editObjective}
                    onChange={(e) => setEditObjective(e.target.value)}
                    rows={2}
                    className="w-full rounded-xl bg-surface-container-lowest border border-outline-variant/30 px-4 py-2.5 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 resize-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-primary tracking-wide uppercase mb-1">Summary</label>
                  <input
                    data-testid="project-edit-summary"
                    type="text"
                    value={editSummary}
                    onChange={(e) => setEditSummary(e.target.value)}
                    className="w-full rounded-xl bg-surface-container-lowest border border-outline-variant/30 px-4 py-2.5 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40"
                  />
                </div>
                <div className="flex gap-3">
                  <ActionButton
                    testId="project-edit-save"
                    variant="primary"
                    size="sm"
                    onClick={saveEdits}
                  >
                    {saving ? "Saving…" : "Save Changes"}
                  </ActionButton>
                  <ActionButton
                    testId="project-edit-cancel"
                    variant="ghost"
                    size="sm"
                    onClick={cancelEditing}
                  >
                    Cancel
                  </ActionButton>
                </div>
              </div>
            ) : (
              /* ── Display mode ──────────────────────── */
              <>
                <div className="flex items-start justify-between gap-4">
                  <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-foreground font-headline">
                    {project.name}
                  </h1>
                  <div className="flex items-center gap-2 shrink-0">
                    {!project.archived && (
                      <>
                        <ActionButton
                          testId="project-edit-button"
                          variant="ghost"
                          size="sm"
                          onClick={startEditing}
                        >
                          Edit
                        </ActionButton>
                        <ActionButton
                          testId="project-archive-button"
                          variant="danger"
                          size="sm"
                          onClick={() => setShowArchiveConfirm(true)}
                        >
                          Archive
                        </ActionButton>
                      </>
                    )}
                  </div>
                </div>

                <div className="mt-4 flex flex-wrap items-center gap-2">
                  {project.archived ? (
                    <Badge testId="project-status" variant="neutral">ARCHIVED</Badge>
                  ) : (
                    <Badge
                      testId="project-status"
                      variant={project.status === "active" ? "info" : project.status === "paused" ? "neutral" : "neutral"}
                    >
                      {project.status.toUpperCase()}
                    </Badge>
                  )}
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
              </>
            )}
          </div>

          {/* Archive confirmation */}
          {showArchiveConfirm && (
            <div
              data-testid="project-archive-confirm"
              className="mb-6 rounded-2xl bg-error-container/10 border border-error/20 p-5"
            >
              <p className="text-sm text-error font-medium mb-3">
                Archive &quot;{project.name}&quot;? This will remove it from the active portfolio view.
              </p>
              <div className="flex gap-3">
                <ActionButton
                  testId="project-archive-confirm-yes"
                  variant="danger"
                  size="sm"
                  onClick={handleArchive}
                >
                  {archiving ? "Archiving…" : "Yes, Archive"}
                </ActionButton>
                <ActionButton
                  testId="project-archive-confirm-no"
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowArchiveConfirm(false)}
                >
                  Cancel
                </ActionButton>
              </div>
            </div>
          )}

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
