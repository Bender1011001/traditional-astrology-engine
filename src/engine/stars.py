from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
import math
import swisseph as swe
from .models import Planet, Chart, PlanetName

FIXED_STAR_EPOCH = 2025
FIXED_STAR_CATALOG = "Swiss Ephemeris fixed star catalog (swe.fixstar) when available; fallback to traditional longitudes."
FIXED_STAR_PRECESSION = "Swiss Ephemeris JD positions when available; fallback linear precession of 1° per 72 years from 2025 epoch."

@dataclass
class FixedStar:
    name: str
    longitude: float # 2025 Epoch
    nature: str
    magnitude: int
    glory: str = ""
    nemesis: str = ""
    orb: float = 1.0
    swe_name: Optional[str] = None

# 2025 Coordinates and forensic meanings derived from Binder1_part_030.txt
STARS = [
    FixedStar(
        name="Aldebaran", 
        longitude=70.133, # 10°08' Gemini
        nature="Mars", 
        magnitude=1, 
        glory="Integrity, Honor, Moral Courage",
        nemesis="Compromise of Integrity; Ruin through dishonesty",
        swe_name="Aldebaran"
    ),
    FixedStar(
        name="Regulus", 
        longitude=150.167, # 00°10' Virgo
        nature="Mars/Jupiter", 
        magnitude=1, 
        glory="Power, Command, Nobility",
        nemesis="Revenge; Total fall from grace due to pettiness",
        swe_name="Regulus"
    ),
    FixedStar(
        name="Antares", 
        longitude=250.100, # 10°06' Sagittarius
        nature="Mars/Jupiter", 
        magnitude=1, 
        glory="Intensity, Bravery, Strategic Genius",
        nemesis="Obsession; Self-destruction through mania",
        swe_name="Antares"
    ),
    FixedStar(
        name="Fomalhaut", 
        longitude=334.200, # 04°12' Pisces
        nature="Venus/Mercury", 
        magnitude=1, 
        glory="Charisma, Artistic/Spiritual Legacy",
        nemesis="Corruption of Ideals; Dreaming without doing",
        swe_name="Fomalhaut"
    ),
    FixedStar(
        name="Caput Algol", 
        longitude=56.500, # 26°30' Taurus
        nature="Saturn/Mars", 
        magnitude=2, 
        orb=2.5,
        glory="None (Pure Malefic)",
        nemesis="Losing one's head, beheading, extreme violence",
        swe_name="Algol"
    ),
    FixedStar(
        name="Spica", 
        longitude=204.067, # ~24 Libra (Adjusted for 2025)
        nature="Venus/Mars", 
        magnitude=1, 
        glory="Success through art, diplomacy, and intellect",
        nemesis="None (Pure Benefic)",
        swe_name="Spica"
    ),
]

def get_fixed_star_meta() -> Dict[str, str]:
    return {
        "catalog": FIXED_STAR_CATALOG,
        "epoch": str(FIXED_STAR_EPOCH),
        "precession": FIXED_STAR_PRECESSION
    }

@dataclass
class StarContact:
    star_name: str
    planet_name: str
    contact_type: str # "CONJUNCTION" or "PARAN"
    angle: Optional[str] = None
    message: str = ""

def get_shortest_dist(a: float, b: float) -> float:
    d = abs(a - b)
    if d > 180: d = 360 - d
    return d

def _normalize_deg(deg: float) -> float:
    return deg % 360.0

def _get_obliquity_deg(jd: Optional[float]) -> float:
    if jd is None:
        return 23.4392911
    try:
        res = swe.calc_ut(jd, swe.ECL_NUT)
        coords = res[0] if isinstance(res[0], (list, tuple)) else res
        if isinstance(coords, (list, tuple)) and len(coords) > 1:
            return coords[1]
        if isinstance(coords, (list, tuple)) and coords:
            return coords[0]
    except Exception:
        pass
    return 23.4392911

