import asyncio
import sys
import os
import logging

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Configure logging
logging.basicConfig(level=logging.INFO)

from src.services.engine_bridge import generate_full_nativity_async
from src.engine.pdf_generator import PDFReportGenerator

async def compare_reports():
    print("=== Comparing Report Tiers ===")
    
    # Mock Data
    chart_request = {
        "date": "1990-01-01",
        "time": "12:00",
        "city": "London",
        "state": "",
        "name": "Test Native"
    }
    
    # 1. Generate Data (Once)
    print("Generating Chart Data...")
    chart_data = await generate_full_nativity_async(
        date_str=chart_request.get("date"),
        time_str=chart_request.get("time"),
        city=chart_request.get("city"),
        state=chart_request.get("state"),
        name=chart_request.get("name"),
        house_system="P",
        zodiac_system="T",
        ayanamsa="0"
    )
    
    if "error" in chart_data:
        print(f"Error: {chart_data['error']}")
        return

    # 2. Generate Calibration PDF
    print("\nGenerating CALIBRATION PDF...")
    gen_cal = PDFReportGenerator(chart_data, tier="CALIBRATION")
    pdf_cal = gen_cal.generate()
    size_cal = len(pdf_cal.getvalue())
    with open("report_calibration.pdf", "wb") as f:
        f.write(pdf_cal.getvalue())
    print(f"✅ Calibration PDF Created: {size_cal} bytes")
    
    # 3. Generate Full PDF
    print("\nGenerating FULL PDF...")
    gen_full = PDFReportGenerator(chart_data, tier="FULL")
    pdf_full = gen_full.generate()
    size_full = len(pdf_full.getvalue())
    with open("report_full.pdf", "wb") as f:
        f.write(pdf_full.getvalue())
    print(f"✅ Full PDF Created: {size_full} bytes")
    
    # 4. Compare
    diff = size_full - size_cal
    percent = (diff / size_full) * 100
    print(f"\nResult: Full report is {diff} bytes larger ({percent:.1f}%) than Calibration.")
    
    if size_cal < size_full:
        print("✅ PASS: Calibration report is significantly smaller (short version confirmed).")
    else:
        print("❌ FAIL: Reports are same size or Calibration is larger.")

if __name__ == "__main__":
    asyncio.run(compare_reports())
