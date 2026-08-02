"""Validate the research-only al-Biruni reference and condition source pack."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SPEC_PATH = ROOT / "al_biruni_reference_condition_spec.json"
MANIFEST_PATH = ROOT / "al_biruni_reference_condition_rule_manifest.json"
VECTORS_PATH = ROOT / "al_biruni_reference_condition_validation_vectors.json"

SOURCE_PACK_ID = "islamicate_al_biruni_tafhim_reference_conditions_v1"
EDITION_ID = "wright_1934_halle_facing_scan"

DESCENDING_CYCLE = (
    "saturn",
    "jupiter",
    "mars",
    "sun",
    "venus",
    "mercury",
    "moon",
)
DIURNAL_ORDER = ("sun", "venus", "mercury", "moon", "saturn", "jupiter", "mars")
NOCTURNAL_ORDER = (
    "moon",
    "saturn",
    "jupiter",
    "mars",
    "sun",
    "venus",
    "mercury",
)

SIGNS = (
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
)
MALE_SIGNS = frozenset(SIGNS[::2])
FEMALE_SIGNS = frozenset(SIGNS[1::2])

FIXED_PLANET_GENDER = {
    "saturn": "male",
    "jupiter": "male",
    "mars": "male",
    "sun": "male",
    "venus": "female",
    "moon": "female",
}
FIXED_PLANET_SECT = {
    "saturn": "diurnal",
    "jupiter": "diurnal",
    "mars": "nocturnal",
    "sun": "diurnal",
    "venus": "nocturnal",
    "moon": "nocturnal",
}
SECTS = frozenset({"diurnal", "nocturnal"})

EXPECTED_FACING_HASHES = {
    458: "bbdcf80f232009449e5c68416ae414b2878d4aae26add914f87235ad4fa4840a",
    459: "fe869e88cba3522dedd25604d9d76a34ad3d2dac544cf9add08e1901da396c5e",
    504: "77543e1bae10876d856d1a0be7d02683c72f471044dfcd3f262c4a3107d7354c",
    505: "86177a978a7880943ffc3be86d7b24b34f7065961ca4ef866fedea7c3ff0dde9",
    514: "6f62f3820b2f189d4a9e8ebea7c95b05f30d7a765adfcf52dc2a20b08e3cf382",
    515: "48a0f6623a200e680ae06fab61ff216c9f49aa222ecc292c6f92dffa92f985a2",
    516: "f00f016a9f25a3db501c0b5f4316e97c52a79c290be48428b60997cd02cbc86a",
    517: "636c8ea3d7cd7fb5985ad3bb5df9801dd1c2e14d310d603315868c3999fed986",
    654: "36357c879304e3cc7b44f60eec3324eb091f52474112f203052c82887a537554",
    655: "f773ad91ad63efb9dcf18e219fbea7e186383d533e570fcf7ea855aeeef923ff",
    656: "203bc69b2203c7f52467bf50fb73f284cadb94d2eb81e6381ef556e4de3cc0f0",
    657: "9e0ebd7c1e4190e107f248f90cf6b30448d5939b3da46d316a1bbc4dc4c5cee3",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def require_choice(value: str, choices: frozenset[str], label: str) -> str:
    if value not in choices:
        raise ValueError(f"Invalid {label}: {value!r}; expected one of {sorted(choices)}")
    return value


def sign_gender(sign: str) -> str:
    normalized = sign.lower()
    if normalized in MALE_SIGNS:
        return "male"
    if normalized in FEMALE_SIGNS:
        return "female"
    raise ValueError(f"Unknown zodiac sign: {sign!r}")


def fixed_planet_gender(planet: str) -> str:
    normalized = planet.lower()
    if normalized == "mercury":
        raise ValueError("Mercury gender requires an explicit contextual basis")
    try:
        return FIXED_PLANET_GENDER[normalized]
    except KeyError as exc:
        raise ValueError(f"Unknown planet: {planet!r}") from exc


def fixed_planet_sect(planet: str) -> str:
    normalized = planet.lower()
    if normalized == "mercury":
        raise ValueError("Mercury sect requires an explicit contextual basis")
    try:
        return FIXED_PLANET_SECT[normalized]
    except KeyError as exc:
        raise ValueError(f"Unknown planet: {planet!r}") from exc


def resolve_mercury(
    *,
    sign: str | None = None,
    associated_planet: str | None = None,
    alone: bool = False,
) -> dict[str, str]:
    if associated_planet is not None:
        normalized = associated_planet.lower()
        if normalized == "mercury":
            raise ValueError("Mercury cannot resolve its classifications from itself")
        return {
            "gender": fixed_planet_gender(normalized),
            "sect": fixed_planet_sect(normalized),
        }
    if alone and sign is not None:
        gender = sign_gender(sign)
        return {
            "gender": "male",
            "sect": "diurnal" if gender == "male" else "nocturnal",
        }
    raise ValueError("Mercury gender and sect bases are required")


def firdaria_major_order(nativity_sect: str) -> list[str]:
    normalized = require_choice(nativity_sect, SECTS, "nativity sect")
    return list(DIURNAL_ORDER if normalized == "diurnal" else NOCTURNAL_ORDER)


def firdaria_subperiods(major_ruler: str) -> list[dict[str, Any]]:
    normalized = major_ruler.lower()
    if normalized not in DESCENDING_CYCLE:
        raise ValueError(f"Unknown firdaria ruler: {major_ruler!r}")
    start = DESCENDING_CYCLE.index(normalized)
    subordinate_order = [
        DESCENDING_CYCLE[(start + offset) % len(DESCENDING_CYCLE)]
        for offset in range(len(DESCENDING_CYCLE))
    ]
    result: list[dict[str, Any]] = []
    for index, subordinate in enumerate(subordinate_order, start=1):
        rulers = [normalized] if index == 1 else [normalized, subordinate]
        result.append(
            {
                "index": index,
                "fraction_start": f"{index - 1}/7",
                "fraction_end": f"{index}/7",
                "rulers": rulers,
            }
        )
    return result


def is_halb(*, nativity_sect: str, planet_sect: str, above_horizon: bool) -> bool:
    chart = require_choice(nativity_sect, SECTS, "nativity sect")
    planet = require_choice(planet_sect, SECTS, "planet sect")
    if not isinstance(above_horizon, bool):
        raise TypeError("above_horizon must be boolean")
    return (planet == chart) == above_horizon


def classify_fixed_planet(
    *, planet: str, nativity_sect: str, above_horizon: bool, sign: str
) -> dict[str, Any]:
    gender = fixed_planet_gender(planet)
    sect = fixed_planet_sect(planet)
    halb = is_halb(
        nativity_sect=nativity_sect,
        planet_sect=sect,
        above_horizon=above_horizon,
    )
    return {
        "halb": halb,
        "hayyiz": halb and gender == sign_gender(sign),
    }


def source_contract(spec: dict[str, Any]) -> dict[str, Any]:
    publication = spec["publication_contract"]
    lineage = spec["lineage_contract"]
    return {
        "author_id": spec["author_id"],
        "work_id": spec["work_id"],
        "edition_id": spec["edition_id"],
        "generic_islamicate_merge": lineage["generic_islamicate_identity_allowed"],
        "source_language_translation_verified": lineage[
            "source_language_translation_verified"
        ],
        "live_engine": publication["live_engine"],
        "customer_eligible": publication["customer_eligible"],
        "interpretation_eligible": publication["interpretation_eligible"],
        "full_reading_eligible": publication["full_reading_eligible"],
        "historical_use_only": publication["historical_use_only"],
    }


def mercury_resolution_matrix() -> dict[str, Any]:
    cases: list[dict[str, str]] = []
    try:
        resolve_mercury()
    except ValueError as exc:
        cases.append({"case": "undeclared", "status": "rejected", "reason": str(exc)})
    else:
        raise AssertionError("Mercury without context must be rejected")

    alone = resolve_mercury(sign="aries", alone=True)
    cases.append({"case": "alone_in_aries", "status": "resolved", **alone})
    associated = resolve_mercury(associated_planet="venus")
    cases.append({"case": "associated_with_venus", "status": "resolved", **associated})
    return {"cases": cases}


def halb_truth_table() -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    for nativity_sect in ("diurnal", "nocturnal"):
        for planet_sect in ("diurnal", "nocturnal"):
            for above_horizon in (True, False):
                cases.append(
                    {
                        "nativity_sect": nativity_sect,
                        "planet_sect": planet_sect,
                        "above_horizon": above_horizon,
                        "halb": is_halb(
                            nativity_sect=nativity_sect,
                            planet_sect=planet_sect,
                            above_horizon=above_horizon,
                        ),
                    }
                )
    return {"cases": cases}


def examples_for_planet(
    planet: str, cases: tuple[tuple[str, bool, str], ...]
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for nativity_sect, above_horizon, sign in cases:
        condition = classify_fixed_planet(
            planet=planet,
            nativity_sect=nativity_sect,
            above_horizon=above_horizon,
            sign=sign,
        )
        result.append(
            {
                "planet": planet,
                "nativity_sect": nativity_sect,
                "above_horizon": above_horizon,
                "sign": sign,
                **condition,
            }
        )
    return result


def hayyiz_examples() -> dict[str, Any]:
    sun_cases = examples_for_planet(
        "sun",
        (
            ("diurnal", True, "aries"),
            ("diurnal", True, "taurus"),
            ("nocturnal", False, "aries"),
            ("nocturnal", True, "aries"),
        ),
    )
    venus_cases = examples_for_planet("venus", (("nocturnal", True, "taurus"),))
    cases = sun_cases + venus_cases
    return {
        "cases": cases,
        "every_hayyiz_is_halb": all(
            not case["hayyiz"] or case["halb"] for case in cases
        ),
        "halb_without_hayyiz_exists": any(
            case["halb"] and not case["hayyiz"] for case in cases
        ),
    }


def mars_examples() -> dict[str, Any]:
    cases = examples_for_planet(
        "mars",
        (
            ("nocturnal", True, "aries"),
            ("nocturnal", True, "taurus"),
            ("diurnal", False, "aries"),
            ("diurnal", True, "aries"),
        ),
    )
    for case in cases:
        case.pop("planet")
    return {"cases": cases}


def evaluate(inputs: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    operation = inputs.get("operation")
    if operation == "source_contract":
        return source_contract(spec)
    if operation == "firdaria_major_order":
        return {"major_order": firdaria_major_order(inputs["nativity_sect"])}
    if operation == "firdaria_subperiods":
        return {"subperiods": firdaria_subperiods(inputs["major_ruler"])}
    if operation == "firdaria_boundaries":
        return {
            "planetary_rulers_only": True,
            "node_periods_authorized": False,
            "major_period_durations_available": False,
            "elapsed_age_boundaries_authorized": False,
        }
    if operation == "sign_gender_table":
        return {sign: sign_gender(sign) for sign in SIGNS}
    if operation == "planet_gender_table":
        return {
            **FIXED_PLANET_GENDER,
            "mercury": "conditional_male_when_alone",
        }
    if operation == "planet_sect_table":
        return {
            **FIXED_PLANET_SECT,
            "mercury": "conditional_on_sign_or_association",
        }
    if operation == "mercury_resolution_matrix":
        return mercury_resolution_matrix()
    if operation == "halb_truth_table":
        return halb_truth_table()
    if operation == "hayyiz_examples":
        return hayyiz_examples()
    if operation == "mars_examples":
        return mars_examples()
    if operation == "joy_boundary":
        return {
            "halb_or_hayyiz_is_a_joy_condition": True,
            "complete_judgment_authorized": False,
            "debility_cancelled": False,
            "malefic_nature_changed": False,
            "score_authorized": False,
            "customer_prediction": False,
        }
    raise ValueError(f"Unknown validation operation: {operation!r}")


def verify_exhaustive_hayyiz_implication() -> None:
    for planet in FIXED_PLANET_GENDER:
        for nativity_sect in SECTS:
            for above_horizon in (False, True):
                for sign in SIGNS:
                    result = classify_fixed_planet(
                        planet=planet,
                        nativity_sect=nativity_sect,
                        above_horizon=above_horizon,
                        sign=sign,
                    )
                    if result["hayyiz"] and not result["halb"]:
                        raise AssertionError(
                            f"Hayyiz without halb: {planet}, {nativity_sect}, "
                            f"above={above_horizon}, {sign}"
                        )


def validate() -> dict[str, Any]:
    spec = load_json(SPEC_PATH)
    manifest = load_json(MANIFEST_PATH)
    vectors_document = load_json(VECTORS_PATH)

    for document_name, document in (
        ("spec", spec),
        ("manifest", manifest),
        ("vectors", vectors_document),
    ):
        if document["source_pack_id"] != SOURCE_PACK_ID:
            raise AssertionError(f"Unexpected source pack in {document_name}")
    if spec["edition_id"] != EDITION_ID:
        raise AssertionError("Unexpected edition identity")

    rules = manifest["rules"]
    vectors = vectors_document["vectors"]
    if len(rules) != 15:
        raise AssertionError(f"Expected 15 atomic rules, found {len(rules)}")
    if len(vectors) != 13:
        raise AssertionError(f"Expected 13 compound vectors, found {len(vectors)}")

    rule_ids = {rule["rule_id"] for rule in rules}
    if len(rule_ids) != len(rules):
        raise AssertionError("Duplicate rule IDs")
    covered_rule_ids = {
        rule_id for vector in vectors for rule_id in vector["rule_ids"]
    }
    if covered_rule_ids != rule_ids:
        missing = sorted(rule_ids - covered_rule_ids)
        extra = sorted(covered_rule_ids - rule_ids)
        raise AssertionError(f"Rule coverage mismatch; missing={missing}, extra={extra}")

    for rule in rules:
        scope = rule["scope"]
        if scope.get("interpretation_eligible") is not False:
            raise AssertionError(f"Interpretation leaked in {rule['rule_id']}")
        if rule["conclusion"].get("customer_prediction") is not False:
            raise AssertionError(f"Customer prediction leaked in {rule['rule_id']}")

    publication = spec["publication_contract"]
    forbidden_true = (
        "live_engine",
        "customer_eligible",
        "interpretation_eligible",
        "full_reading_eligible",
        "arabic_specialist_review_complete",
        "independent_reader_agreement_complete",
    )
    if any(publication[field] for field in forbidden_true):
        raise AssertionError("Research-only publication boundary was weakened")

    expected_hashes = {
        "pdf_sha256": "b5b15d3a25842072d680dd6e6d341c992bff0c2a43141d36b47e6a7e2cc761d2",
        "extracted_text_sha256": "11d1c3f37303ff0c52967c1beb952e490e869fe2ae18f75b657694279bdf247c",
    }
    extract = spec["sources"]["english_astrology_extract"]
    for field, expected in expected_hashes.items():
        if extract[field] != expected:
            raise AssertionError(f"Unexpected local extract {field}")

    facing_pairs = spec["facing_page_evidence"]
    if len(facing_pairs) != 6:
        raise AssertionError("Expected six inspected English/Arabic facing-page pairs")
    observed_facing_hashes: dict[int, str] = {}
    for pair in facing_pairs:
        if pair["arabic_canvas_order"] != pair["english_canvas_order"] + 1:
            raise AssertionError(f"Facing-page order mismatch: {pair}")
        observed_facing_hashes[pair["english_canvas_order"]] = pair[
            "english_sha256"
        ]
        observed_facing_hashes[pair["arabic_canvas_order"]] = pair["arabic_sha256"]
    if observed_facing_hashes != EXPECTED_FACING_HASHES:
        raise AssertionError("Facing-page snapshot hashes changed")

    firdaria = spec["firdaria"]
    if tuple(firdaria["descending_cycle"]) != DESCENDING_CYCLE:
        raise AssertionError("Firdaria descending cycle changed")
    if tuple(firdaria["diurnal_major_order"]) != DIURNAL_ORDER:
        raise AssertionError("Diurnal firdaria order changed")
    if tuple(firdaria["nocturnal_major_order"]) != NOCTURNAL_ORDER:
        raise AssertionError("Nocturnal firdaria order changed")
    if (
        firdaria["node_periods_stated"] is not False
        or firdaria["major_period_durations_stated_in_inspected_passage"] is not False
        or firdaria["elapsed_age_boundary_calculation_authorized"] is not False
    ):
        raise AssertionError("Firdaria fail-closed boundary changed")

    classifications = spec["classifications"]
    if set(classifications["male_signs"]) != MALE_SIGNS:
        raise AssertionError("Male-sign table changed")
    if set(classifications["female_signs"]) != FEMALE_SIGNS:
        raise AssertionError("Female-sign table changed")
    if set(classifications["male_planets"]) != {
        planet for planet, gender in FIXED_PLANET_GENDER.items() if gender == "male"
    }:
        raise AssertionError("Male-planet table changed")
    if set(classifications["female_planets"]) != {
        planet for planet, gender in FIXED_PLANET_GENDER.items() if gender == "female"
    }:
        raise AssertionError("Female-planet table changed")

    passed_ids: list[str] = []
    for vector in vectors:
        actual = evaluate(vector["inputs"], spec)
        if actual != vector["expected"]:
            raise AssertionError(
                f"Vector {vector['vector_id']} failed\n"
                f"expected={json.dumps(vector['expected'], sort_keys=True)}\n"
                f"actual={json.dumps(actual, sort_keys=True)}"
            )
        passed_ids.append(vector["vector_id"])

    verify_exhaustive_hayyiz_implication()
    return {
        "status": "pass",
        "source_pack_id": SOURCE_PACK_ID,
        "rules_checked": len(rules),
        "vectors_passed": len(passed_ids),
        "vector_ids": passed_ids,
        "facing_page_pairs_inspected": len(facing_pairs),
        "fixed_planet_hayyiz_cases_exhaustively_checked": (
            len(FIXED_PLANET_GENDER) * len(SECTS) * 2 * len(SIGNS)
        ),
        "source_language_translation_verified": spec["lineage_contract"][
            "source_language_translation_verified"
        ],
        "live_engine": publication["live_engine"],
        "customer_eligible": publication["customer_eligible"],
        "interpretation_eligible": publication["interpretation_eligible"],
        "full_reading_eligible": publication["full_reading_eligible"],
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2, sort_keys=True))
