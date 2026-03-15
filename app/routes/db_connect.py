import os
from sqlalchemy import create_engine
from dotenv import load_dotenv


load_dotenv()

def get_db_url():
    app_env = os.getenv("APP_ENV", "local").lower()
    prefix = "RDS" if app_env == "rds" else "LOCAL"

    user = os.getenv(f"{prefix}_USER")
    pwd  = os.getenv(f"{prefix}_PASSWORD")
    host = os.getenv(f"{prefix}_HOST")
    port = os.getenv(f"{prefix}_PORT", "3306")
    db   = os.getenv(f"{prefix}_DB", "bikedb")

    return f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}"

engine = create_engine(
    get_db_url(),
    pool_pre_ping=True,
    echo=True
)