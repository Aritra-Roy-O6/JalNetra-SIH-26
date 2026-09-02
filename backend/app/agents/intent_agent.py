from app.agents.state import AgentState

def process_intent(state: AgentState) -> AgentState:
    query = state["raw_query"].lower()
    
    if any(k in query for k in ["fish", "pfz", "catch", "chlorophyll", "sst"]):
        state["intent"] = "pfz"
    elif any(k in query for k in ["weather", "cyclone", "wave", "wind", "safe"]):
        state["intent"] = "weather"
    else:
        state["intent"] = "general"
        
    return state