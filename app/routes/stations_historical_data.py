from flask import jsonify, Blueprint, request
from sqlalchemy import text
from .db_connect import engine
from datetime import datetime, timezone

historical_data_bp = Blueprint("historical_data", __name__)
# Memo: below part will use conor's verson
# # Show all stations in json
# @stations_bp.route('/stations')
# def stations():
#     with engine.connect() as conn:
#         result = conn.execute(text("SELECT * FROM station"))
#         rows = [dict(row) for row in result.mappings()]
#     return jsonify(stations=rows)
#
# # Retrive availability information about a specific station
# @stations_bp.route('/availability/<int:station_id>')
# def get_station(station_id):
#     with engine.connect() as conn:
#         result = conn.execute(
#             text("""
#             SELECT *
#             FROM availability
#             WHERE number = :number
#             ORDER BY last_update DESC
#             LIMIT 1
#             """),
#             {"number": station_id}
#         )
#         row = result.mappings().first()
#
#     if row is None:
#         return jsonify({"error": "Station not found"}), 404
#
#     return jsonify(station=dict(row))

#---------------------------
# NEW: Hourly (last 8 hours)
#---------------------------
@historical_data_bp.route('/availability/<int:station_id>/hourly')
def availability_hourly(station_id):
    #live=true  -> production mode (use current time)
    #live=false -> test mode (default, use MAX(scraped_at) from DB)
    live_mode = request.args.get("live", "false").lower() in ("true", "1", "yes")
    with engine.connect() as conn:
        if live_mode:
            # Use UTC time for consistency(avoid local timezone issues)
            ref_time = datetime.now(timezone.utc).replace(tzinfo=None)
        else:
            ref_row = conn.execute(
                text("""
                            SELECT MAX(scraped_at) AS ref_time
                            FROM availability
                            WHERE number = :number
                            """),
                {"number": station_id}
            ).mappings().first()

            ref_time = ref_row["ref_time"] if ref_row else None
            if ref_time is None:
                return jsonify({"error": "No data for this station"}), 404

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
    return jsonify({
        "station_id": station_id,
        "mode": "hourly",
        "window": "8h",
        "live_mode": live_mode,
        "reference_time": str(ref_time),
        "series": rows
    })

# -----------------------------
# NEW: Daily (last 7 days)
# -----------------------------
@historical_data_bp.route('/availability/<int:station_id>/daily')
def availability_daily(station_id):
    live_mode = request.args.get("live", "false").lower() in ("true", "1", "yes")

    with engine.connect() as conn:
        if live_mode:
            ref_time = datetime.now(timezone.utc).replace(tzinfo=None)
        else:
            ref_row = conn.execute(
                text("""
                SELECT MAX(scraped_at) AS ref_time
                FROM availability
                WHERE number = :number
                """),
                {"number": station_id}
            ).mappings().first()

            ref_time = ref_row["ref_time"] if ref_row else None
            if ref_time is None:
                return jsonify({"error": "No data for this station"}), 404

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

    return jsonify({
        "station_id": station_id,
        "mode": "daily",
        "window": "7d",
        "live_mode": live_mode,
        "reference_time": str(ref_time),
        "series": rows
    })
