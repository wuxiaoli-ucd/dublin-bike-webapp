from flask import Blueprint, jsonify, current_app
from app.services.stations_repo import fetch_stations_with_latest_availability

stations_bp = Blueprint("stations_api", __name__)

@stations_bp.route("/stations", methods=["GET"])
def stations():
    stations = fetch_stations_with_latest_availability(current_app.config)
    return jsonify({"stations": stations})