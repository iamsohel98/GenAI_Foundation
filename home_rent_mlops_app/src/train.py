"""
train.py
--------
Steps 3, 4 & 5 of the MLOps lifecycle:
    Step 3 - Model Training (Linear Regression vs Random Forest)
    Step 4 - MLflow Experiment Tracking (params, metrics, artifacts)
    Step 5 - Model Registration (best model saved + versioned)

Usage:
    python src/train.py

Environment variables (all optional):
    MLFLOW_TRACKING_URI   Where MLflow should log runs. Defaults to a local
                           './mlruns' directory (file-based store), so the
                           whole pipeline works with ZERO extra setup.
    MODEL_DIR              Where the final registered model is copied to
                            for the Flask app to load. Defaults to './models'.
"""

import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error

from data_validation import validate_dataset, clean_dataset, load_dataset, DEFAULT_DATA_PATH
from preprocessing import (
    build_full_pipeline,
    split_features_target,
    train_test_split_data,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = Path(os.getenv("MODEL_DIR", ROOT_DIR / "models"))
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", f"file://{ROOT_DIR / 'mlruns'}")
EXPERIMENT_NAME = "home_rent_prediction"

# Candidate models + hyperparameters to try.
# Keeping this as a simple dict makes it trivial to extend with more models later.
CANDIDATE_MODELS = {
    "linear_regression": {
        "estimator": LinearRegression(),
        "params": {},  # LinearRegression has no hyperparameters worth tuning here
    },
    "random_forest": {
        "estimator": RandomForestRegressor(
            n_estimators=200,
            max_depth=12,
            random_state=42,
            n_jobs=-1,
        ),
        "params": {"n_estimators": 200, "max_depth": 12, "random_state": 42},
    },
}


def evaluate(y_true, y_pred) -> dict:
    """Computes the standard regression metrics used to compare models."""
    return {
        "r2_score": float(r2_score(y_true, y_pred)),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(mean_squared_error(y_true, y_pred) ** 0.5),
    }


def train_and_log_model(model_name, model_config, X_train, X_test, y_train, y_test):
    """
    Trains a single candidate model, logs params/metrics/artifacts to MLflow
    as its own run, and returns (pipeline, metrics_dict, run_id).
    """
    with mlflow.start_run(run_name=model_name) as run:
        pipeline = build_full_pipeline(model_config["estimator"])
        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)
        metrics = evaluate(y_test, y_pred)

        # ---- MLflow: log params ----
        mlflow.log_param("model_type", model_name)
        for k, v in model_config["params"].items():
            mlflow.log_param(k, v)
        mlflow.log_param("train_rows", len(X_train))
        mlflow.log_param("test_rows", len(X_test))

        # ---- MLflow: log metrics ----
        for metric_name, value in metrics.items():
            mlflow.log_metric(metric_name, value)

        # ---- MLflow: log the fitted pipeline as a model artifact ----
        mlflow.sklearn.log_model(pipeline, artifact_path="model")

        logger.info("[%s] metrics: %s", model_name, metrics)

        return pipeline, metrics, run.info.run_id


def select_best_model(results: dict):
    """
    Selects the best model based on R² Score primarily, using MAE as a
    tie-breaker (lower MAE wins on near-equal R²).
    `results` maps model_name -> {"pipeline":..., "metrics":..., "run_id":...}
    """
    best_name = max(
        results,
        key=lambda name: (round(results[name]["metrics"]["r2_score"], 4),
                           -results[name]["metrics"]["mae"]),
    )
    return best_name, results[best_name]


def register_best_model(best_name: str, best_result: dict) -> Path:
    """
    Step 5 - Model Registration.

    Persists the winning pipeline to disk with a simple, filesystem-based
    versioning strategy:
        models/
          model_v{timestamp}.joblib   <- immutable, versioned artifact
          model_latest.joblib         <- symlink/copy always pointing at the newest model
          model_metadata.json         <- which model won, its metrics, run id, version

    This mirrors what an MLflow Model Registry would give you (Staging /
    Production aliases), implemented here with plain files so the Flask
    app has zero external dependency on a running MLflow server at
    inference time.
    """
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    version_tag = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    versioned_path = MODEL_DIR / f"model_v{version_tag}.joblib"
    latest_path = MODEL_DIR / "model_latest.joblib"

    joblib.dump(best_result["pipeline"], versioned_path)
    shutil.copyfile(versioned_path, latest_path)

    metadata = {
        "model_name": best_name,
        "version": version_tag,
        "metrics": best_result["metrics"],
        "mlflow_run_id": best_result["run_id"],
        "registered_at_utc": datetime.utcnow().isoformat(),
        "artifact_path": str(versioned_path.name),
    }
    with open(MODEL_DIR / "model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)

    logger.info("Registered best model '%s' -> %s", best_name, versioned_path)
    return latest_path


def main():
    logger.info("=== STEP 1: Data Validation ===")
    validate_dataset(DEFAULT_DATA_PATH)
    raw_df = load_dataset(DEFAULT_DATA_PATH)
    df = clean_dataset(raw_df)

    logger.info("=== STEP 2: Preprocessing / Train-Test Split ===")
    X, y = split_features_target(df)
    X_train, X_test, y_train, y_test = train_test_split_data(X, y)
    logger.info("Train rows: %s | Test rows: %s", len(X_train), len(X_test))

    logger.info("=== STEP 3 & 4: Model Training + MLflow Tracking ===")
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    results = {}
    for model_name, model_config in CANDIDATE_MODELS.items():
        pipeline, metrics, run_id = train_and_log_model(
            model_name, model_config, X_train, X_test, y_train, y_test
        )
        results[model_name] = {"pipeline": pipeline, "metrics": metrics, "run_id": run_id}

    logger.info("=== Model comparison ===")
    for name, res in results.items():
        logger.info("%s -> R2=%.4f | MAE=%.2f | RMSE=%.2f",
                     name, res["metrics"]["r2_score"], res["metrics"]["mae"], res["metrics"]["rmse"])

    best_name, best_result = select_best_model(results)
    logger.info("Best model selected: %s (R2=%.4f, MAE=%.2f)",
                best_name, best_result["metrics"]["r2_score"], best_result["metrics"]["mae"])

    logger.info("=== STEP 5: Model Registration ===")
    register_best_model(best_name, best_result)

    logger.info("Training pipeline complete.")


if __name__ == "__main__":
    main()
