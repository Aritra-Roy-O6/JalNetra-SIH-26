"""Weather and marine hazard specialist."""

import asyncio

from app.agents.state import AgentState
from app.agents.weather_safety import check_hazard_thresholds, fetch_weather


def weather_safety_agent(state: AgentState) -> AgentState:
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
        source = loop.run_until_complete(fetch_weather(lat, lon))
    else:
        source = asyncio.run(fetch_weather(lat, lon))
    if not source.get("available", True):
        return {"weather_result": {"available": False, "error": source.get("error", "Weather is unavailable."), "stale": source.get("stale", False)}}
    hourly = source.get("marine", {}).get("hourly", {})
    forecast = source.get("forecast", {}).get("hourly", {})
    values = {
        "wave_height_m": (hourly.get("wave_height") or [0])[0],
        "wind_speed_kmph": (forecast.get("wind_speed_10m") or [0])[0],
        "lightning_probability_pct": (forecast.get("precipitation_probability") or [0])[0],
    }
    hazards = check_hazard_thresholds(values)
    return {"weather_result": {"available": True, **hazards, "stale": source.get("stale", False), "source": source.get("source", "Open-Meteo")}}
