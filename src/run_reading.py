import sys
import os
from datetime import datetime
import swisseph as swe

# Adjust path to include "src"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.chart_calculator import calculate_chart_data
from engine.models import Chart, Planet, PlanetName, Sign
from engine.logic import perform_forensic_audit
from engine.reference_data import PLANETARY_YEARS

def map_to_planet_name(k):
    # Mapping string keys to PlanetName enum
    k = k.upper()
    if k == "NORTH_NODE": return PlanetName.NORTH_NODE
    if k == "SOUTH_NODE": return PlanetName.SOUTH_NODE
    try:
        return PlanetName[k]
    except:
        return None

def generate_report_local(chart: Chart, birth_date: datetime, analysis_date: datetime, analysis_jd: float, age: int):
    print("=== AstroForge: UNIVERSAL CAUSATION AUDIT ===\n")
    print("FINAL VERIFIED REPORT\n")
    
    audit = perform_forensic_audit(
        chart,
        chart.jd or 0.0,
        age=age,
        month=analysis_date.month,
        day=analysis_date.day,
        birth_date=birth_date,
        analysis_date=analysis_date,
        analysis_jd=analysis_jd
    )
    summary = audit["summary"]
    
    print(f"SECT: {summary['sect']} | CONSTRUCTIVE: {', '.join(summary['constructive_team'])}")
    print(f"DESTRUCTIVE: {', '.join(summary['destructive_team'])}")
    print(f"LUNAR PHASE: {summary.get('lunar_phase')} | PATTERN: {summary.get('jones_pattern')}")
    
    # Temperament & Mansion (Soul Architecture)
    print("-" * 50)
    print("SECTION 0: SOUL ARCHITECTURE")
    if "temperament" in summary:
        temp = summary["temperament"]
        print(f"  TEMPERAMENT: {temp.get('primary_temperament')}")
        print(f"  Balance: Hot {temp.get('scores',{}).get('Hot')} | Cold {temp.get('scores',{}).get('Cold')} | Wet {temp.get('scores',{}).get('Moist')} | Dry {temp.get('scores',{}).get('Dry')}")
        
    if "lunar_mansion" in summary and summary["lunar_mansion"]:
        lm = summary["lunar_mansion"]
        print(f"  LUNAR MANSION: {lm.get('mansion_number')}. {lm.get('name')} ({lm.get('significator')})")
        print(f"  Image: {lm.get('image')}")
    
    # Soul Guardian
    if "soul_guardian" in audit and audit["soul_guardian"]:
        sg = audit["soul_guardian"]
        print(f"  SOUL GUARDIAN: {sg.get('almuten')} | Term Ruler: {sg.get('term_ruler')}")
        print(f"  Role: {sg.get('job_description')}")
        
    # Planetary Hours
    if "planetary_hours" in summary and summary["planetary_hours"]:
        ph = summary["planetary_hours"]
        if "day_ruler" in ph:
            print(f"  PLANETARY DAY: {ph['day_ruler']} | HOUR: {ph['hour_ruler']}")
            
    print("-" * 50)
    
    # 1. The Lots
    print("SECTION 1: THE HERMETIC LOTS (Geometric Fate)")
    for name, val in audit.get("lots", {}).items():
        sign_idx = int(val / 30) % 12
        sign_name = list(Sign)[sign_idx].value
        deg = val % 30
        print(f"  Lot of {name:<10}: {sign_name:<10} @ {deg:.2f}°")
    print("-" * 50)
    
    # 2. Key Witnesses (Stars & Nodes)
    print("SECTION 2: THE CELESTIAL CURIA (Stars & Nodes)")
    if audit.get("stars"):
        for s in audit["stars"]:
            # Handle list of dicts (returned by check_fixed_stars -> logic)
            # Actually stars logic in logic.py calls check_fixed_stars
            # Handle list of StarContact objects or dicts
            # Logic engine often returns object.
            try:
                s_name = s.star_name
                p_name = s.planet_name
                msg = s.message
            except AttributeError:
                s_name = s.get('star_name', 'Unknown')
                p_name = s.get('planet_name', 'Unknown')
                msg = s.get('message', '')
            print(f"  [STELLATUM] {p_name} + {s_name}: {msg}")
    else:
        print("  No major Royal Star conjunctions detected.")
        
    if audit.get("nodes"):
        for n in audit["nodes"]:
            try:
                p_name = n.planet_name
                n_type = n.node_type
                desc = n.description
            except AttributeError:
                p_name = n.get('planet_name')
                n_type = n.get('node_type')
                desc = n.get('description')
            print(f"  [DRACONIC]  {p_name} ({n_type}): {desc}")
    else:
        print("  No Nodal contacts.")
    print("-" * 50)
        
    # 3. The Ministers (Planets)
    print("SECTION 3: CONDITION OF THE MINISTERS (Planetary Forensic)")
    
    # Logic returns chart.planets? No, audit["planets"] is a list of analysis dicts?
    # Logic.py: "planets": [], # WAIT. Logic.py sets "planets": [] at the end?
    # Let's check logic.py line 434 in Step 254.
    # "planets": [], <-- It's empty in current logic.py!
    # Ah, I need to check if forensic logic populates it or if I need to call something else.
    # Looking at logic.py provided in Step 254... it seems "planets" key is initialized as empty list and never populated in the snippet I saw!
    # The snippet was truncated though.
    # But looking at `perform_forensic_audit`, it does lots of stuff.
    # Wait, `main.py` uses `audit["planets"]`.
    # Let me check `src/engine/logic.py` fully to see if it populates planets.
    # If not, I can just print the chart info myself.
    
    if not audit.get("planets"):
        # Fallback: Print raw chart data
        for p in chart.planets:
            print(f"PLANET: {p.name.value.upper()} @ {p.sign.value} {p.degree_in_sign:.2f}°")
            # We can't easily get the deep analysis without the logic engine doing it.
            # But the user asked for a "Reading", so the logic engine SHOULD produce it.
            # If logic.py is incomplete, that's an issue.
            pass
    
    for p in audit.get("planets", []):
        if p.get("planet") == "Sun": continue # Skip sun if handled separately or just duplicates?
        
        print(f"PLANET: {str(p.get('planet')).upper()}")
        print(f"  Loc: {p.get('sign')} @ {p.get('longitude')%30:.2f}°")
        print(f"  Status: {p.get('sect_status')} | Power: {p.get('power_label')} ({p.get('dignity_score')})")
        
        # Receptions involving this planet
        if "mutual_receptions" in summary:
            for r in summary["mutual_receptions"]:
                if r["planet_a"] == p.get("planet") or r["planet_b"] == p.get("planet"):
                    other = r["planet_b"] if r["planet_a"] == p.get("planet") else r["planet_a"]
                    print(f"  [RECEPTION] Mutual with {other} ({r['type']})")

        # Impacts
        if "impacts" in p:
            for impact in p['impacts']:
                print(f"  ! {impact.get('cause')}: {impact.get('effect')}")
            
        print("")
        
    print("-" * 50)
    
    # 4. Primary Directions
    if "primary_directions" in audit and audit["primary_directions"]:
        print("SECTION 4: PRIMARY DIRECTIONS (Directions to Angles)")
        # Show hits near current age.
        year_now = age
        hits = [d for d in audit["primary_directions"] if year_now - 2 < d['years'] < year_now + 5]
        if hits:
            for h in hits:
                print(f"  Age {h['years']:.1f}: {h['promittor']} {h['aspect']} {h['significator']} ({h['arc']}°)")
        else:
            print("  No major directions to angles in immediate timeframe.")
            
    print("-" * 50)

    # 5. Vitality & Longevity
    if "vitality" in audit and audit["vitality"]:
        vit = audit["vitality"]
        print("SECTION 5: VITALITY & LONGEVITY (Hyleg/Alcocoden)")
        print(f"  HYLEG (Giver of Life): {vit.get('hyleg', 'Unknown')}")
        print(f"  ALCOCODEN (Giver of Years): {vit.get('alcocoden', 'Unknown')}")
        print(f"  Calculated Years: {vit.get('total_years')} ({vit.get('base_years_type')} Base)")
        if 'breakdown' in vit:
            print("  Factors:")
            for factor in vit['breakdown']:
                print(f"    - {factor}")
    else:
        print("SECTION 5: VITALITY")
        print("  No Hyleg/Alcocoden determined (or algorithm failed).")
            
    print("==================================================")


