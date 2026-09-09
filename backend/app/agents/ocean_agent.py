"""PFZ specialist backed by the globally loaded model and live providers."""

import asyncio

from app.agents.state import AgentState
from app.agents.ocean_analytics import computed_pfz
from app.pfz_model import current_pfz_prediction


def ocean_analytics_agent(state: AgentState) -> AgentState:
    location = state.get("location") or {}
    lat = location.get("latitude") if location.get("latitude") is not None else 21.63
    lon = location.get("longitude") if location.get("longitude") is not None else 87.51
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        import nest_asyncio
        nest_asyncio.apply()
        geojson = loop.run_until_complete(computed_pfz(lat, lon))
    else:
        geojson = asyncio.run(computed_pfz(lat, lon))
    candidates = [
        {
            "confidence_score": feature["properties"]["confidence_score"],
            "sst_celsius": feature["properties"]["sst_value"],
            "chlorophyll_mg_m3": feature["properties"]["chlorophyll_value"],
        }
        for feature in geojson.get("features", [])
    ]
    if not candidates:
        return {"ocean_result": {"available": False, "error": "No high-confidence potential fishing zones were found near this coastal location.", "geojson": geojson, "stale": geojson.get("stale", False)}}
    return {"ocean_result": {"available": True, "prediction": {"confidence_score": max(item["confidence_score"] for item in candidates)}, "candidates": candidates, "geojson": geojson, "stale": geojson.get("stale", False)}}
