from typing import Dict, List, Optional, Tuple, Literal
from dataclasses import dataclass
import math
from datetime import datetime
import swisseph as swe
from .models import Planet, PlanetName, Sign
from .reference_data import DOMICILES, MOIETIES, EGYPTIAN_TERMS

# ==========================================
# 1. ANTISCIA & CONTRA-ANTISCIA (Shadow Points)
# ==========================================

@dataclass
class AntisciaPoint:
    original_lon: float
    antiscia_lon: float
    contra_antiscia_lon: float
    antiscia_sign: Sign
    contra_antiscia_sign: Sign

def normalize_deg(deg: float) -> float:
    return deg % 360.0

def get_sign_from_lon(lon: float) -> Sign:
    idx = int(lon / 30)
    return list(Sign)[idx]

def calculate_antiscia_points(longitude: float) -> AntisciaPoint:
    """
    Calculates the Antiscia (Solstice Reflection) and Contra-Antiscia (Equinox Reflection).
    Formula: Antiscia = (180 - longitude) % 360
    Contra = (Antiscia + 180) % 360
    """
    antiscia = normalize_deg(180.0 - longitude)
    contra_antiscia = normalize_deg(antiscia + 180.0)
    
    return AntisciaPoint(
        original_lon=longitude,
        antiscia_lon=antiscia,
        contra_antiscia_lon=contra_antiscia,
        antiscia_sign=get_sign_from_lon(antiscia),
        contra_antiscia_sign=get_sign_from_lon(contra_antiscia)
    )

def check_antiscia_aspect(p1_lon: float, p1_name: PlanetName, p2_lon: float, p2_name: PlanetName) -> Optional[Dict]:
    """
    Checks if Planet 2 is conjunct the Antiscion or Contra-Antiscion of Planet 1.
    Uses strict 'Moiety' orbs as per Lilly.
    """
    shadows = calculate_antiscia_points(p1_lon)
    
    # Get Moieties (Orbs)
    orb1 = MOIETIES.get(p1_name, 5.0) 
    orb2 = MOIETIES.get(p2_name, 5.0)
    mean_orb = (orb1 + orb2) / 2.0
    
    # Check CONJUNCTION to ANTISCIA
    dist_ant = abs(p2_lon - shadows.antiscia_lon)
    if dist_ant > 180: dist_ant = 360 - dist_ant
    
    if dist_ant <= mean_orb:
        return {
            "type": "Antiscia",
            "quality": "Hidden Support",
            "orb": dist_ant,
            "exact": dist_ant <= 1.0
        }
        
    # Check CONJUNCTION to CONTRA-ANTISCIA
    dist_contra = abs(p2_lon - shadows.contra_antiscia_lon)
    if dist_contra > 180: dist_contra = 360 - dist_contra
    
    if dist_contra <= mean_orb:
        return {
            "type": "Contra-Antiscia",
            "quality": "Hidden Friction",
            "orb": dist_contra,
            "exact": dist_contra <= 1.0
        }
        
    return None

# ==========================================
# 2. DODECATEMORIA (Twelfth-Parts)
# ==========================================

@dataclass
class Dodecatemorion:
    method: Literal["Valens", "Paul"]
    longitude: float
    sign: Sign
    term_ruler: str
    term_nature: str 
    
def get_egyptian_term_ruler(lon: float) -> str:
    sign_idx = int(lon / 30)
    sign = list(Sign)[sign_idx]
    deg_in_sign = lon % 30
    
    terms = EGYPTIAN_TERMS.get(sign, [])
    for ruler, limit in terms:
        if deg_in_sign < limit:
            return ruler.value
    return "Unknown"

def calculate_dodecatemorion(longitude: float, method: Literal["Valens", "Paul"] = "Valens") -> Dodecatemorion:
    sign_idx = int(longitude / 30)
    sign_start = sign_idx * 30.0
    deg_in_sign = longitude % 30.0
    
    multiplier = 12.0 if method == "Valens" else 13.0
    
    projected_arc = deg_in_sign * multiplier
    abs_dodec = normalize_deg(sign_start + projected_arc)
    
    term_ruler = get_egyptian_term_ruler(abs_dodec)
    
    return Dodecatemorion(
        method=method,
        longitude=abs_dodec,
        sign=get_sign_from_lon(abs_dodec),
        term_ruler=term_ruler,
        term_nature="Neutral"
    )

# ==========================================
# 3. PLANETARY DAYS & HOURS (Chronocrators)
# ==========================================

@dataclass
class PlanetaryHourInfo:
    day_of_week: str
    day_lord: str
    hour_lord: str
    hour_number: int  # 1-24
    is_daytime: bool
    radicality: str
    night_lord: str

CHALDEAN_ORDER = [
    PlanetName.SATURN,
    PlanetName.JUPITER,
    PlanetName.MARS,
    PlanetName.SUN,
    PlanetName.VENUS,
    PlanetName.MERCURY,
    PlanetName.MOON
]

