from flask import Flask
from dotenv import load_dotenv

from .config import Config
from .routes.routing import routing_bp
from .routes.pages import pages_bp
from .routes.stations_api import stations_bp
from .routes.stations_historical_data import historical_data_bp
from .routes.pages_historical_chart import pages_historical_bp

# from .routes.weather import weather_bp


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(Config)

    # existing blueprints
    app.register_blueprint(routing_bp, url_prefix="/api")
    app.register_blueprint(pages_bp)
    app.register_blueprint(stations_bp, url_prefix="/api")

    # lily's historical chart related blueprints
    app.register_blueprint(historical_data_bp)
    app.register_blueprint(pages_historical_bp)

    # app.register_blueprint(weather_bp) --Andrew

    @app.route('/')
    def root():
        return """
            <h2>Available Endpoints</h2>
            <ul>
                <li><a href="/stations">All Stations</a></li>
                <li>Single Station Example:
                    <a href="/availability/1">/availability/1</a>
                </li>
                <li>
                    Hourly (8h) Test Mode:
                    <a href="/availability/1/hourly">/availability/1/hourly</a>
                </li>
                <li>
                    Daily (7d) Test Mode:
                    <a href="/availability/1/daily">/availability/1/daily</a>
                </li>
            </ul>
        """

    return app