"use client";

import { useEffect, useState } from "react";
import GeospatialMap from "@/components/GeospatialMap";
import ReasoningTracePanel from "@/components/ReasoningTracePanel";
import VoiceInterface from "@/components/VoiceInterface";
import { ApiError, fetchAlerts, fetchPFZ, postQuery } from "@/lib/api";
import { loadLastChatMessage, loadMapState, loadRecentChatMessages, saveChatMessage, saveMapState } from "@/lib/db";

const DEFAULT_QUERY = "Where is the nearest Potential Fishing Zone today?";
const QUICK_QUERIES = [
  ["where fish", "Find fishing zone"],
  ["boundary warning", "Check boundary"],
  ["why low catch", "Explain low catch"],
];
const DEFAULT_MAP_STATE = { center: [20.25, 88.45], zoom: 5 };

export default function DashboardPage() {
  const [pfz, setPfz] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [query, setQuery] = useState(DEFAULT_QUERY);
  const [answer, setAnswer] = useState("Ask a safety or PFZ question to inspect the evidence path.");
  const [trace, setTrace] = useState(null);
  const [status, setStatus] = useState("Connecting to JalNetra API");
  const [loading, setLoading] = useState(false);
  const [mapState, setMapState] = useState(DEFAULT_MAP_STATE);
  const [history, setHistory] = useState([]);
  const [intent, setIntent] = useState(null);
  const [language, setLanguage] = useState("en-IN");
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    Promise.all([fetchPFZ({ latitude: DEFAULT_MAP_STATE.center[0], longitude: DEFAULT_MAP_STATE.center[1] }), fetchAlerts()])
      .then(([pfzData, alertData]) => {
        setPfz(pfzData);
        setAlerts(alertData);
        setStatus("Live prototype data loaded");
      })
      .catch((error) => {
        setStatus(error.message);
        setLogs((current) => [...current, { level: "error", stage: "startup", message: error.message }]);
      });
  }, []);

  useEffect(() => {
    Promise.all([loadMapState(), loadLastChatMessage(), loadRecentChatMessages()]).then(([savedMap, savedChat, savedHistory]) => {
      if (savedMap) setMapState({ center: savedMap.center, zoom: savedMap.zoom });
      setHistory(savedHistory);
      if (savedChat) {
        setQuery(savedChat.query);
        setAnswer(savedChat.answer);
      }
    });
  }, []);

  async function submitQuery(rawQuery) {
    const submittedQuery = rawQuery.trim();
    if (!submittedQuery) {
      return;
    }

    setQuery(submittedQuery);
    setLoading(true);
    setStatus("Checking marine evidence…");
    try {
      const result = await postQuery(submittedQuery, { language, latitude: mapState.center[0], longitude: mapState.center[1] });
      setAnswer(result.answer || "No answer returned.");
      setTrace(result.visual_trace);
      setLogs(result.execution_log || []);
      if (result.geojson) setPfz(result.geojson);
      await saveChatMessage(submittedQuery, result.answer || "No answer returned.");
      setHistory(await loadRecentChatMessages());
      setIntent(result.intent || "Marine query");
      setLanguage(result.language || language);
      setStatus(`Intent detected: ${result.intent || "Marine query"}`);
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "Query failed.";
      setStatus(message);
      setLogs((current) => [...current, { level: "error", stage: "api", message }]);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    submitQuery(query);
  }

  async function handleVoiceResult(result) {
    setQuery(result.transcribed_text);
    setAnswer(result.answer);
    setTrace(result.visual_trace || null);
    setLogs(result.execution_log || []);
    setIntent(result.intent || "Marine query");
    setLanguage(result.language || language);
    if (result.geojson) setPfz(result.geojson);
    await saveChatMessage(result.transcribed_text, result.answer);
    setHistory(await loadRecentChatMessages());
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
          <div role="status" className="border border-slate-300 bg-slate-50 px-3 py-2 text-sm font-medium text-slate-700">
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
                onStatus={(message) => {
                  setStatus(message);
                  if (/unavailable|error|failed|quota|configured/i.test(message)) {
                    setLogs((current) => [...current, { level: "error", stage: "voice", message }]);
                  }
                }}
                onResult={handleVoiceResult}
              />
              <label className="block text-sm font-medium text-slate-700" htmlFor="query-language">Answer language</label>
              <select id="query-language" value={language} onChange={(event) => setLanguage(event.target.value)} disabled={loading} className="w-full border border-slate-300 px-3 py-2 text-sm">
                <option value="en-IN">English</option><option value="hi-IN">हिन्दी (Hindi)</option><option value="ta-IN">தமிழ் (Tamil)</option><option value="te-IN">తెలుగు (Telugu)</option><option value="bn-IN">বাংলা (Bengali)</option><option value="od-IN">ଓଡ଼ିଆ (Odia)</option>
              </select>
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
              <div className="border-t border-slate-200 pt-3">
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Instant demo checks</p>
                <div className="grid gap-2 sm:grid-cols-3 lg:grid-cols-1">
                  {QUICK_QUERIES.map(([quickQuery, label]) => (
                    <button key={quickQuery} type="button" disabled={loading} onClick={() => submitQuery(quickQuery)} className="border border-slate-300 px-2 py-2 text-left text-xs font-medium text-slate-700 hover:border-blue-700 hover:text-blue-800 disabled:text-slate-400">
                      {label}
                    </button>
                  ))}
                </div>
              </div>
            </form>
          </section>

          <section className="border border-slate-300 bg-white">
            <div className="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-4 py-3">
              <h2 className="text-base font-semibold">Recommended action</h2>
              {intent && <span className="bg-blue-100 px-2 py-1 text-xs font-semibold text-blue-900">{intent}</span>}
            </div>
            <p className="p-4 text-sm leading-6 text-slate-700">{answer}</p>
          </section>

          {history.length > 0 && <section className="border border-slate-300 bg-white">
            <div className="border-b border-slate-200 bg-slate-50 px-4 py-3"><h2 className="text-base font-semibold">Available offline</h2></div>
            <div className="divide-y divide-slate-100">{history.map((item) => <button key={item.id} type="button" onClick={() => { setQuery(item.query); setAnswer(item.answer); }} className="w-full px-4 py-3 text-left text-sm hover:bg-slate-50"><span className="block font-medium text-slate-800">{item.query}</span><span className="block truncate text-xs text-slate-500">{item.answer}</span></button>)}</div>
          </section>}

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

        <section className="grid gap-4 xl:min-h-[760px] xl:grid-rows-[1fr_360px]">
          <section className="overflow-hidden border border-slate-300 bg-white">
            <div className="border-b border-slate-200 bg-slate-50 px-4 py-3">
              <h2 className="text-base font-semibold">Geospatial Operations Map</h2>
            </div>
            <div className="h-[min(62vh,460px)] min-h-[360px] xl:h-full">
              <GeospatialMap
                pfz={pfz}
                alerts={alerts}
                mapState={mapState}
                onMapChange={(nextMapState) => {
                  setMapState(nextMapState);
                  saveMapState(nextMapState);
                }}
              />
            </div>
          </section>

          <section className="border border-slate-300 bg-white">
            <div className="border-b border-slate-200 bg-slate-50 px-4 py-3">
              <h2 className="text-base font-semibold">Why JalNetra recommends this</h2>
              <p className="mt-1 text-xs text-slate-600">Follow the evidence from your question through each specialist to the final answer.</p>
            </div>
              <ReasoningTracePanel trace={trace} logs={logs} />
          </section>
        </section>
      </section>
    </main>
  );
}
