import sys
import os
import json
from datetime import datetime
from typing import Dict, Any
import swisseph as swe

# Ensure project root is in path
# Current file is in <ROOT>/tests/regression/
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from src.engine.logic import perform_forensic_audit
    from src.engine.models import Chart, Planet, PlanetName, Sign
except ImportError as e:
    print(f"❌ Critical Error: Could not import engine from {ROOT_DIR}")
    print(f"Traceback details: {e}")
    sys.exit(1)

def run_regression_test():
    """
    Detailed Report Regression Test Suite.
    Compares current engine output against 'Golden References' for historical charts.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ref_path = os.path.join(script_dir, "golden_references.json")
    
    if not os.path.exists(ref_path):
        print(f"❌ Error: Reference file not found at {ref_path}")
        sys.exit(1)

    with open(ref_path, "r") as f:
        golden_data = json.load(f)

    failures = []

    print("🚀 Starting Detailed Report Verification (Regression Suite)\n")

    for key, data in golden_data.items():
        print(f"Checking: {data['name']}...")
        bd = data['birth_data']
        expected = data['expected_results']
        
        # 1. Calculate Natal Chart (Directly with coordinates)
        # Using accurate historical JD
        jd = swe.julday(bd['year'], bd['month'], bd['day'], bd['hour'])
        
        planets_to_calc = {
            "Sun": swe.SUN,
            "Moon": swe.MOON,
            "Mercury": swe.MERCURY,
            "Venus": swe.VENUS,
            "Mars": swe.MARS,
            "Jupiter": swe.JUPITER,
            "Saturn": swe.SATURN,
            "Uranus": swe.URANUS,
            "Neptune": swe.NEPTUNE,
            "Pluto": swe.PLUTO,
            "North_Node": swe.MEAN_NODE
        }
        
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        topo_flags = flags | swe.FLG_TOPOCTR
        swe.set_topo(bd['lon'], bd['lat'], 0)
        
        calculated_planets = []
        sun_alt = 0.0
        
        for pname, pid in planets_to_calc.items():
            res = swe.calc_ut(jd, pid, flags)
            coords = res[0]
            
            # Altitude for Sun / Topocentric
            topo_res = swe.calc_ut(jd, pid, topo_flags)
            topo_coords = topo_res[0]
            xin = (topo_coords[0], topo_coords[1], topo_coords[2])
            azresult = swe.azalt(jd, swe.ECL2HOR, (bd['lon'], bd['lat'], 0), 0, 0, xin)
            altitude = azresult[1]
            
            p_enum = PlanetName.NORTH_NODE if pname == "North_Node" else PlanetName[pname.upper()]
            calculated_planets.append(Planet(
                name=p_enum,
                longitude=coords[0],
                latitude=coords[1],
                speed=coords[3],
                altitude=altitude
            ))
            
            if pname == "Sun":
                sun_alt = altitude

        # Angles and Houses (Placidus)
        cusps, ascmc = swe.houses(jd, bd['lat'], bd['lon'], b'P')
        
        chart_obj = Chart(
            sun_altitude=sun_alt,
            planets=calculated_planets,
            ascendant=ascmc[0],
            mc=ascmc[1],
            geo_lat=bd['lat'],
            geo_lon=bd['lon'],
            jd=jd,
            houses={i+1: c for i, c in enumerate(cusps)}
        )
        
        # 2. Run Forensic Audit
        age_key = [k for k in expected.keys() if k.startswith("lord_of_year_age_")]
        test_age = 0
        if age_key:
            test_age = int(age_key[0].split("_")[-1])
            
        audit = perform_forensic_audit(
            chart_obj, 
            jd=chart_obj.jd, 
            age=test_age, 
            birth_date=datetime(bd['year'], bd['month'], bd['day'])
        )

        # 3. Assertions
        def get_sign_str(lon):
            idx = int(lon / 30) % 12
            return list(Sign)[idx].value

        actuals = {
            "ascendant_sign": get_sign_str(chart_obj.ascendant),
            "mc_sign": get_sign_str(chart_obj.mc),
            "almuten_figuris": audit.get("soul_guardian", {}).get("almuten"),
            "hyleg": audit.get("vitality", {}).get("hyleg")
        }
        
        if age_key:
            actuals[age_key[0]] = audit.get("profections", {}).get("lord_of_year")

        for metric, exp_val in expected.items():
            act_val = actuals.get(metric)
            if str(act_val) != str(exp_val):
                failures.append(f"FAILED: {data['name']} | {metric} | Expected: {exp_val}, Actual: {act_val}")
                print(f"  ❌ {metric}: {act_val} (Expected: {exp_val})")
            else:
                print(f"  ✅ {metric}: {act_val}")
        
    print("\n--- Summary ---")
    if not failures:
        print("✅ ALL TESTS PASSED. Forensic accuracy maintained.")
        sys.exit(0)
    else:
        print(f"❌ {len(failures)} TESTS FAILED.")
        for f in failures:
            print(f"  {f}")
        sys.exit(1)

if __name__ == "__main__":
    run_regression_test()
