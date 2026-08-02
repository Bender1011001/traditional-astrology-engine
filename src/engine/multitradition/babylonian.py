"""Mesopotamian section: an omen corpus, read as an omen corpus.

The governing constraint is a genre boundary, not a technique gap. Enuma Anu
Enlil and the Neo-Assyrian celestial reports judge kings, lands, armies and
harvests; they contain no personality genre at all, and the small Late
Babylonian horoscope corpus is mostly positional record rather than judgment.
So this section reports positions in the tradition's own idiom, reports the
lunar and eclipse condition, surfaces only those encoded omen protases the birth
sky actually satisfies - each apodosis quoted, attributed, and labeled as a
claim about kings and lands - and then stops. It never synthesizes a natal
judgment, because the sources contain nothing to synthesize one from.

Rules are loaded from the hash-pinned research manifests on disk, the same way
`mesoamerican` loads its calendar kernel.
"""

from __future__ import annotations

import json
from datetime import timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

import swisseph as swe

from .timebase import TimeBases
from .types import BirthInput, DisclosureKind, EvidenceGrade, TraditionSection

RESEARCH_ROOT = (
    Path(__file__).resolve().parents[3] / "docs" / "research" / "multitradition"
)
BABYLONIAN = RESEARCH_ROOT / "babylonian"

# The four eclipse-omen packs. Every protasis in them presupposes an eclipse.
OMEN_MANIFESTS = (
    "eae20_witness_rule_manifest.json",
    "eae16_21_commentary_rule_manifest.json",
    "saa8_316_applied_eclipse_rule_manifest.json",
    "saa8_535_lunar_eclipse_rule_manifest.json",
)
# The natal branch: 21 explicit judgment clauses across Texts 1-28.
JUDGMENT_MANIFESTS = (
    "rochberg_texts2_5_9_judgment_rule_manifest.json",
    "rochberg_text16_judgment_rule_manifest.json",
    "rochberg_text27_judgment_rule_manifest.json",
    "rochberg_text10_rule_manifest.json",
)
CATALOG = "rochberg_full_corpus_catalog.json"
CONCORDANCE = "rochberg_cdli_concordance.json"

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
# Rochberg's edition tabulates a horoscope in this order; see
# rochberg_texts1_10_astronomy_spec.json, `published_adjusted_longitudes`.
BABYLONIAN_BODY_ORDER = [
    "Moon", "Sun", "Jupiter", "Venus", "Mercury", "Saturn", "Mars",
]

MONTHS = [
    "nisannu", "ayyaru", "simanu", "duuzu", "abu", "ululu",
    "tashritu", "arahsamna", "kislimu", "tebetu", "shabatu", "addaru",
]
MONTH_LABELS = {
    "nisannu": "Nisannu", "ayyaru": "Ayyaru", "simanu": "Simanu",
    "duuzu": "Du'uzu", "abu": "Abu", "ululu": "Ululu",
    "tashritu": "Tashritu", "arahsamna": "Arahsamna", "kislimu": "Kislimu",
    "tebetu": "Tebetu", "shabatu": "Shabatu", "addaru": "Addaru",
}
# SAA 8 writes the third month `sivan`; the EAE commentary writes `simanu`.
MONTH_ALIASES = {"sivan": "simanu", "tasritu": "tashritu", "du'uzu": "duuzu"}

SYNODIC_MONTH_DAYS = 29.530588853
# Configured first-visibility criterion; disclosed, with alternatives named.
CRESCENT_LAG_MINUTES = 48.0
FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED

# Facts a modern ephemeris can genuinely reconstruct for a birth moment.
MONTH_FACTS = {"babylonian_month", "month"}
DAY_FACTS = {"babylonian_day", "day", "lunar_eclipse_day"}
RECONSTRUCTIBLE = MONTH_FACTS | DAY_FACTS | {
    "phenomenon", "watch", "sets_while_eclipsed",
}

# Why a protasis cannot be evaluated. Reported, never silently dropped.
UNEVALUABLE_REASONS = {
    "wind": "wind and weather observation",
    "winds": "wind and weather observation",
    "lightning": "wind and weather observation",
    "sky_clears": "wind and weather observation",
    "cloud_configuration": "cloud observation",
    "moon_exits_cloud": "cloud observation",
    "moon_dark_region": "requires a Babylonian sidereal zodiac this panel lacks",
    "numusda_relation": "fixed-star relation not reduced to a computable rule",
    "additional_star_state": "fixed-star relation not reduced to a computable rule",
    "papsukkal_state": "fixed-star relation not reduced to a computable rule",
    "venus_moon_event": "planet-in-Moon observation, not a longitude test",
    "venus.event": "planet-in-Moon observation, not a longitude test",
    "moon.motion_relative_to_nodal_zone": "source-gated: the pack requires an "
    "independent lunar-latitude definition before this may be computed",
    "moon.progress_condition": "source-gated pending Assyriological review",
    "source_record": "identifies an ancient record, not a sky condition",
    "source_profile": "identifies an ancient record, not a sky condition",
    "historical_report_passage": "identifies an ancient record, not a sky "
    "condition",
    "commentary_lemma": "commentary layer, keyed to a base omen rather than a sky",
    "base_expression": "commentary layer, keyed to a base omen rather than a sky",
    "base_apodosis": "commentary layer, keyed to a base omen rather than a sky",
    "base_selector": "commentary layer, keyed to a base omen rather than a sky",
    "base_date": "commentary layer, keyed to a base omen rather than a sky",
    "manuscript_reading": "commentary layer, keyed to a manuscript variant",
    "available_selectors": "interpretive framework, not a protasis",
}
DEFAULT_UNEVALUABLE = (
    "eclipse-shape, quadrant, or phase-progress observation no modern "
    "reconstruction can supply"
)

