"""Wind observation specialist using INCOIS ERDDAP."""

from app.agents.state import AgentState
from app.services.marine_data import MarineDataError, fetch_copernicus_wind


def weather_safety_agent(state: AgentState) -> AgentState:
    location = state.get("location") or {}
    if "latitude" not in location or "longitude" not in location:
        return {"weather_result": {"available": False, "error": "Select a map location to retrieve a CMEMS wind observation."}}
    try:
        source = fetch_copernicus_wind(location["latitude"], location["longitude"])
    except MarineDataError as error:
        return {"weather_result": {"available": False, "error": str(error)}}
    wind = {"wind_speed": source["wind_speed"], "wind_direction_deg": source["wind_direction_deg"], "observed_at": source["observed_at"], "source": source["source"]}
    return {"weather_result": {"available": True, "safe": None, "raw_values": wind, "reasons": [f"CMEMS observed wind is {wind['wind_speed']:.1f} m/s."], "alerts": []}}
