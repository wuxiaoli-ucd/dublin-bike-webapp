import pymysql

def get_conn(cfg):
    """Helper for connecting to MySQL"""
    return pymysql.connect(
        host=cfg["DB_HOST"],
        port=cfg["DB_PORT"],
        user=cfg["DB_USER"],
        password=cfg["DB_PASSWORD"],
        database=cfg["DB_NAME"],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )