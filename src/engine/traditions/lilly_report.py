"""William Lilly's *Christian Astrology*, Book 1 — the apparatus, on a nativity.

Thirty-four mined rules and no engine. The pack is unusual in this corpus for
needing no translation at all: Lilly wrote in English, so every rule carries his
own words and the rendering grade problem that gates every other non-English
track simply does not arise here.

It carries a different problem instead, and it is the reason this report is
shaped the way it is. Book 1 is the general apparatus, and a large part of what
it teaches — the considerations before judgment, the modes of perfection,
prohibition and refranation — is HORARY method. Those answer a question asked
at a moment; they do not describe a person born at one. Running them over a
nativity because the chart happens to have planets in it would be a category
error, and the sort that produces confident output.

So they are named as horary and not applied, and what IS applied is the part of
Book 1 that judges a planet's condition in any chart: the essential dignities
with Lilly's own point scores, the accidental fortitudes and debilities, and the
conditions — combustion, cazimi, under the sunbeams, orientality, hayz,
besieging, peregrination.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from ..multitradition import build_panel
from ..multitradition.types import BirthInput
from .report import Delineation, ReportSection, TraditionReport

RESEARCH_ROOT = (
    Path(__file__).resolve().parents[3] / "docs" / "research" / "multitradition"
)
LILLY_DIR = RESEARCH_ROOT / "latin_european"

#: Book 1 material that belongs to a horary question, not to a nativity. Named
#: rather than silently dropped, because their absence is a judgment.
HORARY_ONLY = {
    "lilly.ca1.considerations_before_judgment":
        "whether a question is fit to be judged at all",
    "lilly.ca1.perfection_modes":
        "how a horary question comes to perfection",
    "lilly.ca1.prohibition": "prohibition, which frustrates a perfection",
    "lilly.ca1.refranation": "refranation, likewise",
    "lilly.ca1.frustration": "frustration",
    "lilly.ca1.collection_of_light": "collection of light",
    "lilly.ca1.translation_of_light": "translation of light",
    "lilly.ca1.void_of_course": "the void-of-course Moon",
}

#: The conditions Book 1 defines that DO apply to any chart.
CONDITION_RULES = (
    ("lilly.ca1.combustion", "combustion"),
    ("lilly.ca1.cazimi", "cazimi, the heart of the Sun"),
    ("lilly.ca1.under_sunbeams", "being under the sunbeams"),
    ("lilly.ca1.oriental_occidental", "orientality and occidentality"),
    ("lilly.ca1.hayz", "hayz"),
    ("lilly.ca1.besieging", "besieging"),
    ("lilly.ca1.peregrine", "peregrination"),
    ("lilly.ca1.reception", "reception"),
)

PLANET_NATURES = (
    ("lilly.ca1.saturn_nature", "Saturn"),
    ("lilly.ca1.jupiter_nature", "Jupiter"),
    ("lilly.ca1.mars_nature", "Mars"),
    ("lilly.ca1.sun_nature", "the Sun"),
    ("lilly.ca1.venus_nature", "Venus"),
    ("lilly.ca1.mercury_nature", "Mercury"),
    ("lilly.ca1.moon_nature", "the Moon"),
)


@lru_cache(maxsize=1)
def _rules() -> dict[str, dict[str, Any]]:
    rules: dict[str, dict[str, Any]] = {}
    for path in sorted(LILLY_DIR.glob("*rule_manifest.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for rule in data.get("rules", []):
            rid = rule.get("rule_id")
            if rid:
                rules[rid] = rule
    return rules


def _quote(rule_id: str, trigger: str) -> Delineation | None:
    """Lilly's own words. No engine translation is involved anywhere here."""
    rule = _rules().get(rule_id)
    if rule is None:
        return None
    c = rule.get("conclusion") or {}
    text = c.get("quote")
    if not isinstance(text, str) or not text.strip():
        return None
    return Delineation(
        text=text.strip(),
        rule_id=rule_id,
        source="Lilly, Christian Astrology (1647), Book 1",
        evidence_grade=rule.get("evidence_grade", "?"),
        trigger=trigger,
    )


def _facts(birth: BirthInput) -> dict[str, Any]:
    panel = build_panel(birth)
    section = next(
        (
            s for s in panel["sections"]
            if s["tradition_id"] == "latin_european" and not s.get("error")
        ),
        None,
    )
    if section is None:
        raise RuntimeError("the Latin-European calculation produced no facts")
    return section["facts"]


def build_report(birth: BirthInput) -> TraditionReport:
    facts = _facts(birth)
    report = TraditionReport(
        tradition_id="latin_european",
        display_name="Latin European — Lilly's Christian Astrology, Book 1",
        birth=birth.to_dict(),
    )
    _opening(report, birth, facts)
    _dignity_section(report, facts)
    _conditions_section(report)
    _natures_section(report)
    _horary_boundary_section(report)
    _limits_section(report)
    return report


