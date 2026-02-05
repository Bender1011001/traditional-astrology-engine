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
from src.engine.kakosis import KakosisEngine
from src.engine.dignities import DignityCalculator
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
    
    cs_rating = summary.get('chart_strength_rating', {})
    output.append(f"  Chart Mood  : {cs_rating.get('mood')} - {cs_rating.get('details')[0] if cs_rating.get('details') else 'Stable'}")
    
    hemi = summary.get('hemispheres', {})
    h_focus = summary.get('hemisphere_focus', {})
    output.append(f"  Hemispheres : E({hemi.get('East')}) W({hemi.get('West')}) S({hemi.get('South')}) N({hemi.get('North')})")
    output.append(f"  Soul Focus  : {h_focus.get('orientation')} | {h_focus.get('visibility')}")
    
    temp = report.get("summary", {}).get("temperament", {})
    output.append(f"  Humoral Bias: {temp.get('primary_temperament', 'N/A')}")


    # SECTION I.B: VITALITY & LONGEVITY (The Medieval Core)
    vit = report.get("vitality", {})
    if vit:
        output.append(f"\n[SECTION I.B: VITALITY & THE GIVER OF YEARS]")
        output.append(f"  Hyleg (Giver of Life)  : {vit.get('hyleg')}")
        output.append(f"  Alcocoden (Giver of Yrs): {vit.get('alcocoden')} ({vit.get('base_years_type')} Scale)")
        output.append(f"  Theoretical Lifespan  : {vit.get('total_years'):.1f} years")
        output.append(f"  Vitality Status       : {vit.get('vitality_rating')}")
        output.append(f"  Forensic Breakdown     :")
        for log in vit.get("breakdown", []):
            output.append(f"    - {log}")
    
    # II. PLANETARY FORENSICS (THE ENTIRE COUNCIL)
    output.append(f"\n[SECTION II: THE PLANETARY COUNCIL - EXHAUSTIVE CONDITION]")
    for p in report.get("planets", []):
        name = p.get("planet")
        lon = p.get("longitude", 0.0)
        sign = p.get("sign")
        house = p.get("house_number")
        
        # Monomoiria (Lord of Degree)
        mon_data = p.get("classical", {}).get("monomoiria", {})
        zoidion = mon_data.get("zoidion_ruler", "N/A")
        trigonal = mon_data.get("trigonal_ruler", "N/A")
        
        output.append(f"\n  >> {name.upper()} in {sign} ({lon:.2f}°) | House {house}")
        output.append(f"     Monomoiria (Zoidion): {zoidion} | (Trigonal): {trigonal}")

        # Dodecatemoria (Hidden Geometry)
        dod_data = p.get("classical", {}).get("dodecatemoria", {})
        if dod_data:
            valens = dod_data.get("valens", {})
            paul = dod_data.get("paul", {})
            output.append(f"     Dodecatemoria (Valens): {valens.get('longitude', 0):.2f}° {valens.get('sign')} (Ruler: {valens.get('ruler')})")
            output.append(f"     Dodecatemoria (Paul)  : {paul.get('longitude', 0):.2f}° {paul.get('sign')}")
        
        # Hayz/Halb
        planet_obj = next((obj for obj in chart_model.planets if obj.name.value == name), None)
        if planet_obj:
             hayz_res = DignityCalculator.check_hayz_halb(planet_obj.name, planet_obj.longitude, chart_model)
             output.append(f"     Temporal Nature: {hayz_res.get('status')} ({hayz_res.get('details')[0] if hayz_res.get('details') else 'N/A'})")

        # Mundane Speculum (The 'Physics' of the placement)
        spec = p.get("speculum", {})
        if spec:
            output.append(f"     Mundane Speculum: House Pos {p.get('mundane_house_pos', 0.0):.2f} | Pole {spec.get('pole', 0.0):.2f}° | RA {spec.get('ra', 0.0):.2f}°")

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
    
    # Soul Guardian (Almuten Figuris)
    sg = report.get("soul_guardian", {})
    if sg:
        output.append(f"  ALMUTEN FIGURIS   : {sg.get('almuten')} (Term Ruler: {sg.get('term_ruler')})")
        output.append(f"  SOUL JOB DESC.    : {sg.get('job_description')}")

    # Almuten Scoreboard
    al_data = report.get("advanced_mechanics", {}).get("almuten", {})
    if al_data:
        output.append(f"  DIGNITY SCOREBOARD:")
        for p_al, score_al in al_data.get("scores", {}).items():
            output.append(f"    - {p_al:8}: {score_al.get('total'):2}")

    from src.engine.calculations import calculate_prenatal_syzygy
    san_lon, san_type = calculate_prenatal_syzygy(chart_model.jd)
    output.append(f"  Prenatal Syzygy   : {san_lon:.2f}° ({san_type})")
    
    # Doryphory (Bodyguards)
    dory = DoryphoryEngine.check_doryphory(chart_model)
    output.append(f"  Doryphory Audit (Planetary Bodyguards):")
    for d in dory:
        output.append(f"    - {d.planet.value} is a {d.type} to the {d.related_luminary}")
    
    # RECEPTIONS
    recs = report.get("summary", {}).get("mutual_receptions", [])
    if recs:
        output.append(f"\n[SECTION III.B: MUTUAL RECEPTION AUDIT]")
        for r in recs:
            output.append(f"  - {r['planet_a']} <-> {r['planet_b']} | {r['type']} (Strength {r['score']})")
            output.append(f"    - {r['planet_a']} in {r['planet_b']}'s {', '.join(r['dignities_a_in_b'])}")
            output.append(f"    - {r['planet_b']} in {r['planet_a']}'s {', '.join(r['dignities_b_in_a'])}")

    # THE TEAMS
    output.append(f"\n[SECTION III.C: PLANETARY ALIGNMENTS (TEAMS)]")
    output.append(f"  CONSTRUCTIVE TEAM  : {', '.join(summary.get('constructive_team', []))}")
    output.append(f"  DESTRUCTIVE TEAM   : {', '.join(summary.get('destructive_team', []))}")
    output.append(f"  CAUTION            : {summary.get('team_note')}")

    # Mundane Context (The World History)
    mund_context = report.get("advanced_mechanics", {}).get("mundane_context", [])
    output.append(f"\n  Mundane Hierarchy (The Era of Birth):")
    gc_entry = next((e for e in mund_context if e.get("rank") == 2), {})
    gc = gc_entry.get("data", {})
    if gc:
        output.append(f"    - GREAT CONJUNCTION: {gc.get('description')} in {gc.get('sign')}")
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

    # PROFECTIONS
    prof = report.get("profections", {})
    if prof:
        output.append(f"\n[SECTION IV.B: PROFECTION CYCLES (THE SYMBOLIC CLOCK)]")
        output.append(f"  Current Age      : {prof.get('current_age')}")
        output.append(f"  LORD OF THE YEAR : {prof.get('lord_of_year')} (Annual Sign: {prof.get('annual_sign')})")
        output.append(f"  Monthly Sign     : {prof.get('monthly_sign')} (Month {prof.get('target_month')})")
        output.append(f"  Daily Sign       : {prof.get('daily_sign')} (Day {prof.get('target_day')})")

    # DISTRIBUTOR
    dist = report.get("primary_direction_distributor", {})
    if dist:
        output.append(f"\n[SECTION IV.C: THE DISTRIBUTOR (CHIEF OF FATE)]")
        output.append(f"  Current Term Ruler: {dist.get('planet')}")
        output.append(f"  Directed Asc. Lon : {dist.get('directed_ascendant_deg'):.2f}°")
        output.append(f"  Arc of Direction  : {dist.get('arc'):.2f} degrees")
        output.append(f"  Status            : {dist.get('description')}")

    # PRIMARY DIRECTIONS HITS
    p_dirs = report.get("primary_directions", [])
    if p_dirs:
        output.append(f"\n[SECTION IV.D: PRIMARY DIRECTION HITS (0-100 YEARS)]")
        for d in p_dirs[:15]: # Show first 15 major hits
            output.append(f"  - Age {d['years']:5.2f} ({d['date_offset']}): {d['promittor']:8} {d['aspect']:15} to {d['significator']}")

    # V. ARABIC LOTS & STELLAR CONTACTS
    output.append(f"\n[SECTION V: ARABIC LOTS & STELLAR SIGNATURES]")
    
    # Hermetic Lots
    hermetic = report.get("hermetic_lots", {})
    if hermetic:
        output.append(f"  HERMETIC LOTS (Paulus Alexandrinus):")
        for h_name, h_data in hermetic.items():
            output.append(f"    - {h_name:10}: {h_data['longitude']:6.2f}° in {h_data['sign']} (House {h_data['house']})")

    # Forensic Lots
    forensic = report.get("forensic_lots", {})
    if forensic:
        output.append(f"  FORENSIC LOTS (Risk Assessment):")
        for fname, fdata in forensic.items():
            d = fdata.get("data")
            if d:
                output.append(f"    - {fname:15}: {d['longitude']:6.2f}° in {d['sign']} (House {d['house']})")
                if fdata.get("verification"):
                    output.append(f"      * Verification: {fdata.get('verification')}")

    # Traditional Lots
    lots = report.get("lots", {})
    if lots:
        output.append(f"  TRADITIONAL LOTS:")
        for lname, llon in lots.items():
            if llon:
                lsign = list(Sign)[int(llon / 30) % 12]
                output.append(f"    - {lname:10}: {llon:6.2f}° in {lsign.value}")
        
    stars = report.get("stars", [])
    output.append(f"\n  Fixed Star Intersections:")
    for s in stars:
        output.append(f"    - {s.star_name} ({s.contact_type}) on {s.planet_name}: {s.message}")

    # VI. IATROMATHEMATICAL PROTOCOL (MEDICAL)
    med = report.get("medical_analysis", {})
    output.append(f"\n[SECTION VI: IATROMATHEMATICAL PROTOCOL (MEDICAL)]")
    moon_lon = next(p.longitude for p in chart_model.planets if p.name == PlanetName.MOON)
    mansion = LunarMansionEngine.get_lunar_mansion(moon_lon)
    output.append(f"  Current Lunar Mansion: {mansion.get('mansion_id')} ({mansion.get('name')})")
    output.append(f"  Picatrix Intents (Good): {', '.join(mansion.get('intents_good', []))}")
    output.append(f"  Picatrix Intents (Bad) : {', '.join(mansion.get('intents_bad', []))}")
    output.append(f"  Constitutional Mastery: {med.get('constitutional_sign')} rules the {med.get('governed_body_part')}")
    output.append(f"  Humoral Excess: {med.get('distemper', {}).get('excess_humor')}")
    output.append(f"  Palliative Care: {med.get('distemper', {}).get('palliative_nature')}")
    
    # Pathology Alerts
    alerts = med.get("pathology_alerts", [])
    if alerts:
        output.append(f"  PATHOLOGY ALERTS:")
        for alert in alerts:
            output.append(f"    ! {alert.get('type')}: {alert.get('condition')} - {alert.get('details')}")

    # Surgery Risk
    surg = med.get("surgery_risk_analysis", {})
    if surg:
        safe_str = "SAFE" if surg.get("safe") else "RISKY"
        output.append(f"  SURGERY RISK (Current): {safe_str}")
        for reason in surg.get("reasons", []):
            output.append(f"    - {reason}")

    output.append(f"\n  Critical Decumbiture Thresholds (Lunar Phases from Onset):")
    for d in report.get("critical_days_infancy", []):
        output.append(f"    - {d.get('date')} : {d.get('phase')} (Critical Day {d.get('day_number')})")

    # VII. THE TEMPORAL FORECAST
    output.append(f"\n[SECTION VII: THE TEMPORAL FORECAST (NEXT 5 DAYS)]")
    for f in report.get("forecast_5_day", []):
        output.append(f"  {f.get('display_date')} | Chronocrator: {f.get('chronocrator')}")
        output.append(f"    - Mood: {f.get('mood')} | Status: {f.get('summary')}")

    # VIII. SOLAR RETURN ANALYSIS
    sr = report.get("solar_return", {})
    if sr:
        output.append(f"\n[SECTION VIII: SOLAR RETURN AUDIT (YEAR {sr.get('year')})]")
        output.append(f"  Morin's Axiom: {sr.get('morin_axiom')}")
        output.append(f"  SR Asc. in Natal : House {sr.get('sr_asc_in_natal_house')}")
        loy_sr = sr.get("lord_of_year", {})
        output.append(f"  LoY Performance  : {loy_sr.get('name')} (Weight: {loy_sr.get('weight')})")
        for det_sr in loy_sr.get("details", []):
            output.append(f"    ! {det_sr}")
        output.append(f"  Key Determinations:")
        for deter in sr.get("determinations", []):
            output.append(f"    - {deter['judgment']}")

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
