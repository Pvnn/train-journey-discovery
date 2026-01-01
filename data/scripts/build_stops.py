import json
import os
import re

# Absolute path of this script: data/scripts/build_stops.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_FILE = os.path.join(BASE_DIR, "..", "raw", "PASS-TRAINS.json")
PROCESSED_DIR = os.path.join(BASE_DIR, "..", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

with open(RAW_FILE, "r", encoding="utf-8") as f:
    trains = json.load(f)

print("Passenger trains loaded:", len(trains))

stations = {}
stop_id_counter = 1

# Pattern to extract station name and code
# Example: "BADNERA JN - BD"
station_pattern = re.compile(r"(.+?)\s*-\s*([A-Z0-9]+)$")

for train in trains:
    for stop in train["trainRoute"]:
        raw_station = stop.get("stationName", "").strip()

        # Try to extract name and code
        match = station_pattern.match(raw_station)
        if not match:
            # Skip malformed station names safely
            continue

        station_name, station_code = match.groups()

        station_code = station_code.strip().upper()
        station_name = station_name.strip()

        # Add station only if not already present
        if station_code not in stations:
            stations[station_code] = {
                "stop_id": stop_id_counter,
                "stop_code": station_code,
                "stop_name": station_name
            }
            stop_id_counter += 1


#  Validation checks

print("Unique passenger stations:", len(stations))

for code in ["NDLS", "BCT", "PUNE"]:
    print(code, "->", stations.get(code))

#  Save output

output_path = os.path.join(PROCESSED_DIR, "stops.json")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(stations, f, indent=2, ensure_ascii=False)

print("stops.json saved to data/processed/")
