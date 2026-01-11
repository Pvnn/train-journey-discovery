"""
Data Loader Module - Singleton for loading and caching JSON data files.
Loads all required data files once at initialization and provides cached access.
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path


class DataLoaderError(Exception):
  """Base exception for data loader errors."""
  pass


class DataLoader:
  """
  Singleton class for loading and caching railway data from JSON files.

  Loads all required data files once during initialization and provides
  cached access through getter methods. This ensures data is loaded only
  once per application lifecycle, improving performance.
  """

  def __init__(self, data_directory: str = None):
    """
    Initialize the data loader and load all JSON files.

    Args:
      data_directory: Path to directory containing JSON data files
                     If None, will look for data/processed/ in parent directory

    Raises:
      DataLoaderError: If any required file is missing or cannot be loaded
    """
    # If no directory specified, look for data in parent directory of backend
    if data_directory is None:
      # Get the directory where this file is located (backend/utils/)
      current_dir = Path(__file__).parent
      # Go up two levels: utils -> backend -> project_root
      project_root = current_dir.parent.parent
      # Look for data/processed in project root
      data_directory = project_root / "data" / "processed"

    self.data_directory = Path(data_directory)

    # Check if directory exists
    if not self.data_directory.exists():
      raise DataLoaderError(
        f"Data directory not found: {self.data_directory}\n"
        f"Please ensure data files are in the correct location.\n"
        f"Expected path: {self.data_directory.absolute()}"
      )

    # Data caches - loaded once and reused
    self._stops: Optional[Dict[str, Any]] = None
    self._routes: Optional[Dict[str, Any]] = None
    self._stop_times: Optional[List[Dict[str, Any]]] = None
    self._train_metadata: Optional[Dict[str, Any]] = None
    self._station_metadata: Optional[Dict[str, Any]] = None
    self._stop_routes: Optional[Dict[str, List[str]]] = None
    self._stop_routes_mapping: Optional[Dict[str, Dict[str, int]]] = None

    # Load all data files
    self._load_all_data()

  def _load_json_file(self, filename: str) -> Any:
    """
    Load a JSON file from the data directory.

    Args:
      filename: Name of the JSON file to load

    Returns:
      Parsed JSON data (dict or list)

    Raises:
      DataLoaderError: If file not found or JSON parsing fails
    """
    file_path = self.data_directory / filename

    try:
      with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
      return data
    except FileNotFoundError:
      raise DataLoaderError(
        f"Required data file not found: {file_path}\n"
        f"Please ensure all data files are in the '{self.data_directory}' directory."
      )
    except json.JSONDecodeError as e:
      raise DataLoaderError(
        f"Failed to parse JSON file {filename}: {str(e)}\n"
        f"Please check the file format."
      )
    except Exception as e:
      raise DataLoaderError(
        f"Error loading {filename}: {str(e)}"
      )

  def _load_all_data(self) -> None:
    """
    Load all required JSON data files.

    Loads: stops, routes, stop_times, train_metadata, station_metadata,
           stop_routes, stop_routes_mapping

    Prints loading summary with file sizes and record counts.

    Raises:
      DataLoaderError: If any file fails to load
    """
    print("Railway Data Loader - Initializing...")
    print(f"Data directory: {self.data_directory.absolute()}")
    loading_summary = []

    try:
      # Load stops.json
      print("Loading stops.json...", end=" ")
      self._stops = self._load_json_file("stops.json")
      stops_count = len(self._stops) if isinstance(self._stops, dict) else 0
      print(f"✓ {stops_count} stops loaded")
      loading_summary.append(("Stops", stops_count))

      # Load routes.json
      print("Loading routes.json...", end=" ")
      self._routes = self._load_json_file("routes.json")
      routes_count = len(self._routes) if isinstance(self._routes, dict) else 0
      print(f"✓ {routes_count} routes loaded")
      loading_summary.append(("Routes", routes_count))

      # Load stop_times.json
      print("Loading stop_times.json...", end=" ")
      self._stop_times = self._load_json_file("stop_times.json")
      stop_times_count = len(self._stop_times) if isinstance(self._stop_times, list) else 0
      print(f"✓ {stop_times_count} stop times loaded")
      loading_summary.append(("Stop Times", stop_times_count))

      # Load train_metadata.json
      print("Loading train_metadata.json...", end=" ")
      self._train_metadata = self._load_json_file("train_metadata.json")
      train_meta_count = len(self._train_metadata) if isinstance(self._train_metadata, dict) else 0
      print(f"✓ {train_meta_count} trains loaded")
      loading_summary.append(("Train Metadata", train_meta_count))

      # Load station_metadata.json
      print("Loading station_metadata.json...", end=" ")
      self._station_metadata = self._load_json_file("station_metadata.json")
      station_meta_count = len(self._station_metadata) if isinstance(self._station_metadata, dict) else 0
      print(f"✓ {station_meta_count} stations loaded")
      loading_summary.append(("Station Metadata", station_meta_count))

      # Load stop_routes.json
      print("Loading stop_routes.json...", end=" ")
      self._stop_routes = self._load_json_file("stop_routes.json")
      stop_routes_count = len(self._stop_routes) if isinstance(self._stop_routes, dict) else 0
      print(f"✓ {stop_routes_count} stop-route mappings loaded")
      loading_summary.append(("Stop Routes", stop_routes_count))

      # Load stop_routes_mapping.json
      print("Loading stop_routes_mapping.json...", end=" ")
      self._stop_routes_mapping = self._load_json_file("stop_routes_mapping.json")
      stop_routes_mapping_count = len(self._stop_routes_mapping) if isinstance(self._stop_routes_mapping, dict) else 0
      print(f"✓ {stop_routes_mapping_count} route mappings loaded")
      loading_summary.append(("Stop Routes Mapping", stop_routes_mapping_count))

    except DataLoaderError as e:
      print(f"\n✗ Data loading failed!")
      raise

    # Print summary
    print("\n" + "="*60)
    print("Loading Summary:")
    for name, count in loading_summary:
      print(f"  {name:<25} : {count:>10,} records")
    print("="*60)
    print("✓ All data loaded successfully!")
    print()

  def get_stops(self) -> Dict[str, Any]:
    """
    Get stops data.

    Returns:
      Dictionary mapping stop_code to stop information
      Format: {stop_code: {stop_id, stop_code, stop_name}}
    """
    if self._stops is None:
      raise DataLoaderError("Stops data not loaded. Initialize DataLoader first.")
    return self._stops

  def get_routes(self) -> Dict[str, Any]:
    """
    Get routes data.

    Returns:
      Dictionary mapping route_id to route information
      Format: {route_id: {train_number, train_name, running_days, ...}}
    """
    if self._routes is None:
      raise DataLoaderError("Routes data not loaded. Initialize DataLoader first.")
    return self._routes

  def get_stop_times(self) -> List[Dict[str, Any]]:
    """
    Get stop times data.

    Returns:
      List of stop time records
      Format: [{route_id, stop_id, stop_sequence, arrival_time, departure_time, ...}]
    """
    if self._stop_times is None:
      raise DataLoaderError("Stop times data not loaded. Initialize DataLoader first.")
    return self._stop_times

  def get_train_metadata(self) -> Dict[str, Any]:
    """
    Get train metadata.

    Returns:
      Dictionary mapping train_number to train metadata
      Format: {train_number: {comfort_score, class_type, category, ...}}
    """
    if self._train_metadata is None:
      raise DataLoaderError("Train metadata not loaded. Initialize DataLoader first.")
    return self._train_metadata

  def get_station_metadata(self) -> Dict[str, Any]:
    """
    Get station metadata.

    Returns:
      Dictionary mapping stop_code to station metadata
      Format: {stop_code: {zone, tier, category, min_transfer_time, ...}}
    """
    if self._station_metadata is None:
      raise DataLoaderError("Station metadata not loaded. Initialize DataLoader first.")
    return self._station_metadata

  def get_stop_routes(self) -> Dict[str, List[str]]:
    """
    Get stop-routes mapping.

    Returns:
      Dictionary mapping stop_id to list of route_ids serving that stop
      Format: {stop_id: [route_id1, route_id2, ...]}
    """
    if self._stop_routes is None:
      raise DataLoaderError("Stop routes data not loaded. Initialize DataLoader first.")
    return self._stop_routes

  def get_stop_routes_mapping(self) -> Dict[str, Dict[str, int]]:
    """
    Get stop-routes mapping with internal route mappings.

    Returns:
      Dictionary mapping route_id to internal stop ID mappings
      Format: {route_id: {internal_id: stop_id}}
      Example: {"01211": {"1": 1, "2": 2, "3": 3, ...}}
    """
    if self._stop_routes_mapping is None:
      raise DataLoaderError("Stop routes mapping data not loaded. Initialize DataLoader first.")
    return self._stop_routes_mapping

  def get_stop_by_code(self, stop_code: str) -> Optional[Dict[str, Any]]:
    """
    Get stop information by stop code.

    Args:
      stop_code: Station code (e.g., "NDLS", "MAS")

    Returns:
      Stop information dict or None if not found
    """
    stops = self.get_stops()
    return stops.get(stop_code.upper())

  def get_route_by_id(self, route_id: str) -> Optional[Dict[str, Any]]:
    """
    Get route information by route ID.

    Args:
      route_id: Route/train ID

    Returns:
      Route information dict or None if not found
    """
    routes = self.get_routes()
    return routes.get(route_id)

  def get_route_stop_mapping(self, route_id: str) -> Optional[Dict[str, int]]:
    """
    Get stop ID mapping for a specific route.

    Args:
      route_id: Route/train ID

    Returns:
      Dictionary mapping internal IDs to stop IDs for this route
      Example: {"1": 1, "2": 2, "3": 3, ...}
      Returns None if route not found
    """
    mappings = self.get_stop_routes_mapping()
    return mappings.get(route_id)

  def reload_data(self) -> None:
    """
    Reload all data from JSON files.

    Useful for development/testing or if data files are updated.
    """
    print("\nReloading data...")
    self._load_all_data()

  def __repr__(self) -> str:
    """String representation for debugging."""
    return (
      f"DataLoader(directory='{self.data_directory}', "
      f"stops={len(self._stops) if self._stops else 0}, "
      f"routes={len(self._routes) if self._routes else 0})"
    )


# Module-level singleton instance
# This is created once when the module is imported
# All parts of the application use this same instance
try:
  data_loader = DataLoader()
except DataLoaderError as e:
  print(f"Warning: Failed to initialize data loader: {e}")
  data_loader = None