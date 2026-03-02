from flask import Blueprint, render_template, current_app

pages_bp = Blueprint("pages", __name__)

@pages_bp.route("/")
def index():
    """Executes when a HTTP GET request hits route (/)"""
    # Frontend key separate from backend Routes key
    return render_template("index.html", apikey=current_app.config["MAPS_JS_API_KEY"])