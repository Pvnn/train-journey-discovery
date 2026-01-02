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