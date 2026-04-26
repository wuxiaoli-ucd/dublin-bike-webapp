import datetime
import json
import os
import traceback

import requests
import dbinfo


def get_weather() -> dict:
    params = {
        "lat": dbinfo.LAT,
        "lon": dbinfo.LON,
        "appid": dbinfo.OWKEY,
        "units": "metric",
        "exclude": "minutely,daily,alerts",
    }
    r = requests.get(dbinfo.OPENWEATHER_URL, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def write_to_file(payload: dict) -> str:
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # UTC timestamp in filename, safe for filesystems
    ts = (
    datetime.datetime.now(datetime.UTC)
    .replace(microsecond=0)
    .isoformat()
    .replace(":", "-")
    )
    path = f"data/weather_{ts}.json"

    with open(path, "w") as f:
        json.dump(payload, f, indent=4)

    return path


def main():
    try:
        payload = get_weather()
        path = write_to_file(payload)
        print(f"Weather JSON downloaded -> {path}")
    except Exception:
        # Print full stack trace so cron logs are useful
        print(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()

