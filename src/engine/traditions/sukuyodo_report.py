"""A Sukuyōdō reading — the birth mansion and the three nines.

Forty-five mined rules, and before this nothing: no computation, no panel
section, no page. The mansions, the three-nine relations and the pada signs are
all here now.

One thing has to be said plainly and is said in the report itself. The birth
mansion needs a lunar month and day, and the tradition's own calendars — the
Futian li 符天暦 that the sources name, and the Senmyō reki that was the
Japanese state calendar — are NOT in this repository. What is available is the
panel's own lunisolar kernel, which is a modern reconstruction on Chinese
meridians. So this report computes the mansion under that kernel across every
meridian it offers, gates on their agreement, and states in the body of the
reading that the regime it used is not the regime a Sukuyōshi used.

That distinction matters more here than in most tracks. The pack's own note is
that the gate elsewhere in this package varies a meridian inside one calendar
tradition, whereas the Sukuyōdō gate varies the calendar SYSTEM — a larger
disagreement that must be disclosed as such rather than presented as a timezone
nicety. Using a stand-in kernel and saying so is the honest version of that.
"""

from __future__ import annotations

from typing import Any

from ..multitradition import build_panel
from ..multitradition.sukuyodo import (
    CATEGORY_GLOSS,
    NIU,
    association_categories,
    build as build_sukuyo,
    mansions,
    pada_closure,
    weekday_natal_clause,
    weekday_planet,
)
from ..multitradition.types import BirthInput
from .report import Delineation, ReportSection, TraditionReport


def _lunar_dates(birth: BirthInput) -> dict[str, tuple[int, int]]:
    """Lunar month and day per meridian, from the panel's own kernel."""
    panel = build_panel(birth)
    section = next(
        (
            s for s in panel["sections"]
            if s["tradition_id"] == "ziwei_doushu" and not s.get("error")
        ),
        None,
    )
    if section is None:
        return {}
    check = (section["facts"] or {}).get("calendar_regime_check") or {}
    out: dict[str, tuple[int, int]] = {}
    for regime in check.get("regimes", []):
        month = regime.get("lunar_month_number")
        day = regime.get("lunar_day")
        if month and day:
            out[str(regime.get("label") or regime.get("regime_id"))] = (
                int(month), int(day)
            )
    return out


def build_report(birth: BirthInput) -> TraditionReport:
    report = TraditionReport(
        tradition_id="sukuyodo",
        display_name="Sukuyōdō — the Twenty-Seven Mansions and the Three Nines",
        birth=birth.to_dict(),
    )
    dates = _lunar_dates(birth)
    reading = build_sukuyo(dates) if dates else {
        "status": "refused",
        "why": "no lunar date could be computed for this birth",
        "per_regime": {},
        "regimes_agree": False,
    }
    _calendar_section(report, birth, dates, reading)
    _mansion_section(report, reading)
    _sanku_section(report, reading)
    _sign_section(report, reading)
    _natal_section(report, birth, reading)
    _structure_section(report)
    _limits_section(report, reading)
    return report


def _calendar_section(
    report: TraditionReport,
    birth: BirthInput,
    dates: dict[str, tuple[int, int]],
    reading: dict[str, Any],
) -> None:
    s = report.add(ReportSection("Which Calendar This Reading Used", level=2))
    s.notes.append(
        f"Born {birth.civil_date} at {birth.civil_time} in "
        f"{birth.place_label}. Everything below starts from the lunar month "
        "and day, because the birth mansion is derived from the calendar and "
        "not from the sky."
    )
    s.refusals.append(
        "The calendar this tradition actually used is NOT in this repository. "
        "The sources name the Futian li 符天暦, and the Japanese state "
        "calendar was the Senmyō reki; neither one's tables are here. What "
        "follows was computed with the panel's own lunisolar kernel, a modern "
        "reconstruction on Chinese meridians. It is a stand-in, and the "
        "mansion below is the one that kernel gives — not, on its own "
        "authority, the one a Sukuyōshi would have found."
    )
    for label, (month, day) in dates.items():
        s.notes.append(f"- **{label}** — lunar month {month}, day {day}.")
    if reading.get("regimes_agree"):
        s.notes.append(
            "Every meridian the kernel offers gives the same birth mansion, "
            "so the reading does not turn on which one is chosen."
        )
    s.notes.append(
        "configured_method — "
        + str(reading.get("gate_rationale", ""))
        + " The sources do not prescribe this gate; Sukuyōshi worked in one "
        "regime and did not hedge. The alternative it rejects — picking a "
        "regime silently — is named here rather than left implicit."
    )


