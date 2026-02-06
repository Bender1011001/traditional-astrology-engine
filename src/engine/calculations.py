from typing import Tuple
from .models import Planet, PlanetName, Sect, Sign, Chart
def calculate_sect(sun_altitude: float) -> Sect:
    return Sect.DAY if sun_altitude > 0 else Sect.NIGHT


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

def calculate_prenatal_syzygy(jd_utc: float) -> tuple[float, str]:
    """
    Finds the position of the SAN (Syzygy Ante Nativitatem) using Iterative Newton-Raphson method.
    Resolves to True Syzygy within acceptable tolerance (< 1 sec).
    Returns (longitude, type) where type is "New" or "Full".
    """
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    
    # 1. Determine Target from Birth chart
    res_sun = swe.calc_ut(jd_utc, swe.SUN, flags)
    res_moon = swe.calc_ut(jd_utc, swe.MOON, flags)
    
    s_l = res_sun[0][0]
    m_l = res_moon[0][0]
    
    phase = (m_l - s_l) % 360.0
    
    if phase < 180:
        target_type = "New"
        target_angle = 0.0
    else:
        target_type = "Full"
        target_angle = 180.0
        
    # 2. Newton-Raphson Search
    t = jd_utc
    # Initial guess: approximate backward by phase diff
    # Avg rel speed ~12.19 deg/day
    diff_est = phase - target_angle
    if diff_est < 0: diff_est += 360
    t -= (diff_est / 12.19)
    
    for _ in range(15):
        r_sun = swe.calc_ut(t, swe.SUN, flags)
        r_moon = swe.calc_ut(t, swe.MOON, flags)
        
        s_l, s_v = r_sun[0][0], r_sun[0][3]
        m_l, m_v = r_moon[0][0], r_moon[0][3]
        
        curr_phase = (m_l - s_l) % 360.0
        
        # Delta = Current - Target
        delta = curr_phase - target_angle
        
        # Unwrap
        if delta > 180: delta -= 360
        if delta < -180: delta += 360
        
        if abs(delta) < 0.00001:
            # Result
            final_lon = m_l if target_type == "Full" else s_l
            return (final_lon, target_type)
        
        v_rel = m_v - s_v
        t -= (delta / v_rel)
        
    return (s_l, target_type)

def calculate_solar_status(planet: Planet, sun: Planet) -> str:
    diff = abs(planet.longitude - sun.longitude)
    if diff > 180: diff = 360 - diff
    
    if diff < 0.28: # 17 minutes
        return "CAZIMI"
    if diff < 8.0:
        return "COMBUST"
    if diff < 15.0:
        return "UNDER_BEAMS"
    return "FREE"

def is_in_via_combusta(longitude: float) -> bool:
    """
    Via Combusta (The Burning Way): 15° Libra to 15° Scorpio (195° to 225°).
    """
    return 195.0 <= longitude <= 225.0

def is_besieged(planet: Planet, chart: Chart) -> bool:
    mars = next((p for p in chart.planets if p.name == PlanetName.MARS), None)
    saturn = next((p for p in chart.planets if p.name == PlanetName.SATURN), None)
    
    if not mars or not saturn or planet.name in [PlanetName.MARS, PlanetName.SATURN]:
        return False
        
    def get_shortest_arc(p1_lon, p2_lon):
        diff = p1_lon - p2_lon
        if diff > 180: diff -= 360
        if diff < -180: diff += 360
        return diff
    
    dist_mars = get_shortest_arc(planet.longitude, mars.longitude)
    dist_saturn = get_shortest_arc(planet.longitude, saturn.longitude)
    
    # Check if between
    if (dist_mars * dist_saturn < 0) and (abs(dist_mars) + abs(dist_saturn) < 15):
        return True
    return False

def is_void_of_course(moon_lon: float, chart_planets: list[Planet]) -> bool:
    """
    Bonatti Consideration 5: Void of Course Moon.
    Simplified: No major aspect before leaving the sign (30° boundary).
    """
    moon_sign_idx = int(moon_lon / 30)
    moon_pos_in_sign = moon_lon % 30
    dist_to_end = 30 - moon_pos_in_sign
    
    major_aspects = [0, 60, 90, 120, 180]
    
    for p in chart_planets:
        if p.name == PlanetName.MOON: continue
        
        for aspect in major_aspects:
            for sign_mult in [-1, 1]:
                target_lon = (p.longitude + (sign_mult * aspect)) % 360
                dist_to_target = (target_lon - moon_lon) % 360
                
                # Check if this target is reached by forward motion within the sign
                if dist_to_target < dist_to_end:
                    return False 
    return True
