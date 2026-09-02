from fastapi import APIRouter, Query
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

class AlertResponse(BaseModel):
    id: str
    alert_type: str
    severity: str
    title: str
    description: str
    source: str

@router.get("/alerts", response_model=List[AlertResponse])
def get_active_alerts(
    bbox: Optional[str] = Query(None, description="Bounding box filter")
):
    return [
        AlertResponse(
            id="alt_901",
            alert_type="high_wave",
            severity="medium",
            title="High Wave Advisory",
            description="Waves between 1.5m to 2.2m expected along the South Tamil Nadu coast.",
            source="INCOIS"
        )
    ]