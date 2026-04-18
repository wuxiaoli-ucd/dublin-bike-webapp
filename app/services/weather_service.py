import os
import time
import requests
from datetime import datetime, timezone, timedelta

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

DUBLIN_LAT = 53.3498
DUBLIN_LON = -6.2603
UNITS = "metric"

ONECALL_URL = "https://api.openweathermap.org/data/3.0/onecall"

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
        # keep daily, only exclude what you do not need
        "exclude": "minutely,alerts"
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
        "temp": current["temp"],
        "icon": current["weather"][0]["icon"]
    }


def get_hourly_forecast(base_time: int | None = None, count: int = 4):
    """
    Returns hourly forecast entries starting from:
    - now, if base_time is None
    - the first hourly entry at or after base_time, if provided
    """
    data = _fetch_weather()
    hourly = data.get("hourly", [])

    if not hourly:
        return []

    if base_time is None:
        selected = hourly[:count]
    else:
        start_index = next(
            (i for i, item in enumerate(hourly) if item["dt"] >= base_time),
            None
        )

        if start_index is None:
            # if base_time is beyond available hourly forecast, return empty
            return []

        selected = hourly[start_index:start_index + count]

    return [
        {
            "time": item["dt"],
            "temp": item["temp"],
            "icon": item["weather"][0]["icon"],
            "pop": item.get("pop", 0)
        }
        for item in selected
    ]


def get_daily_forecast(count: int = 4):
    """
    Returns Today + next 3 days by default.
    """
    data = _fetch_weather()
    daily = data.get("daily", [])[:count]

    return [
        {
            "time": item["dt"],
            "min_temp": item["temp"]["min"],
            "max_temp": item["temp"]["max"],
            "icon": item["weather"][0]["icon"],
            "pop": item.get("pop", 0)
        }
        for item in daily
    ]


def get_forecast(base_time: int | None = None):
    """
    Returns both hourly and daily forecast data.
    If base_time is provided, hourly forecast begins from that time.
    """
    return {
        "hourly": get_hourly_forecast(base_time=base_time, count=4),
        "daily": get_daily_forecast(count=4)
    }


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

    max_date = (now_local + timedelta(days=3)).date()
    if target_dt.date() > max_date:
        raise ValueError("Predictions are only available up to 3 days ahead")

    closest_item = min(
        hourly,
        key=lambda item: abs(
            datetime.fromtimestamp(item["dt"], tz=timezone.utc).astimezone() - target_dt
        )
    )

    return {
        "avg_air_temperature": float(closest_item["temp"]),
        "avg_relative_humidity": float(closest_item["humidity"]),
    }