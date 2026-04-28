import glob
import json
import datetime
from sqlalchemy import create_engine, text
import dbinfo

def make_engine():
    """
    Creates an SQLAlchemy engine for the OpenWeather MySQL database.
    """
    return create_engine(
        f"mysql+pymysql://{dbinfo.MYSQL_USER}:{dbinfo.MYSQL_PASSWORD}"
        f"@{dbinfo.MYSQL_HOST}:{dbinfo.MYSQL_PORT}/{dbinfo.MYSQL_DB}",
        echo=True,
        future=True
    )

def row_from_payload(payload: dict):
    """
    Converts the first hourly forecast item into a database row.

    Only the first hourly item is inserted because this script stores a snapshot
    of the nearest available hourly weather at scrape time.
    """
    h = (payload.get("hourly") or [None])[0]
    if not h:
        return None

    dt_utc = datetime.datetime.utcfromtimestamp(h["dt"])

    return {
        "dt": dt_utc,
        "temp": h.get("temp"),
        "feels_like": h.get("feels_like"),
        "pressure": h.get("pressure"),
        "humidity": h.get("humidity"),
        "wind_speed": h.get("wind_speed"),
        "wind_gust": h.get("wind_gust"),
        "weather_id": (h.get("weather") or [{}])[0].get("id"),
        "rain_1h": (h.get("rain") or {}).get("1h"),
        "snow_1h": (h.get("snow") or {}).get("1h"),
    }

def upsert_weather(engine, row: dict):
    """
    Inserts or updates one weather_hourly row.

    dt is the primary key, so ON DUPLICATE KEY UPDATE prevents duplicate
    rows when the script is run more than once for the same forecast hour.
    """
    

    sql = text("""
      INSERT INTO weather_hourly
      (dt, temp, feels_like, pressure, humidity, wind_speed, wind_gust, weather_id, rain_1h, snow_1h)
      VALUES
      (:dt, :temp, :feels_like, :pressure, :humidity, :wind_speed, :wind_gust, :weather_id, :rain_1h, :snow_1h)
      ON DUPLICATE KEY UPDATE
        temp=VALUES(temp),
        feels_like=VALUES(feels_like),
        pressure=VALUES(pressure),
        humidity=VALUES(humidity),
        wind_speed=VALUES(wind_speed),
        wind_gust=VALUES(wind_gust),
        weather_id=VALUES(weather_id),
        rain_1h=VALUES(rain_1h),
        snow_1h=VALUES(snow_1h);
    """)
    with engine.begin() as conn:
        conn.execute(sql, row)

def main():
    engine = make_engine()

    files = sorted(glob.glob("data/weather_*.json"))
    if not files:
        print("No weather JSON files found in data/. Run s01 or s03 first.")
        return

    latest = files[-1]
    with open(latest) as f:
        payload = json.load(f)

    row = row_from_payload(payload)
    if row is None:
        print("No hourly data found in JSON.")
        return

    upsert_weather(engine, row)
    print("Inserted/updated:", row["dt"])

main()