"""Render the premium astrology HTML report template from engine output."""

from __future__ import annotations

import html
import json
import math
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
REPORT_TEMPLATE_DIR = ROOT / "src" / "templates" / "reports"
REPORT_TEMPLATE_NAME = "astrology_report_template.html"
REPORT_CSS_NAME = "astrology_report_template.css"

SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]

SIGN_GLYPHS = {
    "Aries": "Ar",
    "Taurus": "Ta",
    "Gemini": "Ge",
    "Cancer": "Cn",
    "Leo": "Le",
    "Virgo": "Vi",
    "Libra": "Li",
    "Scorpio": "Sc",
    "Sagittarius": "Sg",
    "Capricorn": "Cp",
    "Aquarius": "Aq",
    "Pisces": "Pi",
}

PLANET_GLYPHS = {
    "Sun": "Su",
    "Moon": "Mo",
    "Mercury": "Me",
    "Venus": "Ve",
    "Mars": "Ma",
    "Jupiter": "Ju",
    "Saturn": "Sa",
    "North_Node": "NN",
    "South_Node": "SN",
}

TRADITIONAL_PLANETS = [
    "Sun",
    "Moon",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
]

NON_SEPTENER_BODY_PATTERN = re.compile(
    r"\b(?:Uranus|Neptune|Pluto|North[_\s]+Node|South[_\s]+Node)\b",
    re.IGNORECASE,
)

HOUSE_NAMES = {
    1: "Life and body",
    2: "Assets and movable goods",
    3: "Siblings, messages, short travel",
    4: "Parents, land, foundations",
    5: "Pleasure, children, creation",
    6: "Labor, illness, service",
    7: "Marriage and open counterparties",
    8: "Debt, death, other people's goods",
    9: "God, learning, long journeys",
    10: "Praxis, rank, public action",
    11: "Friends, patrons, hopes",
    12: "Hidden enemies, confinement, retreat",
}

