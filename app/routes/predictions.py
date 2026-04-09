from flask import Blueprint, request, jsonify
from app.services.prediction_service import predict_from_strings, predict_hourly_series, predict_daily_series

predictions_bp = Blueprint("predictions", __name__)


@predictions_bp.route("/predict", methods=["GET"])
def predict():
    try:
        date = request.args.get("date") # request object from Flask
        time = request.args.get("time")
        station_id = request.args.get("station_id")

        if not date or not time or not station_id:
            return jsonify({
                "error": "Missing date, time, or station_id parameter"
            }), 400

        result = predict_from_strings(
            station_id=int(station_id),
            date_str=date,
            time_str=time,
        )

        return jsonify(result)

    except ValueError as e:
        return jsonify({"error": "Predictions are only available up to 3 days from now"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# for predicted availability chart
@predictions_bp.route("/predictions/<int:station_id>/hourly", methods=["GET"])
def predicted_hourly(station_id):
    try:
        data = predict_hourly_series(station_id, hours=8)
        return jsonify(data)

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@predictions_bp.route("/predictions/<int:station_id>/daily", methods=["GET"])
def predicted_daily(station_id):
    try:
        data = predict_daily_series(station_id, days=3)
        return jsonify(data)

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500