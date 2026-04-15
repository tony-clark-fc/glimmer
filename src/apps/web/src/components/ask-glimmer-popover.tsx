/**
 * AskGlimmerPopover — shared contextual "Ask Glimmer" interaction component.
 *
 * PLAN:WorkstreamE.PackageE16.ContextualAskGlimmer
 * ARCH:ContextualAskGlimmerInteraction
 * REQ:ContextualAskGlimmer
 *
 * Provides a consistent sparkle ✦ affordance on data elements across all
 * workspace surfaces. Opens a compact popover with Glimmer avatar and
 * text input. Routes the question through the orchestration core with
 * element context. Respects review-gate discipline.
 */

"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { askGlimmerContextual } from "@/lib/api-client";
import type { AskGlimmerResponse } from "@/lib/types";

type PopoverState = "idle" | "open" | "loading" | "replied" | "error";

interface AskGlimmerPopoverProps {
  /** Element type (e.g. "project", "action_item", "risk", "draft", "classification") */
  elementType: string;
  /** Element identifier */
  elementId: string;
  /** Serialized element data for context */
  elementContext: Record<string, unknown>;
  /** Workspace surface name (e.g. "today", "portfolio", "triage") */
  surface: string;
  /** Optional className for the trigger button container */
  className?: string;
}

export function AskGlimmerPopover({
  elementType,
  elementId,
  elementContext,
  surface,
  className,
}: AskGlimmerPopoverProps) {
  const [state, setState] = useState<PopoverState>("idle");
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState<AskGlimmerResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const popoverRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Close on Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && state !== "idle") {
        handleClose();
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [state]);

  // Close on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        popoverRef.current &&
        !popoverRef.current.contains(e.target as Node) &&
        state !== "idle"
      ) {
        handleClose();
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [state]);

  // Focus input when popover opens
  useEffect(() => {
    if (state === "open") {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [state]);

  const handleClose = useCallback(() => {
    setState("idle");
    setQuestion("");
    setResponse(null);
    setError(null);
  }, []);

  const handleOpen = useCallback(() => {
    setState("open");
  }, []);

  const handleSubmit = useCallback(async () => {
    if (!question.trim()) return;

    setState("loading");
    setError(null);

    try {
      const result = await askGlimmerContextual({
        element_type: elementType,
        element_id: elementId,
        element_context: elementContext,
        surface,
        question: question.trim(),
      });
      setResponse(result);
      setState("replied");
    } catch (err) {
      setError("Couldn't get a response right now. Please try again.");
      setState("error");
    }
  }, [question, elementType, elementId, elementContext, surface]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit],
  );

  if (state === "idle") {
    return (
      <button
        data-testid="ask-glimmer-trigger"
        onClick={handleOpen}
        className={`inline-flex items-center justify-center h-6 w-6 rounded-full text-xs
          text-primary/60 hover:text-primary hover:bg-primary/10
          transition-all duration-200 ${className ?? ""}`}
        title="Ask Glimmer about this"
        aria-label={`Ask Glimmer about this ${elementType}`}
      >
        ✦
      </button>
    );
  }

  return (
    <div ref={popoverRef} className={`relative ${className ?? ""}`}>
      {/* Trigger (stays visible, highlighted) */}
      <button
        data-testid="ask-glimmer-trigger"
        onClick={handleClose}
        className="inline-flex items-center justify-center h-6 w-6 rounded-full text-xs
          text-primary bg-primary/15 transition-all duration-200"
        title="Close"
        aria-label="Close Ask Glimmer"
      >
        ✦
      </button>

      {/* Popover */}
      <div
        data-testid="ask-glimmer-popover"
        className="absolute right-0 top-8 z-50 w-80 rounded-2xl
          bg-surface-container-low border border-outline-variant/30
          shadow-xl shadow-black/40 backdrop-blur-md overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center gap-2 px-4 pt-3 pb-2">
          <span
            className="flex items-center justify-center h-6 w-6 rounded-full
              bg-primary/15 text-primary text-xs font-bold"
            aria-label="Glimmer avatar"
          >
            G
          </span>
          <span className="text-xs font-bold text-primary font-headline tracking-wide">
            Ask Glimmer
          </span>
          <button
            onClick={handleClose}
            className="ml-auto text-xs text-muted-light hover:text-foreground transition-colors"
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        {/* Input area */}
        {(state === "open" || state === "loading") && (
          <div className="px-4 pb-3">
            <div className="flex gap-2">
              <input
                ref={inputRef}
                data-testid="ask-glimmer-input"
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={`Ask about this ${elementType}…`}
                disabled={state === "loading"}
                className="flex-1 rounded-xl bg-surface-container-lowest border border-outline-variant/30
                  px-3 py-1.5 text-xs text-foreground placeholder:text-muted-light
                  focus:outline-none focus:ring-1 focus:ring-primary/40 disabled:opacity-50"
              />
              <button
                data-testid="ask-glimmer-submit"
                onClick={handleSubmit}
                disabled={!question.trim() || state === "loading"}
                className="rounded-xl bg-primary text-on-primary px-3 py-1.5 text-xs font-bold
                  transition-all duration-200 hover:brightness-110 disabled:opacity-40
                  active:scale-95"
              >
                {state === "loading" ? "…" : "Ask"}
              </button>
            </div>
          </div>
        )}

        {/* Response */}
        {state === "replied" && response && (
          <div className="px-4 pb-3 space-y-2">
            <div
              data-testid="ask-glimmer-reply"
              className="rounded-xl bg-surface-container-lowest p-3 text-xs text-foreground leading-relaxed
                max-h-40 overflow-y-auto ghost-border"
            >
              {response.reply}
            </div>
            {response.review_required && (
              <div
                data-testid="ask-glimmer-review-badge"
                className="flex items-center gap-1.5 rounded-full bg-tertiary-container/10
                  border border-tertiary/20 px-3 py-1 text-xs font-bold text-tertiary"
              >
                ⚠ Review required
                {response.review_reason && (
                  <span className="font-normal text-muted-light ml-1">
                    — {response.review_reason}
                  </span>
                )}
              </div>
            )}
            {/* Ask again */}
            <button
              onClick={() => {
                setQuestion("");
                setResponse(null);
                setState("open");
              }}
              className="text-xs text-primary hover:text-primary/80 transition-colors"
            >
              Ask another question
            </button>
          </div>
        )}

        {/* Error */}
        {state === "error" && (
          <div className="px-4 pb-3 space-y-2">
            <div
              data-testid="ask-glimmer-error"
              className="rounded-xl bg-error-container/10 border border-error/20 p-3 text-xs text-error"
            >
              {error}
            </div>
            <button
              onClick={() => setState("open")}
              className="text-xs text-primary hover:text-primary/80 transition-colors"
            >
              Try again
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

