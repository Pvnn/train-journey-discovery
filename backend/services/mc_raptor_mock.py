"""
Mock MC-RAPTOR Implementation - Correctly matches label_manager expectations.
Uses REAL stop_ids from actual stop_times data for proper path reconstruction.
"""

from typing import Dict, List, Any
from backend.services.label_manager import Label


class MCRaptor:
  """
  Mock MC-RAPTOR that creates realistic Labels using actual data.

  Key: Uses real stop_ids from stop_times so reconstruct_path can find them!
  """

  def __init__(
    self,
    stops_data: Dict[str, Any],
    routes_data: Dict[str, Any],
    stop_times_data: List[Dict[str, Any]],
    stop_routes: Dict[str, List[str]],
    train_metadata: Dict[str, Any],
    stop_routes_mapping: Dict[str, Dict[str, int]],
    query_date: str
  ):
    """Initialize mock MCRaptor with data."""
    self.stops_data = stops_data
    self.routes_data = routes_data
    self.stop_times_data = stop_times_data
    self.stop_routes = stop_routes
    self.train_metadata = train_metadata
    self.stop_routes_mapping = stop_routes_mapping
    self.query_date = query_date

    print(f"[MOCK] MCRaptor initialized for date: {query_date}")
    print(f"[MOCK] Loaded {len(stops_data)} stops, {len(routes_data)} routes")

    # Build stop_times lookup: {route_id: [stop_times sorted by sequence]}
    self._build_stop_times_lookup()

    # Find valid routes with enough stops
    self._find_valid_routes()

  def _build_stop_times_lookup(self):
    """Build lookup: route_id -> list of stop_times sorted by sequence."""
    self.route_stop_times = {}
    for st in self.stop_times_data:
      route_id = st.get('route_id')
      if route_id not in self.route_stop_times:
        self.route_stop_times[route_id] = []
      self.route_stop_times[route_id].append(st)

    # Sort each route's stop_times by stop_sequence
    for route_id in self.route_stop_times:
      self.route_stop_times[route_id].sort(key=lambda x: x.get('stop_sequence', 0))

  def _find_valid_routes(self):
    """Find routes with at least 3 stops for creating mock journeys."""
    self.valid_routes = []
    for route_id, stop_times in self.route_stop_times.items():
      if len(stop_times) >= 3:  # Need at least 3 stops for realistic journeys
        self.valid_routes.append(route_id)
      if len(self.valid_routes) >= 10:  # Keep first 10 valid routes
        break

  def search(
    self,
    source_stop_id: int,
    destination_stop_id: int,
    departure_time: int,
    max_transfers: int = 4
  ) -> List[Label]:
    """
    Mock search - returns Labels with REAL stop_ids from stop_times.
    """
    print(f"[MOCK] Running search:")
    print(f"         Source Stop ID: {source_stop_id}")
    print(f"         Destination Stop ID: {destination_stop_id}")
    print(f"         Departure Time: {departure_time} minutes ({departure_time//60:02d}:{departure_time%60:02d})")
    print(f"         Max Transfers: {max_transfers}")

    if len(self.valid_routes) < 1:
      print("[MOCK] No valid routes found")
      return []

    mock_labels = []

    # Journey 1: Direct journey (0 transfers)
    if len(self.valid_routes) >= 1:
      label1 = self._create_mock_journey_label(
        route_ids=[self.valid_routes[0]],
        departure_time=departure_time,
        base_duration=180
      )
      if label1:
        mock_labels.append(label1)

    # Journey 2: One transfer (1 transfer)
    if len(self.valid_routes) >= 2 and max_transfers >= 1:
      label2 = self._create_mock_journey_label(
        route_ids=self.valid_routes[:2],
        departure_time=departure_time + 30,
        base_duration=240
      )
      if label2:
        mock_labels.append(label2)

    # Journey 3: Two transfers (2 transfers)
    if len(self.valid_routes) >= 3 and max_transfers >= 2:
      label3 = self._create_mock_journey_label(
        route_ids=self.valid_routes[:3],
        departure_time=departure_time + 60,
        base_duration=300
      )
      if label3:
        mock_labels.append(label3)

    print(f"[MOCK] Returning {len(mock_labels)} mock journey options")
    return mock_labels

  def _create_mock_journey_label(
    self,
    route_ids: List[str],
    departure_time: int,
    base_duration: int
  ) -> Label:
    """
    Create a Label chain using REAL stop_ids from stop_times.

    This is the KEY fix: We use actual stop_ids that exist in stop_times
    for each route, so reconstruct_path can find them and get departure/arrival times.
    """
    num_segments = len(route_ids)
    segment_duration = base_duration // num_segments if num_segments > 0 else base_duration

    current_label = None

    # Build label chain backwards (destination to source)
    for i in range(num_segments - 1, -1, -1):
      route_id = route_ids[i]

      # Get stop_times for this route
      route_stops = self.route_stop_times.get(route_id, [])

      if len(route_stops) < 2:
        continue

      # Use REAL stop_ids from this route's stop_times
      # For simplicity: use first stop as boarding, second as alighting
      boarding_stop_time = route_stops[0]
      alighting_stop_time = route_stops[1]

      boarding_stop_id = boarding_stop_time.get('stop_id')
      alighting_stop_id = alighting_stop_time.get('stop_id')

      # Calculate arrival time for this segment
      segment_arrival_time = departure_time + segment_duration * (i + 1)

      # Get comfort score from train metadata
      train_number = self.routes_data.get(route_id, {}).get('train_number', route_id)
      comfort = self.train_metadata.get(train_number, {}).get('comfort_score', 3.0)

      # Create Label with REAL stop_ids
      try:
        label = Label(
          arrival_time=segment_arrival_time,
          num_transfers=i,  # Number of transfers to reach this point
          comfort_score=comfort,
          parent_label=current_label,
          route_used=route_id,
          boarding_stop=boarding_stop_id,  # REAL stop_id from stop_times
          alighting_stop=alighting_stop_id  # REAL stop_id from stop_times
        )
        current_label = label
      except Exception as e:
        print(f"[MOCK] Warning: Failed to create label for route {route_id}: {e}")
        continue

    return current_label