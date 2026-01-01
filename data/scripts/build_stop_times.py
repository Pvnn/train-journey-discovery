import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RAW_FILE = os.path.join(BASE_DIR, "..", "raw", "PASS-TRAINS.json")
STOPS_FILE = os.path.join(BASE_DIR, "..", "processed", "stops.json")
PROCESSED_DIR = os.path.join(BASE_DIR, "..", "processed")

os.makedirs(PROCESSED_DIR, exist_ok=True)

with open(RAW_FILE, "r", encoding="utf-8") as f:
    trains = json.load(f)

with open(STOPS_FILE, "r", encoding="utf-8") as f:
    stops = json.load(f)

print("Passenger trains loaded:", len(trains))
print("Stops loaded:", len(stops))

def time_to_minutes(time_str):
    """
    Converts 'HH:MM' to minutes from midnight.
    """
    if not time_str or time_str in ["Source", "Destination"]:
        return None

    hours, minutes = time_str.split(":")
    return int(hours) * 60 + int(minutes)


stop_times = []

for train in trains:
    route_id = train["trainNumber"]

    for stop in train["trainRoute"]:
        station_name = stop.get("stationName", "")
        station_code = station_name.split("-")[-1].strip().upper()

        if station_code not in stops:
            continue

        stop_id = stops[station_code]["stop_id"]
        stop_sequence = int(stop.get("sno", 0))
        day = int(stop.get("day", 1)) - 1  # day offset starts from 0

        arrival_time = time_to_minutes(stop.get("arrives"))
        departure_time = time_to_minutes(stop.get("departs"))

        # Apply temporal ordering using day offset
        if arrival_time is not None:
            arrival_time += day * 1440

        if departure_time is not None:
            departure_time += day * 1440

        stop_times.append({
            "route_id": route_id,
            "stop_id": stop_id,
            "stop_sequence": stop_sequence,
            "arrival_time": arrival_time,
            "departure_time": departure_time,
            "day_offset": day
        })

print("Total stop_times records:", len(stop_times))


output_path = os.path.join(PROCESSED_DIR, "stop_times.json")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(stop_times, f, indent=2, ensure_ascii=False)

print("stop_times.json saved to data/processed/")
