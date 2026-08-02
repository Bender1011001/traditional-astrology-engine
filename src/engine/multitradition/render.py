"""Markdown renderer for the multi-tradition panel.

Disclosures render before facts, deliberately. A reader should learn what was
chosen and what is refused before they see any number.
"""

from __future__ import annotations

from typing import Any

GRADE_LABEL = {
    "validated_research_pack": "validated research pack",
    "live_engine": "live engine",
    "configured_method": "configured method",
    "transcription_grade": "transcription grade",
}
KIND_LABEL = {
    "configured_method": "Configured",
    "fork": "Fork",
    "refusal": "Refused",
    "source": "Source",
}


def render(panel: dict[str, Any]) -> str:
    birth = panel["birth"]
    bases = panel["time_bases"]
    lines: list[str] = [
        f"# Multi-tradition panel — {birth['name']}",
        "",
        "Historical and cultural interpretation of astrological doctrine. "
        "Not medical, financial, legal, psychological, or safety advice.",
        "",
        f"**Birth**: {birth['civil_date']} {birth['civil_time']} "
        f"(UTC{birth['utc_offset_hours']:+g}) — {birth['place_label']} "
        f"({birth['latitude']:.4f}, {birth['longitude']:.4f})",
        f"**UTC**: {birth['utc_datetime']}  ·  "
        f"**JDN**: {bases['julian_day_number']}",
        f"**Local mean time**: {bases['local_mean_time']}  ·  "
        f"**True solar time**: {bases['true_solar_time']} "
        f"(equation of time {bases['equation_of_time_minutes']:+.1f} min)",
        "",
        f"Panel version {panel['panel_version']}. "
        f"Sections: {len(panel['sections'])}.",
        "",
        "---",
        "",
    ]

    for section in panel["sections"]:
        lines.extend(_render_section(section))

    lines.extend([
        "## How to read the labels",
        "",
        "- **validated research pack** — arithmetic from a fail-closed pack whose "
        "standalone validator passes in this repository.",
        "- **live engine** — produced by the shipping Western calculator.",
        "- **configured method** — the product chose a convention the research "
        "pack deliberately refuses to default. Alternatives are named inline.",
        "- **Refused** — the tradition, or the surviving sources for it, cannot "
        "support the claim. This is a finding, not an omission.",
        "",
    ])
    return "\n".join(lines)


def _render_section(section: dict[str, Any]) -> list[str]:
    grade = GRADE_LABEL.get(section["evidence_grade"], section["evidence_grade"])
    lines = [f"## {section['display_name']}", "", f"*Evidence: {grade}*", ""]

    if section.get("error"):
        lines.extend([f"**Section failed**: `{section['error']}`", "", "---", ""])
        return lines

    lines.extend([section["basis"], ""])

    if section.get("disclosures"):
        lines.append("**Disclosures**")
        lines.append("")
        for disclosure in section["disclosures"]:
            label = KIND_LABEL.get(disclosure["kind"], disclosure["kind"])
            text = f"- **{label} — {disclosure['subject']}.** {disclosure['detail']}"
            if disclosure.get("alternatives"):
                text += f" *Alternatives: {', '.join(disclosure['alternatives'])}.*"
            lines.append(text)
        lines.append("")

    facts = section.get("facts") or {}
    if facts:
        lines.append("**Calculation**")
        lines.append("")
        lines.extend(_render_facts(facts))
        lines.append("")

    if section.get("reading"):
        lines.append("**Reading**")
        lines.append("")
        for paragraph in section["reading"]:
            lines.append(paragraph)
            lines.append("")

    lines.extend(["---", ""])
    return lines


def _render_facts(facts: dict[str, Any], indent: int = 0) -> list[str]:
    pad = "  " * indent
    lines: list[str] = []
    for key, value in facts.items():
        label = key.replace("_", " ")
        if isinstance(value, dict):
            lines.append(f"{pad}- **{label}**:")
            lines.extend(_render_facts(value, indent + 1))
        elif isinstance(value, list):
            if value and isinstance(value[0], dict):
                lines.append(f"{pad}- **{label}**:")
                for item in value:
                    summary = ", ".join(
                        f"{k.replace('_', ' ')} {v}" for k, v in item.items()
                    )
                    lines.append(f"{pad}  - {summary}")
            else:
                lines.append(f"{pad}- **{label}**: {', '.join(str(v) for v in value)}")
        else:
            lines.append(f"{pad}- **{label}**: {value}")
    return lines
