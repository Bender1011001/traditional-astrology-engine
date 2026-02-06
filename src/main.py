import sys
import os

# Ensure src is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.models import Planet, PlanetName, Sign, Chart, Sect
from engine.logic import perform_forensic_audit
from engine.reference_data import PLANETARY_YEARS
from src.database.db_manager import DelineationLibrary

def setup_ultimate_verification_chart():
    # 1. SETUP ANGLES for Paran Trigger
    # Antares @ 250.1. Let's put ASC on Antares.
    asc = 250.1
    # Regulus @ 150.167. Let's put MC on Regulus.
    mc = 150.167
    
    # 2. THE MINISTERS
    # Sun in Libra (Fall) - Day Chart
    sun = Planet(PlanetName.SUN, longitude=190.0) 
    
    # Mars on ASC (250.1) to trigger Paran with Regulus on MC
    mars = Planet(PlanetName.MARS, longitude=250.1)
    
    # Saturn in CANCER (95 deg) to trigger specific Melothesia pathology
    saturn = Planet(PlanetName.SATURN, longitude=95.0)
    
    # Jupiter in its own TERM in Cancer
    # Cancer Terms: [("MARS", 7), ("VENUS", 13), ("MERCURY", 19), ("JUPITER", 26), ("SATURN", 30)]
    # Jupiter @ 25 Cancer (115.0 deg) -> Term ruler is JUPITER.
    jupiter = Planet(PlanetName.JUPITER, longitude=115.0) # 25 Cancer
    
    # Mercury at NODAL BENDING
    # North Node @ 150.0 (0 Virgo)
    # North Bending @ 240.0 (0 Sagittarius)
    # South Bending @ 60.0 (0 Gemini)
    mercury = Planet(PlanetName.MERCURY, longitude=240.0) # North Bending
    
    # Moon in Taurus (Exalted)
    moon = Planet(PlanetName.MOON, longitude=40.0)
    
    # Venus in Libra (Domicile)
    venus = Planet(PlanetName.VENUS, longitude=200.0)
    
    planets = [sun, moon, mercury, venus, mars, jupiter, saturn]
    
    return Chart(sun_altitude=20.0, planets=planets, ascendant=asc, mc=mc, north_node=150.0)

def generate_report(chart: Chart, age: int):
    print("=== CODEX CAELESTIS: UNIVERSAL CAUSATION AUDIT ===\n")
    print("FINAL VERIFIED REPORT\n")
    
    audit = perform_forensic_audit(chart, age=age)
    summary = audit["summary"]
    
    print(f"SECT: {summary['sect']} | CONSTRUCTIVE: {', '.join(summary['constructive_team'])}")
    print(f"DESTRUCTIVE: {', '.join(summary['destructive_team'])}")
    print(f"LUNAR PHASE: {summary['lunar_phase']} | PATTERN: {summary['jones_pattern']}")
    print("-" * 50)
    
    # 1. The Lots
    print("SECTION 1: THE HERMETIC LOTS (Geometric Fate)")
    for name, val in audit["lots"].items():
        sign_idx = int(val / 30) % 12
        sign_name = list(Sign)[sign_idx].value
        deg = val % 30
        print(f"  Lot of {name:<10}: {sign_name:<10} @ {deg:.2f}°")
    print("-" * 50)
    
    # 2. Key Witnesses (Stars & Nodes)
    print("SECTION 2: THE CELESTIAL CURIA (Stars & Nodes)")
    if audit["stars"]:
        for s in audit["stars"]:
            star_name = s.star_name if hasattr(s, 'star_name') else s['star_name']
            planet_name = s.planet_name if hasattr(s, 'planet_name') else s['planet_name']
            message = s.message if hasattr(s, 'message') else s['message']
            print(f"  [STELLATUM] {planet_name} + {star_name}: {message}")
    else:
        print("  No major Royal Star conjunctions detected.")
        
    if audit["nodes"]:
        for n in audit["nodes"]:
            p_name = n.planet_name if hasattr(n, 'planet_name') else n['planet_name']
            n_type = n.node_type if hasattr(n, 'node_type') else n['node_type']
            desc = n.description if hasattr(n, 'description') else n['description']
            print(f"  [DRACONIC]  {p_name} ({n_type}): {desc}")
    else:
        print("  No Nodal contacts.")
    print("-" * 50)
        
    # 3. The Ministers (Planets)
    print("SECTION 3: CONDITION OF THE MINISTERS (Planetary Forensic)")
    
    for p in audit["planets"]:
        if p["planet"] == "Sun": continue
        
        print(f"PLANET: {p['planet'].upper()}")
        print(f"  Loc: {p['sign']} @ {p['longitude']%30:.2f}°")
        print(f"  Status: {p['sect_status']} | Power: {p['power_label']} ({p['dignity_score']})")
        print(f"  Solar: {p['solar_status']}")
        
        # Alcocoden Years
        p_name = next((name for name in PlanetName if name.value == p['planet']), None)
        if p_name in PLANETARY_YEARS:
            years = PLANETARY_YEARS[p_name]
            print(f"  Alcocoden Years: Lesser {years['lesser']}, Mean {years['mean']}, Greater {years['greater']}")

        # Impacts
        for impact in p['impacts']:
            print(f"  ! {impact['cause']}: {impact['effect']}")
            
        # Dignity Details
        if p['dignity_details']:
            print(f"  Dignities: {', '.join(p['dignity_details'])}")
            
        # DB Text
        print(f"  TEXT: {p['delineation_text']}")
        print(f"  HOUSE {p['house_number']}: {p['house_delineation_text']}")
        print("")
        
    print("-" * 50)
    # 4. Profections
    if "prediction" in audit:
        pred = audit["prediction"]
        print(f"SECTION 4: CHRONOCRATOR (Age {pred['age']})")
        print(f"  Annual Profection: {pred['annual_profection']['sign']} (Lord: {pred['annual_profection']['lord_of_year']})")
        print(f"  Monthly (Cont):    {pred['monthly_profection']['continuous']}")
        print(f"  Monthly (Salt):    {pred['monthly_profection']['saltatory']}")
        print(f"  Daily Sign:        {pred['daily_profection']['sign']}")
        if pred['epitasis_days']:
            print(f"  EPITASIS TRIGGERS: {', '.join(map(str, pred['epitasis_days']))}")
    print("==================================================")

if __name__ == "__main__":
    chart = setup_ultimate_verification_chart()
    generate_report(chart, 32)
