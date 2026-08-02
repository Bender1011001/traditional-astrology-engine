"""Validate the research-only, fail-closed tonalpohualli cycle artifact."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SPEC_PATH = ROOT / "tonalpohualli_cycle_spec.json"
MANIFEST_PATH = ROOT / "calendar_rule_manifest.json"
VECTORS_PATH = ROOT / "calendar_validation_vectors.json"

EXPECTED_SIGN_ORDER = [
    "cipactli",
    "ehecatl",
    "calli",
    "cuetzpalin",
    "coatl",
    "miquiztli",
    "mazatl",
    "tochtli",
    "atl",
    "itzcuintli",
    "ozomatli",
    "malinalli",
    "acatl",
    "ocelotl",
    "cuauhtli",
    "cozcacuauhtli",
    "ollin",
    "tecpatl",
    "quiahuitl",
    "xochitl",
]
EXPECTED_TRECENA_HEADS = [
    "cipactli",
    "ocelotl",
    "mazatl",
    "xochitl",
    "acatl",
    "miquiztli",
    "quiahuitl",
    "malinalli",
    "coatl",
    "tecpatl",
    "ozomatli",
    "cuetzpalin",
    "ollin",
    "itzcuintli",
    "calli",
    "cozcacuauhtli",
    "atl",
    "ehecatl",
    "cuauhtli",
    "tochtli",
]


class CycleInputError(ValueError):
    """A stable fail-closed error raised for an invalid conversion request."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def load_json(path: Path) -> dict[str, Any]:
    """Load and type-check a JSON object."""
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise AssertionError(f"Expected a JSON object: {path}")
    return value


def _sign_order(spec: dict[str, Any]) -> list[str]:
    signs = spec["cycle"]["day_signs"]
    indices = [sign["index"] for sign in signs]
    if indices != list(range(20)):
        raise AssertionError("Day-sign indices are not the exact range 0..19")
    ids = [str(sign["id"]) for sign in signs]
    if ids != EXPECTED_SIGN_ORDER:
        raise AssertionError("Day-sign order changed from the inspected INAH table")
    if len(ids) != len(set(ids)):
        raise AssertionError("Day-sign identifiers are not unique")
    return ids


def _state_from_index(index: int, signs: list[str], day_offset: int) -> dict[str, Any]:
    normalized = index % 260
    coefficient = normalized % 13 + 1
    sign_id = signs[normalized % 20]
    trecena_start_index = (normalized - (coefficient - 1)) % 260
    return {
        "coefficient": coefficient,
        "day_sign_id": sign_id,
        "canonical_cycle_index": normalized,
        "trecena_position": coefficient,
        "trecena_start_sign_id": signs[trecena_start_index % 20],
        "day_offset": day_offset,
    }


def state_from_offset(spec: dict[str, Any], day_offset: int) -> dict[str, Any]:
    """Return a cycle position relative to canonical 1 Cipactli, with no epoch."""
    if isinstance(day_offset, bool) or not isinstance(day_offset, int):
        raise CycleInputError("day_offset_not_integer")
    return _state_from_index(day_offset, _sign_order(spec), day_offset)


def _canonical_index(coefficient: int, sign_id: str, signs: list[str]) -> int:
    if isinstance(coefficient, bool) or not isinstance(coefficient, int):
        raise CycleInputError("invalid_epoch_coefficient")
    if not 1 <= coefficient <= 13:
        raise CycleInputError("invalid_epoch_coefficient")
    if sign_id not in signs:
        raise CycleInputError("invalid_epoch_day_sign")
    matches = [
        index
        for index in range(260)
        if index % 13 + 1 == coefficient and signs[index % 20] == sign_id
    ]
    if len(matches) != 1:
        raise AssertionError("A coefficient/sign pair did not map uniquely in 260 days")
    return matches[0]


def _validate_epoch(spec: dict[str, Any], epoch: Any) -> tuple[date, int]:
    if epoch is None:
        raise CycleInputError("missing_epoch")
    if not isinstance(epoch, dict):
        raise CycleInputError("invalid_epoch")
    required = set(spec["epoch_contract"]["required_fields"])
    if required - set(epoch):
        raise CycleInputError("incomplete_epoch")
    if epoch["tradition_id"] != spec["epoch_contract"]["required_tradition_id"]:
        raise CycleInputError("wrong_epoch_tradition")
    for field in required - {"epoch_tonalpohualli"}:
        if not isinstance(epoch[field], str) or not epoch[field].strip():
            raise CycleInputError("invalid_epoch")
    epoch_state = epoch["epoch_tonalpohualli"]
    if not isinstance(epoch_state, dict):
        raise CycleInputError("invalid_epoch_state")
    state_fields = set(spec["epoch_contract"]["epoch_tonalpohualli_fields"])
    if state_fields - set(epoch_state):
        raise CycleInputError("invalid_epoch_state")
    try:
        epoch_date = date.fromisoformat(epoch["epoch_civil_date"])
    except ValueError as exc:
        raise CycleInputError("invalid_epoch_civil_date") from exc
    anchor_index = _canonical_index(
        epoch_state["coefficient"],
        epoch_state["day_sign_id"],
        _sign_order(spec),
    )
    return epoch_date, anchor_index


