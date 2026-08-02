"""Pharaonic Egyptian civil calendar section.

The validated `egyptian_civil_calendar_365_v1` pack encodes the 365-day civil
year exactly - three seasons of four thirty-day months plus five heriu-renpet
days - and encodes, just as deliberately, a null chronology default. There is no
approved anchor tying any civil date to a position in that year, so this section
reports the structure and refuses to place the birth inside it. That refusal is
the same shape as the Nahua one: an unresolved correlation is a finding, and
inventing an epoch would make every field downstream of it fiction.

The Sallier IV hemerology is a second, independent refusal. Its access manifest
records `rule_extraction_ready: false`, and Budge states that the portion
probably carrying the five epagomenal days is lost - lost, not proven absent, so
silence in the surviving witness may not be converted into a historical rule.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from .timebase import TimeBases
from .types import BirthInput, DisclosureKind, EvidenceGrade, TraditionSection

RESEARCH_ROOT = (
    Path(__file__).resolve().parents[3] / "docs" / "research" / "multitradition"
)
CIVIL_SPEC = RESEARCH_ROOT / "egyptian" / "civil_calendar_spec.json"
SALLIER_MANIFEST = RESEARCH_ROOT / "egyptian" / "budge_sallier_iv_access_manifest.json"

ADDITIONAL_ID = "heriu_renpet"
# Egyptological citation notation: season month numbered in Roman numerals
# within its season, as Porceddu et al. write "I Akhet 1". A configured display
# choice, disclosed below.
ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV"}


@lru_cache(maxsize=2)
def _spec(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _model() -> dict[str, Any]:
    return _spec(CIVIL_SPEC)["calendar_model"]


def _season_ids() -> list[str]:
    return [season["id"] for season in _model()["seasons"]]


def _season_labels() -> dict[str, str]:
    return {season["id"]: season["source_label"] for season in _model()["seasons"]}


def date_to_position(
    season_id: str, month_in_season: int | None, day: int
) -> dict[str, Any]:
    """Zero-based position in the 365-day year, or the pack's own error id.

    Cycle-internal conversion only. The pack states plainly that this direction
    "needs no civil chronology" - which is exactly why it is the only direction
    this section can run for real.
    """
    model = _model()
    if season_id == ADDITIONAL_ID:
        if not 1 <= day <= model["additional_period"]["days"]:
            return {"error": "invalid_additional_day"}
        return _position_payload(model["ordinary_days"] + day - 1)
    if season_id not in _season_ids():
        return {"error": "unknown_season"}
    if month_in_season is None or not 1 <= month_in_season <= 4:
        return {"error": "invalid_month_in_season"}
    if not 1 <= day <= model["ordinary_month_length_days"]:
        return {"error": "invalid_ordinary_day"}
    index = _season_ids().index(season_id)
    position = (
        index * 4 * model["ordinary_month_length_days"]
        + (month_in_season - 1) * model["ordinary_month_length_days"]
        + (day - 1)
    )
    return _position_payload(position)


def position_to_date(year_position: int) -> dict[str, Any]:
    """Normalize any integer offset under the pack's Euclidean year advance."""
    model = _model()
    year_delta, position = divmod(year_position, model["year_length_days"])
    payload = _position_payload(position)
    payload["year_delta"] = year_delta
    return payload


def _position_payload(position: int) -> dict[str, Any]:
    model = _model()
    length = model["ordinary_month_length_days"]
    if position >= model["ordinary_days"]:
        additional_day = position - model["ordinary_days"] + 1
        return {
            "season_id": ADDITIONAL_ID,
            "month_in_season": None,
            "day": additional_day,
            "year_position": position,
            "year_delta": 0,
            "is_additional_day": True,
            "additional_day": additional_day,
        }
    season_index, within_season = divmod(position, 4 * length)
    month_in_season, day_index = divmod(within_season, length)
    return {
        "season_id": _season_ids()[season_index],
        "month_in_season": month_in_season + 1,
        "day": day_index + 1,
        "year_position": position,
        "year_delta": 0,
        "is_additional_day": False,
        "additional_day": None,
    }


def format_date(payload: dict[str, Any]) -> str:
    """Egyptological notation for a position payload."""
    if payload.get("error"):
        return payload["error"]
    if payload["season_id"] == ADDITIONAL_ID:
        return (
            _model()["additional_period"]["source_label"]
            + " day "
            + str(payload["day"])
        )
    label = _season_labels()[payload["season_id"]]
    return f"{ROMAN[payload['month_in_season']]} {label} {payload['day']}"


