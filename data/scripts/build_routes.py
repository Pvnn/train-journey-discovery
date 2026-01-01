import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_FILE = os.path.join(BASE_DIR, "..", "raw", "PASS-TRAINS.json")
PROCESSED_DIR = os.path.join(BASE_DIR, "..", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)


with open(RAW_FILE, "r", encoding="utf-8") as f:
    trains = json.load(f)

print("Passenger trains loaded:", len(trains))

routes = {}


DAY_ORDER = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]

for train in trains:
    train_number = train["trainNumber"]
    train_name = train.get("trainName", "").strip()
    route_desc = train.get("route", "").strip()
    running_days_obj = train.get("runningDays", {})
    total_stops = len(train.get("trainRoute", []))

    # Convert runningDays dict → binary string
    running_days_str = ""
    for day in DAY_ORDER:
        running_days_str += "1" if running_days_obj.get(day, False) else "0"

    routes[train_number] = {
        "route_id": train_number,
        "train_name": train_name,
        "route_desc": route_desc,
        "running_days": running_days_str,
        "total_stops": total_stops
    }

print("Total routes created:", len(routes))

# Print a sample route
sample_key = list(routes.keys())[0]
print("Sample route:", routes[sample_key])

output_path = os.path.join(PROCESSED_DIR, "routes.json")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(routes, f, indent=2, ensure_ascii=False)

print("routes.json saved to data/processed/")
