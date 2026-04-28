from sqlalchemy import text
from app.services.db import engine

with engine.connect() as conn:
    result = conn.execute(text("SHOW VARIABLES;"))
    for res in result:
        print(res)

sql = '''
CREATE TABLE IF NOT EXISTS station (
number INTEGER NOT NULL,
name VARCHAR(256),
address VARCHAR(256), 
position_lat FLOAT,
position_lng FLOAT,
banking BOOLEAN,
bonus BOOLEAN,
PRIMARY KEY(number)
);
'''

with engine.connect() as conn:
    conn.execute(text(sql))
    conn.commit()

    tab_structure = conn.execute(text("SHOW COLUMNS FROM station;"))
    columns = tab_structure.fetchall()
    print(columns)

sql = """
CREATE TABLE IF NOT EXISTS availability (
number INTEGER NOT NULL,
last_update DATETIME NOT NULL,
bike_stands INTEGER,
available_bike_stands INTEGER,
available_bikes INTEGER,
status VARCHAR(128),
PRIMARY KEY(number, last_update)
);
"""

with engine.connect() as conn:
    conn.execute(text(sql))
    conn.commit()