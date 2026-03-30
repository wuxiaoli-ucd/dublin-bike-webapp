import os
import time
import requests

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