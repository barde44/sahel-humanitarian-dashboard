"""Project configuration and constants."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_RAW = BASE_DIR / "data" / "raw"
DATA_CLEANED = BASE_DIR / "data" / "cleaned"
DATA_REF = BASE_DIR / "data" / "reference"
REPORTS_DIR = BASE_DIR / "reports"

DB_URL = (
    f"postgresql://{os.getenv('DB_USER', 'postgres')}:"
    f"{os.getenv('DB_PASSWORD', '')}@"
    f"{os.getenv('DB_HOST', 'localhost')}:"
    f"{os.getenv('DB_PORT', '5432')}/"
    f"{os.getenv('DB_NAME', 'sahel_dashboard')}"
)

# Chad provinces for the nutrition program
PROVINCES = {
    "Lac": {
        "departments": ["Bol", "Mamdi", "Wayi"],
        "population_weight": 0.35,
    },
    "Kanem": {
        "departments": ["Kanem", "Nord Kanem", "Wadi Bissam"],
        "population_weight": 0.35,
    },
    "Batha": {
        "departments": ["Batha Ouest", "Batha Est", "Fitri"],
        "population_weight": 0.30,
    },
}

# Nutrition program parameters
INTERVENTION_TYPES = [
    "CMAM_OTP",        # Community-based management of acute malnutrition - outpatient
    "CMAM_SC",         # Stabilization center (severe cases)
    "BSFP",            # Blanket supplementary feeding programme
    "IYCF_Counseling", # Infant and young child feeding counseling
    "Screening",       # Nutrition screening
]

NUTRITION_STATUS = ["Normal", "MAM", "MAS"]  # Moderate / Severe acute malnutrition

# MUAC thresholds (mm) for children 6-59 months
MUAC_THRESHOLDS = {
    "MAS": 115,     # < 115mm = severe
    "MAM": 125,     # 115-125mm = moderate
    "Normal": 125,  # >= 125mm = normal
}

# Target beneficiaries per province per month
MONTHLY_TARGETS = {"Lac": 200, "Kanem": 180, "Batha": 150}

# Data quality: deliberate error rates for synthetic data
ERROR_RATES = {
    "duplicate": 0.03,
    "missing_age": 0.04,
    "missing_muac": 0.02,
    "outlier_muac": 0.01,
    "future_date": 0.005,
    "invalid_status": 0.005,
}

RECORD_COUNT = 5000
