import time
from datetime import datetime
from scraper.s06_availability_scraper import main

while True:
    try:
        print(f"Running scraper at {datetime.now()}...")
        main()
        print("Done. Sleeping for 5 minutes...\n")
    except Exception as e:
        print("Error:", e)

    time.sleep(300)  # 5 minutes