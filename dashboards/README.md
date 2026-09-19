# Power BI Dashboard — Setup Guide

## Data Source

Connect Power BI to the cleaned dataset:
- **File:** `data/cleaned/beneficiaries_for_powerbi.xlsx` (or `.csv`)
- **Or PostgreSQL:** Host=localhost, Database=sahel_dashboard, Table=beneficiaries

## Dashboard Pages

### Page 1: Overview
**Purpose:** Program-level summary for management and coordination meetings.

| Visual | Type | Fields |
|--------|------|--------|
| Total Beneficiaries | Card | COUNT of beneficiary_id |
| By Province | Donut chart | province, COUNT |
| By Sex | Donut chart | sex, COUNT |
| Monthly Trend | Line chart | month (X), COUNT (Y) |
| By Nutrition Status | Stacked bar | nutrition_status, COUNT, colored by status |
| Map | Filled map | province as location, COUNT as size |

**Filters:** Province slicer, Date range slicer, Intervention type slicer

### Page 2: Nutrition Analysis
**Purpose:** Clinical monitoring for nutrition coordinators.

| Visual | Type | Fields |
|--------|------|--------|
| MAM/MAS Rate | KPI | % of MAM + MAS vs total |
| MUAC Distribution | Histogram | muac_mm |
| Status by Age Group | Stacked bar | age_group (X), COUNT (Y), nutrition_status (legend) |
| Referral Rate | Gauge | % of MAS cases referred |
| Status Trend | Line chart | month (X), COUNT (Y), nutrition_status (legend) |
| Recovery Funnel | Funnel | follow_up_status stages |

### Page 3: Coverage vs Targets
**Purpose:** Program performance tracking for M&E and donors.

| Visual | Type | Fields |
|--------|------|--------|
| Coverage by Province | Clustered bar | province, actual COUNT vs MONTHLY_TARGETS |
| Monthly Coverage % | Line chart | month (X), coverage_pct (Y), by province |
| Sites Active | Card | COUNT DISTINCT collection_site |
| Underperforming Sites | Table | collection_site, province, COUNT, quality_score |

### Page 4: Data Quality
**Purpose:** IM Officer review before publishing data.

| Visual | Type | Fields |
|--------|------|--------|
| Avg Quality Score | Gauge | AVG of quality_score, target = 90 |
| Quality Distribution | Histogram | quality_score |
| Issues by Type | Bar chart | quality_flag categories, COUNT |
| Collector Performance | Table | data_collector, total_records, avg_quality, pct_missing |
| Missing Data Heatmap | Matrix | field names (rows) vs month (cols), missing count |

### Page 5: Donor Report
**Purpose:** Export-ready page for quarterly donor reporting.

| Visual | Type | Fields |
|--------|------|--------|
| Summary table | Matrix | Province (rows), Key indicators (cols): reached, MAM, MAS, referrals, coverage % |
| Trend chart | Combo chart | Month, beneficiaries reached (bars), MAM rate (line) |
| Key findings | Text box | Auto-populated narrative summary |

## DAX Measures to Create

```dax
// Total beneficiaries
Total Beneficiaries = COUNTROWS(beneficiaries)

// MAM Rate
MAM Rate = 
DIVIDE(
    CALCULATE(COUNTROWS(beneficiaries), beneficiaries[nutrition_status] = "MAM"),
    COUNTROWS(beneficiaries),
    0
)

// MAS Rate
MAS Rate = 
DIVIDE(
    CALCULATE(COUNTROWS(beneficiaries), beneficiaries[nutrition_status] = "MAS"),
    COUNTROWS(beneficiaries),
    0
)

// Referral Rate (MAS cases referred)
Referral Rate = 
DIVIDE(
    CALCULATE(COUNTROWS(beneficiaries), beneficiaries[nutrition_status] = "MAS", beneficiaries[referred] = TRUE()),
    CALCULATE(COUNTROWS(beneficiaries), beneficiaries[nutrition_status] = "MAS"),
    0
)

// Average Quality Score
Avg Quality = AVERAGE(beneficiaries[quality_score])

// Monthly target coverage (Lac example)
Coverage Lac = 
DIVIDE(
    CALCULATE(COUNTROWS(beneficiaries), beneficiaries[province] = "Lac"),
    200 * DISTINCTCOUNT(beneficiaries[month]),
    0
)
```

## Color Scheme

| Element | Color | Hex |
|---------|-------|-----|
| Normal status | Green | #27AE60 |
| MAM status | Orange | #F39C12 |
| MAS status | Red | #E74C3C |
| Lac province | Blue | #2980B9 |
| Kanem province | Teal | #16A085 |
| Batha province | Purple | #8E44AD |
| Background | Light gray | #F5F6FA |

## Export

The Donor Report page should be configured for PDF export (File > Export > PDF) with A4 landscape format.
