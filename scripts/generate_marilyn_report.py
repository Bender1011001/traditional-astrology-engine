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

async def generate_marilyn():
    print("=== Generating Reports for Marilyn Monroe ===")
    
    # User Data
    chart_request = {
        "date": "1926-06-01",
        "time": "09:30",
        "city": "Los Angeles",
        "state": "California",
        "name": "Marilyn Monroe"
    }
    
    print(f"Data: {chart_request}")
    
    # 1. Generate Data
    print("Generating Chart Data (may take 10-20s)...")
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
    filename_cal = "Marilyn_Monroe_Calibration.pdf"
    with open(filename_cal, "wb") as f:
        f.write(pdf_cal.getvalue())
    print(f"✅ Required File Created: {filename_cal} ({size_cal} bytes)")
    
    # 3. Generate Full PDF
    print("\nGenerating FULL PDF...")
    gen_full = PDFReportGenerator(chart_data, tier="FULL")
    pdf_full = gen_full.generate()
    size_full = len(pdf_full.getvalue())
    filename_full = "Marilyn_Monroe_Full_Forensic.pdf"
    with open(filename_full, "wb") as f:
        f.write(pdf_full.getvalue())
    print(f"✅ Required File Created: {filename_full} ({size_full} bytes)")
    
    print("\n=== Generation Complete ===")
    print(f"Files are ready in: {os.getcwd()}")

if __name__ == "__main__":
    asyncio.run(generate_marilyn())