def calculate_planetary_hours(dt: datetime, lat: float, lon: float, asc_sign: Sign = None, asc_lord: str = None) -> PlanetaryHourInfo:
    """
    Calculates the Planetary Hour and Radicality using the Unequal/Temporal Hour method.
    Requires accurate Sunrise/Sunset from Swiss Ephemeris.
    """
    
    # 1. Astro Calculations
    # jd is UTC
    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0 + dt.second/3600.0)
    
    geopos = (lon, lat, 0)
    
    # Rise/Set flags
    # We want Upper Limb rising. swe.FLG_SWIEPH
    
    # Search for events around the specific day
    # Strategy: Collect a sequence of events over 48 hours.
    
    start_search = jd - 1.5
    
    events = []
    # Collect 4 rises and 4 sets starting from start_search
    
    t_iter = start_search
    for _ in range(4):
        # Find next rise (rsmi=0)
        # Signature: (tjd, body, rsmi, geopos, press, temp, flags)
        res = swe.rise_trans(t_iter, swe.SUN, 0, geopos, 0, 0, swe.FLG_SWIEPH)
        t_rise = res[1][0]
        events.append(('rise', t_rise))
        
        # Find next set (rsmi=1)
        res = swe.rise_trans(t_iter, swe.SUN, 1, geopos, 0, 0, swe.FLG_SWIEPH)
        t_set = res[1][0]
        events.append(('set', t_set))
        
        # Advance iterator
        t_iter = min(t_rise, t_set) + (1.0/24.0) 
        
    # Sort events by time
    events.sort(key=lambda x: x[1])
    
    # Filter duplicates (if any) and invalid times
    unique_events = []
    last_t = -1.0
    for etype, t in events:
        if t > last_t + 0.001: # 1.5 min threshold
            unique_events.append((etype, t))
            last_t = t
            
    events = unique_events
    
    # Now find where JD sits
    past_events = [e for e in events if e[1] <= jd]
    
    if not past_events:
        return None 
        
    last_event = past_events[-1]
    
    if last_event[0] == 'rise':
        is_day = True
        period_start = last_event[1]
        future_events = [e for e in events if e[1] > jd and e[0] == 'set']
        period_end = future_events[0][1] if future_events else jd + 0.5
        
        # Astrological Day determination
        # Weekday: (JD + 1.5) % 7. 0=Sun
        day_idx = int((period_start + 1.5) % 7) 
        
    else: # Last event was Set
        is_day = False
        period_start = last_event[1]
        future_events = [e for e in events if e[1] > jd and e[0] == 'rise']
        period_end = future_events[0][1] if future_events else jd + 0.5
        
        # Astrological Day is the day of the PREVIOUS Rise
        prev_rises = [e for e in past_events if e[0] == 'rise']
        if prev_rises:
             t_rise_prev = prev_rises[-1][1]
        else:
             # Fallback call if not found in list (shouldn't happen with adequate search range)
             res = swe.rise_trans(period_start - 0.5, swe.SUN, 0, geopos, 0, 0, swe.FLG_SWIEPH)
             t_rise_prev = res[1][0]
             
        day_idx = int((t_rise_prev + 1.5) % 7)

    # Standardize Rulership Map (0=Sunday)
    RULERS = {
        0: PlanetName.SUN,
        1: PlanetName.MOON,
        2: PlanetName.MARS,
        3: PlanetName.MERCURY,
        4: PlanetName.JUPITER,
        5: PlanetName.VENUS,
        6: PlanetName.SATURN
    }
    day_lord = RULERS[day_idx]

    # Calculate Hour
    duration = period_end - period_start
    hour_length = duration / 12.0
    elapsed = jd - period_start
    hour_idx_12 = int(elapsed / hour_length) + 1
    if hour_idx_12 > 12: hour_idx_12 = 12
    
    # Absolute Hour (1-24)
    abs_hour = hour_idx_12 if is_day else (hour_idx_12 + 12)
    
    # Chaldean Mapping
    start_idx = CHALDEAN_ORDER.index(day_lord)
    
    # Sequence
    steps = abs_hour - 1
    current_idx = (start_idx + steps) % 7
    hour_lord = CHALDEAN_ORDER[current_idx]
    
    # Night Lord (Ruler of Hour 13)
    night_lord_idx = (start_idx + 12) % 7
    night_lord = CHALDEAN_ORDER[night_lord_idx]
    
    # Radicality Check
    radicality = "Unknown"
    if asc_lord:
        if hour_lord == PlanetName(asc_lord):
            radicality = "Radical (Identity)"
        elif asc_sign:
            radicality = "Caution (No Identity)"
        else:
            radicality = "Caution (No Identity)"
            
    return PlanetaryHourInfo(
        day_of_week=day_lord.value + "'s Day",
        day_lord=day_lord.value,
        hour_lord=hour_lord.value,
        hour_number=abs_hour,
        is_daytime=is_day,
        radicality=radicality,
        night_lord=night_lord.value
    )


# ==========================================
# 4. HELPER EXPORT
# ==========================================
class ClassicalMechanicsEngine:
    @staticmethod
    def get_antiscia(longitude: float) -> AntisciaPoint:
        return calculate_antiscia_points(longitude)
        
    @staticmethod
    def get_dodecatemorion(longitude: float, method="Valens") -> Dodecatemorion:
        return calculate_dodecatemorion(longitude, method)
    
    @staticmethod
    def get_planetary_hours(dt: datetime, lat: float, lon: float, asc_sign: Sign = None, asc_lord: str = None) -> PlanetaryHourInfo:
        return calculate_planetary_hours(dt, lat, lon, asc_sign, asc_lord)
        
    @staticmethod
    def check_shadow_aspects(chart_planets: List[Planet]) -> List[Dict]:
        results = []
        for i, p1 in enumerate(chart_planets):
            for j, p2 in enumerate(chart_planets):
                if i >= j: continue 
                aspect = check_antiscia_aspect(p1.longitude, p1.name, p2.longitude, p2.name)
                if aspect:
                    results.append({
                        "planet_1": p1.name.value,
                        "planet_2": p2.name.value,
                        "type": aspect["type"],
                        "quality": aspect["quality"],
                        "orb": round(aspect["orb"], 2),
                        "partile": aspect["exact"]
                    })
        return results