def _opening(
    report: TraditionReport, birth: BirthInput, facts: dict
) -> None:
    s = report.add(ReportSection("The Figure", level=2))
    asc = facts.get("ascendant") or {}
    s.notes.append(
        f"Born {birth.civil_date} at {birth.civil_time} in "
        f"{birth.place_label}. The Ascendant is {asc.get('degree_in_sign', 0):.2f}° "
        f"{asc.get('sign')}, and the houses are "
        f"**{facts.get('house_system')}** — the quadrant system Lilly uses, "
        "not whole sign."
    )
    cusps = facts.get("quadrant_cusps") or []
    if cusps:
        s.notes.append(
            "Cusps: "
            + "; ".join(
                f"{c['house']} at {c['degree_in_sign']:.1f}° {c['sign']}"
                for c in cusps
            )
            + "."
        )
    s.notes.append(
        "Lilly's own English is quoted throughout. This is the one track in "
        "the corpus where no engine translation stands between the source and "
        "the reader, so nothing here carries an unreviewed-rendering caveat."
    )


def _dignity_section(report: TraditionReport, facts: dict) -> None:
    s = report.add(ReportSection("Essential Dignity, Lilly's Scores", level=2))
    for rule_id, trigger in (
        ("lilly.ca1.essential_dignity_points", "how the dignities are scored"),
        ("lilly.ca1.terms_source_ptolemaic", "which terms Lilly prints"),
    ):
        d = _quote(rule_id, trigger)
        if d:
            s.delineations.append(d)

    for row in facts.get("lilly_essential_dignity") or []:
        held = row.get("dignities_held") or []
        s.notes.append(
            f"- **{row['body']}** in {row['sign']} "
            f"{row['degree_in_sign']:.2f}° — {row['essential_score']:+d}"
            + (f" ({', '.join(held)})" if held else "")
            + "."
        )
    strongest = facts.get("strongest_by_essential_dignity") or {}
    if strongest.get("body"):
        s.notes.append(
            f"Strongest by essential dignity: **{strongest['body']}** at "
            f"{strongest.get('score'):+d}. That measures a planet's condition "
            "in its own place. It is not on its own a verdict about the "
            "native, and Lilly's own judgment layer for that sits in Book 3, "
            "which this corpus does not hold."
        )
    comparison = facts.get("third_party_comparison") or {}
    if comparison.get("compared_against"):
        s.notes.append(
            f"Cross-checked against {comparison['compared_against']}: "
            f"{comparison.get('agreement')}."
        )
        if comparison.get("divergence"):
            s.notes.append(
                "Where they diverge, the reason is known and recorded: "
                + str(comparison["divergence"])
            )


def _conditions_section(report: TraditionReport) -> None:
    s = report.add(ReportSection("The Conditions of a Planet", level=2))
    s.notes.append(
        "Book 1's definitions of the states a planet can be in. These hold in "
        "any figure, which is why they are quoted here and the horary "
        "apparatus below is not."
    )
    for rule_id, trigger in CONDITION_RULES:
        d = _quote(rule_id, trigger)
        if d:
            s.delineations.append(d)
    for rule_id in ("lilly.ca1.orb_table", "lilly.ca1.separation_and_moieties"):
        d = _quote(rule_id, "the orbs the conditions are measured within")
        if d:
            s.delineations.append(d)


def _natures_section(report: TraditionReport) -> None:
    s = report.add(ReportSection("The Natures of the Seven", level=2))
    for rule_id, name in PLANET_NATURES:
        d = _quote(rule_id, f"Lilly on the nature of {name}")
        if d:
            s.delineations.append(d)
    s.notes.append(
        "Lilly gives each planet a sect and a benefic or malefic character "
        "alongside its qualities, and both are carried on the rules rather "
        "than flattened into the prose."
    )


def _horary_boundary_section(report: TraditionReport) -> None:
    """Named and not applied. The distinction is the judgment."""
    s = report.add(
        ReportSection("What Book 1 Teaches That This Is Not", level=2)
    )
    s.notes.append(
        "A large part of Book 1 is HORARY method: it judges a question asked "
        "at a moment, not a person born at one. Those rules are mined and "
        "held, and they are deliberately NOT run over this nativity — a "
        "consideration before judgment has nothing to say about a birth, and "
        "applying it would produce output that looked like a finding."
    )
    present = [
        (rid, what) for rid, what in HORARY_ONLY.items() if rid in _rules()
    ]
    for _, what in present:
        s.notes.append(f"- {what[0].upper()}{what[1:]}.")
    s.notes.append(
        f"{len(present)} of the pack's rules sit in that category. They are "
        "available to a horary engine and this report is not one."
    )


def _limits_section(report: TraditionReport) -> None:
    s = report.add(ReportSection("What This Report Does Not Claim", level=2))
    s.notes.append(
        "This is Book 1 only — the apparatus. Lilly's natal delineation is in "
        "Book 3 and is not in this corpus, so nothing here says what any of "
        "these conditions MEANS for this native. The conditions are defined "
        "and the dignities are scored; the judgment they would feed is absent."
    )
    s.notes.append(
        "The accidental fortitude and debility tables are quoted and are not "
        "yet computed against this chart. Lilly's own scores are printed here "
        "so the arithmetic can be checked when it is."
    )
    for rule_id in (
        "lilly.ca1.accidental_fortitude_points",
        "lilly.ca1.accidental_debility_points",
    ):
        d = _quote(rule_id, "the accidental scores, quoted and not yet applied")
        if d:
            s.delineations.append(d)
