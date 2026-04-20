import json
import sys
sys.path.insert(0, "E:\\code.projects\\astrology")
from src.engine.forensic_engine import Auditor

result = Auditor.generate_full_nativity(
    date_str="1996-08-13",
    time_str="07:18",
    city="Fairfield",
    state="California",
    name="Native"
)

if "error" in result:
    print(f"ERROR: {result['error']}")
    sys.exit(1)

td = result.get("technical_data", {})
output = {}

# Core astronomy
astro = td.get("astronomy", {})
output["planets"] = astro.get("planets", {})
output["houses"] = astro.get("houses", {})
output["angles"] = astro.get("angles", {})

# Meta
output["meta"] = td.get("meta", {})

# Analysis
analysis = td.get("analysis", {})
output["sect"] = analysis.get("sect", {})
output["aspects"] = analysis.get("aspects", [])
output["aspects_shadow"] = analysis.get("aspects_shadow", [])
output["dignity"] = analysis.get("dignity", {})
output["temperament"] = analysis.get("temperament", {})
output["vitality"] = analysis.get("vitality", {})
output["syzygy"] = analysis.get("syzygy", {})
output["analysis_angles"] = analysis.get("angles", {})
output["elements"] = analysis.get("supplemental", {}).get("elements", {})
output["hemispheres"] = analysis.get("supplemental", {}).get("hemispheres", {})
output["lunar_mansion"] = analysis.get("supplemental", {}).get("lunar_mansion", {})
output["stars"] = analysis.get("supplemental", {}).get("stars", [])
output["teams"] = analysis.get("teams", {})
output["medical"] = analysis.get("medical", {})
output["forensic_lots"] = analysis.get("forensic_lots", {})

# Planets forensic 
output["planets_forensic"] = td.get("planets_forensic", [])

with open("E:\\code.projects\\astrology\\chart_data.json", "w") as f:
    json.dump(output, f, indent=2, default=str)

print("SUCCESS: Chart data written to chart_data.json")
print(f"Planets: {len(output.get('planets', {}))}")
print(f"Aspects: {len(output.get('aspects', []))}")
print(f"Shadow Aspects: {len(output.get('aspects_shadow', []))}")
