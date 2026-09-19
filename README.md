# Sahel Humanitarian Response Dashboard

End-to-end data pipeline and interactive dashboard for monitoring humanitarian nutrition programs in Chad's Sahel region.

## Problem

Humanitarian organizations in Chad's Sahel collect field data via KoboToolbox, but transforming raw submissions into actionable dashboards for program monitoring, donor reporting, and coordination remains manual and error-prone. Data quality issues (duplicates, missing values, inconsistencies) delay decision-making.

## Solution

A complete data pipeline:

```
KoboToolbox (collection) → Python ETL (clean & transform) → PostgreSQL (store) → Power BI (visualize)
```

With automated data quality checks that flag anomalies before they reach the dashboard.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌────────────┐     ┌───────────┐
│ KoboToolbox │────▶│  Python ETL  │────▶│ PostgreSQL │────▶│ Power BI  │
│  (collect)  │     │ (clean/load) │     │  (store)   │     │(dashboard)│
└─────────────┘     └──────┬───────┘     └────────────┘     └───────────┘
                           │
                    ┌──────▼───────┐     ┌───────────┐
                    │   Quality    │────▶│  Reports   │
                    │   Checks     │     │  (HTML/PDF)│
                    └──────────────┘     └───────────┘
```

## Dataset

Synthetic but realistic dataset simulating a nutrition program across 3 Chadian provinces:
- **~5,000 beneficiary records** across Lac, Kanem, and Batha provinces
- Variables: anonymized ID, location (province/department/village), sex, age, intervention type, date, nutrition status (MAM/MAS/normal), MUAC measurement, follow-up status
- Deliberately includes ~8% data quality issues (duplicates, outliers, missing fields) to demonstrate cleaning

## Tech Stack

| Tool | Role |
|------|------|
| **KoboToolbox** | Form design + data collection simulation |
| **Python 3.11+** | ETL pipeline, data generation, quality checks |
| **pandas** | Data manipulation and cleaning |
| **PostgreSQL 15+** | Structured storage |
| **SQLAlchemy** | ORM / database interface |
| **Power BI** | Interactive dashboard |
| **pytest** | Pipeline testing |
| **Git** | Version control |

## Project Structure

```
sahel-humanitarian-dashboard/
├── README.md
├── requirements.txt
├── .env.example
├── kobo/
│   └── nutrition_survey_form.xlsx    # XLSForm for KoboToolbox
├── src/
│   ├── __init__.py
│   ├── config.py                     # Settings and constants
│   ├── generate/
│   │   ├── __init__.py
│   │   └── synthetic_data.py         # Realistic data generator
│   ├── etl/
│   │   ├── __init__.py
│   │   ├── extract.py                # KoboToolbox API extraction
│   │   ├── transform.py              # Cleaning and transformation
│   │   └── load.py                   # PostgreSQL loading
│   └── quality/
│       ├── __init__.py
│       └── checks.py                 # Automated quality checks
├── data/
│   ├── raw/                          # Raw exports (gitignored)
│   ├── cleaned/                      # Cleaned datasets
│   └── reference/                    # Province codes, indicators
├── dashboards/
│   └── README.md                     # Power BI setup instructions
├── reports/                          # Generated quality reports
├── docs/
│   └── data_dictionary.md            # Variable definitions
└── tests/
    └── test_transform.py
```

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/barde44/sahel-humanitarian-dashboard.git
cd sahel-humanitarian-dashboard
pip install -r requirements.txt

# 2. Configure database
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# 3. Generate synthetic data
python -m src.generate.synthetic_data

# 4. Run ETL pipeline
python -m src.etl.extract
python -m src.etl.transform
python -m src.etl.load

# 5. Run quality checks
python -m src.quality.checks

# 6. Open Power BI dashboard
# See dashboards/README.md
```

## Key Indicators

- Beneficiaries reached (by province, sex, age group)
- MAM/MAS screening rates and outcomes
- Program coverage vs. targets
- Monthly trends and seasonal patterns
- Data quality score per collection site

## Data Governance

- All data is synthetic — no real beneficiary information
- Pipeline enforces data validation rules at ingestion
- Audit trail: every transformation is logged
- Quality checks run before any data reaches the dashboard

## Author

**Steven Barde** — [GitHub](https://github.com/barde44) | [LinkedIn](https://linkedin.com/in/stevenbarde)

*Personal portfolio project demonstrating humanitarian data pipeline skills. Not affiliated with any organization.*
