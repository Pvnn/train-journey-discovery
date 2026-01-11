"""
Journey Service - Orchestrates journey search workflow.
Coordinates between data loader, MC-RAPTOR algorithm, and response formatting.
"""

from typing import List, Dict, Any

from services.label_manager import (
  reconstruct_path,
  enrich_journey
)


class JourneyServiceError(Exception):
  """Base exception for journey service errors."""
  pass

class StationNotFoundError(JourneyServiceError):
  """Raised when source or destination station is not found."""
  pass

class NoRoutesFoundError(JourneyServiceError):
  """Raised when no routes are found between stations."""
  pass

class AlgorithmError(JourneyServiceError):
  """Raised when MC-RAPTOR algorithm encounters an error."""
  pass


def search_journeys(
  source: str,
  destination: str,
  date: str,
  departure_time: str,
  max_transfers: int = 4
) -> List[Dict[str, Any]]:
  """
  Search for journeys between source and destination.

  This is the main entry point for journey search functionality.
  Validates inputs, runs MC-RAPTOR algorithm, and returns enriched journeys.

  NOTE: This function expects validated inputs from the API schema.
  The schema handles:
  - departure_time smart defaults (current time for today, 00:00 for future)
  - All format validations (date, time, station codes)
  - Source != destination check

  Args:
    source: Source station code (e.g., "NDLS", "MAS") - already validated
    destination: Destination station code - already validated
    date: Journey date in YYYY-MM-DD format - already validated
    departure_time: Departure time in HH:MM format - already provided by schema
                   (either user-provided or auto-filled)
    max_transfers: Maximum number of transfers allowed (default: 4)

  Returns:
    List of enriched journey dictionaries, sorted by quality

  Raises:
    StationNotFoundError: If source or destination not found in stops data
    NoRoutesFoundError: If no routes found between stations
    AlgorithmError: If MC-RAPTOR algorithm fails
    JourneyServiceError: For other service-level errors
  """
  # Import here to avoid circular dependencies
  from utils.data_loader import data_loader
  from services.mcraptor_core import MCRaptor

  # Step 1: Load all required data
  try:
    stops_data = data_loader.get_stops()
    routes_data = data_loader.get_routes()
    stop_times_data = data_loader.get_stop_times()
    train_metadata = data_loader.get_train_metadata()
    station_metadata = data_loader.get_station_metadata()
    stop_routes = data_loader.get_stop_routes()
    stop_routes_mapping = data_loader.get_stop_routes_mapping()
  except Exception as e:
    raise JourneyServiceError(f"Failed to load data: {str(e)}")

  # Step 2: Validate source and destination exist in stops.json
  # Convert to uppercase for case-insensitive lookup
  source_upper = source.strip().upper()
  destination_upper = destination.strip().upper()

  if source_upper not in stops_data:
    raise StationNotFoundError(
      f"Source station '{source}' not found. Please check the station code."
    )

  if destination_upper not in stops_data:
    raise StationNotFoundError(
      f"Destination station '{destination}' not found. Please check the station code."
    )

  # Get stop IDs for source and destination
  source_stop_id = stops_data[source_upper]['stop_id']
  destination_stop_id = stops_data[destination_upper]['stop_id']

  # Step 3: Convert departure_time (HH:MM) to minutes from midnight
  # Schema guarantees this is in valid HH:MM format
  try:
    time_parts = departure_time.split(':')
    hours = int(time_parts[0])
    minutes = int(time_parts[1])
    departure_minutes = hours * 60 + minutes
  except (ValueError, IndexError) as e:
    # This should never happen due to schema validation, but handle gracefully
    raise JourneyServiceError(f"Invalid time format received: {departure_time}")

  # Step 4: Initialize MC-RAPTOR with loaded data
  try:
    raptor = MCRaptor(
      stops_data=stops_data,
      routes_data=routes_data,
      stop_times_data=stop_times_data,
      stop_routes=stop_routes,
      train_metadata=train_metadata,
      stop_routes_mapping=stop_routes_mapping,
      query_date=date
    )
  except Exception as e:
    raise AlgorithmError(f"Failed to initialize MC-RAPTOR: {str(e)}")

  # Step 5: Run MC-RAPTOR search to get List[Label]
  try:
    destination_labels = raptor.search(
      source_stop_id=source_stop_id,
      destination_stop_id=destination_stop_id,
      departure_time=departure_minutes,
      max_transfers=max_transfers
    )
  except Exception as e:
    raise AlgorithmError(f"MC-RAPTOR search failed: {str(e)}")

  # Step 6: Check if any routes were found
  if not destination_labels or len(destination_labels) == 0:
    raise NoRoutesFoundError(
      f"No routes found from {source} to {destination} on {date} "
      f"departing at or after {departure_time} with max {max_transfers} transfers"
    )

  # Step 7: For each Label, reconstruct path and enrich journey
  enriched_journeys = []
  for label in destination_labels:
    try:
      # Reconstruct the journey path from the label
      journey = reconstruct_path(
        destination_label=label,
        stops_data=stops_data,
        routes_data=routes_data,
        stop_times_data=stop_times_data,
        train_metadata=train_metadata
      )

      # Skip empty journeys
      if not journey or not journey.segments:
        continue

      # Enrich journey with detailed metadata
      enriched_journey_dict = enrich_journey(
        journey=journey,
        stops_data=stops_data,
        station_metadata=station_metadata,
        train_metadata=train_metadata,
        stop_times_data=stop_times_data
      )

      enriched_journeys.append(enriched_journey_dict)
    except Exception as e:
      # Log the error but continue processing other labels
      # This ensures one bad label doesn't break the entire search
      print(f"Warning: Failed to process label {label}: {str(e)}")
      continue

  # Step 8: Check if any journeys were successfully enriched
  if not enriched_journeys:
    raise NoRoutesFoundError(
      f"Routes found but failed to construct valid journeys from {source} to {destination}"
    )

  # Step 9: Sort journeys by default quality (fewer transfers, less time, higher comfort)
  enriched_journeys = sort_journeys(enriched_journeys)

  return enriched_journeys


