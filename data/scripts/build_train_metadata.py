"""
Purpose: Build comprehensive train metadata for RAPTOR algorithm
Inputs: 
  - data/raw/PASS-TRAINS.json (Passenger trains)
  - data/raw/EXP-TRAINS.json (Express trains)
  - data/raw/SF-TRAINS.json (Superfast trains)
Output: 
  - data/processed/train_metadata.json

Classification Strategy:
  Use train names + file source to determine:
  - Class (AC, Sleeper, General)
  - Comfort score (1-10 scale)
  - Base fare per km (₹/km)
  - Train type category
"""

import json
import os
import re
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.dirname(SCRIPT_DIR)
RAW_DIR = os.path.join(DATA_DIR, "raw")
OUTPUT_PATH = os.path.join(DATA_DIR, "processed", "train_metadata.json")

INPUT_FILES = {
  'PASS': os.path.join(RAW_DIR, "PASS-TRAINS.json"),
  'EXP': os.path.join(RAW_DIR, "EXP-TRAINS.json"),
  'SF': os.path.join(RAW_DIR, "SF-TRAINS.json")
}

# Train classification rules
# Priority order: Higher priority patterns checked first
TRAIN_CLASSIFICATIONS = [
  # Premium AC trains
  {
    'patterns': [
      r'SHATABDI',
      r'RAJDHANI',
      r'VANDE\s+BHARAT',
      r'TEJAS'
    ],
    'category': 'PREMIUM_AC',
    'class_type': 'AC',
    'comfort_score': 10,
    'base_fare_per_km': 2.0,
    'description': 'Premium AC trains with highest comfort'
  },

  # High-end AC trains
  {
    'patterns': [
      r'DURONTO',
      r'GARIB\s+RATH',
      r'HUMSAFAR'
    ],
    'category': 'AC_EXPRESS',
    'class_type': 'AC',
    'comfort_score': 8,
    'base_fare_per_km': 1.3,
    'description': 'AC express trains with good comfort'
  },

  # Superfast trains (from SF file or name)
  {
    'patterns': [
      r'SF',
      r'SUPERFAST',
      r'SUF',
      r'SPL.*SF',
      r'SFTIAS'
    ],
    'category': 'SUPERFAST',
    'class_type': 'Sleeper',
    'comfort_score': 6,
    'base_fare_per_km': 0.6,
    'description': 'Superfast trains with sleeper class'
  },

  # Regular Express trains
  {
    'patterns': [
      r'EXPRESS',
      r'EXP',
      r'EXPRS',
      r'LINK\s+EXP'
    ],
    'category': 'EXPRESS',
    'class_type': 'Sleeper',
    'comfort_score': 5,
    'base_fare_per_km': 0.5,
    'description': 'Regular express trains'
  },

  # Mail trains
  {
    'patterns': [
      r'MAIL',
      r'ML'
    ],
    'category': 'MAIL',
    'class_type': 'Sleeper',
    'comfort_score': 5,
    'base_fare_per_km': 0.5,
    'description': 'Mail trains'
  },

  # Passenger trains
  {
    'patterns': [
      r'PASSENGER',
      r'PASS',
      r'PASSEN',
      r'LOCAL',
      r'MEMU',
      r'DEMU'
    ],
    'category': 'PASSENGER',
    'class_type': 'General',
    'comfort_score': 3,
    'base_fare_per_km': 0.3,
    'description': 'Passenger and local trains'
  },

  # Special trains
  {
    'patterns': [
      r'SPL',
      r'SPECIAL',
      r'FESTIVAL\s+SPL',
      r'HOLIDAY\s+SPL'
    ],
    'category': 'SPECIAL',
    'class_type': 'Sleeper',
    'comfort_score': 5,
    'base_fare_per_km': 0.5,
    'description': 'Special trains'
  }
]

# Default classification for unmatched trains
DEFAULT_CLASSIFICATION = {
  'category': 'EXPRESS',
  'class_type': 'Sleeper',
  'comfort_score': 5,
  'base_fare_per_km': 0.5,
  'description': 'Default express classification'
}

