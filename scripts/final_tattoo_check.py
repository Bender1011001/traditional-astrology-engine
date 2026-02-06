import os
import sys
import json
from datetime import datetime

# Adjust path to include the project root
ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT_DIR)

from src.astrology_tools import AstrologyTools

def final_tattoo_check():
    tools = AstrologyTools()
    
    # Target 1: The "Power Window" - Feb 7, 02:00 AM (Leo Rising?)
    dt1 = datetime(2026, 2, 7, 2, 0)
    chart1 = tools.calculate_chart(2026, 2, 7, 2, 0, "Fairfield", "CA")
    
    # Target 2: The "Beauty Window" - Feb 11, 01:00 AM (Venus Focus)
    dt2 = datetime(2026, 2, 11, 1, 0)
    chart2 = tools.calculate_chart(2026, 2, 11, 1, 0, "Fairfield", "CA")
    
    with open("chart_outputs/tattoo_final_options.json", "w") as f:
        json.dump({"power_window": chart1, "beauty_window": chart2}, f, indent=2)

if __name__ == "__main__":
    final_tattoo_check()
