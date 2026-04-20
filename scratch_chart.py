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

# Print astronomy data
print("=== ASTRONOMY ===")
print(json.dumps(td.get("astronomy", {}), indent=2, default=str))

print("\n=== META ===")
print(json.dumps(td.get("meta", {}), indent=2, default=str))

print("\n=== ASPECTS ===")
analysis = td.get("analysis", {})
print(json.dumps(analysis.get("aspects", []), indent=2, default=str))

print("\n=== SHADOW ASPECTS ===")
print(json.dumps(analysis.get("aspects_shadow", []), indent=2, default=str))

print("\n=== DIGNITY ===")
print(json.dumps(analysis.get("dignity", {}), indent=2, default=str))

print("\n=== SECT ===")
print(json.dumps(analysis.get("sect", {}), indent=2, default=str))

print("\n=== TEMPERAMENT ===")
print(json.dumps(analysis.get("temperament", {}), indent=2, default=str))

print("\n=== VITALITY ===")
print(json.dumps(analysis.get("vitality", {}), indent=2, default=str))

print("\n=== PLANETS FORENSIC ===")
print(json.dumps(td.get("planets_forensic", []), indent=2, default=str))

print("\n=== SUPPLEMENTAL ===")
print(json.dumps(analysis.get("supplemental", {}), indent=2, default=str))

print("\n=== SYZYGY ===")
print(json.dumps(analysis.get("syzygy", {}), indent=2, default=str))

print("\n=== ANGLES ===")
print(json.dumps(analysis.get("angles", {}), indent=2, default=str))

print("\n=== FORENSIC LOTS ===")
print(json.dumps(analysis.get("forensic_lots", {}), indent=2, default=str))

print("\n=== FATE ===")
fate = analysis.get("fate", {})
print(json.dumps({k: v for k, v in fate.items() if k != "active_directions"}, indent=2, default=str))

print("\n=== MEDICAL ===")
print(json.dumps(analysis.get("medical", {}), indent=2, default=str))

print("\n=== TEAMS ===")
print(json.dumps(analysis.get("teams", {}), indent=2, default=str))
