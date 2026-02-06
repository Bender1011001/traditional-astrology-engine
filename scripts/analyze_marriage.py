import os
import sys
import json
from datetime import datetime

# Adjust path to include the project root
ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT_DIR)

from src.astrology_tools import AstrologyTools

def analyze_marriage():
    tools = AstrologyTools()
    
    # User's natal data
    year, month, day = 1996, 8, 13
    hour, minute = 7, 18
    city, state = "Fairfield", "CA"
    
    print(f"Analyzing marriage for: {year}-{month}-{day} {hour}:{minute} {city}, {state}")
    
    # Get full chart data
    chart = tools.calculate_chart(year, month, day, hour, minute, city, state)
    
    # Extract specific points
    planets = chart['planets']
    houses = chart['houses']
    asc = chart['angles']['Ascendant']
    
    # 7th House (Partnership)
    h7_cusp = houses.get(7) or houses.get('7')
    h7_idx = int(h7_cusp / 30) % 12
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    h7_sign = signs[h7_idx]
    
    # significators
    venus = planets['Venus']
    jupiter = planets['Jupiter']
    sun = planets['Sun']
    moon = planets['Moon']
    
    # Lot of Marriage (Men: Asc + Venus - Saturn) / (Women: Asc + Saturn - Venus)
    # Manual check: Sun in Leo is Day.
    saturn_lon = planets['Saturn']['longitude']
    venus_lon = venus['longitude']
    
    # Generic Greek Lot of Marriage: Asc + Desc - Venus? No, usually gender specific.
    # Let's use the standard "Men" formula for male-identifying users or general partnership lot.
    lot_marriage = (asc + venus_lon - saturn_lon) % 360
    lot_sign = signs[int(lot_marriage / 30) % 12]
    
    results = {
        "h7_cusp": h7_cusp,
        "h7_sign": h7_sign,
        "ruler": "Jupiter" if h7_sign in ["Pisces", "Sagittarius"] else "Other",
        "jupiter_condition": jupiter.get('classical', {}),
        "venus_condition": venus.get('classical', {}),
        "lot_marriage": lot_marriage,
        "lot_sign": lot_sign,
        "receptions": chart.get('receptions', {})
    }
    
    print(f"7th House: {h7_sign} @ {h7_cusp}")
    print(f"Lot of Marriage: {lot_sign} @ {lot_marriage}")
    
    with open("chart_outputs/natal_marriage_analysis.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    analyze_marriage()
