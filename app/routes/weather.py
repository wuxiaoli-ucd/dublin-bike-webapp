from flask import Blueprint, jsonify
from app.services.weather_service import get_current_weather, get_forecast

weather_bp = Blueprint("weather", __name__)


@weather_bp.route("/weather/current")
def current_weather():
    try:
        return jsonify(get_current_weather())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@weather_bp.route("/weather/forecast")
def forecast():
    try:
        return jsonify(get_forecast())
    except Exception as e:
        return jsonify({"error": str(e)}), 500