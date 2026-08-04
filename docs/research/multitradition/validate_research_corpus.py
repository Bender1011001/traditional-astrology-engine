from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import jsonschema


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"Expected a JSON object in {path}")
    return data


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _validate_schema(
    instance: dict[str, Any], schema: dict[str, Any], path: Path
) -> None:
    validator = jsonschema.Draft202012Validator(
        schema,
        format_checker=jsonschema.FormatChecker(),
    )
    errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.path))
    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.absolute_path) or "<root>"
        raise ValueError(f"Schema failure in {path} at {location}: {first.message}")


def _source_ids(vector_file: dict[str, Any]) -> list[str]:
    if "source_id" in vector_file:
        return [str(vector_file["source_id"])]
    return [str(source_id) for source_id in vector_file["source_ids"]]


def validate(root: Path) -> dict[str, Any]:
    root = root.resolve()
    all_json: dict[Path, dict[str, Any]] = {}
    for path in sorted(root.rglob("*.json")):
        all_json[path] = _read_json(path)

    rule_schema = all_json[root / "rule_manifest.schema.json"]
    vector_schema = all_json[root / "validation_vectors.schema.json"]
    corpus_schema = all_json[root / "babylonian" / "horoscope_corpus.schema.json"]
    birth_note_schema = all_json[root / "babylonian" / "birth_note_corpus.schema.json"]

    registry_path = root / "source_registry.json"
    registry = all_json[registry_path]
    sources = registry["sources"]
    source_ids = [str(source["id"]) for source in sources]
    duplicate_source_ids = sorted(
        source_id for source_id, count in Counter(source_ids).items() if count > 1
    )
    if duplicate_source_ids:
        raise ValueError(f"Duplicate source IDs: {duplicate_source_ids}")
    source_id_set = set(source_ids)
    allowed_statuses = set(registry["status_vocabulary"])
    unknown_statuses = sorted(
        {
            str(source["status"])
            for source in sources
            if source["status"] not in allowed_statuses
        }
    )
    if unknown_statuses:
        raise ValueError(f"Unknown source statuses: {unknown_statuses}")

    rule_manifests: dict[Path, dict[str, Any]] = {}
    rule_by_id: dict[str, dict[str, Any]] = {}
    rule_path_by_id: dict[str, Path] = {}
    source_packs: dict[str, set[str]] = {}
    for path, data in all_json.items():
        if not isinstance(data.get("rules"), list):
            continue
        _validate_schema(data, rule_schema, path)
        missing_manifest_sources = sorted(
            set(data["source_registry_ids"]) - source_id_set
        )
        if missing_manifest_sources:
            raise ValueError(
                f"Unknown rule-manifest source IDs in {_relative(path, root)}: "
                f"{missing_manifest_sources}"
            )
        rule_manifests[path] = data
        pack_id = str(data["source_pack_id"])
        source_packs.setdefault(pack_id, set()).add(str(data["tradition_id"]))
        for rule in data["rules"]:
            rule_id = str(rule["rule_id"])
            if rule_id in rule_by_id:
                earlier = _relative(rule_path_by_id[rule_id], root)
                raise ValueError(
                    f"Duplicate rule ID {rule_id!r} in {earlier} and "
                    f"{_relative(path, root)}"
                )
            rule_by_id[rule_id] = rule
            rule_path_by_id[rule_id] = path

    vector_files: dict[Path, dict[str, Any]] = {}
    vector_ids: set[str] = set()
    referenced_rule_ids: set[str] = set()
    for path in sorted(root.rglob("*validation_vectors.json")):
        data = all_json[path]
        _validate_schema(data, vector_schema, path)
        vector_files[path] = data
        pack_id = str(data["source_pack_id"])
        if pack_id not in source_packs:
            raise ValueError(
                f"Vector source pack {pack_id!r} in {_relative(path, root)} "
                "has no rule manifest"
            )
        if str(data["tradition_id"]) not in source_packs[pack_id]:
            raise ValueError(
                f"Tradition/source-pack mismatch in {_relative(path, root)}"
            )
        missing_sources = sorted(set(_source_ids(data)) - source_id_set)
        if missing_sources:
            raise ValueError(
                f"Unknown source IDs in {_relative(path, root)}: {missing_sources}"
            )
        for vector in data["vectors"]:
            vector_id = str(vector["vector_id"])
            if vector_id in vector_ids:
                raise ValueError(f"Duplicate vector ID: {vector_id}")
            vector_ids.add(vector_id)
            for rule_id in vector["rule_ids"]:
                if rule_id not in rule_by_id:
                    raise ValueError(
                        f"Vector {vector_id!r} references unknown rule {rule_id!r}"
                    )
                if rule_by_id[rule_id]["tradition_id"] != data["tradition_id"]:
                    raise ValueError(
                        f"Vector {vector_id!r} crosses traditions through {rule_id!r}"
                    )
                referenced_rule_ids.add(str(rule_id))

    unreferenced_rules = sorted(set(rule_by_id) - referenced_rule_ids)
    if unreferenced_rules:
        raise ValueError(
            "Rules without validation-vector coverage: " + ", ".join(unreferenced_rules)
        )

    corpus_path = root / "babylonian" / "rochberg_texts1_10_corpus_manifest.json"
    corpus = all_json[corpus_path]
    _validate_schema(corpus, corpus_schema, corpus_path)
    if corpus["tablet_count"] != 10 or corpus["record_count"] != 11:
        raise ValueError("Unexpected Rochberg Texts 1-10 tablet or record count")
    if len(corpus["records"]) != corpus["record_count"]:
        raise ValueError("Rochberg corpus record_count does not match records")
    explicit_judgments = [
        judgment
        for record in corpus["records"]
        for judgment in record["explicit_judgments"]
    ]
    if len(explicit_judgments) != 16:
        raise ValueError("Unexpected Rochberg Texts 1-10 explicit-judgment count")
    if any(judgment["customer_prediction"] for judgment in explicit_judgments):
        raise ValueError("A Babylonian corpus judgment enables customer prediction")

    corpus_11_20_path = (
        root / "babylonian" / "rochberg_texts11_20_corpus_manifest.json"
    )
    corpus_11_20 = all_json[corpus_11_20_path]
    _validate_schema(corpus_11_20, corpus_schema, corpus_11_20_path)
    if corpus_11_20["tablet_count"] != 10 or corpus_11_20["record_count"] != 11:
        raise ValueError("Unexpected Rochberg Texts 11-20 tablet or record count")
    if len(corpus_11_20["records"]) != corpus_11_20["record_count"]:
        raise ValueError("Rochberg Texts 11-20 record_count does not match records")
    judgments_11_20 = [
        judgment
        for record in corpus_11_20["records"]
        for judgment in record["explicit_judgments"]
    ]
    if len(judgments_11_20) != 3:
        raise ValueError("Unexpected Rochberg Texts 11-20 judgment-candidate count")
    if any(judgment["customer_prediction"] for judgment in judgments_11_20):
        raise ValueError("A Texts 11-20 judgment enables customer prediction")

    catalog_path = root / "babylonian" / "rochberg_full_corpus_catalog.json"
    catalog = all_json[catalog_path]
    catalog_expected = {
        "numbered_texts": 32,
        "horoscope_text_numbers": 28,
        "birth_note_text_numbers": 4,
        "birth_note_birth_records": 6,
        "horoscope_record_entries": 31,
        "explicit_duplicate_links": 1,
        "catalogued_horoscope_entries_after_explicit_duplicate_collapse": 30,
    }
    if catalog["summary"] != catalog_expected:
        raise ValueError("Unexpected Rochberg full-corpus catalog summary")
    if len(catalog["horoscope_records"]) != 31:
        raise ValueError("Rochberg full catalog does not contain 31 horoscope records")
    if len(catalog["birth_note_records"]) != 4:
        raise ValueError("Rochberg full catalog does not contain four birth notes")
    duplicate_links = [
        record for record in catalog["horoscope_records"] if record["duplicate_of"]
    ]
    if len(duplicate_links) != 1 or duplicate_links[0]["record_id"] != "rochberg1998.text11":
        raise ValueError("Rochberg explicit duplicate linkage changed")
    concordance_path = (
        root / "babylonian" / "rochberg_cdli_concordance.json"
    )
    concordance = all_json[concordance_path]
    concordance_records = concordance["records"]
    if [record["text_number"] for record in concordance_records] != list(range(1, 33)):
        raise ValueError("Rochberg/CDLI concordance no longer covers Texts 1-32 in order")
    catalog_designations: dict[int, str] = {}
    for record in catalog["horoscope_records"]:
        text_number = record["text_number"]
        museum_number = record["museum_number"]
        previous = catalog_designations.setdefault(text_number, museum_number)
        if previous != museum_number:
            raise ValueError("A multi-record Rochberg tablet changed museum designation")
    for record in catalog["birth_note_records"]:
        catalog_designations[record["text_number"]] = record["museum_number"]
    if any(
        record["edition_designation"]
        != catalog_designations[record["text_number"]]
        for record in concordance_records
    ):
        raise ValueError("Rochberg/CDLI concordance disagrees with edition catalog")
    exact_cdli_records = [
        record
        for record in concordance_records
        if record["match_status"] == "exact_verified"
    ]
    unresolved_cdli_records = [
        record
        for record in concordance_records
        if record["match_status"] == "not_found_in_exact_designation_search"
    ]
    if len(exact_cdli_records) != 30 or {
        record["text_number"] for record in unresolved_cdli_records
    } != {11, 16}:
        raise ValueError("Rochberg/CDLI verified or unresolved inventory changed")
    if any(
        record["cdli_rochberg_reference"] != record["text_number"]
        for record in exact_cdli_records
    ):
        raise ValueError("A CDLI record no longer cites the matching Rochberg number")
    cdli_ids = [record["cdli_id"] for record in exact_cdli_records]
    if len(cdli_ids) != len(set(cdli_ids)):
        raise ValueError("A CDLI identifier is assigned to multiple Rochberg tablets")
    cdli_summary = concordance["summary"]
    if (
        cdli_summary["cdli_pages_with_photo"] != 1
        or cdli_summary["cdli_pages_with_no_image_asset"] != 29
        or cdli_summary["cdli_pages_with_in_page_transliteration"] != 0
        or cdli_summary["cdli_pages_with_in_page_translation"] != 0
    ):
        raise ValueError("Rochberg/CDLI observed media or text availability changed")
    text27_concordance = concordance_records[26]
    if (
        text27_concordance["text_number"] != 27
        or text27_concordance.get("cdli_image_status")
        != "photo_thumbnail_present_and_visually_inspected"
    ):
        raise ValueError("Rochberg Text 27 image evidence changed")

    corpus_21_28_path = (
        root / "babylonian" / "rochberg_texts21_28_corpus_manifest.json"
    )
    corpus_21_28 = all_json[corpus_21_28_path]
    _validate_schema(corpus_21_28, corpus_schema, corpus_21_28_path)
    if corpus_21_28["tablet_count"] != 8 or corpus_21_28["record_count"] != 9:
        raise ValueError("Unexpected Rochberg Texts 21-28 tablet or record count")
    if len(corpus_21_28["records"]) != corpus_21_28["record_count"]:
        raise ValueError("Rochberg Texts 21-28 record_count does not match records")
    judgments_21_28 = [
        judgment
        for record in corpus_21_28["records"]
        for judgment in record["explicit_judgments"]
    ]
    if len(judgments_21_28) != 2:
        raise ValueError("Unexpected Rochberg Texts 21-28 judgment-candidate count")
    if any(judgment["customer_prediction"] for judgment in judgments_21_28):
        raise ValueError("A Texts 21-28 judgment enables customer prediction")

    birth_notes_path = (
        root / "babylonian" / "rochberg_birth_notes29_32_manifest.json"
    )
    birth_notes = all_json[birth_notes_path]
    _validate_schema(birth_notes, birth_note_schema, birth_notes_path)
    if birth_notes["tablet_count"] != 4 or birth_notes["birth_record_count"] != 6:
        raise ValueError("Unexpected Rochberg birth-note tablet or birth count")
    actual_birth_records = sum(
        len(tablet["birth_records"]) for tablet in birth_notes["tablets"]
    )
    if actual_birth_records != birth_notes["birth_record_count"]:
        raise ValueError("Rochberg birth-note count does not match records")
    text32 = next(tablet for tablet in birth_notes["tablets"] if tablet["text_number"] == 32)
    if len(text32["birth_records"]) != 3:
        raise ValueError("Rochberg Text 32 no longer preserves three birth notices")

    astronomy_path = root / "babylonian" / "rochberg_texts1_10_astronomy_spec.json"
    astronomy = all_json[astronomy_path]
    position_count = sum(
        len(case["published_adjusted_longitudes"]) for case in astronomy["cases"]
    )
    if position_count != 67:
        raise ValueError(f"Unexpected Rochberg astronomy position count: {position_count}")
    horizons_path = root / "babylonian" / "jpl_horizons_crosscheck_spec.json"
    horizons = all_json[horizons_path]
    if horizons["observed_summary"]["position_comparisons"] != position_count:
        raise ValueError("Horizons observed count does not match Rochberg position count")
    if horizons["live_drift_gates"]["position_comparisons"] != position_count:
        raise ValueError("Horizons drift-gate count does not match Rochberg position count")

    astronomy_11_27_path = (
        root / "babylonian" / "rochberg_texts11_27_astronomy_spec.json"
    )
    astronomy_11_27 = all_json[astronomy_11_27_path]
    position_count_11_27 = sum(
        len(case["published_adjusted_longitudes"])
        for case in astronomy_11_27["cases"]
    )
    if len(astronomy_11_27["cases"]) != 18 or position_count_11_27 != 125:
        raise ValueError("Unexpected Rochberg Texts 11-27 astronomy case/count")
    expected_11_27 = astronomy_11_27["expected_summary"]
    if expected_11_27["position_checks"] != position_count_11_27:
        raise ValueError("Texts 11-27 observed summary does not match target count")
    if expected_11_27["within_body_tolerance"] != 112:
        raise ValueError("Texts 11-27 documented residual inventory changed")
    if expected_11_27["text23_jan5_moon_residual_degrees"] >= 1.0:
        raise ValueError("Text 23 preceding-date diagnostic no longer improves the Moon")
    horizons_11_27_path = (
        root
        / "babylonian"
        / "jpl_horizons_texts11_27_crosscheck_spec.json"
    )
    horizons_11_27 = all_json[horizons_11_27_path]
    if (
        horizons_11_27["observed_summary"]["position_comparisons"]
        != position_count_11_27
    ):
        raise ValueError(
            "Texts 11-27 Horizons observed count does not match Rochberg positions"
        )
    if (
        horizons_11_27["live_drift_gates"]["position_comparisons"]
        != position_count_11_27
    ):
        raise ValueError(
            "Texts 11-27 Horizons drift-gate count does not match Rochberg positions"
        )
    if position_count + position_count_11_27 != 192:
        raise ValueError("Combined Rochberg/Horizons comparison inventory changed")

    text1_path = root / "babylonian" / "rochberg_text1_event_spec.json"
    text1 = all_json[text1_path]
    text1_events = text1["events"]
    text1_event_ids = [str(event["event_id"]) for event in text1_events]
    if len(text1_events) != 12:
        raise ValueError(f"Unexpected Rochberg Text 1 event count: {len(text1_events)}")
    if len(text1_event_ids) != len(set(text1_event_ids)):
        raise ValueError("Duplicate Rochberg Text 1 event IDs")
    if "none of Text 1's astronomical data refer to the date of birth" not in text1[
        "source_finding"
    ]:
        raise ValueError("Rochberg Text 1 is no longer explicitly kept out of natal use")
    if any(
        event.get("validation_policy", "").startswith("Generate")
        for event in text1_events
    ):
        raise ValueError("A Rochberg Text 1 uncertainty was promoted to generation")

    babylonian_judgment_manifest_names = {
        "rochberg_text10_rule_manifest.json",
        "rochberg_text16_judgment_rule_manifest.json",
        "rochberg_text27_judgment_rule_manifest.json",
        "rochberg_texts2_5_9_judgment_rule_manifest.json",
    }
    babylonian_judgment_rules = [
        rule
        for rule_id, rule in rule_by_id.items()
        if rule_path_by_id[rule_id].name in babylonian_judgment_manifest_names
    ]
    if len(babylonian_judgment_rules) != 21:
        raise ValueError(
            "The encoded Babylonian judgment/fragment count no longer matches the "
            "twenty-one clauses found through Text 28"
        )
    if any(rule["conclusion"].get("customer_prediction") for rule in babylonian_judgment_rules):
        raise ValueError("An encoded Babylonian judgment enables customer prediction")

    saa8_corpus_path = (
        root / "babylonian" / "saa8_lunar_eclipse_pilot_corpus.json"
    )
    saa8_corpus = all_json[saa8_corpus_path]
    if len(saa8_corpus["structured_sources"]) != 2:
        raise ValueError("SAA 8 eclipse pilot no longer has two structured witnesses")
    if len(saa8_corpus["passage_units"]) != 24:
        raise ValueError("SAA 8 eclipse pilot passage inventory changed")
    saa8_hashes = {
        source["artifact_id"]: source["tei_sha256_observed_2026_08_01"]
        for source in saa8_corpus["structured_sources"]
    }
    if saa8_hashes != {
        "P236933": "56c8b0569a0c92887ec5bbda0c72b07851b1aff7417d4b81c846f13e0c64487a",
        "P238143": "d838da15523dbbaa8451c56df8768e14feaef58753d2b30d643503310dc728e7",
    }:
        raise ValueError("SAA 8 structured-source hashes changed")
    saa8_manifest_names = {
        "saa8_535_lunar_eclipse_rule_manifest.json": 18,
        "saa8_316_applied_eclipse_rule_manifest.json": 15,
    }
    saa8_rules = [
        rule
        for rule_id, rule in rule_by_id.items()
        if rule_path_by_id[rule_id].name in saa8_manifest_names
    ]
    for manifest_name, expected_count in saa8_manifest_names.items():
        actual_count = sum(
            1
            for rule_id in rule_by_id
            if rule_path_by_id[rule_id].name == manifest_name
        )
        if actual_count != expected_count:
            raise ValueError(f"Unexpected SAA 8 rule count in {manifest_name}")
    if any(rule["domain"] == "natal" for rule in saa8_rules):
        raise ValueError("A SAA 8 state-eclipse rule was mislabeled natal")
    if any(rule["scope"].get("birth_input_eligible") is not False for rule in saa8_rules):
        raise ValueError("A SAA 8 eclipse rule no longer rejects birth input")
    if any(rule["conclusion"].get("customer_prediction") is not False for rule in saa8_rules):
        raise ValueError("A SAA 8 eclipse rule enables customer prediction")
    saa8_vectors_path = (
        root / "babylonian" / "saa8_lunar_eclipse_validation_vectors.json"
    )
    if len(all_json[saa8_vectors_path]["vectors"]) != 12:
        raise ValueError("SAA 8 eclipse validation-vector inventory changed")

    eae20_corpus_path = (
        root / "babylonian" / "eae20_canonical_witness_pilot_corpus.json"
    )
    eae20_corpus = all_json[eae20_corpus_path]
    if len(eae20_corpus["structured_sources"]) != 2:
        raise ValueError("EAE 20 witness pilot no longer has two structured sources")
    if len(eae20_corpus["passage_units"]) != 13:
        raise ValueError("EAE 20 witness pilot passage inventory changed")
    eae20_hashes = {
        source["artifact_id"]: source["retrieved_pdf_sha256"]
        for source in eae20_corpus["structured_sources"]
    }
    if eae20_hashes != {
        "IM 124485": "5bab54e46996419fc98c3423d3c2b69f1c4e7e4a15f598948ccc06ed79c7d72e",
        "VAT 9419 + VAT 11310, probably belonging with VAT 9740+": (
            "d15921dc93a848cd4f26adda674fd412e404850d638cc8496fd7af766971589e"
        ),
    }:
        raise ValueError("EAE 20 witness-source hashes changed")
    eae20_manifest_name = "eae20_witness_rule_manifest.json"
    eae20_rules = [
        rule
        for rule_id, rule in rule_by_id.items()
        if rule_path_by_id[rule_id].name == eae20_manifest_name
    ]
    if len(eae20_rules) != 17:
        raise ValueError("EAE 20 witness rule inventory changed")
    if any(rule["domain"] == "natal" for rule in eae20_rules):
        raise ValueError("An EAE 20 state-omen rule was mislabeled natal")
    if any(
        rule["scope"].get("birth_input_eligible") is not False
        for rule in eae20_rules
    ):
        raise ValueError("An EAE 20 witness rule no longer rejects birth input")
    if any(
        rule["conclusion"].get("customer_prediction") is not False
        for rule in eae20_rules
    ):
        raise ValueError("An EAE 20 witness rule enables customer prediction")
    eae20_vectors_path = (
        root / "babylonian" / "eae20_witness_validation_vectors.json"
    )
    if len(all_json[eae20_vectors_path]["vectors"]) != 11:
        raise ValueError("EAE 20 witness validation-vector inventory changed")

    eae_commentary_inventory_path = (
        root / "babylonian" / "eae15_22_edition_inventory.json"
    )
    eae_commentary_inventory = all_json[eae_commentary_inventory_path]
    if len(eae_commentary_inventory["later_updates"]) != 3:
        raise ValueError("EAE 15-22 critical-update inventory changed")
    if len(eae_commentary_inventory["open_ancient_commentaries"]) != 2:
        raise ValueError("EAE 15-22 open-commentary inventory changed")
    eae_commentary_corpus_path = (
        root / "babylonian" / "eae16_21_commentary_corpus.json"
    )
    eae_commentary_corpus = all_json[eae_commentary_corpus_path]
    if len(eae_commentary_corpus["structured_sources"]) != 2:
        raise ValueError("EAE commentary corpus no longer has two structured sources")
    if len(eae_commentary_corpus["passage_units"]) != 21:
        raise ValueError("EAE commentary passage inventory changed")
    eae_commentary_hashes = {
        source["artifact_id"]: source["structured_edition_sha256"]
        for source in eae_commentary_corpus["structured_sources"]
    }
    if eae_commentary_hashes != {
        "BM 47447 / P461229": (
            "a9330a5d48830886a3d5475476937818ceff52c8a576ca8cf2bc2da6e1f50ffc"
        ),
        "Sm.683 / P425538": (
            "d2f0c77ec23f793725f7ca71d6f1c4e3571bfb3fde7615d9b087662152765fbe"
        ),
    }:
        raise ValueError("EAE commentary structured-source hashes changed")
    eae_commentary_manifest_name = "eae16_21_commentary_rule_manifest.json"
    eae_commentary_rules = [
        rule
        for rule_id, rule in rule_by_id.items()
        if rule_path_by_id[rule_id].name == eae_commentary_manifest_name
    ]
    if len(eae_commentary_rules) != 22:
        raise ValueError("EAE commentary rule inventory changed")
    if any(rule["domain"] == "natal" for rule in eae_commentary_rules):
        raise ValueError("An EAE commentary rule was mislabeled natal")
    if any(
        rule["scope"].get("birth_input_eligible") is not False
        for rule in eae_commentary_rules
    ):
        raise ValueError("An EAE commentary rule no longer rejects birth input")
    if any(
        rule["conclusion"].get("customer_prediction") is not False
        for rule in eae_commentary_rules
    ):
        raise ValueError("An EAE commentary rule enables customer prediction")
    eae_commentary_vectors_path = (
        root / "babylonian" / "eae16_21_commentary_validation_vectors.json"
    )
    if len(all_json[eae_commentary_vectors_path]["vectors"]) != 14:
        raise ValueError("EAE commentary validation-vector inventory changed")

    maya_spec_path = root / "maya" / "calendar_kernel_spec.json"
    maya_spec = all_json[maya_spec_path]
    if maya_spec["source_pack_id"] != "maya_calendar_kernel_gmt_v1":
        raise ValueError("Maya calendar source-pack identity changed")
    acquired_maya_source = maya_spec["acquired_source"]
    if acquired_maya_source["sha256"] != (
        "a12c9e4d8716abdb1e06c05f93778b5ae7e6658614f94a47a157179a76f6e5fa"
    ):
        raise ValueError("Smithsonian Maya calendar PDF hash changed")
    if acquired_maya_source["bytes"] != 6851033 or acquired_maya_source["pages"] != 10:
        raise ValueError("Smithsonian Maya calendar PDF identity changed")
    maya_manifest_name = "calendar_rule_manifest.json"
    maya_rules = [
        rule
        for rule_id, rule in rule_by_id.items()
        if rule_path_by_id[rule_id].parent.name == "maya"
        and rule_path_by_id[rule_id].name == maya_manifest_name
    ]
    if len(maya_rules) != 8:
        raise ValueError("Maya calendar rule inventory changed")
    if any(rule["domain"] != "calendar" for rule in maya_rules):
        raise ValueError("A Maya calendar rule was assigned outside the calendar domain")
    if any(
        rule["scope"].get("birth_input_eligible") is not True
        or rule["scope"].get("interpretation_eligible") is not False
        for rule in maya_rules
    ):
        raise ValueError("A Maya calendar rule crossed the calendar/interpretation boundary")
    if any(
        rule["conclusion"].get("customer_prediction") is not False
        for rule in maya_rules
    ):
        raise ValueError("A Maya calendar rule enables customer prediction")
    maya_publication = maya_spec["publication_contract"]
    if (
        maya_publication["live_engine"] is not False
        or maya_publication["interpretation_eligible"] is not False
        or maya_publication["customer_prediction"] is not False
    ):
        raise ValueError("Maya calendar research pack crossed the live-product boundary")
    maya_vectors_path = root / "maya" / "calendar_validation_vectors.json"
    maya_vectors = all_json[maya_vectors_path]["vectors"]
    if len(maya_vectors) != 12:
        raise ValueError("Maya calendar validation-vector inventory changed")

    nahua_spec_path = root / "nahua" / "tonalpohualli_cycle_spec.json"
    nahua_spec = all_json[nahua_spec_path]
    nahua_signs = nahua_spec["cycle"]["day_signs"]
    if len(nahua_signs) != 20 or [sign["index"] for sign in nahua_signs] != list(
        range(20)
    ):
        raise ValueError("Nahua day-sign inventory changed")
    if (
        nahua_spec["cycle"]["joint_period_days"] != 260
        or nahua_spec["cycle"]["trecena_length_days"] != 13
        or nahua_spec["cycle"]["trecenas_per_cycle"] != 20
    ):
        raise ValueError("Nahua tonalpohualli cycle dimensions changed")
    if nahua_spec["epoch_contract"]["default_epoch"] is not None:
        raise ValueError("A default Nahua civil-date epoch was introduced")
    nahua_boundary = nahua_spec["product_boundary"]
    if (
        nahua_boundary["live_engine"] is not False
        or nahua_boundary["customer_eligible"] is not False
        or nahua_boundary["birth_reading_enabled"] is not False
        or nahua_boundary["correlation_ready"] is not False
        or nahua_boundary["interpretation_ready"] is not False
    ):
        raise ValueError("Nahua research arithmetic crossed its product boundary")
    nahua_rules = [
        rule
        for rule_id, rule in rule_by_id.items()
        if rule_path_by_id[rule_id].parent.name == "nahua"
        and rule_path_by_id[rule_id].name == "calendar_rule_manifest.json"
    ]
    if len(nahua_rules) != 8 or any(
        rule["domain"] != "calendar" for rule in nahua_rules
    ):
        raise ValueError("Nahua calendar rule inventory changed")
    if any(
        rule["conclusion"].get("customer_prediction") is not False
        for rule in nahua_rules
    ):
        raise ValueError("A Nahua calendar rule enables customer prediction")
    nahua_vectors_path = root / "nahua" / "calendar_validation_vectors.json"
    nahua_vectors = all_json[nahua_vectors_path]["vectors"]
    if len(nahua_vectors) != 12:
        raise ValueError("Nahua calendar validation-vector inventory changed")

    bazi_spec_path = root / "bazi" / "sexagenary_kernel_spec.json"
    bazi_spec = all_json[bazi_spec_path]
    bazi_cycle = bazi_spec["cycle"]
    if (
        bazi_cycle["stem_count"] != 10
        or bazi_cycle["branch_count"] != 12
        or bazi_cycle["joint_period"] != 60
        or len(bazi_cycle["stems"]) != 10
        or len(bazi_cycle["branches"]) != 12
    ):
        raise ValueError("BaZi sexagenary cycle dimensions changed")
    if bazi_spec["anchor_contract"]["default_anchor"] is not None:
        raise ValueError("A default BaZi day-count anchor was introduced")
    if bazi_spec["convention_contract"]["default_profile"] is not None:
        raise ValueError("A default BaZi boundary convention was introduced")
    bazi_boundary = bazi_spec["product_boundary"]
    if (
        bazi_boundary["live_engine"] is not False
        or bazi_boundary["customer_eligible"] is not False
        or bazi_boundary["birth_reading_enabled"] is not False
        or bazi_boundary["anchor_ready"] is not False
        or bazi_boundary["convention_ready"] is not False
        or bazi_boundary["interpretation_ready"] is not False
    ):
        raise ValueError("BaZi research arithmetic crossed its product boundary")
    bazi_rules = [
        rule
        for rule_id, rule in rule_by_id.items()
        if rule_path_by_id[rule_id].parent.name == "bazi"
        and rule_path_by_id[rule_id].name == "sexagenary_rule_manifest.json"
    ]
    if len(bazi_rules) != 10 or any(
        rule["domain"] != "calendar" for rule in bazi_rules
    ):
        raise ValueError("BaZi sexagenary rule inventory changed")
    if any(
        rule["conclusion"].get("customer_prediction") is not False
        for rule in bazi_rules
    ):
        raise ValueError("A BaZi sexagenary rule enables customer prediction")
    bazi_vectors_path = root / "bazi" / "sexagenary_validation_vectors.json"
    bazi_vectors = all_json[bazi_vectors_path]["vectors"]
    if len(bazi_vectors) != 20:
        raise ValueError("BaZi sexagenary validation-vector inventory changed")

    egyptian_spec_path = root / "egyptian" / "civil_calendar_spec.json"
    egyptian_spec = all_json[egyptian_spec_path]
    egyptian_model = egyptian_spec["calendar_model"]
    if (
        egyptian_model["year_length_days"] != 365
        or egyptian_model["ordinary_months"] != 12
        or egyptian_model["ordinary_month_length_days"] != 30
        or egyptian_model["ordinary_days"] != 360
        or egyptian_model["additional_days"] != 5
        or egyptian_model["intercalation"] is not False
    ):
        raise ValueError("Egyptian civil-calendar dimensions changed")
    if [season["id"] for season in egyptian_model["seasons"]] != [
        "akhet",
        "peret",
        "shemu",
    ]:
        raise ValueError("Egyptian civil-calendar season order changed")
    if egyptian_spec["chronology_contract"]["default_profile"] is not None:
        raise ValueError("A default Egyptian chronology was introduced")
    egyptian_boundary = egyptian_spec["product_boundary"]
    if (
        egyptian_boundary["live_engine"] is not False
        or egyptian_boundary["customer_eligible"] is not False
        or egyptian_boundary["birth_reading_enabled"] is not False
        or egyptian_boundary["chronology_ready"] is not False
        or egyptian_boundary["hemerology_ready"] is not False
    ):
        raise ValueError("Egyptian calendar research crossed its product boundary")
    egyptian_rules = [
        rule
        for rule_id, rule in rule_by_id.items()
        if rule_path_by_id[rule_id].parent.name == "egyptian"
        and rule_path_by_id[rule_id].name == "civil_calendar_rule_manifest.json"
    ]
    if len(egyptian_rules) != 11 or any(
        rule["domain"] != "calendar" for rule in egyptian_rules
    ):
        raise ValueError("Egyptian civil-calendar rule inventory changed")
    if any(
        rule["conclusion"].get("customer_prediction") is not False
        for rule in egyptian_rules
    ):
        raise ValueError("An Egyptian calendar rule enables customer prediction")
    egyptian_vectors_path = (
        root / "egyptian" / "civil_calendar_validation_vectors.json"
    )
    egyptian_vectors = all_json[egyptian_vectors_path]["vectors"]
    if len(egyptian_vectors) != 17:
        raise ValueError("Egyptian civil-calendar vector inventory changed")
    egyptian_budge_path = (
        root / "egyptian" / "budge_sallier_iv_access_manifest.json"
    )
    egyptian_budge = all_json[egyptian_budge_path]
    egyptian_budge_publication = egyptian_budge["publication"]
    egyptian_budge_preservation = egyptian_budge["witness_description"][
        "preservation"
    ]
    egyptian_budge_boundary = egyptian_budge["product_boundary"]
    if (
        egyptian_budge_publication["sha256"]
        != "084058ed3a69936bcc56e1d96e1be0541a1f18f4d645e16dd1b9fec1a980f419"
        or egyptian_budge_publication["bytes"] != 152147349
        or egyptian_budge_publication["pdf_pages"] != 317
        or egyptian_budge["facsimile"]["plate_count"] != 41
    ):
        raise ValueError("Budge/Sallier IV source identity or plate span changed")
    if (
        egyptian_budge_preservation["epagomenal_absence_interpretation"]
        != "not_preserved_in_this_witness"
        or egyptian_budge_preservation["historical_absence_proven"] is not False
    ):
        raise ValueError("Sallier IV loss became a historical absence claim")
    if (
        egyptian_budge_boundary["live_engine"] is not False
        or egyptian_budge_boundary["customer_eligible"] is not False
        or egyptian_budge_boundary["reading_output"] is not False
    ):
        raise ValueError("Budge/Sallier IV source artifact crossed product boundary")

    phugpa_spec_path = root / "tibetan" / "phugpa_calendar_spec.json"
    phugpa_spec = all_json[phugpa_spec_path]
    if phugpa_spec["source_pack_id"] != "tibetan_phugpa_calendar_janson2014_v1":
        raise ValueError("Phugpa calendar source-pack identity changed")
    phugpa_source = phugpa_spec["acquired_source"]
    if phugpa_source["pdf_sha256"] != (
        "7cafc7df563a3020849c86f4e397daa18b7f7f5ff46244403180aca90b9d0f77"
    ):
        raise ValueError("Janson Tibetan calendar PDF hash changed")
    if phugpa_source["tex_sha256"] != (
        "edf45d3a0978a92cd3eff2482bfd258a4168424f4cfd24f9ead5a24c733a4a4b"
    ):
        raise ValueError("Janson Tibetan calendar TeX hash changed")
    phugpa_rules = [
        rule
        for rule_id, rule in rule_by_id.items()
        if rule_path_by_id[rule_id].parent.name == "tibetan"
        and rule_path_by_id[rule_id].name == "phugpa_calendar_rule_manifest.json"
    ]
    if len(phugpa_rules) != 10:
        raise ValueError("Phugpa calendar rule inventory changed")
    if any(rule["domain"] != "calendar" for rule in phugpa_rules):
        raise ValueError("A Phugpa calendar rule escaped the calendar domain")
    if any(
        rule["scope"].get("birth_input_eligible") is not True
        or rule["scope"].get("interpretation_eligible") is not False
        for rule in phugpa_rules
    ):
        raise ValueError("A Phugpa rule crossed the calendar/interpretation boundary")
    if any(
        rule["conclusion"].get("customer_prediction") is not False
        for rule in phugpa_rules
    ):
        raise ValueError("A Phugpa calendar rule enables customer prediction")
    phugpa_publication = phugpa_spec["publication_contract"]
    if (
        phugpa_publication["live_engine"] is not False
        or phugpa_publication["institutional_conformance"] is not False
        or phugpa_publication["interpretation_eligible"] is not False
        or phugpa_publication["customer_prediction"] is not False
    ):
        raise ValueError("Phugpa research pack crossed its product boundary")
    phugpa_vectors_path = (
        root / "tibetan" / "phugpa_calendar_validation_vectors.json"
    )
    phugpa_vectors = all_json[phugpa_vectors_path]["vectors"]
    if len(phugpa_vectors) != 10:
        raise ValueError("Phugpa calendar validation-vector inventory changed")

    al_biruni_spec_path = (
        root / "islamicate" / "al_biruni_reference_condition_spec.json"
    )
    al_biruni_spec = all_json[al_biruni_spec_path]
    if (
        al_biruni_spec["source_pack_id"]
        != "islamicate_al_biruni_tafhim_reference_conditions_v1"
    ):
        raise ValueError("Al-Biruni source-pack identity changed")
    full_edition = al_biruni_spec["sources"]["institutional_full_edition"]
    if full_edition["mets_sha256"] != (
        "9f6202f26f7f342d02f2374152f9f31c4e2dac435e28656fb8da176c8c4c0f1d"
    ):
        raise ValueError("Al-Biruni Halle METS hash changed")
    if full_edition["iiif_manifest_sha256"] != (
        "c28e88e610bf9fb788c3239aa649ff18862b7241df8a76c8fdfa4cd79960a408"
    ):
        raise ValueError("Al-Biruni Halle IIIF manifest hash changed")
    local_extract = al_biruni_spec["sources"]["english_astrology_extract"]
    if local_extract["pdf_sha256"] != (
        "b5b15d3a25842072d680dd6e6d341c992bff0c2a43141d36b47e6a7e2cc761d2"
    ):
        raise ValueError("Al-Biruni local astrology-extract PDF hash changed")
    if len(al_biruni_spec["facing_page_evidence"]) != 6:
        raise ValueError("Al-Biruni facing-page evidence inventory changed")
    al_biruni_rules = [
        rule
        for rule_id, rule in rule_by_id.items()
        if rule_path_by_id[rule_id].parent.name == "islamicate"
        and rule_path_by_id[rule_id].name
        == "al_biruni_reference_condition_rule_manifest.json"
    ]
    if len(al_biruni_rules) != 15:
        raise ValueError("Al-Biruni reference-condition rule inventory changed")
    if any(
        rule["scope"].get("interpretation_eligible") is not False
        for rule in al_biruni_rules
    ):
        raise ValueError("An Al-Biruni rule crossed the interpretation boundary")
    if any(
        rule["conclusion"].get("customer_prediction") is not False
        for rule in al_biruni_rules
    ):
        raise ValueError("An Al-Biruni rule enables customer prediction")
    al_biruni_publication = al_biruni_spec["publication_contract"]
    if (
        al_biruni_publication["live_engine"] is not False
        or al_biruni_publication["customer_eligible"] is not False
        or al_biruni_publication["interpretation_eligible"] is not False
        or al_biruni_publication["full_reading_eligible"] is not False
        or al_biruni_publication["arabic_specialist_review_complete"] is not False
    ):
        raise ValueError("Al-Biruni research pack crossed its publication boundary")
    al_biruni_vectors_path = (
        root
        / "islamicate"
        / "al_biruni_reference_condition_validation_vectors.json"
    )
    al_biruni_vectors = all_json[al_biruni_vectors_path]["vectors"]
    if len(al_biruni_vectors) != 13:
        raise ValueError("Al-Biruni validation-vector inventory changed")

    islamicate_access_path = (
        root / "islamicate" / "abu_mashar_al_qabisi_access_matrix.json"
    )
    islamicate_access = all_json[islamicate_access_path]
    if (
        islamicate_access["research_only"] is not True
        or islamicate_access["live_engine"] is not False
        or islamicate_access["customer_output_eligible"] is not False
    ):
        raise ValueError("Abu Ma'shar/al-Qabisi access gate crossed its product boundary")
    access_witness_sets = islamicate_access["witness_sets"]
    if len(access_witness_sets) != 3:
        raise ValueError("Abu Ma'shar/al-Qabisi witness-set inventory changed")
    access_artifacts = [
        artifact
        for witness_set in access_witness_sets
        for artifact in witness_set["artifacts"]
    ]
    if len(access_artifacts) != 7:
        raise ValueError("Abu Ma'shar/al-Qabisi TEI artifact inventory changed")
    access_registry_ids = {
        witness_set["source_registry_id"] for witness_set in access_witness_sets
    }
    if not access_registry_ids <= source_id_set:
        raise ValueError(
            "Unknown Abu Ma'shar/al-Qabisi access source IDs: "
            f"{sorted(access_registry_ids - source_id_set)}"
        )
    if any(
        source["status"] != "full_text_inspected"
        for source in sources
        if source["id"] in access_registry_ids
    ):
        raise ValueError("An Islamicate TEI source lost full-text-inspected status")
    if any(
        edition["rule_extraction_ready"] is not False
        for edition in islamicate_access["controlling_editions"]
    ):
        raise ValueError("An Islamicate controlling edition became prematurely rule-ready")

    islamicate_concordance_path = (
        root
        / "islamicate"
        / "al_biruni_abu_mashar_al_qabisi_candidate_concordance.json"
    )
    islamicate_concordance = all_json[islamicate_concordance_path]
    if (
        islamicate_concordance["research_only"] is not True
        or islamicate_concordance["rule_manifest"] is not False
        or islamicate_concordance["rule_extraction_ready"] is not False
        or islamicate_concordance["live_engine"] is not False
        or islamicate_concordance["customer_output_eligible"] is not False
    ):
        raise ValueError("Islamicate candidate concordance crossed its product boundary")
    unknown_concordance_sources = (
        set(islamicate_concordance["source_registry_ids"]) - source_id_set
    )
    if unknown_concordance_sources:
        raise ValueError(
            "Unknown Islamicate concordance source IDs: "
            f"{sorted(unknown_concordance_sources)}"
        )
    islamicate_comparison_concepts = islamicate_concordance["comparison_concepts"]
    islamicate_candidate_passages = [
        candidate
        for concept in islamicate_comparison_concepts
        for candidate in concept["candidates"]
    ]
    islamicate_variant_observations = islamicate_concordance[
        "variant_observations"
    ]
    if len(islamicate_comparison_concepts) != 5:
        raise ValueError("Islamicate comparison-concept inventory changed")
    if len(islamicate_candidate_passages) != 30:
        raise ValueError("Islamicate candidate-passage inventory changed")
    if len(islamicate_variant_observations) != 8:
        raise ValueError("Islamicate variant-observation inventory changed")

    # Defensibility specs: every tradition with a reading section must publish
    # the six-part spec that governs what its reading may and may not claim.
    defensibility_standard = root / "DEFENSIBILITY.md"
    if not defensibility_standard.is_file():
        raise ValueError("DEFENSIBILITY.md standard is missing")
    required_spec_sections = (
        "## Core-technique checklist",
        "## Judgment hierarchy",
        "## Worked-example inventory",
        "## Refusal list",
        "## Conventions requiring disclosure",
        "## Current implementation gap",
    )
    defensibility_tracks = (
        "jyotisha",
        "bazi",
        "islamicate",
        "medieval_jewish",
        "maya",
        "nahua",
        "babylonian",
    )
    defensibility_specs: dict[str, int] = {}
    for track in defensibility_tracks:
        spec_path = root / track / "defensibility_spec.md"
        if not spec_path.is_file():
            raise ValueError(f"Missing defensibility spec: {track}")
        text = spec_path.read_text(encoding="utf-8")
        missing_sections = [s for s in required_spec_sections if s not in text]
        if missing_sections:
            raise ValueError(
                f"Defensibility spec {track} missing sections: {missing_sections}"
            )
        # Every checklist row must carry a recognised status. An unlabelled row
        # would silently vanish from the ceiling report.
        if "## Core-technique checklist" in text:
            checklist = text.split("## Core-technique checklist", 1)[1]
            checklist = checklist.split("\n## ", 1)[0]
            data_rows = [
                line
                for line in checklist.splitlines()
                if line.startswith("|") and not set(line) <= set("|- ")
            ]
            # Drop the header row.
            data_rows = [r for r in data_rows if not r.lstrip("| ").startswith("#")]
            unlabelled = [
                row
                for row in data_rows
                if not any(
                    f"`{s}`" in row.lower()
                    for s in ("implemented", "computable", "source_gated", "refused")
                )
            ]
            if unlabelled:
                raise ValueError(
                    f"Defensibility spec {track} has checklist rows with no "
                    f"status token: {unlabelled[:2]}"
                )
        if "## Refusal list" in text:
            refusal_block = text.split("## Refusal list", 1)[1]
            refusal_block = refusal_block.split("\n## ", 1)[0]
            if refusal_block.count("- ") < 3:
                raise ValueError(
                    f"Defensibility spec {track} lists fewer than three refusals"
                )
        defensibility_specs[track] = len(text.splitlines())

    # Ceiling gate: no tradition may carry a `computable` checklist item.
    # `computable` means "our gap, and actionable" - so a spec claiming one is a
    # spec admitting the reading is below what its own sources permit. Items
    # that are source_gated or refused are facts about the corpus and are fine.
    from importlib import util as _import_util

    ceiling_module_path = root / "ceiling_report.py"
    ceiling_spec = _import_util.spec_from_file_location(
        "ceiling_report", ceiling_module_path
    )
    if ceiling_spec is None or ceiling_spec.loader is None:
        raise ValueError("Cannot load ceiling_report.py")
    ceiling_module = _import_util.module_from_spec(ceiling_spec)
    ceiling_spec.loader.exec_module(ceiling_module)
    ceiling = ceiling_module.build()
    below = ceiling["summary"]["below_ceiling"]
    if below:
        gaps = {
            track: ceiling["traditions"][track]["actionable_gaps"] for track in below
        }
        raise ValueError(
            f"Traditions below their source ceiling (actionable gaps remain): {gaps}"
        )

    # Worked-example suites: the defensibility standard's requirement 4. Every
    # suite must validate against its schema, and every claim marked comparable
    # must actually pass against the engine.
    worked_example_paths = sorted(root.rglob("worked_examples.json"))
    if not worked_example_paths:
        raise ValueError("No worked-example suites found")
    worked_schema = all_json[root / "worked_examples.schema.json"]
    worked_example_counts: dict[str, int] = {}
    for path in worked_example_paths:
        suite = all_json[path]
        _validate_schema(suite, worked_schema, path)
        if suite["tradition_id"] not in {
            str(source.get("tradition")) for source in sources
        } | {"maya", "indian_jyotisha"}:
            raise ValueError(f"Unknown worked-example tradition in {path.name}")
        missing_worked_sources = sorted(
            set(suite["source_registry_ids"]) - source_id_set
        )
        if missing_worked_sources:
            raise ValueError(
                f"Unknown worked-example source IDs in {_relative(path, root)}: "
                f"{missing_worked_sources}"
            )
        worked_example_counts[path.parent.name] = len(suite["examples"])

    coverage_manifest_path = root / "engine_coverage_manifest.json"
    coverage_manifest = all_json[coverage_manifest_path]
    coverage_schema = all_json[root / "engine_coverage_manifest.schema.json"]
    _validate_schema(coverage_manifest, coverage_schema, coverage_manifest_path)
    coverage_boundary = coverage_manifest["global_product_boundary"]
    if (
        coverage_boundary["western_engine_live"] is not True
        or coverage_boundary["nonwestern_live_engines"] != []
        or coverage_boundary["nonwestern_customer_eligible_modules"] != []
        or coverage_boundary["prose_may_invent_missing_rules"] is not False
        or coverage_boundary["missing_modules_must_be_reported"] is not True
    ):
        raise ValueError("Global engine-coverage product boundary changed")
    coverage_tracks = coverage_manifest["tracks"]
    coverage_modules = [
        module for track in coverage_tracks for module in track["modules"]
    ]
    coverage_status_counts = Counter(
        module["coverage_status"] for module in coverage_modules
    )
    if len(coverage_tracks) != 27 or len(coverage_modules) != 93:
        raise ValueError("Global engine coverage inventory changed")
    if coverage_status_counts != Counter(
        {"research_verified": 35, "source_limited": 55, "not_implemented": 3}
    ):
        raise ValueError("Global engine coverage status counts changed")
    if any(
        track["live_engine"] is not False
        or track["customer_eligible"] is not False
        for track in coverage_tracks
    ):
        raise ValueError("A non-Western coverage track crossed its product boundary")

    return {
        "status": "pass",
        "root": str(root),
        "sources": len(source_ids),
        "rule_manifests": len(rule_manifests),
        "rules": len(rule_by_id),
        "validation_vector_files": len(vector_files),
        "validation_vectors": len(vector_ids),
        "rules_with_vector_coverage": len(referenced_rule_ids),
        "babylonian_corpus_tablets": corpus["tablet_count"],
        "babylonian_corpus_records": corpus["record_count"],
        "babylonian_explicit_judgments": len(explicit_judgments),
        "babylonian_texts11_20_records": corpus_11_20["record_count"],
        "babylonian_texts11_20_judgment_candidates": len(judgments_11_20),
        "babylonian_source_clause_candidates_through_text20": (
            len(explicit_judgments) + len(judgments_11_20)
        ),
        "babylonian_texts21_28_records": corpus_21_28["record_count"],
        "babylonian_texts21_28_judgment_candidates": len(judgments_21_28),
        "babylonian_source_clause_candidates_through_text28": (
            len(explicit_judgments) + len(judgments_11_20) + len(judgments_21_28)
        ),
        "babylonian_birth_note_tablets": birth_notes["tablet_count"],
        "babylonian_birth_note_birth_records": actual_birth_records,
        "babylonian_full_catalog_horoscope_records": len(catalog["horoscope_records"]),
        "babylonian_full_catalog_birth_notes": len(catalog["birth_note_records"]),
        "babylonian_cdli_exact_tablet_matches": len(exact_cdli_records),
        "babylonian_cdli_unresolved_tablets": len(unresolved_cdli_records),
        "babylonian_astronomy_positions": position_count,
        "babylonian_texts11_27_astronomy_positions": position_count_11_27,
        "babylonian_all_recomputed_astronomy_positions": (
            position_count + position_count_11_27
        ),
        "babylonian_horizons_crosschecked_positions": (
            horizons["observed_summary"]["position_comparisons"]
            + horizons_11_27["observed_summary"]["position_comparisons"]
        ),
        "babylonian_text1_event_records": len(text1_events),
        "babylonian_saa8_eclipse_structured_sources": len(
            saa8_corpus["structured_sources"]
        ),
        "babylonian_saa8_eclipse_passage_units": len(saa8_corpus["passage_units"]),
        "babylonian_saa8_eclipse_rules": len(saa8_rules),
        "babylonian_saa8_eclipse_vectors": len(
            all_json[saa8_vectors_path]["vectors"]
        ),
        "babylonian_eae20_structured_sources": len(
            eae20_corpus["structured_sources"]
        ),
        "babylonian_eae20_passage_units": len(eae20_corpus["passage_units"]),
        "babylonian_eae20_rules": len(eae20_rules),
        "babylonian_eae20_vectors": len(
            all_json[eae20_vectors_path]["vectors"]
        ),
        "babylonian_eae15_22_later_critical_updates": len(
            eae_commentary_inventory["later_updates"]
        ),
        "babylonian_eae_commentary_structured_sources": len(
            eae_commentary_corpus["structured_sources"]
        ),
        "babylonian_eae_commentary_passage_units": len(
            eae_commentary_corpus["passage_units"]
        ),
        "babylonian_eae_commentary_rules": len(eae_commentary_rules),
        "babylonian_eae_commentary_vectors": len(
            all_json[eae_commentary_vectors_path]["vectors"]
        ),
        "maya_calendar_rules": len(maya_rules),
        "maya_calendar_vectors": len(maya_vectors),
        "maya_calendar_correlation_profiles": len(maya_spec["correlations"]),
        "maya_calendar_live_engine": maya_publication["live_engine"],
        "maya_calendar_interpretation_eligible": maya_publication[
            "interpretation_eligible"
        ],
        "nahua_tonalpohualli_rules": len(nahua_rules),
        "nahua_tonalpohualli_vectors": len(nahua_vectors),
        "nahua_tonalpohualli_day_signs": len(nahua_signs),
        "nahua_tonalpohualli_joint_period_days": nahua_spec["cycle"][
            "joint_period_days"
        ],
        "nahua_tonalpohualli_default_epoch": nahua_spec["epoch_contract"][
            "default_epoch"
        ],
        "nahua_tonalpohualli_live_engine": nahua_boundary["live_engine"],
        "nahua_tonalpohualli_customer_eligible": nahua_boundary[
            "customer_eligible"
        ],
        "worked_example_suites": len(worked_example_paths),
        "worked_examples_by_tradition": worked_example_counts,
        "defensibility_specs": len(defensibility_specs),
        "traditions_at_source_ceiling": len(
            ceiling["summary"]["at_source_ceiling"]
        ),
        "actionable_gaps_remaining": ceiling["summary"]["total_actionable_gaps"],
        "defensibility_spec_tracks": sorted(defensibility_specs),
        "bazi_sexagenary_rules": len(bazi_rules),
        "bazi_sexagenary_vectors": len(bazi_vectors),
        "bazi_sexagenary_joint_period": bazi_cycle["joint_period"],
        "bazi_sexagenary_default_anchor": bazi_spec["anchor_contract"][
            "default_anchor"
        ],
        "bazi_sexagenary_live_engine": bazi_boundary["live_engine"],
        "bazi_sexagenary_customer_eligible": bazi_boundary[
            "customer_eligible"
        ],
        "egyptian_civil_calendar_rules": len(egyptian_rules),
        "egyptian_civil_calendar_vectors": len(egyptian_vectors),
        "egyptian_civil_calendar_year_days": egyptian_model[
            "year_length_days"
        ],
        "egyptian_civil_calendar_default_profile": egyptian_spec[
            "chronology_contract"
        ]["default_profile"],
        "egyptian_civil_calendar_live_engine": egyptian_boundary["live_engine"],
        "egyptian_civil_calendar_customer_eligible": egyptian_boundary[
            "customer_eligible"
        ],
        "egyptian_budge_sallier_pdf_pages": egyptian_budge_publication[
            "pdf_pages"
        ],
        "egyptian_budge_sallier_plates": egyptian_budge["facsimile"][
            "plate_count"
        ],
        "egyptian_budge_sallier_rule_extraction_ready": egyptian_budge[
            "interpretive_boundaries"
        ]["rule_extraction_ready"],
        "tibetan_phugpa_calendar_rules": len(phugpa_rules),
        "tibetan_phugpa_calendar_vectors": len(phugpa_vectors),
        "tibetan_phugpa_epoch_profiles": len(phugpa_spec["epoch_profiles"]),
        "tibetan_phugpa_live_engine": phugpa_publication["live_engine"],
        "tibetan_phugpa_institutional_conformance": phugpa_publication[
            "institutional_conformance"
        ],
        "islamicate_al_biruni_rules": len(al_biruni_rules),
        "islamicate_al_biruni_vectors": len(al_biruni_vectors),
        "islamicate_al_biruni_facing_page_pairs": len(
            al_biruni_spec["facing_page_evidence"]
        ),
        "islamicate_al_biruni_source_language_translation_verified": (
            al_biruni_spec["lineage_contract"][
                "source_language_translation_verified"
            ]
        ),
        "islamicate_al_biruni_live_engine": al_biruni_publication["live_engine"],
        "islamicate_comparison_witness_sets": len(access_witness_sets),
        "islamicate_comparison_tei_artifacts": len(access_artifacts),
        "islamicate_comparison_rule_extraction_ready": all(
            edition["rule_extraction_ready"]
            for edition in islamicate_access["controlling_editions"]
        ),
        "islamicate_comparison_live_engine": islamicate_access["live_engine"],
        "islamicate_comparison_concepts": len(islamicate_comparison_concepts),
        "islamicate_candidate_passages": len(islamicate_candidate_passages),
        "islamicate_variant_observations": len(islamicate_variant_observations),
        "engine_coverage_tracks": len(coverage_tracks),
        "engine_coverage_modules": len(coverage_modules),
        "engine_coverage_research_verified": coverage_status_counts[
            "research_verified"
        ],
        "engine_coverage_source_limited": coverage_status_counts[
            "source_limited"
        ],
        "engine_coverage_not_implemented": coverage_status_counts[
            "not_implemented"
        ],
        "nonwestern_live_engines": len(
            coverage_boundary["nonwestern_live_engines"]
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the multi-tradition source, rule, vector, and corpus graph."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Multi-tradition research directory.",
    )
    args = parser.parse_args()
    print(json.dumps(validate(args.root), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
