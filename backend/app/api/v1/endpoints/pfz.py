from fastapi import APIRouter, Query
from typing import Optional, List
from pydantic import BaseModel

router = APIRouter()

class PFZFeature(BaseModel):
    id: str
    latitude: float
    longitude: float
    sst_celsius: float
    chlorophyll_mg_m3: float
    confidence_score: float
    recommendation: str

@router.get("/pfz", response_model=List[PFZFeature])
def get_potential_fishing_zones(
    bbox: Optional[str] = Query(None, description="Bounding box: min_lon,min_lat,max_lon,max_lat"),
    date: Optional[str] = Query(None, description="ISO Date string YYYY-MM-DD")
):
    # Stub response matching Ocean Analytics Agent schema
    return [
        PFZFeature(
            id="pfz_zone_01",
            latitude=9.28,
            longitude=79.12,
            sst_celsius=28.4,
            chlorophyll_mg_m3=2.3,
            confidence_score=0.88,
            recommendation="High productivity zone identified near Pamban Pass."
        )
    ]