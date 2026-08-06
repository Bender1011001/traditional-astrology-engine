"""Rhetorius of Egypt — the Byzantine compilation, in his own inspection order.

Thirty-one mined rules and no engine. The pack's most useful single fact is
structural: Rhetorius states his own judgment hierarchy — the seven inspections
— and closes it by saying that examining them in this way is how you avoid
going wrong about the foundations of the nativity. So this report runs in that
order rather than in the order this engine happens to compute things.

Every rendering here shows the Greek beside it. That is not decoration: the
grade on all of them is `engine_translation_unreviewed`, and the only thing
that makes such a grade honest rather than an excuse is putting the original
where it can be checked.

What this track does NOT have is a worked nativity. The Hellenistic corpus's
worked charts are Valens', not Rhetorius', so nothing here reproduces a stated
judgment of his on a known figure. That is the real gap in this track and it is
a mining target — the codices exist — not a permanent condition.
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
BYZ_DIR = RESEARCH_ROOT / "byzantine"


@lru_cache(maxsize=1)
def _rules() -> dict[str, dict[str, Any]]:
    rules: dict[str, dict[str, Any]] = {}
    for path in sorted(BYZ_DIR.glob("*rule_manifest.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for rule in data.get("rules", []):
            rid = rule.get("rule_id")
            if rid:
                rules[rid] = rule
    return rules


def _fire(rule_id: str, trigger: str) -> Delineation | None:
    """Quote a rule, with its Greek attached where the pack carries it."""
    rule = _rules().get(rule_id)
    if rule is None:
        return None
    c = rule.get("conclusion") or {}
    text = c.get("engine_rendering") or c.get("judgment")
    if not isinstance(text, str) or not text.strip():
        return None
    greek = c.get("greek") or c.get("greek_key")
    body = text.strip()
    if isinstance(greek, str) and greek.strip():
        # The rendering is unreviewed; showing the original is what makes that
        # grade a label rather than an excuse.
        body = f"{body}\n\n> {greek.strip()}"
    return Delineation(
        text=body,
        rule_id=rule_id,
        source="Rhetorius of Egypt, Compendium (Byzantine codices)",
        evidence_grade=rule.get("evidence_grade", "?"),
        trigger=trigger,
    )


def _facts(birth: BirthInput) -> dict[str, Any]:
    """Rhetorius reads a Hellenistic figure; the panel already computes one."""
    panel = build_panel(birth)
    section = next(
        (
            s for s in panel["sections"]
            if s["tradition_id"] == "hellenistic" and not s.get("error")
        ),
        None,
    )
    if section is None:
        raise RuntimeError("no Hellenistic figure was computed")
    return section["facts"]


def build_report(birth: BirthInput) -> TraditionReport:
    facts = _facts(birth)
    report = TraditionReport(
        tradition_id="byzantine",
        display_name="Byzantine — Rhetorius of Egypt, the Seven Inspections",
        birth=birth.to_dict(),
    )
    _opening(report, birth, facts)
    _sect_section(report, facts)
    _places_section(report)
    _lots_section(report)
    _doctrine_section(report)
    _limits_section(report)
    return report


def _opening(report: TraditionReport, birth: BirthInput, facts: dict) -> None:
    s = report.add(ReportSection("The Seven Inspections", level=2))
    asc = facts.get("ascendant") or {}
    s.notes.append(
        f"Born {birth.civil_date} at {birth.civil_time} in "
        f"{birth.place_label}. The Ascendant is "
        f"{asc.get('degree_in_sign', 0):.2f}° {asc.get('sign')}, and the "
        f"nativity is {facts.get('sect')}."
    )
    for rule_id, trigger in (
        ("byz.rhet.p.pinax.seven_inspections_order",
         "Rhetorius states his own order of judgment"),
        ("byz.rhet.p.pinax.inspection1_opening_sequence",
         "and what the first inspection opens with"),
    ):
        d = _fire(rule_id, trigger)
        if d:
            s.delineations.append(d)
    s.notes.append(
        "This report follows that order rather than the order the engine "
        "computes in. Flattening a tradition's hierarchy into parallel "
        "bullet points is the reliable tell of a synthetic reading, and "
        "Rhetorius is unusually explicit about what his hierarchy is."
    )


def _sect_section(report: TraditionReport, facts: dict) -> None:
    s = report.add(ReportSection("Sect and Its Leaders", level=2))
    d = _fire(
        "byz.rhet.l.sect_leaders_by_day_and_night",
        "who leads each sect",
    )
    if d:
        s.delineations.append(d)
    rule = _rules().get("byz.rhet.l.sect_leaders_by_day_and_night")
    if rule:
        c = rule.get("conclusion") or {}
        is_day = facts.get("sect") == "day"
        leaders = c.get("day_sect_leaders" if is_day else "night_sect_leaders")
        if leaders:
            s.notes.append(
                f"This is a {facts.get('sect')} nativity, so the sect leaders "
                f"are {', '.join(leaders)}. Mercury "
                f"{c.get('mercury', 'is common to both')}."
            )
    d = _fire(
        "byz.rhet.l.benefic_malefic_are_nominal_categories",
        "what benefic and malefic actually name",
    )
    if d:
        s.delineations.append(d)
    d = _fire(
        "byz.rhet.p.birth_ease_by_sect_and_gender",
        "the ease of the birth itself, by sect",
    )
    if d:
        s.delineations.append(d)


def _places_section(report: TraditionReport) -> None:
    s = report.add(ReportSection("The Twelve Places", level=2))
    s.notes.append(
        "The Byzantine presentation enumerates the places in REVERSE and "
        "carries a third name for the twelfth, metakosmios — beyond the "
        "world. The codices of the second class credit the doctrine to "
        "Hermes, and the pack carries that attribution rather than "
        "presenting it as Rhetorius' own."
    )
    for rule_id, trigger in (
        ("byz.rhet.p.twelfth_place_names_and_significations",
         "the twelfth place, which the reversed order puts first"),
        ("byz.rhet.p.dodekatopos_names_and_significations",
         "the places and what each signifies"),
        ("byz.rhet.l.four_angles_elemental_blend",
         "the four angles and their elemental blend"),
    ):
        d = _fire(rule_id, trigger)
        if d:
            s.delineations.append(d)


def _lots_section(report: TraditionReport) -> None:
    s = report.add(ReportSection("The Lots and Their Lords", level=2))
    for rule_id, trigger in (
        ("byz.rhet.p.lots_first_age_lords_last_age",
         "which lot governs which age"),
        ("byz.rhet.p.fortune_lord_placement_source_of_gain",
         "the lord of Fortune, and where gain comes from"),
        ("byz.rhet.p.lot_of_anairetes_formula_and_moon_application",
         "the Lot of the Anairetes"),
        ("byz.rhet.p.aitiatikos_lot_formula", "the aitiatikos lot"),
        ("byz.rhet.p.annual_distribution_multiple_origins",
         "the annual distribution, which he draws from several origins"),
    ):
        d = _fire(rule_id, trigger)
        if d:
            s.delineations.append(d)
    s.refusals.append(
        "The lots above are quoted as doctrine and are NOT cast for this "
        "nativity. Several key to house cusps or to a prenatal syzygy this "
        "engine does not compute, and casting the rest while omitting those "
        "would present a partial set as a complete one."
    )


def _doctrine_section(report: TraditionReport) -> None:
    s = report.add(ReportSection("Rhetorius on Method", level=2))
    for rule_id, trigger in (
        ("byz.epit.moon_kenodromia_definition",
         "the Moon running void (kenodromia)"),
        ("byz.epit.moon_syndesmos_definition", "the binding and the loosing"),
        ("byz.rhet.p.orthos_and_plagios_signs",
         "the straight and the crooked signs"),
        ("byz.epit.ptolemy_canonised_as_law_and_rule",
         "how the compiler regards Ptolemy"),
        ("byz.epit.book_evaluation_requires_experience",
         "what the compiler says a book is worth without practice"),
        ("byz.epit.antiochus_dating_verdict_is_unreliable",
         "and where the compilation's own dating cannot be trusted"),
    ):
        d = _fire(rule_id, trigger)
        if d:
            s.delineations.append(d)


def _limits_section(report: TraditionReport) -> None:
    s = report.add(ReportSection("What This Report Does Not Claim", level=2))
    s.notes.append(
        "**There is no worked nativity of Rhetorius' in this corpus.** The "
        "Hellenistic worked charts belong to Valens. So nothing here "
        "reproduces a judgment Rhetorius himself made about a known figure, "
        "which is the strongest check this project has and the one this track "
        "cannot yet pass. The codices exist; this is a mining target."
    )
    s.notes.append(
        "Every rendering shows its Greek. The renderings are graded as "
        "unreviewed engine translations, and the original is printed beside "
        "each one precisely so that grade means *check this* rather than "
        "*trust this*."
    )
    unresolved = _rules().get("byz.rhet.p.poleuon_hour_lord_unresolved")
    if unresolved:
        s.refusals.append(
            "The poleuon — the hour lord — is left unresolved by the pack, so "
            "no hour lord is named here. Rhetorius' text gives the candidates "
            "and the codices do not agree on the rule."
        )
