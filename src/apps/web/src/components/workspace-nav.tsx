"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/today", label: "Today" },
  { href: "/portfolio", label: "Portfolio" },
  { href: "/triage", label: "Triage" },
  { href: "/drafts", label: "Drafts" },
  { href: "/review", label: "Review" },
] as const;

export function WorkspaceNav() {
  const pathname = usePathname();

  return (
    <nav
      aria-label="Workspace navigation"
      className="flex items-center gap-1 px-4 py-2 border-b border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950"
    >
      <Link
        href="/today"
        className="mr-4 text-lg font-semibold tracking-tight text-zinc-900 dark:text-zinc-100"
        data-testid="nav-home"
      >
        Glimmer
      </Link>

      {NAV_ITEMS.map(({ href, label }) => {
        const isActive =
          pathname === href || pathname.startsWith(href + "/");

        return (
          <Link
            key={href}
            href={href}
            data-testid={`nav-${label.toLowerCase()}`}
            className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
              isActive
                ? "bg-zinc-100 text-zinc-900 dark:bg-zinc-800 dark:text-zinc-100"
                : "text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900 dark:text-zinc-400 dark:hover:bg-zinc-900 dark:hover:text-zinc-100"
            }`}
          >
            {label}
          </Link>
        );
      })}
    </nav>
  );
}

