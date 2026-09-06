"use client";

import { Background, Controls, ReactFlow } from "@xyflow/react";

const NODE_CLASS = {
  input: "border-emerald-700 bg-emerald-50 text-emerald-950",
  agent: "border-blue-800 bg-blue-50 text-blue-950",
  database_record: "border-amber-700 bg-amber-50 text-amber-950",
};

function layoutTrace(trace) {
  const nodes = trace?.nodes || [];
  const edges = trace?.edges || [];

  return {
    nodes: nodes.map((node, index) => ({
      id: node.id,
      position: { x: (index % 2) * 260, y: Math.floor(index / 2) * 120 },
      data: {
        label: (
          <div className={`rounded border px-3 py-2 text-xs shadow-sm ${NODE_CLASS[node.type] || NODE_CLASS.agent}`}>
            <div className="font-semibold">{node.label}</div>
            <div className="mt-1 uppercase tracking-normal text-slate-500">{node.type}</div>
          </div>
        ),
      },
      type: "default",
      sourcePosition: "right",
      targetPosition: "left",
    })),
    edges: edges.map((edge, index) => ({
      id: `${edge.source}-${edge.target}-${index}`,
      source: edge.source,
      target: edge.target,
      label: edge.label,
      animated: true,
      style: { stroke: "#2563eb" },
    })),
  };
}

export default function ReasoningTracePanel({ trace }) {
  const graph = layoutTrace(trace);

  if (!graph.nodes.length) {
    return (
      <div className="flex h-full min-h-[280px] items-center justify-center border border-dashed border-slate-300 bg-white text-sm text-slate-500">
        Submit a query to view the reasoning trace.
      </div>
    );
  }

  return (
    <div className="h-full min-h-[320px] overflow-hidden border border-slate-200 bg-white">
      <ReactFlow nodes={graph.nodes} edges={graph.edges} fitView nodesDraggable={false}>
        <Background gap={18} size={1} />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}
