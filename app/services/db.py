import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()


def get_db_settings() -> dict:
    """
    Reads database connection settings from environment variables.

    Uses APP_ENV to determine which configuration to load:
        - "local" (default): uses LOCAL_* variables
        - "rds": uses RDS_* variables
    - Ensures all required fields are present before returning.

    Returns:
        dict containing:
        {
            "user": ...,
            "password": ...,
            "host": ...,
            "port": ...,
            "db": ...
        }
    
    Raises:
        ValueError if any required environment variable is missing.
    """
    
    # default to local if APP_ENV is not set
    app_env = os.getenv("APP_ENV", "local").lower()

    # select configuration based on environment
    if app_env == "rds":
        # remote db - AWS RDS
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
    # validate that all required values are present
    missing = [k for k, v in settings.items() if v in (None, "")]
    if missing:
        raise ValueError(
            f"Missing database environment variables for APP_ENV={app_env}: {', '.join(missing)}"
        )

    return settings


def get_db_url() -> str:
    """
    Constructs an SQLAlchemy-compatible database URL.

    Format:
    mysql+pymysql://user:password@host:port/db
    """
    s = get_db_settings()
    return f'mysql+pymysql://{s["user"]}:{s["password"]}@{s["host"]}:{s["port"]}/{s["db"]}'

# Create global SQLAlchemy engine instance which is reused for executing queries
engine = create_engine(
    get_db_url(),
    pool_pre_ping=True, # ensures connections validated before use
    pool_recycle=3600, # recycles connections
    echo=os.getenv("SQL_ECHO", "false").lower() in ("true", "1", "yes"), # for debugging
)
