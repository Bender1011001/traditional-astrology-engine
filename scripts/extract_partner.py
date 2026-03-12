import json, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open('reading_output.json', encoding='utf-8'))

# Primary directions to DSC
print("=== PRIMARY DIRECTIONS (to Descendant / 7th cusp) ===")
pds = d.get('primary_directions', [])
for pd in pds:
    if 'DSC' in str(pd.get('angle','')) or 'Desc' in str(pd.get('angle','')) or '7' in str(pd.get('angle','')):
        print(json.dumps(pd, indent=2, default=str))
print(f"\nTotal directions found: {len(pds)}")
# Show all angles targeted
angles_seen = set()
for pd in pds:
    angles_seen.add(str(pd.get('angle', pd.get('target', pd.get('point', '?')))))
print(f"Angles targeted: {angles_seen}")

# Show first few directions
print("\n=== FIRST 5 PRIMARY DIRECTIONS ===")
for pd in pds[:5]:
    print(json.dumps(pd, indent=2, default=str))

# Upcoming transits that hit 7th house or Venus/Jupiter
print("\n=== UPCOMING TRANSITS (3mo) ===")
transits = d.get('upcoming_transits_3mo', [])
for t in transits:
    desc = str(t)
    if any(k in desc for k in ['Jupiter', 'Venus', 'Pisces', '7th', 'Descendant']):
        print(json.dumps(t, indent=2, default=str))
print(f"\nTotal upcoming transits: {len(transits)}")

# Show all transits
print("\n=== ALL UPCOMING TRANSITS ===")
for t in transits[:15]:
    print(json.dumps(t, indent=2, default=str))

# Advanced prediction - transits
ap = d.get('advanced_prediction', {})
print("\n=== ADVANCED TRANSITS ===")
trs = ap.get('transits', [])
for t in trs:
    print(json.dumps(t, indent=2, default=str))

# Lots detail
print("\n=== LOT OF EROS ===")
lots = d.get('lots', {})
eros = lots.get('Eros', {})
print(json.dumps(eros, indent=2, default=str))

# Advanced mechanics
print("\n=== ADVANCED MECHANICS KEYS ===")
am = d.get('advanced_mechanics', {})
print(json.dumps(list(am.keys()), indent=2))

# Dodecatemoria of Venus and Jupiter
print("\n=== VENUS DODECATEMORIA ===")
for p in d.get('planets', []):
    if p['name'] in ['Venus', 'Jupiter']:
        dod = p.get('classical', {}).get('dodecatemoria', {})
        print(f"{p['name']}: Valens={dod.get('valens',{}).get('longitude_fmt',{}).get('string','?')} ({dod.get('valens',{}).get('sign','?')} H{dod.get('valens',{}).get('house','?')})")
        print(f"         Paul={dod.get('paul',{}).get('longitude_fmt',{}).get('string','?')} ({dod.get('paul',{}).get('sign','?')} H{dod.get('paul',{}).get('house','?')})")
