import os
import sys
import json
from datetime import datetime

# Adjust path to include the project root
ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT_DIR)

from src.astrology_tools import AstrologyTools

def analyze_children():
    tools = AstrologyTools()
    
    # User's natal data
    year, month, day = 1996, 8, 13
    hour, minute = 7, 18
    city, state = "Fairfield", "CA"
    
    print(f"Analyzing children for: {year}-{month}-{day} {hour}:{minute} {city}, {state}")
    
    # Get full chart data
    chart = tools.calculate_chart(year, month, day, hour, minute, city, state)
    
    # Extract specific points
    planets = chart['planets']
    houses = chart['houses']
    
    # 5th House
    h5_cusp = houses.get(5) or houses.get('5')
    
    # Lot of Children (Greek/Hellenistic formula)
    sun_alt = planets['Sun']['altitude']
    is_day = sun_alt > 0
    
    asc = chart['angles']['Ascendant']
    saturn = planets['Saturn']['longitude']
    jupiter = planets['Jupiter']['longitude']
    
    if is_day:
        lot_children = (asc + saturn - jupiter) % 360
    else:
        lot_children = (asc + jupiter - saturn) % 360
    
    print(f"Is Day Birth: {is_day}")
    print(f"Ascendant: {asc}")
    print(f"Saturn: {saturn}")
    print(f"Jupiter: {jupiter}")
    print(f"Lot of Children: {lot_children}")
    print(f"5th House Cusp: {h5_cusp}")
    
    # Logic for finding 5th house sign
    signs = ["Aires", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    h5_sign = signs[int(h5_cusp / 30) % 12]
    lot_sign = signs[int(lot_children / 30) % 12]
    
    # Save results
    with open("chart_outputs/natal_children_analysis.json", "w") as f:
        json.dump({
            "is_day": is_day,
            "asc": asc,
            "saturn": saturn,
            "jupiter": jupiter,
            "lot_children": lot_children,
            "lot_sign": lot_sign,
            "h5_cusp": h5_cusp,
            "h5_sign": h5_sign,
            "jupiter_condition": planets['Jupiter'].get('classical', {}),
            "saturn_condition": planets['Saturn'].get('classical', {})
        }, f, indent=2)

if __name__ == "__main__":
    analyze_children()
