from flask import Flask
from dotenv import load_dotenv
load_dotenv()
# from .config import Config
from .routes.routing import routing_bp
from .routes.pages import pages_bp
from .routes.stations_api import stations_bp
from .routes.stations_history_api import stations_history_bp

# from .routes.weather import weather_bp


def create_app():
    app = Flask(__name__)
    # app.config.from_object(Config)

    # existing blueprints
    app.register_blueprint(routing_bp, url_prefix="/api")
    app.register_blueprint(pages_bp)
    app.register_blueprint(stations_bp, url_prefix="/api")

    # lily's historical chart related blueprints
    app.register_blueprint(stations_history_bp, url_prefix="/api")

    # app.register_blueprint(weather_bp) --Andrew


    return app
