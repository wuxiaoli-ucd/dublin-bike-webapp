import os

class Config:
    ROUTES_API_KEY = os.getenv("ROUTES_API_KEY")
    MAPS_JS_API_KEY = os.getenv("MAPS_JS_API_KEY")

    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")