from typing import Set
from collections import defaultdict

from services.label_manager import LabelManager, Label
from services.label_manager import filter_routes_by_date


class MCRaptor:
    """
    MC-RAPTOR CORE (Person A)

    - Label-based RAPTOR algorithm
    - Uses LabelManager for Pareto dominance
    - Produces Labels only (NO path reconstruction here)
    """

    def __init__(
        self,
        stops_data,
        routes_data,
        stop_times_data,
        stop_routes,
        train_metadata,
        stop_routes_mapping,
        query_date,
        station_metadata=None
    ):
        self.stops = stops_data
        self.routes = routes_data
        self.stop_times = stop_times_data
        self.stop_routes = stop_routes
        self.train_metadata = train_metadata
        self.stop_routes_mapping = stop_routes_mapping
        self.query_date = query_date
        self.station_metadata = station_metadata or {}

        # Label storage
        self.label_manager = LabelManager()

        # route_id -> stop_times sorted by stop_sequence
        self.route_stop_times = defaultdict(list)
        for st in self.stop_times:
            self.route_stop_times[st["route_id"]].append(st)

        for rid in self.route_stop_times:
            self.route_stop_times[rid].sort(key=lambda x: x["stop_sequence"])

        # Build stop_id -> station_code mapping for lookups
        self.stop_id_to_code = {}
        for stop_code, stop_info in self.stops.items():
            stop_id = stop_info.get("stop_id")
            if stop_id is not None:
                # Store both int and string versions for flexibility
                self.stop_id_to_code[str(stop_id)] = stop_code
                self.stop_id_to_code[int(stop_id)] = stop_code

    def _get_station_code(self, stop_id):
        """Convert stop_id (int or str) to station code."""
        stop_id_str = str(stop_id)
        return self.stop_id_to_code.get(stop_id_str)

    def _get_routes_for_stop(self, stop_id):
        """Get routes serving a stop by converting stop_id to station code."""
        station_code = self._get_station_code(stop_id)
        if station_code:
            return self.stop_routes.get(station_code, [])
        return []

    def _get_min_transfer_time(self, stop_id):
        """Get minimum transfer time for a stop from station_metadata."""
        station_code = self._get_station_code(stop_id)
        if station_code and station_code in self.station_metadata:
            return self.station_metadata[station_code].get("min_transfer_time", 30)
        # Default transfer time if not found
        return 30

    # ===================================================
    # PUBLIC SEARCH
    # ===================================================
    def search(
        self,
        source_stop_id,
        destination_stop_id,
        departure_time,
        max_transfers=4
    ):
        # Normalize IDs ONCE to strings
        source_stop_id = str(source_stop_id)
        destination_stop_id = str(destination_stop_id)

        # Initialize source label
        self.label_manager.initialize_source(source_stop_id, departure_time)

        # -------- ROUND 0 --------
        marked_stops = self._initialize_round_0(
            source_stop_id,
            departure_time
        )

        # -------- TRANSFER ROUNDS --------
        for k in range(1, max_transfers + 1):
            if not marked_stops:
                break
            marked_stops = self._run_round_k(marked_stops, k)

        return self.label_manager.get_pareto_optimal_labels(destination_stop_id)

    # ===================================================
    # ROUND 0 — NO TRANSFERS
    # ===================================================
    def _initialize_round_0(
        self,
        source_stop_id,
        departure_time
    ) -> Set[str]:

        marked_stops = set()

        # Get the source label (should always exist after initialize_source)
        source_labels = self.label_manager.get_pareto_optimal_labels(source_stop_id)
        if not source_labels:
            # This should never happen, but handle gracefully
            return marked_stops
        
        base_label = source_labels[0]

        # Get routes serving the source stop (convert stop_id to station code)
        serving_routes = self._get_routes_for_stop(source_stop_id)
        serving_routes = filter_routes_by_date(
            self.routes,
            serving_routes,
            self.query_date
        )

        if not serving_routes:
            # No routes serve this stop on the query date
            return marked_stops

        # For each route serving the source stop
        for route_id in serving_routes:
            # Get the stop mapping for this route (keys are strings in JSON)
            route_stops = self.stop_routes_mapping.get(route_id, {})
            
            # Check if source_stop_id (string) is in route_stops
            # route_stops keys are strings from JSON: {"1": 1, "2": 2, ...}
            if source_stop_id not in route_stops:
                # Try with int key as fallback (in case JSON loader converted to int)
                source_stop_id_int = None
                try:
                    source_stop_id_int = int(source_stop_id)
                except (ValueError, TypeError):
                    pass
                
                if source_stop_id_int is not None and source_stop_id_int in route_stops:
                    boarding_sequence = route_stops[source_stop_id_int]
                else:
                    continue
            else:
                boarding_sequence = route_stops[source_stop_id]

            # Traverse the route from boarding stop
            improved = self._traverse_route(
                route_id=route_id,
                boarding_stop_id=source_stop_id,
                base_label=base_label,
                boarding_sequence=boarding_sequence,
                num_transfers=0
            )

            marked_stops.update(improved)

        return marked_stops

    # ===================================================
    # ROUND k > 0 — TRANSFERS
    # ===================================================
    def _run_round_k(
        self,
        prev_marked: Set[str],
        round_k: int
    ) -> Set[str]:

        new_marked = set()

        for stop_id in prev_marked:
            # Ensure stop_id is string
            stop_id = str(stop_id)
            
            # Get all Pareto-optimal labels for this stop
            labels = self.label_manager.get_pareto_optimal_labels(stop_id)

            if not labels:
                continue

            # Get minimum transfer time for this station
            min_transfer_time = self._get_min_transfer_time(stop_id)

            # Get routes serving this stop (convert stop_id to station code)
            route_ids = self._get_routes_for_stop(stop_id)
            route_ids = filter_routes_by_date(
                self.routes,
                route_ids,
                self.query_date
            )

            # For each label at this stop, try to transfer
            for label in labels:
                # Calculate earliest possible boarding time after transfer buffer
                earliest_boarding_time = label.arrival_time + min_transfer_time

                # Debug logging (temporary)
                station_code = self._get_station_code(stop_id)
                print(f"[TRANSFER] Stop {stop_id} ({station_code}): "
                      f"arrival={label.arrival_time}, "
                      f"min_transfer={min_transfer_time}, "
                      f"earliest_board={earliest_boarding_time}, "
                      f"label_transfers={label.num_transfers}")

                # Try each route serving this stop
                for route_id in route_ids:
                    route_stops = self.stop_routes_mapping.get(route_id, {})
                    
                    # Check if stop_id (string) is in route_stops
                    if stop_id not in route_stops:
                        # Try with int key as fallback
                        stop_id_int = None
                        try:
                            stop_id_int = int(stop_id)
                        except (ValueError, TypeError):
                            pass
                        
                        if stop_id_int is not None and stop_id_int in route_stops:
                            boarding_sequence = route_stops[stop_id_int]
                        else:
                            continue
                    else:
                        boarding_sequence = route_stops[stop_id]

                    # Traverse route with transfer buffer constraint
                    # num_transfers = label.num_transfers + 1 (not round_k)
                    improved = self._traverse_route(
                        route_id=route_id,
                        boarding_stop_id=stop_id,
                        base_label=label,
                        boarding_sequence=boarding_sequence,
                        num_transfers=label.num_transfers + 1,
                        earliest_boarding_time=earliest_boarding_time,
                        marked_stops=new_marked
                    )

                    if improved:
                        print(f"[TRANSFER] Route {route_id}: {len(improved)} stops improved")

        return new_marked

    # ===================================================
    # ROUTE TRAVERSAL
    # ===================================================
    def _traverse_route(
        self,
        route_id,
        boarding_stop_id,
        base_label,
        boarding_sequence,
        num_transfers,
        marked_stops=None,
        earliest_boarding_time=None
    ) -> Set[str]:

        improved = set()

        comfort = self.train_metadata.get(
            route_id, {}
        ).get("comfort_score", 0.0)

        # Get all stop_times for this route
        route_stop_times_list = self.route_stop_times.get(route_id, [])
        
        if not route_stop_times_list:
            return improved

        # Find the boarding stop_time to get departure time
        boarding_departure_time = None
        for st in route_stop_times_list:
            # Normalize stop_id comparison (stop_times has int, boarding_stop_id is string)
            st_stop_id = st["stop_id"]
            boarding_stop_id_normalized = str(boarding_stop_id)
            
            # Compare stop_id (handle both int and string)
            if (str(st_stop_id) == boarding_stop_id_normalized and 
                st["stop_sequence"] == boarding_sequence):
                boarding_departure_time = st.get("departure_time")
                if boarding_departure_time is not None:
                    boarding_departure_time += (st.get("day_offset", 0) * 1440)
                break

        # If we can't board (no valid departure time), skip this route
        if boarding_departure_time is None:
            return improved

        # Check boarding time constraint
        # For Round 0: must be after base_label arrival
        # For transfers: must be after base_label arrival + min_transfer_time
        if earliest_boarding_time is not None:
            # Transfer round: check against earliest_boarding_time
            if boarding_departure_time < earliest_boarding_time:
                return improved
        else:
            # Round 0: check against base_label arrival
            if base_label.arrival_time > boarding_departure_time:
                return improved

        # Traverse all stops after boarding sequence
        for st in route_stop_times_list:
            # Skip stops before or at boarding sequence
            if st["stop_sequence"] <= boarding_sequence:
                continue
            if st["arrival_time"] is None:
                continue

            arrival_time = (
                st["arrival_time"]
                + (st.get("day_offset", 0) * 1440)
            )

            # Normalize stop_id to string for Label
            alighting_stop_id = str(st["stop_id"])

            label = Label(
                arrival_time=arrival_time,
                num_transfers=num_transfers,
                comfort_score=comfort,
                parent_label=base_label,
                route_used=route_id,
                boarding_stop=boarding_stop_id,
                alighting_stop=alighting_stop_id
            )

            # Add label using string stop_id (LabelManager expects strings)
            if self.label_manager.add_label(alighting_stop_id, label):
                improved.add(alighting_stop_id)
                if marked_stops is not None:
                    marked_stops.add(alighting_stop_id)

        return improved