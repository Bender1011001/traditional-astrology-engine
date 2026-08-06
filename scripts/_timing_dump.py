import os
import sys
from datetime import datetime

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "src"))
from src.engine.models import Sign
from src.engine.prediction import (FIRDARIA_DAY, calculate_zr_lifetime_map)
from src.engine.reference_data import DOMICILES
from src.scripts.generate_premium_report import generate_chart_data_object

BIRTH = datetime(1996, 8, 13)
ASC_IDX = 5  # Virgo
SIGNS = list(Sign)
VENUS_SIGNS = {"Taurus", "Libra"}

d = generate_chart_data_object("Native", "1996-08-13", "07:18", "Fairfield", "CA", latitude=38.2494, longitude=-122.0397)
fate = d["analysis"]["fate"]

print("=== ANNUAL PROFECTIONS (age 29-50): marriage-relevant years ===")
for age in range(29, 51):
    sidx = (ASC_IDX + age) % 12
    sign = SIGNS[sidx].value
    house = (age % 12) + 1
    loy = DOMICILES[SIGNS[sidx]].value
    tags = []
    if house == 7:
        tags.append("**7TH-HOUSE YEAR (marriage angle; LOY=Jupiter, the 7th lord)**")
    if loy == "Venus":
        tags.append("Venus = Lord of Year")
    if sign == "Cancer":
        tags.append("profected to Cancer (where natal Venus+Mars sit)")
    if sign == "Pisces":
        tags.append("profected to the 7th sign (Pisces)")
    if tags:
        yr = 1996 + age
        print(f"  age {age} (~{yr}-08 to {yr+1}-08): house {house}, {sign}, LOY {loy}  -> {'; '.join(tags)}")

print("\n=== FIRDARIA (day chart) — Venus & Jupiter windows ===")
cum = 0.0
for planet, dur in FIRDARIA_DAY:
    start_age, end_age = cum, cum + dur
    if planet.value in ("Venus", "Jupiter", "Mercury", "Moon"):
        print(f"  {planet.value:8} major: age {start_age:.0f}-{end_age:.0f}  (~{1996+int(start_age)}-{1996+int(end_age)})")
    cum = end_age

print("\n=== ZODIACAL RELEASING — L1 chapters from Spirit & Fortune ===")
for lot in ("Spirit", "Fortune"):
    blk = fate.get("zodiacal_releasing", {}).get(lot, {})
    print(f"\n[{lot}] start {blk.get('start_sign')}")
    for ch in blk.get("l1_chapters", []):
        s = ch["sign"]
        flags = []
        if s in VENUS_SIGNS:
            flags.append("VENUS SIGN")
        if s == "Pisces":
            flags.append("7th sign")
        if s == "Cancer":
            flags.append("Venus+Mars placement")
        if ch.get("peak_from_fortune"):
            flags.append("PEAK")
        if flags:
            print(f"   {ch['sign']:11} {ch['start_date']} -> {ch['end_date']}  {'  '.join(flags)}")

print("\n=== ZR from LOT OF EROS (desire/love) ===")
eros_lon = 87.689
eros_sign = SIGNS[int(eros_lon / 30) % 12]
print(f"Eros in {eros_sign.value}")
for ch in calculate_zr_lifetime_map(eros_sign, BIRTH, years=60, max_level=1):
    s = ch["sign"]
    if s in VENUS_SIGNS or s in ("Pisces", "Cancer", "Libra", "Taurus"):
        print(f"   {s:11} {ch['start_date']} -> {ch['end_date']}  duration {ch['duration_years']}y")

print("\n=== PRIMARY DIRECTIONS involving Venus / Jupiter / Descendant ===")
for dd in fate.get("primary_directions", []):
    sig = str(dd.get("significator", "")); prom = str(dd.get("promittor", "")); asp = dd.get("aspect", "")
    yrs = dd.get("years")
    if any(x in (sig + prom) for x in ("Venus", "Jupiter", "Descendant", "Desc")):
        print(f"   {sig} {asp} {prom} @ age {yrs:.1f} (~{1996+int(yrs)})" if isinstance(yrs,(int,float)) else f"   {sig} {asp} {prom}")
for dd in fate.get("planet_to_planet_directions", []):
    sig = str(dd.get("significator", "")); prom = str(dd.get("promittor", "")); asp = dd.get("aspect","")
    yrs = dd.get("years")
    if "Venus" in (sig+prom) and isinstance(yrs,(int,float)) and 25 <= yrs <= 55:
        print(f"   p2p: {sig} {asp} {prom} @ age {yrs:.1f} (~{1996+int(yrs)})")