def place_civil_date(
    civil_days_from_anchor: int | None,
    profile: dict[str, Any] | None,
) -> dict[str, Any]:
    """Fail-closed civil-date conversion. Returns the pack's error ids, not guesses.

    `civil_days_from_anchor` is the signed civil-day difference between the date
    being converted and the profile's anchor date. Without a complete named
    profile there is nothing to subtract from, and the pack requires that this
    fail rather than default.
    """
    contract = _spec(CIVIL_SPEC)["chronology_contract"]
    if profile is None:
        return {"error": "missing_profile"}
    missing = [field for field in contract["required_fields"] if field not in profile]
    if missing:
        return {"error": "missing_profile", "missing_fields": missing}
    if profile["tradition_id"] != contract["required_tradition_id"]:
        return {"error": "wrong_tradition"}
    if profile["model_id"] != contract["required_model_id"]:
        return {"error": "wrong_calendar_model"}
    if civil_days_from_anchor is None:
        return {"error": "unresolved_civil_date"}
    anchor = profile["anchor_egyptian_date"]
    anchor_position = date_to_position(
        anchor["season_id"], anchor.get("month_in_season"), anchor["day"]
    )
    if anchor_position.get("error"):
        return {"error": "invalid_anchor_egyptian_date"}
    return position_to_date(anchor_position["year_position"] + civil_days_from_anchor)


def build(birth: BirthInput, bases: TimeBases) -> TraditionSection:
    spec = _spec(CIVIL_SPEC)
    model = spec["calendar_model"]
    contract = spec["chronology_contract"]

    section = TraditionSection(
        tradition_id="pharaonic_egyptian",
        display_name="Pharaonic Egyptian civil calendar",
        evidence_grade=EvidenceGrade.VALIDATED_PACK,
        basis=(
            "The 365-day civil-year structure and its position arithmetic from the "
            "validated Egyptian civil calendar pack. The pack registers no "
            "chronology profile, so this birth is not placed in the calendar."
        ),
    )
    section.disclose(
        DisclosureKind.SOURCE,
        "Pack provenance",
        "Year length, the three seasons of four thirty-day months, the five "
        "heriu-renpet days, the non-intercalating model and the position/date "
        "bijection come from egyptian_civil_calendar_365_v1, anchored to Porceddu "
        "et al. 2008 and the UCL civil-calendar table.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Placing this birth in the Egyptian year",
        "Refused. The pack's chronology contract sets default_profile to null: it "
        "requires a named profile carrying regime, authority, anchor civil date, "
        "anchor Egyptian date, calendar policy, locality, day boundary and "
        "uncertainty in days, and there is no approved profile for any regime. "
        "The 365-day year "
        "drifts a full day against the seasons every four years, so an unanchored "
        "conversion is not approximately right - it is wrong by an unbounded "
        "amount. The birth's civil day (JDN "
        f"{bases.julian_day_number}) is therefore reported as the withheld input, "
        "not converted.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Back-projected calendars",
        "The later Alexandrian/Coptic leap rule, a modern fixed month-and-day "
        "table, and any unnamed reign or locality are all rejected by the pack as "
        "chronology profiles. A profile whose model_id is not pharaonic_civil_365 "
        "fails closed rather than being coerced.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Hemerology and any birth reading",
        "Refused. The pack's output contract permits calendar position fields only "
        "and names prognosis, personality, fate, health, death, morality, "
        "compatibility and recommendation as forbidden fields. A calendar position "
        "is not a witness-specific judgment, and no lucky/unlucky verdict is "
        "produced here even where a date is otherwise well formed.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Sallier IV and the epagomenal days",
        "Refused, and for a reason worth stating precisely. The Sallier IV access "
        "manifest records rule_extraction_ready: false - the file is acquired but "
        "not fully read, with no complete transcription, no translation and no "
        "collation against Bakir 1966 or Leitz 1994. Budge further states that the "
        "portion probably containing the Five Epagomenal Days is LOST. Loss is "
        "unknown evidence, not proof that the original calendar assigned those "
        "days no prognosis, so this section neither supplies a prognosis nor "
        "asserts that none existed.",
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Date notation",
        "Dates are written in the Egyptological convention used by the pack's own "
        "source - Roman month number within the season, then season, then day, as "
        "in 'I Akhet 1'. The season names are the pack's source labels.",
        ("Greek month names (Thoth, Phaophi, ...)", "Plain 1-12 month numbering"),
    )

    landmarks = {
        format_date(position_to_date(position)): position
        for position in (0, 29, 30, 120, 240, 359, 360, 364)
    }
    round_trip_ok = _round_trip_holds(model["year_length_days"])

    section.facts = {
        "calendar_model": {
            "model_id": model["model_id"],
            "year_length_days": model["year_length_days"],
            "ordinary_months": model["ordinary_months"],
            "ordinary_month_length_days": model["ordinary_month_length_days"],
            "ordinary_days": model["ordinary_days"],
            "additional_days": model["additional_days"],
            "intercalation": model["intercalation"],
            "seasons": [
                f"{season['source_label']} ({season['months']} months)"
                for season in model["seasons"]
            ],
            "additional_period": model["additional_period"]["source_label"],
        },
        "birth_placement": {
            "placed": False,
            "chronology_profile_used": None,
            "withheld_input_jdn": bases.julian_day_number,
            "withheld_input_civil_date": birth.civil_date.isoformat(),
            "reason": "no_approved_chronology_profile",
        },
        "chronology_contract": {
            "default_profile": contract["default_profile"],
            "required_fields": contract["required_fields"],
            "unsupported_profiles": contract["unsupported_profiles"],
        },
        "cycle_internal_structure": {
            "landmark_positions": landmarks,
            "position_date_round_trip_over_365_positions": round_trip_ok,
        },
        "fail_closed_selfcheck": _fail_closed_selfcheck(),
        "hemerology_boundary": {
            key: spec["hemerology_boundary"][key]
            for key in (
                "heriu_renpet_prognosis",
                "missing_witness_text_creates_negative_rule",
                "calendar_position_creates_birth_reading",
            )
        },
        "sallier_iv_witness": _sallier_facts(),
    }
    section.reading = [
        "What this tradition's surviving apparatus can and cannot do with a birth "
        "date, stated in its own terms:",
        "The civil year is a fixed arithmetic object - "
        f"{model['ordinary_months']} months of "
        f"{model['ordinary_month_length_days']} days across Akhet, Peret and "
        f"Shemu, then {model['additional_days']} heriu-renpet days upon the year, "
        f"{model['year_length_days']} days total, with no intercalation. Positions "
        "inside it convert both ways exactly, and that arithmetic is verified over "
        "all 365 positions above.",
        "What is missing is the join between that object and a date on a modern "
        "calendar. Because the year never intercalates, it slides against the "
        "seasons by roughly one day in four years and a full year in about 1460 - "
        "so the join is not a detail, it is the whole conversion. The pack "
        "registers no approved anchor, and refuses to invent one.",
        "The hemerological layer - the calendars of lucky and unlucky days that "
        "would be the closest Egyptian analogue to a birth judgment - is a "
        "separate, source-limited problem. Sallier IV survives in two portions "
        "with lacunae, has no complete critical transcription in hand, and its "
        "likely epagomenal section is lost. This section quotes no prognosis and "
        "invents none.",
    ]
    return section


