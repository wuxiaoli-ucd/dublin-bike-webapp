from flask import Blueprint, jsonify, request
from app.services.stations_history_repo import fetch_station_history_hourly, fetch_station_history_daily

stations_history_bp = Blueprint("stations_history_api", __name__)


@stations_history_bp.route("/availability/<int:station_id>/hourly", methods=["GET"])
def availability_hourly(station_id):
    """
    Returns hourly historical availability for a station.

    Query params:
    - live (optional): if true, uses recently scraped data instead of previously
        stored data from a static db

    Response:
        {"time": "...", "available_bikes": ..., "available_bike_stands": ...}, ...

    Default mode is used for testing purposes. 
    """
    live_mode = request.args.get("live", "false").lower() in ("true", "1", "yes") # whether we use realtime or from db

    data = fetch_station_history_hourly(station_id, live_mode=live_mode)
    if data is None:
        return jsonify({"error": "No data for this station"}), 404

    return jsonify(data)


@stations_history_bp.route("/availability/<int:station_id>/daily", methods=["GET"])
def availability_daily(station_id):
    """
    Returns daily historical availability for a station.

    Query params:
    - live (optional): same behaviour as hourly endpoint

    Response:
        {"date": "...", "available_bikes": ..., "available_bike_stands": ...}, ...
    """
    live_mode = request.args.get("live", "false").lower() in ("true", "1", "yes")

    data = fetch_station_history_daily(station_id, live_mode=live_mode)
    if data is None:
        return jsonify({"error": "No data for this station"}), 404

    return jsonify(data)