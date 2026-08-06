"""Full 6-iteration Opus 4.8 natal report for 1996-08-23, rendered to PDF."""
import json
import os
import sys
import traceback

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "src"))

MODEL = os.environ.get("OPENROUTER_MODEL", "google/gemini-3.5-flash")
os.environ["OPENROUTER_MODEL"] = MODEL
TAG = os.environ.get("REPORT_TAG", "flash")

from src.engine.chat_oracle import _openrouter_request
from src.engine.pdf_generator import PDFReportGenerator
from src.scripts.generate_premium_report import (generate_chart_data,
                                                 run_premium_report)

NAME = "Native"
DATE, TIME, CITY, STATE = "1996-08-13", "07:18", "Fairfield", "CA"
LAT, LON = 38.2494, -122.0397
ITERS = int(os.environ.get("REPORT_ITERS", "6"))

print(f"Preflight: pinging {MODEL} ...")
ping = _openrouter_request(
    messages=[{"role": "user", "content": "Reply with the single word: OK"}],
    temperature=0.0, max_tokens=10,
)
print("Preflight:", repr(ping)[:200])
if not ping or ping.startswith("Error") or ping.startswith("Oracle"):
    print("PREFLIGHT FAILED — aborting.")
    sys.exit(2)

print(f"\nGenerating chart data for {DATE} {TIME} {CITY},{STATE} ...")
chart_str = generate_chart_data(NAME, DATE, TIME, CITY, STATE, latitude=LAT, longitude=LON)
if not chart_str:
    print("CHART GENERATION FAILED")
    sys.exit(1)

os.makedirs("premium_reports", exist_ok=True)
md_path = os.path.join("premium_reports", f"native_0813_{TAG}.md")
print(f"\nRunning full report ({ITERS} iterations, Opus 4.8) ...")
report_md = run_premium_report(chart_str, md_path, ITERS)
print(f"Markdown report: {md_path} ({len(report_md.split()):,} words)")

# Render to PDF
pdf_path = os.path.join("premium_reports", f"native_0813_{TAG}.pdf")
try:
    pdf_data = json.loads(chart_str)
    # Ensure the PDF title block can read birth meta.
    meta = pdf_data.get("meta", {})
    chart_meta = meta.get("chart", {}) or {}
    meta.setdefault("date", chart_meta.get("date", DATE))
    meta.setdefault("time", chart_meta.get("time", TIME))
    meta.setdefault("city", chart_meta.get("city", CITY))
    meta.setdefault("state", chart_meta.get("state", STATE))
    meta.setdefault("subject_name", NAME)
    pdf_data["meta"] = meta

    gen = PDFReportGenerator(pdf_data, tier="FULL")
    buf = gen.generate(custom_content=report_md)
    with open(pdf_path, "wb") as f:
        f.write(buf.getvalue())
    print(f"\nPDF: {pdf_path} ({os.path.getsize(pdf_path):,} bytes)")
except Exception as e:
    print(f"PDF RENDER FAILED: {e!r}")
    traceback.print_exc()
    print("(Markdown report is still available.)")

print("\nDONE")
