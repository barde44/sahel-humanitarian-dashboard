"""Generate realistic synthetic humanitarian nutrition data for Chad's Sahel.

Produces ~5,000 beneficiary records mimicking KoboToolbox exports, including
deliberate data quality issues (duplicates, missing values, outliers) to
demonstrate cleaning capabilities.
"""

import random
import uuid
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker

from src.config import (
    PROVINCES, INTERVENTION_TYPES, NUTRITION_STATUS,
    MUAC_THRESHOLDS, ERROR_RATES, RECORD_COUNT, DATA_RAW,
)

fake_fr = Faker("fr_FR")
Faker.seed(42)
random.seed(42)
np.random.seed(42)

# Common Chadian first names
MALE_NAMES = [
    "Mahamat", "Adam", "Abdoulaye", "Ousmane", "Ibrahim", "Moussa",
    "Youssouf", "Ali", "Hassan", "Abakar", "Djibrine", "Ismail",
    "Saleh", "Brahim", "Tahir", "Hissein", "Adoum", "Abdelkerim",
]
FEMALE_NAMES = [
    "Fatima", "Amina", "Hawa", "Mariam", "Khadija", "Aisha",
    "Zara", "Halima", "Falmata", "Ndjamena", "Achta", "Habiba",
    "Mounira", "Zenaba", "Kaltouma", "Fatime", "Djamila", "Hadja",
]
FAMILY_NAMES = [
    "Mahamat", "Adam", "Ali", "Abdoulaye", "Ousmane", "Hassan",
    "Ibrahim", "Moussa", "Tahir", "Djibrine", "Abakar", "Brahim",
    "Ismail", "Saleh", "Youssouf", "Adoum", "Hissein", "Deby",
]

# Village names by department
VILLAGES = {
    "Bol": ["Bol Centre", "Baga Sola", "Kaya", "Liwa", "Tchoukoutalia"],
    "Mamdi": ["Mamdi", "Ngouri", "Doum Doum", "Isseirom"],
    "Wayi": ["Wayi", "Kouloudia", "Mao Sud"],
    "Kanem": ["Mao", "Mondo", "Moussoro Sud", "Kekedina"],
    "Nord Kanem": ["Nokou", "Rig Rig", "Ziguey"],
    "Wadi Bissam": ["Wadi Bissam", "Amdoback", "Ntiona"],
    "Batha Ouest": ["Ati", "Djeddaa", "Assinet"],
    "Batha Est": ["Oum Hadjer", "Am Dam", "Mangalme"],
    "Fitri": ["Yao", "Fitri Centre", "Abourda"],
}


def generate_beneficiary_id():
    return f"BEN-{uuid.uuid4().hex[:8].upper()}"


def pick_location():
    province = random.choices(
        list(PROVINCES.keys()),
        weights=[p["population_weight"] for p in PROVINCES.values()],
    )[0]
    department = random.choice(PROVINCES[province]["departments"])
    village = random.choice(VILLAGES[department])
    return province, department, village


def generate_muac(status):
    if status == "MAS":
        return max(80, int(np.random.normal(108, 5)))
    elif status == "MAM":
        return int(np.random.normal(120, 3))
    else:
        return int(np.random.normal(140, 10))


def generate_record(submission_date):
    sex = random.choice(["M", "F"])
    age_months = random.randint(6, 59)
    first_name = random.choice(MALE_NAMES if sex == "M" else FEMALE_NAMES)
    last_name = random.choice(FAMILY_NAMES)

    status_weights = [0.60, 0.25, 0.15]  # Normal, MAM, MAS
    nutrition_status = random.choices(NUTRITION_STATUS, weights=status_weights)[0]

    intervention = random.choice(INTERVENTION_TYPES)
    if nutrition_status == "MAS":
        intervention = random.choice(["CMAM_SC", "CMAM_OTP"])
    elif nutrition_status == "MAM":
        intervention = random.choice(["CMAM_OTP", "BSFP"])

    province, department, village = pick_location()
    muac = generate_muac(nutrition_status)

    follow_up = random.choice(["New", "Follow-up_1", "Follow-up_2", "Discharged"])
    if nutrition_status == "Normal" and intervention == "Screening":
        follow_up = "New"

    return {
        "beneficiary_id": generate_beneficiary_id(),
        "submission_date": submission_date.strftime("%Y-%m-%d"),
        "first_name": first_name,
        "last_name": last_name,
        "sex": sex,
        "age_months": age_months,
        "province": province,
        "department": department,
        "village": village,
        "intervention_type": intervention,
        "nutrition_status": nutrition_status,
        "muac_mm": muac,
        "follow_up_status": follow_up,
        "referred": nutrition_status == "MAS" and random.random() < 0.7,
        "caregiver_name": f"{random.choice(FEMALE_NAMES)} {last_name}",
        "data_collector": f"Agent_{random.randint(1, 25):02d}",
        "collection_site": f"{village}_CSI" if random.random() < 0.6 else f"{village}_Mobile",
    }


