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

import re
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Clause-level output policy.
#
# The corpus-wide publication policy refuses lifespan/death claims about a
# living person. Rule-level suppression alone proved insufficient: an ordinary
# placement aphorism can smuggle "short-lived" into the report through a rule
# whose CATEGORY is unobjectionable. So the policy is enforced semantically, on
# every clause of every delineation, at construction time - Delineation is the
# only type that can carry sourced text to the page, so redacting in its
# __post_init__ closes every rendering path at once, including to_dict/JSON.
#
# Redaction is clause-level, not statement-level: the rest of the verse is
# real sourced content and survives; only the refused clause is replaced, with
# the topic named so the withholding is auditable.
# ---------------------------------------------------------------------------

REFUSED_TOPIC_PATTERNS: dict[str, re.Pattern[str]] = {
    "longevity": re.compile(
        r"\b(short[\s-]?lived|long[\s-]?lived|not\s+(be\s+)?long[\s-]?lived|"
        r"long\s+lease\s+of\s+life|(span|length)\s+of\s+(his\s+)?life|"
        r"longevity|lives?\s+to\s+(a\s+great\s+age|\d+)|"
        r"full\s+span\s+of\s+years|medium\s+life)\b",
        re.IGNORECASE,
    ),
    "death": re.compile(
        r"\b(dies?\b|death|deceases?|does\s+not\s+(live|survive)|"
        r"loss\s+of\s+life|end\s+of\s+(his|her|the)\s+life|maraka)\b",
        re.IGNORECASE,
    ),
}
_CLAUSE_SPLIT = re.compile(r"([;.!?]|\s+—\s+)")


def redact_refused_topics(text: str) -> tuple[str, list[str]]:
    """Replace clauses carrying refused topics; return (text, topics_redacted).

    A clause is the span between clause punctuation. Splitting keeps the
    delimiters so the surviving text reads naturally.
    """
    parts = _CLAUSE_SPLIT.split(text)
    redacted: list[str] = []
    out: list[str] = []
    for part in parts:
        hit = next(
            (topic for topic, pattern in REFUSED_TOPIC_PATTERNS.items()
             if pattern.search(part)),
            None,
        )
        if hit and not _CLAUSE_SPLIT.fullmatch(part or " "):
            out.append(f"[{hit} clause withheld per publication policy]")
            if hit not in redacted:
                redacted.append(hit)
        else:
            out.append(part)
    return "".join(out), redacted


@dataclass(frozen=True)
class Delineation:
    """One sourced statement, keyed to something actually computed in the chart.

    Construction redacts refused-topic clauses (lifespan, death) and records
    which topics were withheld - so no engine, renderer or serializer can leak
    a refused clause, because the unredacted text never survives construction.
    """

    text: str
    rule_id: str
    source: str
    evidence_grade: str
    trigger: str  # the computed fact that selected this rule
    caveat: str | None = None
    topics_redacted: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        clean, topics = redact_refused_topics(self.text)
        if topics:
            object.__setattr__(self, "text", clean)
            object.__setattr__(self, "topics_redacted", tuple(topics))

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
        if self.topics_redacted:
            payload["topics_redacted"] = list(self.topics_redacted)
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


def render_layered(report: TraditionReport) -> str:
    """Three outputs from one dataset (review finding 16).

    Part I  READING - synthesis and structural notes; only supported
                      conclusions, no audit language, no citations apparatus.
    Part II EVIDENCE - every quoted delineation with citation, trigger,
                      grade and table, grouped under its section.
    Part III AUDIT  - refusals (with their categories), withheld content
                      notices, method notes and configuration.

    The evidence database stays relational; the reader is no longer asked to
    process forty-two refusals before finding out what the system can say.
    """
    from .readiness import classify

    birth = report.birth
    # What kind of document this is, decided by what it contains rather than
    # by what the product category wishes it were. Seven documents under one
    # "full reading" heading, when one of them delineates nothing, misleads by
    # arrangement even when every sentence in them is true.
    kind = classify(report)
    lines = [
        f"# {report.display_name}",
        "",
        f"**{birth.get('name')}** — {birth.get('civil_date')} {birth.get('civil_time')} "
        f"(UTC{birth.get('utc_offset_hours'):+g}), {birth.get('place_label')}",
        "",
        f"> **{kind.label}.** {kind.explanation}",
        "",
        f"## Part I — {kind.label}",
        "",
    ]
    for section in report.sections:
        if not section.notes:
            continue
        lines.append("#" * min(section.level + 1, 4) + " " + section.title)
        lines.append("")
        for note in section.notes:
            lines.append(note)
            lines.append("")

    lines += ["## Part II — Evidence", ""]
    for section in report.sections:
        if not section.delineations and not section.table:
            continue
        lines.append("#" * min(section.level + 1, 4) + " " + section.title)
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
            if d.topics_redacted:
                lines.append(">")
                lines.append(
                    "> *The source also states a "
                    + " and a ".join(d.topics_redacted)
                    + " result here; it is withheld by publication policy.*"
                )
            if d.caveat:
                lines.append(">")
                lines.append(f"> *{d.caveat}*")
            lines.append("")

    lines += ["## Part III — Audit", ""]
    any_refusal = False
    for section in report.sections:
        for refusal in section.refusals:
            any_refusal = True
            lines.append(f"- **{section.title}**: {refusal}")
    if any_refusal:
        lines.append("")
    if report.method_notes:
        lines.append("### Method and limits")
        lines.append("")
        for note in report.method_notes:
            lines.append(f"- {note}")
        lines.append("")
    lines.append(
        f"*{report.delineation_count} sourced delineations · "
        f"{report.word_count:,} words. Every quoted judgment in Part II carries "
        f"its rule id and source; everything the sources do not support is in "
        f"Part III rather than filled in.*"
    )
    return "\n".join(lines)


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
            if d.topics_redacted:
                lines.append(">")
                lines.append(
                    "> *The source also states a "
                    + " and a ".join(d.topics_redacted)
                    + " result here; it is withheld by publication policy.*"
                )
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
