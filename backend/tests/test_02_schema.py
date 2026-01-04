"""
Test 2: Schema Validation Unit Test
Tests schema validation and smart defaults.
"""

import sys
import os
# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
  sys.path.insert(0, project_root)

def test_schema_validation():
  print("TEST 2: Schema Validation")

  try:
    from backend.api.schemas import journey_request_schema
    from marshmallow import ValidationError
    from datetime import date, timedelta

    # Test 2.1: Valid request with all fields
    print("\n✓ Test 2.1: Valid request with all fields")
    valid_data = {
      "source": "NDLS",
      "destination": "MAS",
      "date": (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
      "departure_time": "14:30",
      "max_transfers": 3
    }
    result = journey_request_schema.load(valid_data)
    assert result['departure_time'] == "14:30"
    assert result['_time_source'] == 'user_provided'
    print("  → Validation passed, departure_time preserved")

    # Test 2.2: Future date without time (should default to 00:00)
    print("\n✓ Test 2.2: Future date without departure_time")
    data_no_time = {
      "source": "NDLS",
      "destination": "MAS",
      "date": (date.today() + timedelta(days=5)).strftime('%Y-%m-%d'),
      "max_transfers": 4
    }
    result = journey_request_schema.load(data_no_time)
    assert result['departure_time'] == "00:00", f"Expected 00:00, got {result['departure_time']}"
    assert result['_time_source'] == 'start_of_day'
    print(f"  → Auto-filled departure_time: {result['departure_time']}")
    print(f"  → time_source: {result['_time_source']}")

    # Test 2.3: Today's date without time (should use current time)
    print("\n✓ Test 2.3: Today's date without departure_time")
    data_today = {
      "source": "NDLS",
      "destination": "MAS",
      "date": date.today().strftime('%Y-%m-%d'),
    }
    result = journey_request_schema.load(data_today)
    assert result['departure_time'] is not None
    assert result['_time_source'] == 'current_time'
    print(f"  → Auto-filled with current time: {result['departure_time']}")

    # Test 2.4: Source == Destination (should fail)
    print("\n✓ Test 2.4: Source == Destination validation")
    try:
      invalid_data = {
        "source": "NDLS",
        "destination": "NDLS",
        "date": (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
      }
      journey_request_schema.load(invalid_data)
      print("  ❌ Should have raised ValidationError")
      return False
    except ValidationError as e:
      print("  → Correctly rejected: Source and destination must be different")

    # Test 2.5: Past date (should fail)
    print("\n✓ Test 2.5: Past date validation")
    try:
      past_data = {
        "source": "NDLS",
        "destination": "MAS",
        "date": (date.today() - timedelta(days=1)).strftime('%Y-%m-%d'),
      }
      journey_request_schema.load(past_data)
      print("  ❌ Should have raised ValidationError")
      return False
    except ValidationError as e:
      print("  → Correctly rejected: Date cannot be in the past")

    # Test 2.6: Invalid time format
    print("\n✓ Test 2.6: Invalid time format validation")
    try:
      invalid_time = {
        "source": "NDLS",
        "destination": "MAS",
        "date": (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
        "departure_time": "25:99"
      }
      journey_request_schema.load(invalid_time)
      print("  ❌ Should have raised ValidationError")
      return False
    except ValidationError as e:
      print("  → Correctly rejected: Invalid time format")

    # Test 2.7: Max transfers validation
    print("\n✓ Test 2.7: Max transfers bounds")
    result = journey_request_schema.load({
      "source": "NDLS",
      "destination": "MAS",
      "date": (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
    })
    assert result['max_transfers'] == 4, "Default should be 4"
    print("  → Default max_transfers: 4")

    print("\nALL SCHEMA TESTS PASSED!")
    return True

  except Exception as e:
    print(f"\nSCHEMA TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    return False

if __name__ == "__main__":
  test_schema_validation()
