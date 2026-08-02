"""Validate the Abu Ma'shar and al-Qabisi passage-access research gate."""

from __future__ import annotations

import hashlib
import json
import re
import urllib.request
from argparse import ArgumentParser
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
MATRIX_PATH = ROOT / "abu_mashar_al_qabisi_access_matrix.json"
CONCORDANCE_PATH = ROOT / "al_biruni_abu_mashar_al_qabisi_candidate_concordance.json"
REGISTRY_PATH = ROOT.parent / "source_registry.json"

EXPECTED_ARTIFACT_HASHES = {
    "abu_mashar_great_introduction_arabic_tei": (
        "816c724496c75b5a42e87bf1f765808f8616c20b96e47e90c00d631b24ee2208"
    ),
    "abu_mashar_great_introduction_hermann_latin_tei": (
        "5a4898588e4caf2af4d32671950a99d664d7a362102ec4afc291c65145231cbe"
    ),
    "abu_mashar_great_introduction_john_latin_tei": (
        "d1bf58221d60c39405e05da3d1cb3eb66d3569445941ecfe6f7a55f10d73564d"
    ),
    "al_qabisi_introduction_arabic_tei": (
        "3267ff80d6b10dbecf3a2eed7a51495db0842dd20d711a5952cbcbfa05657add"
    ),
    "al_qabisi_introduction_john_latin_tei": (
        "0766e56b232809e763e8ae1f1cbcbd131ce3649df811ef319e2c1d6803de74b8"
    ),
    "abu_mashar_abbreviation_arabic_tei": (
        "fcd2bbc3df7d19ce5bf10f9abbf2cd5cfba8bcbbb8635a4ab58dda779bda488a"
    ),
    "abu_mashar_abbreviation_adelard_latin_tei": (
        "420283ecbe1d320d1a4cd0f048ee39bf37e0be5dbbdecc905ec1b0d8b55cf777"
    ),
}

EXPECTED_WITNESS_WORKS = {
    "abu_mashar_great_introduction_wurzburg_tei": "kitab_al_mudkhal_al_kabir",
    "al_qabisi_introduction_wurzburg_tei": (
        "kitab_al_mudkhal_ila_sinaat_ahkam_al_nujum"
    ),
    "abu_mashar_abbreviation_wurzburg_tei": "mukhtasar_al_mudkhal",
}

EXPECTED_PAGE_BREAK_PROFILES = {
    "abu_mashar_great_introduction_arabic_tei": (454, {}),
    "abu_mashar_great_introduction_hermann_latin_tei": (
        168,
        {"#MsN": 108, "#Ratdolt": 137},
    ),
    "abu_mashar_great_introduction_john_latin_tei": (386, {"#ms": 191}),
    "al_qabisi_introduction_arabic_tei": (69, {}),
    "al_qabisi_introduction_john_latin_tei": (140, {}),
    "abu_mashar_abbreviation_arabic_tei": (36, {"#B": 22}),
    "abu_mashar_abbreviation_adelard_latin_tei": (26, {"#S": 9}),
}

EXPECTED_CONCEPT_IDS = {
    "planet_and_sign_gender_sect",
    "halb_and_hayyiz",
    "planetary_house_joys",
    "firdaria_year_values",
    "firdaria_sequence_and_subperiods",
}

