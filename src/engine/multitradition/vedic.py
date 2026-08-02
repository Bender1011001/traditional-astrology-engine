"""Vedic (sidereal) section: rasi, nakshatra, whole-sign houses, Vimshottari.

Calculation reuses the shipping Swiss Ephemeris calculator in sidereal mode. The
ayanamsa is a configured choice: the engine supports eight, and no research pack
selects one, so Lahiri is disclosed with its alternatives rather than assumed.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import swisseph as swe

from .types import BirthInput, DisclosureKind, EvidenceGrade, TraditionSection

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
SIGN_LORD = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada",
    "Revati",
]
# Vimshottari lord order; the nakshatra lords repeat this nine-fold sequence.
DASHA_SEQUENCE: list[tuple[str, int]] = [
    ("Ketu", 7), ("Venus", 20), ("Sun", 6), ("Moon", 10), ("Mars", 7),
    ("Rahu", 18), ("Jupiter", 16), ("Saturn", 19), ("Mercury", 17),
]
DASHA_YEARS = dict(DASHA_SEQUENCE)
DASHA_TOTAL_YEARS = 120
SIDEREAL_YEAR_DAYS = 365.2425
NAKSHATRA_SPAN = 360.0 / 27.0

GRAHAS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
OWN_SIGNS = {
    "Sun": {"Leo"}, "Moon": {"Cancer"}, "Mercury": {"Gemini", "Virgo"},
    "Venus": {"Taurus", "Libra"}, "Mars": {"Aries", "Scorpio"},
    "Jupiter": {"Sagittarius", "Pisces"}, "Saturn": {"Capricorn", "Aquarius"},
}
EXALTATION = {
    "Sun": "Aries", "Moon": "Taurus", "Mercury": "Virgo", "Venus": "Pisces",
    "Mars": "Capricorn", "Jupiter": "Cancer", "Saturn": "Libra",
}
DEBILITATION = {
    "Sun": "Libra", "Moon": "Scorpio", "Mercury": "Pisces", "Venus": "Virgo",
    "Mars": "Cancer", "Jupiter": "Capricorn", "Saturn": "Aries",
}
AYANAMSA_ALTERNATIVES = (
    "Fagan-Bradley", "Krishnamurti", "Raman", "True Citra", "True Revati",
    "Surya Siddhanta", "Hipparchos",
)


def _sign_of(longitude: float) -> tuple[str, float]:
    index = int((longitude % 360) // 30)
    return SIGNS[index], (longitude % 360) - index * 30


def _nakshatra_of(longitude: float) -> tuple[str, str, int, float]:
    lon = longitude % 360
    index = int(lon // NAKSHATRA_SPAN)
    into = lon - index * NAKSHATRA_SPAN
    pada = int(into // (NAKSHATRA_SPAN / 4)) + 1
    lord = DASHA_SEQUENCE[index % 9][0]
    return NAKSHATRAS[index], lord, pada, into / NAKSHATRA_SPAN


def _dignity(graha: str, sign: str) -> str:
    if sign == EXALTATION.get(graha):
        return "exalted"
    if sign == DEBILITATION.get(graha):
        return "debilitated"
    if sign in OWN_SIGNS.get(graha, set()):
        return "own sign"
    return "neutral placement"


def build(birth: BirthInput, chart: Any) -> TraditionSection:
    """Build the Vedic section from a sidereal chart produced by ChartCalculator."""
    section = TraditionSection(
        tradition_id="indian_jyotisha",
        display_name="Vedic (Jyotisha)",
        evidence_grade=EvidenceGrade.CONFIGURED,
        basis=(
            "Swiss Ephemeris sidereal positions; whole-sign houses; "
            "Vimshottari dasha keyed to the Moon's nakshatra."
        ),
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Ayanamsa",
        "Lahiri (Chitrapaksha) selected. The engine supports eight ayanamsas and "
        "no validated research pack selects one; a different choice shifts every "
        "sidereal longitude and can move a placement across a sign boundary.",
        AYANAMSA_ALTERNATIVES,
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "House system",
        "Whole-sign houses, the dominant classical Jyotisha convention. "
        "Sripati and equal-house variants exist and would move cusp-adjacent "
        "placements.",
        ("Sripati", "Equal house from the lagna degree"),
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Nodes",
        "Mean nodes used for Rahu/Ketu. True-node calculation differs by up to "
        "about 1.5 degrees and is a live disagreement between schools.",
        ("True node",),
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Interpretation depth",
        "This section reports calculation and structural condition only. "
        "Divisional charts beyond D1, Shadbala, and Ashtakavarga are not "
        "computed, so no strength claim depending on them is made.",
    )

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(chart.jd)

    planet_map = {p.name.value: p for p in chart.planets}
    asc_sign, asc_deg = _sign_of(chart.ascendant)
    asc_index = SIGNS.index(asc_sign)
    asc_nak, asc_nak_lord, asc_pada, _ = _nakshatra_of(chart.ascendant)

    grahas: list[dict[str, Any]] = []
    for name in GRAHAS:
        planet = planet_map.get(name)
        if planet is None:
            continue
        sign, degree = _sign_of(planet.longitude)
        nak, nak_lord, pada, _ = _nakshatra_of(planet.longitude)
        grahas.append({
            "graha": name,
            "rasi": sign,
            "degree_in_sign": round(degree, 4),
            "house": (SIGNS.index(sign) - asc_index) % 12 + 1,
            "nakshatra": nak,
            "pada": pada,
            "nakshatra_lord": nak_lord,
            "dignity": _dignity(name, sign),
            "retrograde": getattr(planet, "speed", 0.0) < 0,
        })

    # Rahu/Ketu live in chart.planets; the scalar chart.north_node field is unused.
    for label, key in (("Rahu", "North_Node"), ("Ketu", "South_Node")):
        node = planet_map.get(key)
        if node is None:
            continue
        sign, degree = _sign_of(node.longitude)
        nak, nak_lord, pada, _ = _nakshatra_of(node.longitude)
        grahas.append({
            "graha": label,
            "rasi": sign,
            "degree_in_sign": round(degree, 4),
            "house": (SIGNS.index(sign) - asc_index) % 12 + 1,
            "nakshatra": nak,
            "pada": pada,
            "nakshatra_lord": nak_lord,
            "dignity": "not assessed for nodes",
            "retrograde": True,
        })

    moon = planet_map["Moon"]
    moon_nak, moon_lord, moon_pada, elapsed = _nakshatra_of(moon.longitude)
    dashas = _vimshottari(birth, moon_lord, elapsed)

    section.facts = {
        "ayanamsa_degrees": round(ayanamsa, 6),
        "lagna": {
            "rasi": asc_sign,
            "degree_in_sign": round(asc_deg, 4),
            "lord": SIGN_LORD[asc_sign],
            "nakshatra": asc_nak,
            "pada": asc_pada,
            "nakshatra_lord": asc_nak_lord,
        },
        "janma_rasi": _sign_of(moon.longitude)[0],
        "janma_nakshatra": {"name": moon_nak, "pada": moon_pada, "lord": moon_lord},
        "grahas": grahas,
        "houses": [
            {
                "house": h,
                "rasi": SIGNS[(asc_index + h - 1) % 12],
                "lord": SIGN_LORD[SIGNS[(asc_index + h - 1) % 12]],
            }
            for h in range(1, 13)
        ],
        "vimshottari_mahadashas": dashas,
    }
    return section


def _vimshottari(
    birth: BirthInput, starting_lord: str, elapsed_fraction: float
) -> list[dict[str, Any]]:
    """Mahadasha sequence from the Moon's nakshatra, with the birth balance."""
    names = [name for name, _ in DASHA_SEQUENCE]
    index = names.index(starting_lord)
    cursor = birth.civil_datetime
    balance_years = (1.0 - elapsed_fraction) * DASHA_YEARS[starting_lord]

    rows: list[dict[str, Any]] = []
    end = cursor + timedelta(days=balance_years * SIDEREAL_YEAR_DAYS)
    rows.append({
        "lord": starting_lord,
        "start": cursor.date().isoformat(),
        "end": end.date().isoformat(),
        "years": round(balance_years, 3),
        "partial_at_birth": True,
    })
    cursor = end
    for step in range(1, 10):
        lord = names[(index + step) % 9]
        years = DASHA_YEARS[lord]
        end = cursor + timedelta(days=years * SIDEREAL_YEAR_DAYS)
        rows.append({
            "lord": lord,
            "start": cursor.date().isoformat(),
            "end": end.date().isoformat(),
            "years": years,
            "partial_at_birth": False,
        })
        cursor = end
    return rows