def _round_trip_holds(year_length: int) -> bool:
    """Every position must survive position -> date -> position unchanged."""
    for position in range(year_length):
        payload = position_to_date(position)
        back = date_to_position(
            payload["season_id"], payload["month_in_season"], payload["day"]
        )
        if back.get("year_position") != position:
            return False
    return True


def _fail_closed_selfcheck() -> dict[str, Any]:
    """Reproduce the pack's own chronology vectors, including the negative ones."""
    synthetic_profile = {
        "profile_id": "test_fixture_not_historical",
        "tradition_id": "pharaonic_egyptian",
        "model_id": "pharaonic_civil_365",
        "anchor_civil_date": "2000-01-01",
        "calendar_policy": "proleptic_gregorian_test_fixture",
        "anchor_egyptian_date": {
            "season_id": "akhet",
            "month_in_season": 1,
            "day": 1,
        },
        "historical_regime": "synthetic_test_only",
        "authority": "arithmetic_validation_only",
        "uncertainty_days": 0,
        "locality": "test_fixture",
        "day_start": "civil_midnight_test_fixture",
    }
    coptic_profile = dict(synthetic_profile, model_id="alexandrian_coptic_leap")
    # 2000-01-01 -> 2000-12-30 is 364 civil days, the pack's synthetic vector.
    synthetic = place_civil_date(364, synthetic_profile)
    return {
        "note": (
            "Contract reproduction from the pack's own vectors. None of these "
            "concerns this birth."
        ),
        "no_profile_supplied": place_civil_date(0, None)["error"],
        "coptic_model_supplied": place_civil_date(0, coptic_profile)["error"],
        "synthetic_fixture_profile": {
            "profile_id": synthetic_profile["profile_id"],
            "historical_regime": synthetic_profile["historical_regime"],
            "result": format_date(synthetic),
            "year_position": synthetic["year_position"],
            "not_this_birth": True,
        },
    }


def _sallier_facts() -> dict[str, Any]:
    if not SALLIER_MANIFEST.is_file():
        return {"manifest_present": False}
    manifest = _spec(SALLIER_MANIFEST)
    preservation = manifest["witness_description"]["preservation"]
    boundaries = manifest["interpretive_boundaries"]
    return {
        "witness_id": manifest["witness_id"],
        "traditional_name": manifest["witness_description"]["traditional_name"],
        "british_museum_number": manifest["witness_description"][
            "british_museum_number"
        ],
        "surviving_range": preservation["surviving_range_from_porceddu_2008"],
        "lost_ranges": preservation["lost_ranges_from_budge_1923"],
        "epagomenal_status": preservation["epagomenal_absence_interpretation"],
        "historical_absence_proven": preservation["historical_absence_proven"],
        "rule_extraction_ready": boundaries["rule_extraction_ready"],
        "complete_translation_present": boundaries["complete_translation_present"],
        "modern_critical_edition_collated": boundaries[
            "modern_critical_edition_collated"
        ],
    }
