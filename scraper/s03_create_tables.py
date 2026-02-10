import dbinfo
import requests
import json
import sqlalchemy as sqla
from sqlalchemy import create_engine,text
import traceback
import glob
import os
from pprint import pprint
import simplejson as json
import time
from IPython.display import display


USER = "root"
PASSWORD = "NewPassword123!"
PORT = "3306"
DB = "local_databasejcdecaux"
URI = "127.0.0.1"

connection_string = "mysql+pymysql://{}:{}@{}:{}/{}".format(USER, PASSWORD, URI, PORT, DB)

engine = create_engine(connection_string, echo = True)

with engine.connect() as conn:
    result = conn.execute(text("SHOW VARIABLES;"))
    for res in result:
        print(res)

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
PRIMARY KEY(number, last_update)
);
"""

with engine.connect() as conn:
    res = conn.execute(text(sql))
    conn.commit()