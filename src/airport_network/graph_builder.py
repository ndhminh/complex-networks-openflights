import networkx as nx


def build_networks(airports, routes):
    G_multi = nx.MultiDiGraph()
    G = nx.DiGraph()

    # Add airport nodes
    for _, airport in airports.iterrows():
        airport_id = airport["airport_id"]

        attributes = {
            "name": airport["name"],
            "city": airport["city"],
            "country": airport["country"],
            "IATA": airport["IATA"],
            "latitude": float(airport["latitude"]),
            "longitude": float(airport["longitude"])
        }

        G_multi.add_node(airport_id, **attributes)
        G.add_node(airport_id, **attributes)

    # Preserve individual route records
    for _, route in routes.iterrows():
        G_multi.add_edge(
            route["source_id"],
            route["destination_id"],
            airline=route["airline"],
            airline_id=route["airline_id"],
            stops=route["stops"],
            equipment=route["equipment"],
            codeshare=route["codeshare"]
        )

    # Aggregate multiple records into unique directed connections
    grouped_routes = routes.groupby(
        ["source_id", "destination_id"]
    )

    for (source, destination), group in grouped_routes:
        G.add_edge(
            source,
            destination,
            route_records=len(group),
            airline_count=group["airline"].nunique(),
            airlines=group["airline"].dropna().unique().tolist()
        )

    return G_multi, G