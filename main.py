from src.airport_network.data_loader import load_datasets
from src.airport_network.preprocessing import (
    prepare_airports,
    match_airports_and_routes
)
from src.airport_network.graph_builder import build_networks
from src.airport_network.network_cleaner import (
    inspect_network,
    clean_network
)
from src.airport_network.analysis import analyze_network
from src.airport_network.exporter import export_network
from src.airport_network.reporting import (
    print_network_summary,
    print_network_anomalies,
    print_analysis_results
)


def main():
    # 1. Load datasets
    airports_raw, routes_raw = load_datasets()

    print("RAW DATASET STATISTICS")
    print("=" * 60)
    print(f"Airport records: {len(airports_raw)}")
    print(f"Unique airport IDs: {airports_raw['airport_id'].nunique()}")
    print(f"Route records: {len(routes_raw)}")

    # 2. Preprocess and match datasets
    airports = prepare_airports(airports_raw)

    matched_airports, valid_routes = match_airports_and_routes(
        airports,
        routes_raw
    )

    print("\nDATA PREPARATION")
    print("=" * 60)
    print(f"Airports with valid coordinates: {len(airports)}")
    print(f"Matched airports: {len(matched_airports)}")
    print(f"Valid route records: {len(valid_routes)}")

    # 3. Construct graph representations
    G_multi, G = build_networks(
        matched_airports,
        valid_routes
    )

    # 4. Inspect networks before cleaning
    multi_stats = inspect_network(G_multi)
    directed_stats = inspect_network(G)

    print_network_summary("MULTIDIGRAPH BEFORE CLEANING", multi_stats)
    print_network_anomalies(G_multi, multi_stats)

    print_network_summary("DIRECTED GRAPH BEFORE CLEANING", directed_stats)

    # 5. Clean networks
    G_multi = clean_network(G_multi)
    G = clean_network(G)

    print_network_summary(
        "MULTIDIGRAPH AFTER CLEANING",
        inspect_network(G_multi)
    )

    print_network_summary(
        "DIRECTED GRAPH AFTER CLEANING",
        inspect_network(G)
    )

    # 6. Analyze the cleaned directed graph
    analysis = analyze_network(G)
    print_analysis_results(G, analysis)

    # 7. Export network data
    output_file = export_network(G, analysis)

    print(f"\nNetwork exported successfully: {output_file}")


if __name__ == "__main__":
    main()