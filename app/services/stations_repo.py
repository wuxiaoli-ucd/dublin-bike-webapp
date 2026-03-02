from .db import get_conn

def fetch_stations_with_latest_availability(cfg):
    sql = """
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
    """
    conn = get_conn(cfg)
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    conn.close()

    stations = []
    for r in rows:
        stations.append({
            "number": r["number"],
            "name": r["name"],
            "position": {"lat": float(r["position_lat"]), "lng": float(r["position_lng"])},
            "available_bikes": r.get("available_bikes"),
            "available_bike_stands": r.get("available_bike_stands"),
            "bike_stands": r.get("bike_stands"),
            "status": r.get("status"),
            "scraped_at": r.get("scraped_at"),
        })
    return stations