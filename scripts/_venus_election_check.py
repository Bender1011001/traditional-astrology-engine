import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "src"))
import swisseph as swe

from src.engine.planetary_hours import PlanetaryHourEngine

LAT, LON = 38.2494, -122.0397
TZ = -7  # PDT
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
CHALDEAN = ["Saturn","Jupiter","Mars","Sun","Venus","Mercury","Moon"]

def lon_of(jd, body):
    return swe.calc_ut(jd, body, swe.FLG_SWIEPH)[0][0]

def sign_deg(lon):
    return SIGNS[int(lon//30)%12], round(lon%30,2)

def aspect(a, b):
    d = abs(a-b)%360
    if d>180: d=360-d
    for name,ang in [("conjunction",0),("sextile",60),("square",90),("trine",120),("opposition",180)]:
        if abs(d-ang)<=6.5:
            return name, round(abs(d-ang),2)
    return None, round(d,1)

def venus_dignity(lon):
    s = SIGNS[int(lon//30)%12]
    if s in ("Taurus","Libra"): return f"DOMICILE in {s} (very strong)"
    if s=="Pisces": return "EXALTATION in Pisces (strong)"
    if s in ("Aries","Scorpio"): return f"DETRIMENT in {s} (weak)"
    if s=="Virgo": return "FALL in Virgo (weak)"
    if s in ("Cancer","Scorpio","Pisces"): return f"Triplicity (water) in {s} (moderate)"
    return f"Peregrine in {s} (no major dignity)"

# Friday June 12, 2026, evaluate at ~Friday 21:00 PDT = Sat 04:00 UT
jd = swe.julday(2026,6,13,4.0)
print("=== POSITIONS (Fri Jun 12, 2026 ~21:00 PDT) ===")
pos = {}
for name,b in [("Sun",swe.SUN),("Moon",swe.MOON),("Venus",swe.VENUS),("Mars",swe.MARS),("Jupiter",swe.JUPITER),("Saturn",swe.SATURN)]:
    L = lon_of(jd,b); pos[name]=L
    s,d = sign_deg(L); print(f"  {name:8} {s} {d}°")

print("\n=== VENUS CONDITION ===")
print("  Dignity:", venus_dignity(pos["Venus"]))
for other in ("Saturn","Mars","Jupiter"):
    asp,orb = aspect(pos["Venus"],pos[other])
    tag = " <-- AFFLICTION" if (other in ("Saturn","Mars") and asp in ("conjunction","square","opposition")) else (" (benefic aid)" if other=="Jupiter" and asp in ("conjunction","sextile","trine") else "")
    print(f"  Venus-{other}: {asp or 'no aspect'} (orb {orb}°){tag}")

print("\n=== MOON ===")
elong = (pos["Moon"]-pos["Sun"])%360
waxing = elong<180
phase = "NEW/dark" if elong<15 or elong>345 else ("FULL" if 165<elong<195 else ("waxing" if waxing else "waning"))
ms,md = sign_deg(pos["Moon"])
print(f"  Moon in {ms} {md}°, elongation {round(elong,1)}° -> {('WAXING' if waxing else 'WANING')} ({phase})")
masp,morb = aspect(pos["Moon"],pos["Venus"])
print(f"  Moon-Venus: {masp or 'no aspect'} (orb {morb}°)")

print("\n=== PLANETARY HOURS (Friday Jun 12 @ Fairfield) ===")
t = PlanetaryHourEngine._calculate_sun_times(LAT, LON, datetime(2026,6,12))
rise, setting, nxt = t["rise_jd"], t["set_jd"], t["next_rise_jd"]
def jd_local(j):
    y,m,d,h = swe.revjul(j)
    dt = datetime(int(y),int(m),int(d)) + timedelta(hours=h) + timedelta(hours=TZ)
    return dt
print(f"  Sunrise: {jd_local(rise):%a %H:%M} PDT | Sunset: {jd_local(setting):%a %H:%M} PDT")
day_h=(setting-rise)/12; night_h=(nxt-setting)/12
start_idx = CHALDEAN.index("Venus")  # Friday day-ruler
venus_hours=[]
for i in range(24):
    ruler = CHALDEAN[(start_idx+i)%7]
    if i<12:
        hs=rise+i*day_h; he=rise+(i+1)*day_h
    else:
        hs=setting+(i-12)*night_h; he=setting+(i-11)*night_h
    if ruler=="Venus":
        venus_hours.append((jd_local(hs), jd_local(he), "day" if i<12 else "night"))
print("  VENUS HOURS tonight/Friday:")
for s,e,ph in venus_hours:
    print(f"    {s:%a %H:%M} -> {e:%H:%M} PDT  ({ph} hour)")
