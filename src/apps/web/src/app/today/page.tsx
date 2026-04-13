"use client";

import { useEffect, useState } from "react";
import { fetchLatestFocusPack, ApiError } from "@/lib/api-client";
import { PersonaAvatar } from "@/components/persona-avatar";
import type { FocusPack } from "@/lib/types";

type LoadState = "loading" | "loaded" | "empty" | "error";

export default function TodayPage() {
  const [focusPack, setFocusPack] = useState<FocusPack | null>(null);
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchLatestFocusPack()
      .then((fp) => {
        if (!cancelled) {
          setFocusPack(fp);
          setState("loaded");
        }
      })
      .catch((err) => {
        if (cancelled) return;
        if (err instanceof ApiError && err.status === 404) {
          setState("empty");
        } else {
          setError(err.message ?? "Failed to load focus pack");
          setState("error");
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div data-testid="page-today">
      <div className="flex items-center gap-3">
        <PersonaAvatar context="today" size="md" />
        <div>
          <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
            Today
          </h1>
          <p className="mt-1 text-zinc-600 dark:text-zinc-400">
            Your daily operating brief — priorities, deadlines, and what needs
            attention now.
          </p>
        </div>
      </div>

      {state === "loading" && (
        <div
          data-testid="today-loading"
          className="mt-8 text-sm text-zinc-500"
        >
          Loading focus pack…
        </div>
      )}

      {state === "error" && (
        <div
          data-testid="today-error"
          className="mt-8 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-300"
        >
          {error}
        </div>
      )}

      {state === "empty" && (
        <div
          data-testid="today-empty-state"
          className="mt-8 rounded-lg border border-dashed border-zinc-300 p-8 text-center text-sm text-zinc-500 dark:border-zinc-700 dark:text-zinc-500"
        >
          No priorities yet. Connect accounts and ingest signals to populate your
          daily brief.
        </div>
      )}

      {state === "loaded" && focusPack && (
        <div data-testid="today-focus-pack" className="mt-6 space-y-6">
          {/* Top actions */}
          <FocusSection
            testId="focus-top-actions"
            title="Top Actions"
            data={focusPack.top_actions}
            emptyText="No top actions right now."
          />

          {/* High risk items */}
          <FocusSection
            testId="focus-high-risk"
            title="High Risk Items"
            data={focusPack.high_risk_items}
            emptyText="No high-risk items flagged."
          />

          {/* Waiting on */}
          <FocusSection
            testId="focus-waiting-on"
            title="Waiting On"
            data={focusPack.waiting_on_items}
            emptyText="Nothing waiting on external responses."
          />

          {/* Reply debt */}
          {focusPack.reply_debt_summary && (
            <div data-testid="focus-reply-debt">
              <h2 className="text-lg font-medium text-zinc-800 dark:text-zinc-200">
                Reply Debt
              </h2>
              <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                {focusPack.reply_debt_summary}
              </p>
            </div>
          )}

          {/* Calendar pressure */}
          {focusPack.calendar_pressure_summary && (
            <div data-testid="focus-calendar-pressure">
              <h2 className="text-lg font-medium text-zinc-800 dark:text-zinc-200">
                Calendar Pressure
              </h2>
              <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
                {focusPack.calendar_pressure_summary}
              </p>
            </div>
          )}

          <p className="text-xs text-zinc-400">
            Generated{" "}
            {new Date(focusPack.generated_at).toLocaleString()}
          </p>
        </div>
      )}
    </div>
  );
}

// ── Focus section helper ────────────────────────────────────────

function FocusSection({
  testId,
  title,
  data,
  emptyText,
}: {
  testId: string;
  title: string;
  data: Record<string, unknown> | null;
  emptyText: string;
}) {
  const items = data
    ? Array.isArray(data) ? data : Object.entries(data)
    : null;

  return (
    <div data-testid={testId}>
      <h2 className="text-lg font-medium text-zinc-800 dark:text-zinc-200">
        {title}
      </h2>
      {!items || items.length === 0 ? (
        <p className="mt-1 text-sm text-zinc-500">{emptyText}</p>
      ) : (
        <ul className="mt-2 space-y-2">
          {(Array.isArray(data) ? data : Object.entries(data!)).map(
            (item: unknown, i: number) => (
              <li
                key={i}
                className="rounded-md border border-zinc-200 bg-white p-3 text-sm text-zinc-700 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300"
              >
                {typeof item === "string"
                  ? item
                  : Array.isArray(item)
                    ? `${item[0]}: ${JSON.stringify(item[1])}`
                    : JSON.stringify(item)}
              </li>
            ),
          )}
        </ul>
      )}
    </div>
  );
}
