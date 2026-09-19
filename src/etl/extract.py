"""Extract data from KoboToolbox API or local CSV export.

In production, this module calls the KoboToolbox API. For this portfolio
project, it reads from the synthetic CSV export (simulating what the API
returns after export).
"""

import os
import json
from pathlib import Path

import pandas as pd
import requests

from src.config import DATA_RAW


def extract_from_kobo_api(api_url: str, token: str, form_uid: str) -> pd.DataFrame:
    """Extract submissions from KoboToolbox API v2.

    This is the production-ready function. It calls the real API.
    Requires KOBO_TOKEN and KOBO_FORM_UID in .env.
    """
    headers = {"Authorization": f"Token {token}"}
    url = f"{api_url}/assets/{form_uid}/data.json"

    all_results = []
    while url:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        all_results.extend(data.get("results", []))
        url = data.get("next")

    df = pd.json_normalize(all_results)
    print(f"Extracted {len(df)} records from KoboToolbox API")
    return df


def extract_from_csv(filename: str = "kobo_nutrition_export.csv") -> pd.DataFrame:
    """Extract from local CSV export (simulates KoboToolbox export)."""
    filepath = DATA_RAW / filename
    if not filepath.exists():
        raise FileNotFoundError(
            f"{filepath} not found. Run `python -m src.generate.synthetic_data` first."
        )

    df = pd.read_csv(filepath)
    print(f"Extracted {len(df)} records from {filepath}")
    return df


def extract(source: str = "csv") -> pd.DataFrame:
    """Main extraction entry point."""
    if source == "api":
        api_url = os.getenv("KOBO_API_URL")
        token = os.getenv("KOBO_TOKEN")
        form_uid = os.getenv("KOBO_FORM_UID")
        if not all([api_url, token, form_uid]):
            raise ValueError("Set KOBO_API_URL, KOBO_TOKEN, KOBO_FORM_UID in .env")
        return extract_from_kobo_api(api_url, token, form_uid)

    return extract_from_csv()


if __name__ == "__main__":
    df = extract()
    print(f"\nShape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