def load_all_trains():
  """Load trains from all three files"""
  print("LOADING TRAIN DATA")

  all_trains = []
  file_counts = {}

  for file_type, file_path in INPUT_FILES.items():
    if os.path.exists(file_path):
      try:
        with open(file_path, 'r', encoding='utf-8') as f:
          trains = json.load(f)

        # Add file source to each train
        for train in trains:
          train['_source_file'] = file_type
          all_trains.append(train)

        file_counts[file_type] = len(trains)
        print(f"✓ Loaded {len(trains):4} trains from {file_type}-TRAINS.json")

      except Exception as e:
        print(f"Error loading {file_path}: {e}")
    else:
      print(f"File not found: {file_path}")

  print()
  print(f"Total trains loaded: {len(all_trains)}")
  print()

  return all_trains, file_counts


def classify_train(train):
  """
  Classify a train based on its name and source file.

  Args:
    train: Train dictionary with trainName and _source_file

  Returns:
    Classification dictionary with category, class, comfort, fare
  """
  train_name = train.get('trainName', '').upper()
  source_file = train.get('_source_file', '')

  # Try each classification rule in order
  for rule in TRAIN_CLASSIFICATIONS:
    for pattern in rule['patterns']:
      if re.search(pattern, train_name):
        return {
          'category': rule['category'],
          'class_type': rule['class_type'],
          'comfort_score': rule['comfort_score'],
          'base_fare_per_km': rule['base_fare_per_km'],
          'description': rule['description'],
          'matched_pattern': pattern
        }

  # Source file based classification as fallback
  if source_file == 'SF':
    return {
      'category': 'SUPERFAST',
      'class_type': 'Sleeper',
      'comfort_score': 6,
      'base_fare_per_km': 0.6,
      'description': 'Superfast train (by file)',
      'matched_pattern': 'SF-file'
    }
  elif source_file == 'PASS':
    return {
      'category': 'PASSENGER',
      'class_type': 'General',
      'comfort_score': 3,
      'base_fare_per_km': 0.3,
      'description': 'Passenger train (by file)',
      'matched_pattern': 'PASS-file'
    }
  elif source_file == 'EXP':
    return {
      'category': 'EXPRESS',
      'class_type': 'Sleeper',
      'comfort_score': 5,
      'base_fare_per_km': 0.5,
      'description': 'Express train (by file)',
      'matched_pattern': 'EXP-file'
    }

  # Ultimate fallback
  return {
    **DEFAULT_CLASSIFICATION,
    'matched_pattern': 'default'
  }


def build_train_metadata(trains):
  """
  Build comprehensive metadata for all trains.

  Args:
    trains: List of train dictionaries

  Returns:
    Dictionary mapping train_number to metadata
  """
  print("BUILDING TRAIN METADATA")
  print()

  train_metadata = {}
  classification_counts = Counter()

  for train in trains:
    train_number = train.get('trainNumber', 'UNKNOWN')
    train_name = train.get('trainName', 'Unknown')

    # Classify the train
    classification = classify_train(train)
    classification_counts[classification['category']] += 1

    # Build metadata entry
    metadata = {
      'train_number': train_number,
      'train_name': train_name,
      'category': classification['category'],
      'class_type': classification['class_type'],
      'comfort_score': classification['comfort_score'],
      'base_fare_per_km': classification['base_fare_per_km'],
      'description': classification['description'],
      'source_file': train.get('_source_file', 'UNKNOWN'),

      # Additional useful fields
      'total_stops': len(train.get('schedule', [])),
      'distance_km': train.get('distance', 0),

      # Keep original schedule for reference (optional, can be removed if too large)
      # 'schedule': train.get('schedule', [])
    }

    train_metadata[train_number] = metadata

  print(f"Processed {len(train_metadata)} trains")
  print()

  return train_metadata, classification_counts


