import asyncio
import sys
import os
import json
from datetime import datetime

# Setup paths
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "src"))

# Force UTF-8 for Windows terminal
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.engine.logic import perform_forensic_audit
from src.engine.chart_calculator import calculate_chart_data
from src.engine.models import Chart, Planet, PlanetName, Sign

async def run_detailed_reading():
    date_str = "1996-08-13"
    time_str = "07:18"
    city = "Fairfield"
    state = "CA"
    
    # 1. Calculate Chart Data
    chart_data = calculate_chart_data(date_str=date_str, time_str=time_str, city=city, state=state)
    
    if "error" in chart_data:
        print(f"Error: {chart_data['error']}")
        return

    # 2. Reconstruct Chart Model properly
    planets_dict = chart_data["planets"]
    planet_objects = []
    sun_alt = 0.0
    for pname, pdata in planets_dict.items():
        try:
            p_enum = PlanetName(pname)
            p_obj = Planet(
                name=p_enum, 
                longitude=pdata["longitude"], 
                latitude=pdata.get("latitude", 0.0), 
                speed=pdata.get("speed", 0.0), 
                altitude=pdata.get("altitude", 0.0)
            )
            planet_objects.append(p_obj)
            if p_enum == PlanetName.SUN:
                sun_alt = pdata.get("altitude", 0.0)
        except ValueError:
            pass

    # FIXED: Ascendant and MC are in 'angles' key
    angles = chart_data.get("angles", {})
    houses_data = chart_data.get("houses", {})
    
    chart_model = Chart(
        sun_altitude=sun_alt, 
        planets=planet_objects, 
        ascendant=angles.get("Ascendant", 0.0), 
        mc=angles.get("MC", 0.0), 
        north_node=planets_dict.get("North_Node", {}).get("longitude", 0.0), 
        houses=houses_data, 
        jd=chart_data["meta"]["julian_day"], 
        geo_lat=chart_data["meta"]["lat"], 
        geo_lon=chart_data["meta"]["lon"]
    )
    
    # 3. Perform Universal Forensic Audit
    birth_dt = datetime(1996, 8, 13, 7, 18)
    # Target age 29 (current/upcoming)
    report = perform_forensic_audit(
        chart_model, 
        jd=chart_data["meta"]["julian_day"], 
        age=29, 
        birth_date=birth_dt,
        analysis_date=datetime.now()
    )
    
    # Print a truly MASSIVE dossier
    print("\n" + "#" * 90)
    print(" " * 20 + "UNIVERSAL FORENSIC DOSSIER: CODEX CAELESTIS")
    print(" " * 22 + f"NATIVITY: {date_str} {time_str} | FAIRFIELD, CA")
    print("#" * 90)

    # --- I. SUMMARY ---
    summary = report.get("summary", {})
    print(f"\n[SECTION I: CONSTITUTIONAL SUMMARY]")
    print(f"  Sect: {summary.get('sect')} | Lunar Phase: {summary.get('lunar_phase')}")
    print(f"  Temperament: {summary.get('temperament', {}).get('dominant_humor', 'N/A')}")
    print(f"  Jones Pattern: {summary.get('jones_pattern', 'N/A')}")
    print(f"  Natal Rooting: {summary.get('chart_strength_rating', {}).get('score', 0)}/100 ({summary.get('chart_strength_rating', {}).get('mood', 'N/A')})")

    # --- II. PLANETARY DISPOSITIONS (The Council) ---
    print(f"\n[SECTION II: THE PLANETARY COUNCIL (Forensic Condition)]")
    for p in report.get("planets", []):
        name = p.get("planet")
        sign = p.get("sign")
        house = p.get("house_number")
        score = p.get("dignity_score", 0)
        power = p.get("power_label", "Unknown")
        
        print(f"\n  >> {name} in {sign} (House {house}) | Power: {power} (Score: {score})")
        
        # Impacts (Dignity details, Aspects, Eclipses)
        for impact in p.get("impacts", []):
            print(f"     - {impact.get('cause')}: {impact.get('effect')}")
        
        # Delineation
        dtext = p.get("delineation_text", "")
        if dtext:
            print(f"     DELINEATION: {dtext}")

    # --- III. PREDICTIVE CHRONOCRATORS (Lords of Time) ---
    print(f"\n[SECTION III: TIME-LORD CHRONOLOGY (Age 29)]")
    pred = report.get("prediction", {})
    ap = pred.get("annual_profection", {})
    print(f"  Annual Profection: {ap.get('sign')} (Lord of Year: {ap.get('lord_of_year')})")
    
    # ZR
    if "zodiacal_releasing" in report:
        zr = report["zodiacal_releasing"].get("Spirit", {})
        print(f"  Zodiacal Releasing (Spirit): L1: {zr.get('L1', {}).get('sign')} | L2: {zr.get('L2', {}).get('sign')}")

    # --- IV. VITALITY & MEDICAL ---
    vit = report.get("vitality", {})
    print(f"\n[SECTION IV: VITALITY & MEDICAL ARCHITECTURE]")
    print(f"  Hyleg: {vit.get('hyleg')} | Alcocoden: {vit.get('alcocoden')}")
    print(f"  Magnitude: {vit.get('magnitude')} | Baseline Life Promise: {vit.get('years', 0):.1f} Years")
    
    med = report.get("medical_analysis", {})
    print(f"  Constitutional Focus: {med.get('constitutional_sign')} (Rules: {med.get('governed_body_part')})")
    print(f"  Physiological Bias: {med.get('distemper', {}).get('excess_humor')}")

    # --- V. PRIMARY DIRECTIONS & LOTS ---
    print(f"\n[SECTION V: PRIMARY DIRECTIONS & ARABIC LOTS]")
    for d in report.get("primary_directions", [])[:5]:
        print(f"  - {d.get('promittor')} {d.get('aspect')} {d.get('significator')} at Age {d.get('years')}")
    
    lots = report.get("lots", {})
    print(f"\n  Arabic Lots (Key Longitudes):")
    for lname, llon in lots.items():
        print(f"    - {lname:10}: {llon:.2f}°")

    print("\n" + "#" * 90)
    print(" " * 30 + "END OF MASTER DOSSIER")
    print("#" * 90 + "\n")

if __name__ == "__main__":
    asyncio.run(run_detailed_reading())
