import os
import time
import requests
from datetime import datetime, timezone, timedelta

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
# Dublin city centre
DUBLIN_LAT = 53.3498
DUBLIN_LON = -6.2603
UNITS = "metric"

ONECALL_URL = "https://api.openweathermap.org/data/3.0/onecall"


# cache for shared backend use
_weather_cache = {
    "data": None,
    "timestamp": 0
}

CACHE_SECONDS = 600  # 10 minutes


def _fetch_weather():
    now = time.time()

    if _weather_cache["data"] and (now - _weather_cache["timestamp"] < CACHE_SECONDS):
        return _weather_cache["data"]

    params = {
        "lat": DUBLIN_LAT,
        "lon": DUBLIN_LON,
        "appid": WEATHER_API_KEY,
        "units": UNITS,
        "exclude": "minutely,daily,alerts"
    }

    response = requests.get(ONECALL_URL, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    _weather_cache["data"] = data
    _weather_cache["timestamp"] = now

    return data


def get_current_weather():
    data = _fetch_weather()
    current = data["current"]

    return {
        "weather": current["weather"][0]["main"],
        "temp": current["temp"]
    }


def get_forecast():
    data = _fetch_weather()
    hourly = data["hourly"][:4]

    return [
        {
            "time": item["dt"],
            "temp": item["temp"],
            "icon": item["weather"][0]["icon"],
            "pop": item.get("pop", 0)
        }
        for item in hourly
    ]


def get_prediction_weather(target_dt: datetime):
    """
    Gets forecast data
    Finds closest time match
    Translates to model features
    """
    
    data = _fetch_weather()
    hourly = data.get("hourly", [])

    if not hourly:
        raise ValueError("No hourly forecast data available")

    if target_dt.tzinfo is None:
        target_dt = target_dt.replace(tzinfo=timezone.utc).astimezone()

    now_local = datetime.now().astimezone()
    if target_dt < now_local:
        raise ValueError("Prediction datetime must be in the future")

    if target_dt > now_local + timedelta(days=3):
        raise ValueError("Predictions are only available up to 3 days ahead")

    best_match = None
    best_diff = None

    for item in hourly:
        forecast_dt = datetime.fromtimestamp(item["dt"], tz=timezone.utc).astimezone()
        diff = abs((forecast_dt - target_dt).total_seconds())

        if best_diff is None or diff < best_diff:
            best_diff = diff
            best_match = item

    return {
        "avg_air_temperature": float(best_match["temp"]),
        "avg_relative_humidity": float(best_match["humidity"]),
    }