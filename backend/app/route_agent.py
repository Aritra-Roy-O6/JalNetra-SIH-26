"""Route Optimization and Risk Agent."""

from app.state import AgentState


def route_optimization_agent(state: AgentState) -> AgentState:
    """Return a mock safe route and the hazards avoided by the route."""
    return {
        "route_result": {
            "geojson": {
                "type": "LineString",
                "coordinates": [[88.0, 20.0], [88.3, 20.2], [88.8, 20.5]],
            },
            "hazards_avoided": ["alert-cyclone-01", "Seasonal_Ban"],
            "algorithm": "dijkstra_mock",
        }
    }
