import sys
import os
import json
from datetime import datetime
from typing import Dict, Any

# Ensure project root is in path
sys.path.append(".")

try:
    from src.engine.chart_calculator import get_julian_day, calculate_chart_data
    from src.engine.logic import perform_forensic_audit
    from src.engine.models import Chart, Planet, PlanetName
except ImportError as e:
    print(f"❌ Critical Error: Could not import engine. Path: {os.getcwd()}")
    print(f"Traceback details: {e}")
    sys.exit(1)

def run_regression_test():
    """
    God Mode Regression Test Suite.
    Compares current engine output against 'Golden References' for historical charts.
    """
    ref_path = os.path.join("tests", "regression", "golden_references.json")
    if not os.path.exists(ref_path):
        print(f"❌ Error: Reference file not found at {ref_path}")
        sys.exit(1)

    with open(ref_path, "r") as f:
        golden_data = json.load(f)

    failures = []

    print("🚀 Starting God Mode Verification (Regression Suite)\n")

    for key, data in golden_data.items():
        print(f"Checking: {data['name']}...")
        bd = data['birth_data']
        expected = data['expected_results']
        
        # 1. Calculate Natal Chart
        # Format date and time for calculate_chart_data
        date_str = f"{bd['year']}-{bd['month']:02d}-{bd['day']:02d}"
        # Convert decimal hour to HH:MM
        hours = int(bd['hour'])
        minutes = int((bd['hour'] - hours) * 60)
        time_str = f"{hours:02d}:{minutes:02d}"
        
        chart_data_raw = calculate_chart_data(date_str, time_str, "", "", lat=bd['lat'], lon=bd['lon'])
        
        if "error" in chart_data_raw:
            print(f"  ❌ Error calculating chart: {chart_data_raw['error']}")
            failures.append(f"FAILED: {data['name']} | Calculation Error")
            continue

        # Reconstruct Chart object for forensic audit
        planets = []
        for pname, pinfo in chart_data_raw["planets"].items():
            try:
                p_enum = PlanetName[pname.upper()]
                planets.append(Planet(
                    name=p_enum,
                    longitude=pinfo["longitude"],
                    latitude=pinfo.get("latitude", 0),
                    speed=pinfo.get("speed", 0),
                    altitude=pinfo.get("altitude", 0)
                ))
            except (KeyError, ValueError):
                continue
                
        chart_obj = Chart(
            sun_altitude=chart_data_raw["planets"].get("Sun", {}).get("altitude", 0),
            planets=planets,
            ascendant=chart_data_raw["angles"]["Ascendant"],
            mc=chart_data_raw["angles"]["MC"],
            geo_lat=bd['lat'],
            geo_lon=bd['lon'],
            jd=chart_data_raw["meta"]["julian_day"],
            houses=chart_data_raw["houses"]
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
        # Get Sign labels correctly
        from src.engine.models import Sign
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