def analyze_metadata(train_metadata, classification_counts, file_counts):
  """Analyze and display statistics about train metadata"""
  print("TRAIN METADATA ANALYSIS")
  print()

  # Distribution by category
  print("Distribution by Category:")
  total = sum(classification_counts.values())
  for category, count in classification_counts.most_common():
    pct = (count / total) * 100
    print(f"  {category:20} : {count:5} trains ({pct:5.1f}%)")

  # Distribution by class type
  print()
  print("Distribution by Class Type:")
  class_counts = Counter(meta['class_type'] for meta in train_metadata.values())
  for class_type, count in class_counts.most_common():
    pct = (count / total) * 100
    print(f"  {class_type:20} : {count:5} trains ({pct:5.1f}%)")

  # Distribution by comfort score
  print()
  print("Distribution by Comfort Score:")
  comfort_counts = Counter(meta['comfort_score'] for meta in train_metadata.values())
  for score in sorted(comfort_counts.keys(), reverse=True):
    count = comfort_counts[score]
    pct = (count / total) * 100
    bars = '█' * int(pct / 2)
    print(f"  Score {score:2}/10 : {count:5} trains ({pct:5.1f}%) {bars}")

  # Distribution by fare
  print()
  print("Distribution by Base Fare (₹/km):")
  fare_counts = Counter(meta['base_fare_per_km'] for meta in train_metadata.values())
  for fare in sorted(fare_counts.keys(), reverse=True):
    count = fare_counts[fare]
    pct = (count / total) * 100
    print(f"  ₹{fare:4.1f}/km : {count:5} trains ({pct:5.1f}%)")

  print("Distribution by Source File:")
  source_counts = Counter(meta['source_file'] for meta in train_metadata.values())
  for source, count in source_counts.most_common():
    pct = (count / total) * 100
    print(f"  {source:10} : {count:5} trains ({pct:5.1f}%)")


  print()
  print("Sample Trains by Category:")

  samples_shown = set()
  for category in classification_counts.keys():
    category_trains = [
      (num, meta) for num, meta in train_metadata.items()
      if meta['category'] == category
    ]

    if category_trains:
      # Show first train of this category
      train_num, meta = category_trains[0]

      comfort_icon = {
        10: '⭐⭐⭐',
        8: '⭐⭐',
        6: '⭐',
        5: '○',
        3: '·'
      }.get(meta['comfort_score'], '○')

      print(f"  {comfort_icon} [{meta['category']:15}] "
            f"{train_num:6} - {meta['train_name'][:40]:40} | "
            f"₹{meta['base_fare_per_km']:.1f}/km")

  # Overall statistics
  print()
  print("Overall Statistics:")
  print("-" * 70)
  print(f"  Total trains: {len(train_metadata)}")

  avg_comfort = sum(m['comfort_score'] for m in train_metadata.values()) / len(train_metadata)
  print(f"  Average comfort score: {avg_comfort:.1f}/10")

  avg_fare = sum(m['base_fare_per_km'] for m in train_metadata.values()) / len(train_metadata)
  print(f"  Average base fare: ₹{avg_fare:.2f}/km")

  avg_stops = sum(m['total_stops'] for m in train_metadata.values()) / len(train_metadata)
  print(f"  Average stops per train: {avg_stops:.1f}")

  total_distance = sum(m['distance_km'] for m in train_metadata.values())
  print(f"  Total network distance: {total_distance:,.0f} km")


def save_metadata(train_metadata):
  """Save metadata to JSON file"""
  print("SAVING OUTPUT")

  os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

  with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    json.dump(train_metadata, f, indent=2, ensure_ascii=False)

  print(f"Saved {len(train_metadata)} trains to:")
  print(f"  {OUTPUT_PATH}")
  print(f"File size: {os.path.getsize(OUTPUT_PATH) / 1024:.1f} KB")

  # Show sample
  print("Sample metadata (first 3 trains):")
  for i, (train_num, meta) in enumerate(list(train_metadata.items())[:3], 1):
    print(f"\n{i}. Train {train_num}:")
    print(json.dumps(meta, indent=2))


def main():
  """Main execution function"""
  print("TRAIN METADATA BUILDER")

  try:
    # Load data
    trains, file_counts = load_all_trains()
    if not trains:
      print("No trains loaded. Check input files.")
      return

    # Build metadata
    train_metadata, classification_counts = build_train_metadata(trains)

    # Analyze
    analyze_metadata(train_metadata, classification_counts, file_counts)

    # Save
    save_metadata(train_metadata)

    print()
    print("TRAIN METADATA COMPLETE!")


  except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()


if __name__ == "__main__":
  main()
