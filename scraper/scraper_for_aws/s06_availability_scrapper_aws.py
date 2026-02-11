import requests
import traceback
from datetime import datetime, UTC
import time
import os
import dbinfo
import json
from sqlalchemy import create_engine,text



def availability_to_db(raw_text, in_engine):
    # let us load the stations from the text received from jcdecaux
    stations = json.loads(raw_text)

    scraped_at = datetime.now(UTC)
    with in_engine.connect() as conn:
        # let us print the type of the object stations (a dictionary) and load the content
        for station in stations:


            # let us load only the parts that we have included in our db:
            # number INTEGER NOT NULL,
            # last_update DATETIME NOT NULL,
            # bike_stands INTEGER,
            # available_bike_stands INTEGER,
            # available_bikes INTEGER,
            # status VARCHAR(128),
            # PRIMARY KEY(number, last_update)

            timestamps_ms = station.get('last_update')
            last_update_dt = datetime.fromtimestamp(timestamps_ms/1000, UTC)

            # let us extract the relevant info from the dictionary
            vals = (int(station.get('number')), last_update_dt, int(station.get('bike_stands')), int(station.get('available_bike_stands')), int(station.get('available_bikes')),station.get('status'))


            # now let us use the engine to insert into the stations

            conn.execute(text("""
                INSERT INTO availability
                (number, last_update, bike_stands, available_bike_stands,available_bikes,status,scraped_at)
                VALUES
                (:number, :last_update, :bike_stands, :available_bike_stands, :available_bikes, :status, :scraped_at)
                ON DUPLICATE KEY UPDATE
                    bike_stands = VALUES(bike_stands),
                    available_bike_stands = VALUES(available_bike_stands),
                    available_bikes = VALUES(available_bikes),
                    status = VALUES(status),
                    scraped_at = VALUES(scraped_at)
            """), {
                "number": vals[0],
                "last_update": vals[1],
                "bike_stands": vals[2],
                "available_bike_stands": vals[3],
                "available_bikes": vals[4],
                "status": vals[5],
                "scraped_at":scraped_at,
            })
        conn.commit()

def main():
    USER = "admin"
    PASSWORD = "wuxiaoliireland"
    PORT = "3306"
    DB = "bikedb"
    URI = "bikedb.cfcky6a8ux7c.eu-west-1.rds.amazonaws.com"

    connection_string = "mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4".format(USER, PASSWORD, URI, PORT, DB)

    engine = create_engine(connection_string,pool_pre_ping=True)

    while True:
        try:
            r = requests.get(dbinfo.STATIONS_URI, params={"apiKey": dbinfo.JCKEY, "contract": dbinfo.NAME},timeout=30)
            r.raise_for_status()
            availability_to_db(r.text,engine)
            print("Data inserted")
        except Exception:
            print(traceback.format_exc())
        time.sleep(5 * 60)  # NOTE: if you are downloading static station data only, you need to do this just once!

# CTRL + Z or CTRL + C to stop it
main()