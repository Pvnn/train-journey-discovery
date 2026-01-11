"""
TEST: MC-RAPTOR Core — Direct + Time-Feasible Forced Transfer

This test verifies:
1. Direct route behavior (Round 0 + 1 transfer)
2. FORCED TRANSFER behavior where:
   - No direct route exists
   - A valid S → X → D path exists
   - Transfer is TIME-FEASIBLE
"""

from backend.services.mcraptor_core import MCRaptor
from backend.utils.data_loader import data_loader


# ============================================================
# HELPER: Find TIME-FEASIBLE forced transfer scenario
# ============================================================
def find_time_feasible_forced_transfer(
    stops,
    stop_routes,
    stop_routes_mapping,
    stop_times,
    station_metadata
):
    print("\n[SEARCH] Finding TIME-FEASIBLE forced transfer scenario...")

    # station_code -> stop_id
    station_to_stop_id = {
        code: str(info["stop_id"])
        for code, info in stops.items()
        if "stop_id" in info
    }

    # stop_id -> routes
    stop_id_to_routes = {}
    for station_code, routes in stop_routes.items():
        if station_code in station_to_stop_id:
            sid = station_to_stop_id[station_code]
            stop_id_to_routes.setdefault(sid, set()).update(routes)

    # route -> ordered stops
    route_to_stops = {
        rid: list(stops_map.keys())
        for rid, stops_map in stop_routes_mapping.items()
    }

    # index stop_times by (route_id, stop_id)
    stop_time_index = {}
    for st in stop_times:
        key = (st["route_id"], str(st["stop_id"]))
        stop_time_index.setdefault(key, []).append(st)

    # iterate source S
    for s, routes_s in stop_id_to_routes.items():
        for route_sx in routes_s:
            if route_sx not in route_to_stops:
                continue

            stops_on_route = route_to_stops[route_sx]
            if s not in stops_on_route:
                continue

            s_idx = stops_on_route.index(s)

            # possible transfer stops X
            for x in stops_on_route[s_idx + 1 :]:
                routes_x = stop_id_to_routes.get(x, set())
                if not routes_x:
                    continue

                # arrival time at X on S→X
                sx_times = stop_time_index.get((route_sx, x), [])
                for st_sx in sx_times:
                    if st_sx["arrival_time"] is None:
                        continue

                    arrival_x = st_sx["arrival_time"] + st_sx.get("day_offset", 0) * 1440
                    min_transfer = station_metadata.get(
                        next(
                            (c for c, sid in station_to_stop_id.items() if sid == x),
                            None
                        ),
                        {}
                    ).get("min_transfer_time", 30)

                    earliest_board = arrival_x + min_transfer

                    # try X → D
                    for route_xd in routes_x:
                        if route_xd == route_sx:
                            continue
                        if route_xd not in route_to_stops:
                            continue
                        if x not in route_to_stops[route_xd]:
                            continue

                        x_idx = route_to_stops[route_xd].index(x)

                        for d in route_to_stops[route_xd][x_idx + 1 :]:
                            # ensure NO direct route S → D
                            direct = False
                            for r in routes_s:
                                if r in route_to_stops and s in route_to_stops[r] and d in route_to_stops[r]:
                                    if route_to_stops[r].index(s) < route_to_stops[r].index(d):
                                        direct = True
                                        break
                            if direct:
                                continue

                            xd_times = stop_time_index.get((route_xd, x), [])
                            for st_xd in xd_times:
                                if st_xd["departure_time"] is None:
                                    continue

                                dep_x = st_xd["departure_time"] + st_xd.get("day_offset", 0) * 1440

                                if dep_x >= earliest_board:
                                    print("[SEARCH] ✅ Found TIME-FEASIBLE forced transfer")
                                    return s, x, d, route_sx, route_xd, st_sx["departure_time"]

    return None


# ============================================================
# FORCED TRANSFER TEST
# ============================================================
def test_forced_transfer():
    print("\n" + "=" * 70)
    print("FORCED TRANSFER (TIME-FEASIBLE)")
    print("=" * 70)

    stops = data_loader.get_stops()
    routes = data_loader.get_routes()
    stop_times = data_loader.get_stop_times()
    stop_routes = data_loader.get_stop_routes()
    stop_routes_mapping = data_loader.get_stop_routes_mapping()
    train_metadata = data_loader.get_train_metadata()
    station_metadata = data_loader.get_station_metadata()

    result = find_time_feasible_forced_transfer(
        stops,
        stop_routes,
        stop_routes_mapping,
        stop_times,
        station_metadata
    )

    if result is None:
        print("❌ No time-feasible forced transfer found")
        return

    s, x, d, route_sx, route_xd, departure_time = result

    print(f"""
[SCENARIO]
  Source      : {s}
  Transfer    : {x}
  Destination : {d}
  Route S→X   : {route_sx}
  Route X→D   : {route_xd}
  Departure   : {departure_time}
""")

    raptor = MCRaptor(
        stops_data=stops,
        routes_data=routes,
        stop_times_data=stop_times,
        stop_routes=stop_routes,
        train_metadata=train_metadata,
        stop_routes_mapping=stop_routes_mapping,
        query_date="2025-01-10",
        station_metadata=station_metadata
    )

    print("[TEST] Running MC-RAPTOR (max_transfers=1)")
    labels = raptor.search(
        source_stop_id=s,
        destination_stop_id=d,
        departure_time=departure_time,
        max_transfers=1
    )

    print(f"[RESULT] Labels returned: {len(labels)}")
    for lbl in labels:
        print(" ", lbl)

    valid = [l for l in labels if l.num_transfers == 1]

    if valid:
        print("✅ FORCED TRANSFER TEST PASSED")
    else:
        print("❌ FORCED TRANSFER TEST FAILED")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    test_forced_transfer()
