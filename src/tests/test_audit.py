
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from engine.models import Chart, Planet, PlanetName, Sect
from engine.logic import perform_forensic_audit

def test_audit():
    # Mock Data
    planets = [
        Planet(PlanetName.SUN, 30.5, 0, 1), # Taurus
        Planet(PlanetName.MOON, 150.0, 0, 13), # Virgo
        Planet(PlanetName.MERCURY, 40.0, 0, 1.2), # Taurus
        Planet(PlanetName.VENUS, 60.0, 0, 1.1), # Gemini
        Planet(PlanetName.MARS, 200.0, 0, 0.5), # Libra
        Planet(PlanetName.SATURN, 5.0, 0, 0.1), # Aries
        Planet(PlanetName.JUPITER, 95.0, 0, 0.1), # Cancer
    ]
    # Ascendant in Aries (0-30). Let's say 10 deg -> Aries.
    chart = Chart(
        sun_altitude=10.0, # Day
        planets=planets,
        ascendant=10.0
    )
    
    # 2023-10-27 JD is approx 2460244.5
    report = perform_forensic_audit(chart, jd=2460244.5)
    
    print("Forensic Report:")
    for p in report["planets"]:
        print(f"Planet: {p['planet']}")
        print(f"  Dignity: {p['dignity_score']} ({', '.join(p['dignity_details'])})")
        print(f"  Solar: {p['solar_status']}")
        if p["impacts"]:
            print(f"  IMPACTS: {p['impacts']}")
        print(f"  Sign Text: {p['delineation_text'][:50]}...")
        print(f"  House: {p['house_number']}")
        print(f"  House Text: {p['house_delineation_text'][:50]}...")
        print("-" * 20)
    
    if "soul_guardian" in report:
        sg = report["soul_guardian"]
        print("\nTHE SOUL'S GUARDIAN (ALMUTEN FIGURIS):")
        print(f"  Guardian: {sg['almuten']}")
        print(f"  Job Description: {sg['job_description']}")
        print(f"  Total Score: {sg['total_score']}")
        
    if "summary" in report:
        s = report["summary"]
        print("\nTEAMS:")
        print(f"  Constructive: {', '.join(s['constructive_team'])}")
        print(f"  Destructive: {', '.join(s['destructive_team'])}")
        print(f"  Note: {s['team_note']}")

if __name__ == "__main__":
    test_audit()