def _equatorial_to_ecliptic(ra: float, dec: float, epsilon: float) -> Tuple[float, float]:
    ra_r = math.radians(ra)
    dec_r = math.radians(dec)
    eps_r = math.radians(epsilon)

    sin_beta = math.sin(dec_r) * math.cos(eps_r) - math.cos(dec_r) * math.sin(eps_r) * math.sin(ra_r)
    beta = math.asin(sin_beta)

    y = math.sin(ra_r) * math.cos(eps_r) + math.tan(dec_r) * math.sin(eps_r)
    x = math.cos(ra_r)
    lam = math.atan2(y, x)

    return (_normalize_deg(math.degrees(lam)), math.degrees(beta))

def _ecliptic_to_equatorial(lon: float, lat: float, epsilon: float) -> Tuple[float, float]:
    lon_r = math.radians(lon)
    lat_r = math.radians(lat)
    eps_r = math.radians(epsilon)

    sin_dec = math.sin(eps_r) * math.sin(lon_r) * math.cos(lat_r) + math.cos(eps_r) * math.sin(lat_r)
    dec_r = math.asin(sin_dec)
    y = math.sin(lon_r) * math.cos(eps_r) - math.tan(lat_r) * math.sin(eps_r)
    x = math.cos(lon_r)
    ra_r = math.atan2(y, x)
    return (_normalize_deg(math.degrees(ra_r)), math.degrees(dec_r))

def _year_from_jd(jd: Optional[float]) -> Optional[int]:
    if jd is None:
        return None
    y, m, d, h = swe.revjul(jd)
    return int(y)

def _precess_longitude(lon_2025: float, jd: Optional[float]) -> float:
    year = _year_from_jd(jd)
    if year is None:
        return lon_2025
    delta_years = year - FIXED_STAR_EPOCH
    return _normalize_deg(lon_2025 + (delta_years / 72.0))

def _get_star_equatorial(star: FixedStar, jd: Optional[float]) -> Optional[Tuple[float, float]]:
    if jd is None or not star.swe_name:
        return None
    try:
        res = swe.fixstar(star.swe_name, jd)
        coords = res[1] if isinstance(res[1], (list, tuple)) else res[0]
        ra = coords[0]
        dec = coords[1]
        return (ra, dec)
    except Exception:
        return None

def _get_star_longitude(star: FixedStar, jd: Optional[float]) -> float:
    ra_dec = _get_star_equatorial(star, jd)
    if ra_dec:
        epsilon = _get_obliquity_deg(jd)
        lon, _ = _equatorial_to_ecliptic(ra_dec[0], ra_dec[1], epsilon)
        return lon
    return _precess_longitude(star.longitude, jd)

def get_star_longitude(star: FixedStar, jd: Optional[float]) -> float:
    return _get_star_longitude(star, jd)

def _angles_for_body(ra: float, dec: float, ramc: float, lat: float, orb: float) -> List[str]:
    hits = []
    ha = (ramc - ra + 540.0) % 360.0 - 180.0

    if abs(ha) <= orb:
        hits.append("MC")
    if abs(abs(ha) - 180.0) <= orb:
        hits.append("IC")

    try:
        cos_h = -math.tan(math.radians(lat)) * math.tan(math.radians(dec))
    except Exception:
        cos_h = 2.0
    if -1.0 <= cos_h <= 1.0:
        h = math.degrees(math.acos(cos_h))
        if abs(ha - (-h)) <= orb:
            hits.append("ASC")
        if abs(ha - h) <= orb:
            hits.append("DSC")

    return hits

def calculate_parans(chart: Chart) -> List[StarContact]:
    """
    Detects stars rising, culminating, setting, or on the IC simultaneously with planets or angles.
    As per Binder1_part_030.txt, Parans prioritize visual synchronization over ecliptic longitude.
    """
    parans = []
    if chart.geo_lat is None or chart.jd is None:
        return parans

    orb = 2.0
    epsilon = _get_obliquity_deg(chart.jd)

    # RAMC from MC (MC is ecliptic longitude)
    ramc, _ = _ecliptic_to_equatorial(chart.mc, 0.0, epsilon)

    # Planet angle hits
    planet_hits = {}
    for planet in chart.planets:
        ra_p, dec_p = _ecliptic_to_equatorial(planet.longitude, planet.latitude, epsilon)
        hits = _angles_for_body(ra_p, dec_p, ramc, chart.geo_lat, orb)
        if hits:
            planet_hits[planet.name.value] = hits

    if not planet_hits:
        return parans

    for star in STARS:
        ra_dec = _get_star_equatorial(star, chart.jd)
        if not ra_dec:
            continue
        s_hits = _angles_for_body(ra_dec[0], ra_dec[1], ramc, chart.geo_lat, orb)
        if not s_hits:
            continue

        for p_name, p_hits in planet_hits.items():
            for s_angle in s_hits:
                for p_angle in p_hits:
                    msg = (
                        f"PARAN: {star.name} is on {s_angle} while {p_name} is on {p_angle}. "
                        f"Eminence Indicator. Nature: {star.nature}. Glory: {star.glory}."
                    )
                    parans.append(StarContact(
                        star_name=star.name,
                        planet_name=p_name,
                        contact_type="PARAN",
                        angle=s_angle,
                        message=msg
                    ))

    return parans

