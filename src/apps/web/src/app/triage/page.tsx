export default function TriagePage() {
  return (
    <div data-testid="page-triage">
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
        Triage
      </h1>
      <p className="mt-2 text-zinc-600 dark:text-zinc-400">
        Incoming signals, proposed classifications, and items awaiting review.
      </p>
      <div
        data-testid="triage-empty-state"
        className="mt-8 rounded-lg border border-dashed border-zinc-300 p-8 text-center text-sm text-zinc-500 dark:border-zinc-700 dark:text-zinc-500"
      >
        No triage items yet. Signals will appear here once connectors are
        active.
      </div>
    </div>
  );
}

