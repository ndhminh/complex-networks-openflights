import networkx as nx


def inspect_network(G):
    self_loop_edges = list(nx.selfloop_edges(G))
    isolated_nodes = list(nx.isolates(G))

    return {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "self_loops": self_loop_edges,
        "isolated_nodes": isolated_nodes
    }


def clean_network(G):
    G = G.copy()

    # Remove self-loops
    G.remove_edges_from(
        list(nx.selfloop_edges(G))
    )

    # Remove isolated nodes
    G.remove_nodes_from(
        list(nx.isolates(G))
    )

    return G