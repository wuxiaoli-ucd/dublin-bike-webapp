from flask import Blueprint, jsonify, request
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
        base_time_raw = request.args.get("base_time")
        base_time = int(base_time_raw) if base_time_raw else None

        return jsonify(get_forecast(base_time=base_time))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500