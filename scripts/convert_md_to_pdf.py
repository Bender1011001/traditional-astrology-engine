
import sys
import os

# Ad-hoc path fix
project_root = r"e:\code.projects\astrology"
sys.path.append(os.path.join(project_root, 'src'))

from engine.pdf_generator import PDFReportGenerator
from io import BytesIO

# MOCK DATA for Marilyn (required by PDF Generator)
chart_data = {
    "meta": {
        "subject_name": "Marilyn Monroe",
        "date": "1926-06-01",
        "time": "09:30",
        "city": "Los Angeles",
        "state": "CA",
        "age": 36 # rough guess for profections
    },
    "technical_data": {
        "astronomy": {
            "planets": {"Sun": {"altitude": 10}}, # Day sect
             "houses": {str(i): {"sign": "Aries"} for i in range(1,13)}
        }
    },
    "forensic_report": {
        "summary": {"lunar_phase": "Disseminating", "sect_status": "Day"},
        "almuten": {"winner": "Venus", "score": 42},
        "temperament": {"primary_temperament": "Sanguine", "humoral_mixture": "Hot/Moist"},
        "medical": {"constitution": "Resilient"},
        "enhanced_profections": {"lord_of_year": "Mars", "annual_sign": "Scorpio"}
    }
}

def convert_md_to_pdf(md_filename):
    print(f"Reading {md_filename}...")
    with open(md_filename, "r", encoding="utf-8") as f:
        md_content = f.read()

    print("Generating PDF...")
    gen = PDFReportGenerator(chart_data, tier="FULL")
    pdf_buffer = gen.generate(custom_content=md_content)
    
    output_filename = md_filename.replace(".md", ".pdf")
    with open(output_filename, "wb") as f:
        f.write(pdf_buffer.getvalue())
        
    print(f"SUCCESS: Created {output_filename}")

if __name__ == "__main__":
    import glob
    
    # Find the most recent markdown file in premium_reports
    report_dir = r"e:\code.projects\astrology\premium_reports"
    list_of_files = glob.glob(os.path.join(report_dir, "*.md"))
    
    if not list_of_files:
        print("No markdown reports found in", report_dir)
        sys.exit(1)
        
    latest_file = max(list_of_files, key=os.path.getctime)
    print(f"Targeting latest report: {latest_file}")
    
    # Update chart data to match the file (Rough Mocking for PDF metadata)
    # in a real world, we'd parse the YAML frontmatter or JSON
    if "1955" in latest_file or "steve" in latest_file.lower():
         chart_data["meta"]["subject_name"] = "Steven Jobs (Steve)"
         chart_data["meta"]["date"] = "1955-02-24"
         chart_data["meta"]["time"] = "19:15"
         chart_data["meta"]["city"] = "San Francisco"
    
    elif "nixon" in latest_file.lower() or "1913" in latest_file:
         chart_data["meta"]["subject_name"] = "Richard Nixon"
         chart_data["meta"]["date"] = "1913-01-09"
         chart_data["meta"]["time"] = "21:35"
         chart_data["meta"]["city"] = "Yorba Linda"
    
    elif "frida" in latest_file.lower() or "kahlo" in latest_file.lower() or "1907" in latest_file:
         chart_data["meta"]["subject_name"] = "Frida Kahlo"
         chart_data["meta"]["date"] = "1907-07-06"
         chart_data["meta"]["time"] = "08:30"
         chart_data["meta"]["city"] = "Coyoacán"

    elif "1996" in latest_file:
         chart_data["meta"]["subject_name"] = "Subject (1996)"
         chart_data["meta"]["date"] = "1996-08-13"
         chart_data["meta"]["time"] = "07:18"
         chart_data["meta"]["time"] = "07:18"
         chart_data["meta"]["city"] = "Fairfield, CA"

    elif "elon" in latest_file.lower() or "musk" in latest_file.lower():
         chart_data["meta"]["subject_name"] = "Elon Musk"
         chart_data["meta"]["date"] = "1971-06-28"
         chart_data["meta"]["time"] = "07:30"
         chart_data["meta"]["city"] = "Pretoria"
         chart_data["meta"]["state"] = "South Africa"

    convert_md_to_pdf(latest_file)
