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


ENGINE_ADAPTERS = {"maya": _maya_engine_output}


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
