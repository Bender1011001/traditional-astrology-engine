import sys
import os
import json
from datetime import datetime
from typing import Dict, Any

# Ensure project root is in path
# We use an absolute reference to ensure reliability across environments
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from src.engine.chart_calculator import ChartCalculator
    from src.engine.logic import perform_forensic_audit
except ImportError as e:
    print(f"❌ Critical Error: Could not import engine from {ROOT_DIR}")
    print(f"Traceback details: {e}")
    sys.exit(1)

def run_regression_test():
    """
    God Mode Regression Test Suite.
    Compares current engine output against 'Golden References' for historical charts.
    """
    ref_path = os.path.join(os.path.dirname(__file__), "golden_references.json")
    if not os.path.exists(ref_path):
        print(f"❌ Error: Reference file not found at {ref_path}")
        sys.exit(1)

    with open(ref_path, "r") as f:
        golden_data = json.load(f)

    calc = ChartCalculator()
    failures = []

    print("🚀 Starting God Mode Verification (Regression Suite)\n")

    for key, data in golden_data.items():
        print(f"Checking: {data['name']}...")
        bd = data['birth_data']
        expected = data['expected_results']
        
        # 1. Calculate Natal Chart
        jd = calc.get_jd(bd['year'], bd['month'], bd['day'], bd['hour'])
        chart = calc.calculate_chart(jd, bd['lat'], bd['lon'])
        
        # 2. Run Forensic Audit
        age_key = [k for k in expected.keys() if k.startswith("lord_of_year_age_")]
        test_age = 0
        if age_key:
            test_age = int(age_key[0].split("_")[-1])
            
        audit = perform_forensic_audit(
            chart, 
            jd=jd, 
            age=test_age, 
            birth_date=datetime(bd['year'], bd['month'], bd['day'])
        )

        # 3. Assertions
        actuals = {
            "ascendant_sign": chart.asc_sign.value if hasattr(chart.asc_sign, 'value') else str(chart.asc_sign),
            "mc_sign": chart.mc_sign.value if hasattr(chart.mc_sign, 'value') else str(chart.mc_sign),
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
