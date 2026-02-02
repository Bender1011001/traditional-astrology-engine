import json
import os
from src.engine.sovereign_engine import SovereignEngine

def generate_report():
    print("Generating chart for 1996-08-13 07:18 Fairfield, CA...")
    
    # 1. Calculate
    result = SovereignEngine.generate_full_nativity(
        date_str="1996-08-13",
        time_str="07:18",
        city="Fairfield, CA",
        state="CA",
        house_system="W",
        zodiac_system="tropical"
    )

    if "error" in result:
        print(f"Error: {result['error']}")
        return

    # 2. Extract Data
    technical_data = result.get("technical_data", {})
    human_translation = result.get("human_translation", {})
    report_markdown = human_translation.get("report_markdown", "# No Report Generated")

    # 3. Save JSON
    output_dir = os.path.join(os.getcwd(), "chart_outputs")
    os.makedirs(output_dir, exist_ok=True)
    
    json_path = os.path.join(output_dir, "native_1996_08_13.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=str, ensure_ascii=False)
    print(f"Saved JSON data to: {json_path}")

    # 4. Save Markdown
    md_path = os.path.join(output_dir, "native_1996_08_13_report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report_markdown)
    print(f"Saved Markdown report to: {md_path}")

if __name__ == "__main__":
    generate_report()
