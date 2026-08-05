"""An Islamicate report, in al-Qabisi's own order.

Eighty-six rules were mined from the Arabic - al-Qabisi's *Introduction to the
Art of Judgements* from the Wurzburg TEI of the 2004 critical edition, and
al-Biruni's *Tafhim* from Wright's 1934 facing edition - and until now none of
them reached a page. The computations existed too, in multitradition/islamicate
and multitradition/qabisi_lots. What was missing was the thing between them.

The order here is the order of al-Qabisi's own chapters, not a Hellenistic
report with Arabic vocabulary pasted over it:

  I    the dignities, and which lord *prevails* (mustawli) over a degree
  II   the planets' natures, years and firdariyya
  III  the conditions of the planets - halb, hayyiz, reception, the aspects
  IV   the hyleg and the kadkhudah, the profection, the tasyir
  V    the lots

Two refusals hold throughout and are not negotiable. The kadkhudah's years are
computed as *structure* and never as a lifespan: the pack refuses the number
and so does this report. And the hyleg is reported with its own status - the
prenatal syzygy is not computed by this engine, so where the settled hyleg
depends on that, it is stated as conditional rather than as a finding.
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
ISLAMICATE_DIR = RESEARCH_ROOT / "islamicate"


@lru_cache(maxsize=1)
def _rules_by_id() -> dict[str, dict[str, Any]]:
    """Every Islamicate rule on disk, so a new pack needs no engine change."""
    rules: dict[str, dict[str, Any]] = {}
    for path in sorted(ISLAMICATE_DIR.glob("*rule_manifest.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for rule in data.get("rules", []):
            rid = rule.get("rule_id")
            if rid:
                rules[rid] = rule
    return rules


def _source_label(rule: dict[str, Any]) -> str:
    passages = rule.get("source_passages") or []
    if passages:
        p = passages[0]
        work = p.get("work") or "al-Qabisi, Introduction"
        loc = p.get("location") or p.get("section") or ""
        return f"{work}, {loc}".strip().rstrip(",")
    scope = rule.get("scope") or {}
    chapter = scope.get("chapter")
    school = rule.get("school_id", "")
    work = "al-Biruni, Tafhim" if "biruni" in school else (
        "al-Qabisi, Introduction to the Art of Judgements"
    )
    return f"{work}{f', chapter {chapter}' if chapter else ''}"


def _fire(rule_id: str, trigger: str) -> Delineation | None:
    """Quote a rule, honouring any refusal it declares."""
    rule = _rules_by_id().get(rule_id)
    if rule is None:
        return None
    c = rule.get("conclusion", {}) or {}
    policy = str(
        c.get("output_policy") or rule.get("output_policy") or ""
    ).lower()
    if "refus" in policy:
        return None
    text = None
    for key in ("engine_rendering", "judgment", "rendering"):
        if isinstance(c.get(key), str) and c[key].strip():
            text = c[key].strip()
            break
    if not text:
        return None
    return Delineation(
        text=text,
        rule_id=rule_id,
        source=_source_label(rule),
        evidence_grade=rule.get("evidence_grade", "?"),
        trigger=trigger,
    )


def _facts(birth: BirthInput) -> tuple[dict[str, Any], dict[str, Any]]:
    """The al-Qabisi section's facts, and al-Biruni's alongside them."""
    panel = build_panel(birth)
    qabisi: dict[str, Any] = {}
    biruni: dict[str, Any] = {}
    for section in panel["sections"]:
        if section.get("error"):
            continue
        if section["tradition_id"] == "islamicate_al_qabisi":
            qabisi = section.get("facts") or {}
        elif section["tradition_id"] == "islamicate_persian":
            biruni = section.get("facts") or {}
    if not qabisi:
        raise RuntimeError("the al-Qabisi calculation produced no facts")
    return qabisi, biruni


def build_report(birth: BirthInput) -> TraditionReport:
    qabisi, biruni = _facts(birth)
    report = TraditionReport(
        tradition_id="islamicate_al_qabisi",
        display_name=(
            "Islamicate — al-Qabisi's Introduction, with al-Biruni's Tafhim"
        ),
        birth=birth.to_dict(),
    )
    _opening(report, birth, qabisi, biruni)
    _dignities_section(report, qabisi)
    _natures_section(report, qabisi)
    _conditions_section(report, qabisi, biruni)
    _lots_section(report, qabisi)
    _hyleg_section(report, qabisi)
    _time_section(report, qabisi)
    _selfcheck_section(report, qabisi)
    _limits(report, qabisi, biruni)
    return report


def _opening(
    report: TraditionReport, birth: BirthInput, qabisi: dict, biruni: dict
) -> None:
    s = report.add(ReportSection("The Nativity and Its Sect", level=2))
    asc = qabisi.get("ascendant") or {}
    sect = qabisi.get("sect")
    s.notes.append(
        f"Born {birth.civil_date} at {birth.civil_time} in "
        f"{birth.place_label}. The Ascendant is "
        f"{asc.get('degree', 0):.2f}° of {asc.get('sign', '?')}, and the "
        f"nativity is {sect}."
    )
    bsect = (biruni.get("sect") or {}) if biruni else {}
    if bsect.get("sun_arc_test_agrees_with_altitude") is not None:
        agrees = bsect["sun_arc_test_agrees_with_altitude"]
        verdict = (
            "Two independent tests of sect agree here"
            if agrees else
            "The two tests of sect DISAGREE here, which is reported rather "
            "than settled by preference"
        )
        s.notes.append(
            f"{verdict}: the Sun's altitude, and the zodiacal arc against the "
            "Ascendant-Descendant axis."
        )
    d = _fire(
        "islam.qabisi.ch1.halb_hayyiz_definition",
        "sect is the first thing al-Qabisi's chapter I settles",
    )
    if d:
        s.delineations.append(d)


def _dignities_section(report: TraditionReport, qabisi: dict) -> None:
    """Chapter I: the five dignities, their scores, and who prevails."""
    s = report.add(ReportSection("The Dignities, and Who Prevails", level=2))
    for rule_id, trigger in (
        ("islam.qabisi.ch1.domicile_table_and_detriment",
         "assigning the domicile lord of every sign"),
        ("islam.qabisi.ch1.exaltation_fall_table_and_ptolemy_disagreement",
         "the exaltations, where al-Qabisi records a disagreement with Ptolemy"),
        ("islam.qabisi.ch1.triplicity_table", "the triplicity lords"),
        ("islam.qabisi.ch1.egyptian_bounds_table", "the Egyptian bounds"),
        ("islam.qabisi.ch1.face_table_chaldean_order",
         "the faces, in the Chaldean order"),
        ("islam.qabisi.ch1.dignity_power_scoring",
         "how much each dignity is worth"),
    ):
        d = _fire(rule_id, trigger)
        if d:
            s.delineations.append(d)

    table = qabisi.get("dignity_scoring_table") or {}
    if table.get("powers"):
        s.notes.append(
            "The scoring table is "
            + ", ".join(f"{k} {v}" for k, v in table["powers"].items())
            + " — the same table Lilly printed seven centuries later, stated "
            "here in Arabic around 950 CE."
        )

    mustawli = qabisi.get("mustawli_of_the_ascendant") or {}
    if mustawli.get("winner"):
        detail = mustawli.get("score_detail") or {}
        s.notes.append(
            f"Over the Ascendant's degree the *mustawli* — the lord that "
            f"prevails — is **{mustawli['winner']}**, on "
            + "; ".join(
                f"{p} ({', '.join(v)})" for p, v in detail.items()
            )
            + "."
        )
        if mustawli.get("tied"):
            s.notes.append(
                "The scores tie between "
                + ", ".join(mustawli["tied"])
                + ", and al-Qabisi's chapter does not break the tie, so it is "
                "left standing rather than broken by this engine."
            )
    d = _fire(
        "islam.qabisi.ch1.mustawli_worked_example",
        "al-Qabisi works the mustawli himself",
    )
    if d:
        s.delineations.append(d)


def _natures_section(report: TraditionReport, qabisi: dict) -> None:
    """Chapter II: the planets' natures and their four tiers of years."""
    s = report.add(ReportSection("The Planets and Their Years", level=2))
    for rule_id, trigger in (
        ("islam.qabisi.ch2.planetary_core_natures",
         "the natures of the seven"),
        ("islam.qabisi.ch2.four_tier_planetary_years_table",
         "the four tiers of planetary years — least, mean, great, greatest"),
        ("islam.qabisi.ch2.firdaria_full_duration_table",
         "the firdariyya durations"),
        ("islam.qabisi.ch2.node_tail_nature_dual_doctrine",
         "the nodes, on which al-Qabisi carries two doctrines at once"),
        ("islam.qabisi.ch2.ages_of_man_table", "the ages of man"),
    ):
        d = _fire(rule_id, trigger)
        if d:
            s.delineations.append(d)


