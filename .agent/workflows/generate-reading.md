---
description: How to generate a comprehensive astrological reading
---

# Generate Comprehensive Reading

This workflow generates a standard "God Mode" astrological report. For the $197 Forensic Audit, use `/generate-premium`.

## 1. Prepare Data
Gather the subject's Name, Date (YYYY-MM-DD), Time (HH:MM), and Location.

## 2. Run Generation
Execute the calculation and synthesis script.

// turbo
```bash
python scripts/generate_reading.py "YYYY-MM-DD" "HH:MM" "City Name" --state "State" --name "Subject Name"
```

## 3. Retrieve Output
Check the `chart_outputs/` directory for:
- `[Name]_[Timestamp]_report.md`: The readable analysis.
- `[Name]_[Timestamp].json`: The technical calculation data.
