import logging
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import swisseph as swe

from .models import Chart, PlanetName

logger = logging.getLogger(__name__)

FIXED_STAR_EPOCH = 2025
FIXED_STAR_CATALOG = "Swiss Ephemeris fixed star catalog (swe.fixstar) when available; fallback to traditional longitudes."
FIXED_STAR_PRECESSION = "Swiss Ephemeris JD positions when available; fallback linear precession of 1° per 72 years from 2025 epoch."
LOCAL_EPHE_DIR = Path(__file__).resolve().parents[1] / "ephe"
DEFAULT_EPHE_DIRS = (
    LOCAL_EPHE_DIR,
    Path("/usr/share/swisseph"),
    Path("/usr/local/share/swisseph"),
)
_FIXSTAR_CATALOG_AVAILABLE: Optional[bool] = None
_FIXSTAR_MISSING_LOGGED = False
_FIXSTAR_WARNED_STARS: set[str] = set()


def _configure_swisseph_ephe_path() -> str:
    existing = os.environ.get("SE_EPHE_PATH", "")
    path_parts: List[str] = [str(path) for path in DEFAULT_EPHE_DIRS]
    path_parts.extend(part for part in existing.split(os.pathsep) if part)

    deduped = list(dict.fromkeys(path_parts))
    ephe_path = os.pathsep.join(deduped)

    # Swiss Ephemeris ignores swe.set_ephe_path() if SE_EPHE_PATH is already
    # non-empty, so set both to the same explicit application path.
    os.environ["SE_EPHE_PATH"] = ephe_path
    swe.set_ephe_path(ephe_path)
    return ephe_path


SWISSEPH_EPHE_PATH = _configure_swisseph_ephe_path()


@dataclass
class FixedStar:
    name: str
    longitude: float  # 2025 Epoch
    nature: str
    magnitude: int
    glory: str = ""
    nemesis: str = ""
    orb: float = 1.0
    swe_name: Optional[str] = None
    mythology: Optional[str] = None


