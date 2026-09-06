"""Shared state passed between JalNetra LangGraph nodes."""

from typing import TypedDict


class AgentState(TypedDict, total=False):
    """Shared state passed through the LangGraph workflow."""

    query: str
    detected_language: str
    intent: str
    entities: dict
    sub_tasks: list[dict]
    ocean_result: dict
    weather_result: dict
    geofence_result: dict
    route_result: dict
    report_result: dict
    response: str
    visual_trace: dict