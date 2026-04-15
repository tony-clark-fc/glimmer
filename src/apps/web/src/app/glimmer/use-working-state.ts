/**
 * useWorkingState — React hook for managing mind-map working state.
 *
 * ARCH:MindMapWorkingStateModel
 * ARCH:PersonaPage.StagedPersistence
 * ARCH:StateOwnershipBoundaries
 * PLAN:WorkstreamE.PackageE14.PersonaPageStagedPersistence
 * REQ:PersonaPageStagedPersistence
 *
 * Manages the client-side candidate nodes and edges with:
 * - Add/update/discard/accept operations on individual nodes
 * - Auto-save to backend on meaningful changes
 * - Confirm & Save batch commit
 * - Discard without persistence
 * - Session restore from backend backup
 *
 * Nothing enters the operational database until the operator
 * explicitly confirms via confirmAll().
 */

"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { Node, Edge } from "@xyflow/react";
import type {
  MindMapNodeData,
  MindMapEdgeData,
  MindMapEntityType,
  MindMapSourceOrigin,
  MindMapEdgeRelation,
  CandidateNodePayload,
  CandidateEdgePayload,
  PasteInCandidateNode,
} from "@/lib/types";
import {
  saveWorkingState,
  fetchWorkingState,
  confirmWorkingState,
  discardWorkingState,
} from "@/lib/api-client";

// ── Node/Edge creation helpers ──────────────────────────────────

function generateNodeId(): string {
  return `node-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`;
}

function generateEdgeId(source: string, target: string): string {
  return `e-${source}-${target}`;
}

// ── Convert between React Flow format and API format ────────────

function nodeToPayload(node: Node<MindMapNodeData>): CandidateNodePayload {
  const data = node.data;
  return {
    node_id: node.id,
    entity_type: data.entityType,
    label: data.label,
    subtitle: data.subtitle,
    status:
      data.status === "accepted"
        ? "accepted_by_operator"
        : data.status === "discarded"
          ? "discarded_by_operator"
          : "pending",
    source_origin: data.sourceOrigin,
    metadata: data.metadata as Record<string, unknown> | undefined,
    position_x: node.position?.x,
    position_y: node.position?.y,
  };
}

function payloadToNode(payload: CandidateNodePayload): Node<MindMapNodeData> {
  return {
    id: payload.node_id,
    type: "mindMapNode",
    position: {
      x: payload.position_x ?? 0,
      y: payload.position_y ?? 0,
    },
    data: {
      entityType: payload.entity_type as MindMapEntityType,
      label: payload.label,
      subtitle: payload.subtitle,
      status:
        payload.status === "accepted_by_operator"
          ? "accepted"
          : payload.status === "discarded_by_operator"
            ? "discarded"
            : "pending",
      sourceOrigin: (payload.source_origin || "conversation") as MindMapSourceOrigin,
      metadata: payload.metadata,
    },
  };
}

function edgeToPayload(edge: Edge<MindMapEdgeData>): CandidateEdgePayload {
  return {
    edge_id: edge.id,
    source_node_id: edge.source,
    target_node_id: edge.target,
    relation: (edge.data?.relation || "linked_to") as MindMapEdgeRelation,
    label: edge.data?.label,
  };
}

function payloadToEdge(payload: CandidateEdgePayload): Edge<MindMapEdgeData> {
  return {
    id: payload.edge_id,
    source: payload.source_node_id,
    target: payload.target_node_id,
    data: {
      relation: payload.relation as MindMapEdgeRelation,
      label: payload.label,
    },
    animated: true,
    style: { stroke: "rgba(129, 140, 248, 0.4)", strokeWidth: 1.5 },
  };
}

// ── Hook state and return types ─────────────────────────────────

