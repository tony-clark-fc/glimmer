/**
 * MindMapCanvas — React Flow visualization for the persona page idea mode.
 *
 * ARCH:PersonaPage.MindMapArchitecture
 * ARCH:MindMapCandidateNodeModel
 * ARCH:MindMapCandidateEdgeModel
 * PLAN:WorkstreamE.PackageE13.PersonaPageMindMap
 * REQ:GlimmerPersonaPage
 *
 * Renders a dynamic, interactive mind-map that grows as the conversation
 * progresses. Supports:
 * - Semantic node types (project, stakeholder, milestone, etc.)
 * - Visual distinction between working/pending and confirmed/persisted nodes
 * - Zoom, pan, and minimap
 * - Click-to-select for inspection
 * - Automatic dagre layout with animated transitions
 * - Demo seed for initial rendering proof
 */

"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
  type OnSelectionChangeParams,
  BackgroundVariant,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import type { MindMapNodeData, MindMapEdgeData } from "@/lib/types";
import { mindMapNodeTypes } from "./mind-map-nodes";
import { applyDagreLayout } from "./mind-map-layout";

// ── Demo seed data ───────────────────────────────────────────────
// This provides an initial visual proof. In production, these nodes
// will be populated from conversation-extracted entities.

function createDemoNodes(): Node<MindMapNodeData>[] {
  return [
    {
      id: "project-1",
      type: "mindMapNode",
      position: { x: 0, y: 0 },
      data: {
        entityType: "project",
        label: "New Mobile App",
        subtitle: "Cross-platform launch by Q3",
        status: "pending",
        sourceOrigin: "conversation",
      },
    },
    {
      id: "stakeholder-1",
      type: "mindMapNode",
      position: { x: 0, y: 0 },
      data: {
        entityType: "stakeholder",
        label: "Sarah Chen",
        subtitle: "Product Lead",
        status: "pending",
        sourceOrigin: "conversation",
      },
    },
    {
      id: "milestone-1",
      type: "mindMapNode",
      position: { x: 0, y: 0 },
      data: {
        entityType: "milestone",
        label: "Beta Release",
        subtitle: "Target: June 15",
        status: "pending",
        sourceOrigin: "conversation",
      },
    },
    {
      id: "risk-1",
      type: "mindMapNode",
      position: { x: 0, y: 0 },
      data: {
        entityType: "risk",
        label: "API dependency on v3 release",
        status: "pending",
        sourceOrigin: "conversation",
      },
    },
    {
      id: "blocker-1",
      type: "mindMapNode",
      position: { x: 0, y: 0 },
      data: {
        entityType: "blocker",
        label: "Design system migration incomplete",
        status: "pending",
        sourceOrigin: "conversation",
      },
    },
    {
      id: "work-item-1",
      type: "mindMapNode",
      position: { x: 0, y: 0 },
      data: {
        entityType: "work_item",
        label: "Implement auth flow",
        subtitle: "Sprint 3",
        status: "pending",
        sourceOrigin: "conversation",
      },
    },
    {
      id: "decision-1",
      type: "mindMapNode",
      position: { x: 0, y: 0 },
      data: {
        entityType: "decision",
        label: "Use React Native over Flutter",
        status: "accepted",
        sourceOrigin: "existing",
      },
    },
    {
      id: "dependency-1",
      type: "mindMapNode",
      position: { x: 0, y: 0 },
      data: {
        entityType: "dependency",
        label: "Backend API v3",
        subtitle: "External team",
        status: "pending",
        sourceOrigin: "conversation",
      },
    },
  ];
}

function createDemoEdges(): Edge<MindMapEdgeData>[] {
  return [
    {
      id: "e-project-stakeholder",
      source: "project-1",
      target: "stakeholder-1",
      data: { relation: "involves" },
      animated: true,
      style: { stroke: "rgba(129, 140, 248, 0.4)", strokeWidth: 1.5 },
    },
    {
      id: "e-project-milestone",
      source: "project-1",
      target: "milestone-1",
      data: { relation: "owns" },
      animated: true,
      style: { stroke: "rgba(52, 211, 153, 0.4)", strokeWidth: 1.5 },
    },
    {
      id: "e-project-risk",
      source: "project-1",
      target: "risk-1",
      data: { relation: "linked_to" },
      style: { stroke: "rgba(255, 183, 131, 0.4)", strokeWidth: 1.5 },
    },
    {
      id: "e-project-blocker",
      source: "project-1",
      target: "blocker-1",
      data: { relation: "blocks" },
      style: { stroke: "rgba(255, 180, 171, 0.4)", strokeWidth: 1.5 },
    },
    {
      id: "e-milestone-work",
      source: "milestone-1",
      target: "work-item-1",
      data: { relation: "owns" },
      style: { stroke: "rgba(228, 225, 230, 0.3)", strokeWidth: 1 },
    },
    {
      id: "e-project-decision",
      source: "project-1",
      target: "decision-1",
      data: { relation: "linked_to" },
      style: { stroke: "rgba(129, 140, 248, 0.3)", strokeWidth: 1 },
    },
    {
      id: "e-risk-dependency",
      source: "risk-1",
      target: "dependency-1",
      data: { relation: "depends_on" },
      style: { stroke: "rgba(144, 143, 160, 0.3)", strokeWidth: 1 },
    },
  ];
}

// ── Selected node detail panel ───────────────────────────────────

