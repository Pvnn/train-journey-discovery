"""
Station Service - Handles station lookup and search operations.

Provides efficient search and retrieval of station information.
"""

from typing import List, Dict, Any, Optional
from utils.data_loader import data_loader


class StationCache:
  """Cache for station data to avoid repeated processing."""

  def __init__(self):
    self._all_stations: Optional[List[Dict[str, Any]]] = None
    self._station_by_code: Optional[Dict[str, Dict[str, Any]]] = None

  def get_all_stations(self) -> List[Dict[str, Any]]:
    """Get all stations (cached)."""
    if self._all_stations is None:
      self._all_stations = build_station_list()
    return self._all_stations

  def get_station_by_code(self, code: str) -> Optional[Dict[str, Any]]:
    """Get station by code (cached)."""
    if self._station_by_code is None:
      stations = self.get_all_stations()
      self._station_by_code = {s['stop_code']: s for s in stations}
    return self._station_by_code.get(code.upper())

  def clear_cache(self):
    """Clear cached data."""
    self._all_stations = None
    self._station_by_code = None


# Global cache instance
_station_cache = StationCache()


def build_station_list() -> List[Dict[str, Any]]:
  """
  Build complete station list with all metadata.

  Returns:
    List of station dictionaries with stop_id, stop_code, stop_name, zone, etc.
  """
  stops_data = data_loader.get_stops()
  station_metadata = data_loader.get_station_metadata()
  stop_routes = data_loader.get_stop_routes()

  stations = []

  for stop_code, stop_info in stops_data.items():
    station = {
      'stop_id': stop_info.get('stop_id'),
      'stop_code': stop_code,
      'stop_name': stop_info.get('stop_name', 'Unknown')
    }

    # Add metadata if available
    metadata = station_metadata.get(stop_code, {})
    station['zone'] = metadata.get('zone', 'Unknown')
    station['tier'] = metadata.get('tier', 'Unknown')
    station['category'] = metadata.get('category', 'Unknown')
    station['min_transfer_time'] = metadata.get('min_transfer_time', 0)

    # Add routes serving this station
    stop_id = str(stop_info.get('stop_id'))
    routes_serving = stop_routes.get(stop_id, [])
    station['routes_serving'] = len(routes_serving)
    station['route_ids'] = routes_serving

    stations.append(station)

  return stations


def get_all_stations(zone_filter: Optional[str] = None) -> List[Dict[str, Any]]:
  """
  Get all stations, optionally filtered by zone.

  Args:
    zone_filter: Optional zone code to filter by (e.g., "WR", "CR", "ER")

  Returns:
    List of station dictionaries
  """
  stations = _station_cache.get_all_stations()

  if zone_filter:
    zone_upper = zone_filter.upper()
    stations = [s for s in stations if s.get('zone', '').upper() == zone_upper]

  return stations


def search_stations(query: str, limit: int = 10) -> List[Dict[str, Any]]:
  """
  Search stations by name or code.

  Logic:
  - Station code: Prefix match (case-insensitive)
  - Station name: Partial match (case-insensitive)

  Args:
    query: Search term (station name or code)
    limit: Maximum number of results (default: 10)

  Returns:
    List of matching station dictionaries (max 10)
  """
  if not query or not query.strip():
    return []

  query_upper = query.strip().upper()
  query_lower = query.strip().lower()

  stations = _station_cache.get_all_stations()
  matches = []

  for station in stations:
    stop_code = station.get('stop_code', '').upper()
    stop_name = station.get('stop_name', '').lower()

    # Check for code prefix match (exact match has priority)
    if stop_code == query_upper:
      matches.insert(0, station)  # Exact match goes first
      continue

    # Check for code prefix match
    if stop_code.startswith(query_upper):
      matches.append(station)
      continue

    # Check for name partial match
    if query_lower in stop_name:
      matches.append(station)

  # Return top N results
  return matches[:limit]


def get_station_details(station_code: str) -> Optional[Dict[str, Any]]:
  """
  Get detailed information for a specific station.

  Args:
    station_code: Station code (e.g., "NDLS", "MAS")

  Returns:
    Detailed station dictionary or None if not found
  """
  return _station_cache.get_station_by_code(station_code)


def format_station_summary(station: Dict[str, Any]) -> Dict[str, Any]:
  """
  Format station data for summary display (search results).

  Args:
    station: Full station dictionary

  Returns:
    Summary dictionary with essential fields
  """
  return {
    'stop_id': station.get('stop_id'),
    'stop_code': station.get('stop_code'),
    'stop_name': station.get('stop_name'),
    'zone': station.get('zone')
  }


def format_station_detail(station: Dict[str, Any]) -> Dict[str, Any]:
  """
  Format station data for detailed display.

  Args:
    station: Full station dictionary

  Returns:
    Detailed dictionary with all fields
  """
  return {
    'stop_id': station.get('stop_id'),
    'stop_code': station.get('stop_code'),
    'stop_name': station.get('stop_name'),
    'zone': station.get('zone'),
    'tier': station.get('tier'),
    'category': station.get('category'),
    'min_transfer_time': station.get('min_transfer_time'),
    'routes_serving': station.get('routes_serving'),
    'route_ids': station.get('route_ids', [])
  }


def clear_station_cache():
  """Clear the station cache (useful for testing or data updates)."""
  _station_cache.clear_cache()