export interface WorkingStateActions {
  /** Add a new candidate node */
  addNode: (
    entityType: MindMapEntityType,
    label: string,
    options?: {
      subtitle?: string;
      sourceOrigin?: MindMapSourceOrigin;
      metadata?: Record<string, unknown>;
    },
  ) => string;
  /** Add an edge between two nodes */
  addEdge: (
    sourceId: string,
    targetId: string,
    relation: MindMapEdgeRelation,
  ) => void;
  /** Accept a pending node (marks it as accepted_by_operator) */
  acceptNode: (nodeId: string) => void;
  /** Discard a node (marks it as discarded_by_operator) */
  discardNode: (nodeId: string) => void;
  /** Accept all pending nodes */
  acceptAll: () => void;
  /** Confirm & Save — persist all accepted entities to the database */
  confirmAll: () => Promise<{ persisted_count: number } | null>;
  /** Discard everything — abandon the session without persisting */
  discardAll: () => Promise<boolean>;
  /** Manually trigger a backup save to the server */
  saveBackup: () => Promise<void>;
  /** Restore from server backup */
  restoreFromBackup: () => Promise<boolean>;
  /** Batch-add candidate nodes from paste-in extraction */
  addNodesFromPasteIn: (nodes: PasteInCandidateNode[]) => void;
  /** Check if there are unsaved working changes */
  hasUnsavedChanges: boolean;
  /** Current state version */
  stateVersion: number;
  /** Whether a save/confirm operation is in progress */
  isSaving: boolean;
  /** Whether the session is confirmed (terminal) */
  isConfirmed: boolean;
  /** Whether the session is discarded (terminal) */
  isDiscarded: boolean;
  /** Counts */
  pendingCount: number;
  acceptedCount: number;
  discardedCount: number;
}

