from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.intent_agent import process_intent
from app.agents.ocean_agent import process_ocean_query
from app.agents.weather_agent import process_weather_query
from app.agents.visual_trace_agent import synthesize_response

def route_by_intent(state: AgentState) -> str:
    intent = state.get("intent", "general")
    if intent in ["pfz", "ocean_conditions"]:
        return "ocean_agent"
    elif intent in ["weather", "alert"]:
        return "weather_agent"
    return "synthesizer"

# Define Graph Flow
builder = StateGraph(AgentState)

builder.add_node("intent_agent", process_intent)
builder.add_node("ocean_agent", process_ocean_query)
builder.add_node("weather_agent", process_weather_query)
builder.add_node("synthesizer", synthesize_response)

builder.set_entry_point("intent_agent")

builder.add_conditional_edges(
    "intent_agent",
    route_by_intent,
    {
        "ocean_agent": "ocean_agent",
        "weather_agent": "weather_agent",
        "synthesizer": "synthesizer"
    }
)

builder.add_edge("ocean_agent", "synthesizer")
builder.add_edge("weather_agent", "synthesizer")
builder.add_edge("synthesizer", END)

orchestrator = builder.compile()