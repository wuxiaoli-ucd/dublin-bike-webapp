from sqlalchemy import create_engine, text
from app.services.db import get_db_settings

s = get_db_settings()

connection_string = f'mysql+pymysql://{s["user"]}:{s["password"]}@{s["host"]}:{s["port"]}/'

engine = create_engine(connection_string, echo=True)

sql = f"""
CREATE DATABASE IF NOT EXISTS {s["db"]};
"""

with engine.connect() as conn:
    conn.execute(text(sql))
    conn.commit()