def _conditions_section(
    report: TraditionReport, qabisi: dict, biruni: dict
) -> None:
    """Chapter III: the conditions - halb, hayyiz, reception, the aspects."""
    s = report.add(ReportSection("The Conditions of the Planets", level=2))
    for rule_id, trigger in (
        ("islam.qabisi.ch3.combustion_cascade_thresholds",
         "the cascade from combustion to the heart of the Sun"),
        ("islam.qabisi.ch3.oriental_occidental_superior_phase",
         "the phases of the superior planets"),
        ("islam.qabisi.ch3.oriental_occidental_inferior_phase",
         "the phases of the inferior planets"),
        ("islam.qabisi.ch3.application_orb_and_types",
         "application, and the orb it happens within"),
        ("islam.qabisi.ch3.reception_and_return", "reception (qabul)"),
        ("islam.qabisi.ch3.translation_and_collection_of_light",
         "translation and collection of light"),
        ("islam.qabisi.ch3.void_of_course_and_feral",
         "the void of course Moon, and the feral planet"),
        ("islam.qabisi.ch3.prevention_man_two_forms", "prevention (man')"),
        ("islam.qabisi.ch3.frustration_variants", "frustration"),
        ("islam.qabisi.ch3.fortune_and_misfortune_conditions",
         "what al-Qabisi counts as fortune and misfortune in a planet"),
    ):
        d = _fire(rule_id, trigger)
        if d:
            s.delineations.append(d)

    summary = (biruni.get("condition_summary") or {}) if biruni else {}
    if summary.get("in_hayyiz") is not None:
        in_hayyiz = summary.get("in_hayyiz") or []
        only_halb = summary.get("halb_without_hayyiz") or []
        s.notes.append(
            "In this chart, in *hayyiz*: "
            + (", ".join(in_hayyiz) if in_hayyiz else "none")
            + ". In *halb* but not hayyiz: "
            + (", ".join(only_halb) if only_halb else "none")
            + ". Every hayyiz is a halb; not every halb is a hayyiz."
        )

    mercury = (biruni.get("mercury_resolution") or {}) if biruni else {}
    if mercury.get("gender"):
        s.notes.append(
            f"Mercury is resolved as {mercury['gender']} and "
            f"{mercury.get('sect')} here, on the basis that he is "
            + str(mercury.get("basis", "")).replace("_", " ") + "."
            + (
                f" Al-Qabisi's own chapter differs: {mercury['al_qabisi_difference']}"
                if mercury.get("al_qabisi_difference") else ""
            )
        )

    condition = qabisi.get("planetary_condition") or {}
    receptions = condition.get("reception_qabul") or []
    if receptions:
        s.notes.append(
            f"{len(receptions)} reception(s) stand in this chart: "
            + "; ".join(
                f"{r['planet']} received by {r['received_by']} by "
                f"{r['by_dignity']} ({r['aspect']})"
                for r in receptions[:6]
            )
            + "."
        )


