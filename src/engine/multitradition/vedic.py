"""Vedic (sidereal) section: rasi, nakshatra, whole-sign houses, Vimshottari.

Calculation reuses the shipping Swiss Ephemeris calculator in sidereal mode. The
ayanamsa is a configured choice: the engine supports eight, and no research pack
selects one, so Lahiri is disclosed with its alternatives rather than assumed.

The reading follows the judgment hierarchy in
`docs/research/multitradition/jyotisha/defensibility_spec.md`: lagna, Moon,
graha condition, bhava rulership, drishti, navamsha cross-check, yogas, dasha.
Yogas come seventh on purpose - a yoga named before its constituents have been
verified is the single fastest way for this section to be dismissed.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from itertools import combinations
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
NODES = ["Rahu", "Ketu"]
GRAHA_ORDER = GRAHAS + NODES
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
NOT_ASSESSED = "not assessed for nodes"
DIGNITY_RANK = {
    "debilitated": 0,
    "neutral placement": 1,
    "own sign": 2,
    "exalted": 3,
}
AYANAMSA_ALTERNATIVES = (
    "Fagan-Bradley", "Krishnamurti", "Raman", "True Citra", "True Revati",
    "Surya Siddhanta", "Hipparchos",
)

# --- Graha drishti (BPHS aspect chapters) ------------------------------------
# Every graha aspects the seventh house from itself. Mars, Jupiter and Saturn
# carry additional special aspects; those asymmetries are precisely what
# separates Vedic aspect logic from the Western degree-orb aspect.
DRISHTI_UNIVERSAL = 7
SPECIAL_DRISHTI: dict[str, tuple[int, ...]] = {
    "Mars": (4, 8),
    "Jupiter": (5, 9),
    "Saturn": (3, 10),
}

# --- Combustion (astangata) --------------------------------------------------
# Configured orb table, measured as ecliptic-longitude separation from the Sun.
COMBUSTION_ORBS: dict[str, float] = {
    "Moon": 12.0, "Mars": 17.0, "Mercury": 14.0,
    "Jupiter": 11.0, "Venus": 10.0, "Saturn": 15.0,
}
COMBUSTION_ORBS_RETROGRADE: dict[str, float] = {"Mercury": 12.0, "Venus": 8.0}
COMBUSTION_ALTERNATIVES = (
    "orb sets differing by several degrees between texts and schools",
    "latitude-corrected (true) angular distance instead of longitude difference",
    "no retrograde reduction for Mercury and Venus",
)

# --- Naisargika (natural) friendship, BPHS relationship chapters --------------
# The table is deliberately asymmetric: the Moon counts Mars neutral while Mars
# counts the Moon a friend. Direction is therefore always stated.
NAISARGIKA: dict[str, dict[str, tuple[str, ...]]] = {
    "Sun": {
        "friends": ("Moon", "Mars", "Jupiter"),
        "neutral": ("Mercury",),
        "enemies": ("Venus", "Saturn"),
    },
    "Moon": {
        "friends": ("Sun", "Mercury"),
        "neutral": ("Mars", "Jupiter", "Venus", "Saturn"),
        "enemies": (),
    },
    "Mars": {
        "friends": ("Sun", "Moon", "Jupiter"),
        "neutral": ("Venus", "Saturn"),
        "enemies": ("Mercury",),
    },
    "Mercury": {
        "friends": ("Sun", "Venus"),
        "neutral": ("Mars", "Jupiter", "Saturn"),
        "enemies": ("Moon",),
    },
    "Jupiter": {
        "friends": ("Sun", "Moon", "Mars"),
        "neutral": ("Saturn",),
        "enemies": ("Mercury", "Venus"),
    },
    "Venus": {
        "friends": ("Mercury", "Saturn"),
        "neutral": ("Mars", "Jupiter"),
        "enemies": ("Sun", "Moon"),
    },
    "Saturn": {
        "friends": ("Mercury", "Venus"),
        "neutral": ("Jupiter",),
        "enemies": ("Sun", "Moon", "Mars"),
    },
}

# --- Yoga structure ----------------------------------------------------------
KENDRAS = (1, 4, 7, 10)
TRIKONAS = (1, 5, 9)
# The lagna is both a kendra and a trikona, so its lord would qualify as a
# yogakaraka trivially. The classical identification excludes it.
YOGAKARAKA_KENDRAS = (4, 7, 10)
YOGAKARAKA_TRIKONAS = (5, 9)
DHANA_HOUSES = (1, 2, 5, 9, 11)


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


NAVAMSHA_ARC = 30.0 / 9.0  # 3 degrees 20 minutes


def navamsha_sign(longitude: float) -> tuple[str, int]:
    """D9 sign and the 1-based navamsha division within the rasi.

    Each 30-degree sign divides into nine 3-20 arcs. The closed form
    `(sign_index * 9 + part) % 12` reproduces the classical rule without a
    lookup table: movable signs start their D9 from themselves, fixed signs from
    the ninth sign, and dual signs from the fifth.
    """
    lon = longitude % 360
    sign_index = int(lon // 30)
    part = int((lon - sign_index * 30) // NAVAMSHA_ARC)
    return SIGNS[(sign_index * 9 + part) % 12], part + 1


def _vargottama(rasi: str, navamsha: str) -> bool:
    """A graha occupying the same sign in D1 and D9 is vargottama - strengthened."""
    return rasi == navamsha


def _dignity(graha: str, sign: str) -> str:
    if sign == EXALTATION.get(graha):
        return "exalted"
    if sign == DEBILITATION.get(graha):
        return "debilitated"
    if sign in OWN_SIGNS.get(graha, set()):
        return "own sign"
    return "neutral placement"


# --------------------------------------------------------------------------- #
# Drishti
# --------------------------------------------------------------------------- #


def _nth_house(house: int, nth: int) -> int:
    """The house `nth` places from `house`, counting the origin as 1."""
    return (house - 1 + nth - 1) % 12 + 1


def drishti_houses(graha: str, house: int) -> dict[int, int]:
    """Map of aspect number -> house aspected, computed by house not by orb.

    Universal seventh aspect for every graha; Mars adds the 4th and 8th,
    Jupiter the 5th and 9th, Saturn the 3rd and 10th.
    """
    steps = sorted({DRISHTI_UNIVERSAL, *SPECIAL_DRISHTI.get(graha, ())})
    return {nth: _nth_house(house, nth) for nth in steps}


ORDINAL_SUFFIX = {1: "st", 2: "nd", 3: "rd"}


def _ordinal(number: int) -> str:
    if 10 <= number % 100 <= 20:
        return f"{number}th"
    return f"{number}{ORDINAL_SUFFIX.get(number % 10, 'th')}"


def _mutual_drishti(
    first: str, first_house: int, second: str, second_house: int
) -> bool:
    first_hits = set(drishti_houses(first, first_house).values())
    second_hits = set(drishti_houses(second, second_house).values())
    return second_house in first_hits and first_house in second_hits


# --------------------------------------------------------------------------- #
# Combustion (astangata)
# --------------------------------------------------------------------------- #


def _separation(first: float, second: float) -> float:
    diff = abs(first - second) % 360.0
    return min(diff, 360.0 - diff)


def combustion(
    graha: str, longitude: float, sun_longitude: float, retrograde: bool
) -> dict[str, Any]:
    """Astangata flag against the configured orb table.

    The Sun itself and the nodes carry no orb, so they are reported as not
    combust with a null orb rather than silently omitted.
    """
    separation = _separation(longitude, sun_longitude)
    orb = COMBUSTION_ORBS.get(graha)
    if retrograde and graha in COMBUSTION_ORBS_RETROGRADE:
        orb = COMBUSTION_ORBS_RETROGRADE[graha]
    return {
        "combust": bool(orb is not None and separation <= orb),
        "solar_separation_degrees": round(separation, 4),
        "combustion_orb_degrees": orb,
    }


# --------------------------------------------------------------------------- #
# Naisargika (natural) friendship
# --------------------------------------------------------------------------- #


def naisargika_relation(graha: str, other: str) -> str:
    """How `graha` naturally regards `other`. Not symmetric - direction matters."""
    if graha not in NAISARGIKA or other not in NAISARGIKA:
        return NOT_ASSESSED
    if graha == other:
        return "own sign lord"
    row = NAISARGIKA[graha]
    if other in row["friends"]:
        return "friend"
    if other in row["enemies"]:
        return "enemy"
    return "neutral"


def _naisargika_table() -> dict[str, dict[str, list[str]]]:
    return {
        graha: {key: list(values) for key, values in row.items()}
        for graha, row in NAISARGIKA.items()
    }


# --------------------------------------------------------------------------- #
# Section build
# --------------------------------------------------------------------------- #


def build(
    birth: BirthInput, chart: Any, as_of: datetime | None = None
) -> TraditionSection:
    """Build the Vedic section from a sidereal chart produced by ChartCalculator."""
    section = TraditionSection(
        tradition_id="indian_jyotisha",
        display_name="Vedic (Jyotisha)",
        evidence_grade=EvidenceGrade.CONFIGURED,
        basis=(
            "Swiss Ephemeris sidereal positions; whole-sign houses; "
            "Vimshottari mahadasha and antardasha keyed to the Moon's nakshatra; "
            "navamsha, drishti, combustion and naisargika relations computed."
        ),
    )
    _disclose(section)

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa = swe.get_ayanamsa_ut(chart.jd)

    planet_map = {p.name.value: p for p in chart.planets}
    asc_sign, asc_deg = _sign_of(chart.ascendant)
    asc_index = SIGNS.index(asc_sign)
    asc_nak, asc_nak_lord, asc_pada, _ = _nakshatra_of(chart.ascendant)
    sun_longitude = planet_map["Sun"].longitude

    grahas: list[dict[str, Any]] = []
    for name in GRAHAS:
        planet = planet_map.get(name)
        if planet is None:
            continue
        grahas.append(
            _graha_row(name, planet.longitude, asc_index, sun_longitude,
                       getattr(planet, "speed", 0.0) < 0, is_node=False)
        )

    # Rahu/Ketu live in chart.planets; the scalar chart.north_node field is unused.
    for label, key in (("Rahu", "North_Node"), ("Ketu", "South_Node")):
        node = planet_map.get(key)
        if node is None:
            continue
        grahas.append(
            _graha_row(label, node.longitude, asc_index, sun_longitude,
                       True, is_node=True)
        )

    by_name = {row["graha"]: row for row in grahas}
    graha_house = {row["graha"]: row["house"] for row in grahas}
    drishti = _drishti_table(grahas)
    for row in drishti:
        by_name[row["graha"]]["drishti_houses"] = list(row["aspects_houses"])

    houses = [
        {
            "house": h,
            "rasi": SIGNS[(asc_index + h - 1) % 12],
            "lord": SIGN_LORD[SIGNS[(asc_index + h - 1) % 12]],
        }
        for h in range(1, 13)
    ]
    house_lords = {row["house"]: row["lord"] for row in houses}
    house_lordships: dict[str, list[int]] = {}
    for house, lord in house_lords.items():
        house_lordships.setdefault(lord, []).append(house)

    moon = planet_map["Moon"]
    moon_nak, moon_lord, moon_pada, elapsed = _nakshatra_of(moon.longitude)
    spans = _mahadasha_spans(birth, moon_lord, elapsed)
    dashas = [_public_span(span) for span in spans]
    reference = as_of or datetime.now()
    running = _running_span(spans, reference)
    antardashas = _antardashas(running) if running else None
    current = _current_periods(running, antardashas, reference)

    facts: dict[str, Any] = {
        "ayanamsa_degrees": round(ayanamsa, 6),
        "lagna": {
            "rasi": asc_sign,
            "degree_in_sign": round(asc_deg, 4),
            "lord": SIGN_LORD[asc_sign],
            "nakshatra": asc_nak,
            "pada": asc_pada,
            "nakshatra_lord": asc_nak_lord,
            "navamsha": navamsha_sign(chart.ascendant)[0],
            "navamsha_lord": SIGN_LORD[navamsha_sign(chart.ascendant)[0]],
            "vargottama": _vargottama(asc_sign, navamsha_sign(chart.ascendant)[0]),
        },
        "janma_rasi": _sign_of(moon.longitude)[0],
        "janma_nakshatra": {"name": moon_nak, "pada": moon_pada, "lord": moon_lord},
        "grahas": grahas,
        "houses": houses,
        "house_lordships": {
            lord: sorted(owned) for lord, owned in sorted(house_lordships.items())
        },
        "drishti": drishti,
        "naisargika_relations": _naisargika_table(),
        "combustion_orbs_configured": {
            "direct": dict(COMBUSTION_ORBS),
            "retrograde_overrides": dict(COMBUSTION_ORBS_RETROGRADE),
        },
        "navamsha_cross_check": _navamsha_cross_check(grahas),
        "yogas": _detect_yogas(house_lords, house_lordships, graha_house, by_name),
        "vimshottari_mahadashas": dashas,
        "vimshottari_antardashas": antardashas,
        "vimshottari_current": current,
    }
    section.facts = facts
    section.reading = _vedic_reading(facts)
    return section


def _graha_row(
    name: str,
    longitude: float,
    asc_index: int,
    sun_longitude: float,
    retrograde: bool,
    is_node: bool,
) -> dict[str, Any]:
    sign, degree = _sign_of(longitude)
    nak, nak_lord, pada, _ = _nakshatra_of(longitude)
    d9_sign, d9_division = navamsha_sign(longitude)
    dispositor = SIGN_LORD[sign]
    row: dict[str, Any] = {
        "graha": name,
        "rasi": sign,
        "degree_in_sign": round(degree, 4),
        "house": (SIGNS.index(sign) - asc_index) % 12 + 1,
        "nakshatra": nak,
        "pada": pada,
        "nakshatra_lord": nak_lord,
        "dignity": NOT_ASSESSED if is_node else _dignity(name, sign),
        "navamsha": d9_sign,
        "navamsha_division": d9_division,
        "navamsha_dignity": NOT_ASSESSED if is_node else _dignity(name, d9_sign),
        "vargottama": _vargottama(sign, d9_sign),
        "retrograde": retrograde,
        "dispositor": dispositor,
        "dispositor_relation": naisargika_relation(name, dispositor),
    }
    row.update(combustion(name, longitude, sun_longitude, retrograde))
    return row


def _drishti_table(grahas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One row per graha: which houses it aspects, and who stands there."""
    occupants: dict[int, list[str]] = {}
    for row in grahas:
        occupants.setdefault(row["house"], []).append(row["graha"])

    table: list[dict[str, Any]] = []
    for row in grahas:
        name = row["graha"]
        house = row["house"]
        aspects = drishti_houses(name, house)
        targets: list[str] = []
        for target_house in sorted(set(aspects.values())):
            targets.extend(occupants.get(target_house, []))
        special = SPECIAL_DRISHTI.get(name, ())
        table.append({
            "graha": name,
            "from_house": house,
            "from_rasi": row["rasi"],
            "aspects": [
                f"{_ordinal(nth)} aspect to house {target}"
                for nth, target in sorted(aspects.items())
            ],
            "aspects_houses": sorted(set(aspects.values())),
            "aspects_grahas": targets,
            "special_drishti": (
                ", ".join(_ordinal(n) for n in special) if special else "none"
            ),
        })
    return table