SIGN_RULERS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def _get(mapping: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = mapping
    for key in keys:
        if not isinstance(current, Mapping) or key not in current:
            return default
        current = current[key]
    return current


def _clean_markdown(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"[*_~>]", "", text)
    text = re.sub(r"^\s*[-+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\|", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _trim_text(text: str, max_chars: int = 760) -> str:
    text = _clean_markdown(text)
    if len(text) <= max_chars:
        return text
    clipped = text[:max_chars].rsplit(".", 1)[0].strip()
    if len(clipped) < max_chars * 0.45:
        clipped = text[:max_chars].rsplit(" ", 1)[0].strip()
    return clipped.rstrip(".") + "."


def _traditional_scope_text(text: str) -> str:
    if not text or not NON_SEPTENER_BODY_PATTERN.search(text):
        return text
    sentences = re.split(r"(?<=[.!?])\s+", text)
    scoped = [sentence for sentence in sentences if not NON_SEPTENER_BODY_PATTERN.search(sentence)]
    return " ".join(scoped).strip()


def strip_raw_appendix(markdown: str) -> str:
    """Remove the raw appendix block while preserving the customer report body."""
    marker = re.search(r"(?mi)^\s*#{2,4}\s+Raw Natal Data \(Audit Appendix\)\s*$", markdown)
    if not marker:
        return markdown
    next_part = re.search(r"(?m)^#\s+Part\s+\d+\s*$", markdown[marker.end() :])
    if not next_part:
        return markdown[: marker.start()].rstrip()
    body_start = marker.end() + next_part.start()
    return (markdown[: marker.start()].rstrip() + "\n\n" + markdown[body_start:].lstrip()).strip()


def extract_section(markdown: str, title_terms: list[str], max_chars: int = 900) -> str:
    cleaned = strip_raw_appendix(markdown)
    headings = list(re.finditer(r"(?m)^(#{1,4})\s+(.+?)\s*$", cleaned))
    lowered_terms = [term.lower() for term in title_terms]
    for index, match in enumerate(headings):
        title = _clean_markdown(match.group(2)).lower()
        if all(term in title for term in lowered_terms):
            start = match.end()
            end = headings[index + 1].start() if index + 1 < len(headings) else len(cleaned)
            return _traditional_scope_text(_trim_text(cleaned[start:end], max_chars=max_chars))
    return ""


def _lon_to_sign(lon: float) -> str:
    return SIGNS[int((lon % 360) // 30)]


def _format_longitude(lon: float) -> str:
    wrapped = lon % 360
    sign = _lon_to_sign(wrapped)
    deg_float = wrapped % 30
    deg = int(deg_float)
    minute_float = (deg_float - deg) * 60
    minute = int(minute_float)
    second = int(round((minute_float - minute) * 60))
    if second == 60:
        second = 0
        minute += 1
    if minute == 60:
        minute = 0
        deg += 1
    return f"{sign} {deg:02d}°{minute:02d}'{second:02d}\""


def _fmt_position(value: Any) -> str:
    if isinstance(value, Mapping):
        formatted = _get(value, "longitude_fmt", "string")
        if formatted:
            return str(formatted)
        lon = value.get("longitude")
        if isinstance(lon, (int, float)):
            return _format_longitude(float(lon))
    if isinstance(value, (int, float)):
        return _format_longitude(float(value))
    return str(value or "Uncomputed")


def _setting_label(value: Any, fallback: str) -> str:
    if isinstance(value, Mapping):
        label = value.get("label") or value.get("name") or value.get("code")
        if label:
            return str(label)
        return fallback
    if value:
        return str(value)
    return fallback


def _xy(longitude: float, radius: float, center: float = 320.0) -> tuple[float, float]:
    angle = math.radians((longitude % 360) - 90)
    return center + math.cos(angle) * radius, center + math.sin(angle) * radius


def build_chart_wheel_svg(chart_data: Mapping[str, Any]) -> str:
    planets = _get(chart_data, "astronomy", "planets", default={}) or {}
    houses = _get(chart_data, "astronomy", "houses", default={}) or {}
    aspects = _get(chart_data, "analysis", "aspects", default=[]) or []

    lines: list[str] = [
        '<svg class="chart-wheel" viewBox="0 0 640 640" role="img" aria-label="Traditional chart wheel">',
        '<circle cx="320" cy="320" r="300"></circle>',
        '<circle cx="320" cy="320" r="246"></circle>',
        '<circle cx="320" cy="320" r="180"></circle>',
        '<circle cx="320" cy="320" r="74"></circle>',
    ]

    for degree in range(0, 360, 30):
        x1, y1 = _xy(degree, 246)
        x2, y2 = _xy(degree, 300)
        lines.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"></line>')
        sx, sy = _xy(degree + 15, 276)
        sign = _lon_to_sign(degree)
        lines.append(
            f'<text class="sign-label" x="{sx:.2f}" y="{sy:.2f}">{html.escape(SIGN_GLYPHS[sign])}</text>'
        )

    for house, cusp in sorted(houses.items(), key=lambda item: int(item[0])):
        if not isinstance(cusp, (int, float)):
            continue
        x1, y1 = _xy(float(cusp), 74)
        x2, y2 = _xy(float(cusp), 246)
        lines.append(
            f'<line class="house-cusp" x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"></line>'
        )
        hx, hy = _xy(float(cusp) + 15, 125)
        lines.append(f'<text class="house-label" x="{hx:.2f}" y="{hy:.2f}">{int(house)}</text>')

    planet_positions: dict[str, float] = {}
    for name, body in planets.items():
        if name not in TRADITIONAL_PLANETS or not isinstance(body, Mapping):
            continue
        lon = body.get("longitude")
        if not isinstance(lon, (int, float)):
            continue
        planet_positions[name] = float(lon)

    for aspect in aspects[:12]:
        a = aspect.get("planet_a") if isinstance(aspect, Mapping) else None
        b = aspect.get("planet_b") if isinstance(aspect, Mapping) else None
        if a not in planet_positions or b not in planet_positions:
            continue
        x1, y1 = _xy(planet_positions[str(a)], 178)
        x2, y2 = _xy(planet_positions[str(b)], 178)
        lines.append(
            f'<line class="aspect-line" x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"></line>'
        )

    planet_items: list[tuple[str, float]] = []
    for name in TRADITIONAL_PLANETS:
        lon = planet_positions.get(name)
        if lon is None:
            continue
        planet_items.append((name, lon))

    placed_lons: list[float] = []
    for name, lon in sorted(planet_items, key=lambda item: item[1] % 360):
        close_before = 0
        for previous in placed_lons:
            delta = abs((lon % 360) - (previous % 360))
            if min(delta, 360 - delta) < 9:
                close_before += 1
        placed_lons.append(lon)
        label_radius = 205 + (close_before * 18)
        label_lon = lon + (close_before * 1.8)
        x, y = _xy(label_lon, label_radius)
        lines.append(
            f'<text class="planet-label-svg" x="{x:.2f}" y="{y:.2f}">{html.escape(PLANET_GLYPHS[name])}</text>'
        )

    lines.append("</svg>")
    return "\n".join(lines)


def _planet_lookup(chart_data: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    planets = _get(chart_data, "analysis", "planets_forensic", default=[]) or []
    return {str(item.get("name")): item for item in planets if isinstance(item, Mapping)}


def _planet_position_rows(chart_data: Mapping[str, Any]) -> list[dict[str, str]]:
    lookup = _planet_lookup(chart_data)
    rows = []
    for name in TRADITIONAL_PLANETS:
        item = lookup.get(name)
        if not item:
            continue
        dignities = item.get("dignities") if isinstance(item.get("dignities"), Mapping) else {}
        accidental = item.get("accidental") if isinstance(item.get("accidental"), Mapping) else {}
        details = dignities.get("details") if isinstance(dignities, Mapping) else []
        if not details:
            details = item.get("details") or []
        retro = "Retrograde" if item.get("retrograde") else "Direct"
        condition_bits = []
        if isinstance(dignities, Mapping) and "total_score" in dignities:
            condition_bits.append(f"Essential {dignities['total_score']}")
        if isinstance(accidental, Mapping) and "total_score" in accidental:
            condition_bits.append(f"Accidental {accidental['total_score']}")
        if details:
            condition_bits.append(str(details[0]))
        rows.append(
            {
                "name": name.replace("_", " "),
                "sign": str(item.get("sign", "")),
                "degree": _fmt_position(item),
                "house": str(item.get("house", "")),
                "motion": retro,
                "condition": "; ".join(condition_bits),
            }
        )
    return rows


def _house_rows(chart_data: Mapping[str, Any]) -> list[dict[str, str]]:
    houses = _get(chart_data, "astronomy", "houses", default={}) or {}
    lookup = _planet_lookup(chart_data)
    planets_by_house: dict[int, list[str]] = {}
    for name, item in lookup.items():
        if name not in TRADITIONAL_PLANETS:
            continue
        house = item.get("house")
        if isinstance(house, int):
            planets_by_house.setdefault(house, []).append(name.replace("_", " "))
    rows = []
    for house_number in range(1, 13):
        cusp = houses.get(str(house_number))
        sign = _lon_to_sign(float(cusp)) if isinstance(cusp, (int, float)) else "Unknown"
        bodies = ", ".join(planets_by_house.get(house_number, []))
        topic = HOUSE_NAMES[house_number]
        if bodies:
            summary = f"{sign} topics: {topic}. Bodies present: {bodies}."
        else:
            ruler = SIGN_RULERS.get(sign, "the sign ruler")
            summary = f"{sign} topics: {topic}. No listed planet is in this house; judge through {ruler}."
        rows.append({"number": str(house_number), "name": f"{sign}: {topic}", "summary": summary})
    return rows


def _dignity_rows(chart_data: Mapping[str, Any]) -> list[dict[str, str | int]]:
    lookup = _planet_lookup(chart_data)
    rows = []
    scores = []
    for item in lookup.values():
        dignities = item.get("dignities") if isinstance(item.get("dignities"), Mapping) else {}
        score = dignities.get("total_score")
        if isinstance(score, (int, float)):
            scores.append(float(score))
    low = min(scores or [0])
    high = max(scores or [1])
    span = high - low or 1
    for name in TRADITIONAL_PLANETS:
        item = lookup.get(name)
        if not item:
            continue
        dignities = item.get("dignities") if isinstance(item.get("dignities"), Mapping) else {}
        score = dignities.get("total_score", 0)
        details = dignities.get("details") if isinstance(dignities, Mapping) else []
        if not details:
            details = item.get("details") or []
        condition = ", ".join(str(detail) for detail in details[:2])
        if not condition:
            condition = f"Computed point in {item.get('sign')} house {item.get('house')}"
        percent = int(18 + ((float(score) - low) / span) * 74)
        rows.append(
            {
                "planet": name.replace("_", " "),
                "condition": condition,
                "percent": percent,
                "total": str(score),
            }
        )
    return rows


def _accidental_rows(chart_data: Mapping[str, Any]) -> list[dict[str, Any]]:
    lookup = _planet_lookup(chart_data)
    rows = []
    for name in TRADITIONAL_PLANETS:
        item = lookup.get(name)
        if not item:
            continue
        accidental = item.get("accidental") if isinstance(item.get("accidental"), Mapping) else {}
        notes = [str(note) for note in accidental.get("details", [])]
        if item.get("solar_status"):
            notes.append(f"Solar status: {item['solar_status']}")
        if not notes:
            notes = [f"House {item.get('house')} with solar status {item.get('solar_status', 'not classified')}."]
        rows.append({"planet": name, "notes": notes})
    return rows


def _temperament_context(chart_data: Mapping[str, Any], markdown: str) -> dict[str, Any]:
    temperament = _get(chart_data, "analysis", "temperament", default={}) or {}
    scores = temperament.get("scores") if isinstance(temperament, Mapping) else {}
    max_score = max([float(value) for value in scores.values()] or [1])
    bars = [
        {
            "label": label,
            "value": str(value),
            "percent": int((float(value) / max_score) * 100),
        }
        for label, value in scores.items()
    ]
    interpretation = extract_section(markdown, ["temperament"], 560)
    if not interpretation:
        primary = temperament.get("primary_temperament", "Not recorded")
        net = temperament.get("net_balance", {})
        interpretation = f"The computed temperament is {primary}. Net balance: {net}."
    return {"bars": bars, "interpretation": interpretation}


def _aspect_rows(chart_data: Mapping[str, Any]) -> list[dict[str, str]]:
    aspects = _get(chart_data, "analysis", "aspects", default=[]) or []
    rows = []
    for aspect in aspects:
        if not isinstance(aspect, Mapping):
            continue
        bodies = f"{aspect.get('planet_a')} {aspect.get('type')} {aspect.get('planet_b')}"
        if aspect.get("planet_a") not in TRADITIONAL_PLANETS or aspect.get("planet_b") not in TRADITIONAL_PLANETS:
            continue
        orb = aspect.get("orb")
        rows.append(
            {
                "bodies": bodies,
                "orb": f"{float(orb):.2f} deg" if isinstance(orb, (int, float)) else "",
                "condition": "Applying" if aspect.get("is_applying") else "Separating",
                "interpretation": str(aspect.get("text") or "Computed core septener aspect."),
            }
        )
    return rows


def _reception_rows(chart_data: Mapping[str, Any]) -> list[dict[str, str]]:
    receptions = _get(chart_data, "analysis", "teams", "receptions", default=[]) or []
    rows = []
    for item in receptions:
        if not isinstance(item, Mapping):
            continue
        if item.get("planet_a") not in TRADITIONAL_PLANETS or item.get("planet_b") not in TRADITIONAL_PLANETS:
            continue
        score = item.get("score")
        rows.append(
            {
                "from": str(item.get("planet_a", "")),
                "to": str(item.get("planet_b", "")),
                "type": str(item.get("type", "")),
                "interpretation": f"Reception score {score}; {item.get('planet_a')} in {item.get('planet_a_sign')} and {item.get('planet_b')} in {item.get('planet_b_sign')}.",
            }
        )
    return rows


def _lot_rows(chart_data: Mapping[str, Any]) -> list[dict[str, str]]:
    lots = _get(chart_data, "analysis", "fate", "hermetic_lots", default={}) or {}
    rows = []
    for name, item in list(lots.items())[:8]:
        if not isinstance(item, Mapping):
            continue
        position = _fmt_position(item)
        status = item.get("status", "Not recorded")
        ruler = item.get("ruler", "ruler not recorded")
        rows.append(
            {
                "name": str(name),
                "position": position,
                "interpretation": f"House {item.get('house')}; ruled by {ruler}; status: {status}.",
            }
        )
    return rows


def _birth_datetime(meta: Mapping[str, Any], chart: Mapping[str, Any]) -> datetime | None:
    date_text = str(meta.get("birth_date") or chart.get("date") or "").strip()
    time_text = str(meta.get("birth_time") or chart.get("time") or "00:00").strip()
    if not date_text:
        return None
    try:
        return datetime.fromisoformat(f"{date_text[:10]}T{time_text[:5] or '00:00'}:00")
    except ValueError:
        try:
            return datetime.fromisoformat(date_text[:10])
        except ValueError:
            return None


def _spirit_peak_context(
    chart_data: Mapping[str, Any],
    meta: Mapping[str, Any],
    chart: Mapping[str, Any],
    firdaria: Mapping[str, Any],
) -> dict[str, str]:
    lots = _get(chart_data, "analysis", "fate", "hermetic_lots", default={}) or {}
    spirit = lots.get("Spirit") if isinstance(lots, Mapping) else None
    if not isinstance(spirit, Mapping):
        return {
            "position": "Not recorded",
            "spirit_sign": "Not recorded",
            "peak_sign": "Not calculated",
            "active_stack": "Not calculated",
            "status": "Lot of Spirit not present in this chart artifact.",
        }

    spirit_lon = spirit.get("longitude")
    spirit_sign = str(spirit.get("sign") or "")
    if not spirit_sign and isinstance(spirit_lon, (int, float)):
        spirit_sign = _lon_to_sign(float(spirit_lon))

    if spirit_sign not in SIGNS:
        return {
            "position": _fmt_position(spirit),
            "spirit_sign": spirit_sign or "Not recorded",
            "peak_sign": "Not calculated",
            "active_stack": "Not calculated",
            "status": "Lot of Spirit sign is unavailable.",
        }

    spirit_index = SIGNS.index(spirit_sign)
    peak_sign = SIGNS[(spirit_index + 9) % 12]
    counter_peak_sign = SIGNS[(spirit_index + 3) % 12]
    birth_dt = _birth_datetime(meta, chart)
    current_age = firdaria.get("Current Age") if isinstance(firdaria, Mapping) else None
    if birth_dt and isinstance(current_age, (int, float)):
        target_dt = birth_dt + timedelta(days=float(current_age) * 365.25)
    else:
        target_dt = birth_dt

    periods: Mapping[str, Any] = {}
    if birth_dt and target_dt:
        try:
            from src.engine.models import Sign
            from src.engine.prediction import calculate_zr_periods

            spirit_enum = next(sign for sign in Sign if sign.value == spirit_sign)
            periods = calculate_zr_periods(spirit_enum, birth_dt, target_dt)
        except (ImportError, StopIteration, ValueError, TypeError, KeyError) as exc:
            periods = {"note": f"Zodiacal Releasing unavailable: {exc}"}

    def level_status(sign_name: str) -> str:
        if sign_name == peak_sign:
            return "peak"
        if sign_name == counter_peak_sign:
            return "counter-peak"
        return "standard"

    active_parts = []
    for level in ["Level 1", "Level 2", "Level 3"]:
        sign_name = str(periods.get(level, ""))
        if sign_name:
            active_parts.append(f"{level.replace('Level ', 'L')}: {sign_name} ({level_status(sign_name)})")

    status = "10th sign from Spirit marks the peak period; 4th sign marks the counter-peak."
    if periods.get("Status"):
        status = f"{periods['Status']}; {status}"

    return {
        "position": _fmt_position(spirit),
        "spirit_sign": spirit_sign,
        "peak_sign": peak_sign,
        "active_stack": "; ".join(active_parts) or str(periods.get("note") or "Not calculated"),
        "status": status,
    }


def _technical_readout(
    chart: Mapping[str, Any],
    sect: str,
    firdaria: Mapping[str, Any],
    profection: Mapping[str, Any],
    spirit_peak: Mapping[str, str],
) -> dict[str, Any]:
    house_system = _setting_label(chart.get("house_system"), "Whole Sign")
    zodiac_system = _setting_label(chart.get("zodiac_system"), "Tropical")
    current_firdaria = f"{firdaria.get('Major Period', '')} / {firdaria.get('Sub Period', '')}".strip(" /")
    current_profection = f"{profection.get('annual_sign', '')} ruled by {profection.get('lord_of_year', '')}".strip()
    return {
        "summary": (
            "This chart is rendered as a Traditional/Hellenistic calculation grid: seven visible planets, "
            "Whole Sign houses, sect-first weighting, essential and accidental dignity, lots, and time-lord logic. "
            "It is not a modern personality-box chart and it does not use non-septener bodies as interpretive rulers."
        ),
        "badges": [
            "7 visible planets",
            "Whole Sign houses",
            "Sect first",
            "Essential dignity",
            "Firdaria",
            "Spirit Lot peak",
        ],
        "rows": [
            {
                "label": "Planet set",
                "value": "Septener only",
                "detail": ", ".join(TRADITIONAL_PLANETS),
            },
            {
                "label": "Non-septener bodies",
                "value": "Excluded",
                "detail": "Not displayed in the chart grid and not used as sign rulers.",
            },
            {
                "label": "House framework",
                "value": house_system,
                "detail": f"Whole Sign topics are used; quadrant angles are reported separately. Zodiac: {zodiac_system}.",
            },
            {
                "label": "Sect",
                "value": sect,
                "detail": "Day/night status changes benefic and malefic weighting before synthesis.",
            },
            {
                "label": "Rulership and dignity",
                "value": "Computed",
                "detail": "Traditional sign rulers plus domicile, exaltation, triplicity, term, face, house, speed, retrogradation, and solar condition.",
            },
            {
                "label": "Time lords",
                "value": current_firdaria or "Not recorded",
                "detail": f"Annual profection: {current_profection or 'not recorded'}.",
            },
            {
                "label": "Spirit Lot peak",
                "value": spirit_peak.get("peak_sign", "Not calculated"),
                "detail": f"Lot of Spirit at {spirit_peak.get('position', 'not recorded')}; active stack: {spirit_peak.get('active_stack', 'not calculated')}.",
            },
        ],
    }


def _primary_direction_rows(chart_data: Mapping[str, Any]) -> list[dict[str, str]]:
    directions = _get(chart_data, "analysis", "fate", "primary_directions", default=[]) or []
    rows = []
    birth_year = int(str(_get(chart_data, "meta", "birth_date", default="1996"))[:4])
    for item in directions[:8]:
        if not isinstance(item, Mapping):
            continue
        years = item.get("years")
        year_text = ""
        if isinstance(years, (int, float)):
            year_text = str(round(birth_year + float(years), 1))
        rows.append(
            {
                "date": year_text or str(item.get("date_offset", "")),
                "promissor": str(item.get("promittor", "")),
                "significator": str(item.get("significator", "")),
                "interpretation": f"{item.get('aspect')} direction; offset {item.get('date_offset')}.",
            }
        )
    return rows


def _next_year_months() -> list[dict[str, str]]:
    labels = ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"]
    focuses = [
        "Read through the profected house and Lord of the Year.",
        "Review Mercury topics before committing to new obligations.",
        "Treat alliance volatility as a chart condition, not a surprise.",
        "Use Saturnian discipline where shared resources are involved.",
        "Keep public commitments narrower and better documented.",
        "Let the 6th-house year emphasize maintenance and workflow.",
        "Return to the strongest natal resource: Mercury in Virgo.",
        "Separate useful solitude from avoidant isolation.",
        "Recheck promises attached to friends, patrons, and networks.",
        "Prioritize clear terms around money and shared risk.",
        "Use fixed-star intensity with composure and restraint.",
        "Close the year by simplifying obligations before expansion.",
    ]
    return [{"label": label, "focus": focus} for label, focus in zip(labels, focuses)]


def build_report_context(
    chart_data: Mapping[str, Any],
    report_markdown: str,
    *,
    title: str = "Classical Nativity Report",
    brand_name: str = "traditional-astrology.com",
) -> dict[str, Any]:
    meta = chart_data.get("meta", {}) if isinstance(chart_data.get("meta"), Mapping) else {}
    chart = meta.get("chart", {}) if isinstance(meta.get("chart"), Mapping) else {}
    subject = str(meta.get("subject_name") or chart.get("name") or "Native")
    city = str(meta.get("city") or chart.get("city") or "")
    state = str(meta.get("state") or chart.get("state") or "")
    location = ", ".join(part for part in [city, state] if part)
    birth_date = str(meta.get("birth_date") or chart.get("date") or "")
    birth_time = str(meta.get("birth_time") or chart.get("time") or "")
    timezone = str(meta.get("timezone") or chart.get("timezone") or "")
    utc_time = str(meta.get("utc_time") or chart.get("utc_time") or "")
    lat = meta.get("lat") or chart.get("lat")
    lon = meta.get("lon") or chart.get("lon")

    sect = str(_get(chart_data, "analysis", "sect", "type", default="Not recorded")).title()
    asc = _fmt_position(_get(chart_data, "analysis", "angles", "Ascendant", default={}))
    mc = _fmt_position(_get(chart_data, "analysis", "angles", "Midheaven", default={}))
    asc_lon = _get(chart_data, "analysis", "angles", "Ascendant", "longitude")
    mc_lon = _get(chart_data, "analysis", "angles", "Midheaven", "longitude")
    descendant = _format_longitude(float(asc_lon) + 180) if isinstance(asc_lon, (int, float)) else "Uncomputed"
    ic = _format_longitude(float(mc_lon) + 180) if isinstance(mc_lon, (int, float)) else "Uncomputed"
    almuten = str(_get(chart_data, "analysis", "dignity", "almuten", "winner", default="Not recorded"))

    lookup = _planet_lookup(chart_data)
    asc_sign = _lon_to_sign(float(asc_lon)) if isinstance(asc_lon, (int, float)) else ""
    asc_ruler = SIGN_RULERS.get(asc_sign, "Ascendant ruler")
    asc_ruler_data = lookup.get(asc_ruler, {})
    asc_ruler_details = asc_ruler_data.get("details", []) if isinstance(asc_ruler_data, Mapping) else []

    firdaria = _get(chart_data, "analysis", "fate", "firdaria", default={}) or {}
    profection = _get(chart_data, "analysis", "enhanced_profections", default={}) or {}
    solar_return = _get(chart_data, "analysis", "solar_return", default={}) or {}
    raw_stars = _get(chart_data, "analysis", "supplemental", "stars", default=[]) or []
    stars = [
        star
        for star in raw_stars
        if not isinstance(star, Mapping) or star.get("planet_name") in TRADITIONAL_PLANETS
    ]
    spirit_peak = _spirit_peak_context(chart_data, meta, chart, firdaria)

    opening = extract_section(report_markdown, ["natal chart audit"], 680)
    if not opening:
        opening = (
            f"This report renders the {birth_date} {birth_time} nativity for {subject}, "
            f"calculated for {location}. It prioritizes sect, dignity, angularity, reception, and timing."
        )

    return {
        "report": {
            "title": title,
            "brand": {"name": brand_name},
            "client": {"display_name": subject},
            "birth": {
                "date": birth_date,
                "time": birth_time,
                "location": location,
                "audit_rows": [
                    {"label": "Coordinates", "value": f"{lat}, {lon}"},
                    {"label": "Timezone", "value": timezone},
                    {"label": "UTC", "value": utc_time},
                    {"label": "House system", "value": _setting_label(chart.get("house_system"), "Whole Sign")},
                    {"label": "Zodiac", "value": _setting_label(chart.get("zodiac_system"), "Tropical")},
                    {"label": "Source report", "value": "premium report markdown plus engine chart data"},
                ],
            },
            "opening_letter": opening,
            "summary": {"sect": sect, "ascendant": asc, "almuten": almuten},
            "at_a_glance": [
                {
                    "label": "Sect",
                    "value": sect,
                    "interpretation": f"Sun altitude: {_get(chart_data, 'analysis', 'sect', 'sun_altitude_deg', default='not recorded')} deg.",
                },
                {
                    "label": "Almuten",
                    "value": almuten,
                    "interpretation": f"Computed score: {_get(chart_data, 'analysis', 'dignity', 'almuten', 'score', default='not recorded')}.",
                },
                {
                    "label": "Ascendant",
                    "value": asc,
                    "interpretation": f"Ascendant ruler: {asc_ruler}.",
                },
                {
                    "label": "Current timing",
                    "value": f"{firdaria.get('Major Period', '')} / {firdaria.get('Sub Period', '')}".strip(" /"),
                    "interpretation": f"Annual sign {profection.get('annual_sign')}; Lord of Year {profection.get('lord_of_year')}.",
                },
            ],
            "conversion": {
                "primary_recommendation": (
                    f"The most useful follow-up is an annual timing review: age {profection.get('age')} "
                    f"activates {profection.get('annual_sign')} with {profection.get('lord_of_year')} as Lord of the Year."
                )
            },
            "technical_readout": _technical_readout(chart, sect, firdaria, profection, spirit_peak),
            "chart": {
                "wheel_svg": build_chart_wheel_svg(chart_data),
                "house_cusps": [],
                "planets": [],
                "planet_set": ", ".join(TRADITIONAL_PLANETS),
            },
            "angles": {
                "ascendant": asc,
                "midheaven": mc,
                "descendant": descendant,
                "imum_coeli": ic,
            },
            "method": {
                "calculation_note": str(_get(chart_data, "analysis", "angles", "note", default="Whole Sign topics with MC reported separately.")),
                "steps": [
                    {"number": "01", "title": "Birth data", "description": "Birth date, clock time, place, timezone, and coordinates are taken from the engine chart data."},
                    {"number": "02", "title": "Sect", "description": "Sect is determined by the Sun's altitude above or below the horizon."},
                    {"number": "03", "title": "Dignity", "description": "Essential dignity uses the engine's configured rulership, exaltation, triplicity, term, and face logic."},
                    {"number": "04", "title": "Condition", "description": "Accidental condition includes house strength, speed, visibility, retrogradation, and solar status."},
                    {"number": "05", "title": "Reception", "description": "Receptions are taken from the engine's standard Lilly reception calculation with sect-gated triplicity rights."},
                    {"number": "06", "title": "Timing", "description": "Annual profection, firdaria, solar return, and primary directions are rendered from computed timing outputs."},
                ],
            },
            "planets": _planet_position_rows(chart_data),
            "houses": _house_rows(chart_data),
            "sect": {
                "heading": f"{sect} chart: sect changes the benefic and malefic priorities",
                "light_analysis": extract_section(report_markdown, ["sect"], 620)
                or f"The engine calculated a {sect} chart from Sun altitude. Jupiter is the benefic of sect in a day chart; Mars is the out-of-sect malefic.",
                "benefic_malefic_analysis": (
                    f"Constructive team: {', '.join(_get(chart_data, 'analysis', 'teams', 'constructive_team', default=[]))}. "
                    f"Destructive team: {', '.join(_get(chart_data, 'analysis', 'teams', 'destructive_team', default=[]))}."
                ),
                "customer_translation": "Read every planetary promise through this day/night distinction before deciding whether a testimony helps, strains, delays, or destabilizes.",
            },
            "dignities": _dignity_rows(chart_data),
            "accidental_conditions": _accidental_rows(chart_data),
            "temperament": _temperament_context(chart_data, report_markdown),
            "ascendant_ruler": {
                "title": f"{asc_ruler} rules the Ascendant",
                "analysis": extract_section(report_markdown, [asc_ruler], 700)
                or f"{asc_ruler} is the ruler of {asc_sign}. Recorded details: {', '.join(str(item) for item in asc_ruler_details[:3])}.",
                "customer_takeaway": f"Treat {asc_ruler}'s condition as the operating style of the whole nativity.",
            },
            "luminaries": {
                "sun": {
                    "title": f"Sun at {_fmt_position(lookup.get('Sun', {}))}",
                    "analysis": extract_section(report_markdown, ["sun"], 700),
                    "evidence": [
                        {"label": "House", "value": str(_get(lookup, "Sun", "house", default=""))},
                        {"label": "Solar status", "value": str(_get(lookup, "Sun", "solar_status", default=""))},
                        {"label": "Dignity", "value": str(_get(lookup, "Sun", "dignities", "total_score", default=""))},
                    ],
                },
                "moon": {
                    "title": f"Moon at {_fmt_position(lookup.get('Moon', {}))}",
                    "analysis": extract_section(report_markdown, ["moon"], 700),
                    "evidence": [
                        {"label": "House", "value": str(_get(lookup, "Moon", "house", default=""))},
                        {"label": "Solar status", "value": str(_get(lookup, "Moon", "solar_status", default=""))},
                        {"label": "Dignity", "value": str(_get(lookup, "Moon", "dignities", "total_score", default=""))},
                    ],
                },
            },
            "personal_planets": [
                {
                    "planet": planet,
                    "title": f"{planet} at {_fmt_position(lookup.get(planet, {}))}",
                    "analysis": extract_section(report_markdown, [planet], 620)
                    or f"{planet} is recorded in house {_get(lookup, planet, 'house', default='')} with essential score {_get(lookup, planet, 'dignities', 'total_score', default='')}.",
                }
                for planet in ["Mercury", "Venus", "Mars"]
            ],
            "social_planets": [
                {
                    "planet": planet,
                    "title": f"{planet} at {_fmt_position(lookup.get(planet, {}))}",
                    "analysis": extract_section(report_markdown, [planet], 700)
                    or f"{planet} is recorded in house {_get(lookup, planet, 'house', default='')} with essential score {_get(lookup, planet, 'dignities', 'total_score', default='')}.",
                }
                for planet in ["Jupiter", "Saturn"]
            ],
            "aspects": _aspect_rows(chart_data),
            "receptions": _reception_rows(chart_data),
            "lots": _lot_rows(chart_data),
            "almuten": {
                "title": f"{almuten} is the Almuten Figuris",
                "score_basis": str(_get(chart_data, "analysis", "dignity", "almuten", "breakdown", default={})),
                "interpretation": extract_section(report_markdown, ["master", "nativity"], 720)
                or f"{almuten} has the highest recorded almuten score in this run.",
            },
            "stars_and_mansions": [
                {
                    "name": str(star.get("name", "Fixed star")) if isinstance(star, Mapping) else "Fixed star",
                    "interpretation": str(star.get("interpretation") or star.get("note") or star) if isinstance(star, Mapping) else str(star),
                }
                for star in stars[:4]
            ]
            or [{"name": "Fixed stars", "interpretation": extract_section(report_markdown, ["fixed stars"], 650)}],
            "timing": {
                "profection": {
                    "title": f"Age {profection.get('age')} profects to {profection.get('annual_sign')}",
                    "age": str(profection.get("age", "")),
                    "house": str(profection.get("annual_sign", "")),
                    "lord": str(profection.get("lord_of_year", "")),
                    "interpretation": extract_section(report_markdown, ["annual profection"], 680)
                    or f"Lord of the Year: {profection.get('lord_of_year')}. Daily sign: {profection.get('daily_sign')}.",
                },
                "firdaria": {
                    "periods": [
                        {
                            "state": "current",
                            "dates": f"{firdaria.get('Major Start')} to {firdaria.get('Major End')}",
                            "ruler": str(firdaria.get("Major Period", "")),
                            "interpretation": f"Major period; current age {firdaria.get('Current Age')}.",
                        },
                        {
                            "state": "current",
                            "dates": f"{firdaria.get('Sub Start')} to {firdaria.get('Sub End')}",
                            "ruler": str(firdaria.get("Sub Period", "")),
                            "interpretation": "Subperiod nested inside the major firdaria period.",
                        },
                    ]
                },
                "spirit_peak": spirit_peak,
                "solar_return": {
                    "title": f"Solar Return {solar_return.get('year', '')}",
                    "emphasis": "; ".join(
                        str(item.get("judgment"))
                        for item in solar_return.get("determinations", [])
                        if isinstance(item, Mapping) and item.get("planet") in TRADITIONAL_PLANETS
                    )[:760],
                    "customer_use": str(solar_return.get("morin_axiom", "")),
                },
                "primary_directions": _primary_direction_rows(chart_data),
                "next_year": {"title": "Next twelve months from the current timing stack", "months": _next_year_months()},
            },
            "synthesis": {
                "title": "The testimony centers on Mercury managing structural pressure",
                "themes": [
                    {
                        "title": "Primary strength",
                        "analysis": extract_section(report_markdown, ["mercury"], 760),
                    },
                    {
                        "title": "Main structural pressure",
                        "analysis": extract_section(report_markdown, ["escape hatch"], 760)
                        or extract_section(report_markdown, ["mutual receptions"], 760),
                    },
                    {
                        "title": "Timing forecast",
                        "analysis": extract_section(report_markdown, ["timing forecast"], 760)
                        or extract_section(report_markdown, ["decade ahead"], 760),
                    },
                ],
            },
            "reflection_prompts": [
                "Which chart strength is actually usable right now?",
                "Which timing factor deserves action, and which one is only background noise?",
                "Where does the report ask for restraint rather than prediction?",
            ],
            "next_steps": {
                "heading": "Continue with the timing question, not a generic repeat reading",
                "body": "The chart is already calculation-heavy. The useful next step is focused timing, compatibility, or horary only when there is a concrete question.",
                "qr_svg": "",
                "actions": [
                    {"url": "/#get-reading", "label": "Timing", "title": "Annual review", "description": "Use the current profection and firdaria stack for a focused year-ahead read."},
                    {"url": "/compatibility.html", "label": "Relationship", "title": "Compatibility chart", "description": "Compare two charts through traditional testimony instead of generic matching."},
                    {"url": "/horary.html", "label": "Question", "title": "Horary Oracle", "description": "Use a separate horary chart for one live, concrete question."},
                ],
            },
        }
    }


def render_html_report(
    chart_data: Mapping[str, Any],
    report_markdown: str,
    output_dir: str | Path,
    *,
    basename: str = "astrology_report",
    title: str = "Classical Nativity Report",
    brand_name: str = "traditional-astrology.com",
) -> Path:
    try:
        from jinja2 import Environment, FileSystemLoader, select_autoescape
    except ImportError as exc:
        raise RuntimeError("Jinja2 is required to render the HTML report template.") from exc

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPORT_TEMPLATE_DIR / REPORT_CSS_NAME, output_path / REPORT_CSS_NAME)

    env = Environment(
        loader=FileSystemLoader(str(REPORT_TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template(REPORT_TEMPLATE_NAME)
    context = build_report_context(chart_data, report_markdown, title=title, brand_name=brand_name)
    rendered = template.render(**context)
    html_path = output_path / f"{basename}.html"
    html_path.write_text(rendered, encoding="utf-8")
    return html_path


def export_pdf_with_playwright(html_path: str | Path, pdf_path: str | Path) -> Path:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("Playwright is required for PDF export from the HTML report.") from exc

    html_path = Path(html_path).resolve()
    pdf_path = Path(pdf_path)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 816, "height": 1056}, device_scale_factor=1)
        page.goto(html_path.as_uri(), wait_until="load")
        page.pdf(
            path=str(pdf_path),
            format="Letter",
            print_background=True,
            prefer_css_page_size=True,
        )
        browser.close()
    return pdf_path


def capture_report_screenshot(html_path: str | Path, image_path: str | Path) -> Path:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("Playwright is required for HTML report screenshots.") from exc

    html_path = Path(html_path).resolve()
    image_path = Path(image_path)
    image_path.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 816, "height": 1056}, device_scale_factor=1)
        page.goto(html_path.as_uri(), wait_until="load")
        page.screenshot(path=str(image_path), full_page=False)
        browser.close()
    return image_path
