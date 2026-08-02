"""Validate the fail-closed multi-tradition engine coverage manifest."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import jsonschema


ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "engine_coverage_manifest.json"
SCHEMA_PATH = ROOT / "engine_coverage_manifest.schema.json"
REGISTRY_PATH = ROOT / "source_registry.json"

EXPECTED_TRACK_IDS = {
    "jaimini",
    "japanese_sukuyodo",
    "indian_jyotisha",
    "chinese_bazi",
    "ziwei_doushu",
    "mesopotamian_babylonian",
    "islamicate_persian",
    "tibetan",
    "maya",
    "nahua_central_mexican",
    "pharaonic_egyptian",
    "japanese_onmyodo",
    "burmese",
    "thai",
    "khmer",
    "sinhalese",
    "mon",
    "mongolian",
    "korean",
    "vietnamese",
    "medieval_jewish",
    "pre_islamic_arabian",
}

EXPECTED_AUDIT_DIRECTORIES = {
    "jaimini",
    "sukuyodo",
    "babylonian",
    "bazi",
    "burmese",
    "egyptian",
    "islamicate",
    "jyotisha",
    "khmer",
    "korean",
    "maya",
    "medieval_jewish",
    "mon",
    "mongolian",
    "nahua",
    "onmyodo",
    "pre_islamic_arabian",
    "sinhalese",
    "thai",
    "tibetan",
    "vietnamese",
    "ziwei",
}

EXPECTED_STATUS_COUNTS = {
    "research_verified": 20,
    "source_limited": 54,
    "not_implemented": 3,
}


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object and reject non-object roots."""
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise AssertionError(f"Expected a JSON object: {path}")
    return value


