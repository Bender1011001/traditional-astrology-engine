from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.services.html_report_renderer import (
    capture_report_screenshot,
    export_pdf_with_playwright,
    load_json,
    load_text,
    render_html_report,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render the print-first HTML astrology report template from chart JSON and premium Markdown."
    )
    parser.add_argument("--chart-data", required=True, help="Path to engine chart_data.json")
    parser.add_argument("--markdown", required=True, help="Path to premium report Markdown")
    parser.add_argument("--output-dir", required=True, help="Directory for rendered artifacts")
    parser.add_argument("--basename", default="astrology_report", help="Output filename stem")
    parser.add_argument("--title", default="Classical Nativity Report", help="Report title")
    parser.add_argument("--pdf", action="store_true", help="Export a PDF with Playwright Chromium")
    parser.add_argument("--screenshot", action="store_true", help="Capture the first page as PNG")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    chart_data = load_json(args.chart_data)
    markdown = load_text(args.markdown)

    html_path = render_html_report(
        chart_data,
        markdown,
        output_dir,
        basename=args.basename,
        title=args.title,
    )
    print(f"HTML: {html_path}")

    if args.pdf:
        pdf_path = output_dir / f"{args.basename}.pdf"
        export_pdf_with_playwright(html_path, pdf_path)
        print(f"PDF: {pdf_path}")

    if args.screenshot:
        image_path = output_dir / f"{args.basename}-page1.png"
        capture_report_screenshot(html_path, image_path)
        print(f"Screenshot: {image_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
