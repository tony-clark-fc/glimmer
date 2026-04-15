/**
 * Glimmer Persona Page — the primary interactive workspace.
 *
 * REQ:GlimmerPersonaPage
 * REQ:VisualPersonaSupport
 * REQ:VisualPersonaAssetManagement
 *
 * Layout (fills viewport below nav):
 * ┌──────────────────────────────────────────────────┐
 * │  Avatar  │   Chat Window          │  Controls    │  ← top section
 * │  (mood)  │   (conversation)       │  (gutter)    │
 * ├──────────┴────────────────────────┴──────────────┤
 * │              Workspace Canvas                     │  ← bottom section
 * │    (mind-map / portfolio cards / mode content)    │
 * └──────────────────────────────────────────────────┘
 *
 * Background: obsidian color cycle with soft glow orbs.
 * Avatar: mood-based, fades to "thinking" on user input.
 */

"use client";

import { useCallback, useEffect, useState } from "react";
import { fetchGlimmerMood } from "@/lib/api-client";
import type {
  ChatMessage,
  InteractionMode,
  WorkspaceMode,
  GlimmerMood,
} from "@/lib/types";

import { GlimmerAvatar } from "./glimmer-avatar";
import type { GlimmerMoodType } from "./glimmer-avatar";
import { ChatWindow } from "./chat-window";
import { ControlsGutter } from "./controls-gutter";
import { WorkspaceCanvas } from "./workspace-canvas";

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export default function GlimmerPage() {
  // ── State ─────────────────────────────────────────────────────
  const [mood, setMood] = useState<GlimmerMoodType>("bau");
  const [moodReason, setMoodReason] = useState("Loading…");
  const [interactionMode, setInteractionMode] = useState<InteractionMode>("chat");
  const [workspaceMode, setWorkspaceMode] = useState<WorkspaceMode>("update");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isThinking, setIsThinking] = useState(false);

  // ── Load mood on mount ────────────────────────────────────────
  useEffect(() => {
    fetchGlimmerMood()
      .then((data: GlimmerMood) => {
        setMood(data.mood);
        setMoodReason(data.reason);
      })
      .catch(() => {
        setMood("bau");
        setMoodReason("Could not determine mood — business as usual");
      });
  }, []);

  // ── Welcome message on mount ──────────────────────────────────
  useEffect(() => {
    const welcomeTimer = setTimeout(() => {
      setMessages([
        {
          id: generateId(),
          role: "glimmer",
          content:
            "Hi! I'm Glimmer, your project chief-of-staff. What would you like to work on? You can switch modes in the controls panel, or just tell me what you need.",
          timestamp: new Date().toISOString(),
          mode: workspaceMode,
        },
      ]);
    }, 800);
    return () => clearTimeout(welcomeTimer);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Handle user sending a message ─────────────────────────────
  const handleSendMessage = useCallback(
    (content: string) => {
      // Check for mode-switch commands
      const lower = content.toLowerCase().trim();
      const modeMap: Record<string, WorkspaceMode> = {
        "idea mode": "idea",
        "plan mode": "plan",
        "report mode": "report",
        "debrief mode": "debrief",
        "update mode": "update",
        "switch to idea": "idea",
        "switch to plan": "plan",
        "switch to report": "report",
        "switch to debrief": "debrief",
        "switch to update": "update",
      };

      for (const [trigger, mode] of Object.entries(modeMap)) {
        if (lower.includes(trigger)) {
          setWorkspaceMode(mode);
        }
      }

      // Add user message
      const userMsg: ChatMessage = {
        id: generateId(),
        role: "user",
        content,
        timestamp: new Date().toISOString(),
        mode: workspaceMode,
      };
      setMessages((prev) => [...prev, userMsg]);

      // Simulate thinking
      setIsThinking(true);

      // Simulate Glimmer response (placeholder — will be wired to LLM)
      const responseTimer = setTimeout(() => {
        setIsThinking(false);
        const glimmerMsg: ChatMessage = {
          id: generateId(),
          role: "glimmer",
          content: getPlaceholderResponse(content, workspaceMode),
          timestamp: new Date().toISOString(),
          mode: workspaceMode,
        };
        setMessages((prev) => [...prev, glimmerMsg]);
      }, 1500 + Math.random() * 1000);

      return () => clearTimeout(responseTimer);
    },
    [workspaceMode],
  );

  // ── Render ────────────────────────────────────────────────────
  return (
    <div
      className="fixed inset-0 top-14 z-20 obsidian-bg flex flex-col overflow-hidden"
      data-testid="page-glimmer"
    >
      {/* ── Top section: Avatar + Chat + Controls ─────────────── */}
      <div className="relative z-10 flex gap-4 p-4 h-[55%] min-h-[320px]">
        {/* Left: Avatar */}
        <div className="flex flex-col items-center justify-center w-[220px] shrink-0">
          <GlimmerAvatar mood={mood} isThinking={isThinking} />
          <div className="mt-3 text-center">
            <span className="text-xs font-bold text-primary font-headline tracking-wide">
              Glimmer
            </span>
            <p className="text-[10px] text-muted-light mt-0.5 capitalize">
              {workspaceMode} mode
            </p>
          </div>
        </div>

        {/* Center: Chat window */}
        <div className="flex-1 min-w-0">
          <ChatWindow
            messages={messages}
            interactionMode={interactionMode}
            isThinking={isThinking}
            onSendMessage={handleSendMessage}
          />
        </div>

        {/* Right: Controls gutter */}
        <ControlsGutter
          interactionMode={interactionMode}
          workspaceMode={workspaceMode}
          mood={mood}
          moodReason={moodReason}
          onInteractionModeChange={setInteractionMode}
          onWorkspaceModeChange={setWorkspaceMode}
        />
      </div>

      {/* ── Bottom section: Workspace canvas ──────────────────── */}
      <div className="relative z-10 flex-1 min-h-0 px-4 pb-4">
        <WorkspaceCanvas mode={workspaceMode} />
      </div>
    </div>
  );
}

// ── Placeholder response generator ──────────────────────────────
// Temporary — will be replaced with real LLM inference calls.

function getPlaceholderResponse(input: string, mode: WorkspaceMode): string {
  const lower = input.toLowerCase();

  if (lower.includes("new project") || lower.includes("start a project")) {
    return "Great! Let's set up a new project. What would you like to call it? I'll need a name, a brief objective, and any key stakeholders you have in mind.";
  }

  if (lower.includes("what's new") || lower.includes("what happened")) {
    return "Let me check your inbox… I'll pull up any new messages, calendar events, and items that need your attention. Switch to Update mode to see the full list.";
  }

  if (lower.includes("how am i doing") || lower.includes("status")) {
    return "Based on your portfolio: you have active projects in progress, with a few items that could use attention. Would you like me to walk through each project, or focus on the ones with blockers?";
  }

  switch (mode) {
    case "idea":
      return "I'm in Idea mode. Tell me about your concept — I'll start building a mind-map with the key elements as we talk.";
    case "plan":
      return "I'm in Plan mode. Which project would you like to discuss? I can show you milestones, upcoming tasks, and timeline pressure.";
    case "report":
      return "I'm in Report mode. Since your last session, I've been monitoring your connected accounts. Would you like the full activity summary or just the highlights?";
    case "debrief":
      return "I'm in Debrief mode. Tell me about what you've been working on, and I'll update the relevant project records and extract any action items.";
    case "update":
      return "I'm in Update mode. I'll check for any unclassified inbox items that need your attention. Give me a moment…";
    default:
      return "I'm here to help. What would you like to work on?";
  }
}