def _mansion_section(report: TraditionReport, reading: dict[str, Any]) -> None:
    s = report.add(ReportSection("The Birth Mansion", level=2))
    if reading.get("status") != "emitted":
        s.refusals.append(
            "The birth mansion is not emitted: "
            + str(reading.get("why", "the regimes disagree"))
            + ". Each regime's own answer is given below instead, because the "
            "disagreement is the finding."
        )
        for regime, row in (reading.get("per_regime") or {}).items():
            got = row.get("mansion") or row.get("error")
            s.notes.append(f"- {regime} would give **{got}**.")
        return

    mansion = reading["birth_mansion"]
    s.notes.append(
        f"The birth mansion is **{mansion}**, the "
        f"{reading['index']} of the twenty-seven, counted from 昴."
    )
    s.notes.append(
        "It was found by both of the text's own formulas, which are "
        "algebraically identical and are computed separately every time as "
        "the redundancy check the text intends: an implementation that "
        "disagrees with only one of them is provably wrong."
    )
    s.notes.append(str(reading.get("method_fork", "")))


def _sanku_section(report: TraditionReport, reading: dict[str, Any]) -> None:
    if reading.get("status") != "emitted":
        _conditional_sections(report, reading)
        return
    s = report.add(ReportSection("The Three Nines", level=2))
    triads = reading.get("triads") or {}
    s.notes.append(
        f"The three heads: 命 (life) {triads.get('命')}, 業 (karma) "
        f"{triads.get('業')}, 胎 (womb) {triads.get('胎')} — nine apart, "
        "circuiting the twenty-seven exactly. This closure is the structural "
        "reason the cycle must be 27 and not 28."
    )
    s.notes.append(
        "Every other mansion's standing toward this birth, by offset. Two "
        "mansions fix the category with no interpretive latitude, which makes "
        "this the most directly implementable rule in the tradition:"
    )
    for row in reading.get("sanku") or []:
        s.notes.append(
            f"- {row['offset']:>2}  {row['mansion']}  {row['category']} "
            f"({row['gloss']})"
        )


def _conditional_sections(
    report: TraditionReport, reading: dict[str, Any]
) -> None:
    """The full reading under each candidate mansion, labelled conditional.

    Refusing the anchor is not a reason to withhold the structure. What turns
    on the calendar is visible this way; a blank page hides it.
    """
    candidates = reading.get("candidates") or []
    if not candidates:
        return
    for candidate in candidates:
        backing = candidate["supported_by"]
        s = report.add(
            ReportSection(
                f"If the Birth Mansion Is {candidate['mansion']}", level=2
            )
        )
        s.notes.append(
            f"Given by {len(backing)} of the "
            f"{len(reading.get('per_regime') or {})} regimes tested: "
            + "; ".join(backing)
            + ". This reading is conditional on that calendar being right."
        )
        triads = candidate["triads"]
        s.notes.append(
            f"The three heads: 命 {triads['命']}, 業 {triads['業']}, "
            f"胎 {triads['胎']}."
        )
        for row in candidate["sanku"]:
            s.notes.append(
                f"- {row['offset']:>2}  {row['mansion']}  {row['category']} "
                f"({row['gloss']})"
            )
        for row in candidate["signs"]:
            s.notes.append(
                f"- {row['pada']} of its four pada in {row['sign']} "
                f"({row['western_equivalent']}), resident "
                f"{row['resident_luminary']}."
            )


def _sign_section(report: TraditionReport, reading: dict[str, Any]) -> None:
    if reading.get("status") != "emitted":
        return
    s = report.add(ReportSection("The Sign and Its Resident", level=2))
    rows = reading.get("signs") or []
    if not rows:
        s.notes.append("The birth mansion's pada fall in no tabled sign.")
        return
    for row in rows:
        s.notes.append(
            f"- {row['pada']} of its four pada fall in **{row['sign']}** "
            f"({row['western_equivalent']}), whose resident is "
            f"{row['resident_luminary']}."
        )
    if len(rows) > 1:
        s.notes.append(
            "A mansion holds four pada and a sign holds nine, so most "
            "mansions straddle a boundary. Both signs are given; collapsing "
            "to one would discard the straddle the allotment exists to record."
        )
    s.notes.append(
        "The Western sign names are an engine gloss for orientation only. "
        "T1299 names the signs by their figures — 獅子, 秤, 蝎, 磨竭, 瓶, 魚 — "
        "and no rule in the pack depends on the Western label."
    )


def _natal_section(
    report: TraditionReport, birth: BirthInput, reading: dict[str, Any]
) -> None:
    """What the chapter says of the native, as opposed to of the method.

    Two things here bear on a person rather than on a technique, and neither
    depends on the birth mansion - so they survive the calendar refusal that
    withholds everything else.
    """
    s = report.add(ReportSection("What the Text Says of the Native", level=2))
    weekday = (birth.civil_date.weekday() + 1) % 7  # Monday=0 -> Sunday-first
    planet = weekday_planet(weekday)
    s.notes.append(
        f"The birth falls on the day of **{planet}**. The seven-day cycle is "
        "continuous and unbroken in this text — *one changes each day, one "
        "revolution in seven days, then begins again* — so it needs no lunar "
        "calendar and is unaffected by the regime disagreement above."
    )
    clause = weekday_natal_clause(planet)
    if clause is None:
        return
    if clause.get("absent"):
        s.refusals.append(str(clause["why"]))
    else:
        rendering = clause.get("rendering")
        if rendering:
            s.delineations.append(
                Delineation(
                    text=f"A native of this day {rendering}.",
                    rule_id=str(clause["rule_id"]),
                    source="Sukuyōkyō (T1299), the weekday chapter",
                    evidence_grade="C",
                    trigger=f"born on the day of {planet}",
                )
            )
        for reason in clause.get("refused", []):
            s.refusals.append(
                f"The same clause also carries {reason}, which the pack "
                "refuses for output about a living person. It is withheld "
                "here rather than quietly cut from the quotation."
            )
        s.notes.append(str(clause["not_natal"]))

    assoc = association_categories()
    if assoc and reading.get("status") == "emitted":
        s.delineations.append(
            Delineation(
                text=(
                    "Broadly speaking, take "
                    + "、".join(assoc["favourable"])
                    + " as good and fit for forming ties; all the rest are "
                    "bad, and one should not become close through them."
                ),
                rule_id=str(assoc["rule_id"]),
                source="Sukuyōkyō (T1299), on the three nines",
                evidence_grade="C",
                trigger="the three-nine categories, applied to association",
            )
        )
        s.notes.append(f"The source hedges this itself: {assoc['hedge']}")
        s.notes.append(f"And contradicts itself, preserved: {assoc['tension']}")
        s.notes.append(
            f"The passage calls itself a secret method — {assoc['secrecy_claim']}."
        )
    elif assoc:
        s.notes.append(
            "The association rule is not applied, because it runs over the "
            "three-nine categories and those are reckoned from a birth "
            "mansion this reading could not settle."
        )


def _structure_section(report: TraditionReport) -> None:
    s = report.add(ReportSection("Why the Cycle Is Twenty-Seven", level=2))
    closure = pada_closure()
    s.notes.append(
        f"The pada allotment gives every sign nine pada and every mansion "
        f"four, {closure['total_pada']} in all. That divides into whole "
        "quarters only across 27 mansions."
    )
    s.notes.append(
        f"{NIU} receives {closure['pada_allotted_to_niu']} pada. It is "
        "catalogued in the text and has no operative role: no three-nine "
        "category, no election day, no pada, and no birth-mansion computation "
        "in this engine can reach it. Its natal clause exists and may be "
        "quoted as a textual fact, which is a different thing from using it."
    )
    s.notes.append(
        f"The text also lists {NIU} inside a thirteen-mansion enumeration of "
        "the solar half, nine lines before an allotment that gives it nothing. "
        "That is an internal discrepancy in the source and it is recorded "
        "rather than quietly corrected."
    )
    s.notes.append(
        "The order runs from 昴 rather than from the Chinese lunar-lodge "
        "origin 角. That is the Indian nakshatra order as received, and it is "
        "what makes the three-nine rotation come out as the text states it — "
        "starting at 角 would rotate every relationship by eleven places and "
        "still look plausible."
    )


def _limits_section(report: TraditionReport, reading: dict[str, Any]) -> None:
    s = report.add(ReportSection("What This Report Does Not Claim", level=2))
    s.notes.append(
        "The 32 rules behind the mansion work are extracted from the MAINLAND "
        "recension. Japanese practice used a different one, so nothing here "
        "may be described as 'what Japanese sukuyōshi used' until the Japanese "
        "recension is collated against it. The two are versions of one work "
        "and they agree at the point the Murakami example tests, which is "
        "reassuring and is not collation."
    )
    s.notes.append(
        "The tradition's horoscopy — twelve places, the nine planets against "
        "the lunar stations, the concentric rings — is described in the pack "
        "and is not computed here. Only the mansion layer is."
    )
    s.notes.append(
        "The observational derivation of the natal mansion is not implemented. "
        "It is the route the 961 arbitration preferred for exactly this "
        "question, so its absence is the largest single gap in this reading, "
        "and it is a gap rather than a refusal."
    )
    s.notes.append(
        "Every category gloss is an engine rendering: "
        + ", ".join(f"{k} {v.split(' —')[0]}" for k, v in CATEGORY_GLOSS.items())
        + ". They are unreviewed."
    )
    assert len(mansions()) == 27  # the invariant the whole reading rests on
