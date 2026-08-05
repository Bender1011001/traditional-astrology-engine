"""A Hellenistic report, judged in the tradition's own order.

Sect is the first judgment - Firmicus says so in as many words, and the report
opens there. Then the Ascendant and the whole-sign topics, then each of the
seven planets in its sign, house, bounds, face and sect-standing, then the
Hermetic lots. Delineation is quoted from Firmicus (Latin, Kroll/Skutsch) and
Ptolemy (Greek, Boll/Boer) with rule ids; the Mathesis delineation manifest is
loaded WHEN PRESENT, so the report grows as extraction lands without an engine
change. Firmicus' sect-splits are honoured: a cell that differentiates by day
and by night is selected by the chart's actual sect.

Valens now speaks too. His Anthologiae pack was mined from page images after
the OCR proved to hold zero Greek codepoints, and his topical chapters on
marriage and foreign travel are judged against the chart in his own vocabulary
(see valens_facts). That judgment is tri-valued on purpose: he leans on a
distribution of times this engine does not compute, so a rule gated on a
chronocrator comes back undecided and is REPORTED undecided, never counted as
ruled out. Rules whose conditions the engine cannot decide are listed as
undecided rather than fired because they sound apt.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from ..multitradition import build_panel
from ..multitradition.types import BirthInput
from .report import Delineation, ReportSection, TraditionReport
from .synthesis import synthesize
from .valens_facts import CONFIGURED_METHODS, ValensChart, evaluate

RESEARCH_ROOT = (
    Path(__file__).resolve().parents[3] / "docs" / "research" / "multitradition"
)
HELLENISTIC_RESEARCH = RESEARCH_ROOT / "hellenistic"
DOCTRINE_MANIFEST = HELLENISTIC_RESEARCH / "delineation_rule_manifest.json"
MATHESIS_MANIFEST = (
    HELLENISTIC_RESEARCH / "mathesis_delineation_rule_manifest.json"
)
VALENS_MANIFEST = (
    HELLENISTIC_RESEARCH / "valens_delineation_rule_manifest.json"
)


def _manifest_paths() -> list[Path]:
    """Every rule manifest in the Hellenistic research directory.

    Globbed rather than listed so a new extraction pass is picked up without an
    engine change; the two named packs are kept first so their ids win any tie.
    """
    named = [DOCTRINE_MANIFEST, MATHESIS_MANIFEST, VALENS_MANIFEST]
    found = sorted(HELLENISTIC_RESEARCH.glob("*rule_manifest.json"))
    return named + [p for p in found if p not in named]

ORDINAL = {
    1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th",
    7: "7th", 8: "8th", 9: "9th", 10: "10th", 11: "11th", 12: "12th",
}
ANGLES = (1, 4, 7, 10)
FIRE_SIGNS = {"Aries", "Leo", "Sagittarius"}


@lru_cache(maxsize=1)
def _rules_by_id() -> dict[str, dict[str, Any]]:
    rules: dict[str, dict[str, Any]] = {}
    for path in _manifest_paths():
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            for r in data.get("rules", []):
                rules.setdefault(r["rule_id"], r)
    return rules


def _source_label(rule: dict[str, Any]) -> str:
    passages = rule.get("source_passages") or []
    if not passages:
        return rule.get("rule_id", "unknown")
    p = passages[0]
    return f"{p.get('work', 'Mathesis')}, {p.get('location') or p.get('section') or ''}".strip().rstrip(",")


def _fire(
    rule_id: str, trigger: str, text_key: str | None = None
) -> Delineation | None:
    rule = _rules_by_id().get(rule_id)
    if rule is None:
        return None
    c = rule.get("conclusion", {}) or {}
    policy = c.get("output_policy") or rule.get("output_policy")
    if isinstance(policy, str) and "refus" in policy.lower():
        return None
    text = None
    for key in ([text_key] if text_key else []) + ["engine_rendering", "judgment"]:
        if key and isinstance(c.get(key), str) and c[key].strip():
            text = c[key].strip()
            break
    if not text:
        return None
    return Delineation(
        text=text, rule_id=rule_id, source=_source_label(rule),
        evidence_grade=rule.get("evidence_grade", "?"), trigger=trigger,
    )


def _cell(
    rule_id: str, block: str, key: str, is_day: bool, trigger: str
) -> tuple[Delineation | None, str | None]:
    """A Mathesis delineation cell, honouring sect-splits and per-cell policy."""
    rule = _rules_by_id().get(rule_id)
    if rule is None:
        return None, None
    cell = (rule.get("conclusion", {}).get(block) or {}).get(str(key))
    if cell is None:
        return None, None
    if isinstance(cell, str):
        return _fire(rule_id, trigger) and Delineation(
            text=cell, rule_id=rule_id, source=_source_label(rule),
            evidence_grade=rule.get("evidence_grade", "?"), trigger=trigger,
        ), None
    if not isinstance(cell, dict):
        return None, None
    if str(cell.get("output_policy", "")).lower() == "refused":
        return None, (
            f"The source states a result here ({trigger}) and it is withheld: "
            f"{cell.get('output_policy_reason', 'the pack refuses this cell')}."
        )
    text = None
    sect_key = "by_day" if is_day else "by_night"
    other_key = "by_night" if is_day else "by_day"
    sub = cell.get(sect_key)
    if isinstance(sub, dict):
        # Sect-split sub-cells carry their own text and their own policy.
        if str(sub.get("output_policy", "")).lower() == "refused":
            return None, (
                f"The source states a result here ({trigger}, "
                f"{sect_key.replace('_', ' ')}) and it is withheld: "
                f"{sub.get('output_policy_reason', 'the pack refuses this cell')}."
            )
        if isinstance(sub.get("engine_rendering"), str):
            text = sub["engine_rendering"]
            trigger += f" · {sect_key.replace('_', ' ')}"
    elif isinstance(sub, str):
        text = sub
        trigger += f" · {sect_key.replace('_', ' ')}"
    elif isinstance(cell.get("engine_rendering"), str):
        text = cell["engine_rendering"]
    if not text:
        if cell.get(other_key) is not None and cell.get(sect_key) is None:
            # Firmicus stated a result for the OTHER sect only. Silence here
            # would look like a gap; the truth is a sect-conditional source.
            return None, (
                f"Firmicus differentiates by sect here ({trigger}) and states "
                f"a result only for {'nocturnal' if is_day else 'diurnal'} "
                "nativities; this chart is "
                f"{'diurnal' if is_day else 'nocturnal'}, so nothing is quoted."
            )
        return None, None
    return Delineation(
        text=text, rule_id=rule_id, source=_source_label(rule),
        evidence_grade=rule.get("evidence_grade", "?"), trigger=trigger,
    ), None


def _facts(birth: BirthInput) -> dict[str, Any]:
    panel = build_panel(birth)
    section = next(
        s for s in panel["sections"] if s["tradition_id"] == "hellenistic"
    )
    if section.get("error"):
        raise RuntimeError(f"Hellenistic calculation failed: {section['error']}")
    return section["facts"]


def build_report(birth: BirthInput) -> TraditionReport:
    facts = _facts(birth)
    report = TraditionReport(
        tradition_id="hellenistic",
        display_name="Hellenistic — Structural Reading with Classical Testimonies",
        birth=birth.to_dict(),
    )
    is_day = facts.get("sect") == "day"
    placements = facts.get("placements", [])

    _sect_section(report, facts, is_day, placements)
    _ascendant_section(report, facts)
    _planets_section(report, facts, is_day, placements)
    _lots_section(report, facts, is_day)
    _valens_doctrine_section(report, facts, is_day)
    _valens_topic_section(
        report, facts, "marriage", "Marriage, after Valens", "b2.marriage"
    )
    _valens_topic_section(
        report, facts, "foreign travel", "Foreign Travel, after Valens",
        "b2.travel",
    )
    _undecided_section(report)
    fired = [d for s in report.sections for d in s.delineations]
    report.sections.insert(1, synthesize(fired, None, tradition="hellenistic"))
    _limits(report)
    return report


def _sect_section(
    report: TraditionReport, facts: dict, is_day: bool, placements: list
) -> None:
    s = report.add(ReportSection("Sect — the First Judgment", level=2))
    s.notes.append(
        f"This is a **{'diurnal' if is_day else 'nocturnal'}** nativity; the "
        f"sect light is the {'Sun' if is_day else 'Moon'}. Firmicus makes sect "
        "the first thing judged for every planet, and this report follows him."
    )
    d = _fire(
        "hel.firmicus.sect_first_judgment_hierarchy",
        "the tradition's own judgment order, applied to every planet below",
    )
    if d:
        s.delineations.append(d)
    if is_day:
        d = _fire(
            "hel.firmicus.sect_diurnal_trio_and_lacuna",
            "a diurnal nativity: Sun, Jupiter and Saturn are of the sect in favour",
        )
        if d:
            s.delineations.append(d)
    else:
        d = _fire(
            "hel.ptolemy.sect_diurnal_nocturnal_assignment",
            "a nocturnal nativity: Moon, Venus and Mars are of the sect in favour",
        )
        if d:
            s.delineations.append(d)
    sect_light_sign = next(
        (p["sign"] for p in placements
         if p["body"] == ("Sun" if is_day else "Moon")), None,
    )
    if sect_light_sign in FIRE_SIGNS:
        d = _fire(
            "hel.ptolemy.triplicity_fire_sun_jupiter_mars_participant",
            f"the sect light stands in {sect_light_sign}, a fire-trigon sign",
        )
        if d:
            s.delineations.append(d)


def _ascendant_section(report: TraditionReport, facts: dict) -> None:
    s = report.add(ReportSection("The Ascendant and the Twelve Topics", level=2))
    asc = facts.get("ascendant", {})
    mc = facts.get("midheaven", {})
    s.notes.append(
        f"The Ascendant rises at **{asc.get('sign')} "
        f"{asc.get('degree_in_sign', 0):.2f}°**; whole-sign houses follow from "
        f"it, which is the Hellenistic norm. The quadrant Midheaven falls at "
        f"{mc.get('sign')} {mc.get('degree_in_sign', 0):.2f}° and is read as a "
        "degree of eminence, not a cusp."
    )


def _planets_section(
    report: TraditionReport, facts: dict, is_day: bool, placements: list
) -> None:
    report.add(ReportSection("The Seven Planets", level=2)).table = [
        {
            "Planet": p["body"],
            "Sign": f"{p['sign']} {p['degree_in_sign']:.1f}°",
            "House": p["whole_sign_house"],
            "Bound": p.get("bound_lord_egyptian", ""),
            "Face": p.get("face_lord", ""),
            "Sect standing": p.get("sect_status", ""),
            "Dignity": "domicile" if p.get("in_own_domicile")
                       else ("exaltation" if p.get("in_exaltation") else ""),
        }
        for p in placements
    ]
    for p in placements:
        sub = report.add(ReportSection(
            f"{p['body']} in {p['sign']}, {ORDINAL[p['whole_sign_house']]} house",
            level=3,
        ))
        bits = [
            f"{p['body']} stands at **{p['sign']} {p['degree_in_sign']:.2f}°** "
            f"in the {ORDINAL[p['whole_sign_house']]} whole-sign house, "
            f"{p.get('sect_status', '')}.",
            f"Bound lord {p.get('bound_lord_egyptian')}, face lord "
            f"{p.get('face_lord')}, Dorothean triplicity lord "
            f"{p.get('triplicity_lord_dorothean')}.",
        ]
        sub.notes.append(" ".join(bits))

        angular = p["whole_sign_house"] in ANGLES
        of_sect = "in favour" in str(p.get("sect_status", ""))
        if angular and of_sect:
            d = _fire(
                "hel.firmicus.sect_angular_felicity_or_calamity",
                f"{p['body']} is of the sect in favour AND angular "
                f"({ORDINAL[p['whole_sign_house']]})",
                text_key="if_favor",
            )
            if d:
                sub.delineations.append(d)
        elif angular and "contrary" in str(p.get("sect_status", "")):
            d = _fire(
                "hel.firmicus.sect_angular_felicity_or_calamity",
                f"{p['body']} is contrary to the sect AND angular "
                f"({ORDINAL[p['whole_sign_house']]})",
                text_key="if_contrary",
            )
            if d:
                sub.delineations.append(d)
        if p.get("in_own_domicile"):
            d = _fire(
                "hel.firmicus.domicile_table_and_gender_pairing",
                f"{p['body']} stands in its own domicile, {p['sign']}",
            )
            if d:
                sub.delineations.append(d)
        if p.get("in_exaltation"):
            d = _fire(
                "hel.firmicus.exaltation_degrees_table",
                f"{p['body']} stands in its exaltation, {p['sign']}",
            )
            if d:
                sub.delineations.append(d)
        if p.get("face_lord") == p["body"]:
            d = _fire(
                "hel.firmicus.decan_face_table_and_own_decan_doctrine",
                f"{p['body']} stands in its own decan",
            )
            if d:
                sub.delineations.append(d)
        # Mathesis cells (present once the extraction lands; sect-aware).
        planet_lower = p["body"].lower()
        d = _fire(
            f"hel.valens.b1.planet_nature.{planet_lower}",
            f"{p['body']}'s nature, stated by Valens",
        )
        if d:
            sub.delineations.append(d)
        for rid_pattern, block, key in (
            (f"hel.mathesis.b3.planet_in_house.{planet_lower}",
             "results_by_house", str(p["whole_sign_house"])),
            (f"hel.mathesis.b5.planet_in_sign.{planet_lower}",
             "results_by_sign", p["sign"]),
        ):
            d, refusal = _cell(
                rid_pattern, block, key, is_day,
                f"{p['body']} in the {ORDINAL[p['whole_sign_house']]} house"
                if block == "results_by_house"
                else f"{p['body']} in {p['sign']}",
            )
            if d:
                sub.delineations.append(d)
            elif refusal:
                sub.refusals.append(refusal)


def _lots_section(report: TraditionReport, facts: dict, is_day: bool) -> None:
    s = report.add(ReportSection("The Hermetic Lots", level=2))
    lots = facts.get("lots", {})
    rows = []
    for name, lot in lots.items():
        if isinstance(lot, dict):
            rows.append({
                "Lot": name.replace("_", " ").title(),
                "Sign": lot.get("sign", ""),
                "Degree": f"{lot.get('degree_in_sign', 0):.2f}°"
                          if lot.get("degree_in_sign") is not None else "",
                "House": lot.get("whole_sign_house", ""),
            })
    if rows:
        s.table = rows
    s.notes.append(
        "Fortune and Spirit reverse their formula by sect, which this chart's "
        "sect has already decided above."
    )
    # Valens states the Lot of Fortune doctrine conditioned on sect; his rule
    # carries conditions {chart.sect == day}, so fire it only when it matches.
    lot_rule = _rules_by_id().get("hel.valens.b2.lot_of_fortune")
    if lot_rule is not None:
        want = None
        for cond in (lot_rule.get("conditions", {}) or {}).get("all", []):
            if cond.get("fact") == "chart.sect":
                want = cond.get("value")
        if want is None or want == ("day" if is_day else "night"):
            d = _fire(
                "hel.valens.b2.lot_of_fortune",
                f"Valens' Lot of Fortune doctrine for a {'diurnal' if is_day else 'nocturnal'} chart",
            )
            if d:
                s.delineations.append(d)
        else:
            s.refusals.append(
                "Valens states his Lot of Fortune doctrine for "
                f"{want} nativities; this chart is "
                f"{'diurnal' if is_day else 'nocturnal'}, so his statement is "
                "not quoted here rather than being applied across the sect line."
            )


def _undecided_section(report: TraditionReport) -> None:
    s = report.add(ReportSection("Testimonies that could not be decided", level=2))
    s.notes.append(
        "These sourced rules exist and were NOT fired, because deciding them "
        "needs a fact this engine does not yet compute. Listed so the omission "
        "is visible rather than silent."
    )
    for rid, why in (
        ("hel.ptolemy.parents_same_sect_doryphoria_brilliance",
         "needs a doryphoria (bodyguarding) computation with sect filtering"),
        ("hel.ptolemy.parents_opposite_sect_doryphoria_instability",
         "needs the same doryphoria computation"),
        ("hel.ptolemy.children_alien_sect_places_humble",
         "needs orientality of the child-sign rulers"),
        ("hel.firmicus.domicile_lord_host_guest_doctrine",
         "needs a host-condition judgment (the dispositor's own strength) the "
         "engine states structurally but the rule words qualitatively"),
    ):
        if rid in _rules_by_id():
            s.notes.append(f"- `{rid}` — {why}")


def _limits(report: TraditionReport) -> None:
    mathesis_loaded = MATHESIS_MANIFEST.exists()
    report.method_notes.extend([
        "Delineations quote Firmicus Maternus (Mathesis, Kroll/Skutsch Latin "
        "critical edition, read directly) and Ptolemy (Apotelesmatika, "
        "Boll/Boer Greek, read directly), each as its own voice. Every "
        "rendering is graded engine_translation_unreviewed.",
        (
            "The Mathesis delineation manifest is loaded: Book III-VII cells "
            "fire against computed houses and signs, sect-selected."
            if mathesis_loaded else
            "The Mathesis Books III-VII delineation extraction is IN PROGRESS; "
            "this report currently fires doctrine rules only and will grow "
            "several hundred cells with no engine change when it lands."
        ),
        "Valens contributes ZERO rules: his 1908 OCR contains no Greek "
        "codepoints in 1.1 million characters (verified by counting). Page "
        "images are the only route to his sect doctrine and to any worked "
        "nativity - none exists anywhere in the fetched Hellenistic corpus.",
        "Ptolemy's Boll/Boer edition is a corrected reprint of the 1940 first "
        "edition; its US copyright status is genuinely unverified, and rules "
        "quote short passages under that stated uncertainty.",
        "Firmicus' Book II is missing chapters VIII-XIV against its own "
        "internal index - the loss is the manuscript tradition's, recorded in "
        "the corpus, and nothing is reconstructed to fill it.",
        "No numerical dignity score appears here: Valens and Dorotheus judge "
        "by condition, not points. The 5/4/3/2/1 table is al-Qabisi's and the "
        "scored version of this sky lives in the Latin-European section.",
    ])


def _valens_topic_section(
    report: TraditionReport, facts: dict, topic: str, title: str, tag: str
) -> None:
    """Judge Valens' topical chapter against this chart, tri-valued.

    Everything he states as a condition is tested; what fires is quoted, what
    the chart denies is counted, and what this engine cannot decide is named
    fact by fact rather than being folded in among the denials.
    """
    chart = ValensChart(facts)
    s = report.add(ReportSection(title, level=2))
    denied = 0
    undecided: dict[str, int] = {}
    for rule_id, rule in sorted(_rules_by_id().items()):
        if tag not in rule_id:
            continue
        conds = rule.get("conditions") or {}
        flat = [
            c for grp in conds.values() if isinstance(grp, list) for c in grp
        ]
        # Chapter headings and method statements are keyed on the topic itself
        # rather than on the chart; they frame the section, they do not judge.
        if any(
            c.get("fact") in ("chapter.topic", "technique.step") for c in flat
        ):
            d = _fire(rule_id, f"Valens opens his chapter on {topic}")
            if d:
                s.delineations.append(d)
            continue
        verdict, unknowns = evaluate(rule, chart)
        if verdict == "pass":
            d = _fire(rule_id, _valens_trigger(rule))
            if d:
                s.delineations.append(d)
            else:
                s.refusals.append(
                    f"{rule_id}: this chart meets Valens' conditions, but the "
                    "pack withholds the statement from publication."
                )
        elif verdict == "fail":
            denied += 1
        else:
            for fact_name in unknowns:
                undecided[fact_name] = undecided.get(fact_name, 0) + 1

    if not s.delineations and not undecided and not denied:
        report.sections.remove(s)
        return

    n = len(s.delineations)
    s.notes.insert(0, (
        f"{n} of Valens' statements on {topic} "
        f"{'is' if n == 1 else 'are'} met by this chart; {denied} "
        f"{'is' if denied == 1 else 'are'} ruled out by it."
    ))
    if undecided:
        top = sorted(undecided.items(), key=lambda kv: -kv[1])[:6]
        s.notes.append(
            f"{sum(undecided.values())} further conditions cannot be decided "
            "here. This engine does not compute Valens' distribution of times, "
            "so a rule gated on a chronocrator stays open instead of being "
            "counted against the chart. Most often wanted: "
            + ", ".join(f"{k} ({n})" for k, n in top) + "."
        )
    for method in sorted(chart.used_methods):
        s.notes.append("configured_method - " + CONFIGURED_METHODS[method])


def _valens_trigger(rule: dict) -> str:
    """Name the conditions that let this rule fire."""
    conds = rule.get("conditions") or {}
    flat = [c for grp in conds.values() if isinstance(grp, list) for c in grp]
    return "Valens' condition met: " + ", ".join(
        c.get("fact", "?") for c in flat[:3]
    )


def _valens_doctrine_section(
    report: TraditionReport, facts: dict, is_day: bool
) -> None:
    """Valens' method chapters, fired where the chart decides them.

    His triplicity lords, trigons and chronocrator doctrine are chart-general
    statements of method rather than per-placement cells, so they belong in
    their own section instead of being scattered through the planets.
    """
    s = report.add(ReportSection("Valens on Method", level=2))
    fired = 0
    for rule_id, trigger in (
        ("hel.valens.b2.triplicity_lords",
         "Valens' own triplicity-lord assignment"),
        ("hel.valens.b2.trigons", "Valens on the trigons"),
        ("hel.valens.b2.lord_of_hour_or_lot",
         "Valens on the lord of the hour and of the lot"),
        ("hel.valens.b2.active_inactive_times.method",
         "Valens on active and inactive times (chronocrators)"),
        ("hel.valens.b1.combination.preface",
         "Valens' preface to the planet-pair combinations"),
    ):
        d = _fire(rule_id, trigger)
        if d:
            s.delineations.append(d)
            fired += 1
    if not fired:
        s.notes.append(
            "No Valens method chapter is encoded in the loaded pack."
        )
        return
    s.notes.insert(0, (
        f"{fired} method statement(s) from the Anthologiae. These are the "
        "tradition's own procedure, not per-placement delineation, so they are "
        "stated once here rather than repeated under each planet."
    ))
