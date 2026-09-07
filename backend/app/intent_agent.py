"""Intent and Translation Agent."""

import re
from datetime import date, timedelta

from app.language import detect_language, translate_to_english
from app.state import AgentState

INTENT_CATEGORIES = (
    "PFZ", "Weather", "Safety", "Route", "Trend", "AlertSubscription", "Regulation"
)


def _fallback_intent(query: str) -> str:
    query_lower = query.lower()
    if any(term in query_lower for term in ("route", "navigate", "waypoint", "safest way")):
        return "Route"
    if any(term in query_lower for term in ("subscribe", "alert me", "notify", "notification")):
        return "AlertSubscription"
    if any(term in query_lower for term in ("decline", "decreased", "productivity", "trend", "why has")):
        return "Trend"
    if any(term in query_lower for term in ("regulation", "restricted", "restriction", "seasonal ban", "geofence")):
        return "Regulation"
    if any(term in query_lower for term in ("weather", "wind", "wave", "cyclone", "storm", "safe")):
        return "Weather"
    if any(term in query_lower for term in ("pfz", "fishing zone", "fish", "chlorophyll", "sst")):
        return "PFZ"
    return "Weather"


def _extract_entities(query: str) -> dict:
    query_lower = query.lower()
    entities = {}
    if "odisha" in query_lower:
        entities["location"] = "Odisha coast"
    elif "mumbai" in query_lower:
        entities["location"] = "Mumbai coast"
    coordinate_match = re.search(r"(-?\d+(?:\.\d+)?)\s*[,/]\s*(-?\d+(?:\.\d+)?)", query)
    if coordinate_match:
        entities["coordinates"] = [float(coordinate_match.group(1)), float(coordinate_match.group(2))]
    if "tomorrow" in query_lower:
        entities["date"] = str(date.today() + timedelta(days=1))
    if "thursday" in query_lower:
        entities["time_reference"] = "Thursday"
    for vessel_type in ("trawler", "fishing boat", "cargo vessel"):
        if vessel_type in query_lower:
            entities["vessel_type"] = vessel_type
    return entities


def _tasks_for_query(query: str, primary_intent: str) -> list[dict]:
    query_lower = query.lower()
    tasks = []
    if any(term in query_lower for term in ("report", "digest", "incident summary", "authority")):
        tasks.append({"intent": "Reporting", "agents": ["reporting"]})
    if primary_intent in ("PFZ", "Trend") or any(term in query_lower for term in ("pfz", "fishing zone")):
        tasks.append({"intent": "PFZ", "agents": ["ocean"]})
    if primary_intent in ("Weather", "Safety") or any(term in query_lower for term in ("weather", "safe", "cyclone", "wave")):
        tasks.append({"intent": "Weather", "agents": ["weather"]})
    if primary_intent in ("Regulation",) or any(term in query_lower for term in ("restricted", "regulation", "geofence")):
        tasks.append({"intent": "Regulation", "agents": ["geofence"]})
    if primary_intent == "Route" or "route" in query_lower:
        tasks.append({"intent": "Route", "agents": ["weather", "geofence", "route"]})
    return tasks or [{"intent": primary_intent, "agents": ["weather"]}]


def intent_translation_agent(state: AgentState) -> AgentState:
    """Detect language, classify intent, extract entities, and create sub-tasks."""
    original_query = state.get("original_query", state["query"])
    requested_language = state.get("requested_language", "en-IN")
    detected_language = detect_language(original_query, requested_language)
    query = translate_to_english(original_query, detected_language)
    intent = _fallback_intent(query)
    return {
        "original_query": original_query,
        "translated_query": query,
        "requested_language": requested_language,
        "intent": intent,
        "detected_language": detected_language,
        "entities": _extract_entities(query),
        "sub_tasks": _tasks_for_query(query, intent),
    }
