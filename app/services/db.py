import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()


def get_db_settings() -> dict:
    app_env = os.getenv("APP_ENV", "local").lower()

    # Prefer explicit LOCAL_/RDS_ vars if present, otherwise fall back to DB_* vars
    if app_env == "rds":
        settings = {
            "user": os.getenv("RDS_USER"),
            "password": os.getenv("RDS_PASSWORD"),
            "host": os.getenv("RDS_HOST"),
            "port": int(os.getenv("RDS_PORT", "3306")),
            "db": os.getenv("RDS_DB"),
        }
    else:
        settings = {
            "user": os.getenv("LOCAL_USER"),
            "password": os.getenv("LOCAL_PASSWORD"),
            "host": os.getenv("LOCAL_HOST"),
            "port": int(os.getenv("LOCAL_PORT", "3306")),
            "db": os.getenv("LOCAL_DB"),
        }

    missing = [k for k, v in settings.items() if v in (None, "")]
    if missing:
        raise ValueError(
            f"Missing database environment variables for APP_ENV={app_env}: {', '.join(missing)}"
        )

    return settings


def get_db_url() -> str:
    s = get_db_settings()
    return f'mysql+pymysql://{s["user"]}:{s["password"]}@{s["host"]}:{s["port"]}/{s["db"]}'


engine = create_engine(
    get_db_url(),
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=os.getenv("SQL_ECHO", "false").lower() in ("true", "1", "yes"),
)
