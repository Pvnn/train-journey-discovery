"""
Test 1: Data Loader Unit Test
Tests that data_loader successfully loads all JSON files.
"""

import sys
import os
# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
  sys.path.insert(0, project_root)

def test_data_loader():
  print("TEST 1: Data Loader")

  try:
    from backend.utils.data_loader import data_loader

    # Test 1.1: Check data_loader initialized
    print("\n✓ Test 1.1: Data loader initialized")
    assert data_loader is not None, "data_loader should not be None"

    # Test 1.2: Get stops data
    print("✓ Test 1.2: Getting stops data...")
    stops = data_loader.get_stops()
    assert isinstance(stops, dict), "Stops should be a dictionary"
    print(f"  → {len(stops)} stops loaded")

    # Test 1.3: Get routes data
    print("✓ Test 1.3: Getting routes data...")
    routes = data_loader.get_routes()
    assert isinstance(routes, dict), "Routes should be a dictionary"
    print(f"  → {len(routes)} routes loaded")

    # Test 1.4: Get stop_times data
    print("✓ Test 1.4: Getting stop_times data...")
    stop_times = data_loader.get_stop_times()
    assert isinstance(stop_times, list), "Stop times should be a list"
    print(f"  → {len(stop_times)} stop times loaded")

    # Test 1.5: Get train metadata
    print("✓ Test 1.5: Getting train metadata...")
    train_metadata = data_loader.get_train_metadata()
    assert isinstance(train_metadata, dict), "Train metadata should be a dictionary"
    print(f"  → {len(train_metadata)} trains loaded")

    # Test 1.6: Get station metadata
    print("✓ Test 1.6: Getting station metadata...")
    station_metadata = data_loader.get_station_metadata()
    assert isinstance(station_metadata, dict), "Station metadata should be a dictionary"
    print(f"  → {len(station_metadata)} stations loaded")

    # Test 1.7: Get stop_routes
    print("✓ Test 1.7: Getting stop_routes...")
    stop_routes = data_loader.get_stop_routes()
    assert isinstance(stop_routes, dict), "Stop routes should be a dictionary"
    print(f"  → {len(stop_routes)} stop-route mappings loaded")

    # Test 1.8: Get stop_routes_mapping
    print("✓ Test 1.8: Getting stop_routes_mapping...")
    stop_routes_mapping = data_loader.get_stop_routes_mapping()
    assert isinstance(stop_routes_mapping, dict), "Stop routes mapping should be a dictionary"
    print(f"  → {len(stop_routes_mapping)} route mappings loaded")

    # Test 1.9: Test utility methods
    print("✓ Test 1.9: Testing utility methods...")
    first_stop_code = list(stops.keys())[0] if stops else None
    if first_stop_code:
      stop_info = data_loader.get_stop_by_code(first_stop_code)
      assert stop_info is not None, f"Should find stop {first_stop_code}"
      print(f"  → get_stop_by_code('{first_stop_code}') works")

    first_route_id = list(routes.keys())[0] if routes else None
    if first_route_id:
      route_info = data_loader.get_route_by_id(first_route_id)
      assert route_info is not None, f"Should find route {first_route_id}"
      print(f"  → get_route_by_id('{first_route_id}') works")

    print("\nALL DATA LOADER TESTS PASSED!")
    return True

  except Exception as e:
    print(f"\nDATA LOADER TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    return False

if __name__ == "__main__":
  test_data_loader()
