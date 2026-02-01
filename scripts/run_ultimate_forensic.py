import asyncio
import sys
import os
import json
from datetime import datetime, timedelta

# Setup paths
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "src"))

from src.engine.logic import perform_forensic_audit
from src.engine.chart_calculator import calculate_chart_data
from src.engine.models import Chart, Planet, PlanetName, Sign, Sect, LotName
from src.engine.advanced_mechanics import DoryphoryEngine, MonomoiriaEngine, AlmutenEngine, HermeticLotEngine
from src.engine.prediction import calculate_firdaria, calculate_zr_lifetime_map, calculate_zr_periods, FIRDARIA_DAY, FIRDARIA_NIGHT
from src.engine.mansions import LunarMansionEngine
from src.engine.rectification import RectificationEngine
from src.engine.kakosis import KakosisEngine
from src.database.db_manager import DelineationLibrary

async def run_ultimate_reading():
    date_str = "1996-08-13"
    time_str = "07:18"
    city = "Fairfield"
    state = "CA"
    
    # 1. Calculate Chart Data
    chart_data = calculate_chart_data(date_str=date_str, time_str=time_str, city=city, state=state)
    
    if "error" in chart_data:
        print(f"Error: {chart_data['error']}")
        return

    # 2. Reconstruct Chart Model
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
    
    # 3. Traditional Logic Audit
    birth_dt = datetime(1996, 8, 13, 7, 18)
    report = perform_forensic_audit(
        chart_model, 
        jd=chart_data["meta"]["julian_day"], 
        age=29, 
        birth_date=birth_dt,
        analysis_date=datetime.now()
    )
    
    lib = DelineationLibrary()
    sect = Sect.DAY if sun_alt > 0 else Sect.NIGHT

    # --- ULTIMATE REPORT BUFFER ---
    output = []
    output.append("#" * 100)
    output.append(" " * 30 + "CODEX CAELESTIS: THE ULTIMATE FORENSIC DOSSIER")
    output.append(" " * 32 + f"NATIVITY: {date_str} {time_str} | FAIRFIELD, CA")
    output.append("#" * 100)

    # I. CONSTITUTIONAL PROTOCOL
    summary = report.get("summary", {})
    output.append(f"\n[SECTION I: CONSTITUTIONAL PROTOCOL]")
    output.append(f"  Chart Sect  : {summary.get('sect')}")
    output.append(f"  Lunar Phase : {summary.get('lunar_phase')} ({summary.get('lunar_phase_profile')})")
    output.append(f"  Jones Pattern: {summary.get('jones_pattern')}")
    output.append(f"  Total Rooting: {summary.get('chart_strength_rating', {}).get('score')}/100")
    
    temp = report.get("temperament", {})
    output.append(f"  Humoral Bias: {temp.get('dominant_humor', 'N/A')} ({temp.get('temperament_type', 'N/A')})")

    # Rectification Animodar
    animodar_list = RectificationEngine.animodar_rectification(chart_model, chart_model.jd, chart_model.geo_lat, chart_model.geo_lon)
    if animodar_list:
        res = animodar_list[0]
        output.append(f"  Rectification (Animodar): {res.get('difference', 'N/A')} deg diff via {res.get('rectifying_planet')}")
    
    # II. PLANETARY FORENSICS (THE ENTIRE COUNCIL)
    output.append(f"\n[SECTION II: THE PLANETARY COUNCIL - EXHAUSTIVE CONDITION]")
    for p in report.get("planets", []):
        name = p.get("planet")
        lon = p.get("longitude", 0.0)
        sign = p.get("sign")
        house = p.get("house_number")
        
        # Monomoiria (Lord of Degree)
        mon = MonomoiriaEngine.get_zoidion_monomoiria(lon)
        
        output.append(f"\n  >> {name.upper()} in {sign} ({lon:.2f}°) | House {house}")
        output.append(f"     Monomoiria (Lord of the Degree): {mon.value}")
        output.append(f"     Condition Status: {p.get('power_label')} (Weighted Index: {p.get('performance_index')})")
        
        # Kakosis (Maltreatment)
        maltreatments = KakosisEngine.check_maltreatments(next(obj for obj in chart_model.planets if obj.name.value == name), chart_model)
        if maltreatments:
            output.append(f"     KAKOSIS (Maltreatment) AUDIT:")
            for m in maltreatments:
                output.append(f"       ! {m.type}: {m.description} (Severity: {m.severity}/10)")
        
        # All Impacts
        for impact in p.get("impacts", []):
            output.append(f"     - {impact.get('cause')}: {impact.get('effect')}")
        
        # Essential Dignity Details
        for detail in p.get("dignity_details", []):
             output.append(f"     + Dignity: {detail}")
        
        # Delineations
        output.append(f"     NATAL PROMISE: {p.get('delineation_text')}")
        output.append(f"     HOUSE PURPOSE: {p.get('house_delineation_text')}")

    # III. THE ADVANCED MECHANICS (THE ENGINE DEPTH)
    output.append(f"\n[SECTION III: ADVANCED MECHANICS & HIDDEN LAYERS]")
    
    # Almuten Figuris
    almuten = AlmutenEngine.calculate_almuten(chart_model)
    san_lon, san_type = AlmutenEngine.calculate_prenatal_syzygy(chart_model.jd)
    output.append(f"  Almuten Figuris (The Guardian): {almuten.winner.value}")
    output.append(f"  Prenatal Syzygy (SAN): {san_lon:.2f}° ({san_type})")
    
    # Doryphory (Bodyguards)
    dory = DoryphoryEngine.check_doryphory(chart_model)
    output.append(f"  Doryphory Audit (Planetary Bodyguards):")
    for d in dory:
        output.append(f"    - {d.planet.value} is a {d.type} to the {d.related_luminary}")
    
    # Mundane Context (The World History)
    mund_context = report.get("advanced_mechanics", {}).get("mundane_context", [])
    output.append(f"  Mundane Hierarchy (The Era of Birth):")
    
    # Get Rank 2 (Great Conjunction)
    gc_entry = next((e for e in mund_context if e.get("rank") == 2), {})
    gc = gc_entry.get("data", {})
    if gc:
        # Note: Great Conjunction in mundane.py returns sign as string or sign value
        sign_val = gc.get('sign')
        output.append(f"    - GREAT CONJUNCTION: {gc.get('description')} in {sign_val}")
    
    # Get Rank 4 (Aries Ingress)
    ingress_entry = next((e for e in mund_context if e.get("rank") == 4), {})
    ing = ingress_entry.get("data", {})
    if ing:
        output.append(f"    - WORLD ENTRANCE: {ing.get('description')} (Sun at 0° Aries)")

    # IV. LORDS OF TIME (THE PREDICTIVE MATRIX)
    output.append(f"\n[SECTION IV: THE PREDICTIVE MATRIX (CHRONOCRATORS)]")
    
    # Firdaria Table (75 years)
    output.append(f"\n  FIRDARIA SEQUENCE (Ages 0 - 75):")
    f_seq = FIRDARIA_DAY if sect == Sect.DAY else FIRDARIA_NIGHT
    current_age = 0
    for p_name, duration in f_seq:
        output.append(f"    - Age {current_age:2} to {current_age+duration:2}: Period of {p_name.value}")
        current_age += duration

    # Zodiacal Releasing (Spirit)
    spirit_lon = report["lots"].get("Spirit")
    if spirit_lon is not None:
        spirit_sign = list(Sign)[int(spirit_lon / 30) % 12]
        zr_map = calculate_zr_lifetime_map(spirit_sign, birth_dt)
        output.append(f"\n  ZODIACAL RELEASING - MAJOR PERIODS (L1):")
        for period in zr_map[:8]: # Next ~8 periods
            output.append(f"    - {period['start_date']} | {period['sign']:12} ({period['duration_years']} years)")

    # V. ARABIC LOTS & STELLAR CONTACTS
    output.append(f"\n[SECTION V: ARABIC LOTS & STELLAR SIGNATURES]")
    lots = report.get("lots", {})
    for lname, llon in lots.items():
        lsign = list(Sign)[int(llon / 30) % 12]
        output.append(f"  - {lname:10}: {llon:6.2f}° in {lsign.value}")
        
    stars = report.get("stars", [])
    output.append(f"\n  Fixed Star Intersections:")
    for s in stars:
        output.append(f"    - {s.star_name} ({s.contact_type}) on {s.planet_name}: {s.message}")

    # Iatromathematics section update
    med = report.get("medical_analysis", {})
    output.append(f"\n[SECTION VI: IATROMATHEMATICAL PROTOCOL (MEDICAL)]")
    
    # Lunar Mansion
    moon_lon = next(p.longitude for p in chart_model.planets if p.name == PlanetName.MOON)
    mansion = LunarMansionEngine.get_lunar_mansion(moon_lon)
    output.append(f"  Current Lunar Mansion: {mansion.get('mansion_id')} ({mansion.get('name')})")
    output.append(f"  Picatrix Intents (Good): {', '.join(mansion.get('intents_good', []))}")
    output.append(f"  Picatrix Intents (Bad) : {', '.join(mansion.get('intents_bad', []))}")
    
    output.append(f"  Constitutional Mastery: {med.get('constitutional_sign')} rules the {med.get('governed_body_part')}")
    output.append(f"  Humoral Excess: {med.get('distemper', {}).get('excess_humor')}")
    output.append(f"  Palliative Care: {med.get('distemper', {}).get('palliative_nature')}")
    
    # Critical Days
    output.append(f"\n  Critical Decumbiture Thresholds (Lunar Phases from Onset):")
    for d in report.get("critical_days_infancy", []):
        output.append(f"    - {d.get('date')} : {d.get('phase')} (Critical Day {d.get('day_number')})")

    # VII. THE TEMPORAL FORECAST
    output.append(f"\n[SECTION VII: THE TEMPORAL FORECAST (NEXT 5 DAYS)]")
    for f in report.get("forecast_5_day", []):
        output.append(f"  {f.get('display_date')} | Chronocrator: {f.get('chronocrator')}")
        output.append(f"    - Mood: {f.get('mood')} | Status: {f.get('summary')}")
        if f.get("medical"):
            for m in f.get("medical"):
                output.append(f"    ! Medical Alert: {m}")

    output.append("\n" + "#" * 100)
    output.append(" " * 38 + "END OF ULTIMATE FORENSIC DOSSIER")
    output.append("#" * 100 + "\n")

    # WRITE TO FINAL FILE
    with open("final_god_mode_dossier.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))
    
    print(f"Ultimate Dossier generated: final_god_mode_dossier.txt ({len(output)} lines)")

if __name__ == "__main__":
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    asyncio.run(run_ultimate_reading())
