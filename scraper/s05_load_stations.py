import requests
import traceback
import json
from sqlalchemy import text
import scraper.dbinfo as dbinfo
from app.services.db import engine


def stations_to_db(raw_text, in_engine):
    stations = json.loads(raw_text)

    print(type(stations), len(stations))

    with in_engine.connect() as conn:
        for station in stations:
            vals = (
                int(station.get("number")),
                station.get("name"),
                station.get("address"),
                float(station.get("position").get("lat")),
                float(station.get("position").get("lng")),
                bool(station.get("banking")),
                bool(station.get("bonus")),
            )

            conn.execute(text("""
                INSERT INTO station
                (number, name, address, position_lat, position_lng, banking, bonus)
                VALUES
                (:number, :name, :address, :lat, :lng, :banking, :bonus)
                ON DUPLICATE KEY UPDATE
                    name = VALUES(name),
                    address = VALUES(address),
                    position_lat = VALUES(position_lat),
                    position_lng = VALUES(position_lng),
                    banking = VALUES(banking),
                    bonus = VALUES(bonus)
            """), {
                "number": vals[0],
                "name": vals[1],
                "address": vals[2],
                "lat": vals[3],
                "lng": vals[4],
                "banking": vals[5],
                "bonus": vals[6],
            })

        conn.commit()


def main():
    try:
        r = requests.get(
            dbinfo.STATIONS_URI,
            params={
                "apiKey": dbinfo.JCKEY,
                "contract": dbinfo.NAME,
            },
            timeout=30,
        )
        r.raise_for_status()

        stations_to_db(r.text, engine)

    except Exception:
        print(traceback.format_exc())


main()