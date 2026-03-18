from flask import Blueprint, jsonify
from app.services.stations_repo import fetch_stations_with_latest_availability

stations_bp = Blueprint("stations_api", __name__)

@stations_bp.route("/stations", methods=["GET"])
def stations():
    """
    Handles GET requests to /api/stations
    Fetches all stations with their latest availability data from the db
    Returns them as JSON for frontend use
    """
    stations = fetch_stations_with_latest_availability()
    return jsonify({"stations": stations})