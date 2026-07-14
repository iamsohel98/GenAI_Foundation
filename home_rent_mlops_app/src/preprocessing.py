"""
preprocessing.py
-----------------
Step 2 of the MLOps lifecycle: Data Preprocessing.

Builds a single reusable scikit-learn Pipeline (via ColumnTransformer) that:
    - One-Hot Encodes categorical features (location, furnishing)
    - Scales numeric features (bhk, area_sqft, bathrooms, parking)

The SAME fitted preprocessing pipeline object is bundled together with the
trained model (as one joblib artifact), so at inference time in Flask we
never risk "training/serving skew" -- the exact transformations used during
training are guaranteed to be reapplied during prediction.
"""

from typing import Tuple

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

CATEGORICAL_FEATURES = ["location", "furnishing"]
NUMERIC_FEATURES = ["bhk", "area_sqft", "bathrooms", "parking"]
TARGET_COLUMN = "rent"

ALL_FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES


def build_preprocessor() -> ColumnTransformer:
    """
    Returns an UNFITTED ColumnTransformer that:
      - One-Hot Encodes categorical columns (handle_unknown='ignore' so that
        a category unseen during training does not crash inference).
      - Standard-scales numeric columns (zero mean, unit variance).
    """
    categorical_transformer = OneHotEncoder(handle_unknown="ignore")
    numeric_transformer = StandardScaler()

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
            ("num", numeric_transformer, NUMERIC_FEATURES),
        ]
    )
    return preprocessor


def split_features_target(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """Splits a cleaned dataframe into X (features) and y (target)."""
    X = df[ALL_FEATURES].copy()
    y = df[TARGET_COLUMN].copy()
    return X, y


def train_test_split_data(
    X: pd.DataFrame, y: pd.Series, test_size: float = 0.2, random_state: int = 42
):
    """Thin wrapper around sklearn's train_test_split for consistency across the project."""
    return train_test_split(X, y, test_size=test_size, random_state=random_state)


def build_full_pipeline(regressor) -> Pipeline:
    """
    Wraps preprocessing + a given regressor into a single end-to-end
    scikit-learn Pipeline. This is the object that actually gets
    fit(), predict()-ed, and persisted to disk / MLflow.
    """
    preprocessor = build_preprocessor()
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", regressor),
        ]
    )
    return pipeline
