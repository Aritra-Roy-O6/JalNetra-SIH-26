"use client";

import { useEffect, useState } from "react";
import GeospatialMap from "@/components/GeospatialMap";
import ReasoningTracePanel from "@/components/ReasoningTracePanel";
import VoiceInterface from "@/components/VoiceInterface";
import { ApiError, fetchAlerts, fetchPFZ, postQuery } from "@/lib/api";

const DEFAULT_QUERY = "Where is the nearest Potential Fishing Zone today?";

export default function DashboardPage() {
  const [pfz, setPfz] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [query, setQuery] = useState(DEFAULT_QUERY);
  const [answer, setAnswer] = useState("Ask a safety or PFZ question to inspect the evidence path.");
  const [trace, setTrace] = useState(null);
  const [status, setStatus] = useState("Connecting to JalNetra API");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    Promise.all([fetchPFZ(), fetchAlerts()])
      .then(([pfzData, alertData]) => {
        setPfz(pfzData);
        setAlerts(alertData);
        setStatus("Live prototype data loaded");
      })
      .catch((error) => setStatus(error.message));
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!query.trim()) {
      return;
    }

    setLoading(true);
    setStatus("Running agent workflow");
    try {
      const result = await postQuery(query.trim());
      setAnswer(result.answer || "No answer returned.");
      setTrace(result.visual_trace);
      setStatus(`Intent detected: ${result.intent || "Marine query"}`);
    } catch (error) {
      setStatus(error instanceof ApiError ? error.message : "Query failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-100 text-slate-950">
      <header className="border-b-4 border-orange-500 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-normal text-blue-800">
              SIH 2026 - ISRO Problem 26176
            </p>
            <h1 className="text-2xl font-bold text-slate-950">JalNetra ORCA Dashboard</h1>
            <p className="text-sm text-slate-600">
              PFZ, marine alerts, geofences, and explainable agent reasoning for coastal operations.
            </p>
          </div>
          <div className="border border-slate-300 bg-slate-50 px-3 py-2 text-sm font-medium text-slate-700">
            {status}
          </div>
        </div>
      </header>

      <section className="mx-auto grid max-w-7xl gap-4 px-4 py-4 lg:grid-cols-[360px_1fr]">
        <aside className="space-y-4">
          <section className="border border-slate-300 bg-white">
            <div className="border-b border-slate-200 bg-slate-50 px-4 py-3">
              <h2 className="text-base font-semibold">Marine Query</h2>
            </div>
            <form onSubmit={handleSubmit} className="space-y-3 p-4">
              <VoiceInterface
                disabled={loading}
                onStatus={setStatus}
                onResult={(result) => {
                  setQuery(result.transcribed_text);
                  setAnswer(result.answer);
                  setTrace(result.visual_trace || null);
                }}
              />
              <label className="block text-sm font-medium text-slate-700" htmlFor="query">
                Fisherman / authority question
              </label>
              <textarea
                id="query"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                className="min-h-28 w-full border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-700"
              />
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-800 px-4 py-2 text-sm font-semibold text-white disabled:bg-slate-400"
              >
                {loading ? "Processing" : "Ask ORCA"}
              </button>
            </form>
          </section>

          <section className="border border-slate-300 bg-white">
            <div className="border-b border-slate-200 bg-slate-50 px-4 py-3">
              <h2 className="text-base font-semibold">Answer</h2>
            </div>
            <p className="p-4 text-sm leading-6 text-slate-700">{answer}</p>
          </section>

          <section className="border border-slate-300 bg-white">
            <div className="border-b border-slate-200 bg-slate-50 px-4 py-3">
              <h2 className="text-base font-semibold">Active Layers</h2>
            </div>
            <dl className="grid grid-cols-3 gap-px bg-slate-200 text-center text-sm">
              <div className="bg-white p-3">
                <dt className="font-semibold text-green-700">PFZ</dt>
                <dd>{pfz?.features?.length || 0}</dd>
              </div>
              <div className="bg-white p-3">
                <dt className="font-semibold text-amber-700">Alerts</dt>
                <dd>{alerts.length}</dd>
              </div>
              <div className="bg-white p-3">
                <dt className="font-semibold text-blue-700">Bounds</dt>
                <dd>1</dd>
              </div>
            </dl>
          </section>
        </aside>

        <section className="grid min-h-[760px] gap-4 xl:grid-rows-[1fr_360px]">
          <section className="overflow-hidden border border-slate-300 bg-white">
            <div className="border-b border-slate-200 bg-slate-50 px-4 py-3">
              <h2 className="text-base font-semibold">Geospatial Operations Map</h2>
            </div>
            <div className="h-[460px] xl:h-full">
              <GeospatialMap pfz={pfz} alerts={alerts} />
            </div>
          </section>

          <section className="border border-slate-300 bg-white">
            <div className="border-b border-slate-200 bg-slate-50 px-4 py-3">
              <h2 className="text-base font-semibold">Visual Reasoning Trace</h2>
            </div>
            <ReasoningTracePanel trace={trace} />
          </section>
        </section>
      </section>
    </main>
  );
}
