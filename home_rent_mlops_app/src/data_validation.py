"""
data_validation.py
-------------------
Step 1 of the MLOps lifecycle: Data Ingestion & Validation.

Responsibilities:
    1. Read the raw dataset from CSV.
    2. Validate schema (expected columns / dtypes).
    3. Check for null values.
    4. Check for duplicate rows.
    5. Generate a human-readable + machine-readable validation report.

This module is imported by:
    - src/train.py          (before training starts)
    - tests/test_app.py     (unit tests for validation logic)

It can also be run standalone:
    python src/data_validation.py
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

EXPECTED_COLUMNS = [
    "location",
    "bhk",
    "area_sqft",
    "bathrooms",
    "furnishing",
    "parking",
    "rent",
]

NUMERIC_COLUMNS = ["bhk", "area_sqft", "bathrooms", "parking", "rent"]

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_PATH = ROOT_DIR / "data" / "home_rent_data.csv"
REPORT_PATH = ROOT_DIR / "data" / "validation_report.json"


@dataclass
class ValidationReport:
    """Structured container for validation results."""

    file_path: str
    total_rows: int = 0
    total_columns: int = 0
    missing_columns: List[str] = field(default_factory=list)
    null_counts: dict = field(default_factory=dict)
    duplicate_rows: int = 0
    rows_after_cleaning: int = 0
    is_valid: bool = False
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return self.__dict__

    def save(self, path: Path = REPORT_PATH) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=4, default=str)
        logger.info("Validation report saved to %s", path)


def load_dataset(path: Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """Reads the CSV dataset from disk. Raises FileNotFoundError if missing."""
    if not Path(path).exists():
        raise FileNotFoundError(f"Dataset not found at: {path}")
    df = pd.read_csv(path)
    logger.info("Loaded dataset with shape: %s", df.shape)
    return df


def check_missing_columns(df: pd.DataFrame) -> List[str]:
    """Returns list of expected columns that are missing from the dataframe."""
    return [col for col in EXPECTED_COLUMNS if col not in df.columns]


def check_null_values(df: pd.DataFrame) -> dict:
    """Returns a dict of column -> null count for every column that has nulls."""
    null_counts = df.isnull().sum()
    return {col: int(count) for col, count in null_counts.items() if count > 0}


def check_duplicates(df: pd.DataFrame) -> int:
    """Returns the number of fully-duplicated rows in the dataframe."""
    return int(df.duplicated().sum())


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies basic cleaning:
      - Drops duplicate rows
      - Drops rows with nulls in critical columns
      - Enforces sane value ranges (defensive programming)
    Returns a cleaned copy; does NOT mutate the input.
    """
    cleaned = df.copy()
    cleaned = cleaned.drop_duplicates()
    cleaned = cleaned.dropna(subset=EXPECTED_COLUMNS)

    # Guard against nonsensical rows that would poison the model
    cleaned = cleaned[cleaned["area_sqft"] > 0]
    cleaned = cleaned[cleaned["rent"] > 0]
    cleaned = cleaned[cleaned["bhk"] > 0]
    cleaned = cleaned[cleaned["bathrooms"] > 0]

    cleaned = cleaned.reset_index(drop=True)
    return cleaned


def validate_dataset(path: Path = DEFAULT_DATA_PATH, save_report: bool = True) -> ValidationReport:
    """
    Runs the full validation flow and returns a ValidationReport.
    Raises ValueError if the dataset is fundamentally invalid
    (e.g. missing required columns / empty file).
    """
    report = ValidationReport(file_path=str(path))

    try:
        df = load_dataset(path)
    except FileNotFoundError as e:
        report.errors.append(str(e))
        report.is_valid = False
        if save_report:
            report.save()
        raise

    report.total_rows = len(df)
    report.total_columns = len(df.columns)
    report.missing_columns = check_missing_columns(df)
    report.null_counts = check_null_values(df)
    report.duplicate_rows = check_duplicates(df)

    if report.missing_columns:
        report.errors.append(f"Missing required columns: {report.missing_columns}")

    if report.total_rows == 0:
        report.errors.append("Dataset is empty.")

    cleaned = clean_dataset(df) if not report.missing_columns else pd.DataFrame()
    report.rows_after_cleaning = len(cleaned)
    report.is_valid = len(report.errors) == 0 and report.rows_after_cleaning > 0

    if save_report:
        report.save()

    logger.info("Validation complete. is_valid=%s | rows: %s -> %s (after cleaning)",
                report.is_valid, report.total_rows, report.rows_after_cleaning)

    if not report.is_valid:
        raise ValueError(f"Dataset failed validation: {report.errors}")

    return report


if __name__ == "__main__":
    validate_dataset()
