from pathlib import Path

# Project directories
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = PROJECT_ROOT / "dataset"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

# Input files
AIRPORTS_FILE = DATASET_DIR / "airports.dat.txt"
ROUTES_FILE = DATASET_DIR / "routes.dat.txt"

# Output files
NETWORK_FILE = OUTPUT_DIR / "airport_network.json"

AIRPORT_COLUMNS = [
    "airport_id", "name", "city", "country",
    "IATA", "ICAO", "latitude", "longitude",
    "altitude", "timezone", "DST", "tz",
    "type", "source"
]

ROUTE_COLUMNS = [
    "airline", "airline_id",
    "source", "source_id",
    "destination", "destination_id",
    "codeshare", "stops", "equipment"
]