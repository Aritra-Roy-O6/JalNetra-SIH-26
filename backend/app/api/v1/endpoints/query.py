from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid

from app.agents.orchestrator import orchestrator
from app.agents.state import AgentState

router = APIRouter()

class QueryRequest(BaseModel):
    user_id: str
    query: str
    language: Optional[str] = "en"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class QueryResponse(BaseModel):
    query_id: str
    response: str
    language: str
    reasoning_trace: Dict[str, Any]
    geojson: Optional[Dict[str, Any]] = None

@router.post("/query", response_model=QueryResponse)
async def handle_user_query(request: QueryRequest):
    query_id = str(uuid.uuid4())
    
    initial_state: AgentState = {
        "query_id": query_id,
        "user_id": request.user_id,
        "raw_query": request.query,
        "detected_language": request.language or "en",
        "translated_query": request.query,
        "intent": None,
        "user_location": {"lat": request.latitude, "lon": request.longitude} if request.latitude else None,
        "ocean_data": None,
        "weather_data": None,
        "geofence_data": None,
        "route_data": None,
        "nodes": [],
        "edges": [],
        "final_text_response": "",
        "geojson_overlays": None
    }
    
    # Execute LangGraph Pipeline
    final_state = await orchestrator.ainvoke(initial_state)
    
    return QueryResponse(
        query_id=query_id,
        response=final_state["final_text_response"],
        language=final_state["detected_language"],
        reasoning_trace={
            "nodes": final_state["nodes"],
            "edges": final_state["edges"]
        },
        geojson=final_state.get("geojson_overlays")
    )