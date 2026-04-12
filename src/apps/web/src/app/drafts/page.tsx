export default function DraftsPage() {
  return (
    <div data-testid="page-drafts">
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
        Drafts
      </h1>
      <p className="mt-2 text-zinc-600 dark:text-zinc-400">
        Review and refine communication drafts — context, variants, and
        copy-ready output.
      </p>
      <div
        data-testid="drafts-empty-state"
        className="mt-8 rounded-lg border border-dashed border-zinc-300 p-8 text-center text-sm text-zinc-500 dark:border-zinc-700 dark:text-zinc-500"
      >
        No drafts yet. Drafts are generated from triage and planner
        workflows.
      </div>
    </div>
  );
}

