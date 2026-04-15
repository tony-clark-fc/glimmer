"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Sun,
  LayoutGrid,
  Zap,
  PenLine,
  Search,
  CheckCircle,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

const NAV_ITEMS: { href: string; label: string; icon: LucideIcon }[] = [
  { href: "/today", label: "Today", icon: Sun },
  { href: "/portfolio", label: "Portfolio", icon: LayoutGrid },
  { href: "/triage", label: "Triage", icon: Zap },
  { href: "/drafts", label: "Drafts", icon: PenLine },
  { href: "/research", label: "Research", icon: Search },
  { href: "/review", label: "Review", icon: CheckCircle },
];

export function WorkspaceNav() {
  const pathname = usePathname();

  return (
    <nav
      aria-label="Workspace navigation"
      className="sticky top-0 z-50 h-14 bg-[#0a0a0c]/80 backdrop-blur-2xl border-b border-outline-variant/20"
    >
      <div className="max-w-[960px] mx-auto px-6 md:px-0">
        <div className="flex items-center h-14 gap-1">
          {/* Glimmer logo mark */}
          <div className="flex items-center gap-2.5 mr-8">
            <span
              className="flex items-center justify-center h-8 w-8 rounded-lg bg-indigo-500 text-white text-sm font-black shadow-[0_0_15px_rgba(129,140,248,0.3)]"
              aria-hidden="true"
            >
              G
            </span>
            <Link
              href="/today"
              className="text-lg font-extrabold tracking-tight text-primary font-headline hover:text-accent-text transition-colors"
              data-testid="nav-home"
            >
              Glimmer
            </Link>
          </div>

          {/* Nav items */}
          <div className="flex items-center gap-0.5">
            {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
              const isActive =
                pathname === href || pathname.startsWith(href + "/");

              return (
                <Link
                  key={href}
                  href={href}
                  data-testid={`nav-${label.toLowerCase()}`}
                  className={`relative flex items-center gap-2 rounded-full px-4 py-1.5 text-xs font-medium tracking-wide transition-all duration-200 ${
                    isActive
                      ? "bg-primary/10 text-primary after:absolute after:bottom-[-9px] after:left-0 after:w-full after:h-[2px] after:bg-primary"
                      : "text-muted-light hover:text-primary hover:bg-surface-container-high/50"
                  }`}
                >
                  <Icon size={16} strokeWidth={isActive ? 2.25 : 1.75} />
                  <span className="hidden sm:inline">{label}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}
