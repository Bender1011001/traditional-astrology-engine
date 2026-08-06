"""Render a reading markdown file to PDF, with Unicode (Cyrillic/Greek) support.

The standard fulfilment path renders PDFs from the composer's markdown using
ReportLab's built-in Type1 fonts, which cannot display anything outside
Latin-1. This wrapper registers Unicode TrueType faces first, so translated
reports typeset correctly.

Usage:
    python scripts/render_report_pdf.py <report.md> <out.pdf> \
        --date 1987-02-01 --time 02:00 --city Kostanay --state "Kostanay Region"

The chart arguments are needed because the PDF cover draws a real chart wheel
from the chart data, not from the prose.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engine.fonts import ensure_unicode_fonts  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("markdown")
    ap.add_argument("output")
    ap.add_argument("--name", default="Guest")
    ap.add_argument("--date", required=True)
    ap.add_argument("--time", required=True)
    ap.add_argument("--city", required=True)
    ap.add_argument("--state", default="")
    ap.add_argument("--lat", type=float, default=None)
    ap.add_argument("--lon", type=float, default=None)
    args = ap.parse_args()

    unicode_ok = ensure_unicode_fonts()
    print(f"unicode fonts registered: {unicode_ok}")
    if not unicode_ok:
        print(
            "WARNING: no Unicode serif font found. Non-Latin text will not render.",
            file=sys.stderr,
        )

    # Import AFTER font registration so the stylesheet picks up the overrides.
    from src.engine.pdf_generator import PDFReportGenerator
    from src.scripts.generate_premium_report import generate_chart_data

    body = open(args.markdown, encoding="utf-8").read()
    chart = json.loads(
        generate_chart_data(
            name=args.name,
            date_str=args.date,
            time_str=args.time,
            city=args.city,
            state=args.state,
            latitude=args.lat,
            longitude=args.lon,
        )
    )

    buf = PDFReportGenerator(chart, tier="FULL").generate(custom_content=body)
    data = buf.getvalue()
    with open(args.output, "wb") as fh:
        fh.write(data)

    pages = len(re.findall(rb"/Type /Page[^s]", data))
    print(f"wrote {args.output}: {len(data):,} bytes, {pages} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
