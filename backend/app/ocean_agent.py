"""Ocean Analytics Agent."""

from pfz_heuristics import generate_mock_pfz

from app.state import AgentState


def ocean_analytics_agent(state: AgentState) -> AgentState:
    """Generate ranked PFZ evidence from the deterministic prototype heuristic."""
    pfz = generate_mock_pfz()
    candidates = []
    for feature in pfz["features"]:
        coordinates = feature["geometry"]["coordinates"][0]
        longitude = sum(point[0] for point in coordinates[:-1]) / (len(coordinates) - 1)
        latitude = sum(point[1] for point in coordinates[:-1]) / (len(coordinates) - 1)
        candidates.append(
            {
                "lat": latitude,
                "lon": longitude,
                "confidence_score": feature["properties"]["confidence"],
                "sst_celsius": feature["properties"]["sst_celsius"],
                "chlorophyll_mg_m3": feature["properties"]["chlorophyll_mg_m3"],
            }
        )
    return {"ocean_result": {"candidates": candidates, "geojson": pfz}}
