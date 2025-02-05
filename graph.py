import networkx as nx
import matplotlib
matplotlib.use('TkAgg',force=True)
import matplotlib.pyplot as plt
import scipy as sp

class TicketToRideVisualizer:
    def __init__(self, game_state):
        self.game_state = game_state

    def visualize_game_map(self):
        G = nx.Graph()

        # Add nodes (cities)
        for city in self.game_state.routes:
            G.add_node(city)

        # Add edges (routes)
        for city1, connections in self.game_state.routes.items():
            for city2, routes in connections.items():
                for route in routes:
                    cb = route.claimed_by if route.claimed_by else 'Unclaimed'
                    G.add_edge(city1, city2, color=route.color.value, length=route.length, claimed_by=cb)

        # Customize node and edge appearance
        pos = nx.kamada_kawai_layout(G)
        node_color = ["lightblue"] * len(G.nodes)
        edge_colors = [edge_attr["color"] for u,v,edge_attr in G.edges(data=True)]

        # Draw the graph
        fig, ax = plt.subplots(figsize=(12, 8))
        nx.draw(G, pos, with_labels=True, node_color=node_color, edge_color=edge_colors, ax=ax, node_size=500, font_size=8)

        # Add edge labels
        edge_labels = {(u, v): f"{edge_attr['length'], edge_attr['claimed_by']}" for u, v, edge_attr in G.edges(data=True)}
        # Adjust label positions to appear above the edges
        label_pos = {k: (v[0], v[1] + 0.03) for k, v in pos.items()}
        nx.draw_networkx_edge_labels(G, label_pos, edge_labels=edge_labels, ax=ax, font_size=6)


        # Save the plot
        plt.savefig("ticket_to_ride_map.png")
        plt.show()
        return 0
