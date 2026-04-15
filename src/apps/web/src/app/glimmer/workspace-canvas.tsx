/**
 * WorkspaceCanvas — bottom section of the Glimmer persona page.
 *
 * REQ:GlimmerPersonaPage
 *
 * Fills the remaining viewport below the top conversation area.
 * Content adapts to the active workspace mode:
 * - Idea: Mind-map canvas for project creation/editing
 * - Plan: Project work items, milestones, tasks
 * - Report: What Glimmer has been doing (activity log)
 * - Debrief: Structured input for what the operator has been doing
 * - Update: New inbox items and triage queue
 */

"use client";

import { useEffect, useState } from "react";
import type { WorkspaceMode } from "@/lib/types";
import type { ProjectSummary } from "@/lib/types";
import { fetchProjects } from "@/lib/api-client";

interface WorkspaceCanvasProps {
  mode: WorkspaceMode;
}

const MODE_HEADERS: Record<WorkspaceMode, { title: string; desc: string; icon: string }> = {
  idea: { title: "Idea Workshop", desc: "Create or refine a project — Glimmer will build a mind-map as you talk", icon: "💡" },
  plan: { title: "Plan View", desc: "Discuss milestones, tasks, and timelines for your active projects", icon: "📋" },
  report: { title: "Activity Report", desc: "Glimmer tells you what happened while you were away", icon: "📊" },
  debrief: { title: "Debrief", desc: "Tell Glimmer what you've been doing — she'll update the portfolio", icon: "🗣" },
  update: { title: "Inbox Update", desc: "New items that need attention, triage, or assignment", icon: "📥" },
};

export function WorkspaceCanvas({ mode }: WorkspaceCanvasProps) {
  const header = MODE_HEADERS[mode];

  return (
    <div
      className="flex-1 min-h-0 rounded-t-2xl overflow-hidden relative z-10"
      style={{
        background: "linear-gradient(180deg, rgba(14,14,17,0.6), rgba(10,10,12,0.8))",
        borderTop: "1px solid rgba(129, 140, 248, 0.06)",
      }}
      data-testid="workspace-canvas"
      data-mode={mode}
    >
      {/* Mode header bar */}
      <div className="flex items-center gap-3 px-6 py-3 border-b border-outline-variant/10">
        <span className="text-lg">{header.icon}</span>
        <div>
          <h2 className="text-xs font-bold text-primary tracking-widest uppercase font-headline">
            {header.title}
          </h2>
          <p className="text-[10px] text-muted-light">{header.desc}</p>
        </div>
      </div>

      {/* Canvas content */}
      <div className="h-full overflow-y-auto p-6">
        {mode === "idea" && <IdeaCanvas />}
        {mode === "plan" && <PlanCanvas />}
        {mode === "report" && <ReportCanvas />}
        {mode === "debrief" && <DebriefCanvas />}
        {mode === "update" && <UpdateCanvas />}
      </div>
    </div>
  );
}

// ── Mode-specific canvases ──────────────────────────────────────

function IdeaCanvas() {
  return (
    <div className="flex flex-col items-center justify-center h-64 text-center">
      <div className="w-24 h-24 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center mb-4">
        <span className="text-3xl">💡</span>
      </div>
      <p className="text-sm text-on-surface-variant max-w-md">
        Describe your idea in the chat — Glimmer will extract concepts, stakeholders,
        and milestones into a visual mind-map here.
      </p>
      <p className="text-xs text-muted-light mt-2">
        Say things like &ldquo;I want to start a new project for…&rdquo; or
        &ldquo;Let&apos;s update the scope on…&rdquo;
      </p>
    </div>
  );
}

function PlanCanvas() {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);

  useEffect(() => {
    fetchProjects().then(setProjects).catch(() => {});
  }, []);

  return (
    <div>
      {projects.length === 0 ? (
        <p className="text-sm text-muted-light">No active projects yet. Switch to Idea mode to create one.</p>
      ) : (
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
          {projects.map((p) => (
            <div
              key={p.id}
              className="luminous-card rounded-2xl p-4 cursor-pointer"
            >
              <h3 className="text-sm font-bold text-foreground">{p.name}</h3>
              {p.objective && (
                <p className="text-xs text-on-surface-variant mt-1 line-clamp-2">{p.objective}</p>
              )}
              <div className="flex gap-3 mt-3 text-[10px] text-muted-light">
                <span>{p.open_items} items</span>
                {p.active_blockers > 0 && (
                  <span className="text-error">{p.active_blockers} blockers</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ReportCanvas() {
  return (
    <div className="flex flex-col items-center justify-center h-64 text-center">
      <div className="w-24 h-24 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center mb-4">
        <span className="text-3xl">📊</span>
      </div>
      <p className="text-sm text-on-surface-variant max-w-md">
        Ask Glimmer &ldquo;What&apos;s happened since I was last here?&rdquo; and
        she&apos;ll summarize new messages, classifications, and extractions.
      </p>
    </div>
  );
}

function DebriefCanvas() {
  return (
    <div className="flex flex-col items-center justify-center h-64 text-center">
      <div className="w-24 h-24 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center mb-4">
        <span className="text-3xl">🗣</span>
      </div>
      <p className="text-sm text-on-surface-variant max-w-md">
        Tell Glimmer about your day — meetings, decisions, progress.
        She&apos;ll update project records and extract action items.
      </p>
    </div>
  );
}

function UpdateCanvas() {
  return (
    <div className="flex flex-col items-center justify-center h-64 text-center">
      <div className="w-24 h-24 rounded-full bg-tertiary/10 border border-tertiary/20 flex items-center justify-center mb-4">
        <span className="text-3xl">📥</span>
      </div>
      <p className="text-sm text-on-surface-variant max-w-md">
        Glimmer will show you new inbox items that need triage,
        items she couldn&apos;t classify, and suggested assignments.
      </p>
    </div>
  );
}