def sort_journeys(
  journeys: List[Dict[str, Any]], 
  sort_by: str = "quality",
  order: str = "asc"
) -> List[Dict[str, Any]]:
  """
  Sort journeys by specified criteria.

  Supports multiple sorting strategies:
  - "quality": Multi-key sort (transfers -> time -> comfort -> fare)
  - "time": Total journey time
  - "transfers": Number of transfers
  - "comfort": Comfort score
  - "fare": Total fare

  Args:
    journeys: List of journey dictionaries
    sort_by: Sort criteria ("quality"|"time"|"transfers"|"comfort"|"fare")
    order: Sort order ("asc"|"desc")

  Returns:
    Sorted list of journeys
  """

  def get_sort_key(journey: Dict[str, Any], criterion: str) -> tuple:
    """Generate sort key based on criterion."""

    if criterion == "quality":
      # Multi-key sorting: transfers, time, -comfort, fare
      transfers = journey.get('total_transfers', 999)
      time = journey.get('total_time', 999999)
      comfort = journey.get('comfort_score', 0.0)
      fare = journey.get('total_fare', 999999.0)
      return (transfers, time, -comfort, fare)

    elif criterion == "time":
      return (journey.get('total_time', 999999),)

    elif criterion == "transfers":
      # Secondary sort by time when transfers are equal
      transfers = journey.get('total_transfers', 999)
      time = journey.get('total_time', 999999)
      return (transfers, time)

    elif criterion == "comfort":
      # Higher comfort is better, so negate for ascending sort
      comfort = journey.get('comfort_score', 0.0)
      return (-comfort,)

    elif criterion == "fare":
      return (journey.get('total_fare', 999999.0),)

    else:
      # Default to quality sorting
      transfers = journey.get('total_transfers', 999)
      time = journey.get('total_time', 999999)
      comfort = journey.get('comfort_score', 0.0)
      fare = journey.get('total_fare', 999999.0)
      return (transfers, time, -comfort, fare)

  # Sort journeys
  sorted_journeys = sorted(
    journeys, 
    key=lambda j: get_sort_key(j, sort_by),
    reverse=(order == "desc")
  )

  return sorted_journeys


