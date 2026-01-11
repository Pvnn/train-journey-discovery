from typing import Set
from collections import defaultdict

from services.label_manager import LabelManager, Label
from services.label_manager import filter_routes_by_date


class MCRaptor:
    """
    MC-RAPTOR CORE (Person A)

    - Label-based RAPTOR
    - Uses LabelManager for dominance
    - Produces Labels only (no reconstruction)
    """

    def __init__(
        self,
        stops_data,
        routes_data,
        stop_times_data,
        stop_routes,
        train_metadata,
        stop_routes_mapping,
        query_date
    ):
        self.stops = stops_data
        self.routes = routes_data
        self.stop_times = stop_times_data
        self.stop_routes = stop_routes
        self.train_metadata = train_metadata
        self.stop_routes_mapping = stop_routes_mapping
        self.query_date = query_date

        self.label_manager = LabelManager()

        # route_id -> sorted stop_times
        self.route_stop_times = defaultdict(list)
        for st in self.stop_times:
            self.route_stop_times[st["route_id"]].append(st)

        for rid in self.route_stop_times:
            self.route_stop_times[rid].sort(key=lambda x: x["stop_sequence"])

    # ---------------------------------------------------
    # PUBLIC SEARCH
    # ---------------------------------------------------
    def search(self, source_stop_id, destination_stop_id, departure_time, max_transfers=4):

        source_stop_id = str(source_stop_id)
        destination_stop_id = str(destination_stop_id)

        # ✅ FIX 1: correct initialization
        self.label_manager.initialize_source(source_stop_id, departure_time)

        # Round 0
        marked_stops = self._initialize_round_0(source_stop_id, departure_time)

        # Transfer rounds
        for k in range(1, max_transfers + 1):
            if not marked_stops:
                break
            marked_stops = self._run_round_k(marked_stops, k)

        return self.label_manager.get_pareto_optimal_labels(destination_stop_id)

    # ---------------------------------------------------
    # ROUND 0
    # ---------------------------------------------------
    def _initialize_round_0(self, source_stop_id, departure_time) -> Set[str]:
        marked_stops = set()

        serving_routes = self.stop_routes.get(source_stop_id, [])
        serving_routes = filter_routes_by_date(
            self.routes, serving_routes, self.query_date
        )

        base_label = self.label_manager.get_pareto_optimal_labels(source_stop_id)[0]

        for route_id in serving_routes:
            route_stops = self.stop_routes_mapping.get(route_id, {})
            if source_stop_id not in route_stops:
                continue

            boarding_seq = route_stops[source_stop_id]

            boarding_st = None
            for st in self.route_stop_times[route_id]:
                if (
                    str(st["stop_id"]) == source_stop_id
                    and st["departure_time"] is not None
                    and st["departure_time"] >= departure_time
                ):
                    boarding_st = st
                    break

            if boarding_st is None:
                continue

            improved = self._traverse_route(
                route_id=route_id,
                boarding_stop_id=source_stop_id,
                base_label=base_label,
                boarding_sequence=boarding_seq,
                num_transfers=0
            )

            marked_stops.update(improved)

        return marked_stops

    # ---------------------------------------------------
    # ROUND k > 0
    # ---------------------------------------------------
    def _run_round_k(self, prev_marked: Set[str], round_k: int) -> Set[str]:
        new_marked = set()

        for stop_id in prev_marked:
            labels = self.label_manager.get_pareto_optimal_labels(stop_id)

            route_ids = self.stop_routes.get(stop_id, [])
            route_ids = filter_routes_by_date(
                self.routes, route_ids, self.query_date
            )

            for label in labels:
                for route_id in route_ids:
                    route_stops = self.stop_routes_mapping.get(route_id, {})
                    if stop_id not in route_stops:
                        continue

                    self._traverse_route(
                        route_id=route_id,
                        boarding_stop_id=stop_id,
                        base_label=label,
                        boarding_sequence=route_stops[stop_id],
                        num_transfers=round_k,
                        marked_stops=new_marked
                    )

        return new_marked

    # ---------------------------------------------------
    # ROUTE TRAVERSAL
    # ---------------------------------------------------
    def _traverse_route(
        self,
        route_id,
        boarding_stop_id,
        base_label,
        boarding_sequence,
        num_transfers,
        marked_stops=None
    ):
        improved = set()

        for st in self.route_stop_times[route_id]:
            if st["stop_sequence"] <= boarding_sequence:
                continue
            if st["arrival_time"] is None:
                continue

            arrival = st["arrival_time"] + (st.get("day_offset", 0) * 1440)

            label = Label(
                arrival_time=arrival,
                num_transfers=num_transfers,
                comfort_score=0.0,
                parent_label=base_label,
                route_used=route_id,
                boarding_stop=boarding_stop_id,
                alighting_stop=str(st["stop_id"])
            )

            if self.label_manager.add_label(str(st["stop_id"]), label):
                improved.add(str(st["stop_id"]))
                if marked_stops is not None:
                    marked_stops.add(str(st["stop_id"]))

        return improved