export function useWorkingState(
  sessionId: string | null,
): {
  nodes: Node<MindMapNodeData>[];
  edges: Edge<MindMapEdgeData>[];
  actions: WorkingStateActions;
} {
  const [nodes, setNodes] = useState<Node<MindMapNodeData>[]>([]);
  const [edges, setEdges] = useState<Edge<MindMapEdgeData>[]>([]);
  const [stateVersion, setStateVersion] = useState(1);
  const [isSaving, setIsSaving] = useState(false);
  const [isConfirmed, setIsConfirmed] = useState(false);
  const [isDiscarded, setIsDiscarded] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const saveTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Auto-save debounce: backup to server after 2s of inactivity
  const scheduleSave = useCallback(() => {
    if (!sessionId) return;
    setHasUnsavedChanges(true);
    if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current);
    saveTimeoutRef.current = setTimeout(() => {
      // Trigger save — uses latest refs via closure
      setNodes((currentNodes) => {
        setEdges((currentEdges) => {
          setStateVersion((v) => {
            if (sessionId && currentNodes.length > 0) {
              saveWorkingState(
                sessionId,
                currentNodes.map(nodeToPayload),
                currentEdges.map(edgeToPayload),
                v,
              )
                .then(() => setHasUnsavedChanges(false))
                .catch((err) => console.error("Auto-save failed:", err));
            }
            return v;
          });
          return currentEdges;
        });
        return currentNodes;
      });
    }, 2000);
  }, [sessionId]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current);
    };
  }, []);

  // ── Node operations ────────────────────────────────────────────

  const addNode = useCallback(
    (
      entityType: MindMapEntityType,
      label: string,
      options?: {
        subtitle?: string;
        sourceOrigin?: MindMapSourceOrigin;
        metadata?: Record<string, unknown>;
      },
    ): string => {
      const id = generateNodeId();
      const newNode: Node<MindMapNodeData> = {
        id,
        type: "mindMapNode",
        position: { x: 0, y: 0 },
        data: {
          entityType,
          label,
          subtitle: options?.subtitle,
          status: "pending",
          sourceOrigin: options?.sourceOrigin ?? "conversation",
          metadata: options?.metadata,
        },
      };
      setNodes((prev) => [...prev, newNode]);
      setStateVersion((v) => v + 1);
      scheduleSave();
      return id;
    },
    [scheduleSave],
  );

  const addEdge = useCallback(
    (sourceId: string, targetId: string, relation: MindMapEdgeRelation) => {
      const id = generateEdgeId(sourceId, targetId);
      const newEdge: Edge<MindMapEdgeData> = {
        id,
        source: sourceId,
        target: targetId,
        data: { relation },
        animated: true,
        style: { stroke: "rgba(129, 140, 248, 0.4)", strokeWidth: 1.5 },
      };
      setEdges((prev) => [...prev, newEdge]);
      scheduleSave();
    },
    [scheduleSave],
  );

  const acceptNode = useCallback(
    (nodeId: string) => {
      setNodes((prev) =>
        prev.map((n) =>
          n.id === nodeId
            ? { ...n, data: { ...n.data, status: "accepted" as const } }
            : n,
        ),
      );
      setStateVersion((v) => v + 1);
      scheduleSave();
    },
    [scheduleSave],
  );

  const discardNode = useCallback(
    (nodeId: string) => {
      setNodes((prev) =>
        prev.map((n) =>
          n.id === nodeId
            ? { ...n, data: { ...n.data, status: "discarded" as const } }
            : n,
        ),
      );
      setStateVersion((v) => v + 1);
      scheduleSave();
    },
    [scheduleSave],
  );

  const acceptAll = useCallback(() => {
    setNodes((prev) =>
      prev.map((n) =>
        n.data.status === "pending"
          ? { ...n, data: { ...n.data, status: "accepted" as const } }
          : n,
      ),
    );
    setStateVersion((v) => v + 1);
    scheduleSave();
  }, [scheduleSave]);

  // ── Batch operations ───────────────────────────────────────────

  const confirmAll = useCallback(async (): Promise<{
    persisted_count: number;
  } | null> => {
    if (!sessionId) return null;
    setIsSaving(true);
    try {
      // First, ensure the latest state is saved
      const currentNodes = nodes;
      const currentEdges = edges;
      await saveWorkingState(
        sessionId,
        currentNodes.map(nodeToPayload),
        currentEdges.map(edgeToPayload),
        stateVersion,
      );

      // Collect accepted node IDs
      const acceptedIds = currentNodes
        .filter((n) => n.data.status === "accepted")
        .map((n) => n.id);

      if (acceptedIds.length === 0) return null;

      const result = await confirmWorkingState(sessionId, acceptedIds);
      setIsConfirmed(true);
      setHasUnsavedChanges(false);
      return { persisted_count: result.persisted_count };
    } catch (err) {
      console.error("Confirm failed:", err);
      return null;
    } finally {
      setIsSaving(false);
    }
  }, [sessionId, nodes, edges, stateVersion]);

  const discardAll = useCallback(async (): Promise<boolean> => {
    if (!sessionId) return false;
    setIsSaving(true);
    try {
      await discardWorkingState(sessionId);
      setIsDiscarded(true);
      setNodes([]);
      setEdges([]);
      setHasUnsavedChanges(false);
      return true;
    } catch (err) {
      console.error("Discard failed:", err);
      return false;
    } finally {
      setIsSaving(false);
    }
  }, [sessionId]);

  const saveBackup = useCallback(async () => {
    if (!sessionId || nodes.length === 0) return;
    setIsSaving(true);
    try {
      await saveWorkingState(
        sessionId,
        nodes.map(nodeToPayload),
        edges.map(edgeToPayload),
        stateVersion,
      );
      setHasUnsavedChanges(false);
    } catch (err) {
      console.error("Manual save failed:", err);
    } finally {
      setIsSaving(false);
    }
  }, [sessionId, nodes, edges, stateVersion]);

  const restoreFromBackup = useCallback(async (): Promise<boolean> => {
    if (!sessionId) return false;
    try {
      const state = await fetchWorkingState(sessionId);
      if (state.state_version === 0 || !state.candidate_nodes?.length) {
        return false;
      }
      setNodes(state.candidate_nodes.map(payloadToNode));
      setEdges(state.candidate_edges.map(payloadToEdge));
      setStateVersion(state.state_version);
      setHasUnsavedChanges(false);
      return true;
    } catch {
      return false;
    }
  }, [sessionId]);

  const addNodesFromPasteIn = useCallback(
    (pasteInNodes: PasteInCandidateNode[]) => {
      const newNodes: Node<MindMapNodeData>[] = pasteInNodes.map((n) => ({
        id: n.node_id,
        type: "mindMapNode",
        position: { x: 0, y: 0 },
        data: {
          entityType: n.entity_type as MindMapEntityType,
          label: n.label,
          subtitle: n.subtitle,
          status: "pending" as const,
          sourceOrigin: "paste_in" as MindMapSourceOrigin,
          metadata: n.metadata,
        },
      }));
      setNodes((prev) => [...prev, ...newNodes]);
      setStateVersion((v) => v + newNodes.length);
      scheduleSave();
    },
    [scheduleSave],
  );

  // ── Computed counts ────────────────────────────────────────────

  const pendingCount = nodes.filter((n) => n.data.status === "pending").length;
  const acceptedCount = nodes.filter((n) => n.data.status === "accepted").length;
  const discardedCount = nodes.filter((n) => n.data.status === "discarded").length;

  return {
    nodes,
    edges,
    actions: {
      addNode,
      addEdge,
      acceptNode,
      discardNode,
      acceptAll,
      confirmAll,
      discardAll,
      saveBackup,
      restoreFromBackup,
      addNodesFromPasteIn,
      hasUnsavedChanges,
      stateVersion,
      isSaving,
      isConfirmed,
      isDiscarded,
      pendingCount,
      acceptedCount,
      discardedCount,
    },
  };
}

