/**
 * Mind-map layout — dagre-based automatic node positioning.
 *
 * ARCH:PersonaPage.MindMapArchitecture
 * PLAN:WorkstreamE.PackageE13.PersonaPageMindMap
 *
 * Uses dagre to compute a top-to-bottom hierarchical layout for
 * mind-map nodes and edges. Supports incremental re-layout as
 * new nodes are added during conversation.
 */

import dagre from "@dagrejs/dagre";
import type { Node, Edge } from "@xyflow/react";

const NODE_WIDTH = 200;
const NODE_HEIGHT = 80;
const RANK_SEP = 80; // vertical space between ranks
const NODE_SEP = 40; // horizontal space between nodes

export interface LayoutOptions {
  direction?: "TB" | "LR"; // top-to-bottom or left-to-right
  rankSep?: number;
  nodeSep?: number;
}

/**
 * Apply dagre layout to nodes and edges, returning new positioned nodes.
 *
 * Preserves existing node/edge data — only updates position.
 */
export function applyDagreLayout(
  nodes: Node[],
  edges: Edge[],
  options: LayoutOptions = {},
): Node[] {
  const {
    direction = "TB",
    rankSep = RANK_SEP,
    nodeSep = NODE_SEP,
  } = options;

  const g = new dagre.graphlib.Graph();
  g.setDefaultEdgeLabel(() => ({}));
  g.setGraph({
    rankdir: direction,
    ranksep: rankSep,
    nodesep: nodeSep,
    marginx: 40,
    marginy: 40,
  });

  // Add nodes
  for (const node of nodes) {
    g.setNode(node.id, { width: NODE_WIDTH, height: NODE_HEIGHT });
  }

  // Add edges
  for (const edge of edges) {
    g.setEdge(edge.source, edge.target);
  }

  dagre.layout(g);

  // Map back to React Flow nodes with computed positions
  return nodes.map((node) => {
    const nodeWithPosition = g.node(node.id);
    if (!nodeWithPosition) return node;

    return {
      ...node,
      position: {
        x: nodeWithPosition.x - NODE_WIDTH / 2,
        y: nodeWithPosition.y - NODE_HEIGHT / 2,
      },
    };
  });
}

