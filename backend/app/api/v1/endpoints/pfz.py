from fastapi import APIRouter, Query

from app.pfz_model import MODEL_FEATURES, current_pfz_prediction, load_pfz_model

router = APIRouter()


@router.get("/pfz")
def get_potential_fishing_zones(
    latitude: float | None = Query(None),
    longitude: float | None = Query(None),
    distance_to_coast_km: float | None = Query(None, ge=0),
) -> dict:
    """Return the globally loaded PFZ model prediction and feature provenance."""
    model = load_pfz_model()
    return {
        "model_features": list(MODEL_FEATURES),
        "prediction": current_pfz_prediction(latitude, longitude, distance_to_coast_km, model),
    }
