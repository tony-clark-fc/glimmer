/**
 * ControlsGutter — right-side control panel for the Glimmer persona page.
 *
 * REQ:GlimmerPersonaPage
 *
 * Contains:
 * 1. Interaction mode selector (Voice / Whisper / Chat)
 * 2. Workspace mode selector (Idea / Plan / Report / Debrief / Update)
 * 3. Glimmer mood indicator
 */

"use client";

import type { InteractionMode, WorkspaceMode } from "@/lib/types";
import type { GlimmerMoodType } from "./glimmer-avatar";

interface ControlsGutterProps {
  interactionMode: InteractionMode;
  workspaceMode: WorkspaceMode;
  mood: GlimmerMoodType;
  moodReason: string;
  onInteractionModeChange: (mode: InteractionMode) => void;
  onWorkspaceModeChange: (mode: WorkspaceMode) => void;
}

const INTERACTION_MODES: { value: InteractionMode; label: string; icon: string; desc: string }[] = [
  { value: "voice", label: "Voice", icon: "🎙", desc: "You speak, Glimmer speaks" },
  { value: "whisper", label: "Whisper", icon: "👁", desc: "You speak, Glimmer types" },
  { value: "chat", label: "Chat", icon: "💬", desc: "Nobody speaks" },
];

const WORKSPACE_MODES: { value: WorkspaceMode; label: string; icon: string; desc: string }[] = [
  { value: "idea", label: "Idea", icon: "💡", desc: "New or update a project" },
  { value: "plan", label: "Plan", icon: "📋", desc: "Milestones and tasks" },
  { value: "report", label: "Report", icon: "📊", desc: "What Glimmer's been doing" },
  { value: "debrief", label: "Debrief", icon: "🗣", desc: "Tell Glimmer what you did" },
  { value: "update", label: "Update", icon: "📥", desc: "New inbox items & triage" },
];

const MOOD_EMOJI: Record<GlimmerMoodType, string> = {
  bau: "😊",
  happy: "😄",
  grumpy: "😤",
  thinking: "🤔",
  worried: "😟",
};

const MOOD_COLOR: Record<GlimmerMoodType, string> = {
  bau: "text-primary",
  happy: "text-emerald-400",
  grumpy: "text-error",
  thinking: "text-primary",
  worried: "text-tertiary",
};

export function ControlsGutter({
  interactionMode,
  workspaceMode,
  mood,
  moodReason,
  onInteractionModeChange,
  onWorkspaceModeChange,
}: ControlsGutterProps) {
  return (
    <div
      className="flex flex-col gap-6 h-full w-[180px] shrink-0"
      data-testid="controls-gutter"
    >
      {/* Mood indicator */}
      <div className="rounded-2xl bg-surface-container-lowest/60 border border-outline-variant/10 p-3">
        <div className="text-[10px] font-bold text-muted-light uppercase tracking-widest mb-2">
          Mood
        </div>
        <div className="flex items-center gap-2">
          <span className="text-lg">{MOOD_EMOJI[mood]}</span>
          <div>
            <span className={`text-xs font-bold capitalize ${MOOD_COLOR[mood]}`}>
              {mood === "bau" ? "Focused" : mood}
            </span>
            <p className="text-[10px] text-muted-light leading-tight mt-0.5">
              {moodReason}
            </p>
          </div>
        </div>
      </div>

      {/* Interaction mode */}
      <div className="rounded-2xl bg-surface-container-lowest/60 border border-outline-variant/10 p-3">
        <div className="text-[10px] font-bold text-muted-light uppercase tracking-widest mb-2">
          Interaction
        </div>
        <div className="space-y-1">
          {INTERACTION_MODES.map((m) => (
            <button
              key={m.value}
              onClick={() => onInteractionModeChange(m.value)}
              data-testid={`mode-${m.value}`}
              className={`w-full text-left rounded-xl px-3 py-2 text-xs transition-all ${
                interactionMode === m.value
                  ? "bg-primary/15 text-primary border border-primary/30 mode-active-pulse"
                  : "text-muted-light hover:text-foreground hover:bg-surface-container-high/50 border border-transparent"
              }`}
            >
              <span className="mr-1.5">{m.icon}</span>
              <span className="font-bold">{m.label}</span>
              <p className="text-[10px] opacity-60 mt-0.5 pl-5">{m.desc}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Workspace mode */}
      <div className="rounded-2xl bg-surface-container-lowest/60 border border-outline-variant/10 p-3 flex-1">
        <div className="text-[10px] font-bold text-muted-light uppercase tracking-widest mb-2">
          Mode
        </div>
        <div className="space-y-1">
          {WORKSPACE_MODES.map((m) => (
            <button
              key={m.value}
              onClick={() => onWorkspaceModeChange(m.value)}
              data-testid={`workspace-${m.value}`}
              className={`w-full text-left rounded-xl px-3 py-2 text-xs transition-all ${
                workspaceMode === m.value
                  ? "bg-primary/15 text-primary border border-primary/30"
                  : "text-muted-light hover:text-foreground hover:bg-surface-container-high/50 border border-transparent"
              }`}
            >
              <span className="mr-1.5">{m.icon}</span>
              <span className="font-bold">{m.label}</span>
              <p className="text-[10px] opacity-60 mt-0.5 pl-5">{m.desc}</p>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

