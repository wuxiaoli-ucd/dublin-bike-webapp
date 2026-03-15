from flask import render_template, Blueprint

pages_historical_bp = Blueprint("pages_historical", __name__)

@pages_historical_bp.route("/historical-test")
def historical_test():
    return render_template("historical_availability.html")