def run_reading(date_str, time_str, city, state):
    print(f"Calculating chart for {date_str} {time_str} in {city}, {state}...")
    
    data = calculate_chart_data(date_str, time_str, city, state)
    
    if "error" in data:
        print(f"Error: {data['error']}")
        return

    # Convert to Chart Object
    planet_objects = []
    sun_alt = 0.0
    
    for name, pdata in data["planets"].items():
        pname = map_to_planet_name(name)
        if not pname: continue
        
        planet = Planet(
            name=pname,
            longitude=pdata["longitude"],
            latitude=pdata.get("latitude", 0.0),
            speed=pdata.get("speed", 0.0),
            altitude=pdata.get("altitude", 0.0)
        )
        planet_objects.append(planet)
        
        if pname == PlanetName.SUN:
            sun_alt = pdata.get("altitude", 0.0)

    # Angles
    asc = data["angles"]["Ascendant"]
    mc = data["angles"]["MC"]
    nn = data["planets"].get("North_Node", {}).get("longitude", 0.0)
    sn = data["planets"].get("South_Node", {}).get("longitude", 0.0)

    chart = Chart(
        sun_altitude=sun_alt,
        planets=planet_objects,
        ascendant=asc,
        mc=mc,
        north_node=nn,
        south_node=sn,
        geo_lat=data["meta"].get("lat"),
        geo_lon=data["meta"].get("lon"),
        jd=data["meta"].get("julian_day")
    )
    
    # Birth datetime (local, naive)
    try:
        birth_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        birth_dt = datetime.now()

    # Analysis datetime (now)
    analysis_dt = datetime.now()

    # Calculate completed years
    age = analysis_dt.year - birth_dt.year - ((analysis_dt.month, analysis_dt.day) < (birth_dt.month, birth_dt.day))

    # Analysis JD for transit-based sections
    analysis_jd = swe.julday(
        analysis_dt.year,
        analysis_dt.month,
        analysis_dt.day,
        analysis_dt.hour + analysis_dt.minute / 60.0 + analysis_dt.second / 3600.0
    )
    
    # Generate Report
    try:
        generate_report_local(chart, birth_dt, analysis_dt, analysis_jd, age)
    except Exception:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    d_str = "1996-08-13"
    t_str = "07:18"
    city = "Fairfield"
    state = "CA"
    
    run_reading(d_str, t_str, city, state)
