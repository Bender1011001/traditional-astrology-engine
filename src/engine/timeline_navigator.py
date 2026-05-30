"""
Transit timeline engine for the local astrology player.

This module produces real Swiss Ephemeris-backed frames for an animated
traditional astrology wheel. It keeps the natal chart fixed, advances the
transiting seven visible planets through time, and scores each frame with
explainable traditional timing signals.

Historical Use Only. This is symbolic timing analysis, not medical, legal,
financial, safety, or emergency advice.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional, Tuple

import swisseph as swe

from .forensic_forecast import get_profection_timings
from .lots import calculate_all_lots
from .models import Chart, Planet, PlanetName, Sect, Sign
from .prediction import (
    calculate_daily_profection,
    calculate_firdaria,
    calculate_monthly_profection,
    calculate_profection_sign,
    calculate_zr_periods,
    get_lord_of_year,
)


DISCLAIMER = (
    "Historical Use Only - symbolic timing analysis, not medical, legal, "
    "financial, safety, emergency, or deterministic life advice."
)

TRADITIONAL_PLANETS: Tuple[Tuple[PlanetName, int], ...] = (
    (PlanetName.SUN, swe.SUN),
    (PlanetName.MOON, swe.MOON),
    (PlanetName.MERCURY, swe.MERCURY),
    (PlanetName.VENUS, swe.VENUS),
    (PlanetName.MARS, swe.MARS),
    (PlanetName.JUPITER, swe.JUPITER),
    (PlanetName.SATURN, swe.SATURN),
)

TRADITIONAL_PLANET_NAMES = {planet.value for planet, _ in TRADITIONAL_PLANETS}

ASPECTS: Tuple[Tuple[str, float], ...] = (
    ("Conjunction", 0.0),
    ("Sextile", 60.0),
    ("Square", 90.0),
    ("Trine", 120.0),
    ("Opposition", 180.0),
)

SIGN_KEYWORDS = {
    Sign.ARIES: "initiative, courage, new action",
    Sign.TAURUS: "resources, stability, material security",
    Sign.GEMINI: "communication, learning, adaptability",
    Sign.CANCER: "home, family, emotional security",
    Sign.LEO: "authority, creativity, recognition",
    Sign.VIRGO: "service, health routines, analysis",
    Sign.LIBRA: "partnerships, contracts, balance",
    Sign.SCORPIO: "shared resources, investigation, hidden matters",
    Sign.SAGITTARIUS: "travel, philosophy, legal affairs",
    Sign.CAPRICORN: "career, structure, long-term goals",
    Sign.AQUARIUS: "community, innovation, alliances",
    Sign.PISCES: "solitude, spirituality, surrender",
}

PLANETARY_DAYS = {
    "Sunday": PlanetName.SUN,
    "Monday": PlanetName.MOON,
    "Tuesday": PlanetName.MARS,
    "Wednesday": PlanetName.MERCURY,
    "Thursday": PlanetName.JUPITER,
    "Friday": PlanetName.VENUS,
    "Saturday": PlanetName.SATURN,
}

INTENT_PLANETS = {
    "general": set(),
    "launch": {
        PlanetName.SUN,
        PlanetName.MOON,
        PlanetName.MERCURY,
        PlanetName.JUPITER,
    },
    "work": {
        PlanetName.SUN,
        PlanetName.MERCURY,
        PlanetName.JUPITER,
        PlanetName.SATURN,
    },
    "relationship": {PlanetName.MOON, PlanetName.VENUS, PlanetName.JUPITER},
    "study": {PlanetName.MERCURY, PlanetName.JUPITER, PlanetName.MOON},
    "rest": {PlanetName.MOON, PlanetName.SATURN, PlanetName.VENUS},
}

MAX_FRAMES = 900


def normalize_degree(value: float) -> float:
    return value % 360.0


def angle_distance(a: float, b: float) -> float:
    diff = abs(normalize_degree(a) - normalize_degree(b)) % 360.0
    return diff if diff <= 180.0 else 360.0 - diff


def julian_day_for_datetime(value: datetime) -> float:
    hour = value.hour + (value.minute / 60.0) + (value.second / 3600.0)
    return swe.julday(value.year, value.month, value.day, hour)


def sign_for_longitude(longitude: float) -> Sign:
    return list(Sign)[int(normalize_degree(longitude) / 30.0) % 12]


def planet_payload(planet: Planet) -> Dict[str, Any]:
    return {
        "name": planet.name.value,
        "longitude": round(normalize_degree(planet.longitude), 4),
        "latitude": round(planet.latitude, 4),
        "speed": round(planet.speed, 5),
        "retrograde": planet.is_retrograde,
        "sign": planet.sign.value,
        "degree": round(planet.degree_in_sign, 2),
    }


def rebuild_chart_from_raw(raw: Dict[str, Any]) -> Chart:
    """Reconstruct a Chart object from serialized calculator output."""
    planets: List[Planet] = []
    raw_planets = raw.get("planets", {})
    if isinstance(raw_planets, dict):
        planet_items = raw_planets.items()
    elif isinstance(raw_planets, list):
        planet_items = ((item.get("name", ""), item) for item in raw_planets)
    else:
        planet_items = []

    for name_str, pdata in planet_items:
        if not isinstance(pdata, dict):
            continue
        try:
            name = PlanetName(str(name_str))
        except ValueError:
            continue
        planets.append(
            Planet(
                name=name,
                longitude=float(pdata.get("longitude", 0.0)),
                latitude=float(pdata.get("latitude", 0.0)),
                speed=float(pdata.get("speed", 0.0)),
                altitude=float(pdata.get("altitude", 0.0)),
            )
        )

    raw_houses = raw.get("houses", {})
    houses: Dict[int, float] = {}
    if isinstance(raw_houses, dict):
        for key, value in raw_houses.items():
            try:
                houses[int(key)] = float(value)
            except (TypeError, ValueError):
                continue
    elif isinstance(raw_houses, list):
        for index, value in enumerate(raw_houses, start=1):
            try:
                if isinstance(value, dict):
                    houses[index] = float(value.get("cusp", 0.0))
                else:
                    houses[index] = float(value)
            except (TypeError, ValueError):
                continue

    angles = raw.get("angles", {})
    meta = raw.get("meta", {})
    sun_altitude = meta.get("sun_altitude")
    if sun_altitude is None:
        sun = next((planet for planet in planets if planet.name == PlanetName.SUN), None)
        sun_altitude = sun.altitude if sun is not None else 0.0
    return Chart(
        sun_altitude=float(sun_altitude),
        planets=planets,
        ascendant=float(angles.get("Ascendant", 0.0)),
        mc=float(angles.get("MC", 0.0)),
        geo_lat=float(meta.get("lat", 0.0)),
        geo_lon=float(meta.get("lon", 0.0)),
        jd=float(meta.get("julian_day", 0.0)),
        houses=houses or None,
    )


def resolve_birth_datetime(raw: Dict[str, Any]) -> datetime:
    utc_time = raw.get("meta", {}).get("utc_time")
    if not utc_time:
        raise ValueError("Chart output does not include meta.utc_time.")
    parsed = datetime.fromisoformat(str(utc_time).replace("Z", "+00:00"))
    if parsed.tzinfo is not None:
        parsed = parsed.replace(tzinfo=None)
    return parsed


def natal_payload(chart: Chart) -> Dict[str, Any]:
    houses = {
        str(key): round(normalize_degree(value), 4)
        for key, value in (chart.houses or {}).items()
    }
    planets = [
        planet_payload(planet)
        for planet in chart.planets
        if planet.name.value in TRADITIONAL_PLANET_NAMES
    ]
    return {
        "sect": "Day" if chart.sun_altitude > 0 else "Night",
        "ascendant": round(normalize_degree(chart.ascendant), 4),
        "mc": round(normalize_degree(chart.mc), 4),
        "geo_lat": chart.geo_lat,
        "geo_lon": chart.geo_lon,
        "houses": houses,
        "planets": planets,
    }


def transit_positions_at(target: datetime) -> Dict[PlanetName, Dict[str, Any]]:
    jd = julian_day_for_datetime(target)
    positions: Dict[PlanetName, Dict[str, Any]] = {}
    for planet, swe_id in TRADITIONAL_PLANETS:
        result = swe.calc_ut(jd, swe_id, swe.FLG_SWIEPH | swe.FLG_SPEED)
        coords = result[0] if isinstance(result[0], (list, tuple)) else result
        longitude = normalize_degree(float(coords[0]))
        speed = float(coords[3])
        positions[planet] = {
            "name": planet.value,
            "longitude": round(longitude, 4),
            "latitude": round(float(coords[1]), 4),
            "speed": round(speed, 5),
            "retrograde": speed < 0,
            "sign": sign_for_longitude(longitude).value,
            "degree": round(longitude % 30.0, 2),
        }
    return positions


def _planet_orb(planet: PlanetName) -> float:
    if planet == PlanetName.MOON:
        return 4.0
    if planet in {PlanetName.JUPITER, PlanetName.SATURN}:
        return 3.0
    return 2.0


def _aspect_hit(distance: float, orb_limit: float) -> Optional[Tuple[str, float, float]]:
    best: Optional[Tuple[str, float, float]] = None
    for aspect_name, aspect_angle in ASPECTS:
        orb = abs(distance - aspect_angle)
        if orb <= orb_limit and (best is None or orb < best[1]):
            best = (aspect_name, orb, aspect_angle)
    return best


def _out_of_sect_malefic(sect: Sect) -> PlanetName:
    return PlanetName.MARS if sect == Sect.DAY else PlanetName.SATURN


def _in_sect_benefic(sect: Sect) -> PlanetName:
    return PlanetName.JUPITER if sect == Sect.DAY else PlanetName.VENUS


def _intent_multiplier(
    intent: str, transiting: PlanetName, natal_planet: PlanetName, delta: float
) -> float:
    relevant = INTENT_PLANETS.get(intent, set())
    if not relevant:
        return 1.0
    if transiting in relevant or natal_planet in relevant:
        return 1.25 if delta >= 0 else 1.15
    return 0.9


def _score_aspect(
    transiting: PlanetName,
    natal_planet: PlanetName,
    aspect: str,
    orb: float,
    orb_limit: float,
    sect: Sect,
    intent: str,
) -> Tuple[float, str, str]:
    soft = aspect in {"Sextile", "Trine"}
    conjunction = aspect == "Conjunction"
    hard = aspect in {"Square", "Opposition"}
    exactness = max(0.35, 1.0 - (orb / max(orb_limit, 0.1)))
    quality = "mixed"

    if transiting in {PlanetName.VENUS, PlanetName.JUPITER}:
        if soft:
            delta = 12.0
            quality = "supportive"
        elif conjunction:
            delta = 8.0
            quality = "supportive"
        else:
            delta = 2.0
            quality = "mixed"
        if transiting == _in_sect_benefic(sect):
            delta *= 1.15
    elif transiting in {PlanetName.MARS, PlanetName.SATURN}:
        if hard:
            delta = -14.0
            quality = "caution"
        elif conjunction:
            delta = -8.0
            quality = "caution"
        else:
            delta = -3.0
            quality = "tempering"
        if transiting == _out_of_sect_malefic(sect):
            delta *= 1.35
        else:
            delta *= 0.8
    elif transiting == PlanetName.MERCURY:
        delta = 5.0 if (soft or conjunction) else -4.0
        quality = "supportive" if delta > 0 else "mixed"
    elif transiting == PlanetName.MOON:
        delta = 4.0 if (soft or conjunction) else -4.0
        quality = "supportive" if delta > 0 else "mixed"
    else:
        delta = 4.0 if (soft or conjunction) else -4.0
        quality = "supportive" if delta > 0 else "mixed"

    delta *= exactness
    delta *= _intent_multiplier(intent, transiting, natal_planet, delta)
    return (
        round(delta, 2),
        quality,
        f"Transiting {transiting.value} {aspect.lower()} natal {natal_planet.value}",
    )


def active_transit_aspects(
    chart: Chart,
    transit_positions: Dict[PlanetName, Dict[str, Any]],
    sect: Sect,
    intent: str,
) -> List[Dict[str, Any]]:
    natal_planets = [
        planet
        for planet in chart.planets
        if planet.name.value in TRADITIONAL_PLANET_NAMES
    ]
    hits: List[Dict[str, Any]] = []
    for transiting, position in transit_positions.items():
        orb_limit = _planet_orb(transiting)
        for natal_planet in natal_planets:
            distance = angle_distance(position["longitude"], natal_planet.longitude)
            match = _aspect_hit(distance, orb_limit)
            if match is None:
                continue
            aspect, orb, aspect_angle = match
            delta, quality, brief = _score_aspect(
                transiting=transiting,
                natal_planet=natal_planet.name,
                aspect=aspect,
                orb=orb,
                orb_limit=orb_limit,
                sect=sect,
                intent=intent,
            )
            hits.append(
                {
                    "transiting": transiting.value,
                    "natal_planet": natal_planet.name.value,
                    "aspect": aspect,
                    "aspect_angle": aspect_angle,
                    "orb": round(orb, 2),
                    "quality": quality,
                    "score_delta": delta,
                    "brief": brief,
                    "transit_longitude": position["longitude"],
                    "natal_longitude": round(normalize_degree(natal_planet.longitude), 4),
                }
            )

    hits.sort(key=lambda item: (abs(item["score_delta"]) * -1, item["orb"]))
    return hits


def moon_condition_at(
    target: datetime, transit_positions: Dict[PlanetName, Dict[str, Any]]
) -> Dict[str, Any]:
    moon = transit_positions[PlanetName.MOON]
    sun = transit_positions[PlanetName.SUN]
    moon_lon = float(moon["longitude"])
    sun_lon = float(sun["longitude"])
    moon_sign = sign_for_longitude(moon_lon)
    moon_sign_index = int(moon_lon / 30.0) % 12
    elongation = (moon_lon - sun_lon) % 360.0

    if elongation < 22.5 or elongation >= 337.5:
        phase = "New Moon"
    elif elongation < 67.5:
        phase = "Waxing Crescent"
    elif elongation < 112.5:
        phase = "First Quarter"
    elif elongation < 157.5:
        phase = "Waxing Gibbous"
    elif elongation < 202.5:
        phase = "Full Moon"
    elif elongation < 247.5:
        phase = "Waning Gibbous"
    elif elongation < 292.5:
        phase = "Last Quarter"
    else:
        phase = "Balsamic"

    sign_end_lon = (moon_sign_index + 1) * 30.0
    degrees_left = (sign_end_lon - moon_lon) % 360.0
    aspect_angles = [0.0, 60.0, 90.0, 120.0, 180.0]
    has_applying = False
    for planet_name in (
        PlanetName.SUN,
        PlanetName.MERCURY,
        PlanetName.VENUS,
        PlanetName.MARS,
        PlanetName.JUPITER,
        PlanetName.SATURN,
    ):
        planet_lon = float(transit_positions[planet_name]["longitude"])
        for aspect_angle in aspect_angles:
            for target_lon in (
                normalize_degree(planet_lon + aspect_angle),
                normalize_degree(planet_lon - aspect_angle),
            ):
                arc = (target_lon - moon_lon) % 360.0
                if 0.0 < arc <= degrees_left + 8.0 and arc < 30.0:
                    has_applying = True
                    break
            if has_applying:
                break
        if has_applying:
            break

    return {
        "sign": moon_sign.value,
        "degree": round(moon_lon % 30.0, 2),
        "longitude": round(moon_lon, 4),
        "phase": phase,
        "elongation": round(elongation, 2),
        "waxing": elongation < 180.0,
        "speed": moon["speed"],
        "fast": float(moon["speed"]) > 13.0,
        "void_of_course": not has_applying,
    }


def timing_layers_for_frame(
    chart: Chart, birth_dt: datetime, birth_jd: float, target: datetime
) -> Dict[str, Any]:
    sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
    age = int((target - birth_dt).days / 365.25)
    asc_sign = sign_for_longitude(chart.ascendant)
    annual_sign = calculate_profection_sign(asc_sign, age)
    lord_of_year = get_lord_of_year(annual_sign)
    _, prof_month, prof_day = get_profection_timings(birth_dt, target)
    monthly_sign = calculate_monthly_profection(annual_sign, prof_month)
    daily_sign = calculate_daily_profection(monthly_sign, prof_day)
    daily_lord = get_lord_of_year(daily_sign)
    day_ruler = PLANETARY_DAYS.get(target.strftime("%A"), PlanetName.SUN)

    zr: Dict[str, Any]
    try:
        lots = calculate_all_lots(chart, sect)
        spirit = lots.get("Spirit")
        if spirit is None:
            zr = {"note": "Lot of Spirit unavailable."}
        else:
            zr = calculate_zr_periods(sign_for_longitude(spirit), birth_dt, target)
    except Exception:
        zr = {"note": "Zodiacal Releasing unavailable for this frame."}

    try:
        firdaria = calculate_firdaria(sect, birth_dt, target)
    except Exception:
        firdaria = {"note": "Firdaria unavailable for this frame."}

    return {
        "age": age,
        "sect": sect.value,
        "annual_sign": annual_sign.value,
        "lord_of_year": lord_of_year.value,
        "monthly_sign": monthly_sign.value,
        "daily_sign": daily_sign.value,
        "daily_lord": daily_lord.value,
        "daily_keywords": SIGN_KEYWORDS.get(daily_sign, ""),
        "planetary_day": target.strftime("%A"),
        "day_ruler": day_ruler.value,
        "day_matches_lord_of_year": day_ruler == lord_of_year,
        "day_matches_daily_lord": day_ruler == daily_lord,
        "firdaria": firdaria,
        "zodiacal_releasing": zr,
    }


def epitasis_marker(
    timing: Dict[str, Any], transit_positions: Dict[PlanetName, Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    try:
        lord = PlanetName(timing["lord_of_year"])
    except ValueError:
        return None
    lord_position = transit_positions.get(lord)
    if not lord_position:
        return None
    lord_transit_sign = sign_for_longitude(float(lord_position["longitude"])).value
    if lord_transit_sign != timing.get("daily_sign"):
        return None
    return {
        "type": "epitasis",
        "label": "Epitasis active",
        "score_delta": 8,
        "detail": (
            f"{timing['lord_of_year']} is transiting {lord_transit_sign}, "
            f"matching the daily profection sign."
        ),
    }


def score_frame(
    aspects: List[Dict[str, Any]],
    moon: Dict[str, Any],
    timing: Dict[str, Any],
    epitasis: Optional[Dict[str, Any]],
    intent: str,
) -> Dict[str, Any]:
    score = 50.0
    reasons: List[Dict[str, Any]] = []

    for aspect in aspects:
        delta = float(aspect["score_delta"])
        score += delta
        reasons.append(
            {
                "label": aspect["brief"],
                "score_delta": round(delta, 2),
                "quality": aspect["quality"],
                "detail": f"{aspect['aspect']} with {aspect['orb']} deg orb.",
            }
        )

    moon_delta = 4.0 if moon.get("waxing") else 1.5
    if intent == "launch":
        moon_delta = 8.0 if moon.get("waxing") else -4.0
    score += moon_delta
    reasons.append(
        {
            "label": "Waxing Moon" if moon.get("waxing") else "Waning Moon",
            "score_delta": round(moon_delta, 2),
            "quality": "supportive" if moon_delta >= 0 else "caution",
            "detail": f"Moon phase: {moon['phase']} in {moon['sign']}.",
        }
    )

    if moon.get("void_of_course"):
        voc_delta = -20.0 if intent == "launch" else -12.0
        score += voc_delta
        reasons.append(
            {
                "label": "Moon void of course",
                "score_delta": voc_delta,
                "quality": "caution",
                "detail": "Traditional texts treat initiation symbolism as weaker.",
            }
        )

    if timing.get("day_matches_lord_of_year"):
        score += 5.0
        reasons.append(
            {
                "label": "Planetary day matches Lord of the Year",
                "score_delta": 5.0,
                "quality": "supportive",
                "detail": f"{timing['planetary_day']} is ruled by {timing['day_ruler']}.",
            }
        )
    elif timing.get("day_matches_daily_lord"):
        score += 3.0
        reasons.append(
            {
                "label": "Planetary day matches daily lord",
                "score_delta": 3.0,
                "quality": "supportive",
                "detail": f"{timing['daily_lord']} is emphasized by the weekday.",
            }
        )

    if epitasis is not None:
        delta = float(epitasis["score_delta"])
        score += delta
        reasons.append(
            {
                "label": epitasis["label"],
                "score_delta": delta,
                "quality": "intense",
                "detail": epitasis["detail"],
            }
        )

    bounded = round(max(0.0, min(100.0, score)), 1)
    if bounded >= 68:
        tone = "supportive"
    elif bounded >= 55:
        tone = "constructive"
    elif bounded >= 42:
        tone = "mixed"
    elif bounded >= 28:
        tone = "caution"
    else:
        tone = "heavy"

    reasons.sort(key=lambda item: abs(float(item["score_delta"])), reverse=True)
    return {
        "score": bounded,
        "tone": tone,
        "label": tone.title(),
        "reasons": reasons[:10],
    }


def iter_frame_datetimes(
    start: datetime, end: datetime, step_hours: int
) -> Iterable[datetime]:
    if end < start:
        raise ValueError("end must be on or after start.")
    if step_hours < 1:
        raise ValueError("step_hours must be at least 1.")

    current = start
    count = 0
    while current <= end:
        if count >= MAX_FRAMES:
            raise ValueError(
                f"Timeline would exceed {MAX_FRAMES} frames. Increase step_hours or shorten the range."
            )
        yield current
        current += timedelta(hours=step_hours)
        count += 1


def build_frame(
    chart: Chart,
    birth_dt: datetime,
    birth_jd: float,
    target: datetime,
    intent: str,
    index: int,
) -> Dict[str, Any]:
    sect = Sect.DAY if chart.sun_altitude > 0 else Sect.NIGHT
    positions = transit_positions_at(target)
    moon = moon_condition_at(target, positions)
    timing = timing_layers_for_frame(chart, birth_dt, birth_jd, target)
    aspects = active_transit_aspects(chart, positions, sect, intent)
    epitasis = epitasis_marker(timing, positions)
    score = score_frame(aspects, moon, timing, epitasis, intent)
    markers = []
    if epitasis is not None:
        markers.append(epitasis)
    if moon.get("void_of_course"):
        markers.append(
            {
                "type": "moon_voc",
                "label": "Moon void of course",
                "detail": "Symbolic caution for initiations.",
            }
        )
    return {
        "index": index,
        "timestamp": target.isoformat(timespec="minutes"),
        "display": target.strftime("%Y-%m-%d %H:%M UTC"),
        "transits": list(positions.values()),
        "moon": moon,
        "timing": timing,
        "aspects": aspects,
        "markers": markers,
        "score": score["score"],
        "tone": score["tone"],
        "score_label": score["label"],
        "reasons": score["reasons"],
    }


def summarize_peaks(frames: List[Dict[str, Any]]) -> Dict[str, Any]:
    supportive = sorted(frames, key=lambda frame: frame["score"], reverse=True)[:5]
    caution = sorted(frames, key=lambda frame: frame["score"])[:5]
    return {
        "supportive": [
            {
                "timestamp": frame["timestamp"],
                "display": frame["display"],
                "score": frame["score"],
                "tone": frame["tone"],
                "top_reason": frame["reasons"][0]["label"] if frame["reasons"] else "",
            }
            for frame in supportive
        ],
        "caution": [
            {
                "timestamp": frame["timestamp"],
                "display": frame["display"],
                "score": frame["score"],
                "tone": frame["tone"],
                "top_reason": frame["reasons"][0]["label"] if frame["reasons"] else "",
            }
            for frame in caution
        ],
    }


def generate_timeline(
    chart: Chart,
    birth_dt: datetime,
    birth_jd: float,
    start: datetime,
    end: datetime,
    step_hours: int = 24,
    intent: str = "general",
) -> Dict[str, Any]:
    normalized_intent = intent if intent in INTENT_PLANETS else "general"
    frames = [
        build_frame(chart, birth_dt, birth_jd, target, normalized_intent, index)
        for index, target in enumerate(iter_frame_datetimes(start, end, step_hours))
    ]
    heatmap = [
        {
            "index": frame["index"],
            "timestamp": frame["timestamp"],
            "display": frame["display"],
            "score": frame["score"],
            "tone": frame["tone"],
        }
        for frame in frames
    ]
    return {
        "method": (
            "Swiss Ephemeris transits over a fixed traditional natal chart; "
            "seven visible planets only; Whole Sign-compatible natal anchor."
        ),
        "disclaimer": DISCLAIMER,
        "intent": normalized_intent,
        "range": {
            "start": start.isoformat(timespec="minutes"),
            "end": end.isoformat(timespec="minutes"),
            "step_hours": step_hours,
            "frame_count": len(frames),
        },
        "natal": natal_payload(chart),
        "frames": frames,
        "heatmap": heatmap,
        "peaks": summarize_peaks(frames),
    }
