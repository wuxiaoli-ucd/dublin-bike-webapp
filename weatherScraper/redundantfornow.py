# openweather_local_download.py
import requests, traceback, datetime, time, os, json
import dbinfo

def write_to_file(payload: dict):
    if not os.path.exists("data"):
        os.mkdir("data")

    now = datetime.datetime.utcnow().replace(microsecond=0).isoformat().replace(":", "-")
    path = f"data/weather_{now}Z.json"
    with open(path, "w") as f:
        json.dump(payload, f)
    print(f"Wrote {path}")

def fetch_onecall():
    params = {
        "lat": dbinfo.LAT,
        "lon": dbinfo.LON,
        "appid": dbinfo.OWKEY,
        "units": "metric",
        "exclude": "minutely,daily,alerts"
    }
    r = requests.get(dbinfo.OPENWEATHER_URL, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def main():
    while True:
        try:
            payload = fetch_onecall()
            write_to_file(payload)
            time.sleep(60*60)  # hourly
        except Exception:
            print(traceback.format_exc())
            time.sleep(60)

main()








