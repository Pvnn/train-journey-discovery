from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class Label:
  """
  Represents a state at a stop during MC-RAPTOR routing.
  Tracks arrival time, transfers, and path for reconstruction.
  """
  arrival_time: int
  num_transfers: int
  comfort_score: float = 0.0
  parent_label: Optional['Label'] = None
  route_used: Optional[str] = None
  boarding_stop: Optional[str] = None
  alighting_stop: Optional[str] = None
  
  def dominates(self, other: 'Label') -> bool:
    """
    Check if this label dominates another (Pareto-optimality).
    Returns True if this label is strictly better in at least one criterion
    and greater than or equal in all criteria.
    
    Args:
      other: Another Label to compare against
      
    Returns:
      True if this label dominates the other, False otherwise
    """
    if not isinstance(other, Label):
      return False

    arrival_ok = self.arrival_time <= other.arrival_time
    transfers_ok = self.num_transfers <= other.num_transfers
    comfort_ok = self.comfort_score >= other.comfort_score  # Higher is better
    
    # Strictly better in AT LEAST ONE criterion
    arrival_better = self.arrival_time < other.arrival_time
    transfers_better = self.num_transfers < other.num_transfers
    comfort_better = self.comfort_score > other.comfort_score
    
    all_ok = arrival_ok and transfers_ok and comfort_ok
    one_better = arrival_better or transfers_better or comfort_better
    
    return all_ok and one_better

  
  def __repr__(self) -> str:
    """String representation for debugging."""
    return (f"Label(arrival={self.arrival_time}, transfers={self.num_transfers}, "
            f"comfort={self.comfort_score}, route={self.route_used}, "
            f"boarding={self.boarding_stop}, alighting={self.alighting_stop})")


@dataclass
class Journey:
  """
  Represents a complete journey from source to destination.
  Contains all segments, metrics, and enrichment data.
  """
  segments: List[Dict[str, Any]] = field(default_factory=list)
  total_time: int = 0
  total_fare: float = 0.0
  total_transfers: int = 0
  comfort_score: float = 0.0
  
  def to_dict(self) -> Dict[str, Any]:
    """
    Convert Journey to dictionary for JSON serialization.
    
    Returns:
      Dictionary with journey details
    """
    return {
      'segments': self.segments,
      'total_time': self.total_time,
      'total_fare': self.total_fare,
      'total_transfers': self.total_transfers,
      'comfort_score': self.comfort_score,
      'num_segments': len(self.segments)
    }
  
  def __repr__(self) -> str:
    """String representation for debugging."""
    return (f"Journey(segments={len(self.segments)}, time={self.total_time}, "
            f"fare={self.total_fare}, transfers={self.total_transfers}, "
            f"comfort={self.comfort_score:.2f})")

class LabelManager:
  """
  Manages Pareto-optimal labels for each stop during MC-RAPTOR routing.
  Handles label dominance checking and maintains only non-dominated labels.
  """
  
  def __init__(self):
    """Initialize empty label storage."""
    self.labels: Dict[str, List[Label]] = {}
  
  def add_label(self, stop_id: str, new_label: Label) -> bool:
    """
    Add a label to a stop if it's not dominated by existing labels.
    Remove any existing labels that are dominated by the new label.
    
    Args:
      stop_id: The stop identifier
      new_label: The label to add
      
    Returns:
      True if label was added (non-dominated), False if dominated
    """
    # Initialize label list for this stop if not exists
    if stop_id not in self.labels:
      self.labels[stop_id] = []
    
    # Check if new label is dominated by any existing label
    for existing_label in self.labels[stop_id]:
      if existing_label.dominates(new_label):
        return False  # New label is dominated, don't add
    
    # Remove existing labels dominated by new label
    self.labels[stop_id] = [
      label for label in self.labels[stop_id]
      if not new_label.dominates(label)
    ]
    
    # Add the new label
    self.labels[stop_id].append(new_label)
    return True
  
  def initialize_source(self, source_stop_id: str, departure_time: int) -> None:
    """
    Initialize the source stop with a label at departure time.
    
    Args:
      source_stop_id: The starting stop identifier
      departure_time: Departure time in minutes from midnight
    """
    source_label = Label(
      arrival_time=departure_time,
      num_transfers=0,
      comfort_score=0.0,
      parent_label=None,
      route_used=None,
      boarding_stop=None,
      alighting_stop=source_stop_id
    )
    self.labels[source_stop_id] = [source_label]
  
  def get_pareto_optimal_labels(self, stop_id: str) -> List[Label]:
    """
    Get all Pareto-optimal labels for a given stop.
    
    Args:
      stop_id: The stop identifier
      
    Returns:
      List of non-dominated labels for the stop (empty list if stop not reached)
    """
    return self.labels.get(stop_id, [])
  
  def get_all_labels(self) -> Dict[str, List[Label]]:
    """
    Get all labels for all stops.
    
    Returns:
      Dictionary mapping stop_id to list of labels
    """
    return self.labels
  
  def has_labels(self, stop_id: str) -> bool:
    """
    Check if a stop has any labels (i.e., has been reached).
    
    Args:
      stop_id: The stop identifier
      
    Returns:
      True if stop has labels, False otherwise
    """
    return stop_id in self.labels and len(self.labels[stop_id]) > 0
  
  def __repr__(self) -> str:
    """String representation for debugging."""
    total_labels = sum(len(labels) for labels in self.labels.values())
    return f"LabelManager(stops={len(self.labels)}, total_labels={total_labels})"

