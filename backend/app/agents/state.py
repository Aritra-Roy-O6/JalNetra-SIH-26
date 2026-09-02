from typing import TypedDict, List, Dict, Any, Optional

class ReasoningNode(TypedDict):
    id: str
    label: str
    type: str  # e.g., "weather_alert", "zone", "route_segment"

class ReasoningEdge(TypedDict):
    source: str
    target: str
    relation: str  # e.g., "affects", "passes_through"

class AgentState(TypedDict):
    query_id: str
    user_id: str
    raw_query: str
    detected_language: str
    translated_query: str
    intent: Optional[str]
    
    # Location context (lat, lon)
    user_location: Optional[Dict[str, float]]
    
    # Data retrieved across agent executions
    ocean_data: Optional[Dict[str, Any]]
    weather_data: Optional[Dict[str, Any]]
    geofence_data: Optional[List[Dict[str, Any]]]
    route_data: Optional[Dict[str, Any]]
    
    # Graph Visual Trace Construction
    nodes: List[ReasoningNode]
    edges: List[ReasoningEdge]
    
    # Final outputs
    final_text_response: str
    geojson_overlays: Optional[Dict[str, Any]]