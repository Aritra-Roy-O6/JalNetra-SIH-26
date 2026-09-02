import networkx as nx

class MarineKnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self._seed_initial_data()

    def _seed_initial_data(self):
        # Sample Zones
        self.graph.add_node("Zone_EEZ_India", type="Zone", name="Indian EEZ", zone_type="EEZ")
        self.graph.add_node("Zone_MPA_GulfOfMannar", type="Zone", name="Gulf of Mannar Marine National Park", zone_type="MPA")
        
        # Sample Regulations
        self.graph.add_node("Reg_Monsoon_Ban", type="Regulation", description="Seasonal Trawling Fishing Ban")
        
        # Edges
        self.graph.add_edge("Zone_MPA_GulfOfMannar", "Reg_Monsoon_Ban", relation="regulated_by")

    def check_geofence_restrictions(self, zone_id: str) -> list:
        if not self.graph.has_node(zone_id):
            return []
        neighbors = list(self.graph.neighbors(zone_id))
        return [self.graph.nodes[n] for n in neighbors]

kg_service = MarineKnowledgeGraph()