def reconstruct_path(
  destination_label: Label,
  stops_data: Dict[str, Any],
  routes_data: Dict[str, Any],
  stop_times_data: List[Dict[str, Any]],
  train_metadata: Optional[Dict[str, Any]] = None
) -> Journey:
  """
  Reconstruct the complete journey path from a destination label.
  Backtracks through parent_label chain to build journey segments.

  ✅ FIXED: Handles None values in departure/arrival times
  ✅ FIXED: Converts stop_ids to strings for consistent lookup
  """
  if destination_label is None:
    return Journey()

  # Build stop_times lookup: {route_id: {stop_id: stop_time_info}}
  stop_times_lookup = {}
  for st in stop_times_data:
    route_id = st['route_id']
    stop_id = str(st['stop_id'])  # ✅ FIX: Convert to string
    if route_id not in stop_times_lookup:
      stop_times_lookup[route_id] = {}
    stop_times_lookup[route_id][stop_id] = st

  # Backtrack through parent_label chain
  segments = []
  current_label = destination_label

  while current_label is not None:
    # Skip source label (no route_used means starting point)
    if current_label.route_used is None or current_label.parent_label is None:
      break

    # Extract segment information
    route_id = current_label.route_used
    boarding_stop_id = str(current_label.boarding_stop)  # ✅ FIX: Convert to string
    alighting_stop_id = str(current_label.alighting_stop)  # ✅ FIX: Convert to string

    # Get stop codes and names from stops_data
    boarding_stop_code = None
    boarding_stop_name = None
    alighting_stop_code = None
    alighting_stop_name = None

    for stop_code, stop_info in stops_data.items():
      if str(stop_info['stop_id']) == boarding_stop_id:
        boarding_stop_code = stop_code
        boarding_stop_name = stop_info['stop_name']
      if str(stop_info['stop_id']) == alighting_stop_id:
        alighting_stop_code = stop_code
        alighting_stop_name = stop_info['stop_name']

    # Get route/train information
    route_info = routes_data.get(route_id, {})
    train_number = route_id
    train_name = route_info.get('train_name', 'Unknown')

    # Get departure and arrival times from stop_times
    departure_time = None
    arrival_time = None
    departure_day_offset = 0
    arrival_day_offset = 0

    if route_id in stop_times_lookup:
      if boarding_stop_id in stop_times_lookup[route_id]:
        st_board = stop_times_lookup[route_id][boarding_stop_id]
        departure_time = st_board.get('departure_time')
        departure_day_offset = st_board.get('day_offset', 0)

      if alighting_stop_id in stop_times_lookup[route_id]:
        st_alight = stop_times_lookup[route_id][alighting_stop_id]
        arrival_time = st_alight.get('arrival_time')
        arrival_day_offset = st_alight.get('day_offset', 0)

    # ✅ FIX: Calculate segment duration with None checks
    segment_duration = 0
    if departure_time is not None and arrival_time is not None:
      actual_departure = departure_time + (departure_day_offset * 1440)
      actual_arrival = arrival_time + (arrival_day_offset * 1440)
      segment_duration = actual_arrival - actual_departure

    # Get train metadata if available
    comfort = 0.0
    train_class = 'Unknown'
    category = 'Unknown'

    if train_metadata and train_number in train_metadata:
      train_info = train_metadata[train_number]
      comfort = train_info.get('comfort_score', 0.0)
      train_class = train_info.get('class_type', 'Unknown')
      category = train_info.get('category', 'Unknown')

    # Build segment
    segment = {
      'route_id': route_id,
      'train_number': train_number,
      'train_name': train_name,
      'category': category,
      'train_class': train_class,
      'boarding_stop_id': boarding_stop_id,
      'boarding_stop_code': boarding_stop_code,
      'boarding_stop_name': boarding_stop_name,
      'alighting_stop_id': alighting_stop_id,
      'alighting_stop_code': alighting_stop_code,
      'alighting_stop_name': alighting_stop_name,
      'departure_time': departure_time,
      'departure_day_offset': departure_day_offset,
      'arrival_time': arrival_time,
      'arrival_day_offset': arrival_day_offset,
      'duration': segment_duration,
      'comfort_score': comfort
    }

    segments.append(segment)
    current_label = current_label.parent_label

  # Reverse segments (built backwards)
  segments.reverse()

  # ✅ FIX: Calculate journey metrics with None checks
  total_time = 0
  total_transfers = destination_label.num_transfers
  total_fare = 0.0
  avg_comfort = 0.0

  if segments:
    # Total time from first departure to last arrival (with day offsets)
    first_dept = segments[0].get('departure_time')  # ✅ FIX: No default value
    first_offset = segments[0].get('departure_day_offset', 0)
    last_arr = segments[-1].get('arrival_time')  # ✅ FIX: No default value
    last_offset = segments[-1].get('arrival_day_offset', 0)

    # ✅ FIX: Only calculate if both times are not None
    if first_dept is not None and last_arr is not None:
      actual_start = first_dept + (first_offset * 1440)
      actual_end = last_arr + (last_offset * 1440)
      total_time = actual_end - actual_start

    # Average comfort score
    comfort_scores = [seg.get('comfort_score', 0.0) for seg in segments]
    avg_comfort = sum(comfort_scores) / len(comfort_scores) if comfort_scores else 0.0

  journey = Journey(
    segments=segments,
    total_time=total_time,
    total_fare=total_fare,
    total_transfers=total_transfers,
    comfort_score=avg_comfort
  )

  return journey

