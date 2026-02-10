#!/usr/bin/env python3
import os
import sys
import json
from datetime import datetime

# Setup paths
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "src"))

from src.engine.pdf_generator import PDFReportGenerator

def find_latest_report(directory="premium_reports", extension=".md"):
    if not os.path.exists(directory):
        return None
    files = [f for f in os.listdir(directory) if f.endswith(extension)]
    if not files:
        return None
    files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)
    return os.path.join(directory, files[0])

def convert_md_to_pdf(md_path):
    print(f"Converting: {md_path}")
    
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # We need some basic chart data for the generator, though it mostly uses custom_content for MD
    # In a real scenario, we might want to load the corresponding .json, but for now we mock the metadata
    chart_data = {
        "meta": {
            "name": "User Client Premium",
            "date": "1996-08-13",
            "time": "07:18",
            "city": "Fairfield",
            "state": "CA",
            "tier": "FULL"
        }
    }
    
    generator = PDFReportGenerator(chart_data, tier="FULL")
    pdf_buffer = generator.generate(custom_content=md_content)
    
    pdf_path = md_path.replace(".md", ".pdf")
    with open(pdf_path, 'wb') as f:
        f.write(pdf_buffer.getbuffer())
    
    print(f"✓ PDF Saved: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    latest_md = find_latest_report()
    if latest_md:
        convert_md_to_pdf(latest_md)
    else:
        print("No report found to convert.")
