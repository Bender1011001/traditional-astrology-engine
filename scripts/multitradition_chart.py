"""Take one birth, produce every tradition's chart.

    python scripts/multitradition_chart.py --name Andrew \
        --date 1996-08-13 --time 07:18 --tz -7 \
        --lat 38.2494 --lon -122.0400 --place "Fairfield, California"

    # everything, including the raw computed facts under each section
    python scripts/multitradition_chart.py ... --full

    # one tradition only
    python scripts/multitradition_chart.py ... --only ziwei_doushu

    # a self-contained page you can open in a browser
    python scripts/multitradition_chart.py ... --html chart.html

    # machine-readable
    python scripts/multitradition_chart.py ... --json

Run with no arguments to use the built-in sample birth.

Every section prints its evidence grade, and every disclosure the section made
is printed with it - configured methods, forks, and above all refusals. The
refusals are not padding. They are the part of this panel that the commercial
programs do not have, and reading a section without them will mislead you about
how much it actually claims.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.engine.multitradition import build_panel  # noqa: E402
from src.engine.multitradition.types import BirthInput  # noqa: E402

GRADE_LABEL = {
    "live_engine": "LIVE ENGINE",
    "validated_research_pack": "VALIDATED PACK",
    "configured_method": "CONFIGURED",
    "transcription_grade": "TRANSCRIPTION (grade D)",
}
KIND_LABEL = {
    "refusal": "REFUSES",
    "fork": "FORK",
    "configured_method": "CONFIGURED",
    "source": "SOURCE",
}
KIND_ORDER = ["refusal", "fork", "configured_method", "source"]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--name", default="Sample Birth")
    p.add_argument("--date", help="birth date, YYYY-MM-DD")
    p.add_argument("--time", default="12:00", help="local wall-clock time, HH:MM")
    p.add_argument("--tz", type=float, help="UTC offset in hours at the birthplace")
    p.add_argument("--lat", type=float, help="latitude, north positive")
    p.add_argument("--lon", type=float, help="longitude, EAST positive")
    p.add_argument("--place", default="", help="place label, for the header only")
    p.add_argument("--only", action="append", help="limit to a tradition_id (repeatable)")
    p.add_argument("--full", action="store_true", help="print each section's raw facts")
    p.add_argument("--json", action="store_true", help="emit the whole panel as JSON")
    p.add_argument("--html", metavar="PATH", help="write a self-contained HTML page")
    return p.parse_args(argv)


def birth_from(args: argparse.Namespace) -> BirthInput:
    if args.date is None:
        # The fixture this panel is developed against, so the tool always runs.
        return BirthInput(
            name="Sample Birth (Fairfield, CA)",
            civil_date=date(1996, 8, 13),
            civil_time="07:18",
            utc_offset_hours=-7.0,
            latitude=38.2494,
            longitude=-122.0400,
            place_label="Fairfield, California",
        )
    missing = [f for f in ("tz", "lat", "lon") if getattr(args, f) is None]
    if missing:
        raise SystemExit(
            f"--date given, so these are required too: {', '.join('--' + m for m in missing)}"
        )
    year, month, day = (int(part) for part in args.date.split("-"))
    return BirthInput(
        name=args.name,
        civil_date=date(year, month, day),
        civil_time=args.time,
        utc_offset_hours=args.tz,
        latitude=args.lat,
        longitude=args.lon,
        place_label=args.place or f"{args.lat:.4f}, {args.lon:.4f}",
    )


def _wrap(text: str, width: int, indent: str) -> list[str]:
    words, lines, current = text.split(), [], ""
    for word in words:
        if current and len(current) + 1 + len(word) > width:
            lines.append(indent + current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(indent + current)
    return lines


def _facts_lines(value, indent: int = 0, key: str | None = None) -> list[str]:
    pad = "    " + "  " * indent
    out: list[str] = []
    label = f"{key}: " if key else ""
    if isinstance(value, dict):
        if key:
            out.append(f"{pad}{key}:")
        for k, v in value.items():
            out.extend(_facts_lines(v, indent + 1, str(k)))
    elif isinstance(value, list):
        if not value:
            out.append(f"{pad}{label}(none)")
        elif all(not isinstance(v, (dict, list)) for v in value):
            out.extend(_wrap(label + ", ".join(str(v) for v in value), 92, pad))
        else:
            out.append(f"{pad}{key}:" if key else f"{pad}-")
            for item in value:
                out.extend(_facts_lines(item, indent + 1))
    else:
        out.extend(_wrap(f"{label}{value}", 92, pad))
    return out


def render_text(panel: dict, full: bool, only: list[str] | None) -> str:
    birth = panel["birth"]
    lines = [
        "=" * 96,
        f"  {birth['name']}",
        f"  {birth['civil_date']} {birth['civil_time']} (UTC{birth['utc_offset_hours']:+g})"
        f"  ·  {birth['place_label']}",
        f"  {birth['latitude']:.4f}, {birth['longitude']:.4f}  ·  UTC {birth['utc_datetime']}",
        "=" * 96,
        "",
    ]

    sections = panel["sections"]
    if only:
        wanted = set(only)
        sections = [s for s in sections if s["tradition_id"] in wanted]
        if not sections:
            available = ", ".join(s["tradition_id"] for s in panel["sections"])
            raise SystemExit(f"No such tradition. Available: {available}")

    for section in sections:
        grade = GRADE_LABEL.get(section["evidence_grade"], section["evidence_grade"])
        lines.append("-" * 96)
        lines.append(f"  {section['display_name']}   [{grade}]")
        lines.append(f"  {section['tradition_id']}")
        lines.append("-" * 96)
        if section.get("error"):
            lines.append(f"    ERROR: {section['error']}")
            lines.append("")
            continue
        lines.extend(_wrap(section["basis"], 92, "    "))
        maturity = section.get("maturity")
        if maturity:
            from src.engine.multitradition.maturity import CATEGORY_LABEL
            lines.append("")
            lines.append(
                f"    MATURITY ({maturity['assessed']}): "
                + CATEGORY_LABEL.get(maturity["category"], maturity["category"])
            )
            for axis in ("source_readiness", "computational_readiness",
                         "validation_coverage", "interpretation_readiness",
                         "publication_readiness"):
                lines.extend(_wrap(f"{axis}: {maturity[axis]}", 88, "      "))
        lines.append("")

        disclosures = section.get("disclosures", [])
        by_kind = {k: [d for d in disclosures if d["kind"] == k] for k in KIND_ORDER}
        for kind in KIND_ORDER:
            for d in by_kind[kind]:
                tag = KIND_LABEL[kind]
                if d.get("category"):
                    tag += f": {d['category']}"
                lines.append(f"    [{tag}] {d['subject']}")
                lines.extend(_wrap(d["detail"], 88, "        "))
                if d.get("alternatives"):
                    lines.extend(
                        _wrap(
                            "alternatives not taken: " + "; ".join(d["alternatives"]),
                            88, "        ",
                        )
                    )
                lines.append("")

        if section.get("reading"):
            lines.append("    READING")
            for para in section["reading"]:
                lines.extend(_wrap(para, 88, "        "))
                lines.append("")

        if full and section.get("facts"):
            lines.append("    FACTS")
            lines.extend(_facts_lines(section["facts"]))
            lines.append("")

    convergence = panel.get("convergence")
    if convergence and not only:
        lines.append("=" * 96)
        lines.append("  CONVERGENCE  ·  what agrees, and whether the agreement means anything")
        lines.append("=" * 96)
        lines.append(
            f"    independent voices: {convergence.get('independent_voice_count')}"
        )
        for agreement in convergence.get("agreements", []):
            lines.append(f"    · {agreement.get('statement', '')}")
            for field in ("supporting", "caveat"):
                value = agreement.get(field)
                if isinstance(value, list):
                    value = ", ".join(value)
                if value:
                    lines.extend(_wrap(f"{field}: {value}", 88, "        "))
            lines.append("")

    grades: dict[str, int] = {}
    refusals = 0
    for section in panel["sections"]:
        grades[section["evidence_grade"]] = grades.get(section["evidence_grade"], 0) + 1
        refusals += sum(
            1 for d in section.get("disclosures", []) if d["kind"] == "refusal"
        )
    lines.append("=" * 96)
    lines.append(
        "  " + panel.get(
            "coverage_summary",
            f"{len(panel['sections'])} modules",
        )
        + f"  ·  {refusals} explicit refusals"
    )
    lines.append(
        "  "
        + ", ".join(f"{GRADE_LABEL.get(g, g)}: {n}" for g, n in sorted(grades.items()))
    )
    lines.append(
        "  A refusal is a result. It says the sources do not support the claim, "
        "which is a fact about"
    )
    lines.append("  the tradition rather than a gap in the software.")
    lines.append("=" * 96)
    return "\n".join(lines)


def render_html(panel: dict) -> str:
    birth = panel["birth"]
    def esc(s) -> str:
        return (
            str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )

    parts = [
        "<!doctype html><meta charset='utf-8'>",
        f"<title>{esc(birth['name'])} — multi-tradition panel</title>",
        """<style>
