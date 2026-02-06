import os
import sys
import json
from datetime import datetime

# Adjust path to include the project root
ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT_DIR)

from src.astrology_tools import AstrologyTools

def examine_launch_moment():
    tools = AstrologyTools()
    
    # Target moment
    dt = datetime(2026, 2, 6, 2, 11)
    print(f"Checking Launch Moment: {dt}")
    
    chart = tools.calculate_chart(2026, 2, 6, 2, 11, "Fairfield", "CA")
    
    with open("chart_outputs/launch_moment_validation.json", "w") as f:
        json.dump(chart, f, indent=2)
    
    # Basic summary to stdout for quick check
    planets = chart['planets']
    sun_lon = planets['Sun']['longitude']
    merc_lon = planets['Mercury']['longitude']
    diff = abs(sun_lon - merc_lon)
    
    print(f"Sun Longitude: {sun_lon}")
    print(f"Mercury Longitude: {merc_lon}")
    print(f"Mercury Proximity: {diff:.2f} degrees")
    
    if diff < 0.28:
        print("✓ CAZIMI: Mercury is in the Heart of the Sun!")
    elif diff < 8.0:
        print("⚠ COMBUST: Mercury is under the beams (use caution).")
    else:
        print("✓ FREE: Mercury is clear of the Sun.")

if __name__ == "__main__":
    examine_launch_moment()