def filter_routes_by_date(
  routes_data: Dict[str, Any],
  route_ids: List[str],
  query_date: str
) -> List[str]:
  """
  Filter a list of route IDs to only those running on the query date.
  
  Args:
    routes_data: Dict[route_id -> route_info] from routes.json
    route_ids: List of route IDs to filter
    query_date: Date string in format 'YYYY-MM-DD' or datetime object
    
  Returns:
    List of route IDs that run on the given date
  """
  # Parse query_date if string
  if isinstance(query_date, str):
    date_obj = datetime.strptime(query_date, '%Y-%m-%d')
  elif isinstance(query_date, datetime):
    date_obj = query_date
  else:
    raise ValueError(f"query_date must be string 'YYYY-MM-DD' or datetime object, got {type(query_date)}")
  
  # Get day of week from Python (Monday=0, Sunday=6)
  python_day = date_obj.weekday()
  
  # Convert to Indian Railways format (Sunday=0, Monday=1, ..., Saturday=6)
  # Python: Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
  # Indian Railways: Sun=0, Mon=1, Tue=2, Wed=3, Thu=4, Fri=5, Sat=6
  indian_railways_day = (python_day + 1) % 7
  
  # Filter routes
  filtered_routes = []
  for route_id in route_ids:
    if route_id in routes_data:
      route_info = routes_data[route_id]
      running_days = route_info.get('running_days', '0000000')
      
      # Check if train runs on this day
      if len(running_days) == 7 and running_days[indian_railways_day] == '1':
        filtered_routes.append(route_id)
  
  return filtered_routes


