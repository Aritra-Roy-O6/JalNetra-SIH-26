import networkx as nx

class MarineKnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self._seed_graph()

    def _seed_graph(self):
        # Zones
        self.graph.add_node("Zone_EEZ_IN", label="Indian EEZ", type="Zone", zone_type="EEZ")
        self.graph.add_node("Zone_Pamban", label="Pamban Coast", type="Zone", zone_type="Territorial")
        self.graph.add_node("Zone_PFZ_01", label="PFZ-Alpha (High Chlorophyll)", type="Zone", zone_type="PFZ")

        # Regulations & Hazards
        self.graph.add_node("Reg_Monsoon_Ban", label="Monsoon Trawling Ban", type="Regulation")
        self.graph.add_node("Hazard_Cyclone_01", label="Cyclone Precaution Alert", type="Hazard")

        # Relationships
        self.graph.add_edge("Zone_Pamban", "Reg_Monsoon_Ban", relation="regulated_by")
        self.graph.add_edge("Hazard_Cyclone_01", "Zone_Pamban", relation="affects")
        self.graph.add_edge("Zone_PFZ_01", "Zone_Pamban", relation="adjacent_to")

    def get_related_nodes(self, node_id: str):
        if not self.graph.has_node(node_id):
            return [], []
        
        nodes = [{"id": node_id, "label": self.graph.nodes[node_id].get("label", node_id), "type": self.graph.nodes[node_id].get("type", "Unknown")}]
        edges = []
        
        for neighbor in self.graph.neighbors(node_id):
            edge_data = self.graph.get_edge_data(node_id, neighbor)
            nodes.append({"id": neighbor, "label": self.graph.nodes[neighbor].get("label", neighbor), "type": self.graph.nodes[neighbor].get("type", "Unknown")})
            edges.append({"source": node_id, "target": neighbor, "relation": edge_data.get("relation", "relates_to")})

        return nodes, edges

# This is the instance that your other files are trying to import!
kg_instance = MarineKnowledgeGraph()