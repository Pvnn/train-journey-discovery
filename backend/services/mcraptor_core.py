import json
import os
from collections import defaultdict


class MCRaptor:
    """
    MC-RAPTOR Core Algorithm (Person A)

    Responsibilities:
    - Load preprocessed timetable data
    - Run RAPTOR rounds (Round 0 + transfers)
    - Track earliest arrival times
    - Track minimal route info for later reconstruction
    - Return SIMPLE results (arrival_time, num_transfers, route_id)

    Does NOT:
    - Create Label objects
    - Do dominance via LabelManager
    - Reconstruct paths
    """

    def __init__(self, data_dir: str):
        self.data_dir = data_dir

        # Loaded data
        self.stops = {}
        self.routes = {}
        self.stop_times = []
        self.stop_routes_mapping = {}

        # RAPTOR state
        self.tau = {}              # tau[k][stop_id] = arrival_time
        self.marked_stops = {}     # marked_stops[k] = set(stop_id)
        self.best_route = {}       # best info for destination

        self._load_data()

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def _load_data(self):
        self.stops = self._load_json("stops.json")
        self.routes = self._load_json("routes.json")
        self.stop_times = self._load_json("stop_times.json")
        self.stop_routes_mapping = self._load_json("stop_routes_mapping.json")

    def _load_json(self, filename):
        path = os.path.join(self.data_dir, filename)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def search(self, source_stop_id, destination_stop_id, departure_time, max_rounds=4):
        """
        Run MC-RAPTOR search.

        Returns:
        List of dicts:
        {
          'arrival_time': int,
          'num_transfers': int,
          'route_id': str
        }
        """

        self.tau = {}
        self.marked_stops = {}
        self.best_route = {}

        # Round 0
        self._initialize_round_0(source_stop_id, departure_time)

        # Subsequent rounds
        for k in range(1, max_rounds + 1):
            self._run_round_k(k)
            if not self.marked_stops.get(k):
                break

        # Collect destination results
        results = []
        for k, arrivals in self.tau.items():
            if destination_stop_id in arrivals:
                results.append({
                    "arrival_time": arrivals[destination_stop_id],
                    "num_transfers": k,
                    "route_id": self.best_route[destination_stop_id]["route_id"]
                })

        return results

    # ------------------------------------------------------------------
    # Round 0 (no transfers)
    # ------------------------------------------------------------------

    def _initialize_round_0(self, source_stop_id, departure_time):
        self.tau[0] = {source_stop_id: departure_time}
        self.marked_stops[0] = {source_stop_id}

        # Find all routes serving the source
        for route_id, stops in self.stop_routes_mapping.items():
            if str(source_stop_id) not in stops:
                continue

            boarding_seq = stops[str(source_stop_id)]

            # Find departure time at source
            for st in self.stop_times:
                if (
                    st["route_id"] == route_id and
                    st["stop_id"] == source_stop_id and
                    st["departure_time"] is not None and
                    st["departure_time"] >= departure_time
                ):
                    self._traverse_route(
                        route_id,
                        source_stop_id,
                        st["departure_time"],
                        round_k=0
                    )
                    break

    # ------------------------------------------------------------------
    # Round k >= 1 (with transfers)
    # ------------------------------------------------------------------

    def _run_round_k(self, k):
        TRANSFER_BUFFER = 30

        self.tau[k] = dict(self.tau[k - 1])
        self.marked_stops[k] = set()

        for stop_id in self.marked_stops[k - 1]:
            arrival_time = self.tau[k - 1][stop_id]

            for route_id, stops in self.stop_routes_mapping.items():
                if str(stop_id) not in stops:
                    continue

                for st in self.stop_times:
                    if (
                        st["route_id"] == route_id and
                        st["stop_id"] == stop_id and
                        st["departure_time"] is not None and
                        st["departure_time"] >= arrival_time + TRANSFER_BUFFER
                    ):
                        self._traverse_route(
                            route_id,
                            stop_id,
                            st["departure_time"],
                            round_k=k
                        )
                        break

    # ------------------------------------------------------------------
    # Route traversal
    # ------------------------------------------------------------------

    def _traverse_route(self, route_id, boarding_stop_id, boarding_time, round_k):
        boarding_seq = self.stop_routes_mapping[route_id][str(boarding_stop_id)]

        for st in self.stop_times:
            if st["route_id"] != route_id:
                continue

            if st["stop_sequence"] <= boarding_seq:
                continue

            if st["arrival_time"] is None:
                continue

            arrival = st["arrival_time"] + (st.get("day_offset", 0) * 1440)
            stop_id = st["stop_id"]

            old_arrival = self.tau[round_k].get(stop_id)

            if old_arrival is None or arrival < old_arrival:
                self.tau[round_k][stop_id] = arrival
                self.marked_stops[round_k].add(stop_id)

                self.best_route[stop_id] = {
                    "arrival_time": arrival,
                    "num_transfers": round_k,
                    "route_id": route_id,
                    "boarding_stop": boarding_stop_id,
                    "parent_stop": boarding_stop_id
                }
