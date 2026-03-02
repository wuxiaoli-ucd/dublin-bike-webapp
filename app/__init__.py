from flask import Flask
from dotenv import load_dotenv
from .config import Config
from .routes.routing import routing_bp
from .routes.pages import pages_bp
from .routes.stations_api import stations_bp

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(routing_bp, url_prefix="/api")
    app.register_blueprint(pages_bp)

    app.register_blueprint(stations_bp, url_prefix="/api") # frontend markers can show bikes/stands/status

    return app