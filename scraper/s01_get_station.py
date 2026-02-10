import time
import traceback
import dbinfo
import requests
import json


r = requests.get(dbinfo.STATIONS_URI,params={"apiKey": dbinfo.JCKEY,"contract": dbinfo.NAME}, timeout=30)
r.raise_for_status()
data = r.json()
print(json.dumps(data, indent=4))

# save the file to json
with open("stations_snapshot.json","w") as f:
    json.dump(data, f, indent=4)
print("Saved successfully")
import os
print("Saved to:", os.path.abspath("stations_snapshot.json"))