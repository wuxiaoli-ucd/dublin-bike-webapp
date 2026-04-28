import os
from dotenv import load_dotenv

load_dotenv()

# API key (secret) from env, non-secret constants can stay hardcoded
JCKEY = os.getenv("JCKEY", "")
NAME = "dublin"
STATIONS_URI = "https://api.jcdecaux.com/vls/v1/stations"
