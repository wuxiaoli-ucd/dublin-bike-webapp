from flask import Blueprint, request, jsonify, current_app

from app.utils.geo import k_nearest_stations
from app.utils.time import duration_to_seconds
from app.services.google_routes import compute_route
from app.services.stations_repo import fetch_stations_with_latest_availability

routing_bp = Blueprint("routing", __name__)


K_CANDIDATES = 10 # number of candidate closest stations 
MIN_SAVING_SECONDS = 30  # amount of time faster in order to choose bike


def station_to_point(station: dict) -> dict:
    """Convert station object to {lat, lng}."""
    return {"lat": station["position"]["lat"], "lng": station["position"]["lng"]}


def best_station_by_walk_time(origin_point: dict, candidates: list[dict], mode: str = "TO_STATION"):
    """
    Pick the best station by walking duration among candidates.

    origin_point: {lat, lng}
    candidates: station dicts with station["position"]["lat|lng"]

    mode:
      - "TO_STATION": walk origin -> station
      - "FROM_STATION": walk station -> origin
    """
    best_station = None
    best_leg = None
    best_s = None

    for st in candidates:
        st_point = station_to_point(st)

        if mode == "TO_STATION":
            leg = compute_route(origin_point, st_point, "WALK")
        else:
            leg = compute_route(st_point, origin_point, "WALK")

        if not leg: # skip if no route returned by Google
            continue

        s = duration_to_seconds(leg["duration"])

        if best_s is None or s < best_s:
            best_station = st
            best_leg = leg
            best_s = s

    return best_station, best_leg, best_s


@routing_bp.route("/route", methods=["POST"])
def route():
    """
    Manages bikeshare route planning.

    Determines whether a journey should be WALK_ONLY or BIKESHARE by:
    - Comparing direct walking time
    - Selecting availabile nearest stations
    - Evaluating real walking durations
    - Computing bike leg duration
    - Applying a minimum time-saving threshold

    Returns structured JSON for frontend map rendering.
    """
    data = request.get_json(force=True) or {}

    start = data.get("start")
    destination = data.get("destination")

    if not start or not destination:
        return jsonify({"error": "start and destination are required"}), 400

    if (
        not isinstance(start, dict)
        or not isinstance(destination, dict)
        or "lat" not in start or "lng" not in start
        or "lat" not in destination or "lng" not in destination
    ):
        return jsonify({"error": "start and destination must be objects {lat, lng}"}), 400

    # 1) Direct walk route (always compute once)
    direct_walk = compute_route(start, destination, "WALK")

    if not direct_walk:
        return jsonify({"error": "Routing service unavailable"}), 503
    
    direct_walk_s = duration_to_seconds(direct_walk["duration"])

    # 2) Load stations (latest availability)
    stations = fetch_stations_with_latest_availability(current_app.config)

    # 3) Build candidate lists (haversine shortlist, then filter by availability)
    depart_candidates = [
        s for s in k_nearest_stations(start, stations, K_CANDIDATES)
        if s.get("status") == "OPEN" and int(s.get("available_bikes") or 0) > 0
    ]
    arrival_candidates = [
        s for s in k_nearest_stations(destination, stations, K_CANDIDATES)
        if s.get("status") == "OPEN" and int(s.get("available_bike_stands") or 0) > 0
    ]

    if not depart_candidates or not arrival_candidates:
        # No feasible bikeshare route -> walk only
        return jsonify({
            "mode": "WALK_ONLY",
            "reason": "NO_AVAILABLE_STATIONS",
            "route": direct_walk,
            "totals": {"durationSeconds": direct_walk_s},
        })

    # 4) Pick best stations by real walking time
    station_a, part1, part1_s = best_station_by_walk_time(start, depart_candidates, mode="TO_STATION")
    station_b, part3, part3_s = best_station_by_walk_time(destination, arrival_candidates, mode="FROM_STATION")

    if not station_a or not station_b:
        return jsonify({
            "mode": "WALK_ONLY",
            "reason": "NO_AVAILABLE_STATIONS",
            "route": direct_walk,
            "totals": {"durationSeconds": direct_walk_s},
        })

    # If both ends choose the same station, cycling makes no sense
    if station_a.get("number") is not None and station_a.get("number") == station_b.get("number"):
        return jsonify({
            "mode": "WALK_ONLY",
            "reason": "SAME_STATION",
            "route": direct_walk,
            "stationA": station_a,
            "stationB": station_b,
            "totals": {"durationSeconds": direct_walk_s},
        })

    # 5) Bike leg 
    a_point = station_to_point(station_a)
    b_point = station_to_point(station_b)
    part2 = compute_route(a_point, b_point, "BICYCLE")

    if not part2: # if bike route fails, fall back to walk only
        return jsonify({
            "mode": "WALK_ONLY",
            "reason": "BIKE_LEG_UNAVAILABLE",
            "route": direct_walk,
            "stationA": station_a,
            "stationB": station_b,
            "totals": {"durationSeconds": direct_walk_s},
        })

    part2_s = duration_to_seconds(part2["duration"])

    bikeshare_s = part1_s + part2_s + part3_s

    # 6) Choose WALK_ONLY if not meaningfully better to bike
    if direct_walk_s <= bikeshare_s + MIN_SAVING_SECONDS:
        return jsonify({
            "mode": "WALK_ONLY",
            "reason": "WALK_FASTER_OR_SIMILAR",
            "route": direct_walk,
            "stationA": station_a,
            "stationB": station_b,
            "totals": {"durationSeconds": direct_walk_s},
        })

    # 7) Return bikeshare plan
    return jsonify({
        "mode": "BIKESHARE",
        "stationA": station_a,
        "stationB": station_b,
        "legs": {
            "walkToStation": part1,          # already computed in station selection
            "cycleBetweenStations": part2,
            "walkToDestination": part3,      # already computed in station selection
        },
        "totals": {
            "durationSeconds": bikeshare_s
        }
    })