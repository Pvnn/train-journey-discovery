"""
Test 4: Flask API Integration Test
Tests complete Flask API endpoint with all layers.
"""

import sys
import os
# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
  sys.path.insert(0, project_root)

def test_flask_api():
  print("TEST 4: Flask API Integration")

  try:
    from flask import Flask, request, jsonify
    from backend.api.schemas import (
      journey_request_schema,
      create_success_response,
      create_error_response
    )
    from backend.services.journey_service import (
      search_journeys,
      StationNotFoundError,
      NoRoutesFoundError,
      AlgorithmError
    )
    from marshmallow import ValidationError
    from datetime import date, timedelta

    # Create Flask app for testing
    app = Flask(__name__)

    @app.route('/api/journey/search', methods=['POST'])
    def api_search_journeys():
      try:
        # Validate with schema
        data = journey_request_schema.load(request.json)

        # Call journey service
        journeys = search_journeys(
          source=data['source'],
          destination=data['destination'],
          date=data['date'],
          departure_time=data['departure_time'],
          max_transfers=data['max_transfers']
        )

        # Return success response
        response = create_success_response(journeys, data)
        return jsonify(response), 200

      except ValidationError as e:
        return jsonify(create_error_response(400, "Invalid request", e.messages)), 400
      except StationNotFoundError as e:
        return jsonify(create_error_response(404, str(e))), 404
      except NoRoutesFoundError as e:
        return jsonify(create_error_response(404, str(e))), 404
      except AlgorithmError as e:
        return jsonify(create_error_response(500, str(e))), 500
      except Exception as e:
        return jsonify(create_error_response(500, "Internal error", str(e))), 500

    # Create test client
    client = app.test_client()

    # Get test stops
    from backend.utils.data_loader import data_loader
    stops = data_loader.get_stops()
    stop_codes = list(stops.keys())[:2]

    if len(stop_codes) < 2:
      print("Need at least 2 stops for testing")
      return False

    # Test 4.1: Valid request
    print("\n✓ Test 4.1: Valid API request")
    response = client.post('/api/journey/search', 
      json={
        "source": stop_codes[0],
        "destination": stop_codes[1],
        "date": (date.today() + timedelta(days=2)).strftime('%Y-%m-%d'),
        "departure_time": "10:00",
        "max_transfers": 3
      },
      content_type='application/json'
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.get_json()
    assert 'journeys' in data
    assert 'metadata' in data
    assert 'query' in data['metadata']
    assert 'results_count' in data['metadata']
    print(f"  → Status: 200 OK")
    print(f"  → Found {data['metadata']['results_count']} journeys")
    print(f"  → time_source: {data['metadata']['query'].get('time_source')}")

    # Test 4.2: Missing departure_time (should auto-fill)
    print("\n✓ Test 4.2: Request without departure_time")
    response = client.post('/api/journey/search',
      json={
        "source": stop_codes[0],
        "destination": stop_codes[1],
        "date": (date.today() + timedelta(days=5)).strftime('%Y-%m-%d')
      },
      content_type='application/json'
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['metadata']['query']['departure_time'] == "00:00"
    assert data['metadata']['query']['time_source'] == "start_of_day"
    print(f"  → Auto-filled departure_time: 00:00")

    # Test 4.3: Invalid station (404)
    print("\n✓ Test 4.3: Invalid station returns 404")
    response = client.post('/api/journey/search',
      json={
        "source": "INVALID",
        "destination": stop_codes[1],
        "date": (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
      },
      content_type='application/json'
    )

    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data
    print(f"  → Status: 404 Not Found")
    print(f"  → Error: {data['error']['message'][:50]}...")

    # Test 4.4: Validation error (400)
    print("\n✓ Test 4.4: Validation error returns 400")
    response = client.post('/api/journey/search',
      json={
        "source": "NDLS",
        "destination": "NDLS",  # Same as source
        "date": (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
      },
      content_type='application/json'
    )

    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    print(f"  → Status: 400 Bad Request")
    print(f"  → Error: {data['error']['message'][:50]}...")

    # Test 4.5: Past date (400)
    print("\n✓ Test 4.5: Past date returns 400")
    response = client.post('/api/journey/search',
      json={
        "source": stop_codes[0],
        "destination": stop_codes[1],
        "date": (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
      },
      content_type='application/json'
    )

    assert response.status_code == 400
    print(f"  → Status: 400 Bad Request")

    print("\nALL FLASK API TESTS PASSED!")
    return True

  except Exception as e:
    print(f"\nFLASK API TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    return False

if __name__ == "__main__":
  test_flask_api()
