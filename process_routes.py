import pandas as pd
import networkx as nx
import json

# ============================================================
# 1. LOAD DATASETS
# ============================================================

AIRPORTS_FILE = "dataset/airports.dat.txt"
ROUTES_FILE = "dataset/routes.dat.txt"

airport_columns = [
    "airport_id", "name", "city", "country",
    "IATA", "ICAO", "latitude", "longitude",
    "altitude", "timezone", "DST", "tz",
    "type", "source"
]

route_columns = [
    "airline", "airline_id",
    "source", "source_id",
    "destination", "destination_id",
    "codeshare", "stops", "equipment"
]

airports = pd.read_csv(
    AIRPORTS_FILE,
    header=None,
    names=airport_columns,
    dtype={"airport_id": "string"}
)

routes = pd.read_csv(
    ROUTES_FILE,
    header=None,
    names=route_columns,
    dtype={
        "source_id": "string",
        "destination_id": "string"
    }
)

print("=" * 60)
print("1. RAW DATASET STATISTICS")
print("=" * 60)

print(f"Total airport records: {len(airports)}")
print(f"Unique airport IDs: {airports['airport_id'].nunique()}")
print(f"Total route records: {len(routes)}")


# ============================================================
# 2. PREPARE AIRPORT AND ROUTE DATA
# ============================================================

# Keep airports with valid IDs and geographical coordinates
airports["latitude"] = pd.to_numeric(
    airports["latitude"], errors="coerce"
)

airports["longitude"] = pd.to_numeric(
    airports["longitude"], errors="coerce"
)

airports = airports.dropna(
    subset=["airport_id", "latitude", "longitude"]
)

# Keep only one record per airport ID
airports = airports.drop_duplicates(
    subset=["airport_id"]
)

# Preserve route records before endpoint filtering
routes = routes.dropna(
    subset=["source_id", "destination_id"]
).copy()

routes_before_filtering = routes.copy()

print("\n" + "=" * 60)
print("2. DATA PREPARATION")
print("=" * 60)

print(f"Airports with valid coordinates: {len(airports)}")
print(f"Route records with valid endpoints: {len(routes)}")


# ============================================================
# 3. MATCH AIRPORTS AND ROUTES
# ============================================================

# V_airports: airports with valid IDs and coordinates
V_airports = set(airports["airport_id"])

# V_routes: all airport IDs appearing in the route database
V_routes = (
    set(routes["source_id"]) |
    set(routes["destination_id"])
)

# Matched airport set: V = V_airports ∩ V_routes
V = V_airports & V_routes

# Keep only routes whose source and destination both exist in the matched airport set
valid_routes = routes[
    routes["source_id"].isin(V) &
    routes["destination_id"].isin(V)
].copy()

# Create airport lookup dictionary
airport_lookup = (
    airports[airports["airport_id"].isin(V)]
    .set_index("airport_id")
    .to_dict("index")
)

print("\n" + "=" * 60)
print("3. AIRPORT-ROUTE MATCHING")
print("=" * 60)

print(f"Airports in 'airports.dat.txt': {len(V_airports)}")
print(f"Airports in 'routes.dat.txt': {len(V_routes)}")
print(f"Matched network airports: {len(V)}")
print(f"Valid route records after matching: {len(valid_routes)}")


# ============================================================
# 4. BUILD MULTIDIGRAPH AND DIRECTED GRAPH
# ============================================================

# MultiDiGraph: Preserves every individual airline route record
G_multi = nx.MultiDiGraph()

# DiGraph: Represents unique directed connections between airports
G = nx.DiGraph()

# Add the same matched airport nodes to both graphs
for airport_id in V:

    airport = airport_lookup[airport_id]

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


# Add every valid route record to the MultiDiGraph
for _, route in valid_routes.iterrows():

    G_multi.add_edge(
        route["source_id"],
        route["destination_id"],
        airline=route["airline"],
        airline_id=route["airline_id"],
        stops=route["stops"],
        equipment=route["equipment"],
        codeshare=route["codeshare"]
    )


# Add unique airport-to-airport connections to the DiGraph
# Multiple airline records for the same directed pair are grouped
grouped_routes = valid_routes.groupby(
    ["source_id", "destination_id"]
)

for (source_id, destination_id), group in grouped_routes:

    G.add_edge(
        source_id,
        destination_id,
        route_records=len(group),
        airline_count=group["airline"].nunique(),
        airlines=group["airline"].dropna().unique().tolist()
    )


# ============================================================
# 5. INSPECT NETWORK BEFORE CLEANING
# ============================================================

print("\n" + "=" * 60)
print("4. NETWORK BEFORE CLEANING")
print("=" * 60)

print("\nMULTIDIGRAPH")
print("Nodes:", G_multi.number_of_nodes())
print("Edges:", G_multi.number_of_edges())

