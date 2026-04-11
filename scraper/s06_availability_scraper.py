import requests
import traceback
from datetime import datetime, UTC
import json
from sqlalchemy import text
import scraper.dbinfo as dbinfo
from app.services.db import engine

def availability_to_db(raw_text, in_engine):
    stations = json.loads(raw_text)

    scraped_at = datetime.now(UTC).replace(tzinfo=None)

    with in_engine.begin() as conn:
        for station in stations:

            timestamps_ms = station.get("last_update")
            if timestamps_ms is None:
                continue
            last_update_dt = datetime.fromtimestamp(timestamps_ms / 1000, UTC).replace(tzinfo=None)

            # let us load only the parts that we have included in our db:
            # number INTEGER NOT NULL,
            # last_update DATETIME NOT NULL,
            # bike_stands INTEGER,
            # available_bike_stands INTEGER,
            # available_bikes INTEGER,
            # status VARCHAR(128),
            # PRIMARY KEY(number, last_update)

            vals = (
                int(station.get("number")),
                last_update_dt,
                int(station.get("bike_stands")),
                int(station.get("available_bike_stands")),
                int(station.get("available_bikes",0)),
                station.get("status"),
            )

            conn.execute(
                text("""
                    INSERT INTO availability
                    (number, last_update, bike_stands, available_bike_stands, available_bikes, status, scraped_at)
                    VALUES
                    (:number, :last_update, :bike_stands, :available_bike_stands, :available_bikes, :status, :scraped_at)
                    ON DUPLICATE KEY UPDATE
                        bike_stands = VALUES(bike_stands),
                        available_bike_stands = VALUES(available_bike_stands),
                        available_bikes = VALUES(available_bikes),
                        status = VALUES(status),
                        scraped_at = VALUES(scraped_at)
                """),
                {
                    "number": vals[0],
                    "last_update": vals[1],
                    "bike_stands": vals[2],
                    "available_bike_stands": vals[3],
                    "available_bikes": vals[4],
                    "status": vals[5],
                    "scraped_at": scraped_at,
                }
            )



def main():
    try:
        r = requests.get(
            dbinfo.STATIONS_URI,
            params={"apiKey": dbinfo.JCKEY, "contract": dbinfo.NAME},
            timeout=30
        )
        r.raise_for_status()
        availability_to_db(r.text, engine)
    except Exception:
        print(traceback.format_exc())


if __name__ == "__main__":
    main()