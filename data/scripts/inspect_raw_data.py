import json
import os

# Get absolute path to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Build path to raw data
RAW_DATA_PATH = os.path.join(BASE_DIR, "..", "raw", "PASS-TRAINS.json")

with open(RAW_DATA_PATH, "r", encoding="utf-8") as f:
    trains = json.load(f)


print("Type of data:", type(trains))
print("Total number of trains:", len(trains))

first_train = trains[0]

print("\nKeys in a train object:")
print(first_train.keys())

print("\nSample train details:")
print("Train Number:", first_train["trainNumber"])
print("Train Name:", first_train["trainName"])
print("Running Days:", first_train["runningDays"])
print("Number of stops:", len(first_train["trainRoute"]))

print("\nFirst stop:")
print(first_train["trainRoute"][0])

print("\nLast stop:")
print(first_train["trainRoute"][-1])
