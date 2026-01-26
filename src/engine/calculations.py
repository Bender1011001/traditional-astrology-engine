from .models import Planet, PlanetName, Sect, Sign, Chart
from .reference_data import (
    DOMICILES, EXALTATIONS, FALLS, DETRIMENTS, 
    TRIPLICITY_RULERS, SIGN_ELEMENTS, EGYPTIAN_TERMS, FACES_ORDER
)

def calculate_sect(sun_altitude: float) -> Sect:
    return Sect.DAY if sun_altitude > 0 else Sect.NIGHT

def get_triplicity_ruler(sign: Sign, sect: Sect) -> PlanetName:
    element = SIGN_ELEMENTS[sign]
    return TRIPLICITY_RULERS[element][sect]

def get_term_ruler(sign: Sign, degree: float) -> PlanetName:
    terms = EGYPTIAN_TERMS[sign]
    for planet, upper_bound in terms:
        if degree < upper_bound:
            return planet
    return terms[-1][0] # Should not happen if degree < 30

def get_face_ruler(sign: Sign, degree: float) -> PlanetName:
    # Faces are 0-10, 10-20, 20-30
    face_idx = int(degree // 10)
    if face_idx > 2: face_idx = 2 # Handle exactly 30?
    
    # Calculate index in FACES_ORDER
    # Aries is 0, 1, 2. Taurus is 3, 4, 5...
    sign_list = list(Sign)
    sign_idx = sign_list.index(sign)
    global_face_idx = (sign_idx * 3) + face_idx
    return FACES_ORDER[global_face_idx % len(FACES_ORDER)]

def calculate_dignity_score(planet: Planet, chart_sect: Sect) -> tuple[int, list[str]]:
    """
    Returns (net_score, breakdown_list)
    """
    score = 0
    breakdown = []
    
    pf = planet.name
    sign = planet.sign
    deg = planet.degree_in_sign
    
    # Positive Dignities
    has_dignity = False
    
    if DOMICILES[sign] == pf:
        score += 5
        breakdown.append("Domicile (+5)")
        has_dignity = True
        
    if EXALTATIONS.get(sign) == pf:
        score += 4
        breakdown.append("Exaltation (+4)")
        has_dignity = True
        
    if get_triplicity_ruler(sign, chart_sect) == pf:
        score += 3
        breakdown.append("Triplicity (+3)")
        has_dignity = True
        
    if get_term_ruler(sign, deg) == pf:
        score += 2
        breakdown.append("Term (+2)")
        has_dignity = True
        
    if get_face_ruler(sign, deg) == pf:
        score += 1
        breakdown.append("Face (+1)")
        has_dignity = True
        
    # Negative Dignities
    if DETRIMENTS.get(sign) == pf:
        score -= 5
        breakdown.append("Detriment (-5)")
        
    if FALLS.get(sign) == pf:
        score -= 4
        breakdown.append("Fall (-4)")
        
    # Peregrine Check
    if not has_dignity:
        # Note: Some definitions say not peregrine if in mutual reception etc, but we stick to strict essential dignity here
        score -= 5
        breakdown.append("Peregrine (-5)")
        
    return score, breakdown

def calculate_solar_proximity(planet: Planet, sun: Planet) -> str:
    if planet.name == PlanetName.SUN:
        return "N/A"
        
    # Simple distance calculation (ignoring 360 wrap logic for simplicity for now, but should fix)
    dist = abs(planet.longitude - sun.longitude)
    if dist > 180:
        dist = 360 - dist
        
    if dist < (17/60): # 0 degrees 17 minutes
        return "CAZIMI"
    elif dist <= 8:
        return "COMBUST"
    elif dist <= 15:
        return "UNDER_BEAMS"
    else:
        return "FREE"

def calculate_lunar_phase(sun_lon: float, moon_lon: float) -> tuple[str, str]:
    """
    Calculates the 8 Soli-Lunar phases and returns (Phase Name, Profile).
    Based on Dane Rudhyar's Cycle of Manifestation.
    """
    diff = (moon_lon - sun_lon) % 360
    
    phases = [
        (45, "New Moon", "The Primitive/The Initiator. Subjective, impulsive, seeding new impulses."),
        (90, "Crescent", "The Breakthrough/The Mobilizer. Struggle to manifest new forms against the past."),
        (135, "First Quarter", "The Builder/The Crisis-Actor. 'Crisis in Action' - building new structures."),
        (180, "Gibbous", "The Perfector/The Analyst. Refining and evaluating the work; seeking growth."),
        (225, "Full Moon", "The Realizer/The Objectifier. Objectivity, Relationship, and Revelation."),
        (270, "Disseminating", "The Teacher/The Demonstrator. Sharing realized vision and values."),
        (315, "Last Quarter", "The Revisor/The Crisis-Thinker. 'Crisis in Consciousness' - re-evaluating beliefs."),
        (360, "Balsamic", "The Prophet/The Seed-Man. Introverted, Future-Oriented, Distillation and Release.")
    ]
    
    for limit, name, profile in phases:
        if diff < limit:
            return name, profile
            
    return "New Moon", "The Primitive/The Initiator. Subjective, impulsive, seeding new impulses."

import swisseph as swe

def calculate_prenatal_syzygy(jd: float) -> float:
    """
    Finds the longitude of the last New Moon or Full Moon before the given JD.
    Uses iterative refinement for precision.
    """
    curr_jd = jd
    
    def get_phase_diff(t):
        res_s = swe.calc_ut(t, swe.SUN, swe.FLG_SWIEPH)
        res_m = swe.calc_ut(t, swe.MOON, swe.FLG_SWIEPH)
        return (res_m[0][0] - res_s[0][0]) % 360

    # 1. Broad search: check every 2 hours going back for 31 days
    step = 2.0 / 24.0
    prev_jd = curr_jd
    found_jd = None
    
    for _ in range(int(31 / step)):
        t1 = curr_jd - step
        d1 = get_phase_diff(t1)
        d_curr = get_phase_diff(curr_jd)
        
        # New Moon crossing (near 0)
        # Check if 0 is between d1 and d_curr
        # Since it wraps, if d_curr < d1 and d1 > 350, it crossed 0.
        if (d_curr < d1 and d1 > 350) or (d_curr < 180 and d1 > 180) or (d_curr > 180 and d1 < 180):
            # Crossing found between t1 and curr_jd
            found_jd = (t1, curr_jd)
            break
        curr_jd = t1

    if not found_jd:
        # Fallback to current sun position if not found (shouldn't happen)
        return swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)[0][0]

    # 2. Refine (Binary search for crossing)
    low, high = found_jd
    for _ in range(15):
        mid = (low + high) / 2
        d_mid = get_phase_diff(mid)
        # We target 0 or 180
        # If we were looking for NM (near 0)
        target = 0 if abs(get_phase_diff(high) - 0) < 90 or abs(get_phase_diff(high) - 360) < 90 else 180
        
        if target == 0:
            if d_mid > 180: # Wrapped
                low = mid
            else:
                high = mid
        else:
            if d_mid < 180:
                low = mid
            else:
                high = mid
                
    # Final longitude
    res = swe.calc_ut(high, swe.SUN, swe.FLG_SWIEPH)
    return res[0][0]
