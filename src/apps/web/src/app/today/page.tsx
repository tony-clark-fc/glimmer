export default function TodayPage() {
  return (
    <div data-testid="page-today">
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
        Today
      </h1>
      <p className="mt-2 text-zinc-600 dark:text-zinc-400">
        Your daily operating brief — priorities, deadlines, and what needs
        attention now.
      </p>
      <div
        data-testid="today-empty-state"
        className="mt-8 rounded-lg border border-dashed border-zinc-300 p-8 text-center text-sm text-zinc-500 dark:border-zinc-700 dark:text-zinc-500"
      >
        No priorities yet. Connect accounts and ingest signals to populate your
        daily brief.
      </div>
    </div>
  );
}

