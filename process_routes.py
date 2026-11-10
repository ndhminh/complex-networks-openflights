import json
import pandas as pd
import networkx as nx

output_file = 'openflights_routes_data.json'

print("1. Loading airports data...")
airport_cols = [
    'airport_id', 'name', 'city', 'country', 'iata', 'icao', 
    'lat', 'lon', 'altitude', 'timezone', 'dst', 'tz', 'type', 'source'
]
airports_df = pd.read_csv('dataset/airports.dat.txt', header=None, names=airport_cols, na_values='\\N')
airports_df = airports_df.dropna(subset=['iata', 'lat', 'lon'])
airport_lookup = airports_df.set_index('iata')[['name', 'city', 'country', 'lat', 'lon']].to_dict('index')
print(f"Loaded {len(airports_df)} valid airports with coordinates.")

print("\n2. Loading raw OpenFlights routes data...")
route_cols = ['airline', 'airline_id', 'source', 'source_id', 'dest', 'dest_id', 'codeshare', 'stops', 'equipment']
df = pd.read_csv('dataset/routes.dat.txt', header=None, names=route_cols, na_values='\\N')
print(f"Total rows loaded: {len(df)}")

df_clean = df.dropna(subset=['source', 'dest']).copy()
print(f"Rows after cleaning missing endpoints: {len(df_clean)}")

print("\n3. Building directed graph (DiGraph) using NetworkX...")
G = nx.from_pandas_edgelist(
    df_clean, 
    source='source', 
    target='dest', 
    edge_attr=['airline', 'stops', 'equipment'],
    create_using=nx.DiGraph()
)

print(f"-> Total Nodes (Airports): {G.number_of_nodes()}")
print(f"-> Total Edges (Routes): {G.number_of_edges()}")

print("\n4. Calculating basic topology metrics...")
degree_cent = nx.degree_centrality(G)
top_hubs = sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:10]

print("\nTop 10 Global Airport Hubs by Degree Centrality:")
for rank, (airport, cent) in enumerate(top_hubs, 1):
    in_deg = G.in_degree(airport)
    out_deg = G.out_degree(airport)
    print(f"  {rank}. Airport Code: {airport} | Centrality: {cent:.4f} | In-Degree: {in_deg} | Out-Degree: {out_deg}")

print("\n5. Exporting complete nodes and edges for the map website...")
valid_nodes = [node for node in G.nodes() if node in airport_lookup]
sub_G = G.subgraph(valid_nodes).copy()

nodes_export = []
for node in sub_G.nodes():
    info = airport_lookup[node]
    nodes_export.append({
        "id": node,
        "name": info['name'],
        "city": info['city'],
        "country": info['country'],
        "lat": info['lat'],
        "lon": info['lon'],
        "in_degree": sub_G.in_degree(node),
        "out_degree": sub_G.out_degree(node),
        "total_degree": sub_G.degree(node),
        "centrality": round(degree_cent.get(node, 0), 4)
    })

edges_export = []
for u, v in sub_G.edges():
    edges_export.append({
        "source": u, 
        "dest": v
    })

map_payload = {
    "total_nodes": sub_G.number_of_nodes(),
    "total_edges": sub_G.number_of_edges(),
    "nodes": nodes_export,
    "edges": edges_export
}

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(map_payload, f, indent=4)

print(f"\nExported {len(nodes_export)} nodes and {len(edges_export)} edges to '{output_file}'")
