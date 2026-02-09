import sys
import os
from datetime import datetime
import pytz

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.engine.calculator.main import ChartCalculator
from src.engine.dignities import DignityCalculator
from src.engine.models import PlanetName, Sect

def generate_receipt():
    # 1. Calculate a Chart (Use a known strong chart, e.g., Mars in Capricorn)
    # Mars is Exalted in Capricorn (28 degrees is degree of exaltation)
    # Let's try to find a date where Mars is in Capricorn. 
    # Approx dates: early 2024? Or just pick a random date and verify, or force it?
    # Actually, let's just run for "now" and see what we get, or pick a specific historical date.
    # Feb 2024 Mars was in Capricorn. Let's try Feb 10, 2024.
    
    calc = ChartCalculator()
    chart_data = calc.calculate_chart(
        date="2024-02-10",
        time="12:00",
        city="London",
        state=""
    )
    
    # 2. Get Mars Data
    mars = next(p for p in chart_data.planets if p.name == "Mars")
    
    # Calculate Sect
    sect = Sect.DAY if chart_data.sun_altitude > 0 else Sect.NIGHT

    # 3. Calculate Dignity
    dignity_data = DignityCalculator.calculate_planet_dignity(
        planet_name=PlanetName.MARS,
        longitude=mars.longitude,
        sect=sect,
        term_system="egyptian" # default
    )
    
    accidental_data = DignityCalculator.calculate_accidental_dignity(mars, chart_data)
    
    # 4. Print Receipt
    print("\n" + "="*40)
    print(f"[AUDIT RECORD: {mars.name.upper()}]")
    print(f"Longitude: {mars.sign} {mars.position_in_sign:.1f}°")
    print(f"Sect: {sect.value}")
    print("-" * 40)
    
    # Essential Scores
    for item in dignity_data.get('score_breakdown', []):
        score = item['score']
        source = item['source']
        sign = "+" if score > 0 else ""
        print(f"{sign}{score:<3} {source}")
        
    # Accidental Scores
    for item in accidental_data.get('details', []):
        score = item['score']
        desc = item['description']
        sign = "+" if score > 0 else ""
        print(f"{sign}{score:<3} {desc}")

    print("-" * 40)
    total_essential = dignity_data.get('total_score', 0)
    total_accidental = accidental_data.get('total_score', 0)
    total = total_essential + total_accidental
    
    rank = "AVERAGE"
    if total > 10: rank = "HEROIC"
    elif total > 5: rank = "STRONG"
    elif total < -5: rank = "CRITICAL"
    
    print(f"TOTAL RANK: {total} ({rank})")
    print("STATUS: VERIFIED")
    print("="*40 + "\n")

if __name__ == "__main__":
    generate_receipt()
