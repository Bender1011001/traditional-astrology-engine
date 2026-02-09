---
description: Create a $197-tier Premium Forensic Astrological Report
---

# Generate Premium Forensic Report

This workflow triggers the "Gold Standard" deep-dive analysis (approx. 7,500 words) used for high-value orders. It involves a 6-iteration LLM synthesis of the forensic structural audit.

## Prerequisites

- [ ] Birth Name
- [ ] Birth Date (YYYY-MM-DD)
- [ ] Birth Time (HH:MM)
- [ ] City & State/Country

## Steps

### 1. Run the Forensic Engine
Execute the premium generation script. This will perform calculations and run the multi-pass LLM chain.

// turbo
```bash
python src/scripts/generate_premium_report.py --name "Subject Name" --date "YYYY-MM-DD" --time "HH:MM" --city "City Name" --state "State/Country"
```

> [!NOTE]
> This process takes 3-5 minutes as it performs 6 sequential LLM calls to build a cohesive narrative.

### 2. Convert to PDF
Once the Markdown file is generated in `premium_reports/`, run the conversion script to produce the client-ready PDF.

// turbo
```bash
python scripts/convert_md_to_pdf.py
```

> [!TIP]
> This script automatically finds the most recently generated Markdown file in the `premium_reports/` directory.

### 3. Verification
Review the final PDF in the `premium_reports/` folder.
- Check word count (target: 6,000 - 8,500).
- Ensure "Mermaid" diagram raw code is suppressed (handled automatically by `PDFReportGenerator`).
- Verify specific remediation suggestions are present in the final part.
