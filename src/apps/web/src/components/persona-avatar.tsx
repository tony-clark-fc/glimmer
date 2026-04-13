/**
 * PersonaAvatar — bounded persona rendering component.
 *
 * ARCH:VisualPersonaSelection
 * ARCH:VisualPersonaRenderingRules
 * REQ:VisualPersonaSupport
 * REQ:ContextAwareVisualPresentation
 *
 * Renders a Glimmer persona image for a given interaction context.
 * Falls back gracefully to a default visual if no asset is available.
 * Remains subordinate to operational content — small, supportive, never dominant.
 */

"use client";

import { useEffect, useState } from "react";
import { fetchPersona } from "@/lib/api-client";
import type { PersonaAsset } from "@/lib/types";

interface PersonaAvatarProps {
  /** Interaction context for persona selection (e.g. "today", "drafting", "triage") */
  context?: string;
  /** Size variant — persona is supportive, never dominant */
  size?: "sm" | "md";
  /** Additional CSS classes */
  className?: string;
}

/** Initials-based fallback when no persona asset is available at all. */
function FallbackAvatar({
  size,
  className,
}: {
  size: "sm" | "md";
  className?: string;
}) {
  const sizeClass = size === "sm" ? "h-8 w-8 text-xs" : "h-10 w-10 text-sm";
  return (
    <div
      data-testid="persona-fallback"
      className={`inline-flex items-center justify-center rounded-full bg-indigo-100 text-indigo-600 font-semibold dark:bg-indigo-900 dark:text-indigo-300 ${sizeClass} ${className ?? ""}`}
      role="img"
      aria-label="Glimmer assistant"
    >
      G
    </div>
  );
}

export function PersonaAvatar({
  context,
  size = "sm",
  className,
}: PersonaAvatarProps) {
  const [asset, setAsset] = useState<PersonaAsset | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [imgError, setImgError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetchPersona(context)
      .then((selection) => {
        if (!cancelled) {
          setAsset(selection.asset);
          setLoaded(true);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setLoaded(true);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [context]);

  // Not yet loaded — render nothing to avoid layout shift
  if (!loaded) {
    return null;
  }

  // No asset available or image failed — show initials fallback
  if (!asset || imgError) {
    return <FallbackAvatar size={size} className={className} />;
  }

  const sizeClass = size === "sm" ? "h-8 w-8" : "h-10 w-10";

  return (
    <img
      data-testid="persona-avatar"
      src={asset.asset_path}
      alt={`Glimmer — ${asset.label}`}
      className={`rounded-full object-cover ${sizeClass} ${className ?? ""}`}
      onError={() => setImgError(true)}
    />
  );
}

