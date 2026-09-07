"""Synthesizing and Visual Reasoning Agent."""

from app.state import AgentState
from app.language import translate_answer


def synthesizing_agent(state: AgentState) -> AgentState:
    """Merge agent evidence into the frontend answer and visual trace."""
    intent = state.get("intent", "Weather")
    nodes = [
        {"id": "user_query", "label": state["query"], "type": "input"},
        {"id": "intent_agent", "label": f"Intent: {intent}", "type": "agent"},
    ]
    edges = [{"source": "user_query", "target": "intent_agent", "label": "classified"}]
    evidence = []
    logs = [
        {"level": "info", "stage": "input", "message": f"Received {state.get('detected_language', 'en-IN')} query: {state.get('original_query', state['query'])}"},
        {"level": "info", "stage": "translation", "message": f"English context: {state.get('translated_query', state['query'])}"},
        {"level": "info", "stage": "intent", "message": f"Selected intent: {intent}"},
    ]
    geojson = None

    if ocean := state.get("ocean_result"):
        candidate = ocean["candidates"][0]
        nodes.append({"id": "pfz_evidence", "label": f"PFZ confidence {candidate['confidence_score']:.0%}", "type": "database_record"})
        edges.append({"source": "intent_agent", "target": "pfz_evidence", "label": "checked SST + chlorophyll"})
        evidence.append(f"PFZ confidence is {candidate['confidence_score']:.0%} at {candidate['lat']:.2f}°N, {candidate['lon']:.2f}°E")
        logs.append({"level": "success", "stage": "ocean", "message": "Checked SST and chlorophyll; PFZ evidence ready."})
        geojson = ocean["geojson"]
    if weather := state.get("weather_result"):
        values = weather["raw_values"]
        nodes.append({"id": "weather_evidence", "label": f"Wave height {values['wave_height_m']}m", "type": "database_record"})
        edges.append({"source": "intent_agent", "target": "weather_evidence", "label": "checked safety threshold"})
        evidence.append(weather["reasons"][0])
        logs.append({"level": "warning" if not weather["safe"] else "success", "stage": "weather", "message": weather["reasons"][0]})
    if geofence := state.get("geofence_result"):
        nodes.append({"id": "geofence_evidence", "label": geofence["active_restrictions"][0], "type": "database_record"})
        edges.append({"source": "intent_agent", "target": "geofence_evidence", "label": "traversed regulation graph"})
        evidence.append(f"{geofence['zone']} has an active {geofence['active_restrictions'][0]} restriction")
        logs.append({"level": "warning", "stage": "geofence", "message": "Active restriction found in the regulation graph."})
    if route := state.get("route_result"):
        nodes.append({"id": "route_evidence", "label": "Risk-aware route", "type": "database_record"})
        edges.append({"source": "intent_agent", "target": "route_evidence", "label": "avoided hazards"})
        evidence.append(f"route avoids {', '.join(route['hazards_avoided'])}")
        logs.append({"level": "success", "stage": "route", "message": "Risk-aware route calculated around listed hazards."})

    nodes.append({"id": "synthesis_agent", "label": "Evidence-based response", "type": "agent"})
    for node in nodes[2:-1]:
        edges.append({"source": node["id"], "target": "synthesis_agent", "label": "supports"})
    english = ". ".join(evidence) + "." if evidence else "No marine evidence was available for this request."
    first = state.get("ocean_result", {}).get("candidates", [{}])[0]
    weather_values = state.get("weather_result", {}).get("raw_values", {})
    geofence = state.get("geofence_result", {})
    route = state.get("route_result", {})
    answer = translate_answer(intent, state.get("requested_language", "en-IN"), {
        "english": english,
        "location": f"{first.get('lat', 0):.2f}°N, {first.get('lon', 0):.2f}°E",
        "confidence": f"{first.get('confidence_score', 0):.0%}",
        "wave": weather_values.get("wave_height_m", "-"),
        "threshold": weather_values.get("wave_threshold_m", "-"),
        "zone": geofence.get("zone", "the Indian EEZ"),
        "restriction": geofence.get("active_restrictions", ["restriction"])[0],
        "hazards": ", ".join(route.get("hazards_avoided", ["active hazards"])),
    })
    logs.append({"level": "success", "stage": "response", "message": f"Prepared simple {state.get('requested_language', 'en-IN')} response."})
    return {
        "response": answer,
        "execution_log": logs,
        "geojson": geojson,
        "visual_trace": {
            "nodes": nodes,
            "edges": edges,
        },
    }
