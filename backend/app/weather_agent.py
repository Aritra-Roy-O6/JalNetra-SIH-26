"""Weather and Safety Agent."""

from app.state import AgentState

MOCK_ALERTS = [
    {
        "id": "alert-cyclone-01",
        "type": "cyclone",
        "severity": "high",
        "message": "Mock cyclone advisory near the Odisha coast.",
        "source": "mock_weather_service",
    }
]


def weather_safety_agent(state: AgentState) -> AgentState:
    """Apply transparent mock wave and wind thresholds to active alerts."""
    raw_values = {"wave_height_m": 3.2, "wave_threshold_m": 2.5, "wind_speed_kmh": 42}
    return {
        "weather_result": {
            "safe": False,
            "reasons": ["wave height 3.2m exceeds the 2.5m safety threshold"],
            "raw_values": raw_values,
            "alerts": MOCK_ALERTS,
        }
    }