:root{--bg:#faf9f7;--ink:#1a1a1a;--dim:#6b6b6b;--rule:#d8d4cc;--card:#fff;
--refuse:#8c2f2f;--fork:#8a6d1f;--conf:#2f5c8c;--src:#4a4a4a}
@media(prefers-color-scheme:dark){:root{--bg:#141414;--ink:#ececec;--dim:#9a9a9a;
--rule:#333;--card:#1c1c1c;--refuse:#e08585;--fork:#d9be6a;--conf:#87b3e0;--src:#b0b0b0}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.6 Iowan Old Style,Palatino,Georgia,serif;padding:2rem 1rem}
main{max-width:52rem;margin:0 auto}
h1{font-size:1.6rem;margin:0 0 .2rem}
.meta{color:var(--dim);font-size:.9rem;margin-bottom:2rem}
section{background:var(--card);border:1px solid var(--rule);border-radius:6px;
padding:1.2rem 1.4rem;margin:0 0 1.2rem}
h2{font-size:1.15rem;margin:0 0 .1rem}
.tid{font:12px ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--dim)}
.grade{float:right;font:11px ui-monospace,monospace;letter-spacing:.06em;
color:var(--dim);border:1px solid var(--rule);border-radius:3px;padding:.1rem .4rem}
.basis{color:var(--dim);font-size:.95rem;margin:.7rem 0 1rem}
.d{border-left:3px solid var(--rule);padding:.1rem 0 .1rem .8rem;margin:.7rem 0}
.d.refusal{border-color:var(--refuse)}.d.fork{border-color:var(--fork)}
.d.configured_method{border-color:var(--conf)}.d.source{border-color:var(--src)}
.k{font:11px ui-monospace,monospace;letter-spacing:.06em}
.d.refusal .k{color:var(--refuse)}.d.fork .k{color:var(--fork)}
.d.configured_method .k{color:var(--conf)}.d.source .k{color:var(--src)}
.subj{font-weight:600}.det{font-size:.93rem}
.alt{font-size:.85rem;color:var(--dim);margin-top:.25rem}
footer{color:var(--dim);font-size:.9rem;border-top:1px solid var(--rule);
padding-top:1rem;margin-top:2rem}
</style>""",
        "<main>",
        f"<h1>{esc(birth['name'])}</h1>",
        f"<div class=meta>{esc(birth['civil_date'])} {esc(birth['civil_time'])} "
        f"(UTC{birth['utc_offset_hours']:+g}) · {esc(birth['place_label'])} · "
        f"{birth['latitude']:.4f}, {birth['longitude']:.4f}</div>",
    ]
    refusals = 0
    for s in panel["sections"]:
        grade = GRADE_LABEL.get(s["evidence_grade"], s["evidence_grade"])
        parts.append("<section>")
        parts.append(f"<span class=grade>{esc(grade)}</span>")
        parts.append(f"<h2>{esc(s['display_name'])}</h2>")
        parts.append(f"<div class=tid>{esc(s['tradition_id'])}</div>")
        if s.get("error"):
            parts.append(f"<div class=basis>ERROR: {esc(s['error'])}</div></section>")
            continue
        parts.append(f"<div class=basis>{esc(s['basis'])}</div>")
        for kind in KIND_ORDER:
            for d in [x for x in s.get("disclosures", []) if x["kind"] == kind]:
                if kind == "refusal":
                    refusals += 1
                parts.append(f"<div class='d {kind}'>")
                parts.append(
                    f"<div class=k>{KIND_LABEL[kind]}</div>"
                    f"<div class=subj>{esc(d['subject'])}</div>"
                    f"<div class=det>{esc(d['detail'])}</div>"
                )
                if d.get("alternatives"):
                    parts.append(
                        "<div class=alt>alternatives not taken: "
                        + esc("; ".join(d["alternatives"]))
                        + "</div>"
                    )
                parts.append("</div>")
        parts.append("</section>")
    parts.append(
        f"<footer>{len(panel['sections'])} traditions · {refusals} explicit refusals. "
        "A refusal is a result: it says the surviving sources do not support the "
        "claim, which is a fact about the tradition rather than a gap in the "
        "software.</footer></main>"
    )
    return "\n".join(parts)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    panel = build_panel(birth_from(args))

    if args.json:
        print(json.dumps(panel, indent=2, ensure_ascii=False, default=str))
        return 0
    if args.html:
        Path(args.html).write_text(render_html(panel), encoding="utf-8")
        print(f"wrote {args.html}")
        return 0
    print(render_text(panel, args.full, args.only))
    failed = [s["tradition_id"] for s in panel["sections"] if s.get("error")]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
