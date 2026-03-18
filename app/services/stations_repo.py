from sqlalchemy import text
from .db import engine


def fetch_stations_with_latest_availability():
    sql = text("""
    SELECT
      s.number,
      s.name,
      s.position_lat,
      s.position_lng,
      a.available_bikes,
      a.available_bike_stands,
      a.bike_stands,
      a.status,
      a.scraped_at
    FROM station s
    LEFT JOIN (
      SELECT a1.*
      FROM availability a1
      JOIN (
        SELECT number, MAX(scraped_at) AS max_scraped_at
        FROM availability
        GROUP BY number
      ) latest
      ON latest.number = a1.number AND latest.max_scraped_at = a1.scraped_at
    ) a
    ON a.number = s.number
    """)

    with engine.connect() as conn:
        rows = conn.execute(sql).mappings().all()

    return [
        {
            "number": r["number"],
            "name": r["name"],
            "position": {
                "lat": float(r["position_lat"]),
                "lng": float(r["position_lng"]),
            },
            "available_bikes": r["available_bikes"],
            "available_bike_stands": r["available_bike_stands"],
            "bike_stands": r["bike_stands"],
            "status": r["status"],
            "scraped_at": r["scraped_at"],
        }
        for r in rows
    ]