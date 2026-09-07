"""Turn specialist outputs into a plain, traceable response."""

from app.agents.state import AgentState
from app.language import translate_answer


def synthesizing_agent(state: AgentState) -> AgentState:
    intent = state.get("intent", "Weather")
    logs = [
        {"level": "info", "stage": "input", "message": f"Received {state.get('detected_language', 'en-IN')} input."},
        {"level": "info", "stage": "translation", "message": f"English context: {state.get('translated_query', state['query'])}"},
        {"level": "info", "stage": "intent", "message": f"Selected {intent} specialist."},
    ]
    evidence, nodes = [], [{"id": "input", "label": state["query"], "type": "input"}, {"id": "intent", "label": intent, "type": "agent"}]
    geojson = None
    ocean = state.get("ocean_result")
    if ocean:
        if ocean.get("available"):
            candidate = ocean["candidates"][0]
            evidence.append(f"The live PFZ model confidence is {candidate['confidence_score']:.0%}")
            logs.append({"level": "success", "stage": "copernicus", "message": "Live Copernicus features passed the PFZ model contract."})
            geojson = ocean.get("geojson")
        else:
            evidence.append(ocean["error"])
            for error in ocean.get("errors", []):
                logs.append({"level": "error", "stage": "ocean", "message": error})
            for warning in ocean.get("warnings", []):
                logs.append({"level": "warning", "stage": "ocean", "message": warning})
            logs.append({"level": "warning", "stage": "pfz", "message": ocean["error"]})
    weather = state.get("weather_result")
    if weather:
        if weather.get("available"):
            evidence.extend(weather["reasons"])
            logs.append({"level": "success", "stage": "incois", "message": "Retrieved current INCOIS wind observation."})
        else:
            evidence.append(weather["error"])
            logs.append({"level": "warning", "stage": "incois", "message": weather["error"]})
    for name, result in (("geofence", state.get("geofence_result")), ("route", state.get("route_result"))):
        if result and not result.get("available", True):
            evidence.append(result["error"])
            logs.append({"level": "warning", "stage": name, "message": result["error"]})
    english = ". ".join(item.rstrip(".") for item in evidence) + "." if evidence else "No marine evidence was available for this request."
    candidate = ocean.get("candidates", [{}])[0] if ocean else {}
    available = bool((ocean or {}).get("available") or (weather or {}).get("available"))
    answer = translate_answer(intent, state.get("requested_language", "en-IN"), {
        "english": english,
        "available": available,
        "location": "the selected map location",
        "confidence": f"{candidate.get('confidence_score', 0):.0%}",
        "wave": "not available",
        "threshold": "not available",
        "zone": "the selected map location",
        "restriction": "a restriction",
        "hazards": "known hazards",
    })
    logs.append({"level": "success", "stage": "response", "message": f"Prepared simple {state.get('requested_language', 'en-IN')} response."})
    nodes.append({"id": "response", "label": "Evidence-based response", "type": "agent"})
    return {"response": answer, "execution_log": logs, "geojson": geojson, "visual_trace": {"nodes": nodes, "edges": [{"source": "input", "target": "intent", "label": "classified"}, {"source": "intent", "target": "response", "label": "answered"}]}}
