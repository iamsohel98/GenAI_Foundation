"""
app.py
------
Step 6 of the MLOps lifecycle: Flask Web Application.

Exposes:
    GET  /            -> HTML form to enter house details
    POST /predict      -> Form submission -> renders prediction result
    GET  /health        -> Health check API (used by Docker/Jenkins/K8s probes)
    POST /api/predict   -> JSON API for programmatic predictions

The app loads the model that was produced by src/train.py
(models/model_latest.joblib). It does NOT retrain on startup -- training
is a separate, explicit MLOps pipeline step (see src/train.py), which
keeps the web app fast to start and decoupled from the training process.
"""

import logging
import os
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, render_template, request

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent
MODEL_PATH = Path(os.getenv("MODEL_PATH", ROOT_DIR / "models" / "model_latest.joblib"))

LOCATIONS = [
    "Andheri", "Bandra", "Powai", "Dadar", "Thane",
    "Malad", "Borivali", "Chembur", "Goregaon", "Kandivali",
]
FURNISHING_TYPES = ["Unfurnished", "Semi-Furnished", "Fully-Furnished"]

app = Flask(__name__)

# ----------------------------------------------------------------------
# Model loading
# ----------------------------------------------------------------------
_model = None
_model_load_error = None


def get_model():
    """
    Lazily loads (and caches) the trained pipeline from disk.
    Using a function (instead of loading at import time) lets the health
    endpoint start responding even if the model file is briefly
    unavailable, and lets tests monkeypatch this easily.
    """
    global _model, _model_load_error
    if _model is None and _model_load_error is None:
        try:
            _model = joblib.load(MODEL_PATH)
            logger.info("Model loaded from %s", MODEL_PATH)
        except Exception as e:  # noqa: BLE001 - we want to capture and surface any load error
            _model_load_error = str(e)
            logger.error("Failed to load model: %s", e)
    return _model


# ----------------------------------------------------------------------
# Input validation
# ----------------------------------------------------------------------
class InputValidationError(Exception):
    """Raised when user-submitted form/JSON data fails validation."""


def validate_and_parse_input(form_data: dict) -> dict:
    """
    Validates raw input (from an HTML form or JSON body) and coerces it
    into the correct types. Raises InputValidationError with a
    user-friendly message on any problem.
    """
    errors = []

    location = form_data.get("location", "")
    if location not in LOCATIONS:
        errors.append(f"Invalid location. Must be one of: {', '.join(LOCATIONS)}")

    furnishing = form_data.get("furnishing", "")
    if furnishing not in FURNISHING_TYPES:
        errors.append(f"Invalid furnishing type. Must be one of: {', '.join(FURNISHING_TYPES)}")

    def _to_number(key, cast, min_value, max_value, label):
        raw_value = form_data.get(key, None)
        try:
            value = cast(raw_value)
        except (TypeError, ValueError):
            errors.append(f"{label} must be a valid number.")
            return None
        if value < min_value or value > max_value:
            errors.append(f"{label} must be between {min_value} and {max_value}.")
            return None
        return value

    bhk = _to_number("bhk", int, 1, 10, "BHK")
    area_sqft = _to_number("area_sqft", float, 100, 20000, "Area (sqft)")
    bathrooms = _to_number("bathrooms", int, 1, 10, "Bathrooms")
    parking_raw = form_data.get("parking", "0")
    try:
        parking = int(parking_raw)
        if parking not in (0, 1):
            raise ValueError
    except (TypeError, ValueError):
        errors.append("Parking must be 0 (No) or 1 (Yes).")
        parking = None

    if errors:
        raise InputValidationError(" | ".join(errors))

    return {
        "location": location,
        "bhk": bhk,
        "area_sqft": area_sqft,
        "bathrooms": bathrooms,
        "furnishing": furnishing,
        "parking": parking,
    }


def predict_rent(payload: dict) -> float:
    """
    Runs the model on a single validated payload dict and returns
    the predicted monthly rent (rounded to nearest integer rupee).
    """
    model = get_model()
    if model is None:
        raise RuntimeError(f"Model is not available: {_model_load_error}")

    input_df = pd.DataFrame([{
        "location": payload["location"],
        "bhk": payload["bhk"],
        "area_sqft": payload["area_sqft"],
        "bathrooms": payload["bathrooms"],
        "furnishing": payload["furnishing"],
        "parking": payload["parking"],
    }])
    prediction = model.predict(input_df)[0]
    return round(float(prediction), 2)


# ----------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    """Renders the home rent prediction form."""
    return render_template(
        "index.html",
        locations=LOCATIONS,
        furnishing_types=FURNISHING_TYPES,
        prediction=None,
        error=None,
        form_values={},
    )


@app.route("/predict", methods=["POST"])
def predict():
    """Handles form submission, runs prediction, and re-renders the page with results."""
    form_values = request.form.to_dict()
    try:
        payload = validate_and_parse_input(form_values)
        prediction = predict_rent(payload)
        return render_template(
            "index.html",
            locations=LOCATIONS,
            furnishing_types=FURNISHING_TYPES,
            prediction=prediction,
            error=None,
            form_values=form_values,
        )
    except InputValidationError as e:
        return render_template(
            "index.html",
            locations=LOCATIONS,
            furnishing_types=FURNISHING_TYPES,
            prediction=None,
            error=str(e),
            form_values=form_values,
        ), 400
    except Exception as e:  # noqa: BLE001 - surfaced to the user as a friendly error
        logger.exception("Prediction failed")
        return render_template(
            "index.html",
            locations=LOCATIONS,
            furnishing_types=FURNISHING_TYPES,
            prediction=None,
            error=f"Something went wrong while predicting rent: {e}",
            form_values=form_values,
        ), 500


@app.route("/api/predict", methods=["POST"])
def api_predict():
    """JSON API endpoint for programmatic / automated predictions."""
    try:
        data = request.get_json(force=True, silent=True) or {}
        payload = validate_and_parse_input(data)
        prediction = predict_rent(payload)
        return jsonify({"status": "success", "predicted_rent": prediction}), 200
    except InputValidationError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:  # noqa: BLE001
        logger.exception("API prediction failed")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """
    Health Check API.
    Returns 200 with model status if the app + model are healthy,
    503 if the model failed to load (used by Docker HEALTHCHECK / Jenkins / k8s).
    """
    model = get_model()
    model_ok = model is not None
    payload = {
        "status": "healthy" if model_ok else "unhealthy",
        "model_loaded": model_ok,
        "model_path": str(MODEL_PATH),
    }
    return jsonify(payload), (200 if model_ok else 503)


if __name__ == "__main__":
    # debug=False for production-style runs; overridden by FLASK_DEBUG env var if needed.
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=debug_mode)
