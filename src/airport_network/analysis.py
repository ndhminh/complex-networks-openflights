import networkx as nx


def analyze_network(G):
    in_degree = dict(G.in_degree())
    out_degree = dict(G.out_degree())
    total_degree = dict(G.degree())

    degree_centrality = nx.degree_centrality(G)

    top_airports = sorted(
        total_degree.items(),
        key=lambda item: item[1],
        reverse=True
    )[:10]

    number_of_nodes = G.number_of_nodes()
    number_of_edges = G.number_of_edges()

    return {
        "in_degree": in_degree,
        "out_degree": out_degree,
        "total_degree": total_degree,
        "degree_centrality": degree_centrality,
        "top_airports": top_airports,
        "density": nx.density(G),
        "average_in_degree": (
            sum(in_degree.values()) / number_of_nodes
            if number_of_nodes else 0
        ),
        "average_out_degree": (
            sum(out_degree.values()) / number_of_nodes
            if number_of_nodes else 0
        )
    }