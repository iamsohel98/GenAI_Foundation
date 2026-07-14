"""
test_app.py
-----------
Step 7 of the MLOps lifecycle: Unit Testing.

Covers:
    1. Health endpoint       (GET /health)
    2. Prediction logic       (form POST /predict, JSON POST /api/predict,
                                validate_and_parse_input, predict_rent)
    3. Data validation functions (src/data_validation.py)

Run with:
    pytest -v
    pytest --cov=src --cov=app tests/        (with pytest-cov installed)
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "src"))

from app import app as flask_app  # noqa: E402
from app import validate_and_parse_input, InputValidationError, predict_rent  # noqa: E402
from data_validation import (  # noqa: E402
    check_missing_columns,
    check_null_values,
    check_duplicates,
    clean_dataset,
    EXPECTED_COLUMNS,
)


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------
@pytest.fixture
def client():
    flask_app.config.update(TESTING=True)
    with flask_app.test_client() as c:
        yield c


@pytest.fixture
def valid_payload():
    return {
        "location": "Bandra",
        "bhk": "2",
        "area_sqft": "750",
        "bathrooms": "2",
        "furnishing": "Semi-Furnished",
        "parking": "1",
    }


@pytest.fixture
def sample_dirty_df():
    """A small dataframe with a null, a duplicate, and all expected columns."""
    df = pd.DataFrame([
        {"location": "Andheri", "bhk": 2, "area_sqft": 700, "bathrooms": 2,
         "furnishing": "Unfurnished", "parking": 1, "rent": 30000},
        {"location": "Andheri", "bhk": 2, "area_sqft": 700, "bathrooms": 2,
         "furnishing": "Unfurnished", "parking": 1, "rent": 30000},  # duplicate
        {"location": "Powai", "bhk": 3, "area_sqft": 900, "bathrooms": None,
         "furnishing": "Semi-Furnished", "parking": 0, "rent": 45000},  # null
    ])
    return df


# ----------------------------------------------------------------------
# 1. Health endpoint tests
# ----------------------------------------------------------------------
class TestHealthEndpoint:
    def test_health_returns_200_when_model_loaded(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_response_has_expected_keys(self, client):
        response = client.get("/health")
        data = response.get_json()
        assert "status" in data
        assert "model_loaded" in data
        assert data["status"] in ("healthy", "unhealthy")


# ----------------------------------------------------------------------
# 2. Prediction logic tests
# ----------------------------------------------------------------------
class TestPredictionLogic:
    def test_valid_input_parses_correctly(self, valid_payload):
        parsed = validate_and_parse_input(valid_payload)
        assert parsed["location"] == "Bandra"
        assert parsed["bhk"] == 2
        assert parsed["area_sqft"] == 750.0
        assert parsed["parking"] == 1

    def test_invalid_location_raises(self, valid_payload):
        valid_payload["location"] = "NotARealPlace"
        with pytest.raises(InputValidationError):
            validate_and_parse_input(valid_payload)

    def test_invalid_furnishing_raises(self, valid_payload):
        valid_payload["furnishing"] = "Luxury"
        with pytest.raises(InputValidationError):
            validate_and_parse_input(valid_payload)

    def test_non_numeric_bhk_raises(self, valid_payload):
        valid_payload["bhk"] = "two"
        with pytest.raises(InputValidationError):
            validate_and_parse_input(valid_payload)

    def test_out_of_range_area_raises(self, valid_payload):
        valid_payload["area_sqft"] = "50"  # below min of 100
        with pytest.raises(InputValidationError):
            validate_and_parse_input(valid_payload)

    def test_invalid_parking_value_raises(self, valid_payload):
        valid_payload["parking"] = "maybe"
        with pytest.raises(InputValidationError):
            validate_and_parse_input(valid_payload)

    def test_predict_rent_returns_positive_float(self, valid_payload):
        parsed = validate_and_parse_input(valid_payload)
        prediction = predict_rent(parsed)
        assert isinstance(prediction, float)
        assert prediction > 0

    def test_predict_endpoint_form_success(self, client, valid_payload):
        response = client.post("/predict", data=valid_payload)
        assert response.status_code == 200
        assert b"Predicted Monthly Rent" in response.data

    def test_predict_endpoint_form_invalid_input(self, client):
        response = client.post("/predict", data={"location": "Nowhere"})
        assert response.status_code == 400

    def test_api_predict_success(self, client, valid_payload):
        response = client.post("/api/predict", json=valid_payload)
        data = response.get_json()
        assert response.status_code == 200
        assert data["status"] == "success"
        assert data["predicted_rent"] > 0

    def test_api_predict_invalid_input_returns_400(self, client):
        response = client.post("/api/predict", json={"location": "Nowhere"})
        data = response.get_json()
        assert response.status_code == 400
        assert data["status"] == "error"


# ----------------------------------------------------------------------
# 3. Data validation function tests
# ----------------------------------------------------------------------
class TestDataValidation:
    def test_check_missing_columns_detects_missing(self):
        df = pd.DataFrame({"location": ["Andheri"], "bhk": [2]})
        missing = check_missing_columns(df)
        assert "rent" in missing
        assert "area_sqft" in missing

    def test_check_missing_columns_returns_empty_when_complete(self):
        df = pd.DataFrame({col: [] for col in EXPECTED_COLUMNS})
        missing = check_missing_columns(df)
        assert missing == []

    def test_check_null_values_detects_nulls(self, sample_dirty_df):
        nulls = check_null_values(sample_dirty_df)
        assert "bathrooms" in nulls
        assert nulls["bathrooms"] == 1

    def test_check_duplicates_detects_duplicate_rows(self, sample_dirty_df):
        duplicate_count = check_duplicates(sample_dirty_df)
        assert duplicate_count == 1

    def test_clean_dataset_removes_nulls_and_duplicates(self, sample_dirty_df):
        cleaned = clean_dataset(sample_dirty_df)
        assert cleaned.isnull().sum().sum() == 0
        assert cleaned.duplicated().sum() == 0
        assert len(cleaned) == 1  # only 1 fully-valid, unique row remains

    def test_clean_dataset_filters_invalid_ranges(self):
        df = pd.DataFrame([
            {"location": "Andheri", "bhk": 2, "area_sqft": -10, "bathrooms": 2,
             "furnishing": "Unfurnished", "parking": 1, "rent": 30000},  # invalid area
            {"location": "Andheri", "bhk": 2, "area_sqft": 700, "bathrooms": 2,
             "furnishing": "Unfurnished", "parking": 1, "rent": 30000},  # valid
        ])
        cleaned = clean_dataset(df)
        assert len(cleaned) == 1
        assert cleaned.iloc[0]["area_sqft"] == 700
