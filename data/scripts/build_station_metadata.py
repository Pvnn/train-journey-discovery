"""
Purpose: Build comprehensive station metadata for mcRAPTOR algorithm
Inputs: 
  - data/raw/station_classification_raw.json (scraped official data)
  - data/processed/stop_routes.json (train frequency from our data)
Output: 
  - data/processed/station_metadata.json

Classification Strategy:
  1. Primary: Use official NSG categories from scraped data
  2. Secondary: Use train frequency from stop_routes.json
  3. Combine both for best classification
"""

import json
import os
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(SCRIPT_DIR)

SCRAPED_DATA_PATH = os.path.join(DATA_DIR, "raw", "station_classification_raw.json")
STOP_ROUTES_PATH = os.path.join(DATA_DIR, "processed", "stop_routes.json")
OUTPUT_PATH = os.path.join(DATA_DIR, "processed", "station_metadata.json")

NSG_MAPPING = {
  'NSG 1': {'min_transfer_time': 15, 'tier': 'PREMIUM_TERMINAL'},
  'NSG 2': {'min_transfer_time': 20, 'tier': 'METRO_TERMINAL'},
  'NSG 3': {'min_transfer_time': 20, 'tier': 'METRO_TERMINAL'},
  'NSG 4': {'min_transfer_time': 30, 'tier': 'MAJOR_JUNCTION'},
  'NSG 5': {'min_transfer_time': 30, 'tier': 'MAJOR_JUNCTION'},
  'NSG 6': {'min_transfer_time': 90, 'tier': 'SMALL_STATION'},
  'NSG-S': {'min_transfer_time': 90, 'tier': 'SMALL_STATION'},  
}

MAJOR_JUNCTIONS = [
  'NDLS', 'CSMT', 'BCT', 'MAS', 'HWH', 'SBC', 'PUNE', 'KYN',
  'LTT', 'BSL', 'ET', 'DDU', 'PNBE', 'DLI', 'GZB', 'BZA',
  'VGLJ', 'AGC', 'BPL', 'NGP'
]


def load_data():
  """Load all required data files"""
  print("LOADING DATA FILES")


  # Load stop routes
  if not os.path.exists(STOP_ROUTES_PATH):
    print(f"✗ Error: {STOP_ROUTES_PATH} not found")
    print("  Please run build_stop_routes.py first!")
    return None, None

  with open(STOP_ROUTES_PATH, 'r', encoding='utf-8') as f:
    stop_routes = json.load(f)
  print(f"✓ Loaded {len(stop_routes)} stations from stop_routes.json")

  # Load scraped classification data (optional)
  scraped_stations = []
  if os.path.exists(SCRAPED_DATA_PATH):
    with open(SCRAPED_DATA_PATH, 'r', encoding='utf-8') as f:
      scraped_stations = json.load(f)
    print(f"✓ Loaded {len(scraped_stations)} stations from scraped data")
  else:
    print(f"⚠ Warning: {SCRAPED_DATA_PATH} not found")
    print("  Will use train frequency only for classification")

  print()
  return stop_routes, scraped_stations


def classify_by_train_count(train_count):
  """
  Classify station based on train frequency.

  As per task: Top 20 → METRO, Next 80 → MAJOR, Rest → SMALL

  Args:
    train_count: Number of trains stopping at station

  Returns:
    dict with tier and min_transfer_time
  """
  if train_count >= 100:  # Top tier
    return {
      'tier': 'METRO_TERMINAL',
      'min_transfer_time': 20
    }
  elif train_count >= 20:  # Major junctions
    return {
      'tier': 'MAJOR_JUNCTION',
      'min_transfer_time': 30
    }
  else:  # Small stations
    return {
      'tier': 'SMALL_STATION',
      'min_transfer_time': 90
    }


def get_tier_from_nsg(nsg_category):
  """
  Get tier classification from NSG category.

  Args:
    nsg_category: Official NSG category (e.g., "NSG 3")

  Returns:
    dict with tier and min_transfer_time, or None if unknown
  """
  return NSG_MAPPING.get(nsg_category)


def build_station_metadata(stop_routes, scraped_stations):
  """
  Build comprehensive station metadata.

  Strategy:
  1. Start with all stations from stop_routes (our actual network)
  2. Try to match with scraped official data
  3. Use official NSG category if available
  4. Otherwise, use train frequency for classification
  5. Combine best of both sources
  """
  print("BUILDING STATION METADATA")
  print()

  # Create lookup from scraped data
  scraped_lookup = {
    station['station_code']: station 
    for station in scraped_stations
  }

  station_metadata = {}
  matched_with_official = 0
  classified_by_frequency = 0

  # Process each station in our network
  for station_code, train_list in stop_routes.items():
    train_count = len(train_list)

    # Try to get official data
    official_data = scraped_lookup.get(station_code)

    if official_data:
      # We have official data - use it!
      matched_with_official += 1

      nsg_category = official_data.get('category', '').strip()
      tier_info = get_tier_from_nsg(nsg_category)

      if not tier_info:
        # Unknown NSG category, fall back to train count
        tier_info = classify_by_train_count(train_count)

      # Parse numeric fields
      try:
        footfall = int(official_data.get('passengers_footfall', '0').replace(',', ''))
      except:
        footfall = 0

      try:
        revenue = int(official_data.get('revenue', '0').replace(',', ''))
      except:
        revenue = 0

      metadata = {
        'station_name': official_data.get('station_name', station_code),
        'station_code': station_code,
        'state': official_data.get('state', ''),
        'zone': official_data.get('zone', ''),
        'division': official_data.get('division', ''),
        'category': nsg_category,
        'tier': tier_info['tier'],
        'min_transfer_time': tier_info['min_transfer_time'],
        'train_count': train_count,
        'passengers_footfall': footfall,
        'revenue': revenue,
        'data_source': 'official'
        }
    else:
      # No official data - classify by train frequency
      classified_by_frequency += 1
      tier_info = classify_by_train_count(train_count)

      metadata = {
        'station_name': station_code,  # Use code as name
        'station_code': station_code,
        'state': '',
        'zone': '',
        'division': '',
        'category': 'UNKNOWN',
        'tier': tier_info['tier'],
        'min_transfer_time': tier_info['min_transfer_time'],
        'train_count': train_count,
        'passengers_footfall': 0,
        'revenue': 0,
        'data_source': 'frequency'
      }

    station_metadata[station_code] = metadata

  print(f"Processed {len(station_metadata)} stations")
  print(f"  • {matched_with_official} matched with official data")
  print(f"  • {classified_by_frequency} classified by train frequency")
  print()

  return station_metadata