# Coordinates are resolved at the chart epoch through Swiss Ephemeris when
# available.  Interpretive catalog entries remain source-specific; do not blend
# a later star manual into Ptolemy without an explicit authority label.
STARS = [
    FixedStar(
        name="Alpheratz",
        longitude=14.317,  # 14°19' Aries
        nature="Jupiter/Venus",
        magnitude=2,
        glory="Independence, Freedom, Love of movement",
        nemesis="Restlessness, Lack of focus",
        swe_name="Alpheratz",
    ),
    FixedStar(
        name="Caput Algol",
        longitude=56.500,  # 26°30' Taurus
        nature="Jupiter/Saturn (Ptolemy: Perseus generally)",
        magnitude=2,
        orb=1.0,
        glory="Public prominence under the Jupiter-Saturn nature Ptolemy assigns to Perseus",
        nemesis="Ptolemy's violent Gorgon judgment requires Mars and anaretic conditions; angular contact alone does not establish it",
        swe_name="Algol",
        mythology="Medusa's Head",
    ),
    FixedStar(
        name="Alcyone",
        longitude=60.167,  # 00°10' Gemini
        nature="Mars/Moon",
        magnitude=3,
        glory="Visionary insight, Spiritual depth",
        nemesis="Blindness (physical or metaphorical), Sorrow",
        swe_name="Alcyone",
    ),
    FixedStar(
        name="Aldebaran",
        longitude=70.133,  # 10°08' Gemini
        nature="Mars",
        magnitude=1,
        glory="Integrity, Honor, Moral Courage",
        nemesis="Compromise of Integrity; Ruin through dishonesty",
        swe_name="Aldebaran",
    ),
    FixedStar(
        name="Capella",
        longitude=82.117,  # 22°07' Gemini
        nature="Mars/Mercury",
        magnitude=1,
        glory="Civic honors, Wealth, Public position",
        nemesis="Inquisitiveness, Wastefulness",
        swe_name="Capella",
    ),
    FixedStar(
        name="Rigel",
        longitude=77.100,  # 17°06' Gemini
        nature="Jupiter/Mars",
        magnitude=1,
        glory="Great fortune, Lasting honors, Inventive mind",
        nemesis="Arrogance, Recklessness",
        swe_name="Rigel",
    ),
    FixedStar(
        name="Bellatrix",
        longitude=81.117,  # 21°07' Gemini
        nature="Mars/Mercury",
        magnitude=2,
        glory="Military success, Quick decision making",
        nemesis="Sudden dishonor, Accidents",
        swe_name="Bellatrix",
    ),
    FixedStar(
        name="Sirius",
        longitude=104.333,  # 14°20' Cancer
        nature="Jupiter/Mars",
        magnitude=1,
        glory="Fame, Wealth, Guardianship",
        nemesis="Danger from dogs, Excessive heat/passion",
        swe_name="Sirius",
        mythology="The Dog Star",
    ),
    FixedStar(
        name="Castor",
        longitude=110.350,  # 20°21' Cancer
        nature="Mercury",
        magnitude=2,
        glory="Intellectual brilliance, Sharp wit",
        nemesis="Violence, Sudden loss",
        swe_name="Castor",
    ),
    FixedStar(
        name="Pollux",
        longitude=113.367,  # 23°22' Cancer
        nature="Mars",
        magnitude=1,
        glory="Bravery, Audacity, Protection",
        nemesis="Cruelty, Malice",
        swe_name="Pollux",
    ),
    FixedStar(
        name="Procyon",
        longitude=116.117,  # 26°07' Cancer
        nature="Mercury/Mars",
        magnitude=1,
        glory="Rapid success, Activity",
        nemesis="Sudden fall, Danger from bites",
        swe_name="Procyon",
    ),
    FixedStar(
        name="Regulus",
        longitude=150.167,  # 00°10' Virgo
        nature="Mars/Jupiter",
        magnitude=1,
        glory="Power, Command, Nobility",
        nemesis="Revenge; Total fall from grace due to pettiness",
        swe_name="Regulus",
        mythology="The Heart of the Lion",
    ),
    FixedStar(
        name="Spica",
        longitude=204.067,  # ~24 Libra (Adjusted for 2025)
        nature="Venus/Mars",
        magnitude=1,
        glory="Success through art, diplomacy, and intellect",
        nemesis="None (Pure Benefic)",
        swe_name="Spica",
        mythology="The Wheat Sheaf of the Virgin",
    ),
    FixedStar(
        name="Arcturus",
        longitude=204.333,  # 24°20' Libra
        nature="Jupiter/Mars",
        magnitude=1,
        glory="Riches, Renown, Prosperity through travel",
        nemesis="Legal troubles",
        swe_name="Arcturus",
    ),
    FixedStar(
        name="Alphecca",
        longitude=222.350,  # 12°21' Scorpio
        nature="Venus/Mercury",
        magnitude=2,
        glory="Artistic talent, Dignity, Poetic mind",
        nemesis="Scandal, Betrayal",
        swe_name="Alphecca",
    ),
    FixedStar(
        name="Antares",
        longitude=250.100,  # 10°06' Sagittarius
        nature="Mars/Jupiter",
        magnitude=1,
        glory="Intensity, Bravery, Strategic Genius",
        nemesis="Obsession; Self-destruction through mania",
        swe_name="Antares",
        mythology="The Heart of the Scorpion",
    ),
    FixedStar(
        name="Vega",
        longitude=285.383,  # 15°23' Capricorn
        nature="Venus/Mercury",
        magnitude=1,
        glory="Hopefulness, Refinement, Political power",
        nemesis="Pretentiousness, Lasciviousness",
        swe_name="Vega",
    ),
    FixedStar(
        name="Altair",
        longitude=292.017,  # 02°01' Aquarius
        nature="Mars/Jupiter",
        magnitude=1,
        glory="Boldness, Courage, Confidence",
        nemesis="Guilt, Bloodshed",
        swe_name="Altair",
    ),
    FixedStar(
        name="Fomalhaut",
        longitude=334.200,  # 04°12' Pisces
        nature="Venus/Mercury",
        magnitude=1,
        glory="Charisma, Artistic/Spiritual Legacy",
        nemesis="Corruption of Ideals; Dreaming without doing",
        swe_name="Fomalhaut",
    ),
    FixedStar(
        name="Deneb Adige",
        longitude=335.333,  # 05°20' Pisces
        nature="Venus/Mercury",
        magnitude=1,
        glory="Intelligence, Quick learning, Fame",
        nemesis="Naivety",
        swe_name="Deneb",
    ),
    FixedStar(
        name="Markab",
        longitude=353.550,  # 23°33' Pisces
        nature="Mars/Mercury",
        magnitude=2,
        glory="Honors, Wealth, Ambition",
        nemesis="Danger from fire/explosions",
        swe_name="Markab",
    ),
]


