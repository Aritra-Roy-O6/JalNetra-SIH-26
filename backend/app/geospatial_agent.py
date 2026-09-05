"""Geospatial and Geofencing Agent."""

from graph_core import G

from app.state import AgentState


def geospatial_geofencing_agent(state: AgentState) -> AgentState:
    """Traverse regulatory graph relationships for the requested location."""
    graph_path = [
        {"source": source, "relation": data["relation"], "target": target}
        for source, target, data in G.edges(data=True)
    ]
    return {
        "geofence_result": {
            "zone": state.get("entities", {}).get("location", "Indian EEZ"),
            "active_restrictions": ["Seasonal_Ban"],
            "graph_path": graph_path,
        }
    }
