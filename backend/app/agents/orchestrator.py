from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.graph.knowledge_graph import kg_instance

# Agent Nodes
def process_intent(state: AgentState) -> AgentState:
    query = state["raw_query"].lower()
    
    if any(k in query for k in ["fish", "pfz", "catch", "chlorophyll", "sst"]):
        state["intent"] = "pfz"
    elif any(k in query for k in ["weather", "cyclone", "wave", "wind", "safe"]):
        state["intent"] = "weather"
    else:
        state["intent"] = "general"
        
    return state

def process_ocean(state: AgentState) -> AgentState:
    nodes, edges = kg_instance.get_related_nodes("Zone_PFZ_01")
    state["nodes"].extend(nodes)
    state["edges"].extend(edges)
    state["ocean_data"] = {
        "sst_celsius": 28.5,
        "chlorophyll_mg_m3": 2.4,
        "confidence": 0.89
    }
    return state

def process_weather(state: AgentState) -> AgentState:
    nodes, edges = kg_instance.get_related_nodes("Hazard_Cyclone_01")
    state["nodes"].extend(nodes)
    state["edges"].extend(edges)
    state["weather_data"] = {
        "wind_speed_knots": 18,
        "wave_height_m": 1.2,
        "warning": "Moderate sea conditions"
    }
    return state

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

# Intent Router
def route_intent(state: AgentState) -> str:
    return "ocean_node" if state["intent"] == "pfz" else "weather_node" if state["intent"] == "weather" else "synthesizer_node"

# Workflow Setup
workflow = StateGraph(AgentState)

workflow.add_node("intent_node", process_intent)
workflow.add_node("ocean_node", process_ocean)
workflow.add_node("weather_node", process_weather)
workflow.add_node("synthesizer_node", synthesize_response)

workflow.set_entry_point("intent_node")

workflow.add_conditional_edges(
    "intent_node",
    route_intent,
    {
        "ocean_node": "ocean_node",
        "weather_node": "weather_node",
        "synthesizer_node": "synthesizer_node"
    }
)

workflow.add_edge("ocean_node", "synthesizer_node")
workflow.add_edge("weather_node", "synthesizer_node")
workflow.add_edge("synthesizer_node", END)

orchestrator = workflow.compile()