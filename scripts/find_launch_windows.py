import os
import sys
import json
from datetime import datetime

# Adjust path to include the project root
ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT_DIR)

from src.astrology_tools import AstrologyTools

def find_launch_windows():
    tools = AstrologyTools()
    
    print("=== ELECTIONAL SEARCH: ASTROLOGY WEBSITE LAUNCH ===")
    print("Activity: Mercantile (Business/Commerce)")
    print("Scanning: Next 336 hours (2 weeks)")
    print()
    
    # Scan for mercantile activity (business launch)
    results = tools.find_electional_window(
        city="Fairfield", 
        state="CA", 
        activity="mercantile", 
        hours_to_scan=336  # 2 weeks
    )
    
    # Save raw results
    with open("chart_outputs/website_launch_windows.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Generate formatted report with natal context
    natal_context = {
        "almuten": "Mercury in Virgo (Exalted)",
        "time_lord": "Mercury Major → Venus Sub-Period (Oct 2025 - Aug 2027)",
        "recommendations": [
            "Launch during Mercury Sub-Period for maximum alignment",
            "Prioritize daytime launches (Diurnal Sect)",
            "Ensure Mercury is visible and not combust",
            "Look for Venus in angular houses for public appeal"
        ]
    }
    
    report = tools.format_electional_report(results, natal_context)
    
    with open("chart_outputs/website_launch_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("✓ Scan complete")
    print(f"✓ Found {len(results.get('best_windows', []))} windows")
    print("✓ Saved to chart_outputs/website_launch_report.md")

if __name__ == "__main__":
    find_launch_windows()
