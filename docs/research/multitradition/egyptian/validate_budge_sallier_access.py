"""Validate the research-only Budge/Sallier IV source-access artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
MULTITRADITION_ROOT = ROOT.parent
MANIFEST_PATH = ROOT / "budge_sallier_iv_access_manifest.json"
REGISTRY_PATH = MULTITRADITION_ROOT / "source_registry.json"
DEFAULT_LOCAL_PDF = (
    MULTITRADITION_ROOT.parent.parent.parent
    / "tmp"
    / "pdfs"
    / "egyptian_budge"
    / "budge_1923_second_series.pdf"
)


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object and reject non-object roots."""
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise AssertionError(f"Expected JSON object: {path}")
    return value


def sha256_file(path: Path) -> str:
    """Compute a streaming SHA-256 digest."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate(local_pdf: Path | None = None) -> dict[str, Any]:
    """Validate source identity, plate mapping, and fail-closed boundaries."""
    manifest = load_json(MANIFEST_PATH)
    registry = load_json(REGISTRY_PATH)
    source = next(
        entry
        for entry in registry["sources"]
        if entry["id"] == manifest["source_registry_id"]
    )
    publication = manifest["publication"]
    identity_pairs = (
        (source["file_sha256"], publication["sha256"]),
        (source["file_bytes"], publication["bytes"]),
        (source["pages"], publication["pdf_pages"]),
        (source["download_file"], publication["download_url"]),
    )
    if any(registry_value != manifest_value for registry_value, manifest_value in identity_pairs):
        raise AssertionError("Budge registry/manifest identity mismatch")

    facsimile = manifest["facsimile"]
    first = facsimile["plate_first"]
    last = facsimile["plate_last"]
    if first != {"roman": "LXXXVIII", "number": 88, "pdf_page": 231}:
        raise AssertionError("Unexpected first Sallier IV facsimile plate")
    if last != {"roman": "CXXVIII", "number": 128, "pdf_page": 311}:
        raise AssertionError("Unexpected last Sallier IV facsimile plate")
    expected_count = last["number"] - first["number"] + 1
    if facsimile["plate_count"] != expected_count or expected_count != 41:
        raise AssertionError("Sallier IV plate inventory is not contiguous")
    expected_last_page = first["pdf_page"] + facsimile["pdf_page_stride"] * (
        expected_count - 1
    )
    if expected_last_page != last["pdf_page"]:
        raise AssertionError("Sallier IV plate-to-PDF mapping changed")
    inspected = facsimile["inspected_plates"]
    if {(item["plate"], item["pdf_page"]) for item in inspected} != {
        ("LXXXVIII", 231),
        ("LXXXIX", 233),
        ("CXXVIII", 311),
    }:
        raise AssertionError("Visually inspected plate inventory changed")

    preservation = manifest["witness_description"]["preservation"]
    if preservation["epagomenal_absence_interpretation"] != "not_preserved_in_this_witness":
        raise AssertionError("Epagomenal loss was misrepresented as historical absence")
    if preservation["historical_absence_proven"] is not False:
        raise AssertionError("Historical epagomenal absence was asserted without evidence")
    boundaries = manifest["interpretive_boundaries"]
    prohibited_true = (
        "complete_file_read",
        "complete_translation_present",
        "rule_extraction_ready",
        "modern_critical_edition_collated",
        "hieratic_transcription_collated",
        "birth_statements_customer_eligible",
        "separate_witness_material_may_be_imported",
        "missing_text_may_be_filled_from_another_witness",
    )
    if any(boundaries[field] is not False for field in prohibited_true):
        raise AssertionError("Budge access artifact exceeded its evidence boundary")
    product = manifest["product_boundary"]
    if (
        product["live_engine"] is not False
        or product["customer_eligible"] is not False
        or product["reading_output"] is not False
        or product["historical_use_only"] is not True
    ):
        raise AssertionError("Budge access artifact crossed the product boundary")

    file_status = "not_checked"
    if local_pdf is not None:
        if not local_pdf.is_file():
            raise AssertionError(f"Local Budge PDF not found: {local_pdf}")
        if local_pdf.stat().st_size != publication["bytes"]:
            raise AssertionError("Local Budge PDF byte count changed")
        if sha256_file(local_pdf) != publication["sha256"]:
            raise AssertionError("Local Budge PDF hash changed")
        file_status = "hash_verified"

    return {
        "status": "pass",
        "source_registry_id": manifest["source_registry_id"],
        "pdf_pages": publication["pdf_pages"],
        "plates": facsimile["plate_count"],
        "visually_inspected_plates": len(inspected),
        "local_file": file_status,
        "rule_extraction_ready": boundaries["rule_extraction_ready"],
        "live_engine": product["live_engine"],
        "customer_eligible": product["customer_eligible"],
    }


def main() -> None:
    """Run the validator, checking the acquired PDF when it is present."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, help="Explicit acquired PDF to hash-check")
    parser.add_argument(
        "--manifest-only",
        action="store_true",
        help="Validate recorded metadata without requiring a local PDF",
    )
    args = parser.parse_args()
    if args.pdf is not None and args.manifest_only:
        parser.error("--pdf and --manifest-only are mutually exclusive")
    local_pdf = args.pdf
    if local_pdf is None and not args.manifest_only and DEFAULT_LOCAL_PDF.is_file():
        local_pdf = DEFAULT_LOCAL_PDF
    print(json.dumps(validate(local_pdf), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
