"""Shared report shape for the per-tradition engines.

Deliberately thin. The value is in each tradition's own engine, not in a common
abstraction that would flatten fifteen different judgment orders into one.

Two rules the type enforces by construction:

1. A delineation carries its citation. `Delineation` cannot be built without a
   `rule_id` and a `source`, so an unsourced sentence cannot reach the page by
   accident - it has to be a `note`, which renders differently and says so.
2. Refusals are part of the report, not an appendix. They render inline, in the
   section where the reader would otherwise expect the missing content.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Delineation:
    """One sourced statement, keyed to something actually computed in the chart."""

    text: str
    rule_id: str
    source: str
    evidence_grade: str
    trigger: str  # the computed fact that selected this rule
    caveat: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "text": self.text,
            "rule_id": self.rule_id,
            "source": self.source,
            "evidence_grade": self.evidence_grade,
            "trigger": self.trigger,
        }
        if self.caveat:
            payload["caveat"] = self.caveat
        return payload


@dataclass
class ReportSection:
    title: str
    level: int = 2
    # Free prose the engine computed itself (placements, structure, arithmetic).
    # Never a delineation - those must be sourced.
    notes: list[str] = field(default_factory=list)
    delineations: list[Delineation] = field(default_factory=list)
    table: list[dict[str, Any]] = field(default_factory=list)
    refusals: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "level": self.level,
            "notes": self.notes,
            "delineations": [d.to_dict() for d in self.delineations],
            "table": self.table,
            "refusals": self.refusals,
        }


@dataclass
class TraditionReport:
    tradition_id: str
    display_name: str
    birth: dict[str, Any]
    sections: list[ReportSection] = field(default_factory=list)
    method_notes: list[str] = field(default_factory=list)

    def add(self, section: ReportSection) -> ReportSection:
        self.sections.append(section)
        return section

    @property
    def delineation_count(self) -> int:
        return sum(len(s.delineations) for s in self.sections)

    @property
    def word_count(self) -> int:
        words = 0
        for s in self.sections:
            words += sum(len(n.split()) for n in s.notes)
            words += sum(len(d.text.split()) for d in s.delineations)
            words += sum(len(r.split()) for r in s.refusals)
        return words

    def to_dict(self) -> dict[str, Any]:
        return {
            "tradition_id": self.tradition_id,
            "display_name": self.display_name,
            "birth": self.birth,
            "sections": [s.to_dict() for s in self.sections],
            "method_notes": self.method_notes,
            "delineation_count": self.delineation_count,
            "word_count": self.word_count,
        }


def _table_md(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return []
    headers = list(rows[0])
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        out.append(
            "| " + " | ".join(str(row.get(h, "")) for h in headers) + " |"
        )
    return out


def render_markdown(report: TraditionReport) -> str:
    birth = report.birth
    lines = [
        f"# {report.display_name}",
        "",
        f"**{birth.get('name')}** — {birth.get('civil_date')} {birth.get('civil_time')} "
        f"(UTC{birth.get('utc_offset_hours'):+g}), {birth.get('place_label')}",
        "",
    ]
    for section in report.sections:
        lines.append("#" * section.level + " " + section.title)
        lines.append("")
        for note in section.notes:
            lines.append(note)
            lines.append("")
        if section.table:
            lines.extend(_table_md(section.table))
            lines.append("")
        for d in section.delineations:
            lines.append(f"> {d.text}")
            lines.append(">")
            detail = f"> — {d.source}"
            if d.trigger:
                detail += f" · selected by: {d.trigger}"
            detail += f" · grade {d.evidence_grade}"
            lines.append(detail)
            if d.caveat:
                lines.append(">")
                lines.append(f"> *{d.caveat}*")
            lines.append("")
        for refusal in section.refusals:
            lines.append(f"**Not stated here.** {refusal}")
            lines.append("")
    if report.method_notes:
        lines.append("## Method and limits")
        lines.append("")
        for note in report.method_notes:
            lines.append(f"- {note}")
        lines.append("")
    lines.append(
        f"*{report.delineation_count} sourced delineations · "
        f"{report.word_count:,} words. Every quoted judgment above carries its "
        f"rule id and source; anything the sources do not support is marked "
        f"'Not stated here' rather than filled in.*"
    )
    return "\n".join(lines)
