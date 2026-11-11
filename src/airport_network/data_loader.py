import pandas as pd

from .config import (
    AIRPORTS_FILE,
    ROUTES_FILE,
    AIRPORT_COLUMNS,
    ROUTE_COLUMNS
)


def load_datasets():
    airports = pd.read_csv(
        AIRPORTS_FILE,
        header=None,
        names=AIRPORT_COLUMNS,
        dtype={"airport_id": "string"}
    )

    routes = pd.read_csv(
        ROUTES_FILE,
        header=None,
        names=ROUTE_COLUMNS,
        dtype={
            "source_id": "string",
            "destination_id": "string"
        }
    )

    return airports, routes