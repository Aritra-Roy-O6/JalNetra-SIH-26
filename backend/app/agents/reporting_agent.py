"""Reporting specialist."""

from app.agents.state import AgentState


def reporting_agent(state: AgentState) -> AgentState:
    sources = [name for name in ("ocean_result", "weather_result", "geofence_result", "route_result") if state.get(name)]
    return {"report_result": {"intent": state.get("intent"), "evidence_sources": sources}}
