from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
import time

from api.schemas import (
  journey_request_schema,
  create_error_response,
  create_success_response
)
from services.journey_service import (
  search_journeys,
  sort_journeys,
  apply_limit,
  StationNotFoundError,
  NoRoutesFoundError,
  AlgorithmError,
  JourneyServiceError
)
from services.station_service import (
  get_all_stations,
  search_stations,
  get_station_details,
  format_station_summary,
  format_station_detail
)

# Create Blueprint for API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/search', methods=['POST'])
def search_journey():
  """
  POST /api/search - Search for journeys between two stations.

  Request Body (JSON):
    {
      "source": "NDLS",              # Required: Source station code
      "destination": "MAS",          # Required: Destination station code
      "date": "2026-01-15",          # Required: Journey date (YYYY-MM-DD)
      "departure_time": "14:30",     # Optional: Departure time (HH:MM)
      "max_transfers": 4             # Optional: Max transfers (default: 4)
    }

  Query Parameters (Optional):
    - sort_by: "time"|"transfers"|"comfort"|"fare"|"quality" (default: "quality")
    - order: "asc"|"desc" (default: "asc")
    - limit: int (default: 10, max: 50)

  Example:
    POST /api/search?sort_by=time&order=asc&limit=5

  Response (200 OK):
    {
      "journeys": [...],
      "metadata": {
        "query": {...},
        "results_count": 5,
        "total_found": 12,
        "sort_by": "time",
        "order": "asc",
        "limit": 5
      }
    }

  Error Responses:
    - 400: Validation errors (invalid input)
    - 404: No routes found or station not found
    - 500: Internal server error (algorithm failure)
  """
  start_time = time.time()

  # Get query parameters for sorting and filtering
  sort_by = request.args.get('sort_by', 'quality')
  order = request.args.get('order', 'asc')
  limit = request.args.get('limit', '10')

  # Log incoming request
  print(f"[POST /api/search] Request body: {request.get_json()}")
  print(f"[POST /api/search] Query params: sort_by={sort_by}, order={order}, limit={limit}")

  try:
    # Step 1: Validate query parameters
    # Validate sort_by
    valid_sort_options = ['quality', 'time', 'transfers', 'comfort', 'fare']
    if sort_by not in valid_sort_options:
      error_response = create_error_response(
        code=400,
        message=f"Invalid sort_by parameter. Must be one of: {', '.join(valid_sort_options)}",
        details={"sort_by": [f"Invalid value: {sort_by}"]}
      )
      return jsonify(error_response), 400

    # Validate order
    if order not in ['asc', 'desc']:
      error_response = create_error_response(
        code=400,
        message="Invalid order parameter. Must be 'asc' or 'desc'",
        details={"order": [f"Invalid value: {order}"]}
      )
      return jsonify(error_response), 400

    # Validate limit
    try:
      limit_int = int(limit)
      if limit_int < 1:
        raise ValueError("Limit must be at least 1")
      if limit_int > 50:
        raise ValueError("Limit cannot exceed 50")
    except ValueError as e:
      error_response = create_error_response(
        code=400,
        message=f"Invalid limit parameter: {str(e)}",
        details={"limit": [f"Must be an integer between 1 and 50"]}
      )
      return jsonify(error_response), 400

    # Step 2: Get and validate JSON body
    json_data = request.get_json()

    if not json_data:
      error_response = create_error_response(
        code=400,
        message="Request body must be valid JSON",
        details={"error": "No JSON data provided"}
      )
      print(f"[POST /api/search] ERROR 400: No JSON data provided")
      return jsonify(error_response), 400

    # Step 3: Validate request using journey_request_schema
    try:
      validated_data = journey_request_schema.load(json_data)
      print(f"[POST /api/search] Validated data: {validated_data}")
    except ValidationError as err:
      # Return field-level validation errors
      error_response = create_error_response(
        code=400,
        message="Invalid request data",
        details=err.messages
      )
      print(f"[POST /api/search] ERROR 400: Validation error - {err.messages}")
      return jsonify(error_response), 400

    # Step 4: Call search_journeys() with validated parameters
    try:
      journeys = search_journeys(
        source=validated_data['source'],
        destination=validated_data['destination'],
        date=validated_data['date'],
        departure_time=validated_data['departure_time'],
        max_transfers=validated_data.get('max_transfers', 4)
      )

      # Store total count before filtering
      total_found = len(journeys)

      # Step 5: Apply sorting
      journeys = sort_journeys(journeys, sort_by=sort_by, order=order)

      # Step 6: Apply limit
      journeys = apply_limit(journeys, limit=limit_int)

      # Step 7: Format success response with enhanced metadata
      response_data = create_success_response(
        journeys=journeys,
        query_params=validated_data
      )

      # Add sorting and filtering metadata
      response_data['metadata']['total_found'] = total_found
      response_data['metadata']['sort_by'] = sort_by
      response_data['metadata']['order'] = order
      response_data['metadata']['limit'] = limit_int
      response_data['metadata']['returned_count'] = len(journeys)

      # Calculate processing duration
      duration_ms = (time.time() - start_time) * 1000
      print(f"[POST /api/search] SUCCESS 200: Found {total_found} journeys, "
            f"returned {len(journeys)} after limit - Duration: {duration_ms:.2f}ms")

      return jsonify(response_data), 200

    except StationNotFoundError as err:
      # Station not found - return 404
      error_response = create_error_response(
        code=404,
        message=str(err),
        details={"error_type": "StationNotFoundError"}
      )
      duration_ms = (time.time() - start_time) * 1000
      print(f"[POST /api/search] ERROR 404: {str(err)} - Duration: {duration_ms:.2f}ms")
      return jsonify(error_response), 404

    except NoRoutesFoundError as err:
      # No routes found - return 404
      error_response = create_error_response(
        code=404,
        message=str(err),
        details={"error_type": "NoRoutesFoundError"}
      )
      duration_ms = (time.time() - start_time) * 1000
      print(f"[POST /api/search] ERROR 404: {str(err)} - Duration: {duration_ms:.2f}ms")
      return jsonify(error_response), 404

    except AlgorithmError as err:
      # MC-RAPTOR algorithm failure - return 500
      error_response = create_error_response(
        code=500,
        message="Internal server error: Algorithm failed",
        details={"error": str(err), "error_type": "AlgorithmError"}
      )
      duration_ms = (time.time() - start_time) * 1000
      print(f"[POST /api/search] ERROR 500: Algorithm error - {str(err)} - Duration: {duration_ms:.2f}ms")
      return jsonify(error_response), 500

    except JourneyServiceError as err:
      # Generic service error - return 500
      error_response = create_error_response(
        code=500,
        message="Internal server error: Service failed",
        details={"error": str(err), "error_type": "JourneyServiceError"}
      )
      duration_ms = (time.time() - start_time) * 1000
      print(f"[POST /api/search] ERROR 500: Service error - {str(err)} - Duration: {duration_ms:.2f}ms")
      return jsonify(error_response), 500

  except Exception as err:
    # Catch-all for unexpected errors
    error_response = create_error_response(
      code=500,
      message="Internal server error: Unexpected error occurred",
      details={"error": str(err), "error_type": type(err).__name__}
    )
    duration_ms = (time.time() - start_time) * 1000
    print(f"[POST /api/search] ERROR 500: Unexpected error - {str(err)} - Duration: {duration_ms:.2f}ms")
    return jsonify(error_response), 500


