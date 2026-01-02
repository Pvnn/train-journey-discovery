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

