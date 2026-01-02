"""
purpose:this tells us in a given train/route, at which position each station occurs by deriving indexes from stop_time.json
Format:
route id->{
    stop_id:position
       }

"""
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STOP_TIMES_FILE = os.path.join(
    BASE_DIR, "..", "processed", "stop_times.json"
)

PROCESSED_DIR = os.path.join(BASE_DIR, "..", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)


with open(STOP_TIMES_FILE, "r", encoding="utf-8") as f:
    stop_times = json.load(f)

print("Stop times records loaded:", len(stop_times))

#Building stop_routes_mapping
stop_routes_mapping = {}

for record in stop_times:
    route_id = record["route_id"]
    stop_id = record["stop_id"]
    stop_sequence = record["stop_sequence"]

    if route_id not in stop_routes_mapping:
        stop_routes_mapping[route_id] = {}

    # Store the earliest sequence if duplicates appear
    if stop_id not in stop_routes_mapping[route_id]:
        stop_routes_mapping[route_id][stop_id] = stop_sequence

print("Total routes in mapping:", len(stop_routes_mapping))

# Print a sample route mapping
sample_route = list(stop_routes_mapping.keys())[0]
print("Sample route_id:", sample_route)
print("Sample stops (first 5):",
      list(stop_routes_mapping[sample_route].items())[:5])

output_path = os.path.join(
    PROCESSED_DIR, "stop_routes_mapping.json"
)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(stop_routes_mapping, f, indent=2, ensure_ascii=False)

print("stop_routes_mapping.json saved to data/processed/")