def check_route_runs_on_date(
  route_info: Dict[str, Any],
  query_date: str
) -> bool:
  """
  Check if a single route runs on the given date.
  
  Args:
    route_info: Route information dict containing 'running_days'
    query_date: Date string in format 'YYYY-MM-DD' or datetime object
    
  Returns:
    True if route runs on the date, False otherwise
  """
  # Parse query_date if string
  if isinstance(query_date, str):
    date_obj = datetime.strptime(query_date, '%Y-%m-%d')
  elif isinstance(query_date, datetime):
    date_obj = query_date
  else:
    raise ValueError(f"query_date must be string 'YYYY-MM-DD' or datetime object")
  
  # Get day of week and convert to Indian Railways format
  python_day = date_obj.weekday()
  indian_railways_day = (python_day + 1) % 7
  
  # Check running_days
  running_days = route_info.get('running_days', '0000000')
  if len(running_days) == 7:
    return running_days[indian_railways_day] == '1'
  return False

import json
def format_time_hhmm(time_minutes: Optional[int]) -> str:
  """
  Convert time in minutes from midnight to HH:MM format.
  
  Args:
    time_minutes: Time in minutes from midnight (can be > 1440 for next day)
    
  Returns:
    Time string in HH:MM format
  """
  if time_minutes is None:
    return "N/A"
  
  # Handle multi-day times
  total_minutes = time_minutes % 1440
  hours = total_minutes // 60
  minutes = total_minutes % 60
  
  return f"{hours:02d}:{minutes:02d}"


def calculate_segment_distance(
  boarding_stop_id: int,
  alighting_stop_id: int,
  route_id: str,
  stop_times_data: List[Dict[str, Any]]
) -> float:
  """
  Calculate distance between two stops on a route.
  This is a placeholder - actual implementation would use distance data.
  
  Args:
    boarding_stop_id: Starting stop ID
    alighting_stop_id: Ending stop ID
    route_id: Route/train ID
    stop_times_data: Stop times data
    
  Returns:
    Distance in kilometers (estimated)
  """
  # Find stop sequences
  boarding_seq = None
  alighting_seq = None
  
  for st in stop_times_data:
    if st['route_id'] == route_id:
      if st['stop_id'] == boarding_stop_id:
        boarding_seq = st['stop_sequence']
      if st['stop_id'] == alighting_stop_id:
        alighting_seq = st['stop_sequence']
  
  if boarding_seq is not None and alighting_seq is not None:
    # Rough estimate: 50 km per stop difference
    stop_diff = abs(alighting_seq - boarding_seq)
    return stop_diff * 50.0
  
  return 0.0


def calculate_segment_fare(
  distance_km: float,
  train_metadata: Dict[str, Any],
  route_id: str
) -> float:
  """
  Calculate fare for a segment based on distance and train class.
  
  Args:
    distance_km: Distance in kilometers
    train_metadata: Train metadata dictionary
    route_id: Route/train ID
    
  Returns:
    Fare amount in rupees
  """
  if route_id in train_metadata:
    base_fare_per_km = train_metadata[route_id].get('base_fare_per_km', 0.5)
    return distance_km * base_fare_per_km
  
  # Default fare if no metadata
  return distance_km * 0.5


