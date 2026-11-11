import pandas as pd


def prepare_airports(airports):
    airports = airports.copy()

    airports["latitude"] = pd.to_numeric(
        airports["latitude"], errors="coerce"
    )

    airports["longitude"] = pd.to_numeric(
        airports["longitude"], errors="coerce"
    )

    airports = airports.dropna(
        subset=["airport_id", "latitude", "longitude"]
    )

    airports = airports.drop_duplicates(
        subset=["airport_id"]
    )

    return airports


def match_airports_and_routes(airports, routes):
    routes = routes.dropna(
        subset=["source_id", "destination_id"]
    ).copy()

    airport_ids = set(airports["airport_id"])

    route_airport_ids = (
        set(routes["source_id"]) |
        set(routes["destination_id"])
    )

    matched_ids = airport_ids & route_airport_ids

    valid_routes = routes[
        routes["source_id"].isin(matched_ids) &
        routes["destination_id"].isin(matched_ids)
    ].copy()

    matched_airports = airports[
        airports["airport_id"].isin(matched_ids)
    ].copy()

    return matched_airports, valid_routes