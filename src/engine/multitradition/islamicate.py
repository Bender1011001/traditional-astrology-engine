"""Islamicate (Arabic-Persian) section, on al-Qabisi's own procedures.

This is the tradition that sits between the Hellenistic corpus and the Latin
West, and the panel used to represent it only as a source audit. It now computes
the techniques al-Qabisi actually sets out in the `Mudkhal` (mid-10th century),
from the hash-pinned Wurzburg Arabic TEI, with two of his own worked examples
used as the correctness anchors rather than as decoration.

Two things this module exists to get right that the rest of the panel could not:

1. **The 5/4/3/2/1 dignity score is al-Qabisi's, not Lilly's.** He states it in
   Chapter I ("the lord of the domicile has five powers, the lord of the
   exaltation four...") and works an almuten example with it in Chapter I para
   77 - six centuries before Lilly printed it. The Hellenistic section still
   refuses the numerical score, correctly, because al-Qabisi is still far later
   than Valens; but it no longer calls the table a Latin invention.

2. **Al-Qabisi states the mean solar motion as a directions rate.** His
   59'08"/day for revolution directions is 0.98556 deg/day against the modern
   360/365.2422 = 0.985647 - agreeing to about a third of an arcsecond, and
   predating the Latin attribution of that same constant to Naibod by centuries.
   That is checked numerically here rather than asserted.

Everything below is computed from the sourced rules. Nothing is customer-facing
and no judgment about a person is produced: hyleg and kadkhudah are emitted as
the *structure* al-Qabisi defines, with the lifespan reading they were built to
support explicitly refused.
"""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any

from ..reference_data import DOROTHEAN_TRIPLICITY
from .hellenistic import (
    DOMICILE,
    EXALTATION,
    SIGNS,
    _bounds_for,
    _face_ruler,
    _sign_of,
    _triplicity,
)
from .types import BirthInput, DisclosureKind, EvidenceGrade, TraditionSection

RESEARCH_ROOT = (
    Path(__file__).resolve().parents[3] / "docs" / "research" / "multitradition"
)
QABISI_MANIFEST = RESEARCH_ROOT / "islamicate" / "al_qabisi_rule_manifest.json"

# Chapter II, one period per planet's own paragraph. They sum to 75.
FIRDARIA_YEARS = {
    "Sun": 10, "Venus": 8, "Mercury": 13, "Moon": 9,
    "Saturn": 11, "Jupiter": 12, "Mars": 7,
    "North Node": 3, "South Node": 2,
}
# The received Perso-Arabic order: diurnal nativities open with the Sun,
# nocturnal with the Moon, each running the seven then the two nodes.
FIRDARIA_DAY_ORDER = [
    "Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars",
    "North Node", "South Node",
]
FIRDARIA_NIGHT_ORDER = [
    "Moon", "Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury",
    "North Node", "South Node",
]

# Chapter I para 22. The whole point of this module's first half.
DIGNITY_POWERS = {
    "domicile": 5, "exaltation": 4, "triplicity": 3, "bound": 2, "face": 1,
}
MASCULINE_SIGNS = {
    "Aries", "Gemini", "Leo", "Libra", "Sagittarius", "Aquarius",
}

# Chapter IV. Places are 1-indexed whole-sign houses from the Ascendant.
HYLEG_SUN_ANY_GENDER = (10, 11)
HYLEG_SUN_MASCULINE_ONLY = (7, 8, 9)
HYLEG_MOON_ANY_GENDER = (1, 2, 3, 7, 8)
HYLEG_MOON_FEMININE_ONLY = (10, 11, 4, 5)
KADKHUDAH_DEFAULT_ORDER = ("domicile", "exaltation", "bound", "triplicity", "face")
KADKHUDAH_DOROTHEUS_ORDER = ("bound", "domicile", "exaltation", "triplicity", "face")

# Chapter IV: one degree of ascensional arc = one year; revolution
# significators instead run at 59'08" per day.
TASYIR_DEGREES_PER_YEAR = 1.0
TASYIR_REVOLUTION_ARCMIN = 59.0
TASYIR_REVOLUTION_ARCSEC = 8.0
MEAN_TROPICAL_YEAR_DAYS = 365.2422


