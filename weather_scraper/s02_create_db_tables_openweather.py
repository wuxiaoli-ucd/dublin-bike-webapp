from sqlalchemy import create_engine, text
import dbinfo

# Required because the database may not exist yet
connection_string = (
    f"mysql+pymysql://{dbinfo.MYSQL_USER}:{dbinfo.MYSQL_PASSWORD}"
    f"@{dbinfo.MYSQL_HOST}:{dbinfo.MYSQL_PORT}/"
)

engine = create_engine(connection_string, echo = False, future=True)

# create db if doesn't exist
with engine.begin() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {dbinfo.MYSQL_DB};"))

engine = create_engine(
    f"{connection_string}{dbinfo.MYSQL_DB}",
    echo=True,
    future=True
)

# create hourly weather table
create_sql = """
CREATE TABLE IF NOT EXISTS weather_hourly (
  dt DATETIME NOT NULL,
  temp FLOAT,
  feels_like FLOAT,
  pressure INT,
  humidity INT,
  wind_speed FLOAT,
  wind_gust FLOAT,
  weather_id INT,
  rain_1h FLOAT,
  snow_1h FLOAT,
  PRIMARY KEY (dt)
);
"""
with engine.begin() as conn:
    conn.execute(text(create_sql))

print("Created weather_hourly table.")

with engine.connect() as conn:
    for res in conn.execute(text("SHOW VARIABLES;")):
        print(res)