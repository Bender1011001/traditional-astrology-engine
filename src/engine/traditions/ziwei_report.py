"""A Zi Wei Dou Shu report, with the board actually filled.

The panel got as far as ``constructed_palaces_only`` - twelve named palaces and
not one star in them. This report places the fourteen main stars, reads the
brightness grid for each, and quotes juan 2's own entry for whatever occupies
the life palace.

The whole layer turns on the LUNAR DAY, and that is the one input this engine
cannot always settle: the panel computes it under three meridians and they can
differ by one. Choosing a meridian would produce a clean-looking chart whose
cleanliness was manufactured. So where the day is invariant the board is
reported settled; where it is not, every star is placed under each candidate
day and the ones that move are named with both palaces. On a two-bureau chart
a one-day disagreement moves the entire board by one palace, and saying that
plainly is the report.

The delineations are quoted where the pack rendered them and reported as
transcribed-but-unrendered where it did not - which is a different state from
missing, and the fixable one.
"""

from __future__ import annotations

from typing import Any

from ..multitradition import build_panel
from ..multitradition.types import BirthInput
from ..multitradition.ziwei_stars import (
    BRANCH_HANZI,
    FOURTEEN,
    STAR_NAMES,
    place_across_candidates,
    star_delineation,
)
from .report import Delineation, ReportSection, TraditionReport

STEM_HANZI = {
    "jia": "甲", "yi": "乙", "bing": "丙", "ding": "丁", "wu": "戊",
    "ji": "己", "geng": "庚", "xin": "辛", "ren": "壬", "gui": "癸",
}

BRIGHTNESS_ENGLISH = {
    "庙": "temple", "旺": "prospering", "得地": "well placed",
    "利益": "benefiting", "平和": "neutral", "不得地": "ill placed",
    "落陷": "fallen",
}


def _facts(birth: BirthInput) -> dict[str, Any]:
    panel = build_panel(birth)
    section = next(
        (
            s for s in panel["sections"]
            if s["tradition_id"] == "ziwei_doushu" and not s.get("error")
        ),
        None,
    )
    if section is None:
        raise RuntimeError("the Zi Wei calculation produced no facts")
    return section["facts"]


def build_report(birth: BirthInput) -> TraditionReport:
    facts = _facts(birth)
    report = TraditionReport(
        tradition_id="ziwei_doushu",
        display_name="Zi Wei Dou Shu — the Twelve Palaces and the Fourteen",
        birth=birth.to_dict(),
    )
    board = _place_board(facts)
    _opening(report, birth, facts)
    _calendar_section(report, facts)
    _palaces_section(report, facts)
    _stars_section(report, facts, board)
    _life_palace_section(report, facts, board)
    _transformations_section(report, facts)
    _limits_section(report, facts, board)
    return report


def _place_board(facts: dict) -> dict[str, Any]:
    construction = facts.get("chart_construction") or {}
    life = (construction.get("life_palace") or {}).get("branch")
    stem = (facts.get("four_transformations") or {}).get("birth_year_stem")
    stem_hanzi = STEM_HANZI.get(str(stem))
    days = sorted({
        r.get("lunar_day")
        for r in (facts.get("calendar_regime_check") or {}).get("regimes", [])
        if r.get("lunar_day")
    })
    if not life or not stem_hanzi or not days:
        return {
            "status": "not_placed",
            "why": (
                "the life palace, the birth-year stem or the lunar day was "
                "not computed"
            ),
        }
    return place_across_candidates(stem_hanzi, life, days)


def _opening(report: TraditionReport, birth: BirthInput, facts: dict) -> None:
    s = report.add(ReportSection("The Chart and Its Palaces", level=2))
    c = facts.get("chart_construction") or {}
    life = c.get("life_palace") or {}
    body = c.get("body_palace") or {}
    s.notes.append(
        f"Born {birth.civil_date} at {birth.civil_time} in "
        f"{birth.place_label}. Chart month {c.get('chart_month')}; the life "
        f"palace falls at {life.get('label')} ({life.get('branch')}) and the "
        f"body palace at {body.get('label')} ({body.get('branch')})."
    )
    hour = (facts.get("hour_keyed_placements") or {}).get("true_solar_time")
    if hour:
        s.notes.append(
            "The double-hour is taken at true solar time "
            f"({hour.get('time')}), giving {hour.get('double_hour_label')}. "
            "The clock-time reckoning is carried alongside it in the panel "
            "because the two can fall in different double-hours and that "
            "moves the life palace."
        )


