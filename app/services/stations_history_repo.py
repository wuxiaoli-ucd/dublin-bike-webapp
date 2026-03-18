from datetime import datetime, timezone
from sqlalchemy import text
from .db import engine


def _get_reference_time(conn, station_id: int, live_mode: bool):
    if live_mode:
        return datetime.now(timezone.utc).replace(tzinfo=None)

    ref_row = conn.execute(
        text("""
            SELECT MAX(scraped_at) AS ref_time
            FROM availability
            WHERE number = :number
        """),
        {"number": station_id}
    ).mappings().first()

    return ref_row["ref_time"] if ref_row else None


def fetch_station_history_hourly(station_id: int, live_mode: bool = False):
    with engine.connect() as conn:
        ref_time = _get_reference_time(conn, station_id, live_mode)
        if ref_time is None:
            return None

        result = conn.execute(
            text("""
                SELECT
                  DATE_FORMAT(last_update, '%Y-%m-%d %H:00:00') AS bucket,
                  AVG(available_bikes) AS avg_bikes,
                  AVG(available_bike_stands) AS avg_stands,
                  COUNT(*) AS samples
                FROM availability
                WHERE number = :number
                  AND last_update BETWEEN DATE_SUB(:ref_time, INTERVAL 8 HOUR) AND :ref_time
                GROUP BY bucket
                ORDER BY bucket
            """),
            {"number": station_id, "ref_time": ref_time}
        )

        rows = [dict(r) for r in result.mappings()]

    return {
        "station_id": station_id,
        "mode": "hourly",
        "window": "8h",
        "live_mode": live_mode,
        "reference_time": str(ref_time),
        "series": rows,
    }


def fetch_station_history_daily(station_id: int, live_mode: bool = False):
    with engine.connect() as conn:
        ref_time = _get_reference_time(conn, station_id, live_mode)
        if ref_time is None:
            return None

        result = conn.execute(
            text("""
                SELECT
                  DATE(last_update) AS bucket,
                  AVG(available_bikes) AS avg_bikes,
                  AVG(available_bike_stands) AS avg_stands,
                  COUNT(*) AS samples
                FROM availability
                WHERE number = :number
                  AND last_update BETWEEN DATE_SUB(:ref_time, INTERVAL 7 DAY) AND :ref_time
                GROUP BY bucket
                ORDER BY bucket
            """),
            {"number": station_id, "ref_time": ref_time}
        )

        rows = [dict(r) for r in result.mappings()]

    return {
        "station_id": station_id,
        "mode": "daily",
        "window": "7d",
        "live_mode": live_mode,
        "reference_time": str(ref_time),
        "series": rows,
    }