print("\nDIRECTED GRAPH")
print("Nodes:", G.number_of_nodes())
print("Edges:", G.number_of_edges())


# Count self-loops and isolated nodes before cleaning
multi_self_loops = nx.number_of_selfloops(G_multi)
directed_self_loops = nx.number_of_selfloops(G)

multi_isolates = list(nx.isolates(G_multi))
directed_isolates = list(nx.isolates(G))

print("\nNETWORK ANOMALIES BEFORE CLEANING")

print(f"MultiDiGraph self-loops: {multi_self_loops}")
print(f"DiGraph self-loops: {directed_self_loops}")

print(f"MultiDiGraph isolated nodes: {len(multi_isolates)}")
print(f"DiGraph isolated nodes: {len(directed_isolates)}")

# Display isolated airport information
if directed_isolates:
    print("\nISOLATED AIRPORTS")

    for airport_id in directed_isolates:
        airport = airport_lookup[airport_id]

        print(
            f"ID: {airport_id} | "
            f"{airport['name']} | "
            f"{airport['IATA']} | "
            f"{airport['country']}"
        )

# Display self-loop route records
self_loop_routes = valid_routes[
    valid_routes["source_id"] == valid_routes["destination_id"]
]

if not self_loop_routes.empty:
    print("\nSELF-LOOP ROUTE RECORDS")

    print(
        self_loop_routes[
            [
                "airline", "airline_id",
                "source", "source_id",
                "destination", "destination_id",
                "stops", "equipment"
            ]
        ].to_string(index=False)
    )


# ============================================================
# 6. CLEAN NETWORK
# ============================================================

print("\n" + "=" * 60)
print("5. NETWORK CLEANING")
print("=" * 60)

# Remove self-loops
G_multi.remove_edges_from(
    list(nx.selfloop_edges(G_multi))
)

G.remove_edges_from(
    list(nx.selfloop_edges(G))
)

# Remove isolated nodes after self-loop removal
G_multi.remove_nodes_from(
    list(nx.isolates(G_multi))
)

G.remove_nodes_from(
    list(nx.isolates(G))
)

# Display cleaned graph sizes
print("\nMULTIDIGRAPH")
print("Nodes:", G_multi.number_of_nodes())
print("Edges:", G_multi.number_of_edges())

print("\nDIRECTED GRAPH")
print("Nodes:", G.number_of_nodes())
print("Edges:", G.number_of_edges())

# Final validation
print("\nFINAL VALIDATION")
print("Remaining self-loops:", nx.number_of_selfloops(G))
print("Remaining isolated nodes:", len(list(nx.isolates(G))))


# ============================================================
# 7. DEGREE ANALYSIS
# ============================================================

# Calculate degree metrics on the cleaned DiGraph
in_degree = dict(G.in_degree())
out_degree = dict(G.out_degree())
total_degree = dict(G.degree())

degree_centrality = nx.degree_centrality(G)

# Sort airports by total degree, descending
top_airports = sorted(
    total_degree.items(),
    key=lambda item: item[1],
    reverse=True
)[:10]

print("\n" + "=" * 60)
print("6. TOP 10 AIRPORTS BY TOTAL DEGREE")
print("=" * 60)

for rank, (airport_id, degree) in enumerate(top_airports, 1):

    airport = airport_lookup[airport_id]

    print(
        f"{rank}. {airport['name']} ({airport['IATA']}) | "
        f"In: {in_degree[airport_id]} | "
        f"Out: {out_degree[airport_id]} | "
        f"Total: {degree} | "
        f"Centrality: {degree_centrality[airport_id]:.5f}"
    )


# ============================================================
# 8. NETWORK STATISTICS
# ============================================================

print("\n" + "=" * 60)
print("7. NETWORK STATISTICS")
print("=" * 60)

print(f"Density: {nx.density(G)}")

print(
    f"Average in-degree: "
    f"{sum(in_degree.values()) / G.number_of_nodes()}"
)

print(
    f"Average out-degree: "
    f"{sum(out_degree.values()) / G.number_of_nodes()}"
)


# ============================================================
# 9. EXPORT CLEANED NETWORK
# ============================================================

nodes_data = []

for node in G.nodes():

    airport = airport_lookup[node]

    nodes_data.append({
        "id": node,
        "name": airport["name"],
        "city": airport["city"],
        "country": airport["country"],
        "IATA": airport["IATA"],
        "latitude": float(airport["latitude"]),
        "longitude": float(airport["longitude"]),
        "in_degree": in_degree[node],
        "out_degree": out_degree[node],
        "total_degree": total_degree[node],
        "degree_centrality": degree_centrality[node]
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

with open("airport_network.json", "w", encoding="utf-8") as file:
    json.dump(
        network_data,
        file,
        ensure_ascii=False,
        indent=4
    )

print("\nNetwork exported successfully.")