# ============================================================================
# STATION LOOKUP ENDPOINTS
# ============================================================================

@api_bp.route('/stations/search', methods=['GET'])
def search_stations_endpoint():
  """
  GET /api/stations/search?q=<search_term> - Search for stations.

  Query Parameters:
    - q: Search term (station name or code) - Required

  Logic:
    - Station code: Prefix match (case-insensitive)
    - Station name: Partial match (case-insensitive)
    - Returns max 10 results

  Response (200 OK):
    [
      {
        "stop_id": 1,
        "stop_code": "NDLS",
        "stop_name": "New Delhi",
        "zone": "NR"
      },
      ...
    ]

  Error Responses:
    - 400: Missing or invalid query parameter
  """
  start_time = time.time()

  query = request.args.get('q', '').strip()

  print(f"[GET /api/stations/search] Query: q={query}")

  # Validate query parameter
  if not query:
    error_response = create_error_response(
      code=400,
      message="Missing required query parameter 'q'",
      details={"q": ["Search term is required"]}
    )
    print(f"[GET /api/stations/search] ERROR 400: Missing query parameter")
    return jsonify(error_response), 400

  if len(query) < 2:
    error_response = create_error_response(
      code=400,
      message="Search term must be at least 2 characters",
      details={"q": ["Minimum 2 characters required"]}
    )
    print(f"[GET /api/stations/search] ERROR 400: Query too short")
    return jsonify(error_response), 400

  try:
    # Search for stations
    results = search_stations(query, limit=10)

    # Format results as summary
    formatted_results = [format_station_summary(station) for station in results]

    duration_ms = (time.time() - start_time) * 1000
    print(f"[GET /api/stations/search] SUCCESS 200: Found {len(formatted_results)} stations - Duration: {duration_ms:.2f}ms")

    return jsonify(formatted_results), 200

  except Exception as err:
    error_response = create_error_response(
      code=500,
      message="Internal server error during station search",
      details={"error": str(err), "error_type": type(err).__name__}
    )
    duration_ms = (time.time() - start_time) * 1000
    print(f"[GET /api/stations/search] ERROR 500: {str(err)} - Duration: {duration_ms:.2f}ms")
    return jsonify(error_response), 500