GENRE_LABEL = "claim about kings, lands, armies and harvests - not about a person"


@lru_cache(maxsize=16)
def _manifest(name: str) -> dict[str, Any]:
    return json.loads((BABYLONIAN / name).read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _omen_rules() -> tuple[tuple[str, dict[str, Any]], ...]:
    return tuple(
        (name, rule)
        for name in OMEN_MANIFESTS
        for rule in _manifest(name)["rules"]
    )


@lru_cache(maxsize=1)
def _judgment_rules() -> tuple[tuple[str, dict[str, Any]], ...]:
    return tuple(
        (name, rule)
        for name in JUDGMENT_MANIFESTS
        for rule in _manifest(name)["rules"]
    )


# --------------------------------------------------------------------------
# astronomy
# --------------------------------------------------------------------------


def _longitude(jd: float, body: int) -> float:
    return swe.calc_ut(jd, body, FLAGS)[0][0]


def _elongation(jd: float) -> float:
    """Moon minus Sun, folded to (-180, 180]. Zero at conjunction."""
    delta = _longitude(jd, swe.MOON) - _longitude(jd, swe.SUN)
    return ((delta + 180.0) % 360.0) - 180.0


def _refine_conjunction(guess: float) -> float:
    lo, hi = guess - 1.5, guess + 1.5
    for _ in range(6):
        if _elongation(lo) < 0 < _elongation(hi):
            break
        lo -= 1.0
        hi += 1.0
    for _ in range(40):
        mid = (lo + hi) / 2.0
        if _elongation(mid) < 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def _previous_conjunction(jd: float) -> float:
    age_days = (_elongation(jd) % 360.0) / (360.0 / SYNODIC_MONTH_DAYS)
    return _refine_conjunction(jd - age_days)


def _event(jd: float, body: int, flag: int, geo: tuple[float, float, float]):
    result, times = swe.rise_trans(jd, body, flag, geo)
    return times[0] if result == 0 else None


def _day_one_evening(
    conjunction_jd: float, geo: tuple[float, float, float]
) -> float | None:
    """First sunset after conjunction at which the crescent would be visible.

    The criterion is the configured moonset lag; see the disclosure.
    """
    probe = conjunction_jd
    for _ in range(6):
        sunset = _event(probe, swe.SUN, swe.CALC_SET, geo)
        if sunset is None:
            return None
        moonset = _event(sunset - 1e-4, swe.MOON, swe.CALC_SET, geo)
        if moonset is not None:
            lag_minutes = (moonset - sunset) * 1440.0
            if CRESCENT_LAG_MINUTES <= lag_minutes <= 720.0:
                return sunset
        probe = sunset + 1e-3
    return None


def _project_calendar(jd: float, geo: tuple[float, float, float]) -> dict[str, Any]:
    """Project a Babylonian month and day onto a modern instant.

    Nisannu is the first month whose day 1 begins on or after the vernal
    equinox; a thirteenth month is reported as intercalary. This is a modern
    reconstruction, not a historical date - the calendar is being run roughly
    two thousand years past its attested use.
    """
    equinox = swe.solcross_ut(0.0, jd - 400.0, FLAGS)
    while True:
        following = swe.solcross_ut(0.0, equinox + 10.0, FLAGS)
        if following > jd:
            break
        equinox = following
    start = _refine_conjunction(_previous_conjunction(equinox + 5.0) - 2 * SYNODIC_MONTH_DAYS)

    day_ones: list[float] = []
    found_nisannu = False
    for step in range(24):
        conjunction = _refine_conjunction(start + step * SYNODIC_MONTH_DAYS)
        day_one = _day_one_evening(conjunction, geo)
        if day_one is None:
            continue
        if not found_nisannu:
            if day_one < equinox:
                continue
            found_nisannu = True
        day_ones.append(day_one)
        if day_one > jd:
            break
    index = None
    for position, day_one in enumerate(day_ones):
        if day_one <= jd:
            index = position
    if index is None:
        return {"status": "not_projectable"}

    month_start = day_ones[index]
    day_number = 1
    cursor = month_start
    for _ in range(40):
        nxt = _event(cursor + 0.1, swe.SUN, swe.CALC_SET, geo)
        if nxt is None or nxt > jd:
            break
        day_number += 1
        cursor = nxt

    intercalary = index >= 12
    name = MONTHS[index % 12]
    return {
        "status": "modern_projection_not_a_historical_date",
        "month_index": index + 1,
        "month": name,
        "month_label": (
            f"intercalary {MONTH_LABELS[name]}" if intercalary else MONTH_LABELS[name]
        ),
        "intercalary": intercalary,
        "day": day_number,
        "day_one_evening_ut": _iso(month_start),
        "year_began_ut": _iso(day_ones[0]),
        "vernal_equinox_ut": _iso(equinox),
    }


def _iso(jd: float) -> str:
    year, month, day, hour = swe.revjul(jd)
    from datetime import datetime

    return (
        datetime(year, month, day) + timedelta(hours=hour)
    ).strftime("%Y-%m-%dT%H:%M UT")


def _night_watch(jd: float, geo: tuple[float, float, float]) -> dict[str, Any]:
    """Evening / middle / dawn watch, as equal thirds of the night."""
    sunset = _event(jd - 1.0, swe.SUN, swe.CALC_SET, geo)
    sunrise = _event(jd - 1.0, swe.SUN, swe.CALC_RISE, geo)
    if sunset is None or sunrise is None:
        return {"is_night": False, "watch": None, "status": "not_computable"}
    last_sunset = sunset
    while True:
        nxt = _event(last_sunset + 0.1, swe.SUN, swe.CALC_SET, geo)
        if nxt is None or nxt > jd:
            break
        last_sunset = nxt
    next_sunrise = _event(last_sunset, swe.SUN, swe.CALC_RISE, geo)
    if next_sunrise is None or not (last_sunset <= jd <= next_sunrise):
        return {"is_night": False, "watch": None, "status": "daylight_birth"}
    fraction = (jd - last_sunset) / (next_sunrise - last_sunset)
    watch = "evening" if fraction < 1 / 3 else ("middle" if fraction < 2 / 3 else "dawn")
    return {
        "is_night": True,
        "watch": watch,
        "sunset_ut": _iso(last_sunset),
        "sunrise_ut": _iso(next_sunrise),
        "fraction_of_night": round(fraction, 4),
    }


def _eclipse_type(flag: int) -> str:
    if flag & swe.ECL_TOTAL:
        return "total"
    if flag & swe.ECL_ANNULAR:
        return "annular"
    if flag & swe.ECL_PARTIAL:
        return "partial"
    if flag & swe.ECL_PENUMBRAL:
        return "penumbral"
    return "unclassified"


def _eclipse_condition(jd: float, geo: tuple[float, float, float]) -> dict[str, Any]:
    flag, attributes = swe.lun_eclipse_how(jd, geo, swe.FLG_SWIEPH)
    umbral = float(attributes[0]) if flag else 0.0
    condition: dict[str, Any] = {
        "lunar_eclipse_in_progress": umbral > 0.0,
        "umbral_magnitude_at_birth": round(umbral, 4),
        "penumbral_magnitude_at_birth": round(float(attributes[1]), 4) if flag else 0.0,
    }
    for label, backwards in (("previous", True), ("next", False)):
        try:
            retflag, times = swe.lun_eclipse_when(jd, swe.FLG_SWIEPH, 0, backwards)
        except Exception:  # noqa: BLE001 - proximity is optional context
            continue
        condition[f"{label}_lunar_eclipse"] = {
            "maximum_ut": _iso(times[0]),
            "type": _eclipse_type(retflag),
            "days_from_birth": round(times[0] - jd, 3),
        }
    try:
        retflag, times = swe.sol_eclipse_when_glob(jd, swe.FLG_SWIEPH, 0, False)
        condition["next_solar_eclipse"] = {
            "maximum_ut": _iso(times[0]),
            "type": _eclipse_type(retflag),
            "days_from_birth": round(times[0] - jd, 3),
        }
    except Exception:  # noqa: BLE001
        pass
    return condition


def _sets_while_eclipsed(
    jd: float, geo: tuple[float, float, float], in_progress: bool
) -> bool:
    if not in_progress:
        return False
    moonset = _event(jd, swe.MOON, swe.CALC_SET, geo)
    if moonset is None:
        return False
    flag, attributes = swe.lun_eclipse_how(moonset, geo, swe.FLG_SWIEPH)
    return bool(flag) and float(attributes[0]) > 0.0


# --------------------------------------------------------------------------
# rule matching
# --------------------------------------------------------------------------


def _month_key(value: Any) -> str | None:
    if isinstance(value, int) and 1 <= value <= 12:
        return MONTHS[value - 1]
    if isinstance(value, str):
        key = value.strip().lower()
        return MONTH_ALIASES.get(key, key)
    return None


def _conditions(rule: dict[str, Any]) -> list[tuple[str, str, Any]]:
    """Flatten both manifest condition shapes into (fact, operator, value)."""
    flattened: list[tuple[str, str, Any]] = []
    for key, value in (rule.get("conditions") or {}).items():
        if key == "all" and isinstance(value, list):
            for clause in value:
                if isinstance(clause, dict) and "fact" in clause:
                    flattened.append(
                        (clause["fact"], clause.get("operator", "equals"),
                         clause.get("value"))
                    )
                else:
                    flattened.append(("__opaque__", "unresolved", clause))
        else:
            flattened.append((key, "equals", value))
    return flattened


def _satisfied(fact: str, operator: str, value: Any, sky: dict[str, Any]) -> bool:
    if fact in MONTH_FACTS:
        return _month_key(value) == sky.get("babylonian_month")
    if fact in DAY_FACTS:
        day = sky.get("babylonian_day")
        if day is None:
            return False
        if operator == "in" and isinstance(value, list):
            return day in value
        if operator == "between_inclusive" and isinstance(value, list):
            return value[0] <= day <= value[1]
        return value == day
    if fact == "phenomenon":
        return sky.get("phenomenon") == "lunar_eclipse"
    return sky.get(fact) == value


def evaluate_rules(sky: dict[str, Any]) -> dict[str, Any]:
    """Evaluate every encoded omen protasis against a reconstructed sky.

    Pure over `sky`, so the matching path can be exercised directly. Nothing is
    stretched: a protasis naming any condition the reconstruction cannot supply
    is reported as unevaluable rather than partially matched, and because every
    protasis in these packs presupposes an eclipse, none matches unless one was
    actually in progress.
    """
    matched: list[dict[str, Any]] = []
    overlap: list[dict[str, Any]] = []
    unevaluable: dict[str, int] = {}
    not_matched = 0
    in_progress = sky.get("phenomenon") == "lunar_eclipse"

    non_executable = 0
    for manifest_name, rule in _omen_rules():
        scope = rule.get("scope") or {}
        conclusion = rule.get("conclusion") or {}
        if scope.get("executable") is False or conclusion.get("executable") is False:
            # The pack itself forbids running this rule; honour that first.
            non_executable += 1
            continue
        clauses = _conditions(rule)
        blockers = [
            fact for fact, operator, _ in clauses
            if operator in {"unresolved", "contains_all", "contains_all_available"}
            or fact not in RECONSTRUCTIBLE
        ]
        if blockers:
            reason = UNEVALUABLE_REASONS.get(blockers[0], DEFAULT_UNEVALUABLE)
            unevaluable[reason] = unevaluable.get(reason, 0) + 1
            continue

        selectors = [c for c in clauses if c[0] != "phenomenon"]
        if not all(_satisfied(*clause, sky) for clause in selectors):
            not_matched += 1
            continue

        record = _apodosis_record(manifest_name, rule)
        calendar = [c for c in selectors if c[0] in MONTH_FACTS | DAY_FACTS]
        if in_progress:
            matched.append(record)
        else:
            not_matched += 1
            if calendar:
                overlap.append(record)

    return {
        "rules_evaluated": len(_omen_rules()),
        "matched": matched,
        "matched_count": len(matched),
        "non_executable_by_pack": non_executable,
        "not_matched_count": not_matched,
        "unevaluable_count": sum(unevaluable.values()),
        "unevaluable_reasons": unevaluable,
        "calendar_selector_overlap": overlap,
        "calendar_selector_overlap_note": (
            "Not matches. These protases name the projected month or day, but the "
            "lunar eclipse every one of them presupposes did not occur."
        ),
    }


def _attribution(rule: dict[str, Any]) -> str:
    passages = rule.get("source_passages") or []
    if not passages:
        return "no source passage recorded"
    passage = passages[0]
    parts = [passage.get("work"), passage.get("section"), passage.get("location")]
    cited = ", ".join(str(part) for part in parts if part)
    return f"{cited} [{passage.get('edition_id', 'edition unrecorded')}]"


def _clauses(conclusion: dict[str, Any]) -> list[str]:
    for key in ("themes", "quoted_base_outcomes", "content", "observations"):
        value = conclusion.get(key)
        if isinstance(value, list) and value:
            return [str(item) for item in value]
    for key in ("theme", "primary", "recipient", "commentary_outcome"):
        value = conclusion.get(key)
        if isinstance(value, str):
            return [value]
    alternatives = conclusion.get("commentary_alternatives")
    if isinstance(alternatives, list) and alternatives:
        return [str(item) for item in alternatives]
    return []


def _concerns(rule: dict[str, Any]) -> str:
    scope = rule.get("scope") or {}
    conclusion = rule.get("conclusion") or {}
    for value in (
        scope.get("target_context"),
        conclusion.get("target"),
        conclusion.get("recipient"),
    ):
        if isinstance(value, str):
            return value
    targets = conclusion.get("targets") or conclusion.get("recipients")
    if isinstance(targets, list) and targets:
        return ", ".join(str(item) for item in targets)
    if isinstance(targets, str):
        return targets
    return "the king and the land"


def _apodosis_record(manifest_name: str, rule: dict[str, Any]) -> dict[str, Any]:
    conclusion = rule.get("conclusion") or {}
    scope = rule.get("scope") or {}
    return {
        "rule_id": rule["rule_id"],
        "pack": _manifest(manifest_name)["school_id"],
        "conclusion_type": conclusion.get("type"),
        "apodosis_clauses": _clauses(conclusion),
        "recensional_variant": conclusion.get("variant"),
        "polarity": conclusion.get("polarity"),
        "concerns": _concerns(rule),
        "genre_label": GENRE_LABEL,
        "attribution": _attribution(rule),
        "evidence_grade": rule.get("evidence_grade"),
        "publication_limit": rule.get("publication_limit"),
        "conflicts_with": rule.get("conflicts_with") or [],
        "birth_input_eligible": bool(scope.get("birth_input_eligible")),
        "match_semantics": (
            "the sky on this date satisfied this ancient protasis; the pack "
            "marks the rule ineligible for birth input, so this is never a "
            "statement about the native"
        ),
        "customer_prediction": bool(conclusion.get("customer_prediction")),
    }


def _judgment_clauses() -> dict[str, Any]:
    records = []
    for manifest_name, rule in _judgment_rules():
        conclusion = rule.get("conclusion") or {}
        scope = rule.get("scope") or {}
        records.append({
            "rule_id": rule["rule_id"],
            "text": scope.get("text"),
            "clauses": _clauses(conclusion),
            "attribution": _attribution(rule),
            "algorithmic_trigger": conclusion.get("algorithmic_trigger"),
            "executable_from_birth_input": bool(
                scope.get("executable_from_birth_input")
            ),
            "evidence_grade": rule.get("evidence_grade"),
            "customer_prediction": bool(conclusion.get("customer_prediction")),
            "pack": _manifest(manifest_name)["school_id"],
        })
    return {
        "encoded_clause_count": len(records),
        "executable_from_birth_input": sum(
            1 for record in records if record["executable_from_birth_input"]
        ),
        "with_resolved_trigger": sum(
            1 for record in records if record["algorithmic_trigger"]
        ),
        "clauses": records,
    }


# --------------------------------------------------------------------------
# section
# --------------------------------------------------------------------------


def _sign_of(longitude: float) -> tuple[str, float]:
    index = int((longitude % 360) // 30)
    return SIGNS[index], (longitude % 360) - index * 30


def _phase_label(elongation: float) -> str:
    angle = elongation % 360.0
    if angle < 12.0 or angle >= 348.0:
        return "conjunction, moon invisible"
    if angle < 90.0:
        return "waxing crescent"
    if angle < 100.0:
        return "first quarter"
    if angle < 170.0:
        return "waxing gibbous"
    if angle < 190.0:
        return "opposition, full moon"
    if angle < 260.0:
        return "waning gibbous"
    if angle < 280.0:
        return "last quarter"
    return "waning crescent"


def _disclose(section: TraditionSection) -> None:
    section.disclose(
        DisclosureKind.REFUSAL,
        "Genre boundary",
        "The Mesopotamian corpus contains no personality genre. Enuma Anu Enlil "
        "and the Neo-Assyrian reports judge kings, lands, armies and harvests; "
        "no protasis in them takes a birth as input and no apodosis in them "
        "describes a person's character, temperament, or disposition. This "
        "section is therefore not a personality reading and cannot be turned "
        "into one - any Babylonian character delineation is an invention, "
        "however ancient the vocabulary it borrows.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Birth-input eligibility",
        f"All {len(_omen_rules())} encoded omen protases are marked "
        "`birth_input_eligible: false` by their own packs, and the twelve the "
        "packs additionally mark non-executable are excluded from matching "
        "outright. A match therefore means only that the sky on this date "
        "satisfied an ancient protasis whose apodosis was addressed to a land "
        "or a king. It never means the omen applies to the native.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Prediction",
        "Apodoses are quoted as historical text about ancient states. Nothing "
        "here is a forecast of political, ecological, financial, medical, or "
        "personal events, and the packs' own publication limits (suppressing "
        "violence, death, disaster, and ritual as present-day prediction) are "
        "carried through with each quotation.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Natal synthesis",
        "The 21 explicit judgment clauses encoded from Rochberg's Texts 1-28 "
        "carry no resolved trigger: every one is marked "
        "`executable_from_birth_input: false` or `algorithmic_trigger: null`. "
        "They are listed as artifacts of specific tablets and are never applied "
        "to this or any other chart, and no judgment is built by analogy from "
        "the state omens.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Witness blending",
        "The EAE 20 pack preserves recension conflicts between IM 124485, VAT "
        "9419, and manuscripts D, S, M, Y. Conflicting witnesses are reported "
        "separately with their `conflicts_with` links intact; they are never "
        "averaged into a single reading.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Commentary layer",
        "Ancient commentary restricts scope, equates words, and preserves "
        "alternatives. Commentary rules are keyed to a base omen rather than to "
        "a sky, so they are never matched independently and never overwrite the "
        "base omen text.",
    )
    concordance = _manifest(CONCORDANCE)["summary"]
    section.disclose(
        DisclosureKind.REFUSAL,
        "Unresolved tablets",
        f"{concordance['unresolved_cdli_matches']} of "
        f"{concordance['numbered_tablets']} numbered tablets are not exactly "
        "matched to a current CDLI record. No claim in this section rests on "
        "them, and their unresolved status is stated rather than smoothed over.",
    )
    section.disclose(
        DisclosureKind.SOURCE,
        "Rule provenance",
        f"{len(_omen_rules())} encoded omen protases are loaded from four "
        "hash-pinned witness packs - the EAE 20 witness comparison (Al-Rawi and "
        "George 2006 with Heessel 2021), the EAE 16-21 ancient commentaries "
        "(CCP/ORACC), and SAA 8 reports 316 and 535 (Hunger 1992 via ORACC) - "
        f"plus {len(_judgment_rules())} judgment clauses from Rochberg's "
        "Babylonian Horoscopes. Apodoses are quoted as the packs encode them: "
        "normalized clause identifiers with their edition citation, not prose "
        "lifted from a modern copyrighted translation, so a specialist can "
        "check each identifier against the cited location.",
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Zodiac",
        "Positions are the shipping engine's tropical Swiss Ephemeris "
        "longitudes. Babylonian sidereal schemes differ: System A and System B "
        "norms are anchored to fixed stars, and at a modern date the offset is "
        "close to a full sign, so a sign named here will frequently not be the "
        "sign a Babylonian scribe would have written.",
        ("Babylonian System A norm", "Babylonian System B norm", "a sidereal ayanamsa"),
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Babylonian calendar projection",
        "The lunisolar calendar is run roughly two thousand years past its "
        "attested use, so the month and day below are a modern projection and "
        "not a historical date. Nisannu is taken as the first month whose day 1 "
        "begins on or after the vernal equinox; day 1 begins at the first "
        "sunset after conjunction at which the Moon sets at least "
        f"{CRESCENT_LAG_MINUTES:.0f} minutes after the Sun; days run sunset to "
        "sunset at the place of birth; a thirteenth month is labeled "
        "intercalary.",
        (
            "the Seleucid 19-year intercalation cycle projected forward",
            "Schoch or Yallop arcus-visionis visibility criteria",
            "sunset reckoned at Babylon rather than at the birthplace",
            "the schematic 30-day month of the astrolabe texts",
        ),
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Omen matching orb",
        "The matching orb is zero on every axis and is stated rather than "
        "defaulted. An eclipse protasis is satisfied only if an umbral lunar "
        "eclipse is in progress at the birth instant - proximity in days never "
        "counts. Month and day selectors must match the projected date exactly, "
        "with no plus-or-minus-one-day widening even though the projected day "
        "boundary is itself uncertain. Watch selectors require a night birth. A "
        "protasis naming any condition the reconstruction cannot supply is "
        "counted unevaluable and never partially matched.",
        (
            "plus or minus one day on the projected calendar day",
            "treating any eclipse in the same lunar month as satisfying the "
            "eclipse condition",
            "scoring partial protasis satisfaction",
        ),
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Night watches",
        "The three watches are computed as equal thirds of the interval from "
        "sunset to sunrise at the place of birth. The corpus itself uses watch "
        "names without defining their boundaries arithmetically.",
        ("seasonal-hour watches", "the schematic watch scheme of MUL.APIN"),
    )
    section.disclose(
        DisclosureKind.SOURCE,
        "Position reporting",
        "Bodies are listed in the order Rochberg's edition tabulates a "
        "horoscope - Moon, Sun, Jupiter, Venus, Mercury, Saturn, Mars - as sign "
        "and degree only. The corpus records no houses, no aspects, no "
        "rulerships, and no sect, and none is supplied here. The packs encode "
        "no Babylonian sign-name table either, so signs carry their standard "
        "modern names.",
    )


def build(birth: BirthInput, bases: TimeBases, chart: Any) -> TraditionSection:
    """Positions, calendar, eclipse condition, matched omens - and a full stop."""
    section = TraditionSection(
        tradition_id="mesopotamian_babylonian",
        display_name="Mesopotamian (Babylonian omen corpus)",
        evidence_grade=EvidenceGrade.CONFIGURED,
        basis=(
            "Encoded Enuma Anu Enlil and SAA 8 omen protases matched against a "
            "reconstructed sky. The rules are hash-pinned research packs; the "
            "calendar projection and the matching orb are product choices and "
            "are disclosed as such."
        ),
    )
    _disclose(section)

    jd = getattr(chart, "jd", None) or bases.julian_day_ut
    geo = (birth.longitude, birth.latitude, 0.0)

    planet_map = {p.name.value: p for p in chart.planets}
    positions = []
    for body in BABYLONIAN_BODY_ORDER:
        planet = planet_map.get(body)
        if planet is None:
            continue
        sign, degree = _sign_of(planet.longitude)
        positions.append({
            "body": body,
            "sign": sign,
            "degree_in_sign": round(degree, 4),
            "zodiac": "tropical",
        })

    try:
        calendar = _project_calendar(jd, geo)
    except Exception as exc:  # noqa: BLE001 - a failed projection is a finding
        calendar = {"status": "not_projectable", "reason": f"{type(exc).__name__}"}
    watch = _night_watch(jd, geo)
    eclipse = _eclipse_condition(jd, geo)
    in_progress = bool(eclipse["lunar_eclipse_in_progress"])

    elongation = _elongation(jd) % 360.0
    conjunction = _previous_conjunction(jd)

    sky = {
        "phenomenon": "lunar_eclipse" if in_progress else "none",
        "babylonian_month": calendar.get("month"),
        "babylonian_day": calendar.get("day"),
        "watch": watch.get("watch"),
        "sets_while_eclipsed": _sets_while_eclipsed(jd, geo, in_progress),
    }
    matching = evaluate_rules(sky)
    matching["configured_orb"] = (
        "zero: umbral eclipse in progress at the birth instant; exact month and "
        "day equality on the projected calendar; watch only for a night birth"
    )
    matching["sky_facts_supplied"] = sky
    if not in_progress:
        matching["no_match_reason"] = (
            "no umbral lunar eclipse was in progress at the birth instant, and "
            "every encoded protasis in these packs presupposes one"
        )

    catalog = _manifest(CATALOG)["summary"]
    judgments = _judgment_clauses()

    section.facts = {
        "corpus_shape": {
            "encoded_omen_protases": matching["rules_evaluated"],
            "omen_packs": len(OMEN_MANIFESTS),
            "rochberg_numbered_texts": catalog["numbered_texts"],
            "horoscope_record_entries": catalog["horoscope_record_entries"],
            "explicit_judgment_clauses": judgments["encoded_clause_count"],
            "judgment_clauses_executable_from_a_birth": judgments[
                "executable_from_birth_input"
            ],
            "genre": "state divination; no natal personality genre survives",
        },
        "positions_in_edition_order": positions,
        "not_recorded_by_this_corpus": [
            "houses", "aspects", "rulerships", "sect", "personality delineation",
        ],
        "babylonian_date_projection": calendar,
        "lunar_condition": {
            "elongation_from_sun_degrees": round(elongation, 4),
            "phase": _phase_label(elongation),
            "synodic_age_days": round(jd - conjunction, 4),
            "previous_conjunction_ut": _iso(conjunction),
        },
        "night_watch": watch,
        "eclipse_condition": eclipse,
        "omen_matching": matching,
        "horoscope_judgment_clauses": judgments,
    }
    section.reading = _reading(section.facts)
    return section


def _reading(facts: dict[str, Any]) -> list[str]:
    """Judgment in the tradition's own order, stopping where the corpus stops."""
    corpus = facts["corpus_shape"]
    calendar = facts["babylonian_date_projection"]
    matching = facts["omen_matching"]
    eclipse = facts["eclipse_condition"]
    lunar = facts["lunar_condition"]

    lines = [
        "What this corpus is. Enuma Anu Enlil and the Neo-Assyrian celestial "
        f"reports are state divination: {corpus['encoded_omen_protases']} encoded "
        "protasis/apodosis pairs judging kings, lands, armies and harvests. The "
        "natal branch is thin, late and laconic - Rochberg's "
        f"{corpus['rochberg_numbered_texts']} numbered texts yield "
        f"{corpus['horoscope_record_entries']} horoscope records that are mostly "
        f"positional, and only {corpus['explicit_judgment_clauses']} explicit "
        "judgment clauses in all. The oldest documented tradition in this panel "
        "is also the one with the least to say about an individual life.",
        "Positions, in the corpus's own idiom. A Late Babylonian horoscope "
        "records body, zodiacal sign and degree, in the order the edition "
        "tabulates them, and nothing else - no houses, no aspects, no "
        "rulerships, no sect: "
        + "; ".join(
            f"{item['body']} in {item['sign']} {item['degree_in_sign']:.2f}°"
            for item in facts["positions_in_edition_order"]
        )
        + " (tropical longitudes; a Babylonian sidereal norm would shift these "
        "by close to a sign).",
    ]

    if calendar.get("status") == "not_projectable":
        lines.append(
            "Calendar. The lunisolar month could not be projected for this "
            "location and date, so no calendrical omen selector is evaluated."
        )
    else:
        lines.append(
            "Calendar and lunar condition. Projected Babylonian date: "
            f"{calendar['month_label']} {calendar['day']} - month "
            f"{calendar['month_index']} of the year that began "
            f"{calendar['year_began_ut']}, a modern projection and not a "
            "historical date. The Moon stood "
            f"{lunar['elongation_from_sun_degrees']:.1f}° east of the Sun and "
            f"{lunar['synodic_age_days']:.1f} days past conjunction - "
            f"{lunar['phase']}."
        )

    previous = eclipse.get("previous_lunar_eclipse")
    following = eclipse.get("next_lunar_eclipse")
    if eclipse["lunar_eclipse_in_progress"]:
        lines.append(
            "Eclipse condition. An umbral lunar eclipse was in progress at the "
            f"birth instant, magnitude {eclipse['umbral_magnitude_at_birth']}. "
            "This is the condition on which the entire encoded corpus turns."
        )
    else:
        nearest = min(
            [item for item in (previous, following) if item],
            key=lambda item: abs(item["days_from_birth"]),
            default=None,
        )
        detail = (
            f" The nearest was {abs(nearest['days_from_birth']):.1f} days away, "
            f"on {nearest['maximum_ut']} ({nearest['type']})."
            if nearest
            else ""
        )
        lines.append(
            "Eclipse condition. No umbral lunar eclipse was in progress at the "
            "birth instant." + detail
        )

    lines.append(_matching_paragraph(matching))
    lines.extend(_matched_omen_lines(matching))
    lines.append(_judgment_paragraph(facts["horoscope_judgment_clauses"]))
    lines.append(
        "Where this stops. The corpus records positions, a date, a lunar and "
        "eclipse condition, and the omens a sky satisfies. It contains no "
        "protasis that takes a birth as input and no apodosis about anyone's "
        "character, temperament, or disposition, so this section reports those "
        "four things and stops. Nothing above is a prediction, and nothing "
        "above can be turned into a personality reading without inventing a "
        "genre the sources do not contain."
    )
    return lines


def _matching_paragraph(matching: dict[str, Any]) -> str:
    if matching["matched_count"]:
        return (
            f"Omen protases matched: {matching['matched_count']} of "
            f"{matching['rules_evaluated']} evaluated. Each is quoted below with "
            "its edition citation and the ancient target it concerns. "
            f"{matching['unevaluable_count']} further protases were unevaluable "
            "because they name conditions no modern reconstruction can supply."
        )
    reasons = ", ".join(
        f"{reason} ({count})"
        for reason, count in sorted(
            matching["unevaluable_reasons"].items(), key=lambda kv: -kv[1]
        )[:3]
    )
    text = (
        f"Omen protases matched: none. All {matching['rules_evaluated']} encoded "
        "protases were evaluated at the disclosed zero orb; "
        f"{matching['non_executable_by_pack']} are marked non-executable by "
        f"their own packs, and {matching['unevaluable_count']} cannot be "
        f"evaluated from a modern ephemeris at all ({reasons})."
    )
    if matching.get("no_match_reason"):
        text += f" For the remainder, {matching['no_match_reason']}."
    overlap = matching.get("calendar_selector_overlap") or []
    if overlap:
        text += (
            f" {len(overlap)} protases name the projected month or day - "
            + ", ".join(item["rule_id"] for item in overlap)
            + " - but they are not matches: the eclipse each of them "
            "presupposes did not occur."
        )
    return text


def _matched_omen_lines(matching: dict[str, Any]) -> list[str]:
    lines = []
    for record in matching["matched"]:
        clauses = ", ".join(f"“{clause}”" for clause in
                            record["apodosis_clauses"]) or "“no clause encoded”"
        line = (
            f"Matched: {record['rule_id']} ({record['conclusion_type']}). "
            f"Apodosis: {clauses}. Concerning {record['concerns']} - a "
            f"{record['genre_label']}. Source: {record['attribution']}. The "
            "pack marks this rule ineligible for birth input: the sky "
            "satisfied the protasis, the omen still addresses a land or a king."
        )
        if record.get("recensional_variant"):
            line += (
                " A recensional variant reads "
                f"“{record['recensional_variant']}”; the witnesses are "
                "reported separately and are not merged."
            )
        lines.append(line)
    return lines


def _judgment_paragraph(judgments: dict[str, Any]) -> str:
    example = next(
        (
            clause for clause in judgments["clauses"]
            if clause["clauses"] and clause["text"]
        ),
        None,
    )
    text = (
        f"The natal branch, quoted as artifact. {judgments['encoded_clause_count']} "
        "explicit judgment clauses survive across Texts 1-28, and "
        f"{judgments['executable_from_birth_input']} of them can be executed from "
        "a birth: every one is recorded with an unresolved trigger, so none "
        "reduces to a rule another chart could satisfy."
    )
    if example:
        quoted = ", ".join(f"“{clause}”" for clause in example["clauses"])
        text += (
            f" {example['text']}, for instance, attaches {quoted} to its own "
            f"ancient native ({example['attribution']}) - a record of what one "
            "tablet says, not a rule that travels."
        )
    return text
