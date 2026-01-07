"""
Test 3: Journey Service Integration Test
Tests journey_service with Mock MCRaptor.
"""

import sys
import os
# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
  sys.path.insert(0, project_root)

def test_journey_service():
  print("TEST 3: Journey Service with Mock MCRaptor")

  try:
    from backend.services.journey_service import (
      search_journeys,
      StationNotFoundError,
      NoRoutesFoundError
    )
    from datetime import date, timedelta

    # Get first two stops from data_loader for testing
    from backend.utils.data_loader import data_loader
    stops = data_loader.get_stops()
    stop_codes = list(stops.keys())[:2]

    if len(stop_codes) < 2:
      print("Need at least 2 stops in data for testing")
      return False

    source_code = stop_codes[0]
    dest_code = stop_codes[1]

    print(f"\nUsing test stops: {source_code} → {dest_code}")

    # Test 3.1: Successful search
    print("\n✓ Test 3.1: Successful journey search")
    future_date = (date.today() + timedelta(days=3)).strftime('%Y-%m-%d')

    journeys = search_journeys(
      source=source_code,
      destination=dest_code,
      date=future_date,
      departure_time="10:00",
      max_transfers=4
    )

    assert isinstance(journeys, list), "Should return a list"
    assert len(journeys) > 0, "Should find at least one journey"
    print(f"  → Found {len(journeys)} journey options")

    # Verify journey structure
    first_journey = journeys[0]
    assert 'segments' in first_journey
    assert 'total_time' in first_journey
    assert 'total_transfers' in first_journey
    assert 'total_fare' in first_journey
    assert 'comfort_score' in first_journey
    print("  → Journey structure is correct")

    # Test 3.2: Invalid source station
    print("\n✓ Test 3.2: Invalid source station")
    try:
      search_journeys(
        source="INVALID",
        destination=dest_code,
        date=future_date,
        departure_time="10:00"
      )
      print("Should have raised StationNotFoundError")
      return False
    except StationNotFoundError as e:
      print(f"  → Correctly raised StationNotFoundError: {str(e)[:50]}...")

    # Test 3.3: Invalid destination station
    print("\n✓ Test 3.3: Invalid destination station")
    try:
      search_journeys(
        source=source_code,
        destination="INVALID",
        date=future_date,
        departure_time="10:00"
      )
      print("Should have raised StationNotFoundError")
      return False
    except StationNotFoundError as e:
      print(f"  → Correctly raised StationNotFoundError: {str(e)[:50]}...")

    print("\nALL JOURNEY SERVICE TESTS PASSED!")
    return True

  except Exception as e:
    print(f"\nJOURNEY SERVICE TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    return False

if __name__ == "__main__":
  test_journey_service()