def inject_errors(df):
    """Inject realistic data quality issues."""
    n = len(df)
    records = df.copy()

    # Duplicates: copy some rows with slight timestamp variation
    n_dup = int(n * ERROR_RATES["duplicate"])
    dup_idx = random.sample(range(n), n_dup)
    duplicates = records.iloc[dup_idx].copy()
    duplicates["beneficiary_id"] = [generate_beneficiary_id() for _ in range(n_dup)]
    records = pd.concat([records, duplicates], ignore_index=True)

    # Missing age
    n_missing_age = int(n * ERROR_RATES["missing_age"])
    missing_age_idx = random.sample(range(len(records)), n_missing_age)
    records.loc[missing_age_idx, "age_months"] = np.nan

    # Missing MUAC
    n_missing_muac = int(n * ERROR_RATES["missing_muac"])
    missing_muac_idx = random.sample(range(len(records)), n_missing_muac)
    records.loc[missing_muac_idx, "muac_mm"] = np.nan

    # Outlier MUAC (impossibly high or low)
    n_outlier = int(n * ERROR_RATES["outlier_muac"])
    outlier_idx = random.sample(range(len(records)), n_outlier)
    records.loc[outlier_idx, "muac_mm"] = random.choices([250, 300, 50, 40], k=n_outlier)

    # Future dates
    n_future = int(n * ERROR_RATES["future_date"])
    future_idx = random.sample(range(len(records)), n_future)
    future_dates = [
        (datetime.now() + timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d")
        for _ in range(n_future)
    ]
    records.loc[future_idx, "submission_date"] = future_dates

    # Invalid nutrition status
    n_invalid = int(n * ERROR_RATES["invalid_status"])
    invalid_idx = random.sample(range(len(records)), n_invalid)
    records.loc[invalid_idx, "nutrition_status"] = random.choices(
        ["UNKNOWN", "", "N/A", "Modéré"], k=n_invalid
    )

    return records.sample(frac=1, random_state=42).reset_index(drop=True)


def generate_dataset():
    """Generate the full synthetic dataset."""
    print(f"Generating {RECORD_COUNT} beneficiary records...")

    # Spread records across 12 months (Oct 2025 - Sep 2026)
    start_date = datetime(2025, 10, 1)
    end_date = datetime(2026, 9, 30)
    date_range = (end_date - start_date).days

    records = []
    for _ in range(RECORD_COUNT):
        offset = random.randint(0, date_range)
        sub_date = start_date + timedelta(days=offset)
        # More submissions during lean season (June-September)
        if sub_date.month in [6, 7, 8, 9]:
            if random.random() < 0.3:
                continue
        records.append(generate_record(sub_date))

    # Top up to target count
    while len(records) < RECORD_COUNT:
        offset = random.randint(0, date_range)
        sub_date = start_date + timedelta(days=offset)
        records.append(generate_record(sub_date))

    df = pd.DataFrame(records[:RECORD_COUNT])

    # Add a kobo-style _uuid and _submission_time
    df["_uuid"] = [str(uuid.uuid4()) for _ in range(len(df))]
    df["_submission_time"] = pd.to_datetime(df["submission_date"]) + pd.to_timedelta(
        np.random.randint(8, 18, size=len(df)), unit="h"
    )

    print(f"  Clean records: {len(df)}")

    # Inject errors
    df_dirty = inject_errors(df)
    print(f"  After error injection: {len(df_dirty)} records")
    print(f"  Added ~{len(df_dirty) - len(df)} duplicates")

    # Save
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    output_path = DATA_RAW / "kobo_nutrition_export.csv"
    df_dirty.to_csv(output_path, index=False)
    print(f"  Saved to: {output_path}")

    # Also save the clean version for validation
    clean_path = DATA_RAW / "kobo_nutrition_export_ground_truth.csv"
    df.to_csv(clean_path, index=False)
    print(f"  Ground truth saved to: {clean_path}")

    # Summary stats
    print("\n--- Dataset Summary ---")
    print(f"Provinces: {df['province'].value_counts().to_dict()}")
    print(f"Nutrition status: {df['nutrition_status'].value_counts().to_dict()}")
    print(f"Sex: {df['sex'].value_counts().to_dict()}")
    print(f"Date range: {df['submission_date'].min()} to {df['submission_date'].max()}")

    return df_dirty


if __name__ == "__main__":
    generate_dataset()
