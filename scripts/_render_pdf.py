"""Render an existing report markdown into a PDF (no LLM). Args: DATE MD_PATH OUT_PATH."""
import os
import sys

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "src"))
from src.engine.pdf_generator import PDFReportGenerator
from src.scripts.generate_premium_report import generate_chart_data_object

date, md_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
data = generate_chart_data_object("Native", date, "07:18", "Fairfield", "CA", latitude=38.2494, longitude=-122.0397)
report = open(md_path, encoding="utf-8").read()

meta = data.get("meta", {})
cm = meta.get("chart", {}) or {}
meta.setdefault("date", cm.get("date", date))
meta.setdefault("time", cm.get("time", "07:18"))
meta.setdefault("city", "Fairfield")
meta.setdefault("state", "CA")
meta.setdefault("subject_name", "Native")
data["meta"] = meta

gen = PDFReportGenerator(data, tier="FULL")
buf = gen.generate(custom_content=report)
with open(out_path, "wb") as f:
    f.write(buf.getvalue())
print(f"PDF OK: {out_path} ({os.path.getsize(out_path):,} bytes)")
