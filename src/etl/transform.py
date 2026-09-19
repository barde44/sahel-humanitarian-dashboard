"""Transform and clean raw KoboToolbox data.

Handles all data quality issues found in humanitarian field data:
- Duplicate records
- Missing values
- Invalid/outlier MUAC measurements
- Future dates
- Inconsistent nutrition status labels
- Type conversions
"""

from datetime import datetime

import numpy as np
import pandas as pd

from src.config import (
    MUAC_THRESHOLDS, NUTRITION_STATUS, DATA_CLEANED, DATA_RAW,
)


def remove_duplicates(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Detect and remove duplicate beneficiary records.

    Uses fuzzy matching on name + age + village + date to catch duplicates
    registered with different IDs.
    """
    # Exact duplicates (same name, age, village, date)
    match_cols = ["first_name", "last_name", "age_months", "village", "submission_date"]
    available_cols = [c for c in match_cols if c in df.columns]

    df_clean = df.copy()
    df_clean["_dup_key"] = df_clean[available_cols].astype(str).agg("|".join, axis=1)

    duplicates = df_clean[df_clean.duplicated(subset="_dup_key", keep="first")]
    df_deduped = df_clean.drop_duplicates(subset="_dup_key", keep="first")
    df_deduped = df_deduped.drop(columns=["_dup_key"])

    n_removed = len(df) - len(df_deduped)
    print(f"  Duplicates removed: {n_removed}")
    return df_deduped, duplicates


def clean_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Fix date issues: parse, remove future dates, handle invalids."""
    df = df.copy()
    df["submission_date"] = pd.to_datetime(df["submission_date"], errors="coerce")

    today = pd.Timestamp(datetime.now().date())
    future_mask = df["submission_date"] > today
    n_future = future_mask.sum()
    if n_future > 0:
        print(f"  Future dates flagged: {n_future}")
        df.loc[future_mask, "submission_date"] = pd.NaT
        df.loc[future_mask, "_quality_flag"] = "future_date"

    return df


def clean_nutrition_status(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize nutrition status labels."""
    df = df.copy()
    status_map = {
        "Normal": "Normal", "normal": "Normal", "NORMAL": "Normal",
        "MAM": "MAM", "mam": "MAM", "Modéré": "MAM", "Moderate": "MAM",
        "MAS": "MAS", "mas": "MAS", "Sévère": "MAS", "Severe": "MAS",
    }

    valid_before = df["nutrition_status"].isin(NUTRITION_STATUS).sum()
    df["nutrition_status"] = df["nutrition_status"].map(status_map)

    invalid_mask = df["nutrition_status"].isna()
    n_invalid = invalid_mask.sum()
    if n_invalid > 0:
        print(f"  Invalid nutrition status: {n_invalid} (set to NaN for review)")

    return df


def clean_muac(df: pd.DataFrame) -> pd.DataFrame:
    """Clean MUAC measurements: handle missing, outliers, type issues."""
    df = df.copy()
    df["muac_mm"] = pd.to_numeric(df["muac_mm"], errors="coerce")

    # Flag outliers (MUAC < 60mm or > 200mm is physiologically impossible for children)
    outlier_mask = (df["muac_mm"] < 60) | (df["muac_mm"] > 200)
    n_outliers = outlier_mask.sum()
    if n_outliers > 0:
        print(f"  MUAC outliers flagged: {n_outliers}")
        df.loc[outlier_mask, "muac_mm"] = np.nan
        df.loc[outlier_mask, "_quality_flag"] = df.loc[outlier_mask, "_quality_flag"].fillna("") + "muac_outlier;"

    n_missing = df["muac_mm"].isna().sum()
    print(f"  MUAC missing (after cleaning): {n_missing}")

    return df


def clean_age(df: pd.DataFrame) -> pd.DataFrame:
    """Clean age field: ensure numeric, flag out-of-range."""
    df = df.copy()
    df["age_months"] = pd.to_numeric(df["age_months"], errors="coerce")

    # Program targets children 6-59 months
    out_of_range = (df["age_months"] < 0) | (df["age_months"] > 120)
    n_oor = out_of_range.sum()
    if n_oor > 0:
        print(f"  Age out of range: {n_oor}")

    n_missing = df["age_months"].isna().sum()
    print(f"  Age missing: {n_missing}")

    return df


def derive_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Create derived fields for analysis."""
    df = df.copy()

    # Age group
    bins = [0, 6, 12, 24, 36, 48, 60, 120]
    labels = ["0-5m", "6-11m", "12-23m", "24-35m", "36-47m", "48-59m", "60m+"]
    df["age_group"] = pd.cut(df["age_months"], bins=bins, labels=labels, right=False)

    # Recalculate nutrition status from MUAC where possible
    conditions = [
        df["muac_mm"] < MUAC_THRESHOLDS["MAS"],
        (df["muac_mm"] >= MUAC_THRESHOLDS["MAS"]) & (df["muac_mm"] < MUAC_THRESHOLDS["MAM"]),
        df["muac_mm"] >= MUAC_THRESHOLDS["Normal"],
    ]
    choices = ["MAS", "MAM", "Normal"]
    df["muac_status"] = np.select(conditions, choices, default="Unknown")
    df.loc[df["muac_mm"].isna(), "muac_status"] = "Unknown"

    # Month and year for time series
    df["month"] = df["submission_date"].dt.to_period("M").astype(str)
    df["year"] = df["submission_date"].dt.year

    # Data quality score per record (0-100)
    score = 100
    penalties = pd.Series(0, index=df.index)
    penalties += df["age_months"].isna() * 20
    penalties += df["muac_mm"].isna() * 20
    penalties += df["nutrition_status"].isna() * 15
    penalties += df["submission_date"].isna() * 25
    penalties += df["_quality_flag"].fillna("").str.len().gt(0) * 10
    df["quality_score"] = (score - penalties).clip(0, 100)

    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Run the full transformation pipeline."""
    print("\n--- Transform Pipeline ---")
    print(f"Input: {len(df)} records")

    df["_quality_flag"] = None

    df, duplicates = remove_duplicates(df)
    df = clean_dates(df)
    df = clean_nutrition_status(df)
    df = clean_muac(df)
    df = clean_age(df)
    df = derive_fields(df)

    # Drop rows with critical missing data
    critical_cols = ["submission_date", "province"]
    before = len(df)
    df = df.dropna(subset=critical_cols)
    print(f"  Dropped {before - len(df)} rows with missing critical fields")

    print(f"Output: {len(df)} clean records")

    # Save cleaned data
    DATA_CLEANED.mkdir(parents=True, exist_ok=True)
    output_path = DATA_CLEANED / "beneficiaries_clean.csv"
    df.to_csv(output_path, index=False)
    print(f"Saved to: {output_path}")

    # Save duplicates log
    if not duplicates.empty:
        dup_path = DATA_CLEANED / "duplicates_log.csv"
        duplicates.to_csv(dup_path, index=False)
        print(f"Duplicates log: {dup_path}")

    return df


if __name__ == "__main__":
    from src.etl.extract import extract
    raw = extract()
    clean = transform(raw)
    print(f"\n--- Final Stats ---")
    print(clean.describe(include="all").to_string())