def _lots_section(report: TraditionReport, qabisi: dict) -> None:
    """Chapter V: the lots, each with the formula that cast it."""
    s = report.add(ReportSection("The Lots", level=2))
    for rule_id, trigger in (
        ("islam.qabisi.ch5.lot_of_fortune_general_method",
         "the general method for casting a lot"),
        ("islam.qabisi.ch5.lot_of_hyleg_and_life",
         "the lots of the hyleg and of life"),
        ("islam.qabisi.ch5.representative_house_lots_with_attribution",
         "the house lots, with the authorities al-Qabisi names for each"),
        ("islam.qabisi.ch5.additional_named_lots_and_inventory",
         "the remaining named lots"),
    ):
        d = _fire(rule_id, trigger)
        if d:
            s.delineations.append(d)

    lots = qabisi.get("named_lots") or {}
    if lots:
        s.notes.append(
            f"{len(lots)} lot(s) are cast for this nativity. Each carries its "
            "own formula so the number can be checked rather than taken:"
        )
        prose: list[str] = []
        for name, lot in list(lots.items())[:14]:
            if not isinstance(lot, dict):
                # Some entries are the pack's own prose notes rather than cast
                # lots - typically a statement of which lots were NOT cast and
                # why. They belong after the list, not disguised inside it
                # with an internal key for a name.
                prose.append(str(lot))
                continue
            reversal = (
                " (reversed by sect)" if lot.get("sect_reverses") else ""
            )
            s.notes.append(
                f"- **{name}** — {lot.get('degree', 0):.2f}° "
                f"{lot.get('sign', '?')}; {lot.get('formula', '')}{reversal}."
            )
        for line in prose:
            s.notes.append(f"Not cast here — {line}")
    weak = _rules_by_id().get("islam.qabisi.ch5.commodity_price_lots_self_declared_weak")
    if weak is not None:
        s.notes.append(
            "Al-Qabisi's commodity-price lots are carried in the pack but not "
            "cast here: he declares their weakness himself, and an engine that "
            "printed them beside the rest would be flattening a distinction "
            "the author drew."
        )


