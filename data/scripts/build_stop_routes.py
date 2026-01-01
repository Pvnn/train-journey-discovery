"""
Purpose: Build stop routes index for RAPTOR algorithm
Input: data/raw/train_details.json
Output: data/processed/stop_routes.json

Output format: {station_code: [train_number1, train_number2, ...]}

This enables RAPTOR to quickly answer: "Which trains serve this station?"
"""

import json
import os
from collections import defaultdict
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(SCRIPT_DIR)
RAW_DATA_PATH = os.path.join(DATA_DIR, "raw", "PASS-TRAINS.json")
OUTPUT_PATH = os.path.join(DATA_DIR, "processed", "stop_routes.json")

def extract_station_code(station_name):
  """
  Extract station code from station name string.

  Format: "STATION NAME - CODE"
  Example: "KALYAN JN - KYN" → "KYN"
            "PUNE JN - PUNE" → "PUNE"

  Args:
    station_name (str): Full station name with code

  Returns:
    str: Station code or None if pattern not found
  """
  match = re.search(r' - ([A-Z0-9]+)$', station_name)
  if match:
    return match.group(1)
  else:
    parts = station_name.split(" - ")
    if len(parts) >= 2:
      return parts[-1].strip()
  return None


def build_stop_routes_index(trains_data):
  """
  Build the stop routes index: station_code → [train_numbers]

  Args:
    trains_data (list): List of train dictionaries

  Returns:
    dict: {station_code: [list of train numbers]}
  """
  stop_routes = defaultdict(set)

  trains_processed = 0
  errors = []

  for train in trains_data:
    train_number = train.get("trainNumber")
    train_route = train.get("trainRoute", [])

    if not train_number:
      errors.append(f"Train missing trainNumber: {train.get('trainName', 'Unknown')}")
      continue

    trains_processed += 1

    for stop in train_route:
      station_name = stop.get("stationName")

      if not station_name:
        continue

      station_code = extract_station_code(station_name)

      if station_code:
        stop_routes[station_code].add(train_number)
      else:
        errors.append(f"Could not extract code from: {station_name}")

  stop_routes_final = {
    station: sorted(list(trains))
    for station, trains in stop_routes.items()
  }

  print(f"Processed {trains_processed} trains")
  print(f"Found {len(stop_routes_final)} unique stations")

  if errors:
    print(f"{len(errors)} errors encountered")
    if len(errors) <= 5:
      for err in errors:
        print(f"  - {err}")

  return stop_routes_final


def validate_stop_routes(stop_routes):
  """
  Validate the stop routes index by checking major junctions.
  """
  print()
  print("VALIDATION RESULTS")

  major_junctions = ["NDLS", "PUNE", "BCT", "MAS", "HWH", "SBC", "KYN", "CSMT", "LTT", "BSL", "ET", "DDU"]

  print("\nChecking major junctions (should have 100+ trains):")
  validation_passed = True

  for station_code in major_junctions:
    if station_code in stop_routes:
      train_count = len(stop_routes[station_code])
      status = "✓" if train_count >= 100 else "⚠"
      print(f"{status} {station_code:8} : {train_count:4} trains")

      if train_count < 100:
        validation_passed = False
    else:
      print(f"✗ {station_code:8} : NOT FOUND in dataset")
      validation_passed = False

  print()
  print("Top 10 busiest stations:")
  print("-" * 60)
  sorted_stations = sorted(stop_routes.items(), key=lambda x: len(x[1]), reverse=True)

  for i, (station, trains) in enumerate(sorted_stations[:10], 1):
    print(f"{i:2}. {station:8} : {len(trains):4} trains")

  print()
  print("Overall Statistics:")
  print(f"Total stations: {len(stop_routes)}")
  print(f"Total station-train connections: {sum(len(trains) for trains in stop_routes.values())}")

  avg_trains = sum(len(trains) for trains in stop_routes.values()) / len(stop_routes)
  print(f"Average trains per station: {avg_trains:.1f}")

  return validation_passed

def main():
  """
  Main execution function
  """
  print("BUILDING STOP ROUTES INDEX")
  print(f"Input file: {RAW_DATA_PATH}")
  print(f"Output file: {OUTPUT_PATH}")
  print()

  try:
    print("Step 1: Loading dataset...")

    if not os.path.exists(RAW_DATA_PATH):
      print(f"ERROR: Dataset not found at {RAW_DATA_PATH}")
      return

    with open(RAW_DATA_PATH, 'r', encoding='utf-8') as f:
      trains_data = json.load(f)

    print(f"Loaded {len(trains_data)} trains from dataset")
    print()

    print("Step 2: Building stop routes index...")
    stop_routes = build_stop_routes_index(trains_data)
    print()

    validate_stop_routes(stop_routes)

    print()
    print("SAVING OUTPUT")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
      json.dump(stop_routes, f, indent=2, ensure_ascii=False)

    print(f"Successfully saved to: {OUTPUT_PATH}")
    print(f"File size: {os.path.getsize(OUTPUT_PATH) / 1024:.1f} KB")
    print()

    print("Sample output (first 3 stations):")
    print("-" * 60)
    for i, (station, trains) in enumerate(list(stop_routes.items())[:3]):
        print(f"{station}: {trains[:5]}{'...' if len(trains) > 5 else ''} ({len(trains)} total)")
    print("STOP ROUTES INDEX BUILT SUCCESSFULLY!")

  except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()


if __name__ == "__main__":
  main()