function NodeDetailPanel({ node }: { node: Node<MindMapNodeData> | null }) {
  if (!node) return null;
  const data = node.data;

  return (
    <div
      className="absolute top-3 right-3 z-20 w-56 rounded-2xl bg-surface-container-lowest/90 border border-outline-variant/20 p-4 backdrop-blur-sm"
      data-testid="mindmap-detail-panel"
    >
      <div className="text-[9px] font-bold uppercase tracking-widest text-muted-light mb-1">
        {data.entityType.replace("_", " ")}
      </div>
      <h3 className="text-sm font-bold text-foreground">{data.label}</h3>
      {data.subtitle && (
        <p className="text-xs text-on-surface-variant mt-1">{data.subtitle}</p>
      )}
      <div className="flex items-center gap-2 mt-3">
        <span
          className={`text-[9px] px-1.5 py-0.5 rounded-full font-bold ${
            data.status === "pending"
              ? "bg-tertiary/20 text-tertiary"
              : data.status === "accepted"
                ? "bg-emerald-500/20 text-emerald-400"
                : "bg-error/20 text-error"
          }`}
        >
          {data.status.toUpperCase()}
        </span>
        <span className="text-[9px] text-muted-light">
          via {data.sourceOrigin.replace("_", " ")}
        </span>
      </div>
    </div>
  );
}

// ── Empty state ──────────────────────────────────────────────────

function EmptyMindMap() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center" data-testid="mindmap-empty">
      <div className="w-20 h-20 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center mb-4">
        <span className="text-2xl">🧠</span>
      </div>
      <p className="text-sm text-on-surface-variant max-w-sm">
        Describe your idea in the chat — Glimmer will extract concepts,
        stakeholders, and milestones into a visual mind-map here.
      </p>
      <p className="text-xs text-muted-light mt-2">
        The mind-map grows as you talk.
      </p>
    </div>
  );
}

// ── Main MindMapCanvas component ─────────────────────────────────

export interface MindMapCanvasProps {
  /** External nodes to render (from conversation extraction). */
  externalNodes?: Node<MindMapNodeData>[];
  /** External edges to render. */
  externalEdges?: Edge<MindMapEdgeData>[];
  /** Whether to show demo data when no external nodes are provided. */
  showDemo?: boolean;
}

export function MindMapCanvas({
  externalNodes,
  externalEdges,
  showDemo = true,
}: MindMapCanvasProps) {
  const [selectedNode, setSelectedNode] = useState<Node<MindMapNodeData> | null>(null);

  // Memoize demo data to avoid recreating on every render
  const demoNodes = useMemo(() => createDemoNodes(), []);
  const demoEdges = useMemo(() => createDemoEdges(), []);

  // Decide which nodes/edges to use (stable references via memo)
  const hasExternalData = externalNodes && externalNodes.length > 0;
  const rawNodes = useMemo(
    () => (hasExternalData ? externalNodes : showDemo ? demoNodes : []),
    [hasExternalData, externalNodes, showDemo, demoNodes],
  );
  const rawEdges = useMemo(
    () => (hasExternalData ? (externalEdges ?? []) : showDemo ? demoEdges : []),
    [hasExternalData, externalEdges, showDemo, demoEdges],
  );

  // Apply layout
  const layoutedNodes = useMemo(() => {
    if (rawNodes.length === 0) return [];
    return applyDagreLayout(rawNodes, rawEdges);
  }, [rawNodes, rawEdges]);

  const [nodes, setNodes, onNodesChange] = useNodesState(layoutedNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(rawEdges);

  // Sync when external data changes
  useEffect(() => {
    if (layoutedNodes.length > 0) {
      setNodes(layoutedNodes);
      setEdges(rawEdges);
    }
  }, [layoutedNodes, rawEdges, setNodes, setEdges]);

  const onSelectionChange = useCallback(
    ({ nodes: selected }: OnSelectionChangeParams) => {
      if (selected.length > 0) {
        setSelectedNode(selected[0] as Node<MindMapNodeData>);
      } else {
        setSelectedNode(null);
      }
    },
    [],
  );

  if (rawNodes.length === 0 && !showDemo) {
    return <EmptyMindMap />;
  }

  return (
    <div className="relative w-full h-full min-h-[300px]" data-testid="mindmap-canvas">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onSelectionChange={onSelectionChange}
        nodeTypes={mindMapNodeTypes}
        fitView
        fitViewOptions={{ padding: 0.3 }}
        minZoom={0.3}
        maxZoom={2}
        proOptions={{ hideAttribution: true }}
        className="mindmap-flow"
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={20}
          size={1}
          color="rgba(129, 140, 248, 0.06)"
        />
        <Controls
          position="bottom-left"
          showInteractive={false}
          className="!bg-surface-container-lowest/80 !border-outline-variant/20 !rounded-xl [&>button]:!bg-transparent [&>button]:!border-outline-variant/10 [&>button]:!text-muted-light [&>button:hover]:!text-primary"
        />
        <MiniMap
          position="bottom-right"
          nodeColor={(n) => {
            const data = n.data as MindMapNodeData;
            switch (data?.entityType) {
              case "project": return "#818cf8";
              case "stakeholder": return "#c0c1ff";
              case "milestone": return "#34d399";
              case "risk": return "#ffb783";
              case "blocker": return "#ffb4ab";
              case "work_item": return "#e4e1e6";
              case "decision": return "#818cf8";
              case "dependency": return "#908fa0";
              default: return "#353438";
            }
          }}
          maskColor="rgba(10, 10, 12, 0.7)"
          className="!bg-surface-container-lowest/80 !border-outline-variant/20 !rounded-xl"
        />
      </ReactFlow>

      {/* Detail panel for selected node */}
      <NodeDetailPanel node={selectedNode} />
    </div>
  );
}


