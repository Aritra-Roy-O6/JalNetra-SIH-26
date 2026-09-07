"""Route specialist."""

from app.agents.state import AgentState


def route_optimization_agent(state: AgentState) -> AgentState:
    return {"route_result": {"available": False, "error": "Live route and regulatory data are not configured."}}
