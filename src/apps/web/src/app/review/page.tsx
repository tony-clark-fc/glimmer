export default function ReviewPage() {
  return (
    <div data-testid="page-review">
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
        Review
      </h1>
      <p className="mt-2 text-zinc-600 dark:text-zinc-400">
        Items requiring your judgment — ambiguous classifications, memory
        updates, and approval-gated actions.
      </p>
      <div
        data-testid="review-empty-state"
        className="mt-8 rounded-lg border border-dashed border-zinc-300 p-8 text-center text-sm text-zinc-500 dark:border-zinc-700 dark:text-zinc-500"
      >
        Nothing to review right now. Review items will appear when the
        assistant encounters ambiguity or proposes meaningful changes.
      </div>
    </div>
  );
}

