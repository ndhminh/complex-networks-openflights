import json

from .config import OUTPUT_DIR, NETWORK_FILE


def export_network(G, analysis):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    nodes_data = []

    for node, attributes in G.nodes(data=True):
        nodes_data.append({
            "id": node,
            "name": attributes["name"],
            "city": attributes["city"],
            "country": attributes["country"],
            "IATA": attributes["IATA"],
            "latitude": attributes["latitude"],
            "longitude": attributes["longitude"],
            "in_degree": analysis["in_degree"][node],
            "out_degree": analysis["out_degree"][node],
            "total_degree": analysis["total_degree"][node],
            "degree_centrality": analysis["degree_centrality"][node]
        })

    edges_data = []

    for source, destination, attributes in G.edges(data=True):
        edges_data.append({
            "source": source,
            "destination": destination,
            "route_records": attributes["route_records"],
            "airline_count": attributes["airline_count"],
            "airlines": attributes["airlines"]
        })

    network_data = {
        "nodes": nodes_data,
        "edges": edges_data
    }

    with open(NETWORK_FILE, "w", encoding="utf-8") as file:
        json.dump(
            network_data,
            file,
            ensure_ascii=False,
            indent=4
        )

    return NETWORK_FILE