def enrich_journey_segments(
  journey: Journey,
  stops_data: Dict[str, Any],
  station_metadata: Dict[str, Any],
  train_metadata: Dict[str, Any],
  stop_times_data: List[Dict[str, Any]]
) -> Journey:
  """
  Enrich journey segments with detailed metadata and formatted information.
  
  Args:
    journey: Journey object with basic segments
    stops_data: Dict[stop_code -> stop_info] from stops.json
    station_metadata: Dict[stop_code -> station_info] from station_metadata.json
    train_metadata: Dict[train_number -> train_info] from train_metadata.json
    stop_times_data: List of stop_time records from stop_times.json
    
  Returns:
    Enriched Journey object with full details
  """
  enriched_segments = []
  total_fare = 0.0
  total_distance = 0.0
  
  for i, segment in enumerate(journey.segments):
    # Calculate distance and fare
    distance = calculate_segment_distance(
      segment['boarding_stop_id'],
      segment['alighting_stop_id'],
      segment['route_id'],
      stop_times_data
    )
    
    fare = calculate_segment_fare(
      distance,
      train_metadata,
      segment['route_id']
    )
    
    total_fare += fare
    total_distance += distance
    
    # Format times
    departure_formatted = format_time_hhmm(segment.get('departure_time'))
    arrival_formatted = format_time_hhmm(segment.get('arrival_time'))
    
    # Get station metadata for boarding and alighting
    boarding_code = segment.get('boarding_stop_code')
    alighting_code = segment.get('alighting_stop_code')
    
    boarding_station_info = station_metadata.get(boarding_code, {})
    alighting_station_info = station_metadata.get(alighting_code, {})
    
    # Build enriched segment
    enriched_segment = {
      **segment,  # Keep all original fields
      'distance_km': round(distance, 2),
      'fare': round(fare, 2),
      'departure_time_formatted': departure_formatted,
      'arrival_time_formatted': arrival_formatted,
      'duration_formatted': f"{segment['duration']} min",
      'boarding_station_zone': boarding_station_info.get('zone', 'N/A'),
      'boarding_station_tier': boarding_station_info.get('tier', 'N/A'),
      'alighting_station_zone': alighting_station_info.get('zone', 'N/A'),
      'alighting_station_tier': alighting_station_info.get('tier', 'N/A')
    }
    
    enriched_segments.append(enriched_segment)
    
    # Add transfer information between segments
    if i < len(journey.segments) - 1:
      next_segment = journey.segments[i + 1]
      
      # Transfer happens at current segment's alighting stop
      transfer_stop_code = segment.get('alighting_stop_code')
      transfer_station_info = station_metadata.get(transfer_stop_code, {})
      
      # Calculate transfer/buffer time
      current_arrival_time = segment.get('arrival_time')
      current_arrival_offset = segment.get('arrival_day_offset', 0)
      next_departure_time = next_segment.get('departure_time')
      next_departure_offset = next_segment.get('departure_day_offset', 0)

      transfer_buffer = 0
      if current_arrival_time is not None and next_departure_time is not None:
        current_arrival = current_arrival_time + (current_arrival_offset * 1440)
        next_departure = next_departure_time + (next_departure_offset * 1440)
        transfer_buffer = next_departure - current_arrival
      
      # Get minimum transfer time from station metadata
      min_transfer_time = transfer_station_info.get('min_transfer_time', 30)
      
      # Create transfer info object
      transfer_info = {
        'transfer_number': i + 1,
        'station_code': transfer_stop_code,
        'station_name': segment.get('alighting_stop_name'),
        'station_zone': transfer_station_info.get('zone', 'N/A'),
        'station_tier': transfer_station_info.get('tier', 'N/A'),
        'station_category': transfer_station_info.get('category', 'N/A'),
        'min_transfer_time': min_transfer_time,
        'actual_buffer_time': transfer_buffer,
        'buffer_sufficient': transfer_buffer >= min_transfer_time,
        'previous_train': segment['train_number'],
        'next_train': next_segment['train_number'],
        'arrival_time': format_time_hhmm(segment.get('arrival_time')),
        'departure_time': format_time_hhmm(next_segment.get('departure_time'))
      }
      
      # Add transfer info to enriched segment
      enriched_segment['transfer_after'] = transfer_info
  
  # Update journey with enriched segments and totals
  journey.segments = enriched_segments
  journey.total_fare = round(total_fare, 2)
  
  return journey


def enrich_journey(
  journey: Journey,
  stops_data: Dict[str, Any],
  station_metadata: Dict[str, Any],
  train_metadata: Dict[str, Any],
  stop_times_data: List[Dict[str, Any]]
) -> Dict[str, Any]:
  """
  Main enrichment function - enriches journey and returns as JSON dict.
  
  Args:
    journey: Journey object to enrich
    stops_data: Stops data
    station_metadata: Station metadata
    train_metadata: Train metadata
    stop_times_data: Stop times data
    
  Returns:
    Enriched journey as dictionary
  """
  enriched = enrich_journey_segments(
    journey,
    stops_data,
    station_metadata,
    train_metadata,
    stop_times_data
  )
  
  return enriched.to_dict()