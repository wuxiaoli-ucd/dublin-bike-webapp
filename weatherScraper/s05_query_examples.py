from sqlalchemy import create_engine, text
import dbinfo

engine = create_engine(
    f"mysql+pymysql://{dbinfo.MYSQL_USER}:{dbinfo.MYSQL_PASSWORD}"
    f"@{dbinfo.MYSQL_HOST}:{dbinfo.MYSQL_PORT}/{dbinfo.MYSQL_DB}",
    echo=True,
    future=True
)

print(engine.execute(text("SELECT COUNT(*) FROM weather_hourly;")).fetchall())
print(engine.execute(text("SELECT * FROM weather_hourly ORDER BY dt DESC LIMIT 5;")).fetchall())

