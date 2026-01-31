import sys
import os
sys.path.insert(0, os.path.abspath("e:/code.projects/astrology"))
from src.engine.chart_calculator import calculate_chart_data

res = calculate_chart_data("2023-10-27", "12:00", "New York", "NY")

if "classical" in res.get("planets", {}).get("Sun", {}):
    print("SUCCESS: Sun Classical Data:")
    print(res["planets"]["Sun"]["classical"])
else:
    print("FAIL: Sun Classical Data Missing")

if "classical" in res:
    print("SUCCESS: Planetary Hours:")
    print(res["classical"]["planetary_hours"])
else:
    print("FAIL: Planetary Hours Parsing Failed")
    if "classical_error" in res:
        print("ERROR:", res["classical_error"])
