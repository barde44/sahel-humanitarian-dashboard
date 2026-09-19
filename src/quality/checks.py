"""Automated data quality checks for the humanitarian dashboard.

Produces a quality report summarizing issues found in the cleaned dataset.
This is what an Information Management Officer would review before
publishing dashboard data.
"""

from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np

from src.config import DATA_CLEANED, REPORTS_DIR, MONTHLY_TARGETS


def check_completeness(df: pd.DataFrame) -> dict:
    """Check for missing values in critical fields."""
    critical = ["beneficiary_id", "submission_date", "province", "sex",
                "age_months", "nutrition_status", "muac_mm"]
    results = {}
    for col in critical:
        if col in df.columns:
            n_missing = df[col].isna().sum()
            pct = round(n_missing / len(df) * 100, 1)
            results[col] = {"missing": int(n_missing), "pct": pct}
    return results


def check_consistency(df: pd.DataFrame) -> list[str]:
    """Check logical consistency between fields."""
    issues = []

    # MUAC vs nutrition status consistency
    if "muac_mm" in df.columns and "nutrition_status" in df.columns:
        mask_muac_mas = df["muac_mm"] < 115
        mask_status_normal = df["nutrition_status"] == "Normal"
        inconsistent = (mask_muac_mas & mask_status_normal).sum()
        if inconsistent > 0:
            issues.append(f"MUAC < 115mm but status 'Normal': {inconsistent} records")

    # MAS should have referral
    if "nutrition_status" in df.columns and "referred" in df.columns:
        mas_no_ref = ((df["nutrition_status"] == "MAS") & (~df["referred"])).sum()
        if mas_no_ref > 0:
            issues.append(f"MAS cases without referral: {mas_no_ref} records")

    return issues


def check_coverage(df: pd.DataFrame) -> dict:
    """Check program coverage vs monthly targets."""
    if "month" not in df.columns or "province" not in df.columns:
        return {}

    coverage = {}
    for province, target in MONTHLY_TARGETS.items():
        province_data = df[df["province"] == province]
        monthly = province_data.groupby("month").size()
        coverage[province] = {
            "target_per_month": target,
            "avg_per_month": round(monthly.mean(), 0) if len(monthly) > 0 else 0,
            "min_month": int(monthly.min()) if len(monthly) > 0 else 0,
            "max_month": int(monthly.max()) if len(monthly) > 0 else 0,
            "months_below_target": int((monthly < target).sum()),
        }
    return coverage


def check_collector_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Flag data collectors with unusual patterns."""
    if "data_collector" not in df.columns:
        return pd.DataFrame()

    stats = df.groupby("data_collector").agg(
        total_records=("beneficiary_id", "count"),
        avg_quality=("quality_score", "mean"),
        pct_missing_muac=("muac_mm", lambda x: round(x.isna().mean() * 100, 1)),
        pct_mas=("nutrition_status", lambda x: round((x == "MAS").mean() * 100, 1)),
    ).round(1)

    # Flag collectors with quality score below 70 or high missing rate
    stats["flagged"] = (stats["avg_quality"] < 70) | (stats["pct_missing_muac"] > 10)

    return stats.sort_values("avg_quality")


def generate_report(df: pd.DataFrame) -> str:
    """Generate a comprehensive quality report."""
    print("\n--- Data Quality Checks ---")

    lines = []
    lines.append("# Data Quality Report")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Records analyzed:** {len(df)}")
    lines.append("")

    # 1. Completeness
    lines.append("## 1. Completeness")
    completeness = check_completeness(df)
    for field, stats in completeness.items():
        status = "OK" if stats["pct"] < 5 else "WARNING" if stats["pct"] < 10 else "CRITICAL"
        lines.append(f"- **{field}**: {stats['missing']} missing ({stats['pct']}%) [{status}]")
        print(f"  {field}: {stats['missing']} missing ({stats['pct']}%) [{status}]")
    lines.append("")

    # 2. Consistency
    lines.append("## 2. Consistency")
    issues = check_consistency(df)
    if issues:
        for issue in issues:
            lines.append(f"- WARNING: {issue}")
            print(f"  {issue}")
    else:
        lines.append("- All consistency checks passed.")
        print("  All consistency checks passed.")
    lines.append("")

    # 3. Coverage
    lines.append("## 3. Program Coverage vs Targets")
    coverage = check_coverage(df)
    for province, stats in coverage.items():
        pct = round(stats["avg_per_month"] / stats["target_per_month"] * 100) if stats["target_per_month"] > 0 else 0
        lines.append(f"- **{province}**: avg {stats['avg_per_month']}/month "
                     f"(target: {stats['target_per_month']}) = {pct}% coverage")
        print(f"  {province}: {pct}% coverage")
    lines.append("")

    # 4. Collector performance
    lines.append("## 4. Data Collector Performance")
    perf = check_collector_performance(df)
    if not perf.empty:
        flagged = perf[perf["flagged"]]
        lines.append(f"- **{len(flagged)}** collectors flagged for review (low quality or high missing rate)")
        if not flagged.empty:
            for name, row in flagged.head(5).iterrows():
                lines.append(f"  - {name}: avg quality {row['avg_quality']}, "
                            f"missing MUAC {row['pct_missing_muac']}%")
        print(f"  {len(flagged)} collectors flagged")
    lines.append("")

    # 5. Overall quality score
    lines.append("## 5. Overall Quality Score")
    avg_quality = df["quality_score"].mean() if "quality_score" in df.columns else 0
    lines.append(f"- **Average quality score: {avg_quality:.1f}/100**")
    print(f"  Average quality score: {avg_quality:.1f}/100")

    quality_dist = df["quality_score"].describe() if "quality_score" in df.columns else None
    if quality_dist is not None:
        lines.append(f"- Min: {quality_dist['min']:.0f} | "
                     f"Median: {quality_dist['50%']:.0f} | "
                     f"Max: {quality_dist['max']:.0f}")

    report = "\n".join(lines)

    # Save
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORTS_DIR / f"quality_report_{datetime.now().strftime('%Y%m%d')}.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"\nReport saved: {report_path}")

    return report


if __name__ == "__main__":
    filepath = DATA_CLEANED / "beneficiaries_clean.csv"
    if not filepath.exists():
        print("Run transform first: python -m src.etl.transform")
    else:
        df = pd.read_csv(filepath)
        generate_report(df)
