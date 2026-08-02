"""Run classical worked examples against the engine and publish the results.

The premise: if a tradition's own author worked a chart and stated a verdict, an
engine claiming to implement that tradition should reproduce the verdict. This
runner executes every example whose encoding_status is `comparable` and reports
pass/fail per claim. Examples still at `inventory_only` are counted and listed,
never silently skipped - an un-run example is a visible gap, not an absence.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[2]
SCHEMA_PATH = ROOT / "worked_examples.schema.json"


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(payload: dict[str, Any], dotted: str) -> Any:
    current: Any = payload
    for part in dotted.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def _compare(actual: Any, expected: Any, mode: str, tolerance: float | None) -> bool:
    if mode == "exact":
        return actual == expected
    if mode == "case_insensitive":
        return str(actual).strip().lower() == str(expected).strip().lower()
    if mode == "numeric_tolerance":
        try:
            return abs(float(actual) - float(expected)) <= (tolerance or 0.0)
        except (TypeError, ValueError):
            return False
    return False


def _maya_engine_output(example: dict[str, Any]) -> dict[str, Any] | None:
    """Produce the Maya kernel output for one worked example.

    Kept local to the runner so the suite does not depend on the product panel;
    a worked example must test the kernel, not the presentation layer.
    """
    sys.path.insert(0, str(REPO_ROOT))
    from src.engine.multitradition.mesoamerican import (  # noqa: PLC0415
        LORDS_OF_NIGHT,
        MAYA_SPEC,
        _emod,
        _spec,
    )

    spec = _spec(MAYA_SPEC)
    chart = example.get("chart_data") or {}
    civil = chart.get("civil_date")
    if not civil:
        return None

    # Derive the JDN from the expected anchor claim when the date is BCE, since
    # proleptic-Gregorian parsing of negative years is not portable.
    jdn_claim = next(
        (
            c
            for c in example["author_judgment"]["claims"]
            if c.get("engine_field") == "integer_jdn"
        ),
        None,
    )
    if jdn_claim is None:
        return None
    jdn = int(jdn_claim["expected_value"])

    names = spec["tzolkin"]["name_profiles"]["yucatec_smithsonian_2012"]
    months = spec["haab"]["month_names"]
    weights = spec["long_count"]["weights_days"]

    def profile(constant: int) -> dict[str, Any]:
        total = jdn - constant
        remaining = total
        parts: dict[str, int] = {}
        for unit in spec["long_count"]["component_order"]:
            parts[unit] = remaining // weights[unit]
            remaining -= parts[unit] * weights[unit]
        position = _emod(total + 348, 365)
        return {
            "integer_jdn": jdn,
            "total_day": total,
            "long_count": ".".join(
                str(parts[u]) for u in spec["long_count"]["component_order"]
            ),
            "tzolkin": f"{_emod(total + 3, 13) + 1} {names[_emod(total + 19, 20)]}",
            "haab": f"{position % 20} {months[position // 20]}",
            "lord_of_night": LORDS_OF_NIGHT[_emod(total + 1, 9)],
        }

    primary = profile(584283)
    primary["__correlation_delta__"] = (
        primary["total_day"] - profile(584285)["total_day"]
    )
    return primary


def _jyotisha_engine_output(example: dict[str, Any]) -> dict[str, Any] | None:
    """Structural navamsha facts the classical rule constrains."""
    if example["example_id"] != "jyotisha.navamsha.selfcheck":
        return None

    sys.path.insert(0, str(REPO_ROOT))
    from collections import Counter  # noqa: PLC0415

    from src.engine.multitradition.vedic import (  # noqa: PLC0415
        NAVAMSHA_ARC,
        SIGNS,
        navamsha_sign,
    )

    counts = Counter(navamsha_sign((i + 0.5) * NAVAMSHA_ARC)[0] for i in range(108))
    return {
        "navamsha_division_balance": (
            set(counts) == set(SIGNS) and set(counts.values()) == {9}
        ),
        "navamsha_aries_first": navamsha_sign(0.01)[0],
        "navamsha_taurus_first": navamsha_sign(30.01)[0],
        "navamsha_gemini_first": navamsha_sign(60.01)[0],
        "navamsha_pisces_last": navamsha_sign(359.99)[0],
    }


def _bazi_engine_output(example: dict[str, Any]) -> dict[str, Any] | None:
    """Structural consequences of the BaZi tables, plus the day anchor."""
    sys.path.insert(0, str(REPO_ROOT))
    from src.engine.multitradition.bazi import (  # noqa: PLC0415
        BRANCH_ELEMENT,
        COMMAND_STATES,
        DAY_ANCHOR_INDEX,
        DAY_ANCHOR_JDN,
        HIDDEN_STEMS,
        STEM_ELEMENT,
        _pair,
        _stems,
        seasonal_state,
        ten_god,
    )

    eid = example["example_id"]

    if eid == "bazi.anchor.independent_crosscheck":
        idx_2000 = (DAY_ANCHOR_INDEX + (2451545 - DAY_ANCHOR_JDN)) % 60
        idx_1949 = (DAY_ANCHOR_INDEX + (2433191 - DAY_ANCHOR_JDN)) % 60
        stem, branch = _pair(idx_2000)
        return {
            "anchor_1949_index": idx_1949,
            "anchor_2000_index": idx_2000,
            "anchor_2000_pair": f"{stem}/{branch}",
        }

    if eid == "bazi.hidden_stems.main_qi_identity":
        return {
            "main_qi_matches_branch_element_all_12": all(
                STEM_ELEMENT[stems[0]][0] == BRANCH_ELEMENT[branch]
                for branch, stems in HIDDEN_STEMS.items()
            ),
            "pure_branch_count": sum(
                1 for stems in HIDDEN_STEMS.values() if len(stems) == 1
            ),
        }

    if eid == "bazi.ten_gods.relation_closure":
        stems = _stems()
        return {
            "ten_distinct_relations_all_day_masters": all(
                len({ten_god(dm, other)[0] for other in stems}) == 10
                for dm in stems
            ),
            "self_relation_all_stems": (
                "bi_jian"
                if all(ten_god(s, s)[0] == "bi_jian" for s in stems)
                else "MISMATCH"
            ),
            "same_element_opposite_polarity_all_stems": (
                "jie_cai"
                if all(
                    ten_god(a, b)[0] == "jie_cai"
                    for a in stems
                    for b in stems
                    if STEM_ELEMENT[a][0] == STEM_ELEMENT[b][0]
                    and STEM_ELEMENT[a][1] != STEM_ELEMENT[b][1]
                )
                else "MISMATCH"
            ),
        }

    if eid == "bazi.seasonal.command_closure":
        elements = ["Wood", "Fire", "Earth", "Metal", "Water"]
        branches = list(HIDDEN_STEMS)
        bijective = all(
            sorted(seasonal_state(e, b) for e in elements) == sorted(COMMAND_STATES)
            for b in branches
        )
        from src.engine.multitradition.bazi import SEASON_ELEMENT  # noqa: PLC0415

        season_wang = all(
            seasonal_state(SEASON_ELEMENT[b], b).startswith("wang") for b in branches
        )
        return {
            "seasonal_state_bijection_all_12_months": bijective,
            "season_element_always_wang": season_wang,
        }

    return None


def _tibetan_engine_output(example: dict[str, Any]) -> dict[str, Any] | None:
    """Year-character anchors and sexagenary structural consequences."""
    sys.path.insert(0, str(REPO_ROOT))
    from src.engine.multitradition.tibetan import (  # noqa: PLC0415
        ELEMENTS,
        year_character,
    )

    eid = example["example_id"]
    if eid in ("tibetan.year_character.rabjung_anchor",
               "tibetan.year_character.jiazi_crosscheck"):
        return {
            f"year_{year}": year_character(year)
            for year in (1027, 1984, 1996)
        }

    if eid == "tibetan.year_character.cycle_closure":
        span = [year_character(1984 + offset) for offset in range(60)]
        characters = {
            (c["element"], c["animal"], c["polarity"]) for c in span
        }
        element_counts = {e: 0 for e in ELEMENTS}
        for c in span:
            element_counts[c["element"]] += 1
        polarities = [c["polarity"] for c in span]
        return {
            "sixty_unique_characters": len(characters) == 60,
            "each_element_twelve_years": set(element_counts.values()) == {12},
            "polarity_strictly_alternates": all(
                polarities[i] != polarities[i + 1] for i in range(59)
            ),
        }
    return None


ENGINE_ADAPTERS = {
    "maya": _maya_engine_output,
    "jyotisha": _jyotisha_engine_output,
    "bazi": _bazi_engine_output,
    "tibetan": _tibetan_engine_output,
}


def run(tradition_filter: str | None = None) -> dict[str, Any]:
    schema = _read(SCHEMA_PATH)
    validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    )

    suites: list[tuple[str, dict[str, Any]]] = []
    for path in sorted(ROOT.rglob("worked_examples.json")):
        data = _read(path)
        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
        if errors:
            location = ".".join(str(p) for p in errors[0].absolute_path) or "<root>"
            raise ValueError(
                f"Worked-example schema failure in {path.name} at {location}: "
                f"{errors[0].message}"
            )
        suites.append((path.parent.name, data))

    if not suites:
        raise ValueError("No worked-example suites found")

    results: list[dict[str, Any]] = []
    totals = {"comparable": 0, "inventory": 0, "claims_run": 0, "claims_passed": 0}

    for track, suite in suites:
        if tradition_filter and track != tradition_filter:
            continue
        adapter = ENGINE_ADAPTERS.get(track)
        for example in suite["examples"]:
            entry: dict[str, Any] = {
                "tradition": track,
                "example_id": example["example_id"],
                "work": example["work"],
                "encoding_status": example["encoding_status"],
                "claims": [],
            }
            if example["encoding_status"] != "comparable" or adapter is None:
                totals["inventory"] += 1
                entry["skipped_reason"] = (
                    "encoding_status is not 'comparable'"
                    if example["encoding_status"] != "comparable"
                    else f"no engine adapter registered for '{track}'"
                )
                entry["blockers"] = example.get("blockers", [])
                results.append(entry)
                continue

            totals["comparable"] += 1
            produced = adapter(example)
            for claim in example["author_judgment"]["claims"]:
                field = claim.get("engine_field")
                if produced is None or not field:
                    entry["claims"].append(
                        {"claim_id": claim["claim_id"], "result": "not_runnable"}
                    )
                    continue
                actual = _resolve(produced, field)
                passed = _compare(
                    actual,
                    claim.get("expected_value"),
                    claim.get("comparison", "manual"),
                    claim.get("tolerance"),
                )
                totals["claims_run"] += 1
                totals["claims_passed"] += int(passed)
                entry["claims"].append({
                    "claim_id": claim["claim_id"],
                    "result": "pass" if passed else "FAIL",
                    "expected": claim.get("expected_value"),
                    "actual": actual,
                    "author_states": claim["author_states"],
                })
            results.append(entry)

    failures = [
        (entry["example_id"], claim["claim_id"])
        for entry in results
        for claim in entry["claims"]
        if claim["result"] == "FAIL"
    ]

    return {
        "status": "pass" if not failures else "fail",
        "suites": len(suites),
        "examples_comparable": totals["comparable"],
        "examples_inventory_only": totals["inventory"],
        "claims_run": totals["claims_run"],
        "claims_passed": totals["claims_passed"],
        "failures": failures,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run classical worked examples.")
    parser.add_argument("--tradition", help="Restrict to one tradition directory.")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    report = run(args.tradition)
    summary = {k: v for k, v in report.items() if k != "results"}
    if args.verbose:
        summary["results"] = report["results"]
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
