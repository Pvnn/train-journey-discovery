from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

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
  
  Args:
    destination_label: The final label at destination stop
    stops_data: Dict[stop_code -> stop_info] from stops.json
    routes_data: Dict[route_id -> route_info] from routes.json
    stop_times_data: List of stop_time records from stop_times.json
    train_metadata: Dict[train_number -> train_info] from train_metadata.json
    
  Returns:
    Journey object with complete path and metrics
  """
  if destination_label is None:
    return Journey()
  
  # Build stop_times lookup: {route_id: {stop_id: stop_time_info}}
  stop_times_lookup = {}
  for st in stop_times_data:
    route_id = st['route_id']
    stop_id = st['stop_id']
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
    boarding_stop_id = current_label.boarding_stop  # This is stop_id (integer)
    alighting_stop_id = current_label.alighting_stop  # This is stop_id (integer)
    
    # Get stop codes and names from stops_data
    # stops_data is Dict[stop_code -> {stop_id, stop_code, stop_name}]
    # Need to find stop_code from stop_id
    boarding_stop_code = None
    boarding_stop_name = None
    alighting_stop_code = None
    alighting_stop_name = None
    
    for stop_code, stop_info in stops_data.items():
      if stop_info['stop_id'] == boarding_stop_id:
        boarding_stop_code = stop_code
        boarding_stop_name = stop_info['stop_name']
      if stop_info['stop_id'] == alighting_stop_id:
        alighting_stop_code = stop_code
        alighting_stop_name = stop_info['stop_name']
    
    # Get route/train information
    route_info = routes_data.get(route_id, {})
    train_number = route_id  # route_id IS the train_number
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
    
    # Calculate segment duration (accounting for day offset)
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
  
  # Calculate journey metrics
  total_time = 0
  total_transfers = destination_label.num_transfers
  total_fare = 0.0
  avg_comfort = 0.0
  
  if segments:
    # Total time from first departure to last arrival (with day offsets)
    first_dept = segments[0].get('departure_time', 0)
    first_offset = segments[0].get('departure_day_offset', 0)
    last_arr = segments[-1].get('arrival_time', 0)
    last_offset = segments[-1].get('arrival_day_offset', 0)
    
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