@api_bp.route('/stations/<code>', methods=['GET'])
def get_station_by_code(code: str):
  """
  GET /api/stations/<code> - Get detailed station information.

  Path Parameters:
    - code: Station code (e.g., "NDLS", "MAS")

  Response (200 OK):
    {
      "stop_id": 1,
      "stop_code": "NDLS",
      "stop_name": "New Delhi",
      "zone": "NR",
      "tier": "A1",
      "category": "NSG-1",
      "min_transfer_time": 10,
      "routes_serving": 150,
      "route_ids": ["12301", "12302", ...]
    }

  Error Responses:
    - 404: Station not found
  """
  start_time = time.time()

  print(f"[GET /api/stations/{code}] Looking up station")

  try:
    # Get station details
    station = get_station_details(code)

    if not station:
      error_response = create_error_response(
        code=404,
        message=f"Station '{code}' not found",
        details={"station_code": code}
      )
      duration_ms = (time.time() - start_time) * 1000
      print(f"[GET /api/stations/{code}] ERROR 404: Station not found - Duration: {duration_ms:.2f}ms")
      return jsonify(error_response), 404

    # Format detailed response
    formatted_station = format_station_detail(station)

    duration_ms = (time.time() - start_time) * 1000
    print(f"[GET /api/stations/{code}] SUCCESS 200: Station found - Duration: {duration_ms:.2f}ms")

    return jsonify(formatted_station), 200

  except Exception as err:
    error_response = create_error_response(
      code=500,
      message="Internal server error during station lookup",
      details={"error": str(err), "error_type": type(err).__name__}
    )
    duration_ms = (time.time() - start_time) * 1000
    print(f"[GET /api/stations/{code}] ERROR 500: {str(err)} - Duration: {duration_ms:.2f}ms")
    return jsonify(error_response), 500


@api_bp.route('/stations', methods=['GET'])
def get_all_stations_endpoint():
  """
  GET /api/stations - Get all stations (cached).

  Query Parameters (Optional):
    - zone: Filter by zone (e.g., "WR", "CR", "ER")

  Response (200 OK):
    [
      {
        "stop_id": 1,
        "stop_code": "NDLS",
        "stop_name": "New Delhi",
        "zone": "NR"
      },
      ...
    ]

  Note: Response is cached for fast performance.
  """
  start_time = time.time()

  zone = request.args.get('zone', '').strip()

  print(f"[GET /api/stations] Zone filter: {zone if zone else 'None'}")

  try:
    # Get all stations (optionally filtered by zone)
    stations = get_all_stations(zone_filter=zone if zone else None)

    # Format as summary
    formatted_stations = [format_station_summary(station) for station in stations]

    duration_ms = (time.time() - start_time) * 1000
    print(f"[GET /api/stations] SUCCESS 200: Returned {len(formatted_stations)} stations - Duration: {duration_ms:.2f}ms")

    return jsonify(formatted_stations), 200

  except Exception as err:
    error_response = create_error_response(
      code=500,
      message="Internal server error during station retrieval",
      details={"error": str(err), "error_type": type(err).__name__}
    )
    duration_ms = (time.time() - start_time) * 1000
    print(f"[GET /api/stations] ERROR 500: {str(err)} - Duration: {duration_ms:.2f}ms")
    return jsonify(error_response), 500


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@api_bp.route('/health', methods=['GET'])
def health_check():
  """
  GET /api/health - Health check endpoint.

  Returns basic health status of the API.
  """
  return jsonify({
    "status": "healthy",
    "service": "Journey Search API",
    "version": "1.0.0"
  }), 200