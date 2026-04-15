/**
 * MindMapNodes — custom React Flow node types for the persona page mind-map.
 *
 * ARCH:PersonaPage.MindMapArchitecture
 * ARCH:MindMapCandidateNodeModel
 * PLAN:WorkstreamE.PackageE13.PersonaPageMindMap
 *
 * Each entity type has distinct visual encoding:
 * - Color coding by entity type
 * - Dashed border for working (unconfirmed) state, solid for confirmed
 * - Icon per type
 * - Hover "Ask Glimmer" affordance
 */

"use client";

import { memo, useState } from "react";
import { Handle, Position } from "@xyflow/react";
import type { NodeProps, Node } from "@xyflow/react";
import type { MindMapNodeData, MindMapEntityType } from "@/lib/types";

// ── Visual config per entity type ────────────────────────────────

const ENTITY_CONFIG: Record<
  MindMapEntityType,
  { icon: string; color: string; bgColor: string; borderColor: string; glowColor: string }
> = {
  project: {
    icon: "📁",
    color: "text-primary",
    bgColor: "bg-primary/10",
    borderColor: "border-primary/40",
    glowColor: "rgba(129, 140, 248, 0.15)",
  },
  stakeholder: {
    icon: "👤",
    color: "text-secondary",
    bgColor: "bg-secondary/10",
    borderColor: "border-secondary/40",
    glowColor: "rgba(192, 193, 255, 0.15)",
  },
  milestone: {
    icon: "🏁",
    color: "text-emerald-400",
    bgColor: "bg-emerald-500/10",
    borderColor: "border-emerald-500/40",
    glowColor: "rgba(52, 211, 153, 0.15)",
  },
  risk: {
    icon: "⚠️",
    color: "text-tertiary",
    bgColor: "bg-tertiary/10",
    borderColor: "border-tertiary/40",
    glowColor: "rgba(255, 183, 131, 0.15)",
  },
  blocker: {
    icon: "🚫",
    color: "text-error",
    bgColor: "bg-error/10",
    borderColor: "border-error/40",
    glowColor: "rgba(255, 180, 171, 0.15)",
  },
  work_item: {
    icon: "📋",
    color: "text-foreground",
    bgColor: "bg-surface-container-high/60",
    borderColor: "border-outline-variant/40",
    glowColor: "rgba(228, 225, 230, 0.08)",
  },
  decision: {
    icon: "⚖️",
    color: "text-primary-fixed-dim",
    bgColor: "bg-primary/5",
    borderColor: "border-primary/30",
    glowColor: "rgba(129, 140, 248, 0.1)",
  },
  dependency: {
    icon: "🔗",
    color: "text-muted-light",
    bgColor: "bg-surface-container/60",
    borderColor: "border-outline-variant/30",
    glowColor: "rgba(144, 143, 160, 0.1)",
  },
};

// ── Type label for display ───────────────────────────────────────

const TYPE_LABELS: Record<MindMapEntityType, string> = {
  project: "Project",
  stakeholder: "Stakeholder",
  milestone: "Milestone",
  risk: "Risk",
  blocker: "Blocker",
  work_item: "Work Item",
  decision: "Decision",
  dependency: "Dependency",
};

// ── Base mind-map node ───────────────────────────────────────────

export type MindMapNode = Node<MindMapNodeData, "mindMapNode">;

function MindMapNodeComponent({ data, selected }: NodeProps<MindMapNode>) {
  const [hovered, setHovered] = useState(false);
  const config = ENTITY_CONFIG[data.entityType];
  const isWorking = data.status === "pending";
  const isDiscarded = data.status === "discarded";

  return (
    <div
      className={`
        relative rounded-2xl px-4 py-3 min-w-[160px] max-w-[240px]
        transition-all duration-200
        ${config.bgColor}
        ${isWorking ? "border-dashed" : "border-solid"}
        ${isDiscarded ? "opacity-40" : "opacity-100"}
        border-2 ${config.borderColor}
        ${selected ? "ring-2 ring-primary/50 scale-105" : ""}
      `}
      style={{
        boxShadow: hovered || selected
          ? `0 0 20px ${config.glowColor}, 0 4px 16px rgba(0,0,0,0.3)`
          : `0 2px 8px rgba(0,0,0,0.2)`,
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      data-testid={`mindmap-node-${data.entityType}`}
      data-node-status={data.status}
    >
      {/* Handles */}
      <Handle
        type="target"
        position={Position.Top}
        className="!bg-primary/60 !border-primary/30 !w-2 !h-2"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        className="!bg-primary/60 !border-primary/30 !w-2 !h-2"
      />

      {/* Header: icon + type label */}
      <div className="flex items-center gap-2 mb-1">
        <span className="text-sm">{config.icon}</span>
        <span className={`text-[9px] font-bold uppercase tracking-widest ${config.color}`}>
          {TYPE_LABELS[data.entityType]}
        </span>
        {isWorking && (
          <span className="text-[8px] px-1.5 py-0.5 rounded-full bg-tertiary/20 text-tertiary font-bold ml-auto">
            DRAFT
          </span>
        )}
      </div>

      {/* Label */}
      <p className="text-xs font-semibold text-foreground leading-tight line-clamp-2">
        {data.label}
      </p>

      {/* Subtitle / metadata */}
      {data.subtitle && (
        <p className="text-[10px] text-muted-light mt-1 leading-tight line-clamp-1">
          {data.subtitle}
        </p>
      )}

      {/* Hover: "Ask Glimmer" affordance */}
      {hovered && !isDiscarded && (
        <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 whitespace-nowrap z-50">
          <span className="text-[9px] px-2 py-0.5 rounded-full bg-primary/20 text-primary border border-primary/20 font-bold">
            💬 Ask Glimmer about this
          </span>
        </div>
      )}
    </div>
  );
}

export const MindMapNodeMemo = memo(MindMapNodeComponent);

// ── Node types map for React Flow ────────────────────────────────

export const mindMapNodeTypes = {
  mindMapNode: MindMapNodeMemo,
} as const;

