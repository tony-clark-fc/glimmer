export default function PortfolioPage() {
  return (
    <div data-testid="page-portfolio">
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
        Portfolio
      </h1>
      <p className="mt-2 text-zinc-600 dark:text-zinc-400">
        Compare active projects across urgency, health, and attention demand.
      </p>
      <div
        data-testid="portfolio-empty-state"
        className="mt-8 rounded-lg border border-dashed border-zinc-300 p-8 text-center text-sm text-zinc-500 dark:border-zinc-700 dark:text-zinc-500"
      >
        No projects yet. Create your first project to start building your
        portfolio view.
      </div>
    </div>
  );
}

