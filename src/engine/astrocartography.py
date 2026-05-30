import logging
import math
from typing import Any, Mapping

import swisseph as swe

from src.engine.calculator.main import calculate_chart_data
from src.engine.dignities import DignityCalculator
from src.engine.models import PlanetName, Sect, Sign

logger = logging.getLogger(__name__)

TRADITIONAL_PLANETS = ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn")

PLANET_IDS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
}

PLANET_COLORS = {
    "Sun": "#d4af37",
    "Moon": "#d7d2c4",
    "Mercury": "#b9aa8f",
    "Venus": "#c48a4a",
    "Mars": "#b87333",
    "Jupiter": "#e0c77a",
    "Saturn": "#8c8171",
}

ANGLE_LABELS = {
    "MC": "Midheaven",
    "IC": "Imum Coeli",
    "ASC": "Ascendant",
    "DSC": "Descendant",
}

ANGLE_THEMES = {
    "MC": "public visibility, vocation, reputation, and visible work",
    "IC": "home, roots, private life, land, and foundations",
    "ASC": "body, identity, beginnings, autonomy, and first impressions",
    "DSC": "partners, clients, allies, contracts, and open counterparts",
}

PLANET_THEMES = {
    "Sun": "recognition, authority, purpose, and leadership",
    "Moon": "belonging, care, rhythm, the public mood, and daily life",
    "Mercury": "trade, writing, study, sales, travel, and negotiation",
    "Venus": "patronage, art, ease, affection, and alliance",
    "Mars": "competition, urgency, execution, severance, and courage",
    "Jupiter": "growth, teaching, patrons, law, faith, and opportunity",
    "Saturn": "discipline, permanence, boundaries, seniority, and delay",
    "Uranus": "disruption, invention, and volatility",
    "Neptune": "idealization, imagination, fog, and porous boundaries",
    "Pluto": "intensity, pressure, and deep transformation",
}

PLANET_INTENT_WEIGHTS = {
    "overview": {
        "Sun": 8,
        "Moon": 7,
        "Mercury": 7,
        "Venus": 7,
        "Mars": 5,
        "Jupiter": 8,
        "Saturn": 5,
    },
    "career": {
        "Sun": 10,
        "Jupiter": 9,
        "Mercury": 8,
        "Saturn": 7,
        "Mars": 6,
        "Venus": 4,
        "Moon": 3,
    },
    "business": {
        "Mercury": 10,
        "Sun": 8,
        "Mars": 8,
        "Jupiter": 7,
        "Saturn": 6,
        "Venus": 5,
        "Moon": 3,
    },
    "relationship": {
        "Venus": 10,
        "Moon": 8,
        "Jupiter": 7,
        "Sun": 5,
        "Mercury": 5,
        "Mars": 4,
        "Saturn": 3,
    },
    "home": {
        "Moon": 10,
        "Venus": 8,
        "Jupiter": 7,
        "Saturn": 6,
        "Sun": 4,
        "Mercury": 4,
        "Mars": 3,
    },
    "creative": {
        "Venus": 10,
        "Sun": 9,
        "Mercury": 7,
        "Moon": 6,
        "Jupiter": 6,
        "Mars": 5,
        "Saturn": 2,
    },
    "study": {
        "Mercury": 10,
        "Jupiter": 8,
        "Saturn": 8,
        "Sun": 5,
        "Moon": 4,
        "Venus": 3,
        "Mars": 2,
    },
}

ANGLE_INTENT_WEIGHTS = {
    "overview": {"MC": 7, "ASC": 7, "DSC": 6, "IC": 6},
    "career": {"MC": 10, "ASC": 7, "DSC": 5, "IC": 2},
    "business": {"MC": 9, "ASC": 8, "DSC": 7, "IC": 2},
    "relationship": {"DSC": 10, "ASC": 6, "IC": 5, "MC": 3},
    "home": {"IC": 10, "Moon": 6, "ASC": 5, "DSC": 3, "MC": 2},
    "creative": {"MC": 8, "ASC": 8, "DSC": 5, "IC": 3},
    "study": {"MC": 7, "ASC": 7, "IC": 5, "DSC": 4},
}