@lru_cache(maxsize=1)
def _manifest() -> dict[str, Any]:
    return json.loads(QABISI_MANIFEST.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _rule_ids() -> frozenset[str]:
    return frozenset(r["rule_id"] for r in _manifest()["rules"])


def _requires(rule_id: str) -> str:
    """Fail closed if a rule this code depends on is not in the pack."""
    if rule_id not in _rule_ids():
        raise KeyError(f"al-Qabisi rule absent from pack: {rule_id}")
    return rule_id


def profect(sign_index: int, years_elapsed: int) -> int:
    """Whole-sign annual profection: one sign per completed year.

    Chapter IV states this by worked example rather than by formula, so the
    formula is verified against his own numbers in `worked_example_selfcheck`.
    """
    return (sign_index + years_elapsed) % 12


def dignity_claims(longitude: float, is_day: bool) -> dict[str, str | None]:
    """The five dignity lords of one degree, in al-Qabisi's own five categories."""
    sign, degree = _sign_of(longitude)
    bound_lord = None
    for lord, start, end in _bounds_for(sign):
        if start <= degree < end:
            bound_lord = lord
            break
    exalt_lord = next(
        (p for p, (s, _d) in EXALTATION.items() if s == sign), None
    )
    return {
        "domicile": DOMICILE.get(sign),
        "exaltation": exalt_lord,
        "triplicity": _triplicity(sign, is_day, DOROTHEAN_TRIPLICITY),
        "bound": bound_lord,
        "face": _face_ruler(longitude),
    }


def mustawli(longitude: float, is_day: bool) -> dict[str, Any]:
    """Al-mustawli - the planet prevailing over a degree by summed powers.

    This is the technique the Latin West received as `almuten`, scored with the
    5/4/3/2/1 table al-Qabisi states in Chapter I para 22.
    """
    claims = dignity_claims(longitude, is_day)
    scores: dict[str, int] = {}
    detail: dict[str, list[str]] = {}
    for category, lord in claims.items():
        if lord is None:
            continue
        power = DIGNITY_POWERS[category]
        scores[lord] = scores.get(lord, 0) + power
        detail.setdefault(lord, []).append(f"{category} +{power}")
    if not scores:
        return {"winner": None, "scores": {}, "claims": claims}
    best = max(scores.values())
    winners = sorted(p for p, s in scores.items() if s == best)
    return {
        "winner": winners[0] if len(winners) == 1 else None,
        "tied": winners if len(winners) > 1 else [],
        "scores": scores,
        "score_detail": detail,
        "claims": claims,
    }


def firdaria_periods(is_day: bool, max_years: int = 75) -> list[dict[str, Any]]:
    """The nine firdaria periods in order, with running start/end ages."""
    order = FIRDARIA_DAY_ORDER if is_day else FIRDARIA_NIGHT_ORDER
    periods: list[dict[str, Any]] = []
    age = 0.0
    for ruler in order:
        years = FIRDARIA_YEARS[ruler]
        if age >= max_years:
            break
        periods.append({
            "ruler": ruler,
            "years": years,
            "starts_at_age": round(age, 4),
            "ends_at_age": round(age + years, 4),
        })
        age += years
    return periods


def cast_lot(from_longitude: float, to_longitude: float, ascendant: float) -> float:
    """Al-Qabisi's stated general lot method, Chapter V.

    "Add to the arc between the two places the Ascendant's own degree, then cast
    that total from the start of the Ascendant's sign." Adding the arc to the
    whole ascendant longitude is the same operation and is what is done here.
    """
    return (ascendant + (to_longitude - from_longitude)) % 360


# Chapter I: which sign-distances behold, and which behold nothing. The 2nd,
# 6th, 8th and 12th from a sign see nothing of it - al-Qabisi says so outright,
# which is why aversion is computed here rather than assumed.
ASPECT_BY_SIGN_DISTANCE = {
    0: "conjunction", 2: "sextile", 10: "sextile",
    3: "square", 9: "square",
    4: "trine", 8: "trine",
    6: "opposition",
}
AVERSE_SIGN_DISTANCES = (1, 5, 7, 11)


def sign_aspect(from_longitude: float, to_longitude: float) -> str | None:
    """Whole-sign aspect between two points, per al-Qabisi's own sign table.

    Returns None where the source says the signs behold nothing of each other.
    """
    a = SIGNS.index(_sign_of(from_longitude)[0])
    b = SIGNS.index(_sign_of(to_longitude)[0])
    return ASPECT_BY_SIGN_DISTANCE.get((b - a) % 12)


def ray_falls_at(longitude: float, aspect_sign_distance: int) -> float:
    """Chapter I: a planet's ray falls in the beholding sign at the SAME degree.

    That is al-Qabisi's own definition of shu'a, and it is what makes a
    degree-level aspect check possible without inventing an orb.
    """
    sign_index = SIGNS.index(_sign_of(longitude)[0])
    degree = longitude % 30
    return ((sign_index + aspect_sign_distance) % 12) * 30 + degree


def beholders_of(
    longitude: float, planet_longitudes: dict[str, float]
) -> dict[str, str]:
    """Which planets behold a place, and by which aspect."""
    found: dict[str, str] = {}
    for name, planet_longitude in planet_longitudes.items():
        aspect = sign_aspect(planet_longitude, longitude)
        if aspect:
            found[name] = aspect
    return found


def hyleg_candidates(
    sun: float, moon: float, ascendant: float, fortune: float,
    syzygy: float | None, is_day: bool,
    planet_longitudes: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    """Every hyleg candidate al-Qabisi admits, in his stated order of inspection.

    Emitted as a candidate ledger with each place's eligibility shown, rather
    than as a single answer, because the final gate - that one of the five
    dignity lords must aspect the place - is evaluated here by whole-sign
    aspect only, which is a disclosed simplification of his own wording.
    """
    asc_index = SIGNS.index(_sign_of(ascendant)[0])

    def place_of(longitude: float) -> int:
        return ((SIGNS.index(_sign_of(longitude)[0]) - asc_index) % 12) + 1

    def is_masculine(longitude: float) -> bool:
        return _sign_of(longitude)[0] in MASCULINE_SIGNS

    def within_five_before_asc(longitude: float) -> bool:
        return 0 < (ascendant - longitude) % 360 <= 5

    def luminary_entry(name: str, longitude: float) -> dict[str, Any]:
        place = place_of(longitude)
        masculine = is_masculine(longitude)
        near_asc = within_five_before_asc(longitude)
        if name == "Sun":
            eligible = (
                near_asc
                or place in HYLEG_SUN_ANY_GENDER
                or (place in HYLEG_SUN_MASCULINE_ONLY and masculine)
            )
            basis = "10th/11th any gender; 7th/8th/9th only if masculine"
        else:
            eligible = (
                place in HYLEG_MOON_ANY_GENDER
                or near_asc
                or (place in HYLEG_MOON_FEMININE_ONLY and not masculine)
            )
            basis = "1st/2nd/3rd/7th/8th any gender; 10th/11th/4th/5th only if feminine"
        return {
            "candidate": name,
            "longitude": round(longitude, 4),
            "whole_sign_place": place,
            "sign_gender": "masculine" if masculine else "feminine",
            "within_5deg_before_ascendant": near_asc,
            "eligible_by_place": eligible,
            "place_rule": basis,
        }

    first, second = ("Sun", "Moon") if is_day else ("Moon", "Sun")
    longitudes = {"Sun": sun, "Moon": moon}
    ledger = [luminary_entry(first, longitudes[first]),
              luminary_entry(second, longitudes[second])]

    for name, longitude in (("Prenatal syzygy", syzygy),
                            ("Lot of Fortune", fortune),
                            ("Ascendant", ascendant)):
        if longitude is None:
            ledger.append({
                "candidate": name,
                "eligible_by_place": False,
                "note": "not computed in this panel; al-Qabisi requires it in the fallback chain",
            })
            continue
        place = place_of(longitude)
        angular = place in (1, 4, 7, 10)
        ledger.append({
            "candidate": name,
            "longitude": round(longitude, 4),
            "whole_sign_place": place,
            "eligible_by_place": angular or name == "Ascendant",
            "place_rule": (
                "Ascendant is the stated default if all else fails"
                if name == "Ascendant" else "must be angular"
            ),
        })

    # Al-Qabisi's final gate: a place is hyleg-eligible only if one of the five
    # dignity lords OF THAT DEGREE beholds it. Applied here properly rather than
    # skipped - that omission is what used to leave this technique unsettled.
    if planet_longitudes is not None:
        for entry in ledger:
            if entry.get("longitude") is None:
                continue
            claims = dignity_claims(entry["longitude"], is_day)
            lords = {lord for lord in claims.values() if lord}
            witnesses = {
                lord: sign_aspect(planet_longitudes[lord], entry["longitude"])
                for lord in lords
                if lord in planet_longitudes
                and sign_aspect(planet_longitudes[lord], entry["longitude"])
            }
            entry["dignity_lords_of_its_degree"] = sorted(lords)
            entry["lords_that_behold_it"] = witnesses
            entry["passes_aspect_gate"] = bool(witnesses)
            entry["eligible"] = bool(entry["eligible_by_place"]) and bool(witnesses)
    return ledger


def settle_hyleg(ledger: list[dict[str, Any]]) -> dict[str, Any]:
    """The first candidate in al-Qabisi's stated order that passes both gates.

    Candidate state is tri-valued: pass, fail, or UNKNOWN (not computed). An
    uncomputed candidate earlier in the inspection order must never be treated
    as a failure - unknown does not collapse into false. If any unknown
    candidate precedes the first passing one, the settlement is CONDITIONAL and
    says exactly what it is conditional on.
    """
    unknown_before: list[str] = []
    for entry in ledger:
        candidate = entry["candidate"]
        if entry.get("longitude") is None:
            # Not computed. Its eligibility is unknown, not false.
            unknown_before.append(candidate)
            continue
        if entry.get("eligible"):
            result: dict[str, Any] = {
                "hyleg": candidate,
                "longitude": entry["longitude"],
                "beheld_by": entry.get("lords_that_behold_it", {}),
            }
            if unknown_before:
                result["status"] = "conditional"
                result["conditional_on"] = list(unknown_before)
                result["chosen_because"] = (
                    "first COMPUTED candidate in al-Qabisi's order to pass both "
                    "the place test and the dignity-lord aspect gate - but "
                    + " and ".join(unknown_before)
                    + (" precede it in his inspection order and were not "
                       "computed, so this holds only if they do not qualify. "
                       "An uncomputed candidate is unknown, not failed.")
                )
            else:
                result["status"] = "settled"
                result["chosen_because"] = (
                    "first candidate in al-Qabisi's own order of inspection to "
                    "pass both the place test and the dignity-lord aspect gate; "
                    "every earlier candidate was computed and failed"
                )
            return result
    default = next(
        (e for e in ledger if e["candidate"] == "Ascendant"), None
    )
    result = {
        "hyleg": "Ascendant",
        "longitude": default["longitude"] if default else None,
        "status": "conditional" if unknown_before else "settled",
        "chosen_because": (
            "no computed candidate passed both gates; al-Qabisi's stated "
            "default is the Ascendant degree itself"
        ),
        "beheld_by": default.get("lords_that_behold_it", {}) if default else {},
    }
    if unknown_before:
        result["conditional_on"] = list(unknown_before)
        result["chosen_because"] += (
            "; conditional, because " + " and ".join(unknown_before)
            + " were never computed and their eligibility is unknown"
        )
    return result


def kadkhudah_for(
    hyleg_longitude: float,
    is_day: bool,
    dorotheus_order: bool = False,
    planet_longitudes: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Kadkhudah by priority order, with the Dorotheus fork computed both ways.

    Al-Qabisi requires the candidate to BEHOLD the hyleg, not merely to hold a
    dignity over it: "whichever of these holds the greatest claim over the
    hyleg's degree AND beholds the hyleg." When planet positions are supplied
    the aspect gate is applied and non-beholding lords are skipped, which is
    what the text actually says to do.
    """
    claims = dignity_claims(hyleg_longitude, is_day)
    order = KADKHUDAH_DOROTHEUS_ORDER if dorotheus_order else KADKHUDAH_DEFAULT_ORDER
    skipped: list[dict[str, str]] = []
    for category in order:
        lord = claims.get(category)
        if not lord:
            continue
        if planet_longitudes is not None:
            aspect = (
                sign_aspect(planet_longitudes[lord], hyleg_longitude)
                if lord in planet_longitudes else None
            )
            if not aspect:
                skipped.append({"lord": lord, "category": category,
                                "reason": "does not behold the hyleg"})
                continue
            return {
                "kadkhudah": lord, "won_by": category, "beholds_by": aspect,
                "order_used": list(order), "aspect_gate_applied": True,
                "skipped_for_not_beholding": skipped,
            }
        return {
            "kadkhudah": lord, "won_by": category,
            "order_used": list(order), "aspect_gate_applied": False,
        }
    return {
        "kadkhudah": None, "order_used": list(order),
        "aspect_gate_applied": planet_longitudes is not None,
        "skipped_for_not_beholding": skipped,
        "note": "no dignity lord of the hyleg's degree beholds it",
    }


# Chapter V. Formula is (from, to, cast_from); "reverse" flips from/to by night.
NAMED_LOTS = {
    "Fortune": ("Sun", "Moon", "Ascendant", True),
    "Spirit": ("Moon", "Sun", "Ascendant", True),
    "Life": ("Jupiter", "Saturn", "Ascendant", True),
    "Men's marriage": ("Sun", "Venus", "Ascendant", False),
    "Women's marriage (Hermes)": ("Venus", "Saturn", "Ascendant", False),
    "Women's marriage (Valens)": ("Sun", "Moon", "Ascendant", False),
    "Enemies (some of the ancients)": ("Saturn", "Mars", "Ascendant", False),
}


def named_lots(
    planet_longitudes: dict[str, float], ascendant: float, is_day: bool
) -> dict[str, Any]:
    """The named lots of Chapter V whose formulas use only planets and the Asc.

    House-cusp-based lots (Wealth, Death, Enemies-per-Hermes) need cusps this
    section does not compute and are named as omitted rather than approximated.
    """
    out: dict[str, Any] = {}
    for label, (a, b, _cast, sect_reverses) in NAMED_LOTS.items():
        if a not in planet_longitudes or b not in planet_longitudes:
            continue
        first, second = (a, b) if (is_day or not sect_reverses) else (b, a)
        longitude = cast_lot(
            planet_longitudes[first], planet_longitudes[second], ascendant
        )
        out[label] = {
            "longitude": round(longitude, 4),
            "sign": _sign_of(longitude)[0],
            "degree": round(longitude % 30, 4),
            "formula": f"{first} -> {second}, cast from the Ascendant",
            "sect_reverses": sect_reverses,
        }
    out["_omitted_house_cusp_lots"] = (
        "Wealth (2nd), Death (8th, cast from Saturn not the Ascendant), "
        "Sultanate (10th), Friends (11th), Enemies per Hermes (12th) all key "
        "to house cusps or the Midheaven; this section computes whole-sign "
        "places, not cusps, so they are named and not approximated."
    )
    return out


def planetary_condition(
    planet_longitudes: dict[str, float], is_day: bool
) -> dict[str, Any]:
    """Chapter III condition doctrine, to the extent longitudes alone decide it.

    Reception and aversion/feral are decidable from position. Translation and
    collection of light, prevention, and every frustration variant additionally
    need speed, retrogradation and combustion state, which this section does not
    receive - so those are reported as not decided rather than guessed at.
    """
    receptions: list[dict[str, str]] = []
    for name, longitude in planet_longitudes.items():
        claims = dignity_claims(longitude, is_day)
        for category, lord in claims.items():
            if not lord or lord == name or lord not in planet_longitudes:
                continue
            aspect = sign_aspect(longitude, planet_longitudes[lord])
            if aspect:
                receptions.append({
                    "planet": name, "received_by": lord,
                    "by_dignity": category, "aspect": aspect,
                })
    feral = [
        name for name, longitude in planet_longitudes.items()
        if not any(
            other != name and sign_aspect(planet_longitudes[other], longitude)
            for other in planet_longitudes
        )
    ]
    return {
        "reception_qabul": receptions,
        "feral_wahshi": feral,
        "feral_definition": (
            "a planet in a sign no other planet beholds, for as long as it "
            "remains there (Ch. III)"
        ),
        "not_decided_here": {
            "translation_and_collection_of_light": "needs planetary speed ordering",
            "prevention_man": "needs degree-ordered application within a sign",
            "frustration_variants": "needs retrogradation state",
            "return_radd": "needs combustion and retrogradation state",
        },
        "friendship_table_note": (
            "Al-Qabisi's friendship/enmity table is attributed to 'some of the "
            "ancients' and is explicitly ASYMMETRIC - Saturn is more hostile to "
            "Venus than she to him. It is recorded in the rule pack and is not "
            "reduced to a symmetric matrix here, because symmetrising it would "
            "destroy the property the source is careful to state."
        ),
    }


def oblique_ascension(longitude: float, geo_lat: float, obliquity: float) -> float:
    """Oblique ascension of an ecliptic degree for a latitude.

    OA = RA - AD, with AD the ascensional difference. This is the measure
    al-Qabisi's jarbakhtar explicitly calls for ("the Ascendant's oblique
    ascension for the locality"), not right ascension.
    """
    lam = math.radians(longitude % 360)
    eps = math.radians(obliquity)
    ra = math.degrees(math.atan2(math.cos(eps) * math.sin(lam), math.cos(lam))) % 360
    dec = math.asin(math.sin(eps) * math.sin(lam))
    tan_product = math.tan(math.radians(geo_lat)) * math.tan(dec)
    if abs(tan_product) > 1:  # circumpolar: the degree never rises here
        return ra
    ascensional_difference = math.degrees(math.asin(tan_product))
    return (ra - ascensional_difference) % 360


def jarbakhtar(
    ascendant: float, geo_lat: float, obliquity: float, limit: int = 6
) -> list[dict[str, Any]]:
    """Al-Qabisi's bound-directions of the Ascendant, Chapter IV.

    Direct the Ascendant to the end of its own bound by oblique ascension; the
    bound's lord governs that many years, at his stated rate of one year per
    degree, one month per five arcminutes, six days per arcminute. Then the next
    bound's lord takes over, and so on for life.
    """
    periods: list[dict[str, Any]] = []
    cursor = ascendant % 360
    total_years = 0.0
    for _ in range(limit):
        sign, degree = _sign_of(cursor)
        bound = next(
            ((lord, s, e) for lord, s, e in _bounds_for(sign) if s <= degree < e),
            None,
        )
        if bound is None:
            break
        lord, _start, end = bound
        end_longitude = SIGNS.index(sign) * 30 + end
        arc = (
            oblique_ascension(end_longitude, geo_lat, obliquity)
            - oblique_ascension(cursor, geo_lat, obliquity)
        ) % 360
        years = arc * TASYIR_DEGREES_PER_YEAR
        periods.append({
            "bound_lord": lord,
            "from": {"sign": sign, "degree": round(degree, 4)},
            "to_bound_end_degree": end,
            "oblique_arc_degrees": round(arc, 4),
            "years": round(years, 4),
            "starts_at_age": round(total_years, 4),
            "ends_at_age": round(total_years + years, 4),
        })
        total_years += years
        cursor = (end_longitude + 1e-9) % 360
    return periods


def revolution_rate_degrees_per_day() -> float:
    """Al-Qabisi's 59'08" per day, in degrees."""
    return (TASYIR_REVOLUTION_ARCMIN + TASYIR_REVOLUTION_ARCSEC / 60.0) / 60.0


def build(birth: BirthInput, chart: Any) -> TraditionSection:
    section = TraditionSection(
        tradition_id="islamicate_al_qabisi",
        display_name="Islamicate (al-Qabisi's own procedures)",
        evidence_grade=EvidenceGrade.LIVE_ENGINE,
        basis=(
            "Al-Qabisi's own procedures from the Mudkhal (mid-10th century), "
            "computed on tropical positions from the shipping engine. Two of his "
            "worked examples are reproduced below as correctness anchors."
        ),
    )
    section.disclose(
        DisclosureKind.SOURCE,
        "Text and edition",
        "Al-Qabisi, al-Mudkhal ila Sina'at Ahkam al-Nujum, from the Wurzburg "
        "Arabic TEI (CC BY-SA 4.0), hash-pinned in this repository. Rules were "
        "read from the Arabic directly; every rendering is graded "
        "engine_translation_unreviewed and an independent Arabic specialist "
        "review is still outstanding, so nothing here may be promoted to "
        "customer-facing prose.",
    )
    section.disclose(
        DisclosureKind.SOURCE,
        "The dignity score is al-Qabisi's, not Lilly's",
        "Chapter I para 22 states the 5/4/3/2/1 table outright - domicile five "
        "powers, exaltation four, triplicity three, bound two, face one - and "
        "para 77 works an almuten example with it. Lilly printed it in 1647; "
        "al-Qabisi wrote it roughly six centuries earlier, and the Latin West "
        "received it in translation. The Hellenistic section still refuses the "
        "numerical score, which remains correct: al-Qabisi is later than Valens "
        "either way. Only the attribution was wrong, and it has been corrected "
        "there too.",
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Houses",
        "Whole-sign places are used for the hyleg candidate positions. "
        "Al-Qabisi's own angularity test is stated against an equal-hour house "
        "division set out in his zij, which this panel does not compute; the "
        "whole-sign reading is a disclosed simplification and can move a "
        "borderline candidate.",
        ("Equal-hour division per al-Qabisi's zij", "Regiomontanus", "Porphyry"),
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "No lifespan number",
        "Hyleg and kadkhudah exist in this tradition to yield a quantity of "
        "life, and that output is refused. The candidate structure is shown "
        "because it is the tradition's own core method and omitting it would be "
        "a worse misrepresentation than showing it; the years are not computed, "
        "and no death claim is produced.",
    
        category="policy_suppressed",
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Aspect model behind the hyleg and kadkhudah gates",
        "Al-Qabisi requires that a hyleg place be beheld by one of the five "
        "dignity lords of its degree, and that a kadkhudah candidate behold the "
        "hyleg. That gate IS applied here, using his own Chapter I sign-aspect "
        "table - sextile at the 3rd and 11th, square at the 4th and 10th, trine "
        "at the 5th and 9th, opposition at the 7th, and nothing at all at the "
        "2nd, 6th, 8th and 12th, which he states outright. Whole-sign aspect is "
        "used rather than a degree orb, because he defines the ray as falling "
        "in the beholding sign at the same degree and never states an orb; a "
        "degree-orb model would be an import, and it can move a borderline "
        "candidate.",
        ("Degree-based aspects with an orb", "Moiety-of-orbs models"),
    )

    sun_altitude = getattr(chart, "sun_altitude", 0.0)
    is_day = sun_altitude > 0
    planet_map = {p.name.value: p for p in chart.planets}
    sun = planet_map["Sun"].longitude
    moon = planet_map["Moon"].longitude
    ascendant = chart.ascendant
    fortune = cast_lot(sun, moon, ascendant) if is_day else cast_lot(moon, sun, ascendant)
    planet_longitudes = {
        name: planet_map[name].longitude
        for name in ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn")
        if name in planet_map
    }

    asc_sign, asc_degree = _sign_of(ascendant)
    asc_index = SIGNS.index(asc_sign)

    section.disclose(
        DisclosureKind.FORK,
        "Kadkhudah priority order",
        "Al-Qabisi's default runs domicile, exaltation, bound, triplicity, face. "
        "He names Dorotheus as reversing it, putting the bound lord ahead of the "
        "domicile lord. Both are computed below; neither is asserted, because "
        "the source states the disagreement without resolving it.",
        ("Dorotheus: bound lord before domicile lord",),
    )

    rate = revolution_rate_degrees_per_day()
    modern = 360.0 / MEAN_TROPICAL_YEAR_DAYS
    _ledger = hyleg_candidates(
        sun, moon, ascendant, fortune, None, is_day, planet_longitudes
    )
    _settled = settle_hyleg(_ledger)
    section.facts = {
        "sect": "day" if is_day else "night",
        "dignity_scoring_table": {
            "source": "Chapter I para 22 (rule islam.qabisi.ch1.dignity_power_scoring)",
            "powers": DIGNITY_POWERS,
            "note": "the table Lilly later printed; stated here in Arabic c. 950 CE",
        },
        "mustawli_of_the_ascendant": mustawli(ascendant, is_day),
        "ascendant": {"sign": asc_sign, "degree": round(asc_degree, 4)},
        "firdaria": {
            "order_basis": "diurnal opens with the Sun, nocturnal with the Moon",
            "years_table": FIRDARIA_YEARS,
            "total_years": sum(FIRDARIA_YEARS.values()),
            "periods": firdaria_periods(is_day),
        },
        "lot_of_fortune": {
            "longitude": round(fortune, 4),
            "sign": _sign_of(fortune)[0],
            "method": "arc Sun->Moon by day (reversed by night) cast from the Ascendant",
        },
        "hyleg_candidate_ledger": hyleg_candidates(
            sun, moon, ascendant, fortune, None, is_day, planet_longitudes
        ),
        "hyleg_settled": _settled,
        "named_lots": named_lots(planet_longitudes, ascendant, is_day),
        "planetary_condition": planetary_condition(planet_longitudes, is_day),
        "kadkhudah_forks": {
            "note": (
                "Computed on the settled hyleg's own degree, with al-Qabisi's "
                "aspect gate applied: a dignity lord that does not behold the "
                "hyleg is skipped, and the skips are listed. Structure, not a "
                "lifespan verdict - the years are still refused."
            ),
            "locus": _settled["hyleg"],
            "al_qabisi_default": kadkhudah_for(
                _settled["longitude"], is_day, False, planet_longitudes
            ),
            "dorotheus_order": kadkhudah_for(
                _settled["longitude"], is_day, True, planet_longitudes
            ),
        },
        "tasyir": {
            "general_rate": "one degree of ascensional arc = one year",
            "revolution_rate_arcmin_arcsec": "59'08\" per day",
            "revolution_rate_degrees_per_day": round(rate, 8),
            "modern_mean_solar_motion_degrees_per_day": round(modern, 8),
            "difference_arcseconds": round(abs(rate - modern) * 3600.0, 4),
            "finding": (
                "al-Qabisi's stated constant IS the mean solar motion, given "
                "directly, centuries before the Latin tradition attached the "
                "same value to Naibod"
            ),
            "significators_directed": [
                "Ascendant degree", "Sun", "Moon", "Lot of Fortune", "Midheaven",
            ],
            "jarbakhtar_bound_directions": jarbakhtar(
                ascendant,
                getattr(chart, "geo_lat", 0.0),
                getattr(chart, "obliquity", 23.4392911),
            ),
            "jarbakhtar_conversion": (
                "1 degree = 1 year, 5 arcminutes = 1 month, 1 arcminute = 6 "
                "days - mutually consistent under a schematic 360-day year"
            ),
            "still_not_computed": (
                "directions of the five significators to arbitrary promittors; "
                "only the Ascendant's own bound-directions are run, which is "
                "the one case al-Qabisi specifies completely"
            ),
        },
        "profection_of_this_birth": {
            "natal_ascendant_sign": asc_sign,
            "method": "whole-sign, one sign per completed year",
            "example_years_1_to_12": [
                {
                    "completed_years": n,
                    "profected_sign": SIGNS[profect(asc_index, n)],
                    "year_lord": DOMICILE[SIGNS[profect(asc_index, n)]],
                }
                for n in range(12)
            ],
        },
        "worked_example_selfcheck": worked_example_selfcheck(),
    }
    return section


def worked_example_selfcheck() -> dict[str, Any]:
    """Reproduce al-Qabisi's own two worked examples. Neither is this birth.

    These are the anchors that make the rest of the module checkable: if the
    profection formula or the 5/4/3/2/1 scoring were wrong, these would fail.
    """
    _requires("islam.qabisi.ch4.annual_profection_worked_example")
    _requires("islam.qabisi.ch1.mustawli_worked_example")

    # Chapter IV: Asc Capricorn 17, MC Scorpio 8, Sun Pisces 15, Moon Libra 15,
    # Fortune Leo 19, three complete years elapsed.
    elapsed = 3
    stated = {
        "ascendant": ("Capricorn", "Aries"),
        "sun": ("Pisces", "Gemini"),
        "moon": ("Libra", "Capricorn"),
        "midheaven": ("Scorpio", "Aquarius"),
        "lot_of_fortune": ("Leo", "Scorpio"),
    }
    profection_rows = {}
    for point, (natal, expected) in stated.items():
        got = SIGNS[profect(SIGNS.index(natal), elapsed)]
        profection_rows[point] = {
            "natal_sign": natal,
            "al_qabisi_says": expected,
            "computed": got,
            "matches": got == expected,
        }
    year_lord = DOMICILE["Aries"]
    profection_rows["salkhadhay_year_lord"] = {
        "al_qabisi_says": "Mars",
        "computed": year_lord,
        "matches": year_lord == "Mars",
    }

    # Chapter I para 77: the 2nd house at 5 Aries. Mars 5(domicile)+1(face)=6;
    # Sun 4(exaltation)+3(triplicity)=7; so the Sun prevails.
    aries_five = SIGNS.index("Aries") * 30 + 5.0
    scored = mustawli(aries_five, is_day=True)
    mustawli_row = {
        "locus": "5 degrees of Aries (al-Qabisi's own example)",
        "al_qabisi_says": {"Mars": 6, "Sun": 7, "winner": "Sun"},
        "computed_scores": scored["scores"],
        "computed_winner": scored["winner"],
        "mars_matches": scored["scores"].get("Mars") == 6,
        "sun_matches": scored["scores"].get("Sun") == 7,
        "winner_matches": scored["winner"] == "Sun",
    }

    firdaria_total = sum(FIRDARIA_YEARS.values())
    return {
        "note": (
            "Al-Qabisi's own worked examples, reproduced. Not this birth's chart."
        ),
        "annual_profection": profection_rows,
        "all_profection_points_match": all(
            row["matches"] for row in profection_rows.values()
        ),
        "mustawli_dignity_scoring": mustawli_row,
        "mustawli_fully_matches": (
            mustawli_row["mars_matches"]
            and mustawli_row["sun_matches"]
            and mustawli_row["winner_matches"]
        ),
        "firdaria_total_years": firdaria_total,
        "firdaria_total_matches_stated_75": firdaria_total == 75,
    }
