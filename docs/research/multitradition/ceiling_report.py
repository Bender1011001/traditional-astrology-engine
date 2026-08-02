"""Report each tradition's distance from the best reading its sources permit.

"Best on earth" is not self-certifying, and a claim nobody can check is worth
nothing. This report makes it checkable by scoring every tradition against its
own defensibility spec's core-technique checklist - the list of techniques that
tradition's OWN authorities treat as mandatory - and classifying whatever is
missing.

The key distinction, and the reason a tradition can be at its ceiling while
still having unimplemented techniques:

  implemented   - computed and rendered today
  computable    - inputs exist; this is OUR gap and it is actionable
  source_gated  - blocked on an edition, translation, or specialist review
  refused       - the tradition or its surviving sources cannot support it

A tradition is AT ITS CEILING when nothing on its checklist is `computable`.
Remaining `source_gated` and `refused` items are not deficiencies in the engine;
they are facts about the surviving corpus, and implementing past them would make
the section less defensible, not more.

Run:
    python docs/research/multitradition/ceiling_report.py
    python docs/research/multitradition/ceiling_report.py --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
STATUSES = ("implemented", "computable", "source_gated", "refused")
# Rows look like: | 6 | Technique name | source basis | `implemented` (note) |
ROW = re.compile(r"^\|\s*(\d+)\s*\|(.+?)\|(.+?)\|(.+?)\|\s*$")


def _status_of(cell: str) -> str | None:
    """First recognised status token in the cell, or None if the row is a header."""
    lowered = cell.lower()
    for status in STATUSES:
        if f"`{status}`" in lowered:
            return status
    return None


def _parse_spec(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    items: list[dict[str, Any]] = []
    in_checklist = False
    for line in text.splitlines():
        if line.startswith("## Core-technique checklist"):
            in_checklist = True
            continue
        if in_checklist and line.startswith("## "):
            break
        if not in_checklist:
            continue
        match = ROW.match(line)
        if not match:
            continue
        number, technique, _source, status_cell = match.groups()
        status = _status_of(status_cell)
        if status is None:
            continue
        items.append({
            "number": int(number),
            "technique": technique.strip().strip("*").strip(),
            "status": status,
            "detail": status_cell.strip(),
        })

    refusals = 0
    if "## Refusal list" in text:
        block = text.split("## Refusal list", 1)[1].split("\n## ", 1)[0]
        refusals = block.count("\n- ")

    return {"items": items, "refusal_count": refusals}


def build() -> dict[str, Any]:
    tracks = sorted(
        p.parent.name for p in ROOT.glob("*/defensibility_spec.md")
    )
    report: dict[str, Any] = {"traditions": {}, "summary": {}}
    at_ceiling: list[str] = []
    below_ceiling: list[str] = []

    for track in tracks:
        parsed = _parse_spec(ROOT / track / "defensibility_spec.md")
        items = parsed["items"]
        counts = {status: 0 for status in STATUSES}
        for item in items:
            counts[item["status"]] += 1

        actionable = [i for i in items if i["status"] == "computable"]
        ceiling = not actionable
        (at_ceiling if ceiling else below_ceiling).append(track)

        report["traditions"][track] = {
            "checklist_items": len(items),
            "counts": counts,
            "at_source_ceiling": ceiling,
            "actionable_gaps": [
                {"number": i["number"], "technique": i["technique"]}
                for i in actionable
            ],
            "source_gated": [
                {"number": i["number"], "technique": i["technique"]}
                for i in items
                if i["status"] == "source_gated"
            ],
            "refusals_declared": parsed["refusal_count"],
        }

    report["summary"] = {
        "traditions_scored": len(tracks),
        "at_source_ceiling": sorted(at_ceiling),
        "below_ceiling": sorted(below_ceiling),
        "total_actionable_gaps": sum(
            len(t["actionable_gaps"]) for t in report["traditions"].values()
        ),
    }
    return report


def render(report: dict[str, Any]) -> str:
    lines = [
        "Distance from the best reading each tradition's sources permit",
        "=" * 62,
        "",
        "A tradition is AT ITS CEILING when nothing on its own core-technique",
        "checklist is still `computable`. Source-gated and refused items are",
        "facts about the surviving corpus, not engine deficiencies.",
        "",
        f"{'tradition':18} {'items':>5} {'impl':>5} {'todo':>5} "
        f"{'gated':>6} {'refuse':>6}  ceiling",
        "-" * 62,
    ]
    for track, data in sorted(report["traditions"].items()):
        counts = data["counts"]
        mark = "YES" if data["at_source_ceiling"] else "no"
        lines.append(
            f"{track:18} {data['checklist_items']:5d} "
            f"{counts['implemented']:5d} {counts['computable']:5d} "
            f"{counts['source_gated']:6d} {counts['refused']:6d}  {mark}"
        )

    summary = report["summary"]
    lines.extend([
        "-" * 62,
        f"At ceiling: {len(summary['at_source_ceiling'])}/"
        f"{summary['traditions_scored']} traditions",
        f"Actionable gaps remaining: {summary['total_actionable_gaps']}",
        "",
    ])
    if summary["total_actionable_gaps"]:
        lines.append("Actionable work, by tradition:")
        for track, data in sorted(report["traditions"].items()):
            for gap in data["actionable_gaps"]:
                lines.append(f"  {track:18} #{gap['number']:<3} {gap['technique']}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = build()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(
        json.dumps(report, indent=2, ensure_ascii=False)
        if args.json
        else render(report)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