INTENT_LABELS = {
    "overview": "General map",
    "career": "Vocation and visibility",
    "business": "Trade, sales, and self-directed work",
    "relationship": "Partnership and clients",
    "home": "Home and roots",
    "creative": "Creative output",
    "study": "Study and teaching",
}

HIGHLIGHT_LIMIT = 8
INFLUENCE_BAND_KM = 300
TARGET_REVIEW_RADIUS_KM = 1000
LATITUDE_MIN = -85.0
LATITUDE_MAX = 85.0
LATITUDE_STEP = 2.0


def generate_astrocartography_map(
    *,
    date_str: str,
    time_str: str,
    city: str,
    state: str = "",
    name: str = "Native",
    latitude: float | None = None,
    longitude: float | None = None,
    house_system: str | None = "W",
    zodiac_system: str | None = "tropical",
    ayanamsa: str | None = None,
    node_type: str = "mean",
    time_unknown: bool = False,
    intent: str = "overview",
    planets: list[str] | None = None,
    target_locations: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Calculate a chart-tied astrocartography payload from birth data."""
    raw_chart_data = calculate_chart_data(
        date_str=date_str,
        time_str=time_str,
        city=city,
        state=state,
        latitude=latitude,
        longitude=longitude,
        house_system=house_system,
        zodiac_system=zodiac_system,
        ayanamsa=ayanamsa,
        node_type=node_type,
    )
    if "error" in raw_chart_data:
        raise ValueError(str(raw_chart_data["error"]))

    chart_data = {
        "meta": {
            "subject_name": name,
            "chart": raw_chart_data.get("meta", {}),
        },
        "astronomy": {
            "planets": raw_chart_data.get("planets", {}),
            "houses": raw_chart_data.get("houses", {}),
            "angles": raw_chart_data.get("angles", {}),
        },
        "analysis": {},
    }
    return build_astrocartography_map_from_chart_data(
        chart_data,
        intent=intent,
        planets=planets,
        target_locations=target_locations,
        time_unknown=time_unknown,
    )


def build_astrocartography_map_from_chart_data(
    chart_data: Mapping[str, Any],
    *,
    intent: str = "overview",
    planets: list[str] | None = None,
    target_locations: list[Mapping[str, Any]] | None = None,
    time_unknown: bool = False,
) -> dict[str, Any]:
    """Build astrocartography lines and rankings from existing chart output."""
    intent_key = intent if intent in PLANET_INTENT_WEIGHTS else "overview"
    meta = _chart_meta(chart_data)
    jd = _as_float(meta.get("julian_day") or _get(chart_data, "meta", "julian_day"))
    if jd is None:
        raise ValueError("Chart data does not include a Julian Day.")

    selected_planets = _select_planets(planets)
    planet_context = _planet_contexts(chart_data, selected_planets)
    gst_deg = _greenwich_sidereal_degrees(jd)

    lines: list[dict[str, Any]] = []
    try:
        for planet_name in selected_planets:
            pid = PLANET_IDS.get(planet_name)
            if pid is None:
                continue
            eq = _equatorial_position(jd, pid)
            context = planet_context.get(planet_name, {})
            for angle in ("MC", "IC", "ASC", "DSC"):
                segments = _line_segments_for_angle(eq["ra_deg"], eq["dec_deg"], gst_deg, angle)
                if not segments:
                    continue
                score = _line_score(planet_name, angle, context, intent_key)
                line = {
                    "id": f"{planet_name.lower()}_{angle.lower()}",
                    "planet": planet_name,
                    "angle": angle,
                    "angle_label": ANGLE_LABELS[angle],
                    "label": f"{planet_name} {angle}",
                    "color": PLANET_COLORS.get(planet_name, "#d4af37"),
                    "stroke": _angle_stroke(angle),
                    "stroke_pattern": _angle_stroke_pattern(angle),
                    "right_ascension_deg": round(eq["ra_deg"], 6),
                    "declination_deg": round(eq["dec_deg"], 6),
                    "natal_longitude": _rounded(context.get("longitude")),
                    "natal_sign": context.get("sign"),
                    "natal_house": context.get("house"),
                    "dignity_score": context.get("dignity_score"),
                    "sect_role": context.get("sect_role"),
                    "score": score,
                    "score_label": _score_label(score),
                    "themes": {
                        "planet": PLANET_THEMES.get(planet_name, "planetary emphasis"),
                        "angle": ANGLE_THEMES[angle],
                    },
                    "interpretation": _line_interpretation(
                        planet_name, angle, context, intent_key, score
                    ),
                    "segments": segments,
                }
                lines.append(line)
    finally:
        swe.close()

    ranked_lines = sorted(lines, key=lambda item: item["score"], reverse=True)[
        :HIGHLIGHT_LIMIT
    ]
    targets = _score_target_locations(target_locations or [], lines)

    return {
        "status": "ok",
        "chart": {
            "subject_name": _get(chart_data, "meta", "subject_name") or "Native",
            "date": meta.get("date"),
            "time": meta.get("time"),
            "city": meta.get("city"),
            "state": meta.get("state"),
            "latitude": meta.get("lat"),
            "longitude": meta.get("lon"),
            "timezone": meta.get("timezone"),
            "utc_time": meta.get("utc_time"),
            "julian_day": jd,
            "house_system": meta.get("house_system"),
            "sect": _sect(chart_data),
            "time_confidence": "low_noon_placeholder" if time_unknown else "birth_time_supplied",
        },
        "intent": {"key": intent_key, "label": INTENT_LABELS[intent_key]},
        "map": {
            "projection": "equirectangular",
            "latitude_range": [LATITUDE_MIN, LATITUDE_MAX],
            "influence_band_km": INFLUENCE_BAND_KM,
            "target_review_radius_km": TARGET_REVIEW_RADIUS_KM,
            "greenwich_sidereal_deg": round(gst_deg, 6),
        },
        "lines": lines,
        "ranked_lines": ranked_lines,
        "target_locations": targets,
        "legend": {
            "angles": ANGLE_THEMES,
            "planets": {name: PLANET_THEMES[name] for name in selected_planets},
        },
        "method": (
            "MC/IC lines use planetary right ascension against Greenwich sidereal time; "
            "ASC/DSC lines solve the horizon equation by sampled geographic latitude."
        ),
        "disclaimer": (
            "Historical Use Only. Astrocartography here is symbolic mapping from the natal chart, "
            "not relocation, immigration, financial, legal, medical, or safety advice."
        ),
    }


def _chart_meta(chart_data: Mapping[str, Any]) -> Mapping[str, Any]:
    meta = chart_data.get("meta", {})
    if isinstance(meta, Mapping):
        chart_meta = meta.get("chart")
        if isinstance(chart_meta, Mapping):
            return chart_meta
        return meta
    return {}


def _planet_contexts(
    chart_data: Mapping[str, Any], selected_planets: tuple[str, ...]
) -> dict[str, dict[str, Any]]:
    astronomy = chart_data.get("astronomy", {})
    if not isinstance(astronomy, Mapping):
        astronomy = {}
    planets = astronomy.get("planets", {})
    if not isinstance(planets, Mapping):
        planets = {}
    houses = _int_keyed_houses(astronomy.get("houses", {}))
    angles = astronomy.get("angles", {})
    if not isinstance(angles, Mapping):
        angles = {}
    ascendant = _as_float(angles.get("Ascendant") or angles.get("Asc"))

    analysis = chart_data.get("analysis", {})
    if not isinstance(analysis, Mapping):
        analysis = {}
    forensic_rows = analysis.get("planets_forensic") or chart_data.get("planets_forensic") or []
    forensic_lookup = {
        row.get("name"): row
        for row in forensic_rows
        if isinstance(row, Mapping) and row.get("name")
    }

    sect = _sect(chart_data)
    sect_enum = Sect.DAY if sect == "DAY" else Sect.NIGHT
    contexts: dict[str, dict[str, Any]] = {}
    for name in selected_planets:
        row = forensic_lookup.get(name)
        raw = planets.get(name, {}) if isinstance(planets, Mapping) else {}
        if not isinstance(raw, Mapping):
            raw = {}
        longitude = _as_float(
            (row or {}).get("longitude") if isinstance(row, Mapping) else None
        )
        if longitude is None:
            longitude = _as_float(raw.get("longitude"))

        dignity_score = None
        house = None
        if isinstance(row, Mapping):
            dignity_score = _as_float(_get(row, "dignities", "total_score"))
            house = row.get("house")

        if longitude is not None:
            if dignity_score is None:
                dignity_score = _dignity_score(name, longitude, sect_enum)
            if house is None and ascendant is not None:
                house = DignityCalculator.get_house_number(longitude, ascendant, houses)

        contexts[name] = {
            "longitude": longitude,
            "sign": _sign_name(longitude) if longitude is not None else None,
            "house": house,
            "dignity_score": int(dignity_score) if dignity_score is not None else None,
            "sect_role": _sect_role(name, sect),
        }
    return contexts


def _select_planets(planets: list[str] | None) -> tuple[str, ...]:
    if not planets:
        return TRADITIONAL_PLANETS
    lookup = {name.lower(): name for name in TRADITIONAL_PLANETS}
    selected: list[str] = []
    for raw in planets:
        key = str(raw or "").strip().replace("_", " ").lower()
        key = key.replace(" ", "")
        normalized_lookup = {k.replace(" ", ""): v for k, v in lookup.items()}
        name = normalized_lookup.get(key)
        if name and name not in selected:
            selected.append(name)
    return tuple(selected or TRADITIONAL_PLANETS)


def _equatorial_position(jd: float, planet_id: int) -> dict[str, float]:
    flags = swe.FLG_SWIEPH | swe.FLG_EQUATORIAL | swe.FLG_SPEED
    res = swe.calc_ut(jd, planet_id, flags)
    coords = res[0] if isinstance(res[0], (list, tuple)) else res
    return {"ra_deg": float(coords[0]) % 360.0, "dec_deg": float(coords[1])}


def _greenwich_sidereal_degrees(jd: float) -> float:
    return (float(swe.sidtime(jd)) * 15.0) % 360.0


def _line_segments_for_angle(
    ra_deg: float, dec_deg: float, gst_deg: float, angle: str
) -> list[list[dict[str, float]]]:
    if angle == "MC":
        lon = _normalize_lon(ra_deg - gst_deg)
        return [_vertical_segment(lon)]
    if angle == "IC":
        lon = _normalize_lon(ra_deg + 180.0 - gst_deg)
        return [_vertical_segment(lon)]

    points: list[dict[str, float]] = []
    lat = LATITUDE_MIN
    while lat <= LATITUDE_MAX + 0.0001:
        lon = _asc_desc_longitude(ra_deg, dec_deg, gst_deg, lat, angle)
        if lon is not None:
            points.append({"lat": round(lat, 4), "lon": round(lon, 4)})
        lat += LATITUDE_STEP
    return _split_wrapped_segments(points)


def _vertical_segment(lon: float) -> list[dict[str, float]]:
    points = []
    lat = LATITUDE_MIN
    while lat <= LATITUDE_MAX + 0.0001:
        points.append({"lat": round(lat, 4), "lon": round(lon, 4)})
        lat += LATITUDE_STEP
    return points


def _asc_desc_longitude(
    ra_deg: float, dec_deg: float, gst_deg: float, lat_deg: float, angle: str
) -> float | None:
    lat_rad = math.radians(lat_deg)
    dec_rad = math.radians(dec_deg)
    horizon_arg = -math.tan(lat_rad) * math.tan(dec_rad)
    if horizon_arg < -1.0 or horizon_arg > 1.0:
        return None
    hour_angle = math.degrees(math.acos(max(-1.0, min(1.0, horizon_arg))))
    if angle == "ASC":
        hour_angle = -hour_angle
    elif angle != "DSC":
        return None
    local_sidereal = (ra_deg + hour_angle) % 360.0
    return _normalize_lon(local_sidereal - gst_deg)


def _split_wrapped_segments(
    points: list[dict[str, float]]
) -> list[list[dict[str, float]]]:
    if not points:
        return []
    segments: list[list[dict[str, float]]] = [[points[0]]]
    for prev, point in zip(points, points[1:]):
        if abs(point["lon"] - prev["lon"]) > 180.0:
            segments.append([point])
        else:
            segments[-1].append(point)
    return [segment for segment in segments if len(segment) >= 2]


def _line_score(
    planet: str, angle: str, context: Mapping[str, Any], intent: str
) -> int:
    planet_weight = PLANET_INTENT_WEIGHTS[intent].get(planet, 4)
    angle_weight = ANGLE_INTENT_WEIGHTS[intent].get(angle, 4)
    dignity = int(context.get("dignity_score") or 0)
    house = context.get("house")
    score = 50 + planet_weight + angle_weight
    score += max(-12, min(12, dignity)) * 1.25
    score += _sect_score_modifier(planet, context.get("sect_role"))
    score += _house_score_modifier(house, intent)
    if planet in {"Mars", "Saturn"} and score > 82:
        score = 82
    return int(max(0, min(100, round(score))))


def _sect_score_modifier(planet: str, sect_role: Any) -> int:
    role = str(sect_role or "").lower()
    if "out-of-sect malefic" in role:
        return -7
    if "benefic of sect" in role:
        return 6
    if "malefic of sect" in role:
        return 3
    if "luminary of sect" in role:
        return 4
    if "contrary luminary" in role:
        return -1
    if planet == "Mercury":
        return 1
    return 0


def _house_score_modifier(house: Any, intent: str) -> int:
    try:
        house_num = int(house)
    except (TypeError, ValueError):
        return 0
    if intent in {"career", "business"}:
        return {10: 5, 1: 4, 11: 3, 2: 3, 3: 2, 6: -2, 12: -3}.get(house_num, 0)
    if intent == "relationship":
        return {7: 5, 5: 3, 11: 2, 12: -3, 6: -2}.get(house_num, 0)
    if intent == "home":
        return {4: 5, 2: 3, 1: 2, 10: -2, 12: -2}.get(house_num, 0)
    if intent == "creative":
        return {5: 5, 10: 3, 1: 3, 3: 2, 12: -2}.get(house_num, 0)
    if intent == "study":
        return {3: 4, 9: 4, 1: 2, 10: 2, 12: -2}.get(house_num, 0)
    return {1: 2, 4: 2, 7: 2, 10: 2, 6: -1, 8: -1, 12: -2}.get(house_num, 0)


def _line_interpretation(
    planet: str,
    angle: str,
    context: Mapping[str, Any],
    intent: str,
    score: int,
) -> str:
    sign = context.get("sign") or "its natal sign"
    house = context.get("house")
    dignity = context.get("dignity_score")
    house_text = f" in natal house {house}" if house else ""
    dignity_text = f" with essential score {dignity}" if dignity is not None else ""
    return (
        f"{planet} on the {ANGLE_LABELS[angle]} emphasizes {PLANET_THEMES.get(planet)} "
        f"through {ANGLE_THEMES[angle]}. In this chart {planet} is in {sign}{house_text}"
        f"{dignity_text}; the {INTENT_LABELS[intent].lower()} score is {score}/100."
    )


def _score_label(score: int) -> str:
    if score >= 78:
        return "strong emphasis"
    if score >= 64:
        return "useful emphasis"
    if score >= 48:
        return "mixed emphasis"
    return "caution emphasis"


def _angle_stroke(angle: str) -> str:
    if angle == "MC":
        return "solid"
    if angle == "IC":
        return "dashed"
    if angle == "ASC":
        return "dotted"
    return "dash-dot"


def _angle_stroke_pattern(angle: str) -> str:
    if angle == "MC":
        return ""
    if angle == "IC":
        return "10 7"
    if angle == "ASC":
        return "1.5 7"
    return "12 5 2 5"


def _score_target_locations(
    target_locations: list[Mapping[str, Any]], lines: list[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    scored_targets = []
    for target in target_locations:
        lat = _as_float(target.get("latitude"))
        lon = _as_float(target.get("longitude"))
        if lat is None or lon is None:
            continue
        hits = []
        for line in lines:
            distance = _distance_to_line_km(lat, lon, line.get("segments", []))
            if distance is None:
                continue
            if distance <= TARGET_REVIEW_RADIUS_KM:
                proximity_bonus = max(0.0, (TARGET_REVIEW_RADIUS_KM - distance) / 25.0)
                hits.append(
                    {
                        "line_id": line["id"],
                        "label": line["label"],
                        "planet": line["planet"],
                        "angle": line["angle"],
                        "distance_km": round(distance, 1),
                        "score": int(min(100, round(line["score"] + proximity_bonus))),
                        "score_label": line["score_label"],
                    }
                )
        hits.sort(key=lambda item: (item["score"], -item["distance_km"]), reverse=True)
        scored_targets.append(
            {
                "name": str(target.get("name") or target.get("city") or "Target"),
                "latitude": lat,
                "longitude": lon,
                "closest_symbolic_lines": hits[:5],
            }
        )
    return scored_targets


def _distance_to_line_km(
    lat: float, lon: float, segments: Any
) -> float | None:
    best: float | None = None
    if not isinstance(segments, list):
        return None
    for segment in segments:
        if not isinstance(segment, list):
            continue
        for point in segment:
            if not isinstance(point, Mapping):
                continue
            point_lat = _as_float(point.get("lat"))
            point_lon = _as_float(point.get("lon"))
            if point_lat is None or point_lon is None:
                continue
            distance = _haversine_km(lat, lon, point_lat, point_lon)
            if best is None or distance < best:
                best = distance
    return best


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_km = 6371.0088
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(_normalize_lon(lon2 - lon1))
    a = (
        math.sin(d_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2.0) ** 2
    )
    return radius_km * 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))


def _dignity_score(planet: str, longitude: float, sect: Sect) -> int | None:
    try:
        planet_enum = _planet_enum(planet)
        if planet_enum is None:
            return None
        return int(
            DignityCalculator.calculate_planet_dignity(
                planet_enum, longitude, sect
            ).get("total_score", 0)
        )
    except Exception as exc:
        logger.debug("Dignity score unavailable for %s: %s", planet, exc)
        return None


def _planet_enum(name: str) -> PlanetName | None:
    key = name.upper()
    if key == "NORTH NODE":
        key = "NORTH_NODE"
    if key == "SOUTH NODE":
        key = "SOUTH_NODE"
    try:
        return PlanetName[key]
    except KeyError:
        return None


def _sect(chart_data: Mapping[str, Any]) -> str:
    sect_type = _get(chart_data, "analysis", "sect", "type")
    if isinstance(sect_type, str) and sect_type.upper() in {"DAY", "NIGHT"}:
        return sect_type.upper()
    sun_altitude = _as_float(_get(chart_data, "astronomy", "planets", "Sun", "altitude"))
    return "DAY" if sun_altitude is None or sun_altitude >= 0 else "NIGHT"


def _sect_role(planet: str, sect: str) -> str:
    if planet == "Sun":
        return "luminary of sect" if sect == "DAY" else "contrary luminary"
    if planet == "Moon":
        return "luminary of sect" if sect == "NIGHT" else "contrary luminary"
    if planet == "Jupiter":
        return "benefic of sect" if sect == "DAY" else "benefic contrary to sect"
    if planet == "Venus":
        return "benefic of sect" if sect == "NIGHT" else "benefic contrary to sect"
    if planet == "Saturn":
        return "malefic of sect" if sect == "DAY" else "out-of-sect malefic"
    if planet == "Mars":
        return "malefic of sect" if sect == "NIGHT" else "out-of-sect malefic"
    if planet == "Mercury":
        return "sect-neutral translator"
    return "non-traditional point"


def _int_keyed_houses(value: Any) -> dict[int, float]:
    houses = {}
    if not isinstance(value, Mapping):
        return houses
    for key, raw in value.items():
        try:
            houses[int(key)] = float(raw)
        except (TypeError, ValueError):
            continue
    return houses


def _sign_name(longitude: float | None) -> str | None:
    if longitude is None:
        return None
    return list(Sign)[int((longitude % 360.0) / 30.0) % 12].value


def _normalize_lon(lon: float) -> float:
    return ((lon + 180.0) % 360.0) - 180.0


def _as_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _rounded(value: Any) -> float | None:
    number = _as_float(value)
    return round(number, 6) if number is not None else None


def _get(root: Mapping[str, Any], *keys: str) -> Any:
    cur: Any = root
    for key in keys:
        if not isinstance(cur, Mapping):
            return None
        cur = cur.get(key)
    return cur