def _hyleg_section(report: TraditionReport, qabisi: dict) -> None:
    """Chapter IV: the hyleg and the kadkhudah - structure, never a lifespan."""
    s = report.add(ReportSection("The Hyleg and the Kadkhudah", level=2))
    for rule_id, trigger in (
        ("islam.qabisi.ch4.hyleg_candidate_places",
         "which places make a candidate eligible"),
        ("islam.qabisi.ch4.kadkhudah_alcocoden",
         "how the kadkhudah is found from the hyleg"),
        ("islam.qabisi.ch4.al_wali_governor", "al-wali, the governor"),
    ):
        d = _fire(rule_id, trigger)
        if d:
            s.delineations.append(d)

    settled = qabisi.get("hyleg_settled") or {}
    if settled.get("hyleg"):
        status = settled.get("status")
        s.notes.append(
            f"The hyleg settles on **{settled['hyleg']}** at "
            f"{settled.get('longitude', 0):.2f}°, beheld by "
            + ", ".join(
                f"{p} ({a})" for p, a in (settled.get("beheld_by") or {}).items()
            )
            + "."
        )
        if status == "conditional":
            pending = settled.get("conditional_on") or []
            plural = len(pending) != 1
            s.notes.append(
                "This is **conditional**, and the condition is named: "
                + ", ".join(pending)
                + f" {'precede' if plural else 'precedes'} it in al-Qabisi's "
                "inspection order and this engine does not compute "
                f"{'them' if plural else 'it'}. An uncomputed candidate is not "
                "a failed one, so the finding is held open rather than "
                "asserted."
            )
        else:
            s.notes.append(f"Status: {status}. {settled.get('chosen_because', '')}")

    ledger = qabisi.get("hyleg_candidate_ledger") or []
    if ledger:
        s.notes.append(
            "The full inspection, candidate by candidate, so the settlement "
            "can be audited:"
        )
        for row in ledger:
            place = row.get("whole_sign_place")
            # A candidate this engine never computed has not been TESTED, and
            # printing it as "not eligible; aspect gate failed" collapses
            # not_computed into failed - which is precisely the distinction
            # settle_hyleg exists to preserve. It must not be undone in prose.
            if row.get("longitude") is None or place is None:
                s.notes.append(
                    f"- {row['candidate']}: **not computed** by this engine, "
                    "so neither test was applied. This is not a failure — it "
                    "is the reason the settlement above is conditional."
                )
                continue
            verdict = "eligible" if row.get("eligible") else "not eligible"
            gate = "passed" if row.get("passes_aspect_gate") else "failed"
            s.notes.append(
                f"- {row['candidate']}: place {place}, {verdict} by place; "
                f"aspect gate {gate}."
            )

    forks = qabisi.get("kadkhudah_forks") or {}
    default = forks.get("al_qabisi_default") or {}
    if default.get("kadkhudah"):
        s.notes.append(
            f"On that hyleg the kadkhudah is **{default['kadkhudah']}**, won by "
            f"{default.get('won_by')}, beholding by "
            f"{default.get('beholds_by')}."
        )
    s.refusals.append(
        "The kadkhudah's YEARS are not given. The pack refuses the number and "
        "so does this report: the structure of the doctrine is a legitimate "
        "thing to show, and a lifespan told to a reader is not."
    )


