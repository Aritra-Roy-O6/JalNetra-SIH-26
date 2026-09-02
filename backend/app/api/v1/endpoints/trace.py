from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter()

class TraceResponse(BaseModel):
    query_id: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]

@router.get("/trace/{query_id}", response_model=TraceResponse)
def get_reasoning_trace(query_id: str):
    return TraceResponse(
        query_id=query_id,
        nodes=[
            {"id": "Zone_Pamban", "label": "Pamban Coast", "type": "Zone"},
            {"id": "Hazard_Cyclone_01", "label": "Cyclone Precaution", "type": "Hazard"}
        ],
        edges=[
            {"source": "Hazard_Cyclone_01", "target": "Zone_Pamban", "relation": "affects"}
        ]
    )