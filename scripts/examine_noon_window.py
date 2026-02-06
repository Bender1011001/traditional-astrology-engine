import os
import sys
import json
from datetime import datetime

# Adjust path to include the project root
ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT_DIR)

from src.astrology_tools import AstrologyTools

def examine_noon_window():
    tools = AstrologyTools()
    
    # Target moment: Friday Feb 6, 11:55 AM PST
    dt = datetime(2026, 2, 6, 11, 55)
    print(f"Checking Strategic Window: {dt}")
    
    chart = tools.calculate_chart(2026, 2, 6, 11, 55, "Fairfield", "CA")
    
    with open("chart_outputs/strategic_launch_validation.json", "w") as f:
        json.dump(chart, f, indent=2)
    
    # Extraction
    planets = chart['planets']
    mc = chart['angles']['MC']
    asc = chart['angles']['Ascendant']
    
    merc_lon = planets['Mercury']['longitude']
    sat_lon = planets['Saturn']['longitude']
    
    print(f"Ascendant: {asc:.2f}")
    print(f"Midheaven (MC): {mc:.2f}")
    print(f"Mercury: {merc_lon:.2f}")
    print(f"Saturn: {sat_lon:.2f}")
    print(f"Mercury-MC Distance: {abs(merc_lon - mc):.2f} degrees")
    print(f"Mercury-Saturn Distance: {abs(merc_lon - sat_lon):.2f} degrees")

if __name__ == "__main__":
    examine_noon_window()
