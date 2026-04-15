/**
 * Shared UI primitives for Glimmer workspace pages.
 *
 * "Luminous Workframe" design system — dark-first, tonal surfaces,
 * ghost borders, and glow effects. See DESIGN.md.
 */

import type { ReactNode } from "react";

// ── Page Header ─────────────────────────────────────────────────

export function PageHeader({
  title,
  description,
  children,
  testId,
}: {
  title: string;
  description: string;
  children?: ReactNode;
  testId?: string;
}) {
  return (
    <div data-testid={testId} className="mb-10">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-foreground font-headline">
            {title}
          </h1>
          <p className="mt-2 text-sm text-on-surface-variant leading-relaxed max-w-2xl">
            {description}
          </p>
        </div>
        {children && <div className="flex items-center gap-2 shrink-0">{children}</div>}
      </div>
    </div>
  );
}

// ── Section Card ────────────────────────────────────────────────

export function SectionCard({
  title,
  count,
  children,
  testId,
  variant = "default",
}: {
  title: string;
  count?: number;
  children: ReactNode;
  testId?: string;
  variant?: "default" | "accent" | "warning" | "danger";
}) {
  const accentBar = {
    default: "via-primary/15",
    accent: "via-primary/30",
    warning: "via-tertiary/25",
    danger: "via-error/25",
  }[variant];

  return (
    <section
      data-testid={testId}
      className="luminous-card rounded-2xl overflow-hidden"
    >
      {/* Gradient accent bar at top — replaces solid border per No-Line Rule */}
      <div className={`h-px bg-gradient-to-r from-transparent ${accentBar} to-transparent`} />
      <div className="px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-[2px] w-5 bg-primary shadow-[0_0_8px_rgba(129,140,248,0.4)]" />
          <h2 className="text-xs font-bold text-primary tracking-[0.15em] uppercase font-headline">
            {title}
          </h2>
        </div>
        {count !== undefined && (
          <span className="text-xs font-bold text-muted-light bg-surface-container-highest/40 rounded-full px-2.5 py-0.5">
            {count}
          </span>
        )}
      </div>
      <div className="px-6 pb-6">{children}</div>
    </section>
  );
}

// ── Info Banner ─────────────────────────────────────────────────

export function InfoBanner({
  children,
  variant = "info",
  testId,
}: {
  children: ReactNode;
  variant?: "info" | "warning" | "success" | "accent";
  testId?: string;
}) {
  const styles = {
    info: "glass-effect text-on-surface-variant",
    warning: "bg-tertiary-container/10 border border-tertiary/20 text-tertiary",
    success: "bg-emerald-500/10 border border-emerald-500/20 text-emerald-400",
    accent: "bg-primary/5 border-l-4 border-primary text-indigo-100/80 backdrop-blur-sm",
  }[variant];

  return (
    <div
      data-testid={testId}
      className={`flex items-center gap-3 rounded-2xl px-5 py-3 text-sm font-medium ${styles}`}
    >
      {children}
    </div>
  );
}

// ── Empty State ─────────────────────────────────────────────────

export function EmptyState({
  icon,
  message,
  testId,
}: {
  icon?: string;
  message: string;
  testId?: string;
}) {
  return (
    <div
      data-testid={testId}
      className="flex flex-col items-center justify-center rounded-2xl bg-surface-container-lowest py-20 px-8 text-center ghost-border"
    >
      {icon && <span className="text-3xl mb-4 opacity-30">{icon}</span>}
      <p className="text-sm text-muted-light max-w-md leading-relaxed">{message}</p>
    </div>
  );
}

// ── Loading Skeleton ────────────────────────────────────────────

export function LoadingSkeleton({
  lines = 3,
  testId,
}: {
  lines?: number;
  testId?: string;
}) {
  return (
    <div data-testid={testId} className="space-y-3">
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="skeleton h-4"
          style={{ width: `${85 - i * 15}%` }}
        />
      ))}
    </div>
  );
}

export function CardSkeleton({ count = 3, testId }: { count?: number; testId?: string }) {
  return (
    <div data-testid={testId} className="space-y-4">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="rounded-2xl bg-surface-container-low p-6 space-y-3 ghost-border">
          <div className="skeleton h-4 w-2/3" />
          <div className="skeleton h-3 w-full" />
          <div className="skeleton h-3 w-4/5" />
        </div>
      ))}
    </div>
  );
}

// ── Error State ─────────────────────────────────────────────────

export function ErrorState({
  message,
  testId,
}: {
  message: string;
  testId?: string;
}) {
  return (
    <div
      data-testid={testId}
      className="rounded-2xl bg-error-container/10 border border-error/20 p-5 text-sm text-error"
    >
      <div className="flex items-center gap-2">
        <span className="text-error" aria-hidden="true">⚠</span>
        {message}
      </div>
    </div>
  );
}

// ── Badge ───────────────────────────────────────────────────────

export function Badge({
  children,
  variant = "neutral",
  testId,
}: {
  children: ReactNode;
  variant?: "neutral" | "success" | "warning" | "danger" | "info" | "accent";
  testId?: string;
}) {
  const styles = {
    neutral: "bg-surface-container-highest/40 text-muted-light border border-outline-variant/30",
    success: "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30",
    warning: "bg-tertiary-container/10 text-tertiary border border-tertiary/20",
    danger: "bg-red-500/10 text-error border border-error/30",
    info: "bg-primary/10 text-primary border border-primary/30",
    accent: "bg-secondary-container/30 text-secondary border border-secondary/20",
  }[variant];

  return (
    <span
      data-testid={testId}
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-bold tracking-wide ${styles}`}
    >
      {children}
    </span>
  );
}

// ── Action Button ───────────────────────────────────────────────

export function ActionButton({
  children,
  variant = "primary",
  size = "sm",
  onClick,
  testId,
}: {
  children: ReactNode;
  variant?: "primary" | "success" | "danger" | "ghost";
  size?: "sm" | "md";
  onClick?: () => void;
  testId?: string;
}) {
  const base = "inline-flex items-center justify-center font-bold rounded-2xl transition-all duration-200 active:scale-95";

  const sizeClass = size === "sm" ? "px-4 py-1.5 text-xs" : "px-5 py-2.5 text-sm";

  const styles = {
    primary: "bg-primary text-on-primary primary-glow hover:brightness-110",
    success: "bg-primary/20 text-primary border border-primary/30 rounded-full hover:bg-primary/30",
    danger: "text-on-surface-variant border border-outline-variant/30 rounded-full hover:bg-white/5",
    ghost: "text-primary hover:bg-surface-container-high hover:text-accent-text",
  }[variant];

  return (
    <button
      data-testid={testId}
      onClick={onClick}
      className={`${base} ${sizeClass} ${styles}`}
    >
      {children}
    </button>
  );
}

// ── Item Card (for lists) ───────────────────────────────────────

export function ItemCard({
  children,
  testId,
  onClick,
  hoverable = false,
}: {
  children: ReactNode;
  testId?: string;
  onClick?: () => void;
  hoverable?: boolean;
}) {
  const Component = onClick ? "button" : "div";
  return (
    <Component
      data-testid={testId}
      onClick={onClick}
      className={`w-full text-left luminous-card rounded-2xl p-5 ${
        hoverable || onClick
          ? "cursor-pointer"
          : ""
      }`}
    >
      {children}
    </Component>
  );
}