def analyze_metadata(station_metadata):
  """Analyze and display statistics about the metadata"""
  print("STATION METADATA ANALYSIS")
  print()

  # Distribution by tier
  tier_counts = Counter(meta['tier'] for meta in station_metadata.values())

  print("Distribution by Tier:")
  for tier, count in tier_counts.most_common():
    pct = (count / len(station_metadata)) * 100
    print(f"  {tier:25} : {count:4} stations ({pct:5.1f}%)")

  # Distribution by transfer time
  print()
  print("Distribution by Transfer Time:")
  transfer_counts = Counter(meta['min_transfer_time'] for meta in station_metadata.values())
  for time in sorted(transfer_counts.keys()):
    count = transfer_counts[time]
    pct = (count / len(station_metadata)) * 100
    print(f"  {time:3} minutes : {count:4} stations ({pct:5.1f}%)")

  # Top stations by train count
  print()
  print("Top 20 Stations by Train Count:")
  sorted_by_trains = sorted(
    station_metadata.values(),
    key=lambda x: x['train_count'],
    reverse=True
  )

  for i, meta in enumerate(sorted_by_trains[:20], 1):
    tier_symbol = {
      'PREMIUM_TERMINAL': '⭐',
      'METRO_TERMINAL': '🏢',
      'MAJOR_JUNCTION': '🚉',
      'SMALL_STATION': '🚏'
    }.get(meta['tier'], '•')

    print(f"{i:2}. {tier_symbol} {meta['station_code']:6} - {meta['station_name']:30} "
          f"| {meta['train_count']:3} trains | {meta['min_transfer_time']:2} min | {meta['tier']}")

  # Validate major junctions
  print()
  print("Major Junction Validation:")
  print("-" * 70)
  for junction in MAJOR_JUNCTIONS:
    if junction in station_metadata:
      meta = station_metadata[junction]
      status = "✓" if meta['tier'] in ['METRO_TERMINAL', 'MAJOR_JUNCTION', 'PREMIUM_TERMINAL'] else "⚠"
      print(f"{status} {junction:6} : {meta['train_count']:3} trains | "
            f"{meta['min_transfer_time']:2} min | {meta['tier']}")
    else:
      print(f"✗ {junction:6} : NOT FOUND in dataset")

  # Data source breakdown
  print("Data Source Breakdown:")
  source_counts = Counter(meta['data_source'] for meta in station_metadata.values())
  for source, count in source_counts.items():
    pct = (count / len(station_metadata)) * 100
    print(f"  {source:12} : {count:4} stations ({pct:5.1f}%)")

  # Overall stats
  print()
  print("Overall Statistics:")
  print(f"  Total stations: {len(station_metadata)}")

  total_trains = sum(meta['train_count'] for meta in station_metadata.values())
  print(f"  Total train-station connections: {total_trains}")

  avg_trains = total_trains / len(station_metadata)
  print(f"  Average trains per station: {avg_trains:.1f}")

  has_footfall = sum(1 for meta in station_metadata.values() if meta['passengers_footfall'] > 0)
  print(f"  Stations with footfall data: {has_footfall} ({has_footfall/len(station_metadata)*100:.1f}%)")


def save_metadata(station_metadata):
  """Save metadata to JSON file"""
  print()
  print("SAVING OUTPUT")


  os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

  with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(station_metadata, f, indent=2, ensure_ascii=False)

  print(f"Saved {len(station_metadata)} stations to:")
  print(f"  {OUTPUT_PATH}")
  print(f"File size: {os.path.getsize(OUTPUT_PATH) / 1024:.1f} KB")

  # Show sample
  print()
  print("Sample metadata (first 2 stations):")
  for code, meta in list(station_metadata.items())[:2]:
    print(f"\n{code}:")
    print(json.dumps(meta, indent=2))


def main():
  """Main execution function"""
  print()
  print("STATION METADATA BUILDER")
  print()

  try:
    # Load data
    stop_routes, scraped_stations = load_data()
    if not stop_routes:
      return

    # Build metadata
    station_metadata = build_station_metadata(stop_routes, scraped_stations)

    # Analyze
    analyze_metadata(station_metadata)

    # Save
    save_metadata(station_metadata)

    print()
    print("STATION METADATA COMPLETE!")

  except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()


if __name__ == "__main__":
  main()
