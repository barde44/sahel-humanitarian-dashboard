"""Load cleaned data into PostgreSQL.

Creates the schema and loads the transformed beneficiary data.
Can also export to CSV/Excel for Power BI if PostgreSQL is not available.
"""

import pandas as pd
from sqlalchemy import create_engine, text

from src.config import DB_URL, DATA_CLEANED


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS provinces (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    population_weight FLOAT
);

CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    province_id INTEGER REFERENCES provinces(id)
);

CREATE TABLE IF NOT EXISTS beneficiaries (
    id SERIAL PRIMARY KEY,
    beneficiary_id VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    sex CHAR(1),
    age_months INTEGER,
    age_group VARCHAR(10),
    caregiver_name VARCHAR(200),
    province VARCHAR(50),
    department VARCHAR(100),
    village VARCHAR(100),
    submission_date DATE,
    month VARCHAR(7),
    year INTEGER,
    intervention_type VARCHAR(50),
    nutrition_status VARCHAR(10),
    muac_mm FLOAT,
    muac_status VARCHAR(10),
    follow_up_status VARCHAR(20),
    referred BOOLEAN,
    data_collector VARCHAR(50),
    collection_site VARCHAR(100),
    quality_score INTEGER,
    quality_flag TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ben_province ON beneficiaries(province);
CREATE INDEX IF NOT EXISTS idx_ben_date ON beneficiaries(submission_date);
CREATE INDEX IF NOT EXISTS idx_ben_status ON beneficiaries(nutrition_status);
CREATE INDEX IF NOT EXISTS idx_ben_month ON beneficiaries(month);
"""


def create_schema(engine):
    """Create database tables."""
    with engine.connect() as conn:
        for statement in SCHEMA_SQL.split(";"):
            stmt = statement.strip()
            if stmt:
                conn.execute(text(stmt))
        conn.commit()
    print("Database schema created.")


def load_to_postgres(df: pd.DataFrame):
    """Load cleaned data into PostgreSQL."""
    engine = create_engine(DB_URL)
    create_schema(engine)

    # Rename quality flag column
    df = df.rename(columns={"_quality_flag": "quality_flag"})

    # Select columns matching the table
    table_cols = [
        "beneficiary_id", "first_name", "last_name", "sex", "age_months",
        "age_group", "caregiver_name", "province", "department", "village",
        "submission_date", "month", "year", "intervention_type",
        "nutrition_status", "muac_mm", "muac_status", "follow_up_status",
        "referred", "data_collector", "collection_site", "quality_score",
        "quality_flag",
    ]
    df_load = df[[c for c in table_cols if c in df.columns]].copy()
    df_load["age_group"] = df_load["age_group"].astype(str)

    df_load.to_sql("beneficiaries", engine, if_exists="replace", index=False)
    print(f"Loaded {len(df_load)} records into PostgreSQL (beneficiaries table)")

    engine.dispose()


def load_to_csv(df: pd.DataFrame):
    """Export cleaned data as CSV and Excel for Power BI (no DB required)."""
    DATA_CLEANED.mkdir(parents=True, exist_ok=True)

    csv_path = DATA_CLEANED / "beneficiaries_for_powerbi.csv"
    df.to_csv(csv_path, index=False)
    print(f"Exported CSV for Power BI: {csv_path}")

    xlsx_path = DATA_CLEANED / "beneficiaries_for_powerbi.xlsx"
    df.to_excel(xlsx_path, index=False, sheet_name="Beneficiaries")
    print(f"Exported Excel for Power BI: {xlsx_path}")


def load(df: pd.DataFrame, target: str = "csv"):
    """Main load entry point."""
    print("\n--- Load ---")
    if target == "postgres":
        load_to_postgres(df)
    load_to_csv(df)


if __name__ == "__main__":
    filepath = DATA_CLEANED / "beneficiaries_clean.csv"
    if not filepath.exists():
        print("Run transform first: python -m src.etl.transform")
    else:
        df = pd.read_csv(filepath)
        load(df)
