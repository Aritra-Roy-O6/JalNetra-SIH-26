from app.agents.state import AgentState
from app.graph.knowledge_graph import kg_instance

def process_weather_query(state: AgentState) -> AgentState:
    nodes, edges = kg_instance.get_related_nodes("Hazard_Cyclone_01")
    state["nodes"].extend(nodes)
    state["edges"].extend(edges)
    state["weather_data"] = {
        "wind_speed_knots": 18,
        "wave_height_m": 1.2,
        "warning": "Moderate sea conditions"
    }
    return state