def _time_section(report: TraditionReport, qabisi: dict) -> None:
    """Chapter IV's time-lord systems: firdariyya, profection, tasyir."""
    s = report.add(ReportSection("The Divisions of Time", level=2))
    for rule_id, trigger in (
        ("islam.qabisi.ch4.annual_profection_worked_example",
         "the annual profection"),
        ("islam.qabisi.ch4.primary_directions_tasyir", "the tasyir"),
        ("islam.qabisi.ch4.jarbakhtar_bound_directions",
         "the jarbakhtar, directed through the bounds"),
        ("islam.qabisi.ch4.sahib_al_dawr_hour_lord_years",
         "sahib al-dawr, the lord of the turn"),
    ):
        d = _fire(rule_id, trigger)
        if d:
            s.delineations.append(d)

    firdaria = qabisi.get("firdaria") or {}
    periods = firdaria.get("periods") or []
    if periods:
        s.notes.append(
            f"The firdariyya opens with {periods[0].get('ruler')} because the "
            f"nativity is {qabisi.get('sect')}, and runs "
            f"{firdaria.get('total_years')} years: "
            + ", ".join(
                f"{p['ruler']} {p['starts_at_age']:.0f}–{p['ends_at_age']:.0f}"
                for p in periods
            )
            + "."
        )

    profection = qabisi.get("profection_of_this_birth") or {}
    years = profection.get("example_years_1_to_12") or []
    if years:
        s.notes.append(
            "The profection turns one whole sign a year from "
            f"{profection.get('natal_ascendant_sign')}: "
            + ", ".join(
                f"year {y['completed_years'] + 1} {y['profected_sign']} "
                f"({y['year_lord']})"
                for y in years[:12]
            )
            + "."
        )

    tasyir = qabisi.get("tasyir") or {}
    if tasyir.get("finding"):
        # Quoted from the pack, which does not always terminate its prose.
        finding = str(tasyir["finding"]).rstrip()
        if finding and finding[-1] not in ".!?":
            finding += "."
        s.notes.append(f"On the rate of direction — {finding}")


def _selfcheck_section(report: TraditionReport, qabisi: dict) -> None:
    """Al-Qabisi's own worked examples, run against this engine.

    These are the only end-to-end checks the text offers, and they are worth a
    section of their own: an engine that cannot reproduce the author's own
    arithmetic has no business reporting a chart in his name.
    """
    check = qabisi.get("worked_example_selfcheck") or {}
    if not check:
        return
    s = report.add(
        ReportSection("Al-Qabisi's Own Worked Examples, Rerun", level=2)
    )
    s.notes.append(check.get("note", ""))
    passed = failed = 0
    for topic, block in check.items():
        if not isinstance(block, dict):
            continue
        for case, row in block.items():
            if not isinstance(row, dict) or "matches" not in row:
                continue
            if row["matches"]:
                passed += 1
            else:
                failed += 1
                s.notes.append(
                    f"- **MISMATCH** in {topic}/{case}: he says "
                    f"{row.get('al_qabisi_says')}, this engine computes "
                    f"{row.get('computed')}."
                )
    s.notes.insert(
        1,
        f"{passed} of his worked figures reproduce"
        + (f"; {failed} do NOT and are named below." if failed else
           ", and none disagree."),
    )


#: What al-Biruni's pack cannot reach but al-Qabisi's does, so the limits
#: section does not report a layer the reader has just been shown.
QABISI_SUPPLIES = {
    "al-qabisi introduction doctrine": "named_lots",
    "firdaria period durations and dates": "firdaria",
    "tasyir / directions": "tasyir",
}


def _covered_by_qabisi(layer: str, qabisi: dict) -> bool:
    key = QABISI_SUPPLIES.get(layer.strip().lower())
    return bool(key and qabisi.get(key))


def _limits(report: TraditionReport, qabisi: dict, biruni: dict) -> None:
    s = report.add(ReportSection("What This Report Does Not Claim", level=2))
    s.notes.append(
        "Every rendering from the Arabic is an unreviewed engine translation. "
        "The rule ids are given throughout so any line can be taken back to "
        "the Wurzburg TEI of the 2004 critical edition and checked."
    )
    # al-Biruni's pack lists what IT does not reach, and some of those are
    # exactly what al-Qabisi's pack supplies above. Repeating the whole list
    # would tell the reader that something absent is missing from the report
    # they are holding, which is not true.
    gated = [
        layer
        for layer in ((biruni.get("distinctive_layers_gated") or [])
                      if biruni else [])
        if not _covered_by_qabisi(layer, qabisi)
    ]
    if gated:
        s.notes.append(
            "Reached by neither pack and therefore absent rather than "
            "approximated: " + ", ".join(gated) + "."
        )
    s.notes.append(
        "The prenatal syzygy is not computed. It stands first in al-Qabisi's "
        "hyleg order, so wherever the hyleg above is marked conditional, this "
        "is the thing it is conditional on."
    )
    concordance = (biruni.get("variant_concordance") or {}) if biruni else {}
    if concordance.get("preserved_variants"):
        s.notes.append(
            f"{concordance['preserved_variants']} textual variant(s) across "
            f"{len(concordance.get('witness_lineages') or [])} witness "
            "lineages are preserved in the pack rather than harmonised. Where "
            "the Arabic and the several Latin translators disagree, they are "
            "recorded as disagreeing."
        )
