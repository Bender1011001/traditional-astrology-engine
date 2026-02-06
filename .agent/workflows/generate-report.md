---
description: How to generate a practitioner-grade astrological report
---

To generate a professional-grade report (Technical JSON + Markdown Reading), use the following script:

### Basic Command
```bash
python src/scripts/generate_practitioner_report.py --name "Native Name" --date "YYYY-MM-DD" --time "HH:MM" --city "City Name"
```

### Advanced Options
- `--house_system`: Use `W` (Whole Sign), `P` (Placidus), `K` (Koch), etc. (Default: W)
- `--ayanamsa`: Optional ayanamsa for sidereal calculations (e.g., `lahiri`, `fagan_bradley`).
- `--output_dir`: Directory to save the reports.

### Example
```bash
python src/scripts/generate_practitioner_report.py --name "Alexander Hamilton" --date "1755-01-11" --time "12:00" --city "Charlestown" --house_system "P"
```

The script will output two files in the specified directory:
1. `*_technical_chart.json`: The raw technical data for engine consumption.
2. `*_reading_report.md`: The professional, human-readable narrative.
