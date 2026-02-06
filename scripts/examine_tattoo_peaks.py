import os
import sys
import json
from datetime import datetime

# Adjust path to include the project root
ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT_DIR)

from src.astrology_tools import AstrologyTools

def examine_peak_windows():
    tools = AstrologyTools()
    
    # Window 1: Tonight (Cazimi)
    dt1 = datetime(2026, 2, 5, 2, 0)
    print(f"Checking Window 1: {dt1}")
    chart1 = tools.calculate_chart(2026, 2, 5, 2, 0, "Fairfield", "CA")
    
    # Window 2: Next Week (Peak Art)
    dt2 = datetime(2026, 2, 11, 5, 0)
    print(f"Checking Window 2: {dt2}")
    chart2 = tools.calculate_chart(2026, 2, 11, 5, 0, "Fairfield", "CA")
    
    with open("chart_outputs/tattoo_peak_comparison.json", "w") as f:
        json.dump({"window1": chart1, "window2": chart2}, f, indent=2)

if __name__ == "__main__":
    examine_peak_windows()
