"""Which mined rules actually reach a page, and which never do.

    python scripts/audit_engine_coverage.py
    python scripts/audit_engine_coverage.py --charts 24
    python scripts/audit_engine_coverage.py --json

The corpus grows by mining and the reports grow by wiring, and those are two
different activities that are easy to confuse. A manifest whose rule ids no
engine references is indistinguishable, from every other signal in this project,
from a manifest that was never written: the validators pass, the rule count goes
up, the coverage report lists the module, and not one sentence changes in any
report.

That has now happened twice - once to the Valens pack and once to four packs at
the same time - so it gets a measurement rather than vigilance.

A rule is counted REACHED if it produces a rendered delineation on at least one
of several varied nativities. Varied matters: a rule gated on a nocturnal chart
or a retrograde Saturn will never fire on one birth, and calling it dead would
be the same error in the opposite direction.

Calculation manifests correctly reach nothing - they feed the panel's arithmetic
rather than producing prose - so they are listed separately from the delineation
manifests, which are the ones where a zero is a finding.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.engine.multitradition.types import BirthInput  # noqa: E402
from src.engine.traditions import (  # noqa: E402
    REPORT_ENGINES,
    build_tradition_report,
)

RESEARCH = Path(__file__).resolve().parents[1] / "docs" / "research" / "multitradition"

#: Manifests that exist to drive computation, not to be quoted. A zero here is
#: correct and expected, and lumping them in with the delineation packs would
#: make the real finding harder to see.
CALCULATION_MANIFESTS = {
    "bazi/sexagenary_rule_manifest.json",
    "egyptian/civil_calendar_rule_manifest.json",
    "jyotisha/brhajjataka_calculation_rule_manifest.json",
    "jyotisha/strength_rule_manifest.json",
    "jyotisha/varga_rule_manifest.json",
    "maya/calendar_rule_manifest.json",
    "nahua/calendar_rule_manifest.json",
    "nahua/correlation_rule_manifest.json",
    "tibetan/phugpa_calendar_rule_manifest.json",
    "vietnamese/calendar_rule_manifest.json",
    "ziwei/calculation_rule_manifest.json",
}


def varied_births(count: int, seed: int = 11) -> list[BirthInput]:
    """Charts spread over time, clock, latitude and hemisphere.

    The spread is the point. Sect, retrogradation, combustion and hemisphere
    all gate rules, and a single birth exercises one value of each.
    """
    rng = random.Random(seed)
    out = []
    for i in range(count):
        out.append(
            BirthInput(
                name=f"Sample {i}",
                civil_date=date(
                    rng.randint(1935, 2010), rng.randint(1, 12), rng.randint(1, 28)
                ),
                civil_time=f"{rng.randint(0, 23):02d}:{rng.randint(0, 59):02d}",
                utc_offset_hours=rng.choice([-8, -5, 0, 1, 5.5, 8, 9]),
                latitude=rng.uniform(-35.0, 55.0),
                longitude=rng.uniform(-120.0, 140.0),
                place_label="Sample",
                sex=rng.choice(["male", "female"]),
            )
        )
    return out


def manifests() -> dict[str, set[str]]:
    """Every rule id on disk, keyed by <track>/<file>."""
    out: dict[str, set[str]] = {}
    for path in sorted(RESEARCH.rglob("*manifest.json")):
        try:
            rules = json.loads(path.read_text(encoding="utf-8")).get("rules", [])
        except (OSError, json.JSONDecodeError):
            continue
        ids = {r["rule_id"] for r in rules if r.get("rule_id")}
        if ids:
            out[f"{path.parent.name}/{path.name}"] = ids
    return out


def fired_rule_ids(births: list[BirthInput]) -> tuple[set[str], list[str]]:
    """Every rule id that reached a page, and any engine that blew up."""
    seen: set[str] = set()
    errors: list[str] = []
    for tradition_id in sorted(REPORT_ENGINES):
        for birth in births:
            try:
                report = build_tradition_report(tradition_id, birth)
            except Exception as exc:
                errors.append(f"{tradition_id}: {type(exc).__name__}: {exc}")
                continue
            for section in report.sections:
                for d in section.delineations:
                    seen.add(d.rule_id)
    return seen, errors


def audit(charts: int) -> dict:
    births = varied_births(charts)
    seen, errors = fired_rule_ids(births)
    packs = manifests()

    rows = []
    for name, ids in sorted(packs.items()):
        reached = len(ids & seen)
        rows.append({
            "manifest": name,
            "rules": len(ids),
            "reached": reached,
            "is_calculation": name in CALCULATION_MANIFESTS,
        })
    dead = [
        r for r in rows if r["reached"] == 0 and not r["is_calculation"]
    ]
    return {
        "charts_tested": charts,
        "rules_total": sum(r["rules"] for r in rows),
        "rules_reached": len(seen),
        "manifests": rows,
        "unwired_manifests": sorted(
            dead, key=lambda r: -r["rules"]
        ),
        "unwired_rules": sum(r["rules"] for r in dead),
        "engine_errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--charts", type=int, default=12,
                   help="how many varied nativities to exercise (default 12)")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    args = p.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    result = audit(args.charts)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    print(f"Exercised {result['charts_tested']} varied nativities across "
          f"{len(REPORT_ENGINES)} report engines.\n")
    print(f"{'manifest':<56}{'rules':>7}{'reached':>9}")
    for row in result["manifests"]:
        if row["reached"] or row["is_calculation"]:
            tag = "  (calc)" if row["is_calculation"] else ""
            print(f"{row['manifest']:<56}{row['rules']:>7}{row['reached']:>9}{tag}")

    print("\nDELINEATION MANIFESTS NO ENGINE READS")
    print("  (a zero here is unrealised work, not a missing source)")
    for row in result["unwired_manifests"]:
        print(f"  {row['rules']:>4}  {row['manifest']}")
    print(f"\n  {result['unwired_rules']} rules mined, validated, and never rendered.")

    if result["engine_errors"]:
        print(f"\n{len(result['engine_errors'])} engine error(s):")
        for err in result["engine_errors"][:8]:
            print(f"  {err}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
