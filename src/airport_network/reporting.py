def print_network_summary(name, statistics):
    print(f"\n{name}")
    print("=" * 60)

    print(f"Nodes: {statistics['nodes']}")
    print(f"Edges: {statistics['edges']}")
    print(f"Self-loops: {len(statistics['self_loops'])}")
    print(f"Isolated nodes: {len(statistics['isolated_nodes'])}")


def print_network_anomalies(G, statistics):
    # Display isolated airport information
    if statistics["isolated_nodes"]:
        print("\nISOLATED AIRPORTS")

        for airport_id in sorted(statistics["isolated_nodes"]):
            airport = G.nodes[airport_id]

            print(
                f"ID: {airport_id} | "
                f"{airport['name']} | "
                f"{airport['IATA']} | "
                f"{airport['country']}"
            )

    # Display individual self-loop route records
    if statistics["self_loops"]:
        print("\nSELF-LOOP ROUTE RECORDS")

        for source, destination in statistics["self_loops"]:
            edge_data = G.get_edge_data(source, destination)

            if G.is_multigraph():
                for attributes in edge_data.values():
                    print(
                        f"Airline: {attributes.get('airline')} | "
                        f"Airline ID: {attributes.get('airline_id')} | "
                        f"Source: {source} | "
                        f"Destination: {destination} | "
                        f"Stops: {attributes.get('stops')} | "
                        f"Equipment: {attributes.get('equipment')}"
                    )
            else:
                print(
                    f"Source: {source} | "
                    f"Destination: {destination} | "
                    f"Route records: {edge_data['route_records']} | "
                    f"Airlines: {edge_data['airlines']}"
                )


def print_analysis_results(G, analysis):
    print("\nTOP 10 AIRPORTS BY TOTAL DEGREE")
    print("=" * 60)

    for rank, (airport_id, degree) in enumerate(
        analysis["top_airports"], 1
    ):
        airport = G.nodes[airport_id]

        print(
            f"{rank}. {airport['name']} ({airport['IATA']}) | "
            f"In: {analysis['in_degree'][airport_id]} | "
            f"Out: {analysis['out_degree'][airport_id]} | "
            f"Total: {degree} | "
            f"Centrality: "
            f"{analysis['degree_centrality'][airport_id]:.5f}"
        )

    print("\nNETWORK STATISTICS")
    print("=" * 60)

    print(f"Density: {analysis['density']:.10f}")
    print(f"Average in-degree: {analysis['average_in_degree']:.6f}")
    print(f"Average out-degree: {analysis['average_out_degree']:.6f}")