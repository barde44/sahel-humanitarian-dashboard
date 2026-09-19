# KoboToolbox Form — Nutrition Screening Survey

## How to use this form

1. Create a free account on [KoboToolbox](https://www.kobotoolbox.org/)
2. Go to **Projects > New > Import an XLSForm**
3. Upload the file `nutrition_survey_form.xlsx` from this folder
4. Deploy the form
5. Copy your **API Token** from Settings > Security
6. Copy the **Form UID** from the URL when viewing the form
7. Add both to your `.env` file

## Form Structure

The XLSForm has 3 sheets:

### survey sheet
| type | name | label |
|------|------|-------|
| start | start | |
| end | end | |
| today | today | |
| text | beneficiary_id | Beneficiary ID |
| text | first_name | First Name |
| text | last_name | Last Name |
| select_one sex | sex | Sex |
| integer | age_months | Age (months) |
| select_one province | province | Province |
| select_one department | department | Department |
| text | village | Village |
| select_one intervention | intervention_type | Intervention Type |
| select_one nutrition_status | nutrition_status | Nutrition Status |
| integer | muac_mm | MUAC (mm) |
| select_one followup | follow_up_status | Follow-up Status |
| select_one yesno | referred | Referred to SC? |
| text | caregiver_name | Caregiver Name |
| text | collection_site | Collection Site |

### choices sheet
Contains the option lists for sex, province, department, intervention types, nutrition status, follow-up status, and yes/no.

### settings sheet
| form_title | form_id |
|-----------|---------|
| Sahel Nutrition Screening | sahel_nutrition_v1 |

## API Access

Once deployed, extract data via the KoboToolbox API v2:

```bash
curl -X GET "https://kf.kobotoolbox.org/api/v2/assets/{FORM_UID}/data.json" \
  -H "Authorization: Token {YOUR_TOKEN}"
```

The `src/etl/extract.py` module handles this automatically when configured.

## Note

For this portfolio project, data is generated synthetically using `src/generate/synthetic_data.py`.
The KoboToolbox form is provided to demonstrate knowledge of the tool and the ability to
design data collection instruments — a key skill for humanitarian IM positions.