def check_fixed_stars(chart: Chart) -> List[StarContact]:
    """
    Main entry point for stellar analysis. 
    Prioritizes Parans over ecliptic conjunctions for eminence, rank, and wealth indicators.
    """
    all_contacts = []
    
    # 1. Calculate Parans (Higher Priority)
    parans = calculate_parans(chart)
    all_contacts.extend(parans)
    
    # 2. Check Ecliptic Conjunctions
    paran_pairs = set((p.star_name, p.planet_name) for p in parans)
    
    for planet in chart.planets:
        p_long = planet.longitude
        p_name = planet.name.value
        
        for star in STARS:
            star_lon = _get_star_longitude(star, chart.jd)
            dist = get_shortest_dist(p_long, star_lon)
            if dist <= star.orb:
                # Skip if already identified as a Paran (to avoid redundancy, but note conjunction is still valid)
                contact_type = "CONJUNCTION"
                msg = f"CONJUNCT {star.name} (Orb: {dist:.2f}°). Nature: {star.nature}. Nemesis: {star.nemesis}."
                
                all_contacts.append(StarContact(
                    star_name=star.name,
                    planet_name=p_name,
                    contact_type=contact_type,
                    message=msg
                ))
                
    # 3. Check Angles (Asc/MC) for direct star presence
    angles = {"Ascendant": chart.ascendant, "Midheaven": chart.mc}
    for angle_name, angle_long in angles.items():
        for star in STARS:
            star_lon = _get_star_longitude(star, chart.jd)
            dist = get_shortest_dist(angle_long, star_lon)
            if dist <= star.orb:
                all_contacts.append(StarContact(
                    star_name=star.name,
                    planet_name=angle_name,
                    contact_type="ANGULAR_PRESENCE",
                    message=f"STAR ON {angle_name.upper()}: {star.name}. Glory: {star.glory}. Nemesis: {star.nemesis}."
                ))
                
    # 4. Antares-Aldebaran Axis Alert (Violent Potential)
    # As per Binder1_part_028.txt:
    # Moon/Mars on this axis (opposite stars) signifies violent death potential.
    aldebaran = next((s for s in STARS if s.name == "Aldebaran"), None)
    antares = next((s for s in STARS if s.name == "Antares"), None)
    
    if aldebaran and antares:
        for p_name_target in [PlanetName.MOON, PlanetName.MARS]:
            planet = next((p for p in chart.planets if p.name == p_name_target), None)
            if planet:
                # Check conjunction with either star
                al_lon = _get_star_longitude(aldebaran, chart.jd)
                an_lon = _get_star_longitude(antares, chart.jd)
                on_aldebaran = get_shortest_dist(planet.longitude, al_lon) <= aldebaran.orb
                on_antares = get_shortest_dist(planet.longitude, an_lon) <= antares.orb
                
                if on_aldebaran or on_antares:
                    msg = (
                        f"CRITICAL AXIS ALERT: {p_name_target.value} is on the Antares-Aldebaran axis. "
                        "Signifies violent potential / cosmic tension between integrity and obsession. "
                        "Traditionally associated with violent death by the sword or hanging."
                    )
                    all_contacts.append(StarContact(
                        star_name="Antares-Aldebaran Axis",
                        planet_name=p_name_target.value,
                        contact_type="AXIS_ALERT",
                        message=msg
                    ))

    return all_contacts
