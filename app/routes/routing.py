from flask import Blueprint, request, jsonify, current_app

from app.utils.geo import k_nearest_stations
from app.utils.time import duration_to_seconds
from app.services.google_routes import compute_route
from app.services.stations_repo import fetch_stations_with_latest_availability
from app.services.prediction_service import predict_from_strings

routing_bp = Blueprint("routing", __name__)


K_CANDIDATES = 10 # number of candidate closest stations, has a fair impact on route gen time (10 seems to be the best compromise)
MIN_SAVING_SECONDS = 30  # amount of time faster in order to choose bike

MIN_PREDICTED_BIKES = 4
MIN_PREDICTED_DOCKS = 4

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


@routing_bp.route("route", methods=["POST"])
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
    departure_mode = data.get("departureMode", "leave_now")
    date_str = data.get("date")
    time_str = data.get("time")

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
    stations = fetch_stations_with_latest_availability()

    # 3) Initial nearest-station shortlist (haversine shortlist, then filter by availability)
    nearest_depart = [
        s for s in k_nearest_stations(start, stations, K_CANDIDATES)
        if s.get("status") == "OPEN"
    ]
    nearest_arrival = [
        s for s in k_nearest_stations(destination, stations, K_CANDIDATES)
        if s.get("status") == "OPEN"
    ]

    # 4) Filter by current or predicted availability
    if departure_mode == "depart_at":
        depart_candidates = add_predictions_to_candidates(
            nearest_depart, date_str, time_str, kind="START"
        )
        arrival_candidates = add_predictions_to_candidates(
            nearest_arrival, date_str, time_str, kind="END"
        )
    else:
        depart_candidates = [
            s for s in nearest_depart
            if int(s.get("available_bikes") or 0) > 0
        ]
        arrival_candidates = [
            s for s in nearest_arrival
            if int(s.get("available_bike_stands") or 0) > 0
        ]

    if not depart_candidates or not arrival_candidates:
        return jsonify({
            "mode": "WALK_ONLY",
            "reason": "NO_AVAILABLE_STATIONS",
            "route": direct_walk,
            "totals": {"durationSeconds": direct_walk_s},
        })


    # 5) Pick best stations by real walking time
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

    # 6) Bike leg 
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

    # 7) Choose WALK_ONLY if not meaningfully better to bike
    if direct_walk_s <= bikeshare_s + MIN_SAVING_SECONDS:
        return jsonify({
            "mode": "WALK_ONLY",
            "reason": "WALK_FASTER_OR_SIMILAR",
            "route": direct_walk,
            "stationA": station_a,
            "stationB": station_b,
            "totals": {"durationSeconds": direct_walk_s},
        })

    # 8) Return bikeshare plan
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


def add_predictions_to_candidates(candidates: list[dict], date_str: str, time_str: str, kind: str):
    """
    Adds prediction fields onto each station dict and returns only stations
    meeting the threshold.
    """
    filtered = []

    for station in candidates:
        try:
            prediction = predict_from_strings(
                station_id=int(station["number"]),
                date_str=date_str,
                time_str=time_str,
            )

            station["predicted_bikes"] = prediction["predicted_bikes"]
            station["predicted_docks"] = prediction["predicted_docks"]

            if kind == "START" and prediction["predicted_bikes"] >= MIN_PREDICTED_BIKES:
                filtered.append(station)

            elif kind == "END" and prediction["predicted_docks"] >= MIN_PREDICTED_DOCKS:
                filtered.append(station)

        except Exception:
            # skip stations that fail prediction
            continue

    return filtered