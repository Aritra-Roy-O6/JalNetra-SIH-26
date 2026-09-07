"""PFZ specialist backed by the globally loaded model and live providers."""

from app.agents.state import AgentState
from app.pfz_model import current_pfz_prediction


def ocean_analytics_agent(state: AgentState) -> AgentState:
    location = state.get("location") or {}
    prediction = current_pfz_prediction(
        location.get("latitude"),
        location.get("longitude"),
        location.get("distance_to_coast_km"),
    )
    if not prediction.get("available"):
        return {"ocean_result": {"available": False, **prediction}}
    features = prediction["features"]
    return {"ocean_result": {"available": True, "prediction": prediction, "candidates": [{
        "confidence_score": prediction["confidence_score"],
        "sst_celsius": features["sst"],
        "chlorophyll_mg_m3": features["chlorophyll"],
    }], "geojson": None}}
