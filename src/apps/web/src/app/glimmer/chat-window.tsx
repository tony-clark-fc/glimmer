/**
 * ChatWindow — conversational interface for the Glimmer persona page.
 *
 * REQ:GlimmerPersonaPage
 * REQ:PersonaPagePasteInIngestion
 *
 * Standard chatbot layout: messages scroll up, input at bottom.
 * User messages right-aligned, Glimmer messages left-aligned.
 * Input disabled in voice mode (user speaks instead of types).
 * Paste button toggles a multi-line paste area for content ingestion.
 */

"use client";

import { useRef, useEffect, useState } from "react";
import type { ChatMessage, InteractionMode } from "@/lib/types";

interface ChatWindowProps {
  messages: ChatMessage[];
  interactionMode: InteractionMode;
  isThinking: boolean;
  onSendMessage: (content: string) => void;
  onPasteIn?: (content: string, contentTypeHint: string) => void;
}

const CONTENT_TYPE_OPTIONS = [
  { value: "freeform", label: "Freeform" },
  { value: "email_snippet", label: "Email" },
  { value: "meeting_notes", label: "Meeting notes" },
  { value: "requirements_excerpt", label: "Requirements" },
];

export function ChatWindow({
  messages,
  interactionMode,
  isThinking,
  onSendMessage,
  onPasteIn,
}: ChatWindowProps) {
  const [input, setInput] = useState("");
  const [pasteMode, setPasteMode] = useState(false);
  const [pasteContent, setPasteContent] = useState("");
  const [pasteContentType, setPasteContentType] = useState("freeform");
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isThinking]);

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (!trimmed) return;
    onSendMessage(trimmed);
    setInput("");
  };

  const handlePasteSubmit = () => {
    const trimmed = pasteContent.trim();
    if (!trimmed || !onPasteIn) return;
    onPasteIn(trimmed, pasteContentType);
    setPasteContent("");
    setPasteMode(false);
    setPasteContentType("freeform");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const inputDisabled = interactionMode === "voice";

  return (
    <div
      className="flex flex-col h-full rounded-2xl overflow-hidden"
      style={{
        background: "linear-gradient(180deg, rgba(14,14,17,0.95), rgba(10,10,12,0.98))",
        border: "1px solid rgba(129, 140, 248, 0.08)",
      }}
      data-testid="chat-window"
    >
      {/* Messages area */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-4 py-4 space-y-3 min-h-0"
      >
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <p className="text-sm text-muted-light italic">
              Start a conversation with Glimmer…
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`chat-message-enter flex ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                msg.role === "user"
                  ? "bg-primary/15 text-foreground border border-primary/20"
                  : "bg-surface-container-low text-on-surface-variant border border-outline-variant/20"
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
              <span className="block mt-1 text-[10px] text-muted-light opacity-60">
                {new Date(msg.timestamp).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            </div>
          </div>
        ))}

        {/* Thinking indicator */}
        {isThinking && (
          <div className="flex justify-start chat-message-enter">
            <div className="bg-surface-container-low rounded-2xl px-4 py-3 border border-outline-variant/20">
              <div className="flex gap-1.5">
                <span className="h-2 w-2 rounded-full bg-primary/60 animate-bounce [animation-delay:0ms]" />
                <span className="h-2 w-2 rounded-full bg-primary/60 animate-bounce [animation-delay:150ms]" />
                <span className="h-2 w-2 rounded-full bg-primary/60 animate-bounce [animation-delay:300ms]" />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input area */}
      <div className="px-4 pb-4 pt-2 border-t border-outline-variant/10">
        {inputDisabled ? (
          <div className="flex items-center justify-center py-3 text-xs text-muted-light">
            <span className="inline-block h-2 w-2 rounded-full bg-emerald-500 mr-2 animate-pulse" />
            Voice mode active — speak to Glimmer
          </div>
        ) : pasteMode ? (
          /* ── Paste-in area ──────────────────────────────── */
          <div className="space-y-2" data-testid="paste-in-area">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-primary">📋 Paste content for analysis</span>
                <select
                  value={pasteContentType}
                  onChange={(e) => setPasteContentType(e.target.value)}
                  className="text-[10px] bg-surface-container-lowest border border-outline-variant/20 rounded px-1.5 py-0.5 text-muted-light"
                  data-testid="paste-in-type"
                >
                  {CONTENT_TYPE_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>
              <button
                onClick={() => { setPasteMode(false); setPasteContent(""); }}
                className="text-xs text-muted-light hover:text-foreground transition-colors"
              >
                Cancel
              </button>
            </div>
            <textarea
              value={pasteContent}
              onChange={(e) => setPasteContent(e.target.value)}
              placeholder="Paste email, meeting notes, requirements, or any content for Glimmer to analyze…"
              rows={4}
              className="w-full resize-none rounded-xl bg-surface-container-lowest border border-primary/20 px-4 py-2.5 text-sm text-foreground placeholder:text-muted-light/50 focus:outline-none focus:border-primary/40 focus:ring-1 focus:ring-primary/20 transition-all"
              data-testid="paste-in-input"
              autoFocus
            />
            <div className="flex justify-end">
              <button
                onClick={handlePasteSubmit}
                disabled={!pasteContent.trim() || isThinking}
                className="px-4 py-1.5 rounded-lg bg-primary/20 text-primary text-xs font-medium hover:bg-primary/30 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                data-testid="paste-in-submit"
              >
                Analyze Content
              </button>
            </div>
          </div>
        ) : (
          /* ── Normal chat input ──────────────────────────── */
          <div className="flex gap-2 items-end">
            {onPasteIn && (
              <button
                onClick={() => setPasteMode(true)}
                title="Paste content for analysis"
                className="shrink-0 h-10 w-10 rounded-xl bg-surface-container-low text-muted-light hover:text-primary hover:bg-primary/10 flex items-center justify-center transition-all border border-outline-variant/10"
                data-testid="paste-in-toggle"
              >
                <span className="text-base">📋</span>
              </button>
            )}
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                interactionMode === "whisper"
                  ? "Speak or type… (Glimmer responds silently)"
                  : "Message Glimmer…"
              }
              rows={1}
              className="flex-1 resize-none rounded-xl bg-surface-container-lowest border border-outline-variant/20 px-4 py-2.5 text-sm text-foreground placeholder:text-muted-light/50 focus:outline-none focus:border-primary/40 focus:ring-1 focus:ring-primary/20 transition-all"
              data-testid="chat-input"
            />
            <button
              onClick={handleSubmit}
              disabled={!input.trim()}
              className="shrink-0 h-10 w-10 rounded-xl bg-primary/20 text-primary hover:bg-primary/30 disabled:opacity-30 disabled:cursor-not-allowed flex items-center justify-center transition-all"
              data-testid="chat-send"
            >
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M22 2 11 13" />
                <path d="M22 2 15 22 11 13 2 9l20-7z" />
              </svg>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

