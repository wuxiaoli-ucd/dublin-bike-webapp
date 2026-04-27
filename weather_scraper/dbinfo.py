import os
from dotenv import load_dotenv
load_dotenv()

# key in env file
OWKEY = os.getenv("OWKEY", "REPLACE")

# coords in Dublin used in weather requests
LAT = 53.3484
LON = -6.2539

OPENWEATHER_URL = "https://api.openweathermap.org/data/3.0/onecall"

# MySQL (EC2 local MySQL)
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "REPLACE_ME")
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_DB = os.getenv("MYSQL_DB", "local_database_openweather")

