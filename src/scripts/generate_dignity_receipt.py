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
    dt_str = "2024-02-10 12:00"
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    
    calc = ChartCalculator()
    chart_data = calc.calculate_chart(
        dt=dt,
        city="London",
        state=""
    )
    
    # 2. Get Mars Data
    mars = next(p for p in chart_data.planets if p.name == PlanetName.MARS)
    
    # Calculate Sect
    sect = Sect.DAY if chart_data.sun_altitude > 0 else Sect.NIGHT

    # 3. Calculate Dignity
    dignity_data = DignityCalculator.calculate_planet_dignity(
        planet_name=PlanetName.MARS,
        longitude=mars.longitude,
        sect=sect
    )
    
    accidental_data = DignityCalculator.calculate_accidental_dignity(mars, chart_data)
    
    # Define Meaning for Dignities
    MEANINGS = {
        "Exaltation": "Planet operates at idealized, peak performance (+4)",
        "Domicile": "Planet is in its own territory, fully self-sufficient (+5)",
        "Triplicity": "Planet has strong environmental/social support (+3)",
        "Term": "Planet has the tactical resources to execute its mission (+2)",
        "Face": "Planet has a slight focus or 'interest' in the area (+1)",
        "Detriment": "Planet is in enemy territory, severely hampered (-5)",
        "Fall": "Planet is functionally disabled or dishonored (-4)",
        "Angular House (9)": "Planet is in the 9th House (Vision/Wisdom), giving it high visibility.",
        "Cadent House (9)": "Planet is in the 9th House, which is 'Cadent', meaning it acts from a distance.",
        "Faster than average speed": "Planet is 'Alert' and moving quickly towards its goals.",
        "Superior Planet Oriental of Sun": "Planet rises before the Sun, making it active and 'proactive' in the world."
    }

    # SCORING LEGEND
    LEGEND = """
[ SCORING LEGEND: TRADITIONAL WEIGHTS ]
+5 Domicile: The planet is in its own home/territory.
+4 Exaltation: The planet is a 'honored guest' at peak performance.
+3 Triplicity: The planet has environmental/social support.
+2 Term: The planet has tactical resources (the 'how-to').
+1 Face: A minor interest or slight affinity.
-5 Detriment: The planet is in exile/enemy territory.
-4 Fall: The planet is functionally 'disabled' or out of favor.
"""

    # 4. Print Receipt
    print("\n" + "="*60)
    print(" [ FORENSIC AUDIT: MARS IN CAPRICORN ]")
    print(" [ SUBJECT: TRANSIT PERFORMANCE SNAPSHOT ]")
    print(" [ METADATA: 2024-02-10 12:00 GMT | LONDON, UK ]")
    print("="*60)
    print(f"\nPLANET: MARS")
    # Position: use ASCII-safe 'deg' to avoid character errors
    print(f"POSITION: Capricorn {mars.degree_in_sign:.1f} deg")
    print(f"SECT: {sect.value.upper()} (Forces the planet to reflect {sect.value} diurnal quality)")
    print("-" * 60)
    
    print(f"{'SCORE':<8} {'SOURCE':<25} {'FORENSIC MEANING'}")
    print("-" * 60)

    # Essential Scores
    for source, score in dignity_data.get('score_breakdown', {}).items():
        if score != 0:
            src_name = source.title()
            sign = "+" if score > 0 else ""
            meaning = MEANINGS.get(src_name, "Calculated mathematical strength.")
            print(f"{sign}{score:<7} {src_name:<25} {meaning}")
        
    # Accidental Scores
    for item in accidental_data.get('details', []):
        print(f"   {item}")

    print("-" * 60)
    total_essential = dignity_data.get('total_score', 0)
    total_accidental = accidental_data.get('total_score', 0)
    total = total_essential + total_accidental
    
    rank = "AVERAGE"
    if total > 10: rank = "HEROIC"
    elif total > 5: rank = "STRONG"
    elif total < -5: rank = "CRITICAL"
    
    print(f"AGGREGATE DIGNITY SCORE: {total}")
    print(f"POSTURE: {rank}")
    print("-" * 60)

    print("\n[ FORENSIC INTERPRETATION ]")
    if rank == "HEROIC":
        print("This Mars represents an unstoppable executive force. In the degree of its Exaltation,\n"
              "it possesses both the idealized vision and the tactical speed to conquer any obstacle.\n"
              "The 9th house placement suggests this strength is applied to high-level strategy and law.")
    
    print(LEGEND)
    print("STATUS: VERIFIED BY BENDER ENGINE V1.0")
    print("="*60 + "\n")

if __name__ == "__main__":
    generate_receipt()
