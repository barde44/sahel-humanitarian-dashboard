# Data Dictionary — Sahel Humanitarian Response Dashboard

## Table: beneficiaries

| Field | Type | Description | Source |
|-------|------|-------------|--------|
| beneficiary_id | VARCHAR(20) | Unique identifier (format: BEN-XXXXXXXX) | Generated at registration |
| first_name | VARCHAR(100) | Beneficiary first name | KoboToolbox form |
| last_name | VARCHAR(100) | Beneficiary family name | KoboToolbox form |
| sex | CHAR(1) | M = Male, F = Female | KoboToolbox form |
| age_months | INTEGER | Age in months (program targets 6-59) | KoboToolbox form |
| age_group | VARCHAR(10) | Derived age bracket (6-11m, 12-23m, etc.) | Computed from age_months |
| caregiver_name | VARCHAR(200) | Name of child's caregiver (usually mother) | KoboToolbox form |
| province | VARCHAR(50) | Chad province: Lac, Kanem, or Batha | KoboToolbox form (GPS or selection) |
| department | VARCHAR(100) | Administrative department within province | KoboToolbox form |
| village | VARCHAR(100) | Village or locality name | KoboToolbox form |
| submission_date | DATE | Date data was collected in the field | KoboToolbox metadata |
| month | VARCHAR(7) | Year-month period (e.g. 2026-03) | Derived from submission_date |
| year | INTEGER | Year of submission | Derived from submission_date |
| intervention_type | VARCHAR(50) | Program intervention type (see below) | KoboToolbox form |
| nutrition_status | VARCHAR(10) | Normal, MAM, or MAS | KoboToolbox form |
| muac_mm | FLOAT | Mid-Upper Arm Circumference in millimeters | KoboToolbox form |
| muac_status | VARCHAR(10) | Status derived from MUAC measurement | Computed: <115=MAS, 115-125=MAM, >=125=Normal |
| follow_up_status | VARCHAR(20) | New, Follow-up_1, Follow-up_2, Discharged | KoboToolbox form |
| referred | BOOLEAN | Whether child was referred to stabilization center | KoboToolbox form |
| data_collector | VARCHAR(50) | ID of the field agent who collected the data | KoboToolbox metadata |
| collection_site | VARCHAR(100) | CSI (health center) or Mobile (outreach) | KoboToolbox form |
| quality_score | INTEGER | Data quality score 0-100 per record | Computed during transform |
| quality_flag | TEXT | Description of quality issues found | Computed during transform |

## Intervention Types

| Code | Description |
|------|-------------|
| CMAM_OTP | Community-based Management of Acute Malnutrition — Outpatient Therapeutic Program |
| CMAM_SC | Community-based Management of Acute Malnutrition — Stabilization Center |
| BSFP | Blanket Supplementary Feeding Programme |
| IYCF_Counseling | Infant and Young Child Feeding Counseling |
| Screening | Nutrition screening (no treatment, assessment only) |

## Nutrition Status (MUAC-based)

| Status | MUAC Range | Action |
|--------|-----------|--------|
| MAS (Severe Acute Malnutrition) | < 115 mm | Referral to stabilization center |
| MAM (Moderate Acute Malnutrition) | 115-124 mm | Supplementary feeding program |
| Normal | >= 125 mm | Preventive counseling |

## Geographic Hierarchy

```
Chad (country)
├── Lac (province)
│   ├── Bol (department)
│   ├── Mamdi
│   └── Wayi
├── Kanem (province)
│   ├── Kanem
│   ├── Nord Kanem
│   └── Wadi Bissam
└── Batha (province)
    ├── Batha Ouest
    ├── Batha Est
    └── Fitri
```
