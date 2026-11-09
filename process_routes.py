import json
import pandas as pd
import networkx as nx

print("1. Loading raw OpenFlights routes data...")
cols = [
    'airline', 'airline_id', 
    'source', 'source_id', 
    'dest', 'dest_id', 
    'codeshare', 'stops', 'equipment'
]

# Read CSV, treating '\N' as missing values (NaN)
df = pd.read_csv('routes.dat.txt', header=None, names=cols, na_values='\\N')

print(f"Total rows loaded: {len(df)}")

# Drop rows where source or destination is missing
df_clean = df.dropna(subset=['source', 'dest']).copy()
print(f"Rows after cleaning missing endpoints: {len(df_clean)}")

print("\n2. Building directed graph (DiGraph) using NetworkX...")
G = nx.from_pandas_edgelist(
    df_clean, 
    source='source', 
    target='dest', 
    edge_attr=['airline', 'stops', 'equipment'],
    create_using=nx.DiGraph()
)

print(f"-> Total Nodes (Airports): {G.number_of_nodes()}")
print(f"-> Total Edges (Routes): {G.number_of_edges()}")

print("\n3. Calculating basic topology metrics...")
# Degree centrality (fraction of nodes it is connected to)
degree_cent = nx.degree_centrality(G)
top_hubs = sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:10]

print("\nTop 10 Global Airport Hubs by Degree Centrality:")
for rank, (airport, cent) in enumerate(top_hubs, 1):
    in_deg = G.in_degree(airport)
    out_deg = G.out_degree(airport)
    print(f"  {rank}. Airport Code: {airport} | Centrality: {cent:.4f} | In-Degree: {in_deg} | Out-Degree: {out_deg}")

print("\n4. Exporting summary data for your website frontend...")
# Prepare top hubs data structure for JSON export
hubs_summary = [
    {
        "airport": airport,
        "centrality": round(cent, 4),
        "in_degree": G.in_degree(airport),
        "out_degree": G.out_degree(airport),
        "total_degree": G.degree(airport)
    }
    for airport, cent in top_hubs
]

dashboard_data = {
    "total_nodes": G.number_of_nodes(),
    "total_edges": G.number_of_edges(),
    "is_weakly_connected": nx.is_weakly_connected(G),
    "top_hubs": hubs_summary
}

with open('openflights_summary.json', 'w', encoding='utf-8') as f:
    json.dump(dashboard_data, f, indent=4)

print("Successfully exported summary to 'openflights_summary.json'!")