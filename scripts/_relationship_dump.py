import json
import os
import sys

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "src"))
from src.scripts.generate_premium_report import generate_chart_data_object

d = generate_chart_data_object("Native", "1996-08-13", "07:18", "Fairfield", "CA", latitude=38.2494, longitude=-122.0397)
a = d["analysis"]
pf = {p["name"]: p for p in a["planets_forensic"]}


def cond(name):
    p = pf.get(name, {})
    dg = p.get("dignities", {})
    return {
        "sign": p.get("sign"),
        "lon": round(float(p.get("longitude", 0)) % 30, 2),
        "dignity_total": dg.get("total_score"),
        "breakdown": dg.get("score_breakdown"),
        "retro": p.get("retrograde"),
        "solar": p.get("solar_status"),
        "maltreatments": [m.get("description") if isinstance(m, dict) else m for m in (p.get("maltreatments") or [])],
    }


print("SECT:", (a.get("sect") or {}).get("type"))
print("\n--- VENUS ---"); print(json.dumps(cond("Venus"), indent=1, default=str))
print("\n--- MARS ---"); print(json.dumps(cond("Mars"), indent=1, default=str))
print("\n--- MOON ---"); print(json.dumps(cond("Moon"), indent=1, default=str))
print("\n--- JUPITER (7th lord) ---"); print(json.dumps(cond("Jupiter"), indent=1, default=str))

top = a.get("topical", {})
print("\n--- 5th & 7th TOPOI ---")
for t in top.get("twelve_topoi", []):
    if t["house"] in (5, 7):
        rc = t.get("ruler_condition", {})
        print(f"H{t['house']} {t['sign']} ruler={t['ruler']} band={rc.get('condition_band')} aversion={t.get('ruler_in_aversion_to_its_house')} occupants={t.get('occupants')} reasons={rc.get('reasons')}")

print("\n--- MARRIAGE SIGNIFICATORS ---")
for s in top.get("natural_significators", []):
    if "Marriage" in s["topic"] or s["topic"] in ("Children",):
        sigs = [(x["planet"], x["condition"].get("condition_band")) for x in s.get("natural_significators", [])]
        print(f"{s['topic']}: house {s['house']} ({s['house_sign']}, lord {s['house_ruler']}) sigs={sigs}")
        print(f"   rule: {s['rule']}")

print("\n--- RECEPTIONS (escape hatches) ---")
for r in (a.get("teams", {}) or {}).get("receptions", []):
    print(" ", json.dumps(r, default=str)[:240])

print("\n--- DEGREE QUALITIES (Venus/Mars/7th cusp) ---")
dq = a.get("degree_qualities", {})
for k in ("Venus", "Mars"):
    c = dq.get(k, {})
    print(f"{k}: {c.get('sign')} deg{c.get('degree_one_based')} mf={c.get('masculine_feminine')} ldsv={c.get('light_dark_smoky_void')} pitted={c.get('pitted')} azimene={c.get('azimene')}")

print("\n--- LOTS (marriage/eros) ---")
for lot, v in (a.get("fate", {}).get("hermetic_lots", {}) or {}).items():
    if any(w in str(lot).lower() for w in ("marriage", "eros", "necessity")):
        lon = v.get("longitude") if isinstance(v, dict) else v
        print(f"  {lot}: {lon}")
fl = a.get("forensic_lots", {}) or {}
for lot, v in fl.items():
    if "marriage" in str(lot).lower() or "eros" in str(lot).lower():
        print(f"  forensic {lot}: {json.dumps(v, default=str)[:200]}")

print("\n--- REMEDIATION (Venus if afflicted) ---")
for rx in (a.get("remediation", {}) or {}).get("prescriptions", []):
    if rx.get("planet") in ("Venus", "Mars"):
        print(f"  {rx['planet']}: {rx['election']['day']}, hour of {rx['election']['planetary_hour']}; acts={rx['safe_remedies']['charitable_acts'][:2]}")
