import dbinfo
import requests
import json
import sqlalchemy as sqla
from sqlalchemy import create_engine, text
import traceback
import glob
import os
from pprint import pprint
import simplejson as json
import time
from IPython.display import display


USER = "admin"
PASSWORD = "wuxiaoliireland"
PORT = "3306"
DB = "bikedb"
URI = "bikedb.cfcky6a8ux7c.eu-west-1.rds.amazonaws.com"

connection_string = "mysql+pymysql://{}:{}@{}:{}?charset=utf8mb4".format(USER, PASSWORD, URI, PORT)

engine = create_engine(connection_string, echo = True)

sql = """
CREATE DATABASE IF NOT EXISTS {};
""".format(DB)

with engine.connect() as conn:
    conn.execute(text(sql))
    conn.commit()

    conn.execute(text("SELECT 1"))
    print("Connected successfully")
