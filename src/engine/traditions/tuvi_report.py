"""A Tử Vi Đẩu Số report — the Vietnamese chart in its own direction.

Fifty-four mined rules and, until now, no engine of any kind. The obvious
shortcut would have been to run this through the Zi Wei machinery and relabel
the output, and the pack exists partly to say why that is wrong: the twelve
palaces enumerate in the REVERSE order from Mệnh, so an identically constructed
board carries every topic in a different place.

The one structural advantage this track has over Zi Wei is worth stating where
a reader can see it. Zi Wei's calendar gate treats 105°E as an adversarial
meridian and refuses when it disagrees with the Chinese ones. For a Vietnamese
chart 105°E is not adversarial: it is the authoritative meridian, the panel
computes the lunar date there, and the day the gate could not settle for Zi Wei
is simply the day this tradition means.
"""

from __future__ import annotations

from typing import Any

from ..multitradition import build_panel
from ..multitradition.tuvi import (
    BRANCHES,
    build as build_tuvi,
    palace_order,
)
from ..multitradition.types import BirthInput
from .report import Delineation, ReportSection, TraditionReport

#: The double-hour a clock time falls in. Tý spans the midnight boundary.
def hour_branch_index(civil_time: str) -> int:
    hour = int(str(civil_time).split(":")[0])
    return ((hour + 1) // 2) % 12


def _facts(birth: BirthInput) -> tuple[dict[str, Any], dict[str, Any]]:
    panel = build_panel(birth)
    section = next(
        (
            s for s in panel["sections"]
            if s["tradition_id"] == "vietnamese" and not s.get("error")
        ),
        None,
    )
    if section is None:
        raise RuntimeError("the Vietnamese calendar produced no facts")
    return section["facts"], panel


def _year_stem(panel: dict) -> str | None:
    """The stem of the sexagenary year.

    Taken from the panel's own Zi Wei section, which already computes it for
    the four transformations. The sexagenary year is astronomy shared between
    the traditions; what each does with it is where they part.
    """
    for section in panel.get("sections", []):
        if section.get("tradition_id") != "ziwei_doushu" or section.get("error"):
            continue
        four = (section.get("facts") or {}).get("four_transformations") or {}
        stem = four.get("birth_year_stem")
        if stem:
            return str(stem)
    return None


def build_report(birth: BirthInput) -> TraditionReport:
    facts, panel = _facts(birth)
    report = TraditionReport(
        tradition_id="vietnamese",
        display_name="Tử Vi Đẩu Số — the Vietnamese Board",
        birth=birth.to_dict(),
    )
    lunar = facts.get("lunar_date") or {}
    month = lunar.get("month_number")
    day = lunar.get("day")
    stem = _year_stem(panel)

    _calendar_section(report, birth, facts, lunar)
    if not (month and day):
        report.sections[-1].refusals.append(
            "No lunar month and day were computed, and the whole board is "
            "placed from them. Nothing below can be built."
        )
        return report

    chart = build_tuvi(
        int(month), int(day), hour_branch_index(birth.civil_time), stem or ""
    )
    _board_section(report, chart, stem)
    _palaces_section(report, chart)
    _direction_section(report)
    _limits_section(report, chart)
    return report


def _calendar_section(
    report: TraditionReport, birth: BirthInput, facts: dict, lunar: dict
) -> None:
    s = report.add(ReportSection("The Vietnamese Lunar Date", level=2))
    profile = facts.get("calendar_profile") or {}
    s.notes.append(
        f"Born {birth.civil_date} at {birth.civil_time} in "
        f"{birth.place_label}. The lunar date is **{lunar.get('label')}**, "
        f"computed at {profile.get('reference_longitude')} — the meridian "
        "Vietnamese practice uses."
    )
    moon = facts.get("month_start_new_moon") or {}
    if moon.get("local_day_differs_from_beijing"):
        s.notes.append(
            "This month's opening new moon falls on a different civil day at "
            f"Hanoi ({moon.get('hanoi_civil_date')}) than at Beijing "
            f"({moon.get('beijing_civil_date')}). That divergence is the "
            "reason this tradition needs its own calendar rather than a "
            "borrowed Chinese one, and it is why a Tử Vi chart and a Zi Wei "
            "chart of the same birth can be built on different days."
        )
    trace = facts.get("boundary_trace") or {}
    if trace.get("within_tolerance"):
        s.refusals.append(
            "This birth falls within "
            f"{trace.get('tolerance_minutes')} minutes of "
            f"{trace.get('closest_event')}. The lunar date is therefore not "
            "safe to assert, and everything placed from it inherits that."
        )
    else:
        s.notes.append(
            f"The nearest calendar boundary is {trace.get('closest_event')}, "
            f"{trace.get('closest_margin_minutes', 0):.0f} minutes away, so "
            "the date is not borderline."
        )


def _board_section(
    report: TraditionReport, chart: dict, stem: str | None
) -> None:
    s = report.add(ReportSection("Mệnh, Thân and the Cục", level=2))
    s.notes.append(
        f"**Mệnh** falls in the palace **{chart['menh']}** and **Thân** in "
        f"**{chart['than']}**. Both are counted the manual's way: begin at "
        "Dần as the first lunar month and count forward to the birth month, "
        "call that palace the hour Tý, then count backward to the birth hour "
        "for Mệnh and forward for Thân."
    )
    cuc = chart.get("cuc")
    if cuc:
        s.notes.append(
            f"The **cục** is {cuc['cuc']} (number {cuc['number']}), set from "
            f"the year-stem pair {cuc['stem_pair']} against Mệnh in "
            f"{cuc['menh_palace']}. The printed grid is a Latin square — each "
            "cục once in every row and every column — which is the check that "
            "catches a mis-transcribed cell, and it passes."
        )
    elif stem is None:
        s.refusals.append(
            "The year stem could not be determined, so the cục is not set and "
            "Tử Vi is not placed. The cục is what the star is placed from."
        )
    resolution = chart.get("tuvi_seat") or {}
    if resolution.get("status") == "printed_and_reconstruction_disagree":
        s.notes.append(
            f"On this day the printed table and the engine's reconstruction "
            f"DISAGREE: the table puts Tử Vi in {resolution['palace']} and the "
            f"reconstruction predicts {resolution['closed_form_predicts']}. "
            "The printed reading is the one used. The reconstruction is a "
            "collation instrument — the book states no formula — and it does "
            "not get to overrule the book."
        )
    seat = chart.get("tuvi_palace")
    if seat:
        s.notes.append(
            f"**Tử Vi** itself sits in **{seat}**, read from the printed "
            f"table for this cục at lunar day {chart['lunar_day']}."
        )
        s.notes.append(
            "Those five tables are printed as a ring around the board rather "
            "than as lists, and the pack records that the PDF's own text "
            "layer flattens the ring into a single column and is unusable for "
            "them. They were read from the page image instead."
        )
    elif chart.get("tuvi_not_placed"):
        s.refusals.append(
            "Tử Vi is not placed: " + str(chart["tuvi_not_placed"]) + "."
        )


def _palaces_section(report: TraditionReport, chart: dict) -> None:
    s = report.add(ReportSection("The Twelve Palaces", level=2))
    for name, branch in chart["palaces"].items():
        s.notes.append(f"- **{name}** — {branch}.")


def _direction_section(report: TraditionReport) -> None:
    """Why this is not Zi Wei relabelled."""
    s = report.add(
        ReportSection("Why This Is Not the Chinese Board Relabelled", level=2)
    )
    from ..multitradition.tuvi import _rules

    for rule_id, trigger in (
        ("vietnam.tuvi.lt.palaces.enumeration_runs_reverse_of_the_chinese_order",
         "the direction the palaces enumerate in"),
        ("vietnam.tuvi.lt.board.twelve_fixed_branch_palaces",
         "the board the palaces sit on"),
    ):
        rule = _rules().get(rule_id)
        if rule is None:
            continue
        text = (rule.get("conclusion") or {}).get("engine_rendering")
        if isinstance(text, str) and text.strip():
            s.delineations.append(
                Delineation(
                    text=text.strip(),
                    rule_id=rule_id,
                    source="Tử Vi construction manual (Vietnamese)",
                    evidence_grade=rule.get("evidence_grade", "?"),
                    trigger=trigger,
                )
            )
    rule = _rules().get(
        "vietnam.tuvi.lt.palaces.enumeration_runs_reverse_of_the_chinese_order"
    )
    if rule:
        c = rule.get("conclusion") or {}
        s.notes.append(str(c.get("relation", "")))
        if c.get("independence"):
            s.notes.append(
                "Two independent Vietnamese witnesses state the reversal — "
                "this construction manual and a Lê Quí Đôn verse — from "
                "different genres and different transmissions. That is what "
                "makes it the tradition's shape rather than one book's quirk."
            )
        if c.get("phu_mau_note"):
            s.notes.append(str(c["phu_mau_note"]))


def _limits_section(report: TraditionReport, chart: dict) -> None:
    s = report.add(ReportSection("What This Report Does Not Claim", level=2))
    s.notes.append(
        "This is the CONSTRUCTION only: the board, Mệnh and Thân, the cục and "
        "Tử Vi's own seat. The remaining stars of the Tử Vi and Thiên Phủ "
        "series, the auxiliaries, and the palace delineations the pack holds "
        "are not placed here."
    )
    s.notes.append(
        f"The twelve palaces run in the Vietnamese order — {', '.join(palace_order()[:4])}"
        " and so on — and reading that sequence off a Chinese board is the "
        "single error this track is most exposed to."
    )
    s.notes.append(
        "Every rendering from the Vietnamese is unreviewed. The attribution of "
        "the verse material to Lê Quí Đôn is traditional and the pack declines "
        "to assert it as authorship."
    )
    if len(BRANCHES) != 12:  # pragma: no cover - a guard on the board itself
        s.refusals.append("The board does not have twelve palaces.")