def apply_limit(
  journeys: List[Dict[str, Any]], 
  limit: int = 10
) -> List[Dict[str, Any]]:
  """
  Apply limit to journey results.

  Args:
    journeys: List of journey dictionaries
    limit: Maximum number of journeys to return (default: 10, max: 50)

  Returns:
    Limited list of journeys
  """
  # Ensure limit is within valid range
  limit = max(1, min(limit, 50))
  return journeys[:limit]


def validate_journey_feasibility(journey: Dict[str, Any]) -> bool:
  """
  Validate if a journey is feasible based on transfer buffers.

  Checks if all transfer connections have sufficient buffer time
  according to station-specific minimum transfer requirements.

  Args:
    journey: Journey dictionary with segments

  Returns:
    True if all transfers have sufficient buffer time, False otherwise
  """
  segments = journey.get('segments', [])

  for segment in segments:
    transfer_info = segment.get('transfer_after')
    if transfer_info:
      # Check if buffer time is sufficient
      if not transfer_info.get('buffer_sufficient', True):
        return False

  return True


def filter_feasible_journeys(
  journeys: List[Dict[str, Any]],
  strict_mode: bool = True
) -> List[Dict[str, Any]]:
  """
  Filter journeys to only include feasible ones.

  In strict mode, removes journeys with insufficient transfer buffers.
  In non-strict mode, returns all journeys (user can decide).

  Args:
    journeys: List of journey dictionaries
    strict_mode: If True, only return journeys with sufficient transfer buffers

  Returns:
    Filtered list of feasible journeys
  """
  if not strict_mode:
    return journeys

  return [
    journey for journey in journeys
    if validate_journey_feasibility(journey)
  ]


def get_journey_summary(journey: Dict[str, Any]) -> Dict[str, Any]:
  """
  Generate a concise summary of a journey for quick display.

  Useful for displaying journey cards in UI before user expands details.

  Args:
    journey: Journey dictionary

  Returns:
    Dictionary with summary information (departure, arrival, duration, etc.)
  """
  segments = journey.get('segments', [])

  if not segments:
    return {}

  first_segment = segments[0]
  last_segment = segments[-1]

  return {
    'departure_station': first_segment.get('boarding_stop_name'),
    'departure_station_code': first_segment.get('boarding_stop_code'),
    'departure_time': first_segment.get('departure_time_formatted'),
    'arrival_station': last_segment.get('alighting_stop_name'),
    'arrival_station_code': last_segment.get('alighting_stop_code'),
    'arrival_time': last_segment.get('arrival_time_formatted'),
    'total_duration_minutes': journey.get('total_time'),
    'total_duration_formatted': f"{journey.get('total_time', 0)} min",
    'num_transfers': journey.get('total_transfers'),
    'num_trains': len(segments),
    'total_fare': journey.get('total_fare'),
    'comfort_score': round(journey.get('comfort_score', 0.0), 2),
    'train_numbers': [seg.get('train_number') for seg in segments]
  }


def format_journey_for_display(journey: Dict[str, Any]) -> Dict[str, Any]:
  """
  Format journey with additional display-friendly fields.

  Adds human-readable formatting for times, durations, and other fields.

  Args:
    journey: Journey dictionary

  Returns:
    Journey with additional formatted fields
  """
  formatted = journey.copy()

  # Add summary at top level
  formatted['summary'] = get_journey_summary(journey)

  # Format total duration in hours and minutes
  total_minutes = journey.get('total_time', 0)
  hours = total_minutes // 60
  minutes = total_minutes % 60

  if hours > 0:
    formatted['total_duration_formatted'] = f"{hours}h {minutes}m"
  else:
    formatted['total_duration_formatted'] = f"{minutes}m"

  # Add journey quality indicators
  formatted['quality_indicators'] = {
    'is_direct': journey.get('total_transfers', 0) == 0,
    'has_many_transfers': journey.get('total_transfers', 0) > 2,
    'is_fast': total_minutes < 360,  # Less than 6 hours
    'is_comfortable': journey.get('comfort_score', 0) >= 3.5,
    'is_affordable': journey.get('total_fare', 0) < 1000
  }

  return formatted