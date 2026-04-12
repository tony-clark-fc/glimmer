interface ProjectPageProps {
  params: Promise<{ id: string }>;
}

export default async function ProjectPage({ params }: ProjectPageProps) {
  const { id } = await params;

  return (
    <div data-testid="page-project">
      <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-100">
        Project
      </h1>
      <p className="mt-2 text-zinc-600 dark:text-zinc-400">
        Workspace for project{" "}
        <span className="font-mono text-zinc-800 dark:text-zinc-200">
          {id}
        </span>{" "}
        — summary, milestones, stakeholders, and next actions.
      </p>
      <div
        data-testid="project-empty-state"
        className="mt-8 rounded-lg border border-dashed border-zinc-300 p-8 text-center text-sm text-zinc-500 dark:border-zinc-700 dark:text-zinc-500"
      >
        Project details will appear here once the domain model is populated.
      </div>
    </div>
  );
}

