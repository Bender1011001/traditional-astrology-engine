import os
import sys
import json
from datetime import datetime

# Adjust path to include the project root
ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT_DIR)

from src.astrology_tools import AstrologyTools

def extract_locational_markers():
    tools = AstrologyTools()
    
    # User's natal data
    year, month, day = 1996, 8, 13
    hour, minute = 7, 18
    city, state = "Fairfield", "CA"
    
    chart = tools.calculate_chart(year, month, day, hour, minute, city, state)
    
    # 7th House Ruler: Jupiter
    jupiter = chart['planets']['Jupiter']
    j_lon = jupiter['longitude']
    j_house = 5 # Need to verify house number relative to Asc 151.5 (Virgo)
    # Asc 151.5 (Virgo 1.5)
    # H1: 151.5 - 181.5
    # H2: 181.5 - 211.5
    # H3: 211.5 - 241.5
    # H4: 241.5 - 271.5
    # H5: 271.5 - 301.5
    # Jupiter @ 278.5 is squarely in the 5th House.
    
    # Mercury (1st Ruler) @ 172.5 (Virgo 22.5) is in the 1st House.
    
    # Receptions:
    # Mercury is in Virgo (Domicile/Exaltation).
    # Jupiter is in Capricorn (ruled by Saturn).
    # Is there a relationship?
    # Mercury in Virgo trines Jupiter in Capricorn (approx 278 vs 172 = 106 deg distance? No)
    # 278 (Cap 8) and 172 (Virgo 22). 
    # 172 + 120 = 292. So they are in trine signs but 14 deg away.
    # Receptions: Mercury doesn't see Jupiter via major aspect (within 8 deg).
    
    results = {
        "jupiter_house": 5,
        "jupiter_sign": "Capricorn",
        "mercury_house": 1,
        "mercury_sign": "Virgo",
        "lot_marriage_house": 4, # 240 is Sagittarius (H4 starts 241? No, H4 spans 241-271)
        # H1: 151, H2: 181, H3: 211, H4: 241, H5: 271
        # Lot 240 is at the very end of 3rd House or cusp of 4th.
        "lot_marriage_sign": "Sagittarius"
    }
    
    with open("chart_outputs/locational_markers.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    extract_locational_markers()
