/**
 * Project form modal — create a new project from the Portfolio page.
 *
 * REQ:ProjectCRUD
 * PLAN:WorkstreamE.PackageE11.ProjectCrudApi
 *
 * Simple form modal with name (required), objective, summary, phase, priority band.
 * On successful creation, calls onSuccess with the new project detail.
 */

"use client";

import { useCallback, useState } from "react";
import { createProject, ApiError } from "@/lib/api-client";
import type { ProjectDetail } from "@/lib/types";

interface ProjectFormModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess: (project: ProjectDetail) => void;
}

export function ProjectFormModal({
  open,
  onClose,
  onSuccess,
}: ProjectFormModalProps) {
  const [name, setName] = useState("");
  const [objective, setObjective] = useState("");
  const [shortSummary, setShortSummary] = useState("");
  const [phase, setPhase] = useState("");
  const [priorityBand, setPriorityBand] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const resetForm = useCallback(() => {
    setName("");
    setObjective("");
    setShortSummary("");
    setPhase("");
    setPriorityBand("");
    setError(null);
    setSaving(false);
  }, []);

  const handleClose = useCallback(() => {
    resetForm();
    onClose();
  }, [onClose, resetForm]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      setError(null);

      const trimmed = name.trim();
      if (!trimmed) {
        setError("Project name is required");
        return;
      }

      setSaving(true);
      try {
        const project = await createProject({
          name: trimmed,
          objective: objective.trim() || undefined,
          short_summary: shortSummary.trim() || undefined,
          phase: phase.trim() || undefined,
          priority_band: priorityBand || undefined,
        });
        resetForm();
        onSuccess(project);
      } catch (err) {
        if (err instanceof ApiError) {
          setError(`Failed to create project: ${err.body}`);
        } else {
          setError("Failed to create project");
        }
      } finally {
        setSaving(false);
      }
    },
    [name, objective, shortSummary, phase, priorityBand, onSuccess, resetForm],
  );

  if (!open) return null;

  return (
    <div
      data-testid="project-form-modal-overlay"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={(e) => {
        if (e.target === e.currentTarget) handleClose();
      }}
    >
      <div
        data-testid="project-form-modal"
        className="luminous-card rounded-2xl w-full max-w-lg mx-4 overflow-hidden"
      >
        {/* Header */}
        <div className="px-6 pt-6 pb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-foreground font-headline">
            New Project
          </h2>
          <button
            data-testid="project-form-close"
            onClick={handleClose}
            className="text-muted-light hover:text-foreground transition-colors text-xl leading-none"
            aria-label="Close"
          >
            ×
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="px-6 pb-6 space-y-4">
          {error && (
            <div
              data-testid="project-form-error"
              className="rounded-xl bg-error-container/10 border border-error/20 px-4 py-2 text-sm text-error"
            >
              {error}
            </div>
          )}

          {/* Name (required) */}
          <div>
            <label
              htmlFor="project-name"
              className="block text-xs font-bold text-primary tracking-wide uppercase mb-1.5"
            >
              Name <span className="text-error">*</span>
            </label>
            <input
              id="project-name"
              data-testid="project-form-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Beta Migration"
              className="w-full rounded-xl bg-surface-container-lowest border border-outline-variant/30 px-4 py-2.5 text-sm text-foreground placeholder:text-muted-light focus:outline-none focus:ring-2 focus:ring-primary/40 transition-shadow"
              autoFocus
              required
            />
          </div>

          {/* Objective */}
          <div>
            <label
              htmlFor="project-objective"
              className="block text-xs font-bold text-primary tracking-wide uppercase mb-1.5"
            >
              Objective
            </label>
            <textarea
              id="project-objective"
              data-testid="project-form-objective"
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              placeholder="What is this project trying to achieve?"
              rows={2}
              className="w-full rounded-xl bg-surface-container-lowest border border-outline-variant/30 px-4 py-2.5 text-sm text-foreground placeholder:text-muted-light focus:outline-none focus:ring-2 focus:ring-primary/40 transition-shadow resize-none"
            />
          </div>

          {/* Short Summary */}
          <div>
            <label
              htmlFor="project-summary"
              className="block text-xs font-bold text-primary tracking-wide uppercase mb-1.5"
            >
              Summary
            </label>
            <input
              id="project-summary"
              data-testid="project-form-summary"
              type="text"
              value={shortSummary}
              onChange={(e) => setShortSummary(e.target.value)}
              placeholder="Brief one-liner for the portfolio view"
              className="w-full rounded-xl bg-surface-container-lowest border border-outline-variant/30 px-4 py-2.5 text-sm text-foreground placeholder:text-muted-light focus:outline-none focus:ring-2 focus:ring-primary/40 transition-shadow"
            />
          </div>

          {/* Phase + Priority Band (inline) */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label
                htmlFor="project-phase"
                className="block text-xs font-bold text-primary tracking-wide uppercase mb-1.5"
              >
                Phase
              </label>
              <input
                id="project-phase"
                data-testid="project-form-phase"
                type="text"
                value={phase}
                onChange={(e) => setPhase(e.target.value)}
                placeholder="e.g. discovery"
                className="w-full rounded-xl bg-surface-container-lowest border border-outline-variant/30 px-4 py-2.5 text-sm text-foreground placeholder:text-muted-light focus:outline-none focus:ring-2 focus:ring-primary/40 transition-shadow"
              />
            </div>
            <div>
              <label
                htmlFor="project-priority"
                className="block text-xs font-bold text-primary tracking-wide uppercase mb-1.5"
              >
                Priority Band
              </label>
              <select
                id="project-priority"
                data-testid="project-form-priority"
                value={priorityBand}
                onChange={(e) => setPriorityBand(e.target.value)}
                className="w-full rounded-xl bg-surface-container-lowest border border-outline-variant/30 px-4 py-2.5 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/40 transition-shadow"
              >
                <option value="">Not set</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              data-testid="project-form-cancel"
              onClick={handleClose}
              className="px-4 py-2 text-sm text-muted-light hover:text-foreground transition-colors rounded-xl"
            >
              Cancel
            </button>
            <button
              type="submit"
              data-testid="project-form-submit"
              disabled={saving}
              className="px-5 py-2 text-sm font-bold bg-primary text-on-primary rounded-xl primary-glow hover:brightness-110 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving ? "Creating…" : "Create Project"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

