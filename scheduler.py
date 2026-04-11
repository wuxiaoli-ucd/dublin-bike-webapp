import time
import subprocess
import sys
from datetime import datetime


while True:
    try:
        print(f"Running scraper at {datetime.now()}...")

        subprocess.run(
            [sys.executable, "-m", "scraper.s06_availability_scraper"],
            check=True
        )

        print("Done. Sleeping for 5 minutes...\n")

    except Exception as e:
        print("Error:", e)

    time.sleep(300)  # 5 minutes