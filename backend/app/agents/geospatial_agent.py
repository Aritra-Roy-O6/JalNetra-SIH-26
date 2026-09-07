"""Geofence specialist."""

from app.agents.state import AgentState


def geospatial_geofencing_agent(state: AgentState) -> AgentState:
    return {"geofence_result": {"available": False, "active_restrictions": [], "error": "A live regulatory geofence source is not configured."}}
