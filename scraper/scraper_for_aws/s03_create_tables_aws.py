import dbinfo
from sqlalchemy import create_engine,text
import os


USER = "admin"
PASSWORD = "wuxiaoliireland"
PORT = "3306"
DB = "bikedb"
URI = "bikedb.cfcky6a8ux7c.eu-west-1.rds.amazonaws.com"

connection_string = "mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4".format(USER, PASSWORD, URI, PORT, DB)

engine = create_engine(connection_string, echo = True)


# Let us create a simplified JCDecaux table: ADD ALL YOUR VARIABLES!
# VARCHAR(256) indicates a string with max 256 chars

sql = '''
CREATE TABLE IF NOT EXISTS station (
number INTEGER NOT NULL,
name VARCHAR(256),
address VARCHAR(256), 
position_lat FLOAT,
position_lng FLOAT,
banking BOOLEAN,
bonus BOOLEAN,
PRIMARY KEY(number)
);
'''

# Execute the query
with engine.connect() as conn:
    res = conn.execute(text(sql))
    conn.commit()
    # Use the engine to execute the DESCRIBE command to inspect the table schema
    tab_structure = conn.execute(text("SHOW COLUMNS FROM station;"))
    # Fetch and print the result to see the columns of the table
    columns = tab_structure.fetchall()
    print(columns)

##################CREATE AVAILABILITY TABLE: DO NOT FORGET ALL VARIABLES############
sql = """
CREATE TABLE IF NOT EXISTS availability (
number INTEGER NOT NULL,
last_update DATETIME NOT NULL,
bike_stands INTEGER,
available_bike_stands INTEGER,
available_bikes INTEGER,
status VARCHAR(128),
scraped_at DATETIME,
PRIMARY KEY(number, last_update)
);
"""

with engine.connect() as conn:
    res = conn.execute(text(sql))
    conn.commit()