def _calendar_section(report: TraditionReport, facts: dict) -> None:
    """The gate that decides whether the fourteen can be placed at all."""
    s = report.add(ReportSection("Which Calendar This Chart Assumes", level=2))
    check = facts.get("calendar_regime_check") or {}
    s.notes.append(str(check.get("purpose", "")))
    for regime in check.get("regimes", []):
        s.notes.append(
            f"- **{regime.get('label')}** — lunar month "
            f"{regime.get('lunar_month_number')}"
            + (" (intercalary)" if regime.get("is_intercalary_month") else "")
            + f", day {regime.get('lunar_day')}."
        )
    if check.get("chart_month_invariant"):
        s.notes.append(
            f"The chart month is **{check.get('chart_month')}** under every "
            "regime, so the twelve palaces stand whatever the calendar does."
        )
    else:
        s.refusals.append(
            "The chart month itself is not invariant across the regimes. "
            "Everything below rests on the month, so nothing below is settled."
        )
    if check.get("lunar_day_invariant"):
        s.notes.append(
            "The lunar day is invariant too, so the fourteen main stars have "
            "one placement rather than several."
        )
    else:
        s.notes.append(
            "The lunar day is **not** invariant. Zi Wei's own palace is "
            "computed from it, so the board is placed under each candidate "
            "day below rather than under a chosen meridian."
        )


def _palaces_section(report: TraditionReport, facts: dict) -> None:
    s = report.add(ReportSection("The Twelve Topic Palaces", level=2))
    palaces = (facts.get("chart_construction") or {}).get("topic_palaces") or {}
    for topic, row in palaces.items():
        label = topic.replace("_historical_label", "").replace("_", " ")
        s.notes.append(
            f"- **{label}** — {row.get('branch_label')} "
            f"({row.get('branch')}), {row.get('topic_label')}."
        )
    order = facts.get("twelve_topic_palace_order") or []
    if any("historical_label" in t for t in order):
        s.notes.append(
            "Two of the twelve carry the labels the text itself uses — 夫妻宮 "
            "for the spouse palace and 僕役宮 for servants. They are kept as "
            "printed rather than modernised, because renaming them would "
            "quietly edit the source."
        )


def _stars_section(
    report: TraditionReport, facts: dict, board: dict[str, Any]
) -> None:
    s = report.add(ReportSection("The Fourteen Main Stars", level=2))
    if board.get("status") == "not_placed":
        s.refusals.append(
            "The fourteen are not placed: " + str(board.get("why", "")) + "."
        )
        return

    boards = board.get("boards") or {}
    first = next(iter(boards.values()), None)
    if first:
        bureau = first.get("bureau") or {}
        s.notes.append(
            f"The five-phase bureau is **{bureau.get('label')}** "
            f"({bureau.get('chinese')}), read by composing the Five Tigers "
            "couplets with the nayin song — the 10x12 grid this needs is "
            "nowhere printed as a grid, and the pack composes it exactly as "
            "the chapter's own worked example does."
        )
        s.notes.append(
            "Zi Wei's palace is found by a closed form recovered from the "
            "five printed grids: it reproduces 58 of their 60 cells and all "
            "ten day-one and day-two anchors the verses state in words. The "
            "two cells it misses are single-character transcription defects, "
            "detectable because a grid must partition the thirty days exactly "
            "once. Where it disagrees with a printed cell it corrects it."
        )

    s.notes.append(str(board.get("note", "")))
    settled = board.get("settled_stars") or {}
    moving = board.get("moving_stars") or {}
    for star in FOURTEEN:
        name = STAR_NAMES.get(star, star)
        if star in settled:
            branch = settled[star]
            level = (first or {}).get("brightness", {}).get(star)
            gloss = (
                f" — {BRIGHTNESS_ENGLISH.get(level, level)}" if level else ""
            )
            s.notes.append(
                f"- **{star} ({name})** — {BRANCH_HANZI.get(branch, branch)}"
                f"{gloss}."
            )
        elif star in moving:
            where = ", ".join(
                f"day {d}: {BRANCH_HANZI.get(b, b)}"
                for d, b in sorted(moving[star].items())
            )
            s.notes.append(
                f"- **{star} ({name})** — moves with the calendar: {where}."
            )
    if moving:
        count = (
            "None of the fourteen has" if len(moving) == len(FOURTEEN)
            else f"{len(moving)} of the fourteen do not have"
        )
        s.refusals.append(
            f"{count} a settled palace. Their positions depend on the lunar "
            "day, and the meridians disagree by one — which on a two-bureau "
            "chart shifts the entire board by a single palace. Both "
            "placements are given above; neither is presented as the answer."
        )


