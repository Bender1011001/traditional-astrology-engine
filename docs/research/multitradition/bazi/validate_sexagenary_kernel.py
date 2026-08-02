"""Validate the research-only, fail-closed BaZi sexagenary kernel artifact."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
SPEC_PATH = ROOT / "sexagenary_kernel_spec.json"
MANIFEST_PATH = ROOT / "sexagenary_rule_manifest.json"
VECTORS_PATH = ROOT / "sexagenary_validation_vectors.json"

EXPECTED_STEM_ORDER = [
    "jia", "yi", "bing", "ding", "wu_stem", "ji", "geng", "xin", "ren", "gui",
]
EXPECTED_BRANCH_ORDER = [
    "zi", "chou", "yin_branch", "mao", "chen", "si",
    "wu_branch", "wei", "shen", "you", "xu", "hai",
]
FORBIDDEN_OUTPUT_FIELDS = {
    "five_element_tally", "ten_god", "hidden_stems", "luck_pillar", "strength",
    "pattern", "personality", "fate", "fortune", "health", "compatibility",
    "recommendation",
}


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _pair(index: int) -> tuple[str, str]:
    return EXPECTED_STEM_ORDER[index % 10], EXPECTED_BRANCH_ORDER[index % 12]


def _shichen(time_of_day: str) -> str:
    hour, minute = (int(part) for part in time_of_day.split(":"))
    if not (0 <= hour < 24 and 0 <= minute < 60):
        raise ValueError(f"Invalid time of day: {time_of_day}")
    return EXPECTED_BRANCH_ORDER[((hour + 1) % 24) // 2]


def _run_vector(spec: dict[str, Any], vector: dict[str, Any]) -> dict[str, Any]:
    inputs = vector["inputs"]
    operation = inputs["operation"]
    cycle = spec["cycle"]

    if operation == "offset":
        index = inputs["offset"] % 60
        stem_id, branch_id = _pair(index)
        if inputs.get("request_interpretation"):
            return {"emit_interpretation": False, "forbidden_fields_absent": True}
        return {"stem_id": stem_id, "branch_id": branch_id, "sexagenary_index": index}

    if operation == "pair_check":
        stem_index = EXPECTED_STEM_ORDER.index(inputs["stem_id"])
        branch_index = EXPECTED_BRANCH_ORDER.index(inputs["branch_id"])
        if stem_index % 2 != branch_index % 2:
            return {"valid_pair": False, "reason": "cross_parity_pair_never_occurs"}
        return {"valid_pair": True}

    if operation == "stem_offset":
        return {"stem_id": EXPECTED_STEM_ORDER[inputs["offset"] % 10]}

    if operation == "branch_offset":
        return {"branch_id": EXPECTED_BRANCH_ORDER[inputs["offset"] % 12]}

    if operation == "shichen":
        return {"shichen_branch_id": _shichen(inputs["time_of_day"])}

    if operation == "first_month_stem":
        table = cycle["month_stem_from_year_stem"]["table"]
        return {"first_month_stem_id": table[inputs["year_stem_id"]]}

    if operation == "zi_hour_stem":
        table = cycle["hour_stem_from_day_stem"]["table"]
        return {"zi_hour_stem_id": table[inputs["day_stem_id"]]}

    if operation == "solar_term_structure":
        terms = spec["solar_terms"]
        return {
            "term_count": terms["term_count"],
            "major_terms": terms["major_terms"],
            "minor_terms": terms["minor_terms"],
            "per_term_longitudes_encoded": False,
        }

    if operation == "civil_date":
        anchor = inputs.get("anchor")
        if anchor is None:
            return {"rejected": True, "reason": "no_named_anchor_profile"}
        required = set(spec["anchor_contract"]["required_fields"])
        if set(anchor) != required:
            return {"rejected": True, "reason": "incomplete_anchor_profile"}
        if anchor["tradition_id"] != spec["anchor_contract"]["required_tradition_id"]:
            return {"rejected": True, "reason": "cross_tradition_anchor"}
        civil = date.fromisoformat(inputs["civil_date"])
        epoch = date.fromisoformat(anchor["anchor_civil_date"])
        day_offset = (civil - epoch).days
        index = (anchor["anchor_sexagenary_index"] + day_offset) % 60
        stem_id, branch_id = _pair(index)
        return {
            "stem_id": stem_id,
            "branch_id": branch_id,
            "sexagenary_index": index,
            "day_offset": day_offset,
        }

    if operation == "pillar_boundary_assignment":
        if inputs.get("convention_profile") is None:
            return {"rejected": True, "reason": "no_named_convention_profile"}
        raise AssertionError("No named convention profile has been approved")

    raise ValueError(f"Unknown vector operation: {operation}")


def validate() -> dict[str, Any]:
    spec = _read(SPEC_PATH)
    manifest = _read(MANIFEST_PATH)
    vectors = _read(VECTORS_PATH)

    stems = spec["cycle"]["stems"]
    branches = spec["cycle"]["branches"]
    if [stem["id"] for stem in stems] != EXPECTED_STEM_ORDER:
        raise AssertionError("Stem inventory or order changed")
    if [branch["id"] for branch in branches] != EXPECTED_BRANCH_ORDER:
        raise AssertionError("Branch inventory or order changed")
    if spec["cycle"]["joint_period"] != 60:
        raise AssertionError("Joint sexagenary period changed")
    if spec["anchor_contract"]["default_anchor"] is not None:
        raise AssertionError("A default day-count anchor was introduced")
    if spec["convention_contract"]["default_profile"] is not None:
        raise AssertionError("A default boundary convention was introduced")

    boundary = spec["product_boundary"]
    for flag in (
        "live_engine", "customer_eligible", "birth_reading_enabled",
        "anchor_ready", "convention_ready", "interpretation_ready",
    ):
        if boundary[flag] is not False:
            raise AssertionError(f"Product boundary flag {flag} is not False")
    if set(spec["output_contract"]["forbidden_fields"]) != FORBIDDEN_OUTPUT_FIELDS:
        raise AssertionError("Forbidden output-field inventory changed")

    # Exhaustive 60-cycle enumeration: parity invariant and pair census.
    pairs = [_pair(index) for index in range(60)]
    if len(set(pairs)) != 60:
        raise AssertionError("Sexagenary cycle does not produce 60 unique pairs")
    if pairs[0] != ("jia", "zi") or pairs[59] != ("gui", "hai"):
        raise AssertionError("Sexagenary cycle endpoints changed")
    for stem_id in EXPECTED_STEM_ORDER:
        if sum(1 for stem, _ in pairs if stem == stem_id) != 6:
            raise AssertionError("A stem does not occur exactly six times")
    for branch_id in EXPECTED_BRANCH_ORDER:
        if sum(1 for _, branch in pairs if branch == branch_id) != 5:
            raise AssertionError("A branch does not occur exactly five times")
    cross_parity = [
        (stem_index, branch_index)
        for stem_index in range(10)
        for branch_index in range(12)
        if stem_index % 2 != branch_index % 2
    ]
    if len(cross_parity) != 60:
        raise AssertionError("Cross-parity complement census changed")
    if any(
        (EXPECTED_STEM_ORDER[stem_index], EXPECTED_BRANCH_ORDER[branch_index]) in pairs
        for stem_index, branch_index in cross_parity
    ):
        raise AssertionError("A cross-parity pair leaked into the sexagenary cycle")

    # Exhaustive lookup-table checks against the closed-form advance.
    month_table = spec["cycle"]["month_stem_from_year_stem"]["table"]
    if set(month_table) != set(EXPECTED_STEM_ORDER):
        raise AssertionError("Month-stem table does not cover all ten year stems")
    for year_stem, first_month_stem in month_table.items():
        year_index = EXPECTED_STEM_ORDER.index(year_stem)
        expected_index = (2 + (year_index % 5) * 2) % 10
        if EXPECTED_STEM_ORDER.index(first_month_stem) != expected_index:
            raise AssertionError(f"Month-stem table row for {year_stem} changed")
    hour_table = spec["cycle"]["hour_stem_from_day_stem"]["table"]
    if set(hour_table) != set(EXPECTED_STEM_ORDER):
        raise AssertionError("Hour-stem table does not cover all ten day stems")
    for day_stem, zi_stem in hour_table.items():
        day_index = EXPECTED_STEM_ORDER.index(day_stem)
        expected_index = (day_index % 5) * 2
        if EXPECTED_STEM_ORDER.index(zi_stem) != expected_index:
            raise AssertionError(f"Hour-stem table row for {day_stem} changed")

    # Exhaustive shichen partition: every minute of the day maps to one branch.
    minute_census: dict[str, int] = {branch_id: 0 for branch_id in EXPECTED_BRANCH_ORDER}
    for hour in range(24):
        for minute in range(60):
            minute_census[_shichen(f"{hour:02d}:{minute:02d}")] += 1
    if any(count != 120 for count in minute_census.values()):
        raise AssertionError("Shichen partition does not give each branch 120 minutes")
    if _shichen("23:00") != "zi" or _shichen("00:59") != "zi" or _shichen("01:00") != "chou":
        raise AssertionError("Zi straddle or Chou boundary changed")

    rule_ids = {rule["rule_id"] for rule in manifest["rules"]}
    covered_rule_ids: set[str] = set()
    failures: list[str] = []
    for vector in vectors["vectors"]:
        covered_rule_ids.update(vector["rule_ids"])
        actual = _run_vector(spec, vector)
        if actual != vector["expected"]:
            failures.append(
                f"{vector['vector_id']}: expected={vector['expected']!r}, actual={actual!r}"
            )
    if failures:
        raise AssertionError("Vector failures:\n" + "\n".join(failures))
    if covered_rule_ids != rule_ids:
        raise AssertionError(
            f"Rule coverage mismatch: missing={sorted(rule_ids - covered_rule_ids)}, "
            f"unknown={sorted(covered_rule_ids - rule_ids)}"
        )

    return {
        "status": "pass",
        "source_count": len(spec["source_registry_ids"]),
        "stems": len(stems),
        "branches": len(branches),
        "unique_pairs": len(set(pairs)),
        "rules": len(rule_ids),
        "vectors": len(vectors["vectors"]),
        "default_anchor": None,
        "default_convention_profile": None,
        "live_engine": boundary["live_engine"],
        "customer_eligible": boundary["customer_eligible"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2, sort_keys=True))
