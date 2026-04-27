from flask import Blueprint, jsonify, request
from app.services.weather_service import get_current_weather, get_forecast

weather_bp = Blueprint("weather", __name__)


@weather_bp.route("/weather/current")
def current_weather():
    """
    Returns a summary of current weather conditions.

    Used by top-right weather widget in the UI

    Response format:
    {
        "weather": "Clouds",
        "temp": 13.2,
        "icon": "03d"
    }

    Data is cached in-memory in the service layer (approx. 10 mins)
      to reduce API calls and improve response time.
    """
    try:
        return jsonify(get_current_weather())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@weather_bp.route("/weather/forecast")
def forecast():
    """
    Returns weather forecast data (hourly and daily).

    Query params:
    - base_time: Unix time used for the forecast

    Response format:
    {
        "hourly": [...],
        "daily": [...]
    }
    """
    try:
        # base_time comes from frontend when user selects "Depart At"
        base_time_raw = request.args.get("base_time")
        base_time = int(base_time_raw) if base_time_raw else None

        return jsonify(get_forecast(base_time=base_time))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500