def get_fixed_star_meta() -> Dict[str, str]:
    return {
        "catalog": FIXED_STAR_CATALOG,
        "epoch": str(FIXED_STAR_EPOCH),
        "precession": FIXED_STAR_PRECESSION,
    }


@dataclass
class StarContact:
    star_name: str
    planet_name: str
    contact_type: str  # "CONJUNCTION" or "PARAN"
    angle: Optional[str] = None
    message: str = ""
    mythology: Optional[str] = None
    orb_deg: Optional[float] = None
    nature: Optional[str] = None


def get_shortest_dist(a: float, b: float) -> float:
    d = abs(a - b)
    if d > 180:
        d = 360 - d
    return d


def _normalize_deg(deg: float) -> float:
    return deg % 360.0


def _get_obliquity_deg(jd: Optional[float]) -> float:
    """Return true obliquity of the ecliptic in degrees for the given Julian Day."""
    if jd is None:
        return 23.4392911
    try:
        res = swe.calc_ut(jd, swe.ECL_NUT)
        coords = res[0] if isinstance(res[0], (list, tuple)) else res
        if isinstance(coords, (list, tuple)) and len(coords) > 0:
            return coords[0]  # true obliquity (index 0); index 1 is mean obliquity
    except Exception as e:
        logger.warning("Obliquity calc failed: %s", repr(e), exc_info=True)
    return 23.4392911


def _equatorial_to_ecliptic(
    ra: float, dec: float, epsilon: float
) -> Tuple[float, float]:
    ra_r = math.radians(ra)
    dec_r = math.radians(dec)
    eps_r = math.radians(epsilon)

    sin_beta = math.sin(dec_r) * math.cos(eps_r) - math.cos(dec_r) * math.sin(
        eps_r
    ) * math.sin(ra_r)
    beta = math.asin(sin_beta)

    y = math.sin(ra_r) * math.cos(eps_r) + math.tan(dec_r) * math.sin(eps_r)
    x = math.cos(ra_r)
    lam = math.atan2(y, x)

    return (_normalize_deg(math.degrees(lam)), math.degrees(beta))


def _ecliptic_to_equatorial(
    lon: float, lat: float, epsilon: float
) -> Tuple[float, float]:
    lon_r = math.radians(lon)
    lat_r = math.radians(lat)
    eps_r = math.radians(epsilon)

    sin_dec = math.sin(eps_r) * math.sin(lon_r) * math.cos(lat_r) + math.cos(
        eps_r
    ) * math.sin(lat_r)
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


