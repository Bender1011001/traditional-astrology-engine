from typing import Tuple
from .models import Planet, PlanetName, Sect, Sign, Chart


def format_longitude(lon: float) -> dict:
    """
    Standard longitude formatter to avoid mixing absolute longitude with sign-degree notation.

    Returns both:
    - absolute longitude in [0,360)
    - sign name
    - degree within sign + minutes/seconds
    - a human-friendly string (e.g., "Leo 06°16'57\"")
    """
    lon_abs = float(lon) % 360.0
    sign_idx = int(lon_abs / 30.0) % 12
    sign = list(Sign)[sign_idx].value
    deg_in_sign = lon_abs % 30.0

    deg = int(deg_in_sign)
    minutes_full = (deg_in_sign - deg) * 60.0
    minute = int(minutes_full)
    second = int(round((minutes_full - minute) * 60.0))
    if second == 60:
        second = 0
        minute += 1
    if minute == 60:
        minute = 0
        deg += 1
        if deg == 30:
            deg = 0

    s = f"{sign} {deg:02d}°{minute:02d}'{second:02d}\""
    return {
        "lon_abs": lon_abs,
        "sign": sign,
        "deg_in_sign": round(deg_in_sign, 6),
        "dms": {"deg": deg, "min": minute, "sec": second},
        "string": s,
    }
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
    details = calculate_prenatal_syzygy_details(jd_utc)
    return (float(details["longitude"]), str(details["type"]))


def calculate_prenatal_syzygy_details(jd_utc: float) -> dict:
    """
    Auditable prenatal syzygy (SAN) finder.

    Returns a dict including:
    - type: "New"|"Full"
    - jd_ut: JD (UT) of the syzygy
    - longitude: ecliptic longitude for the syzygy degree (Sun for New; Moon for Full)
    - sun_longitude, moon_longitude at syzygy
    - note

    Also includes the "next syzygy after birth" for phase disambiguation.
    """
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED

    # 1) Determine which syzygy precedes birth (waxing => last was New; waning => last was Full)
    res_sun = swe.calc_ut(jd_utc, swe.SUN, flags)
    res_moon = swe.calc_ut(jd_utc, swe.MOON, flags)
    s_l = float(res_sun[0][0])
    m_l = float(res_moon[0][0])
    phase = (m_l - s_l) % 360.0

    if phase < 180.0:
        prenatal_type = "New"
        prenatal_target_angle = 0.0
        next_type = "Full"
        next_target_angle = 180.0
    else:
        prenatal_type = "Full"
        prenatal_target_angle = 180.0
        next_type = "New"
        next_target_angle = 0.0

    def _solve_syzygy(t_guess: float, target_angle: float) -> tuple[float, float, float]:
        """
        Newton-Raphson solve for (Moon-Sun) phase == target_angle.
        Returns (jd_ut, sun_lon, moon_lon).
        """
        t = float(t_guess)
        for _ in range(20):
            r_sun = swe.calc_ut(t, swe.SUN, flags)
            r_moon = swe.calc_ut(t, swe.MOON, flags)
            sun_lon = float(r_sun[0][0])
            sun_spd = float(r_sun[0][3])
            moon_lon = float(r_moon[0][0])
            moon_spd = float(r_moon[0][3])

            curr_phase = (moon_lon - sun_lon) % 360.0
            delta = curr_phase - target_angle
            if delta > 180.0:
                delta -= 360.0
            if delta < -180.0:
                delta += 360.0

            if abs(delta) < 0.00001:
                return (t, sun_lon, moon_lon)

            v_rel = moon_spd - sun_spd
            if abs(v_rel) < 1e-6:
                break
            t -= (delta / v_rel)
        return (t, sun_lon, moon_lon)

    # 2) Prenatal solve: back up by an approximate amount based on the current phase offset.
    diff_est = (phase - prenatal_target_angle) % 360.0
    t0 = jd_utc - (diff_est / 12.19)  # avg relative speed deg/day
    pre_jd, pre_sun, pre_moon = _solve_syzygy(t0, prenatal_target_angle)
    pre_lon = pre_sun if prenatal_type == "New" else pre_moon

    # 3) Next syzygy after birth: move forward by the complementary offset.
    diff_est_next = (next_target_angle - phase) % 360.0
    t1 = jd_utc + (diff_est_next / 12.19)
    next_jd, next_sun, next_moon = _solve_syzygy(t1, next_target_angle)
    next_lon = next_sun if next_type == "New" else next_moon

    return {
        "type": prenatal_type,
        "jd_ut": round(float(pre_jd), 8),
        "sun_longitude": round(float(pre_sun), 6),
        "moon_longitude": round(float(pre_moon), 6),
        "longitude": round(float(pre_lon), 6),
        "next_syzygy": {
            "type": next_type,
            "jd_ut": round(float(next_jd), 8),
            "sun_longitude": round(float(next_sun), 6),
            "moon_longitude": round(float(next_moon), 6),
            "longitude": round(float(next_lon), 6),
        },
        "note": "Computed by Newton-Raphson solve for (Moon-Sun) phase == 0°/180° (syzygy) preceding birth; also includes the next syzygy after birth for phase disambiguation.",
    }

def calculate_solar_status(planet: Planet, sun: Planet) -> str:
    # The Sun cannot be "cazimi" (it is the reference body).
    if planet.name == PlanetName.SUN:
        return "SUN"

    diff = abs(planet.longitude - sun.longitude)
    if diff > 180: diff = 360 - diff

    # Moon: treat near-Sun condition as lunation/visibility, not generic combustion doctrine.
    if planet.name == PlanetName.MOON:
        if diff < 8.0:
            return "DARK_MOON"
        if diff < 15.0:
            return "MOON_UNDER_BEAMS"
        return "FREE"

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
