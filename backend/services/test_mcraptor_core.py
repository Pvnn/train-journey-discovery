from backend.utils.data_loader import data_loader
from backend.services.mcraptor_core import MCRaptor


def test_mcraptor_core():
    print("\n[TEST] Loading data...")

    stops = data_loader.get_stops()
    routes = data_loader.get_routes()
    stop_times = data_loader.get_stop_times()
    stop_routes = data_loader.get_stop_routes()
    stop_routes_mapping = data_loader.get_stop_routes_mapping()
    train_metadata = data_loader.get_train_metadata()

    print("[TEST] Initializing MCRaptor...")

    raptor = MCRaptor(
        stops_data=stops,
        routes_data=routes,
        stop_times_data=stop_times,
        stop_routes=stop_routes,
        train_metadata=train_metadata,
        stop_routes_mapping=stop_routes_mapping,
        query_date="2025-01-10"
    )

    print("[TEST] Selecting valid route + boarding stop...")

    # Pick first route with >= 2 stops
    route_id, stops_map = next(iter(stop_routes_mapping.items()))
    stop_ids = list(stops_map.keys())

    source_stop_id = int(stop_ids[0])
    destination_stop_id = int(stop_ids[1])

    print("[DEBUG] Route:", route_id)
    print("[DEBUG] Source stop_id:", source_stop_id)
    print("[DEBUG] Destination stop_id:", destination_stop_id)

    # IMPORTANT: use EARLY time
    departure_time = 600  # 10:00 AM

    print("[DEBUG] Departure time:", departure_time)

    print("[TEST] Running search...")
    labels = raptor.search(
        source_stop_id=source_stop_id,
        destination_stop_id=destination_stop_id,
        departure_time=departure_time,
        max_transfers=2
    )

    print("[TEST] Labels returned:", len(labels))

    for label in labels:
        print(label)


if __name__ == "__main__":
    test_mcraptor_core()