def _get_star_equatorial(
    star: FixedStar, jd: Optional[float]
) -> Optional[Tuple[float, float]]:
    global _FIXSTAR_CATALOG_AVAILABLE, _FIXSTAR_MISSING_LOGGED

    if jd is None or not star.swe_name:
        return None
    if _FIXSTAR_CATALOG_AVAILABLE is False:
        return None

    try:
        flags = swe.FLG_SWIEPH | swe.FLG_EQUATORIAL
        res = swe.fixstar2_ut(star.swe_name, jd, flags)
        coords = res[0]
        ra = coords[0]
        dec = coords[1]
        _FIXSTAR_CATALOG_AVAILABLE = True
        return (ra, dec)
    except Exception as e:
        if "sefstars.txt" in str(e):
            _FIXSTAR_CATALOG_AVAILABLE = False
            if not _FIXSTAR_MISSING_LOGGED:
                logger.warning(
                    "Swiss Ephemeris fixed star catalog sefstars.txt is unavailable "
                    "on path %s; falling back to bundled traditional longitudes.",
                    SWISSEPH_EPHE_PATH,
                )
                _FIXSTAR_MISSING_LOGGED = True
            return None

        if star.swe_name not in _FIXSTAR_WARNED_STARS:
            logger.warning(
                "Star equatorial lookup failed for %s: %s",
                star.swe_name,
                repr(e),
                exc_info=True,
            )
            _FIXSTAR_WARNED_STARS.add(star.swe_name)
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


def _angles_for_body(
    ra: float, dec: float, ramc: float, lat: float, orb: float
) -> List[str]:
    hits = []
    ha = (ramc - ra + 540.0) % 360.0 - 180.0

    if abs(ha) <= orb:
        hits.append("MC")
    if abs(abs(ha) - 180.0) <= orb:
        hits.append("IC")

    try:
        cos_h = -math.tan(math.radians(lat)) * math.tan(math.radians(dec))
    except Exception as e:
        logger.warning("Hour angle calc error: %s", repr(e), exc_info=True)
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
    parans = []  # type: ignore
    if chart.geo_lat is None or chart.jd is None:
        return parans

    orb = 2.0
    epsilon = _get_obliquity_deg(chart.jd)

    # RAMC from MC (MC is ecliptic longitude)
    ramc, _ = _ecliptic_to_equatorial(chart.mc, 0.0, epsilon)

    # Planet angle hits
    planet_hits = {}
    for planet in chart.planets:
        ra_p, dec_p = _ecliptic_to_equatorial(
            planet.longitude, planet.latitude, epsilon
        )
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
                    parans.append(
                        StarContact(
                            star_name=star.name,
                            planet_name=p_name,
                            contact_type="PARAN",
                            angle=s_angle,
                            message=msg,
                            mythology=star.mythology,
                        )
                    )

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

                all_contacts.append(
                    StarContact(
                        star_name=star.name,
                        planet_name=p_name,
                        contact_type=contact_type,
                        message=msg,
                        mythology=star.mythology,
                        orb_deg=dist,
                        nature=star.nature,
                    )
                )

    # 3. Check Angles (Asc/MC) for direct star presence
    angles = {"Ascendant": chart.ascendant, "Midheaven": chart.mc}
    for angle_name, angle_long in angles.items():
        for star in STARS:
            star_lon = _get_star_longitude(star, chart.jd)
            dist = get_shortest_dist(angle_long, star_lon)
            if dist <= star.orb:
                all_contacts.append(
                    StarContact(
                        star_name=star.name,
                        planet_name=angle_name,
                        contact_type="ANGULAR_PRESENCE",
                        message=f"STAR ON {angle_name.upper()}: {star.name}. Glory: {star.glory}. Nemesis: {star.nemesis}.",
                        mythology=star.mythology,
                        orb_deg=dist,
                        nature=star.nature,
                    )
                )

    # Do not manufacture a compound Aldebaran-Antares "axis alert."  The
    # ordinary conjunction records above preserve an actual Moon or Mars
    # contact with either star.  A violent-death judgment additionally requires
    # the complete anaretic configuration of the cited authority; a star
    # conjunction alone cannot supply it.

    return all_contacts
