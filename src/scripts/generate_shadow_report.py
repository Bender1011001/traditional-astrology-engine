import sys
import os
import pytz

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.engine.calculator.main import ChartCalculator
from src.engine.dignities import DignityCalculator
from src.engine.models import PlanetName, Sect
from src.engine.classical_mechanics import ClassicalMechanicsEngine

def generate_shadow_report():
    # Target: A chart where a planet is weak but saved by hidden factors.
    # 2022-09-05: Venus in Virgo. Jupiter in Aries.
    date = "2022-09-05"
    time = "12:00"
    
    calc = ChartCalculator()
    chart = calc.calculate_chart(date, time, "London", "")
    
    venus = next(p for p in chart.planets if p.name == PlanetName.VENUS)
    jupiter = next(p for p in chart.planets if p.name == PlanetName.JUPITER)
    
    # 1. Surface Analysis
    sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
    pd = DignityCalculator.calculate_planet_dignity(
        PlanetName.VENUS, 
        venus.longitude, 
        sect
    )
    score = pd['total_score']
    status = "Weak"
    if score < -2: status = "CRITICAL (FALL)"
    
    print("\n" + "="*60)
    print(" [FORENSIC DEEP DIVE: SHADOW ARCHITECTURE]")
    print("="*60)
    
    print(f"\n[SURFACE ANALYSIS]")
    print(f"Target: VENUS in {venus.sign.value} ({venus.position_in_sign:.2f}°)")
    print(f"Essential Dignity Score: {score}")
    print(f"Condition: {status}")
    print("Standard Judgment: Relational difficulty, scarcity.")

    print(f"\n[SCANNING HIDDEN MECHANICS...]")
    
    # 2. Dodecatemoria
    # Venus at ~1 Virgo (0-1 deg?) No, let's check exact position.
    dodec = ClassicalMechanicsEngine.get_dodecatemorion(venus.longitude)
    print(f"> DETECTED: Dodecatemoria in {dodec.sign.value}")
    
    # 3. Antiscia
    # Check if Venus receives any antiscia/contra-antiscia from Jupiter
    shadow_aspects = ClassicalMechanicsEngine.check_shadow_aspects(chart.planets)
    
    # Look for Venus-Jupiter connections
    v_jup_connection = None
    for aspect in shadow_aspects:
        if (aspect['planet_1'] == "Venus" and aspect['planet_2'] == "Jupiter") or \
           (aspect['planet_1'] == "Jupiter" and aspect['planet_2'] == "Venus"):
            v_jup_connection = aspect
            break
            
    if v_jup_connection:
        print(f"> DETECTED: {v_jup_connection['type']} from {v_jup_connection['planet_2']} (Orb: {v_jup_connection['orb']}°)")
        print(f"> MITIGATION: YES. {v_jup_connection['quality']}.")
    else:
        # Fallback if specific date doesn't work, manual calc for demo
        # Venus at ~2 Virgo (152). Antiscia = 180-152 = 28 (28 Aries).
        # Jupiter at ~6 Aries. No hit.
        # Let's just print the Dodec result for now as proof.
        print("> ADVISORY: No strict Antiscia aspect found in this specific chart.")
    
    print("\n[FINAL JUDGMENT]")
    if dodec.sign.value in ["Taurus", "Libra", "Pisces"]:
         print(f"Dodecatemoria in {dodec.sign.value} (Dignified) overrides surface weakness.")
         print("Conclusion: Hidden resources found despite surface scarcity.")
    else:
         print("Conclusion: Condition remains severe.")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    generate_shadow_report()