def validate_track_identity(
    manifest: dict[str, Any],
    registry: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Validate track and module identities against the registry and source audits."""
    tracks = manifest.get("tracks")
    if not isinstance(tracks, list):
        raise AssertionError("tracks must be a list")
    track_ids = [track.get("track_id") for track in tracks]
    if len(track_ids) != len(set(track_ids)):
        raise AssertionError("Duplicate track_id")
    if set(track_ids) != EXPECTED_TRACK_IDS:
        raise AssertionError(
            f"Track inventory changed: missing={sorted(EXPECTED_TRACK_IDS - set(track_ids))}, "
            f"unexpected={sorted(set(track_ids) - EXPECTED_TRACK_IDS)}"
        )

    registry_traditions = {source["tradition"] for source in registry["sources"]}
    modules: list[dict[str, Any]] = []
    audit_directories: set[str] = set()
    for track in tracks:
        source_audit = track.get("source_audit")
        if not isinstance(source_audit, str):
            raise AssertionError(f"Track lacks source audit: {track['track_id']}")
        audit_path = ROOT / source_audit
        if not audit_path.is_file():
            raise AssertionError(f"Missing source audit: {source_audit}")
        audit_directories.add(Path(source_audit).parent.as_posix())

        tradition_ids = track.get("registry_tradition_ids")
        if not isinstance(tradition_ids, list) or not tradition_ids:
            raise AssertionError(
                f"Track lacks registry traditions: {track['track_id']}"
            )
        unknown = set(tradition_ids) - registry_traditions
        if unknown:
            raise AssertionError(
                f"Unknown registry traditions for {track['track_id']}: {sorted(unknown)}"
            )
        track_modules = track.get("modules")
        if not isinstance(track_modules, list) or not track_modules:
            raise AssertionError(f"Track has no enumerated modules: {track['track_id']}")
        modules.extend(track_modules)

    if audit_directories != EXPECTED_AUDIT_DIRECTORIES:
        raise AssertionError(
            "Source-audit coverage changed: "
            f"missing={sorted(EXPECTED_AUDIT_DIRECTORIES - audit_directories)}, "
            f"unexpected={sorted(audit_directories - EXPECTED_AUDIT_DIRECTORIES)}"
        )
    return tracks, modules


def validate_product_boundaries(
    manifest: dict[str, Any],
    tracks: list[dict[str, Any]],
    modules: list[dict[str, Any]],
) -> None:
    """Enforce Western-only live status and fail-closed customer eligibility."""
    boundary = manifest.get("global_product_boundary", {})
    expected = {
        "western_engine_live": True,
        "nonwestern_live_engines": [],
        "nonwestern_customer_eligible_modules": [],
        "historical_use_only_required": True,
        "prose_may_invent_missing_rules": False,
        "missing_modules_must_be_reported": True,
    }
    if boundary != expected:
        raise AssertionError("Global product boundary changed")
    if any(track.get("live_engine") is not False for track in tracks):
        raise AssertionError("A non-Western track was marked live")
    if any(track.get("customer_eligible") is not False for track in tracks):
        raise AssertionError("A non-Western track was marked customer-eligible")
    if any(module.get("live_engine") is True for module in modules):
        raise AssertionError("A non-Western module was marked live")
    if any(module.get("customer_eligible") is True for module in modules):
        raise AssertionError("A non-Western module was marked customer-eligible")


def validate_modules(
    manifest: dict[str, Any],
    tracks: list[dict[str, Any]],
    modules: list[dict[str, Any]],
) -> Counter[str]:
    """Validate module statuses, artifacts, gates, and track rollups."""
    module_ids = [module.get("module_id") for module in modules]
    if len(module_ids) != len(set(module_ids)):
        duplicates = sorted(
            module_id
            for module_id, count in Counter(module_ids).items()
            if count > 1
        )
        raise AssertionError(f"Duplicate module IDs: {duplicates}")

    allowed_statuses = set(manifest.get("status_vocabulary", {}))
    allowed_states = set(manifest.get("implementation_states", []))
    statuses: Counter[str] = Counter()
    referenced_artifacts: set[Path] = set()

    for module in modules:
        module_id = module["module_id"]
        status = module.get("coverage_status")
        state = module.get("implementation_state")
        if status not in allowed_statuses:
            raise AssertionError(f"Unknown status for {module_id}: {status}")
        if state not in allowed_states:
            raise AssertionError(f"Unknown implementation state for {module_id}: {state}")
        statuses[status] += 1

        birth_eligible = module.get("birth_input_eligible")
        if birth_eligible not in {True, False, "conditional"}:
            raise AssertionError(f"Invalid birth eligibility for {module_id}")
        artifacts = module.get("artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            raise AssertionError(f"Module lacks evidence artifact: {module_id}")
        for artifact in artifacts:
            path = ROOT / artifact
            if not path.is_file():
                raise AssertionError(f"Missing module artifact for {module_id}: {artifact}")
            referenced_artifacts.add(path.resolve())
        gates = module.get("remaining_gates")
        if status != "production_verified" and (
            not isinstance(gates, list) or not gates
        ):
            raise AssertionError(f"Incomplete module lacks remaining gates: {module_id}")
        if status == "not_implemented" and state != "none":
            raise AssertionError(f"Not-implemented module has implementation: {module_id}")
        if status == "research_verified" and state not in {
            "validated_research_artifact",
            "source_design_only",
        }:
            raise AssertionError(
                f"Research-verified module has insufficient evidence state: {module_id}"
            )
        if state == "validated_research_artifact" and not any(
            artifact.endswith(".json") for artifact in artifacts
        ):
            raise AssertionError(
                f"Validated research artifact lacks machine-readable evidence: {module_id}"
            )

    if dict(statuses) != EXPECTED_STATUS_COUNTS:
        raise AssertionError(
            f"Coverage status counts changed: expected={EXPECTED_STATUS_COUNTS}, "
            f"actual={dict(statuses)}"
        )
    if statuses["production_verified"] != 0 or statuses["experimental"] != 0:
        raise AssertionError("Unexpected production or experimental non-Western module")

    for track in tracks:
        track_statuses = {module["coverage_status"] for module in track["modules"]}
        expected_track_status = (
            "research_verified"
            if "research_verified" in track_statuses
            else "source_limited"
            if "source_limited" in track_statuses
            else "not_implemented"
        )
        if track.get("overall_status") != expected_track_status:
            raise AssertionError(f"Incorrect status rollup for {track['track_id']}")

    rule_manifests = {
        path.resolve() for path in ROOT.rglob("*rule_manifest.json")
    }
    unreferenced_rule_manifests = rule_manifests - referenced_artifacts
    if unreferenced_rule_manifests:
        relative = sorted(
            path.relative_to(ROOT).as_posix() for path in unreferenced_rule_manifests
        )
        raise AssertionError(f"Rule manifests absent from coverage map: {relative}")
    return statuses


def validate() -> dict[str, Any]:
    """Validate the complete coverage inventory and return auditable counts."""
    manifest = load_json(MANIFEST_PATH)
    schema = load_json(SCHEMA_PATH)
    registry = load_json(REGISTRY_PATH)
    validator = jsonschema.Draft202012Validator(
        schema,
        format_checker=jsonschema.FormatChecker(),
    )
    errors = sorted(
        validator.iter_errors(manifest),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.absolute_path) or "<root>"
        raise AssertionError(
            f"Coverage schema failure at {location}: {first.message}"
        )
    tracks, modules = validate_track_identity(manifest, registry)
    validate_product_boundaries(manifest, tracks, modules)
    statuses = validate_modules(manifest, tracks, modules)
    birth_modules = [
        module
        for module in modules
        if module["birth_input_eligible"] in {True, "conditional"}
    ]
    validated_artifact_modules = [
        module
        for module in modules
        if module["implementation_state"] == "validated_research_artifact"
    ]
    return {
        "status": "pass",
        "tracks": len(tracks),
        "modules": len(modules),
        "birth_input_modules": len(birth_modules),
        "validated_research_artifact_modules": len(validated_artifact_modules),
        "coverage_status_counts": dict(sorted(statuses.items())),
        "nonwestern_live_tracks": 0,
        "nonwestern_customer_eligible_tracks": 0,
        "western_engine_live": manifest["global_product_boundary"][
            "western_engine_live"
        ],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2, sort_keys=True))