EXPECTED_VARIANT_IDS = {
    "firdaria_great_introduction_mars_variant",
    "firdaria_great_introduction_john_internal_total",
    "firdaria_abbreviation_latin_total",
    "halb_hayyiz_qabisi_latin_terminology",
    "halb_lexeme_semantic_anomaly",
    "hayyiz_abbreviation_competentia",
    "mercury_author_scope_difference",
    "firdaria_scope_not_contradiction",
}

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object and reject non-object roots."""
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise AssertionError(f"Expected a JSON object in {path}")
    return value


def flatten_artifacts(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    """Return every artifact while enforcing unique witness-set identities."""
    witness_sets = matrix.get("witness_sets")
    if not isinstance(witness_sets, list):
        raise AssertionError("witness_sets must be a list")

    witness_ids = [item.get("witness_set_id") for item in witness_sets]
    if len(witness_ids) != len(set(witness_ids)):
        raise AssertionError("Duplicate witness_set_id")
    if set(witness_ids) != set(EXPECTED_WITNESS_WORKS):
        raise AssertionError("Unexpected or missing witness set")

    artifacts: list[dict[str, Any]] = []
    for witness_set in witness_sets:
        witness_id = witness_set["witness_set_id"]
        if witness_set.get("work_id") != EXPECTED_WITNESS_WORKS[witness_id]:
            raise AssertionError(f"Work identity changed for {witness_id}")
        set_artifacts = witness_set.get("artifacts")
        if not isinstance(set_artifacts, list) or not set_artifacts:
            raise AssertionError(f"No artifacts for {witness_id}")
        artifacts.extend(set_artifacts)
    return artifacts


def verify_artifact_metadata(artifacts: list[dict[str, Any]]) -> None:
    """Verify artifact identity, hashes, sizes, languages, and passage markers."""
    artifact_ids = [item.get("artifact_id") for item in artifacts]
    if len(artifact_ids) != len(set(artifact_ids)):
        raise AssertionError("Duplicate artifact_id")
    if set(artifact_ids) != set(EXPECTED_ARTIFACT_HASHES):
        raise AssertionError("Unexpected or missing TEI artifact")

    urls: set[str] = set()
    for artifact in artifacts:
        artifact_id = artifact["artifact_id"]
        digest = artifact.get("sha256")
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            raise AssertionError(f"Invalid SHA-256 for {artifact_id}")
        if digest != EXPECTED_ARTIFACT_HASHES[artifact_id]:
            raise AssertionError(f"Pinned SHA-256 changed for {artifact_id}")
        if not isinstance(artifact.get("bytes"), int) or artifact["bytes"] <= 0:
            raise AssertionError(f"Invalid byte count for {artifact_id}")
        if artifact.get("language") not in {"Arabic", "Latin"}:
            raise AssertionError(f"Unexpected language for {artifact_id}")
        if artifact.get("passage_addressable") is not True:
            raise AssertionError(f"Passage addressing disabled for {artifact_id}")
        if artifact.get("page_break_count", 0) <= 0:
            raise AssertionError(f"No page markers for {artifact_id}")
        expected_primary, expected_secondary = EXPECTED_PAGE_BREAK_PROFILES[
            artifact_id
        ]
        if artifact.get("primary_edition_page_break_count") != expected_primary:
            raise AssertionError(f"Primary page-marker profile changed for {artifact_id}")
        if artifact.get("secondary_witness_page_breaks") != expected_secondary:
            raise AssertionError(
                f"Secondary page-marker profile changed for {artifact_id}"
            )
        expected_total = expected_primary + sum(expected_secondary.values())
        if artifact["page_break_count"] != expected_total:
            raise AssertionError(f"Total page-marker profile changed for {artifact_id}")
        division_profile = artifact.get("division_profile")
        if not isinstance(division_profile, dict) or not division_profile:
            raise AssertionError(f"Missing division profile for {artifact_id}")
        if any(not isinstance(count, int) or count <= 0 for count in division_profile.values()):
            raise AssertionError(f"Invalid division count for {artifact_id}")
        url = artifact.get("url")
        if not isinstance(url, str) or not url.startswith("https://"):
            raise AssertionError(f"Invalid artifact URL for {artifact_id}")
        if url in urls:
            raise AssertionError(f"Duplicate artifact URL: {url}")
        urls.add(url)


def verify_separation_contract(matrix: dict[str, Any]) -> None:
    """Enforce the work, author, translation, and publication boundaries."""
    if matrix.get("research_only") is not True:
        raise AssertionError("Research-only flag changed")
    if matrix.get("live_engine") is not False:
        raise AssertionError("Non-Western live-engine flag changed")
    if matrix.get("customer_output_eligible") is not False:
        raise AssertionError("Customer-output eligibility changed")

    witness_sets = {
        item["witness_set_id"]: item for item in matrix["witness_sets"]
    }
    great = witness_sets["abu_mashar_great_introduction_wurzburg_tei"]
    abbreviation = witness_sets["abu_mashar_abbreviation_wurzburg_tei"]
    qabisi = witness_sets["al_qabisi_introduction_wurzburg_tei"]

    if abbreviation["work_id"] not in great.get("do_not_merge_with_work_ids", []):
        raise AssertionError("Great Introduction no longer excludes the Abbreviation")
    if great["work_id"] not in abbreviation.get("do_not_merge_with_work_ids", []):
        raise AssertionError("Abbreviation no longer excludes the Great Introduction")
    if great["work_id"] not in qabisi.get("do_not_merge_with_work_ids", []):
        raise AssertionError("al-Qabisi pack no longer excludes Abu Ma'shar's Great Introduction")

    great_latin_translators = {
        item.get("translator")
        for item in great["artifacts"]
        if item.get("language") == "Latin"
    }
    if great_latin_translators != {"Hermann of Carinthia", "John of Seville"}:
        raise AssertionError("Great Introduction Latin lineages changed")

    controlling = matrix.get("controlling_editions", [])
    if len(controlling) != 3:
        raise AssertionError("Expected three controlling-edition gates")
    if any(item.get("rule_extraction_ready") is not False for item in controlling):
        raise AssertionError("A controlling edition was prematurely marked rule-ready")

    invariants = matrix.get("hard_invariants", [])
    required_phrases = (
        "different works",
        "separate Latin translation lineages",
        "cannot establish",
        "do not include the modern English translations",
        "never a generic Islamicate doctrine pack",
        "No artifact in this matrix is eligible for the live Western engine",
    )
    joined = "\n".join(invariants)
    for phrase in required_phrases:
        if phrase not in joined:
            raise AssertionError(f"Missing hard invariant containing: {phrase}")


def verify_registry_links(matrix: dict[str, Any], registry: dict[str, Any]) -> None:
    """Ensure every witness set points to an inspected registry source."""
    sources = registry.get("sources")
    if not isinstance(sources, list):
        raise AssertionError("Registry sources must be a list")
    by_id = {item.get("id"): item for item in sources}
    if len(by_id) != len(sources):
        raise AssertionError("Duplicate source registry ID")

    for witness_set in matrix["witness_sets"]:
        source_id = witness_set.get("source_registry_id")
        source = by_id.get(source_id)
        if source is None:
            raise AssertionError(f"Missing registry source: {source_id}")
        if source.get("status") != "full_text_inspected":
            raise AssertionError(f"Registry source is not full-text inspected: {source_id}")
        if "Wurzburg" not in source.get("repository", ""):
            raise AssertionError(f"Unexpected repository for {source_id}")

    controlling_ids = {item["source_id"] for item in matrix["controlling_editions"]}
    missing = controlling_ids - set(by_id)
    if missing:
        raise AssertionError(f"Missing controlling registry sources: {sorted(missing)}")


def verify_candidate_concordance(
    concordance: dict[str, Any],
    registry: dict[str, Any],
) -> tuple[int, int]:
    """Validate candidate-only boundaries, source links, and preserved variants."""
    boundary_values = {
        "research_only": True,
        "rule_manifest": False,
        "rule_extraction_ready": False,
        "live_engine": False,
        "customer_output_eligible": False,
    }
    for field, expected in boundary_values.items():
        if concordance.get(field) is not expected:
            raise AssertionError(f"Concordance boundary changed: {field}")
    if concordance.get("discovery_method", {}).get("quoted_text_stored") is not False:
        raise AssertionError("Concordance unexpectedly stores source quotations")

    registry_ids = {source["id"] for source in registry["sources"]}
    unknown_sources = set(concordance.get("source_registry_ids", [])) - registry_ids
    if unknown_sources:
        raise AssertionError(f"Unknown concordance sources: {sorted(unknown_sources)}")

    concepts = concordance.get("comparison_concepts")
    if not isinstance(concepts, list):
        raise AssertionError("comparison_concepts must be a list")
    concept_ids = [concept.get("concept_id") for concept in concepts]
    if len(concept_ids) != len(set(concept_ids)):
        raise AssertionError("Duplicate comparison concept")
    if set(concept_ids) != EXPECTED_CONCEPT_IDS:
        raise AssertionError("Comparison concept inventory changed")

    candidates = [
        candidate
        for concept in concepts
        for candidate in concept.get("candidates", [])
    ]
    if len(candidates) != 30:
        raise AssertionError("Candidate-passage inventory changed")
    for candidate in candidates:
        artifact_id = candidate.get("artifact_id")
        if artifact_id not in EXPECTED_ARTIFACT_HASHES:
            raise AssertionError(f"Unknown candidate artifact: {artifact_id}")
        status = candidate.get("status", "")
        if not (
            status.startswith("candidate_") or status.startswith("negative_scope_")
        ):
            raise AssertionError(f"Non-candidate status in concordance: {status}")
        if candidate.get("language") == "Latin" and not candidate.get("translator"):
            raise AssertionError(f"Latin candidate lacks translator: {artifact_id}")

    observations = concordance.get("variant_observations")
    if not isinstance(observations, list):
        raise AssertionError("variant_observations must be a list")
    observation_ids = [item.get("observation_id") for item in observations]
    if len(observation_ids) != len(set(observation_ids)):
        raise AssertionError("Duplicate variant observation")
    if set(observation_ids) != EXPECTED_VARIANT_IDS:
        raise AssertionError("Variant-observation inventory changed")
    if any(not item.get("engine_action") for item in observations):
        raise AssertionError("Variant observation lacks fail-closed engine action")

    firdaria = next(
        concept
        for concept in concepts
        if concept["concept_id"] == "firdaria_year_values"
    )
    arithmetic = {
        candidate["artifact_id"]: (
            sum(candidate["listed_values"].values()),
            candidate["stated_total"],
        )
        for candidate in firdaria["candidates"]
    }
    expected_arithmetic = {
        "abu_mashar_great_introduction_arabic_tei": (75, 75),
        "abu_mashar_great_introduction_hermann_latin_tei": (76, None),
        "abu_mashar_great_introduction_john_latin_tei": (74, 75),
        "al_qabisi_introduction_arabic_tei": (75, None),
        "al_qabisi_introduction_john_latin_tei": (75, None),
        "abu_mashar_abbreviation_arabic_tei": (75, 75),
        "abu_mashar_abbreviation_adelard_latin_tei": (75, 77),
    }
    if arithmetic != expected_arithmetic:
        raise AssertionError("Firdaria variant arithmetic changed")

    required_invariants = (
        "No candidate passage is a doctrinal rule.",
        "No Arabic token is translated by this concordance.",
        "Arithmetic disagreement is preserved as evidence and is never silently corrected.",
        "Only the Western engine is live; every item here remains research-only and customer-ineligible.",
    )
    invariants = set(concordance.get("hard_invariants", []))
    if not set(required_invariants) <= invariants:
        raise AssertionError("A concordance hard invariant is missing")
    return len(candidates), len(observations)


def verify_remote_artifacts(artifacts: list[dict[str, Any]]) -> int:
    """Download every TEI artifact and verify its current size and SHA-256."""
    for artifact in artifacts:
        request = urllib.request.Request(
            artifact["url"],
            headers={"User-Agent": "AstrologyResearchCorpusValidator/1.0"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read()
        digest = hashlib.sha256(payload).hexdigest()
        if len(payload) != artifact["bytes"]:
            raise AssertionError(
                f"Remote byte count changed for {artifact['artifact_id']}: "
                f"expected {artifact['bytes']}, got {len(payload)}"
            )
        if digest != artifact["sha256"]:
            raise AssertionError(
                f"Remote SHA-256 changed for {artifact['artifact_id']}: {digest}"
            )
    return len(artifacts)


def validate(*, verify_remote: bool = False) -> dict[str, Any]:
    """Validate local contracts and optionally re-fetch all pinned TEI artifacts."""
    matrix = load_json(MATRIX_PATH)
    concordance = load_json(CONCORDANCE_PATH)
    registry = load_json(REGISTRY_PATH)
    artifacts = flatten_artifacts(matrix)
    verify_artifact_metadata(artifacts)
    verify_separation_contract(matrix)
    verify_registry_links(matrix, registry)
    candidates_checked, observations_checked = verify_candidate_concordance(
        concordance,
        registry,
    )
    remote_verified = verify_remote_artifacts(artifacts) if verify_remote else 0
    return {
        "status": "pass",
        "witness_sets_checked": len(matrix["witness_sets"]),
        "artifacts_checked": len(artifacts),
        "remote_artifacts_verified": remote_verified,
        "candidate_passages_checked": candidates_checked,
        "variant_observations_checked": observations_checked,
        "rule_extraction_ready": False,
        "live_engine": matrix["live_engine"],
        "customer_output_eligible": matrix["customer_output_eligible"],
    }


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verify-remote",
        action="store_true",
        help="Re-download all seven TEI files and compare their pinned byte counts and hashes.",
    )
    args = parser.parse_args()
    print(json.dumps(validate(verify_remote=args.verify_remote), indent=2, sort_keys=True))
