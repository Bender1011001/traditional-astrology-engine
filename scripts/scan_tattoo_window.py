import os
import sys
import json
from datetime import datetime, timedelta

# Adjust path to include the project root
ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT_DIR)

from src.astrology_tools import AstrologyTools

def find_tattoo_window():
    tools = AstrologyTools()
    
    print("=== ELECTIONAL SEARCH: TALISMANIC TATTOO ===")
    
    # 1. Scan for 'art' (Venus)
    print("Scanning for 'art' (Venus focus)...")
    art_results = tools.find_electional_window(
        city="Fairfield", state="CA", activity="art", hours_to_scan=168
    )
    
    # 2. Scan for 'surgery' (Mars safety)
    print("Scanning for 'surgery' (Mars safety focus)...")
    surgery_results = tools.find_electional_window(
        city="Fairfield", state="CA", activity="surgery", hours_to_scan=168
    )
    
    # Save both for analysis
    with open("chart_outputs/tattoo_art_scan.json", "w") as f:
        json.dump(art_results, f, indent=2)
    with open("chart_outputs/tattoo_surgery_scan.json", "w") as f:
        json.dump(surgery_results, f, indent=2)
        
    print("Scans complete. Data saved.")

if __name__ == "__main__":
    find_tattoo_window()
