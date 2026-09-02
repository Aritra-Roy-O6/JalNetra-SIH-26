from app.agents.state import AgentState
from app.graph.knowledge_graph import kg_instance

def process_ocean_query(state: AgentState) -> AgentState:
    nodes, edges = kg_instance.get_related_nodes("Zone_PFZ_01")
    state["nodes"].extend(nodes)
    state["edges"].extend(edges)
    state["ocean_data"] = {
        "sst_celsius": 28.5,
        "chlorophyll_mg_m3": 2.4,
        "confidence": 0.89
    }
    return state