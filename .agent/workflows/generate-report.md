---
description: How to generate a practitioner-grade astrological report
---

# Generate Practitioner Report

Use this workflow to generate a professional-grade report including technical JSON data and a narrative Markdown reading.

## 1. Commands

// turbo
```bash
python src/scripts/generate_practitioner_report.py --name "Native Name" --date "YYYY-MM-DD" --time "HH:MM" --city "City Name"
```

## 2. Advanced Options

- `--house_system`: Use `W` (Whole Sign), `P` (Placidus), `K` (Koch), etc. (Default: W)
- `--ayanamsa`: Optional ayanamsa for sidereal calculations (e.g., `lahiri`, `fagan_bradley`).
- `--output_dir`: Directory to save the reports.

## 3. Outputs
The script saves two files:
1. `*_technical_chart.json`: Raw engine data.
2. `*_reading_report.md`: Professional human-readable narrative.
