from datetime import datetime, timezone
from sqlalchemy import text
from .db import engine


def _get_reference_time(conn, station_id: int, live_mode: bool):
    """
    Determines the latest time that should be used as the end of the chart window.

    In live mode, use the current UTC time.
    In stored mode, use the most recent scraped record for this station.

    Using the latest scraped timestamp in stored mode prevents gaps caused by
    comparing historical data against the real current time.
    """
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
    """
    Returns the last 8 hourly availability buckets for a station.

    Each bucket contains:
    - Average available bikes
    - Average available bike stands
    - Number of records sampled

    Used by the frontend historical chart in "Hours" mode.
    """
    with engine.connect() as conn:
        ref_time = _get_reference_time(conn, station_id, live_mode)
        if ref_time is None:
            return None

        result = conn.execute(
            text("""
                SELECT *
                FROM (
                    SELECT
                      DATE_FORMAT(last_update, '%Y-%m-%d %H:00:00') AS bucket,
                      AVG(available_bikes) AS avg_bikes,
                      AVG(available_bike_stands) AS avg_stands,
                      COUNT(*) AS samples
                    FROM availability
                    WHERE number = :number
                      AND last_update <= :ref_time
                    GROUP BY bucket
                    ORDER BY bucket DESC
                    LIMIT 8
                ) AS last_8_hours
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
    """
    Returns the last 7 daily availability buckets for a station.

    Each bucket aggregates all samples from that date.

    Used by the frontend historical chart in "Days" mode.
    """
    with engine.connect() as conn:
        ref_time = _get_reference_time(conn, station_id, live_mode)
        if ref_time is None:
            return None

        result = conn.execute(
            text("""
                SELECT *
                FROM (
                    SELECT
                      DATE(last_update) AS bucket,
                      AVG(available_bikes) AS avg_bikes,
                      AVG(available_bike_stands) AS avg_stands,
                      COUNT(*) AS samples
                    FROM availability
                    WHERE number = :number
                      AND last_update <= :ref_time
                    GROUP BY bucket
                    ORDER BY bucket DESC
                    LIMIT 7
                ) AS last_7_days
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