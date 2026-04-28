from pathlib import Path
from datetime import datetime, timedelta
import joblib
import pandas as pd

from app.services.stations_repo import fetch_stations_with_latest_availability
from app.services.weather_service import get_prediction_weather

# get project root (avoids issues with relative paths depending on how the app is started e.g., python app/run.py instead of running inside app directory)
BASE_DIR = Path(__file__).resolve().parents[2] 
MODELS_DIR = BASE_DIR / "models"

MODEL_PATH = MODELS_DIR / "bike_model.joblib"
FEATURES_PATH = MODELS_DIR / "model_features.joblib"

# load model at import time once so predictions don't reload files per request
model = joblib.load(MODEL_PATH)
model_features = joblib.load(FEATURES_PATH)


def get_weather_for_datetime(target_dt: datetime) -> dict:
    """
    Returns weather features for the requested prediction time.

    The weather service decides whether to use current, hourly, or daily
    forecast data depending on the target datetime.
    """
    return get_prediction_weather(target_dt)


def get_station_metadata(station_id: int) -> dict:
    """
    Finds station metadata needed by the prediction model.

    The model uses station-specific features such as:
    - station ID
    - capacity
    - latitude/longitude

    Latest availability is fetched through the stations repository because
    it already returns stations in the shape used across the application
    """

    stations = fetch_stations_with_latest_availability()

    for station in stations:
        if int(station["number"]) == int(station_id):
            return {
                "station_id": int(station["number"]),
                "capacity": int(station["bike_stands"]),
                "lat": float(station["position"]["lat"]),
                "lon": float(station["position"]["lng"]),
            }

    raise ValueError(f"Station {station_id} not found")


def build_prediction_input(station_id: int, depart_at: datetime) -> pd.DataFrame:
    """
    Takes station metadata and weather for target time
    Returns a dataframe of model features
    """
    
    station = get_station_metadata(station_id)
    weather = get_weather_for_datetime(depart_at)

    row = {
        "station_id": station["station_id"],
        "capacity": station["capacity"],
        "day": depart_at.day,
        "hour": depart_at.hour,
        "day_of_week": depart_at.weekday(),
        "lat": station["lat"],
        "lon": station["lon"],
        "avg_air_temperature": weather["avg_air_temperature"],
        "avg_relative_humidity": weather["avg_relative_humidity"],
    }

    df = pd.DataFrame([row])
    df = df[model_features]
    return df


def predict_availability(station_id: int, depart_at: datetime) -> dict:
    """
    Predicts available bikes and docks for a station at a future datetime.

    Validation is performed before prediction so the model is only used
    for supported future dates.
    """
    
    validate_prediction_datetime(depart_at) # can only be three days from current date
    
    input_df = build_prediction_input(station_id, depart_at)
    prediction = model.predict(input_df)[0] # predict based on model 

    # so the api never returns negative availability
    predicted_bikes = max(0, round(float(prediction[0])))
    predicted_docks = max(0, round(float(prediction[1])))

    return {
        "station_id": int(station_id),
        "datetime": depart_at.isoformat(),
        "predicted_bikes": predicted_bikes,
        "predicted_docks": predicted_docks,
    }


def predict_from_strings(station_id: int, date_str: str, time_str: str) -> dict:
    """
    Parses frontend date/time strings and returns a single prediction.

    The frontend sends date and time separately, so they are combined here
    before being converted into a datetime object.
    """
    
    dt_formats = [
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
    ]

    depart_at = None

    for dt_format in dt_formats:
        try:
            depart_at = datetime.strptime(f"{date_str} {time_str}", dt_format)
            break
        except ValueError:
            continue

    if depart_at is None:
        raise ValueError("Invalid date/time format. Expected YYYY-MM-DD and HH:MM or HH:MM:SS")

    return predict_availability(int(station_id), depart_at)



MAX_PREDICTION_DAYS = 3

def validate_prediction_datetime(depart_at: datetime) -> None:
    """
    Ensures prediction requests are within the supported time window.

    Prediction time must be in the future
    Prediction date must be no more than MAX_PREDICTION_DAYS ahead

    The limit is date-based rather than exact-hour-based, which keeps the
    behaviour easier to understand for users selecting dates in the UI.
    """
    
    now = datetime.now()

    if depart_at < now:
        raise ValueError("Prediction datetime must be in the future")

    max_date = (now + timedelta(days=MAX_PREDICTION_DAYS)).date()

    if depart_at.date() > max_date:
        raise ValueError(f"Predictions are only available up to {MAX_PREDICTION_DAYS} days ahead")
    


def predict_hourly_series(station_id: int, hours: int = 8) -> list[dict]:
    """
    Generates hourly predictions for the frontend prediction chart.

    Used by the chart's "Hours" mode. Each bucket represents one future
    hourly interval from the current time.
    """
    now = datetime.now()
    series = []

    for i in range(1, hours + 1):
        target_dt = now + timedelta(hours=i)
        prediction = predict_availability(station_id, target_dt)

        series.append({
            "bucket": target_dt.isoformat(), # time interval
            "predicted_bikes": prediction["predicted_bikes"],
            "predicted_docks": prediction["predicted_docks"],
        })

    return {
        "station_id": int(station_id),
        "mode": "hours",
        "series": series,
    }


def predict_daily_series(station_id: int, days: int = 3) -> dict:
    """
    Generates daily predictions for the frontend prediction chart.

    Used by the chart's "Days" mode. Each day is sampled at midday to give
    a consistent representative prediction point.
    """
    now = datetime.now()
    series = []

    for i in range(1, days + 1):
        target_dt = (now + timedelta(days=i)).replace(
            hour=12, minute=0, second=0, microsecond=0
        )

        prediction = predict_availability(station_id, target_dt)

        series.append({
            "bucket": target_dt.isoformat(),
            "predicted_bikes": prediction["predicted_bikes"],
            "predicted_docks": prediction["predicted_docks"],
        })

    return {
        "station_id": int(station_id),
        "mode": "days",
        "series": series,
    }
      