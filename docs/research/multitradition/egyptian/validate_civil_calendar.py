"""Validate the research-only pharaonic Egyptian civil-calendar artifact."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
MULTITRADITION_ROOT = ROOT.parent
SPEC_PATH = ROOT / "civil_calendar_spec.json"
MANIFEST_PATH = ROOT / "civil_calendar_rule_manifest.json"
VECTORS_PATH = ROOT / "civil_calendar_validation_vectors.json"
REGISTRY_PATH = MULTITRADITION_ROOT / "source_registry.json"

SEASONS = ("akhet", "peret", "shemu")
YEAR_LENGTH = 365
ORDINARY_DAYS = 360


class CalendarInputError(ValueError):
    """A stable fail-closed input error."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object and reject non-object roots."""
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise AssertionError(f"Expected JSON object: {path}")
    return value


def _require_int(value: Any, error_code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise CalendarInputError(error_code)
    return value


def position_to_date(year_position: int) -> dict[str, Any]:
    """Normalize an integer position and retain its signed year displacement."""
    position = _require_int(year_position, "year_position_not_integer")
    year_delta, normalized = divmod(position, YEAR_LENGTH)
    if normalized < ORDINARY_DAYS:
        season_index, within_season = divmod(normalized, 120)
        month_index, day_index = divmod(within_season, 30)
        return {
            "season_id": SEASONS[season_index],
            "month_in_season": month_index + 1,
            "day": day_index + 1,
            "year_position": normalized,
            "year_delta": year_delta,
            "is_additional_day": False,
            "additional_day": None,
        }
    additional_day = normalized - ORDINARY_DAYS + 1
    return {
        "season_id": "heriu_renpet",
        "month_in_season": None,
        "day": additional_day,
        "year_position": normalized,
        "year_delta": year_delta,
        "is_additional_day": True,
        "additional_day": additional_day,
    }


def date_to_position(egyptian_date: Any) -> dict[str, Any]:
    """Validate an internal Egyptian date and convert it to year position."""
    if not isinstance(egyptian_date, dict):
        raise CalendarInputError("invalid_egyptian_date")
    season_id = egyptian_date.get("season_id")
    month = egyptian_date.get("month_in_season")
    day = _require_int(egyptian_date.get("day"), "invalid_day")
    if season_id == "heriu_renpet":
        if month is not None:
            raise CalendarInputError("additional_period_has_no_month")
        if not 1 <= day <= 5:
            raise CalendarInputError("invalid_additional_day")
        return position_to_date(ORDINARY_DAYS + day - 1)
    if season_id not in SEASONS:
        raise CalendarInputError("invalid_season")
    month_value = _require_int(month, "invalid_month_in_season")
    if not 1 <= month_value <= 4:
        raise CalendarInputError("invalid_month_in_season")
    if not 1 <= day <= 30:
        raise CalendarInputError("invalid_ordinary_day")
    position = SEASONS.index(season_id) * 120 + (month_value - 1) * 30 + day - 1
    return position_to_date(position)


def _validate_profile(spec: dict[str, Any], profile: Any) -> tuple[date, int]:
    if profile is None:
        raise CalendarInputError("missing_profile")
    if not isinstance(profile, dict):
        raise CalendarInputError("invalid_profile")
    contract = spec["chronology_contract"]
    required = set(contract["required_fields"])
    if required - set(profile):
        raise CalendarInputError("incomplete_profile")
    if profile["tradition_id"] != contract["required_tradition_id"]:
        raise CalendarInputError("wrong_profile_tradition")
    if profile["model_id"] != contract["required_model_id"]:
        raise CalendarInputError("wrong_calendar_model")
    string_fields = required - {"anchor_egyptian_date", "uncertainty_days"}
    if any(
        not isinstance(profile[field], str) or not profile[field].strip()
        for field in string_fields
    ):
        raise CalendarInputError("invalid_profile")
    uncertainty = profile["uncertainty_days"]
    if (
        isinstance(uncertainty, bool)
        or not isinstance(uncertainty, int)
        or uncertainty < 0
    ):
        raise CalendarInputError("invalid_uncertainty")
    try:
        anchor_civil_date = date.fromisoformat(profile["anchor_civil_date"])
    except ValueError as exc:
        raise CalendarInputError("invalid_anchor_civil_date") from exc
    anchor_position = date_to_position(profile["anchor_egyptian_date"])[
        "year_position"
    ]
    return anchor_civil_date, anchor_position


def state_from_civil_date(
    spec: dict[str, Any], civil_date: Any, profile: Any
) -> dict[str, Any]:
    """Convert a resolved civil date under a complete named research profile."""
    anchor_date, anchor_position = _validate_profile(spec, profile)
    if not isinstance(civil_date, str):
        raise CalendarInputError("invalid_civil_date")
    try:
        target_date = date.fromisoformat(civil_date)
    except ValueError as exc:
        raise CalendarInputError("invalid_civil_date") from exc
    offset = (target_date - anchor_date).days
    return position_to_date(anchor_position + offset)


def _run_vector(spec: dict[str, Any], vector: dict[str, Any]) -> dict[str, Any]:
    inputs = vector["inputs"]
    operation = inputs.get("operation")
    try:
        if operation == "date_to_position":
            return date_to_position(inputs["date"])
        if operation == "position_to_date":
            return position_to_date(inputs["year_position"])
        if operation == "civil_date":
            return state_from_civil_date(
                spec,
                inputs["civil_date"],
                inputs.get("profile"),
            )
        if operation == "prognosis_eligibility":
            state = date_to_position(inputs["date"])
            return {
                "preserved_main_calendar_prognosis_available": (
                    False if state["is_additional_day"] else None
                ),
                "historical_absence_proven": False,
                "requires_witness_lookup": True,
                "emit_birth_reading": False,
            }
        if operation == "output_contract":
            output = position_to_date(inputs["year_position"])
            forbidden = set(spec["output_contract"]["forbidden_fields"])
            boundary = spec["product_boundary"]
            return {
                "forbidden_fields_present": sorted(forbidden & set(output)),
                "birth_reading_enabled": boundary["birth_reading_enabled"],
                "customer_eligible": boundary["customer_eligible"],
                "hemerology_ready": boundary["hemerology_ready"],
            }
    except CalendarInputError as exc:
        return {"error": exc.code}
    raise AssertionError(f"Unknown vector operation: {operation}")


def validate() -> dict[str, Any]:
    """Validate sources, calendar invariants, vectors, and product boundaries."""
    spec = load_json(SPEC_PATH)
    manifest = load_json(MANIFEST_PATH)
    vectors = load_json(VECTORS_PATH)
    registry = load_json(REGISTRY_PATH)
    if not (
        spec["source_pack_id"]
        == manifest["source_pack_id"]
        == vectors["source_pack_id"]
    ):
        raise AssertionError("Egyptian source-pack identity mismatch")
    if not (
        spec["tradition_id"]
        == manifest["tradition_id"]
        == vectors["tradition_id"]
    ):
        raise AssertionError("Egyptian tradition identity mismatch")
    if set(spec["source_registry_ids"]) != set(manifest["source_registry_ids"]):
        raise AssertionError("Spec/manifest source mismatch")
    if set(spec["source_registry_ids"]) != set(vectors["source_ids"]):
        raise AssertionError("Spec/vector source mismatch")
    registry_by_id = {source["id"]: source for source in registry["sources"]}
    porceddu = registry_by_id["egyptian_porceddu_periodicity_2008"]
    source_anchor = spec["source_anchors"][0]
    if (
        porceddu["file_sha256"] != source_anchor["sha256"]
        or porceddu["file_bytes"] != source_anchor["bytes"]
        or porceddu["pages"] != source_anchor["pages"]
    ):
        raise AssertionError("Pinned Porceddu PDF identity changed")
    budge = registry_by_id[
        "egyptian_cpl_budge_1923_hieratic_papyri_second_series"
    ]
    budge_anchor = spec["source_anchors"][2]
    if (
        budge["file_sha256"] != budge_anchor["sha256"]
        or budge["file_bytes"] != budge_anchor["bytes"]
        or budge["pages"] != budge_anchor["pages"]
    ):
        raise AssertionError("Pinned Budge PDF identity changed")
    if spec["hemerology_boundary"]["missing_witness_text_creates_negative_rule"] is not False:
        raise AssertionError("Missing Egyptian witness text became a negative rule")

    model = spec["calendar_model"]
    if (
        model["year_length_days"] != YEAR_LENGTH
        or model["ordinary_days"] != ORDINARY_DAYS
        or model["ordinary_months"] != 12
        or model["ordinary_month_length_days"] != 30
        or model["additional_days"] != 5
        or model["intercalation"] is not False
    ):
        raise AssertionError("Egyptian civil-calendar model changed")
    if [season["id"] for season in model["seasons"]] != list(SEASONS):
        raise AssertionError("Egyptian season order changed")
    if spec["chronology_contract"]["default_profile"] is not None:
        raise AssertionError("A default Egyptian chronology was introduced")
    boundary = spec["product_boundary"]
    prohibited_true = {
        "live_engine",
        "customer_eligible",
        "birth_reading_enabled",
        "chronology_ready",
        "hemerology_ready",
    }
    if any(boundary[field] is not False for field in prohibited_true):
        raise AssertionError("Egyptian research artifact crossed product boundary")

    states = [position_to_date(position) for position in range(YEAR_LENGTH)]
    normalized_dates = [
        (state["season_id"], state["month_in_season"], state["day"])
        for state in states
    ]
    if len(set(normalized_dates)) != YEAR_LENGTH:
        raise AssertionError("Egyptian civil year lacks 365 unique positions")
    for position, state in enumerate(states):
        round_trip = date_to_position(
            {
                "season_id": state["season_id"],
                "month_in_season": state["month_in_season"],
                "day": state["day"],
            }
        )
        if round_trip["year_position"] != position:
            raise AssertionError(f"Round trip failed at position {position}")
    if any(
        position_to_date(position)["year_position"]
        != position_to_date(position + YEAR_LENGTH)["year_position"]
        for position in range(-YEAR_LENGTH, YEAR_LENGTH + 1)
    ):
        raise AssertionError("Positive/negative 365-day recurrence failed")

    rule_ids = {rule["rule_id"] for rule in manifest["rules"]}
    covered_rule_ids: set[str] = set()
    failures: list[str] = []
    for vector in vectors["vectors"]:
        covered_rule_ids.update(vector["rule_ids"])
        actual = _run_vector(spec, vector)
        if actual != vector["expected"]:
            failures.append(
                f"{vector['vector_id']}: expected={vector['expected']!r}, "
                f"actual={actual!r}"
            )
    if failures:
        raise AssertionError("Vector failures:\n" + "\n".join(failures))
    if covered_rule_ids != rule_ids:
        raise AssertionError(
            f"Rule coverage mismatch: missing={sorted(rule_ids - covered_rule_ids)}, "
            f"unknown={sorted(covered_rule_ids - rule_ids)}"
        )
    if any(
        rule["conclusion"].get("customer_prediction") is not False
        for rule in manifest["rules"]
    ):
        raise AssertionError("An Egyptian calendar rule enables customer prediction")

    return {
        "status": "pass",
        "sources": len(spec["source_registry_ids"]),
        "seasons": len(SEASONS),
        "ordinary_months": model["ordinary_months"],
        "additional_days": model["additional_days"],
        "unique_positions": len(set(normalized_dates)),
        "rules": len(rule_ids),
        "vectors": len(vectors["vectors"]),
        "default_profile": None,
        "live_engine": boundary["live_engine"],
        "customer_eligible": boundary["customer_eligible"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2, sort_keys=True))
