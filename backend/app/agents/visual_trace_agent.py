from app.agents.state import AgentState

def synthesize_response(state: AgentState) -> AgentState:
    intent = state.get("intent")
    
    if intent == "pfz":
        data = state.get("ocean_data", {})
        state["final_text_response"] = (
            f"Favourable PFZ detected with SST at {data.get('sst_celsius')}°C "
            f"and Chlorophyll level at {data.get('chlorophyll_mg_m3')} mg/m³. "
            f"Confidence score: {int(data.get('confidence', 0)*100)}%."
        )
    elif intent == "weather":
        data = state.get("weather_data", {})
        state["final_text_response"] = (
            f"Current sea status: {data.get('warning')}. "
            f"Wind speed is {data.get('wind_speed_knots')} knots with wave heights around {data.get('wave_height_m')}m."
        )
    else:
        state["final_text_response"] = "Query processed. All coastal zones report standard conditions."

    return state