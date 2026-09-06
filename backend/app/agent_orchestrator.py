"""Central LangGraph traffic controller for JalNetra agents.

This module owns workflow state transitions and routing only. Domain behavior
lives in the individual agent modules under ``app``.
"""

from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.geospatial_agent import geospatial_geofencing_agent
from app.intent_agent import intent_translation_agent
from app.ocean_agent import ocean_analytics_agent
from app.reporting_agent import reporting_agent
from app.route_agent import route_optimization_agent
from app.state import AgentState
from app.synthesis_agent import synthesizing_agent
from app.weather_agent import weather_safety_agent

AGENT_NODES = ("ocean", "weather", "geofence", "route", "reporting")


def route_sub_tasks(state: AgentState) -> list[str]:
    """Fan out to the specialists named by Intent/Translation sub-tasks.

    Returning a list lets LangGraph schedule independent specialists in the
    same superstep. Duplicate agent names are removed while preserving order.
    """
    selected = []
    for task in state.get("sub_tasks", []):
        for agent_name in task.get("agents", []):
            if agent_name in AGENT_NODES and agent_name not in selected:
                selected.append(agent_name)
    return selected or ["weather"]


def build_graph():
    """Build the Intent -> specialists -> Synthesis workflow."""
    workflow = StateGraph(AgentState)
    workflow.add_node("intent", intent_translation_agent)
    workflow.add_node("ocean", ocean_analytics_agent)
    workflow.add_node("weather", weather_safety_agent)
    workflow.add_node("geofence", geospatial_geofencing_agent)
    workflow.add_node("route", route_optimization_agent)
    workflow.add_node("reporting", reporting_agent)
    workflow.add_node("synthesizer", synthesizing_agent)

    workflow.add_edge(START, "intent")
    workflow.add_conditional_edges(
        "intent",
        route_sub_tasks,
        {agent_name: agent_name for agent_name in AGENT_NODES},
    )
    for agent_name in AGENT_NODES:
        workflow.add_edge(agent_name, "synthesizer")
    workflow.add_edge("synthesizer", END)
    return workflow.compile()


graph = build_graph()

__all__ = ["AGENT_NODES", "build_graph", "graph", "route_sub_tasks"]
