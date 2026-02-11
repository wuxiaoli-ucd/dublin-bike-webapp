import requests
import traceback
import datetime
import time
import os
import dbinfo
import json
from sqlalchemy import create_engine,text



def stations_to_db(raw_text, in_engine):
    # let us load the stations from the text received from jcdecaux
    stations = json.loads(raw_text)

    # print type of the stations object, and number of stations
    print(type(stations), len(stations))

    with in_engine.connect() as conn:
        # let us print the type of the object stations (a dictionary) and load the content
        for station in stations:
            print(type(station))

            # let us load only the parts that we have included in our db:
            # number INTEGER NOT NULL,
            # name VARCHAR(256),
            # address VARCHAR(256),
            # position_lat FLOAT,
            # position_lng FLOAT,
            # banking BOOLEAN,
            # bonus BOOLEAN,


            # let us extract the relevant info from the dictionary
            vals = (int(station.get('number')),station.get('name'), station.get('address'), float(station.get('position').get('lat')), float(station.get('position').get('lng')), bool(station.get('banking')),bool(station.get('bonus')))
            print(vals)

            # now let us use the engine to insert into the stations

            conn.execute(text("""
                INSERT INTO station
                (number, name, address,position_lat,position_lng,banking,bonus)
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
                "bonus": vals[6]
            })
        conn.commit()



def main():
    USER = "admin"
    PASSWORD = "wuxiaoliireland"
    PORT = "3306"
    DB = "bikedb"
    URI = "bikedb.cfcky6a8ux7c.eu-west-1.rds.amazonaws.com"

    connection_string = "mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4".format(USER, PASSWORD, URI, PORT, DB)

    engine = create_engine(connection_string)

    try:
        r = requests.get(dbinfo.STATIONS_URI, params={"apiKey": dbinfo.JCKEY, "contract": dbinfo.NAME},timeout=30)
        r.raise_for_status()
        stations_to_db(r.text,engine)
        # time.sleep(5 * 60)  # NOTE: if you are downloading static station data only, you need to do this just once!
    except Exception:
        print(traceback.format_exc())


# CTRL + Z or CTRL + C to stop it
main()