def _navamsha_cross_check(grahas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Where D9 confirms or undercuts D1, per graha.

    A D1 verdict that D9 contradicts is not a finished judgment, so the
    divergence is recorded as a fact rather than left for the prose to notice.
    """
    rows: list[dict[str, Any]] = []
    for row in grahas:
        d1, d9 = row["dignity"], row["navamsha_dignity"]
        if row["vargottama"]:
            verdict = "confirms (vargottama)"
        elif d1 == NOT_ASSESSED or d9 == NOT_ASSESSED:
            verdict = NOT_ASSESSED
        elif DIGNITY_RANK[d9] > DIGNITY_RANK[d1]:
            verdict = "D9 raises the D1 verdict"
        elif DIGNITY_RANK[d9] < DIGNITY_RANK[d1]:
            verdict = "D9 undercuts the D1 verdict"
        else:
            verdict = "D9 matches the D1 dignity"
        rows.append({
            "graha": row["graha"],
            "rasi_d1": row["rasi"],
            "dignity_d1": d1,
            "rasi_d9": row["navamsha"],
            "dignity_d9": d9,
            "vargottama": row["vargottama"],
            "verdict": verdict,
            "diverges": verdict.startswith("D9 raises")
            or verdict.startswith("D9 undercuts"),
        })
    return rows


# --------------------------------------------------------------------------- #
# Yogas
# --------------------------------------------------------------------------- #


def _relation_between(
    first: str, second: str, graha_house: dict[str, int]
) -> str | None:
    """Conjunction (same whole-sign house) or mutual drishti, else None."""
    first_house = graha_house.get(first)
    second_house = graha_house.get(second)
    if first_house is None or second_house is None:
        return None
    if first_house == second_house:
        return "conjunct"
    if _mutual_drishti(first, first_house, second, second_house):
        return "mutual drishti"
    return None


def _condition_phrase(row: dict[str, Any]) -> str:
    parts = [f"{row['rasi']} in house {row['house']}", row["dignity"]]
    if row.get("retrograde"):
        parts.append("retrograde")
    if row.get("combust"):
        parts.append(
            f"combust at {row['solar_separation_degrees']:.2f} deg from the Sun"
        )
    return ", ".join(parts)


def _house_list(houses: list[int]) -> str:
    return ", ".join(str(h) for h in houses)


def _relation_phrase(relation: str) -> str:
    return "conjunct" if relation == "conjunct" else "in mutual drishti"


def _detect_yogas(
    house_lords: dict[int, str],
    house_lordships: dict[str, list[int]],
    graha_house: dict[str, int],
    by_name: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Only structurally verifiable yogas, each reported with its constituents.

    No yoga catalogue and no phala (results) are attached: the section states
    which structural condition was found true and on what facts, which is the
    part a Jyotishi can check against the chart.
    """
    yogas: list[dict[str, Any]] = []
    yogas.extend(_yogakaraka(house_lordships, graha_house, by_name))
    yogas.extend(_raja_yogas(house_lords, graha_house, by_name))
    yogas.extend(_dhana_yogas(house_lords, graha_house, by_name))
    return yogas


def _yogakaraka(
    house_lordships: dict[str, list[int]],
    graha_house: dict[str, int],
    by_name: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for graha in GRAHAS:
        owned = set(house_lordships.get(graha, []))
        kendra = sorted(owned & set(YOGAKARAKA_KENDRAS))
        trikona = sorted(owned & set(YOGAKARAKA_TRIKONAS))
        if not (kendra and trikona) or graha not in graha_house:
            continue
        row = by_name[graha]
        found.append({
            "yoga": "Yogakaraka",
            "grahas": [graha],
            "rule": (
                "one graha ruling both a kendra (4, 7 or 10) and a trikona "
                "(5 or 9) from the lagna"
            ),
            "summary": (
                f"{graha} rules kendra house {_house_list(kendra)} and trikona "
                f"house {_house_list(trikona)}."
            ),
            "constituent_facts": [
                f"{graha} owns house {_house_list(kendra)}, a kendra.",
                f"{graha} owns house {_house_list(trikona)}, a trikona.",
                f"{graha} itself stands in {_condition_phrase(row)}.",
                f"In D9 {graha} falls in {row['navamsha']} "
                f"({row['navamsha_dignity']}).",
            ],
        })
    return found


def _raja_yogas(
    house_lords: dict[int, str],
    graha_house: dict[str, int],
    by_name: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Kendra lord and trikona lord conjunct or in mutual drishti."""
    merged: dict[frozenset[str], dict[str, Any]] = {}
    for kendra in KENDRAS:
        for trikona in TRIKONAS:
            kendra_lord = house_lords[kendra]
            trikona_lord = house_lords[trikona]
            if kendra_lord == trikona_lord:
                continue
            relation = _relation_between(kendra_lord, trikona_lord, graha_house)
            if relation is None:
                continue
            key = frozenset((kendra_lord, trikona_lord))
            entry = merged.setdefault(key, {
                "relation": relation,
                "kendra": {},
                "trikona": {},
            })
            entry["kendra"].setdefault(kendra_lord, set()).add(kendra)
            entry["trikona"].setdefault(trikona_lord, set()).add(trikona)

    found: list[dict[str, Any]] = []
    for key in sorted(merged, key=lambda k: sorted(k)):
        entry = merged[key]
        pair = sorted(key)
        kendra_text = "; ".join(
            f"{lord} owns kendra house {_house_list(sorted(houses))}"
            for lord, houses in sorted(entry["kendra"].items())
        )
        trikona_text = "; ".join(
            f"{lord} owns trikona house {_house_list(sorted(houses))}"
            for lord, houses in sorted(entry["trikona"].items())
        )
        facts = [f"{kendra_text}.", f"{trikona_text}."]
        for graha in pair:
            facts.append(f"{graha} stands in {_condition_phrase(by_name[graha])}.")
        if entry["relation"] == "conjunct":
            facts.append(
                f"{pair[0]} and {pair[1]} occupy the same house "
                f"({graha_house[pair[0]]}) - conjunction verified by whole-sign "
                "co-tenancy."
            )
        else:
            for graha in pair:
                other = pair[1] if graha == pair[0] else pair[0]
                aspects = drishti_houses(graha, graha_house[graha])
                nth = next(
                    n for n, h in sorted(aspects.items())
                    if h == graha_house[other]
                )
                facts.append(
                    f"{graha} casts its {_ordinal(nth)} aspect from house "
                    f"{graha_house[graha]} onto house {graha_house[other]}, "
                    f"where {other} stands."
                )
        found.append({
            "yoga": "Raja Yoga",
            "grahas": pair,
            "rule": "a kendra lord and a trikona lord conjunct or in mutual drishti",
            "summary": (
                f"{pair[0]} and {pair[1]} are "
                f"{_relation_phrase(entry['relation'])} as kendra and trikona "
                "lords."
            ),
            "relation": entry["relation"],
            "constituent_facts": facts,
        })
    return found


def _dhana_yogas(
    house_lords: dict[int, str],
    graha_house: dict[str, int],
    by_name: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Wealth-house lordship: one graha holding two of 1/2/5/9/11, or two joined."""
    dhana_lords: dict[str, list[int]] = {}
    for house in DHANA_HOUSES:
        dhana_lords.setdefault(house_lords[house], []).append(house)

    found: list[dict[str, Any]] = []
    for graha in sorted(dhana_lords):
        owned = sorted(dhana_lords[graha])
        if len(owned) < 2 or graha not in graha_house:
            continue
        row = by_name[graha]
        found.append({
            "yoga": "Dhana Yoga",
            "grahas": [graha],
            "rule": "one graha ruling two or more of houses 1, 2, 5, 9, 11",
            "summary": f"{graha} rules dhana houses {_house_list(owned)}.",
            "constituent_facts": [
                f"{graha} owns houses {_house_list(owned)}, all of them among "
                "the dhana houses 1, 2, 5, 9, 11.",
                f"{graha} stands in {_condition_phrase(row)}.",
                f"In D9 {graha} falls in {row['navamsha']} "
                f"({row['navamsha_dignity']}).",
            ],
        })

    for first, second in combinations(sorted(dhana_lords), 2):
        relation = _relation_between(first, second, graha_house)
        if relation is None:
            continue
        facts = [
            f"{first} owns dhana house {_house_list(sorted(dhana_lords[first]))}.",
            f"{second} owns dhana house {_house_list(sorted(dhana_lords[second]))}.",
            f"{first} stands in {_condition_phrase(by_name[first])}.",
            f"{second} stands in {_condition_phrase(by_name[second])}.",
            f"The two are {_relation_phrase(relation)}.",
        ]
        found.append({
            "yoga": "Dhana Yoga",
            "grahas": [first, second],
            "rule": (
                "two lords of houses 1, 2, 5, 9, 11 conjunct or in mutual drishti"
            ),
            "summary": (
                f"{first} and {second} are dhana lords, "
                f"{_relation_phrase(relation)}."
            ),
            "relation": relation,
            "constituent_facts": facts,
        })
    return found


# --------------------------------------------------------------------------- #
# Vimshottari
# --------------------------------------------------------------------------- #


def _mahadasha_spans(
    birth: BirthInput, starting_lord: str, elapsed_fraction: float
) -> list[dict[str, Any]]:
    """Full-precision mahadasha spans; the public rows derive from these.

    `notional_start` is where the whole period would have begun had none of it
    elapsed before birth. Antardashas are subdivided from that point so the
    sub-periods of a birth-partial mahadasha still sum to the full length.
    """
    names = [name for name, _ in DASHA_SEQUENCE]
    index = names.index(starting_lord)
    cursor = birth.civil_datetime
    balance_years = (1.0 - elapsed_fraction) * DASHA_YEARS[starting_lord]
    full_years = DASHA_YEARS[starting_lord]
    end = cursor + timedelta(days=balance_years * SIDEREAL_YEAR_DAYS)

    spans: list[dict[str, Any]] = [{
        "lord": starting_lord,
        "start": cursor,
        "end": end,
        "years": round(balance_years, 3),
        "full_years": full_years,
        "notional_start": end - timedelta(days=full_years * SIDEREAL_YEAR_DAYS),
        "partial_at_birth": True,
    }]
    cursor = end
    for step in range(1, 10):
        lord = names[(index + step) % 9]
        years = DASHA_YEARS[lord]
        end = cursor + timedelta(days=years * SIDEREAL_YEAR_DAYS)
        spans.append({
            "lord": lord,
            "start": cursor,
            "end": end,
            "years": years,
            "full_years": years,
            "notional_start": cursor,
            "partial_at_birth": False,
        })
        cursor = end
    return spans


def _public_span(span: dict[str, Any]) -> dict[str, Any]:
    return {
        "lord": span["lord"],
        "start": span["start"].date().isoformat(),
        "end": span["end"].date().isoformat(),
        "years": span["years"],
        "partial_at_birth": span["partial_at_birth"],
    }


def _running_span(
    spans: list[dict[str, Any]], reference: datetime
) -> dict[str, Any] | None:
    for span in spans:
        if span["start"] <= reference < span["end"]:
            return span
    return None


def _antardashas(span: dict[str, Any]) -> dict[str, Any]:
    """Proportional bhukti subdivision of one mahadasha.

    antardasha_years = mahadasha_years * antardasha_lord_years / 120, with the
    sub-lords running the standard sequence from the mahadasha lord itself. The
    nine sub-periods therefore sum to the mahadasha's full length by
    construction, since the nine lord-years sum to 120.
    """
    lord = span["lord"]
    full_years = span["full_years"]
    names = [name for name, _ in DASHA_SEQUENCE]
    index = names.index(lord)
    cursor = span["notional_start"]

    rows: list[dict[str, Any]] = []
    exact_total = 0.0
    for step in range(9):
        sub_lord = names[(index + step) % 9]
        years = full_years * DASHA_YEARS[sub_lord] / DASHA_TOTAL_YEARS
        exact_total += years
        end = cursor + timedelta(days=years * SIDEREAL_YEAR_DAYS)
        rows.append({
            "mahadasha_lord": lord,
            "antardasha_lord": sub_lord,
            "start": cursor.date().isoformat(),
            "end": end.date().isoformat(),
            "years": round(years, 6),
            "before_birth": end <= span["start"],
        })
        cursor = end

    return {
        "mahadasha_lord": lord,
        "mahadasha_full_years": full_years,
        "mahadasha_partial_at_birth": span["partial_at_birth"],
        "notional_start": span["notional_start"].date().isoformat(),
        "subdivision_rule": (
            "antardasha_years = mahadasha_years * antardasha_lord_years / 120"
        ),
        "sum_of_antardasha_years": round(exact_total, 6),
        "periods": rows,
    }


def _current_periods(
    span: dict[str, Any] | None,
    antardashas: dict[str, Any] | None,
    reference: datetime,
) -> dict[str, Any]:
    if span is None or antardashas is None:
        return {
            "as_of": reference.date().isoformat(),
            "status": "outside the computed 120-year Vimshottari cycle",
            "mahadasha": None,
            "antardasha": None,
        }
    stamp = reference.date().isoformat()
    running = next(
        (row for row in antardashas["periods"]
         if row["start"] <= stamp < row["end"]),
        None,
    )
    return {
        "as_of": stamp,
        "status": "running",
        "mahadasha": _public_span(span),
        "antardasha": running,
    }


# --------------------------------------------------------------------------- #
# Reading
# --------------------------------------------------------------------------- #


def _suffix(row: dict[str, Any]) -> str:
    parts: list[str] = []
    if row.get("retrograde"):
        parts.append("retrograde")
    if row.get("combust"):
        parts.append(
            f"combust - {row['solar_separation_degrees']:.2f} deg from the Sun "
            f"against a configured {row['combustion_orb_degrees']:.0f} deg orb"
        )
    if not parts:
        return ""
    return ", " + ", ".join(parts)


def _vedic_reading(facts: dict[str, Any]) -> list[str]:
    """Compose in the spec's judgment hierarchy - and label the steps.

    The numbering is not decoration. It is the audit trail showing that yogas
    (step 7) were only reached after lagna, Moon, graha condition, rulership,
    drishti and the navamsha cross-check were each stated.
    """
    by_name = {row["graha"]: row for row in facts["grahas"]}
    lagna = facts["lagna"]
    lordships = facts["house_lordships"]
    lines: list[str] = []

    # 1 - Lagna and lagna lord.
    lines.append(
        f"1. Lagna and lagna lord - {lagna['rasi']} rises at "
        f"{lagna['degree_in_sign']:.2f} degrees, in {lagna['nakshatra']} pada "
        f"{lagna['pada']} (nakshatra lord {lagna['nakshatra_lord']}). Its "
        f"navamsha is {lagna['navamsha']}, lord {lagna['navamsha_lord']}; the "
        f"lagna is "
        f"{'vargottama' if lagna['vargottama'] else 'not vargottama'}."
    )
    lord = lagna["lord"]
    lord_row = by_name.get(lord)
    if lord_row is not None:
        owned = lordships.get(lord, [])
        plural = "s" if len(owned) > 1 else ""
        lines.append(
            f"1. Lagna lord - {lord} rules {lagna['rasi']} and sits in "
            f"{lord_row['rasi']}, house {lord_row['house']}, "
            f"{lord_row['dignity']}{_suffix(lord_row)}. It owns house{plural} "
            f"{_house_list(owned)}. Everything below is qualified by this "
            "condition rather than read around it."
        )

    # 2 - Moon outranks the Sun for personal significations.
    moon = by_name.get("Moon")
    janma = facts["janma_nakshatra"]
    if moon is not None:
        lines.append(
            f"2. Moon, janma rasi and janma nakshatra - {facts['janma_rasi']} "
            f"in house {moon['house']}, {janma['name']} pada {janma['pada']} "
            f"(lord {janma['lord']}); {moon['dignity']}{_suffix(moon)}. In "
            "Jyotisha the Moon outranks the Sun for personal significations, so "
            "this stands above any solar statement in this section."
        )

    # 3 - Graha dignity and placement in D1.
    lines.append(
        "3. Graha dignity and placement in D1 - stated as condition first, with "
        "retrogradation and combustion, before anything is made of it."
    )
    for name in GRAHA_ORDER:
        row = by_name.get(name)
        if row is None:
            continue
        relation = (
            f"sign lord {row['dispositor']}; naisargika relation "
            f"{NOT_ASSESSED}"
            if row["dispositor_relation"] == NOT_ASSESSED
            else f"sign lord {row['dispositor']}, whom {name} naturally "
            f"regards as {row['dispositor_relation']}"
        )
        lines.append(
            f"3. {name} - {row['rasi']} {row['degree_in_sign']:.2f}, house "
            f"{row['house']}, {row['nakshatra']} pada {row['pada']} (lord "
            f"{row['nakshatra_lord']}); {row['dignity']}{_suffix(row)}; "
            f"{relation}."
        )

    # 4 - Bhava rulership.
    lines.append(
        "4. Bhava rulership - which graha owns which house, and where that "
        "owner actually sits. A house is judged through its lord's condition."
    )
    for name in GRAHAS:
        owned = lordships.get(name)
        row = by_name.get(name)
        if not owned or row is None:
            continue
        plural = "s" if len(owned) > 1 else ""
        lines.append(
            f"4. {name} owns house{plural} {_house_list(owned)} - it sits in "
            f"house {row['house']} ({row['rasi']}), "
            f"{row['dignity']}{_suffix(row)}."
        )

    # 5 - Drishti.
    lines.append(
        "5. Drishti - every graha aspects the 7th house from itself; Mars adds "
        "the 4th and 8th, Jupiter the 5th and 9th, Saturn the 3rd and 10th. "
        "Aspects are counted whole-sign by house, not by degree orb."
    )
    for row in facts["drishti"]:
        targets = (
            "Grahas aspected: " + ", ".join(row["aspects_grahas"]) + "."
            if row["aspects_grahas"]
            else "No graha stands in the aspected houses."
        )
        lines.append(
            f"5. {row['graha']} from house {row['from_house']} "
            f"({row['from_rasi']}) - {'; '.join(row['aspects'])}. {targets}"
        )

    # 6 - Navamsha cross-check.
    lines.append(
        "6. Navamsha cross-check - D9 either confirms the D1 verdict or "
        "undercuts it. A D1 judgment never tested against D9 is not a finished "
        "judgment in this tradition."
    )
    notable = [
        row for row in facts["navamsha_cross_check"]
        if row["vargottama"] or row["diverges"]
    ]
    for row in notable:
        if row["vargottama"]:
            lines.append(
                f"6. {row['graha']} is vargottama - the same rasi "
                f"({row['rasi_d1']}) in D1 and D9. D9 confirms."
            )
        else:
            lines.append(
                f"6. {row['graha']} - D1 {row['rasi_d1']} "
                f"({row['dignity_d1']}) against D9 {row['rasi_d9']} "
                f"({row['dignity_d9']}). {row['verdict']}; the two are read "
                "together, not averaged."
            )
    if not notable:
        lines.append(
            "6. No graha is vargottama and none changes dignity class between "
            "D1 and D9; the cross-check neither strengthens nor weakens any D1 "
            "verdict here."
        )

    # 7 - Yogas, only now.
    lines.append(
        "7. Yogas - reached only after steps 1 to 6, and only for structures "
        "whose constituents were verified above. Yogas whose definition needs "
        "Shadbala or Ashtakavarga are not evaluated at all."
    )
    for yoga in facts["yogas"]:
        lines.append(
            f"7. {yoga['yoga']} ({', '.join(yoga['grahas'])}) - "
            f"{yoga['summary']} Rule applied: {yoga['rule']}. Constituent "
            f"facts: {' '.join(yoga['constituent_facts'])}"
        )
    if not facts["yogas"]:
        lines.append(
            "7. None of the three structurally testable classes - yogakaraka, "
            "Raja Yoga, Dhana Yoga - is present in this chart. That is a "
            "finding, not a gap in the calculation."
        )

    # 8 - Dasha, read against the qualified structure.
    lines.extend(_dasha_reading(facts, by_name, lordships))
    return lines


def _dasha_reading(
    facts: dict[str, Any],
    by_name: dict[str, dict[str, Any]],
    lordships: dict[str, list[int]],
) -> list[str]:
    current = facts["vimshottari_current"]
    if not current.get("mahadasha"):
        return [
            f"8. Dasha - as of {current['as_of']} the chart falls "
            f"{current['status']}; no period is asserted."
        ]

    maha = current["mahadasha"]
    antar = current["antardasha"]
    lines = [
        f"8. Dasha - as of {current['as_of']} the running mahadasha is "
        f"{maha['lord']} ({maha['start']} to {maha['end']})"
        + (
            f", and within it the {antar['antardasha_lord']} antardasha "
            f"({antar['start']} to {antar['end']}, "
            f"{antar['years']:.2f} years)."
            if antar
            else "; the antardasha boundary could not be resolved."
        )
    ]
    seen: list[str] = []
    pairs = [("Mahadasha", maha["lord"])]
    if antar:
        pairs.append(("Antardasha", antar["antardasha_lord"]))
    for role, lord in pairs:
        if lord in seen:
            continue
        seen.append(lord)
        row = by_name.get(lord)
        if row is None:
            continue
        owned = lordships.get(lord)
        owns = (
            f"it owns house{'s' if len(owned) > 1 else ''} "
            f"{_house_list(owned)}"
            if owned
            else "it owns no house in the whole-sign scheme"
        )
        lines.append(
            f"8. {role} lord {lord} in the natal structure - {row['rasi']}, "
            f"house {row['house']}, {row['dignity']}{_suffix(row)}; {owns}; in "
            f"D9 {row['navamsha']} ({row['navamsha_dignity']}). The period is "
            "read through that qualified condition, never as a free-floating "
            "theme."
        )
    lines.append(
        "8. Period boundaries are calendar arithmetic on a 365.2425-day year "
        "from the janma-nakshatra balance. They locate a period, not an event."
    )
    return lines


# --------------------------------------------------------------------------- #
# Disclosures
# --------------------------------------------------------------------------- #


def _disclose(section: TraditionSection) -> None:
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
        DisclosureKind.SOURCE,
        "Navamsha",
        "D9 is computed for every graha and the lagna, with vargottama flagged. "
        "Jyotisha treats the navamsha as mandatory rather than optional: a D1 "
        "verdict that D9 contradicts is not a finished judgment.",
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Combustion orbs (astangata)",
        "Combustion is flagged from a configured orb table measured as "
        "ecliptic-longitude separation from the Sun: Moon 12, Mars 17, "
        "Mercury 14 (12 when retrograde), Jupiter 11, Venus 10 (8 when "
        "retrograde), Saturn 15 degrees. These are widely-cited traditional "
        "values, but texts and schools differ by several degrees and a "
        "different table moves grahas across the combustion boundary.",
        COMBUSTION_ALTERNATIVES,
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Drishti scheme",
        "Graha drishti is computed whole-sign by house: the 7th from every "
        "graha, with Mars adding the 4th and 8th, Jupiter the 5th and 9th, and "
        "Saturn the 3rd and 10th. Rahu and Ketu receive the 7th only; the "
        "extended nodal aspects some schools grant them are not asserted, and "
        "no degree-based drishti strength (drishti bala) is computed.",
        (
            "Rahu/Ketu granted 5th and 9th aspects",
            "Degree-proportional drishti strength",
        ),
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Graha friendship",
        "Only naisargika (natural, permanent) friendship is computed, from the "
        "standard BPHS table. Tatkalika (temporary, sign-distance) friendship "
        "and the panchadha compound relation it produces are NOT computed, so "
        "no compound-relation dignity claim is made. Rahu and Ketu carry no "
        "agreed naisargika row and are excluded.",
        ("Tatkalika friendship", "Panchadha (compound) relation"),
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Yoga scope",
        "Only three structurally verifiable classes are tested - yogakaraka, "
        "Raja Yoga, and Dhana Yoga - each reported with the constituent facts "
        "that made it true. No yoga catalogue is applied and no phala (result) "
        "is attached to any detected yoga.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Lifespan (ayurdaya)",
        "No lifespan or longevity claim is made. Ayurdaya methods are "
        "recension-dependent and their branches disagree; length-of-life "
        "arithmetic is not asserted from this section.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Muhurta and remedies",
        "No electional (muhurta) timing and no remedial prescription - gemstone, "
        "mantra, ritual, donation - is given. Those are prescriptive advice "
        "rather than historical delineation.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Varna and social rank",
        "No caste, varna, or social-rank delineation is rendered as a claim "
        "about the reader, even where the classical sources state one. The "
        "material stays in the audit trace with its suppression reason.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Marriage compatibility",
        "No marriage-compatibility verdict (kuta / guna milan) is produced. It "
        "requires a second chart and its own source treatment, and is not a "
        "natal-reading output.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Shadbala and Ashtakavarga",
        "Shadbala and Ashtakavarga are not implemented - their weights are "
        "recension-dependent and unsourced here - so no strength claim, yoga, "
        "or period judgment depending on either is made anywhere in this "
        "section.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Interpretation depth",
        "This section reports calculation and structural condition only. "
        "Divisional charts beyond D1 and D9 are not computed, and moolatrikona "
        "boundaries are pending, so no claim resting on them is made.",
    )
