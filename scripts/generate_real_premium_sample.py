
import asyncio
import logging
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.premium_generator import PremiumGenerator
from src.engine.pdf_generator import PDFReportGenerator
from src.services.engine_bridge import generate_full_nativity_async

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_sample():
    print("--- GENERATING REAL PREMIUM SAMPLE (MARILYN MONROE) ---")
    print("Note: This makes REAL API calls to OpenRouter/Gemini.")
    
    # 1. Define Subject (Marilyn Monroe)
    request = {
        "date": "1926-06-01",
        "time": "09:30",
        "city": "Los Angeles",
        "state": "CA",
        "name": "Marilyn Monroe"
    }
    
    # 2. Calculate Data
    print("1. Calculating Astrological Data...")
    chart_data = await generate_full_nativity_async(
        date_str=request["date"],
        time_str=request["time"],
        city=request["city"],
        state=request["state"],
        name=request["name"],
        house_system="W", # Whole Sign
        zodiac_system="T",
        ayanamsa="0"
    )
    
    if "error" in chart_data:
        print(f"Error calculating chart: {chart_data['error']}")
        return

    # 3. Generate AI Content (The $190 Value)
    print("2. Generating AI Forensic Dossier (This takes ~60-90 seconds)...")
    # We use the PremiumGenerator directly
    try:
        # We'll use the default 6 iterations
        ai_markdown = PremiumGenerator.generate_premium_report_markdown(chart_data)
        print(f"   > AI Content Generated: {len(ai_markdown)} characters.")
    except Exception as e:
        print(f"   > AI Generation Failed: {e}")
        return

    # 4. Render PDF
    print("3. Rendering PDF...")
    generator = PDFReportGenerator(chart_data, tier="FULL")
    pdf_buffer = generator.generate(custom_content=ai_markdown)
    
    # 5. Save to Disk
    filename = "Marilyn_Monroe_PREMIUM_REAL.pdf"
    with open(filename, "wb") as f:
        f.write(pdf_buffer.getvalue())
        
    print(f"\nSUCCESS: generated '{filename}'")
    print("size: {:.2f} KB".format(len(pdf_buffer.getvalue()) / 1024))
    print("--- PROCESS COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(generate_sample())
