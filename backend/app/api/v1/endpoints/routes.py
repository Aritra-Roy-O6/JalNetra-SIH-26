from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

router = APIRouter()

class RouteRequest(BaseModel):
    origin: Dict[str, float]       # {"lat": 9.28, "lon": 79.12}
    destination: Dict[str, float]  # {"lat": 9.45, "lon": 79.35}
    vessel_type: Optional[str] = "motorized_boat"

class RouteResponse(BaseModel):
    route_id: str
    distance_km: float
    estimated_time_mins: int
    hazard_notes: List[str]
    path_geojson: Dict[str, Any]

@router.post("/route", response_model=RouteResponse)
def calculate_safe_route(request: RouteRequest):
    return RouteResponse(
        route_id="route_demo_101",
        distance_km=24.5,
        estimated_time_mins=45,
        hazard_notes=["Passes 2km clear of Restricted MPA Zone"],
        path_geojson={
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [request.origin.get("lon", 79.12), request.origin.get("lat", 9.28)],
                    [request.destination.get("lon", 79.35), request.destination.get("lat", 9.45)]
                ]
            },
            "properties": {"status": "optimized"}
        }
    )