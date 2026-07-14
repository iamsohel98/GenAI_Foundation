"""
generate_data.py
-----------------
Generates a synthetic 'home_rent_data.csv' dataset used to train the
Home Rent Prediction model.

In a real project this file would be replaced by an actual data export
(from a scraper, a database dump, or a partner API). It is kept here so
the whole pipeline is reproducible from scratch with a single command:

    python src/generate_data.py
"""

import numpy as np
import pandas as pd
from pathlib import Path

# Reproducibility
np.random.seed(42)

N_ROWS = 1200

LOCATIONS = [
    "Andheri", "Bandra", "Powai", "Dadar", "Thane",
    "Malad", "Borivali", "Chembur", "Goregaon", "Kandivali",
]

FURNISHING_TYPES = ["Unfurnished", "Semi-Furnished", "Fully-Furnished"]

# Base rent-per-sqft varies by locality (simulates real-world market price)
LOCATION_BASE_RATE = {
    "Andheri": 55, "Bandra": 90, "Powai": 70, "Dadar": 80, "Thane": 40,
    "Malad": 45, "Borivali": 42, "Chembur": 50, "Goregaon": 48, "Kandivali": 44,
}

FURNISHING_MULTIPLIER = {
    "Unfurnished": 1.00,
    "Semi-Furnished": 1.12,
    "Fully-Furnished": 1.28,
}


def generate_row():
    location = np.random.choice(LOCATIONS)
    bhk = np.random.choice([1, 2, 3, 4], p=[0.25, 0.4, 0.25, 0.1])
    area_sqft = int(np.clip(np.random.normal(bhk * 350, 80), 300, 3500))
    bathrooms = int(np.clip(bhk + np.random.choice([-1, 0, 0, 1]), 1, bhk + 1))
    furnishing = np.random.choice(FURNISHING_TYPES, p=[0.4, 0.35, 0.25])
    parking = np.random.choice([0, 1], p=[0.35, 0.65])

    base_rate = LOCATION_BASE_RATE[location]
    furnishing_mult = FURNISHING_MULTIPLIER[furnishing]

    rent = (
        area_sqft * base_rate * furnishing_mult
        + bathrooms * 1500
        + parking * 2000
        + bhk * 1000
    )
    # Add market noise
    rent = rent * np.random.normal(1.0, 0.07)
    rent = int(max(rent, 4000))  # floor rent

    return {
        "location": location,
        "bhk": bhk,
        "area_sqft": area_sqft,
        "bathrooms": bathrooms,
        "furnishing": furnishing,
        "parking": parking,
        "rent": rent,
    }


def inject_data_quality_issues(df: pd.DataFrame) -> pd.DataFrame:
    """Deliberately inject a few nulls / duplicates so the data
    validation stage in the pipeline has something meaningful to catch.
    This mirrors real-world messy data."""
    df = df.copy()

    # Inject a few nulls
    null_idx = np.random.choice(df.index, size=5, replace=False)
    df.loc[null_idx, "bathrooms"] = np.nan

    # Inject a few duplicate rows
    dup_rows = df.sample(3, random_state=1)
    df = pd.concat([df, dup_rows], ignore_index=True)

    return df


def main():
    rows = [generate_row() for _ in range(N_ROWS)]
    df = pd.DataFrame(rows)
    df = inject_data_quality_issues(df)

    out_path = Path(__file__).resolve().parent.parent / "data" / "home_rent_data.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} rows -> {out_path}")


if __name__ == "__main__":
    main()
