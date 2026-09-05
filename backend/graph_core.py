"""In-memory knowledge graph for maritime boundaries and regulations."""

import networkx as nx


G = nx.DiGraph()

G.add_node("EEZ_India", type="Boundary")
G.add_node("Seasonal_Ban", type="Regulation")
G.add_node("Cyclone_01", type="Event")

G.add_edge("EEZ_India", "Seasonal_Ban", relation="regulated_by")
G.add_edge("Cyclone_01", "EEZ_India", relation="affects")


if __name__ == "__main__":
    print(f"Graph initialized with nodes: {list(G.nodes(data=True))}")