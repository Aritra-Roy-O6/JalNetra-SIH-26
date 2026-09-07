"use client";

const LEVEL_CLASS = {
  info: "border-slate-200 bg-slate-50 text-slate-700",
  success: "border-emerald-200 bg-emerald-50 text-emerald-900",
  warning: "border-amber-200 bg-amber-50 text-amber-950",
  error: "border-red-200 bg-red-50 text-red-900",
};

export default function ReasoningTracePanel({ trace, logs = [] }) {
  const entries = logs.length ? logs : (trace?.nodes || []).map((node) => ({
    level: node.type === "database_record" ? "success" : "info",
    stage: node.type,
    message: node.label,
  }));

  return (
    <details className="border border-slate-200 bg-white" open={entries.length > 0}>
      <summary className="cursor-pointer list-none px-3 py-2 text-sm font-semibold text-slate-800">
        <span className="mr-2 text-blue-700">▸</span>Execution log ({entries.length})
      </summary>
      <div className="max-h-64 space-y-2 overflow-y-auto border-t border-slate-200 p-3">
        {!entries.length && <p className="text-sm text-slate-500">Submit a query to view the agent log.</p>}
        {entries.map((entry, index) => (
          <div key={entry.stage + "-" + index} className={(LEVEL_CLASS[entry.level] || LEVEL_CLASS.info) + " rounded border px-3 py-2 text-xs"}>
            <div className="flex items-center justify-between gap-3 font-semibold uppercase tracking-wide">
              <span>{entry.stage}</span><span>{entry.level}</span>
            </div>
            <p className="mt-1 leading-5">{entry.message}</p>
          </div>
        ))}
      </div>
    </details>
  );
}
