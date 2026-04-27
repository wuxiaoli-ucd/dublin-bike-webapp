import datetime
import json, glob

def inspect_file(path):
    """
    Loads a saved weather JSON file and prints a quick summary.

    Extracts a sample of fields from the first hourly record
    to verify expected structure and keys.
    """
    with open(path) as f:
        payload = json.load(f)

    hours = payload.get("hourly", [])
    print(path, "hourly points:", len(hours))
    if hours:
        h0 = hours[0]
        vals = (
            h0.get("dt"),
            h0.get("temp"),
            h0.get("feels_like"),
            h0.get("pressure"),
            h0.get("humidity"),
            h0.get("wind_speed"),
            h0.get("wind_gust"),
            (h0.get("weather") or [{}])[0].get("id"),
            (h0.get("rain") or {}).get("1h"),
            (h0.get("snow") or {}).get("1h"),
        )
        print("Example vals:", vals)

def main():
    files = sorted(glob.glob("data/weather_*.json"))
    for p in files[-3:]:
        inspect_file(p)

main()