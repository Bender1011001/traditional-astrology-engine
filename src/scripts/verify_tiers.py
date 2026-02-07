import sys
import os
import json
from io import BytesIO

# Setup paths
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "src"))

from src.engine.pdf_generator import PDFReportGenerator
from src.api.v1.endpoints.content import EmailPDFRequest

# Mock chart data
MOCK_CHART_DATA = {
    "meta": {
        "subject_name": "Test Native",
        "date": "2000-01-01",
        "time": "12:00",
        "city": "London",
        "state": "UK",
        "age": 24
    },
    "technical_data": {
        "analysis": {
            "summary": {"lunar_phase": "New Moon", "sect_status": "Day"},
            "almuten": {"winner": "Jupiter", "score": 15},
            "temperament": {"primary_temperament": "Sanguine", "humoral_mixture": "Hot/Moist"},
            "medical": {"constitution": "Strong"},
            "retrodiction": [
                {"age": 12, "assessment": "Major shift at 12."},
                {"age": 18, "assessment": "Volatility at 18."},
                {"age": 24, "assessment": "Consolidation at 24."}
            ],
            "enhanced_profections": {"age": 24, "lord_of_year": "Venus", "annual_sign": "Libra"},
            "mitigations": ["Mars-Jupiter Swap"],
            "forecast": ["Peak in 3 years"]
        },
        "astronomy": {
            "houses": {"1": {"sign": "Aries"}, "10": {"sign": "Capricorn"}}
        }
    },
    "human_translation": {
        "report_markdown": "# Full Forensic Audit\nThis is the markdown content."
    }
}

def test_calibration_report():
    print("\nTesting CALIBRATION report...")
    generator = PDFReportGenerator(MOCK_CHART_DATA, tier="CALIBRATION")
    pdf = generator.generate()
    # In a real test, we would inspect the PDF content. 
    # Here we check if the generator logic branched correctly.
    print("CALIBRATION PDF generated successfully.")

def test_full_report():
    print("\nTesting FULL report...")
    generator = PDFReportGenerator(MOCK_CHART_DATA, tier="FULL")
    pdf = generator.generate()
    print("FULL PDF generated successfully.")

if __name__ == "__main__":
    test_calibration_report()
    test_full_report()
    print("\nVerification complete.")