def state_from_civil_date(
    spec: dict[str, Any], civil_date: str, epoch: Any
) -> dict[str, Any]:
    """Map a resolved ISO civil date under a complete, explicitly named epoch."""
    epoch_date, anchor_index = _validate_epoch(spec, epoch)
    if not isinstance(civil_date, str):
        raise CycleInputError("invalid_civil_date")
    try:
        target_date = date.fromisoformat(civil_date)
    except ValueError as exc:
        raise CycleInputError("invalid_civil_date") from exc
    offset = (target_date - epoch_date).days
    return _state_from_index(anchor_index + offset, _sign_order(spec), offset)


def _run_vector(spec: dict[str, Any], vector: dict[str, Any]) -> dict[str, Any]:
    inputs = vector["inputs"]
    operation = inputs.get("operation")
    if operation == "offset":
        return state_from_offset(spec, inputs["day_offset"])
    if operation == "civil_date":
        try:
            return state_from_civil_date(
                spec,
                inputs["civil_date"],
                inputs.get("epoch"),
            )
        except CycleInputError as exc:
            return {"error": exc.code}
    if operation == "output_contract":
        output = state_from_offset(spec, inputs["day_offset"])
        forbidden = set(spec["output_contract"]["forbidden_fields"])
        return {
            "forbidden_fields_present": sorted(forbidden & set(output)),
            "birth_reading_enabled": spec["product_boundary"][
                "birth_reading_enabled"
            ],
            "customer_eligible": spec["product_boundary"]["customer_eligible"],
        }
    raise AssertionError(f"Unknown vector operation: {operation}")


def validate() -> dict[str, Any]:
    """Validate source identity, arithmetic invariants, boundaries, and vectors."""
    spec = load_json(SPEC_PATH)
    manifest = load_json(MANIFEST_PATH)
    vectors = load_json(VECTORS_PATH)
    signs = _sign_order(spec)

    if manifest["source_pack_id"] != vectors["source_pack_id"]:
        raise AssertionError("Manifest/vector source-pack mismatch")
    if manifest["tradition_id"] != spec["tradition_id"] != vectors["tradition_id"]:
        raise AssertionError("Tradition mismatch")
    if set(manifest["source_registry_ids"]) != set(spec["source_registry_ids"]):
        raise AssertionError("Spec/manifest source mismatch")
    if set(vectors["source_ids"]) != set(spec["source_registry_ids"]):
        raise AssertionError("Spec/vector source mismatch")
    boundary = spec["product_boundary"]
    required_false = {
        "live_engine",
        "customer_eligible",
        "birth_reading_enabled",
        "correlation_ready",
        "interpretation_ready",
    }
    if any(boundary[field] is not False for field in required_false):
        raise AssertionError("A prohibited Nahua product boundary was enabled")
    if spec["epoch_contract"]["default_epoch"] is not None:
        raise AssertionError("A default Nahua epoch was introduced")

    states = [state_from_offset(spec, offset) for offset in range(260)]
    pairs = [(state["coefficient"], state["day_sign_id"]) for state in states]
    if len(set(pairs)) != 260:
        raise AssertionError("The first cycle does not contain 260 unique pairs")
    if state_from_offset(spec, 0) | {"day_offset": 260} != state_from_offset(spec, 260):
        raise AssertionError("The joint series does not round-trip at 260 days")
    if any(
        state_from_offset(spec, offset)["canonical_cycle_index"]
        != state_from_offset(spec, offset + 260)["canonical_cycle_index"]
        for offset in range(-260, 261)
    ):
        raise AssertionError("Positive/negative modular round-trip failed")
    trecena_heads = [states[index]["day_sign_id"] for index in range(0, 260, 13)]
    if trecena_heads != EXPECTED_TRECENA_HEADS:
        raise AssertionError("Trecena-head order changed from the inspected table")

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
        "day_signs": len(signs),
        "trecenas": len(trecena_heads),
        "unique_pairs": len(set(pairs)),
        "rules": len(rule_ids),
        "vectors": len(vectors["vectors"]),
        "default_epoch": None,
        "live_engine": boundary["live_engine"],
        "customer_eligible": boundary["customer_eligible"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2, sort_keys=True))
