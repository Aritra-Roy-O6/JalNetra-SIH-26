"""Reporting Agent for authority and disaster-management summaries."""

from app.state import AgentState


def reporting_agent(state: AgentState) -> AgentState:
    """Build an auditable structured report from available agent outputs."""
    evidence_sources = [
        key
        for key in ("ocean_result", "weather_result", "geofence_result", "route_result")
        if state.get(key)
    ]
    return {
        "report_result": {
            "report_type": "coastal_conditions_digest",
            "region": state.get("entities", {}).get("location", "Indian coast"),
            "intent": state.get("intent", "Unknown"),
            "evidence_sources": evidence_sources,
        }
    }