def _life_palace_section(
    report: TraditionReport, facts: dict, board: dict[str, Any]
) -> None:
    """What juan 2 says about whatever holds the life palace."""
    s = report.add(ReportSection("The Life Palace and Its Stars", level=2))
    life = (
        (facts.get("chart_construction") or {}).get("life_palace") or {}
    ).get("branch")
    if not life or board.get("status") == "not_placed":
        s.refusals.append("No star could be placed in the life palace.")
        return

    boards = board.get("boards") or {}
    occupants: dict[str, list[int]] = {}
    for day, b in boards.items():
        for star, branch in (b.get("stars") or {}).items():
            if branch == life:
                occupants.setdefault(star, []).append(day)

    if not occupants:
        s.notes.append(
            "None of the fourteen falls in the life palace under any "
            "candidate day. The text reads such a palace from its opposite "
            "and from the auxiliary stars; that layer is not implemented here "
            "and the absence is reported rather than filled."
        )
        return

    all_days = set(boards)
    for star, days in occupants.items():
        certain = set(days) == all_days
        d = star_delineation(star)
        header = f"**{star} ({STAR_NAMES.get(star, star)})**"
        if not certain:
            header += (
                " — only under lunar day "
                + ", ".join(str(x) for x in sorted(days))
                + f" of {sorted(all_days)}"
            )
        s.notes.append(header)
        if d is None:
            continue
        if d.get("translated") and d.get("engine_rendering"):
            s.delineations.append(
                Delineation(
                    text=str(d["engine_rendering"]),
                    rule_id=d["rule_id"],
                    source=(
                        "Ziwei Doushu Quanshu, "
                        + str(d.get("location") or "juan 2")
                    ),
                    evidence_grade=str(d.get("evidence_grade", "?")),
                    trigger=(
                        f"{star} occupies the life palace"
                        + ("" if certain else ", under one candidate day")
                    ),
                )
            )
        untranslated = [
            c["cell"] for c in d.get("untranslated_cells") or []
            if c.get("has_chinese")
        ]
        if untranslated:
            s.notes.append(
                "Transcribed but not rendered for this star: "
                + ", ".join(untranslated)
                + ". The Chinese is on disk; the rendering pass did not reach "
                "it. That is a different state from missing, and the fixable "
                "one."
            )


def _transformations_section(report: TraditionReport, facts: dict) -> None:
    s = report.add(ReportSection("The Four Transformations", level=2))
    four = facts.get("four_transformations") or {}
    fork = four.get("year_boundary_fork") or {}
    s.notes.append(
        f"Birth-year stem {four.get('birth_year_stem')}, branch "
        f"{four.get('birth_year_branch')}."
    )
    if fork:
        if fork.get("conventions_agree"):
            s.notes.append(
                "The lunar-new-year and li chun conventions assign the same "
                "sexagenary year to this birth, so the transformations do not "
                "turn on which boundary is used. "
                f"{fork.get('verdict', '')}"
            )
        else:
            s.refusals.append(
                "The two year-boundary conventions assign DIFFERENT "
                "sexagenary years to this birth. The four transformations "
                "follow the year stem, so they are not settled here."
            )


def _limits_section(
    report: TraditionReport, facts: dict, board: dict[str, Any]
) -> None:
    s = report.add(ReportSection("What This Report Does Not Claim", level=2))
    profile = facts.get("source_profile") or {}
    s.notes.append(
        "Every rule behind this chart carries evidence grade "
        f"{profile.get('evidence_grade_of_every_rule')} and the pack's review "
        f"status is {profile.get('review_status')}. The renderings from the "
        "Chinese are unreviewed."
    )
    s.notes.append(
        "The auxiliary stars — Lu Cun, Qing Yang and Tuo Luo, Huo and Ling, "
        "the Kui and Yue pair and the rest — are computed in the panel as "
        "positions and are not delineated here. The judgment chapter's own "
        "first step is to check whether the life and body palaces and Lu and "
        "Ma have fallen into a void, and that step is not implemented."
    )
    if board.get("moving_stars"):
        s.notes.append(
            "Because the lunar day is not invariant here, this report shows "
            "the board under each candidate rather than choosing one. A "
            "single-meridian chart would look more finished and would be "
            "asserting something this engine cannot check."
        )
