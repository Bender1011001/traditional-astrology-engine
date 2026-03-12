import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open('reading_output.json', encoding='utf-8'))
lots = d.get('lots', {})
hl = d.get('hermetic_lots', {})

keys = ['Marriage_Men', 'Marriage_Women', 'Eros', 'Friends', 'Enemies', 'Debt']
print("=== RELATIONSHIP LOTS ===")
for k in keys:
    v = lots.get(k, hl.get(k, {}))
    fmt = v.get("longitude_fmt", {}).get("string", "?")
    print(f"  {k}: {fmt}  H{v.get('house','?')}  ruler={v.get('ruler','?')}  status={v.get('status','?')}")
    for m in v.get("maltreatment_details", []):
        print(f"    -> {m}")

# Venus details
print("\n=== VENUS (7th ruler from Virgo Asc = Pisces, but natural significator) ===")
for p in d.get('planets', []):
    if p['name'] == 'Venus':
        print(json.dumps(p, indent=2, default=str))

# 7th house planets
print("\n=== 7th HOUSE PLANETS ===")
for p in d.get('planets', []):
    if p.get('house') == 7:
        print(f"  {p['name']} in {p['sign']} {p['longitude_fmt']['string']}")

# Maltreatments on Venus
print("\n=== VENUS MALTREATMENTS ===")
for p in d.get('planets', []):
    if p['name'] == 'Venus':
        for m in p.get('maltreatments', []):
            print(f"  {m}")

# Summary sect teams
print("\n=== SUMMARY TEAMS ===")
s = d.get('summary', {})
print(f"  Constructive: {s.get('constructive_team')}")
print(f"  Destructive: {s.get('destructive_team')}")
print(f"  Hemispheres: {s.get('hemispheres')}")
print(f"  Focus: {s.get('hemisphere_focus')}")
