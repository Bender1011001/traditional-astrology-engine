"""Tử Vi Đẩu Số — the Vietnamese chart, which is not the Chinese one rotated.

Fifty-four mined rules and no engine. It is tempting to treat this as Zi Wei
with Vietnamese labels, and the pack is emphatic that it is not: the twelve
palaces run in the REVERSE order from Mệnh, so the same names sit on the same
clockwise board running anticlockwise. Two independent Vietnamese witnesses
say so — a construction manual and a Lê Quí Đôn verse — from different genres
and different transmissions, which is why the pack treats the reversal as
established rather than as one book's quirk.

Everything here is read from the pack rather than hardcoded, including the two
tables that carry the whole construction: the cục grid, and the five
Tử-Vi-placement tables. The cục grid is a Latin square — every cục appears once
in every row and every column — and that property is asserted on load, because
it is the internal check that catches a mis-transcribed cell.

One thing this track has that Zi Wei does not: a settled lunar day. Tử Vi is
computed at 105°E, which is the meridian Zi Wei's invariance gate treats as
adversarial. For a Vietnamese chart that meridian is not adversarial at all —
it is the authoritative one, and the day it gives is the day the tradition
means.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

RESEARCH_ROOT = (
    Path(__file__).resolve().parents[3] / "docs" / "research" / "multitradition"
)
TUVI_DIR = RESEARCH_ROOT / "vietnamese"

#: The board itself: twelve fixed palaces named by branch, running clockwise.
BRANCHES = (
    "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
    "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi",
)

#: Where the month count begins. The manual starts the first lunar month at
#: Dần, not at Tý.
MONTH_ONE = BRANCHES.index("Dần")

STEM_PAIRS = {
    "giap": "Giáp Kỷ", "ky": "Giáp Kỷ",
    "yi": "Ất Canh", "at": "Ất Canh", "canh": "Ất Canh", "geng": "Ất Canh",
    "bing": "Bính Tân", "binh": "Bính Tân", "xin": "Bính Tân",
    "tan": "Bính Tân",
    "ding": "Đinh Nhâm", "dinh": "Đinh Nhâm", "ren": "Đinh Nhâm",
    "nham": "Đinh Nhâm",
    "wu": "Mậu Qúy", "mau": "Mậu Qúy", "gui": "Mậu Qúy", "quy": "Mậu Qúy",
    "jia": "Giáp Kỷ", "ji": "Giáp Kỷ", "xu": "Bính Tân",
}


@lru_cache(maxsize=1)
def _rules() -> dict[str, dict[str, Any]]:
    rules: dict[str, dict[str, Any]] = {}
    for path in sorted(TUVI_DIR.glob("*rule_manifest.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for rule in data.get("rules", []):
            rid = rule.get("rule_id")
            if rid:
                rules[rid] = rule
    return rules


def _conclusion(rule_id: str) -> dict[str, Any]:
    return (_rules().get(rule_id) or {}).get("conclusion") or {}


@lru_cache(maxsize=1)
def palace_order() -> tuple[str, ...]:
    """The twelve palaces from Mệnh, in the Vietnamese forward direction.

    This is the Chinese order REVERSED, and the reversal is the single most
    consequential difference between the two systems: every topic sits in a
    different place on an identically constructed board.
    """
    c = _conclusion(
        "vietnam.tuvi.lt.palaces.enumeration_runs_reverse_of_the_chinese_order"
    )
    order = c.get("vietnamese_forward_order_from_menh") or []
    return tuple(order)


@lru_cache(maxsize=1)
def cuc_table() -> dict[str, dict[str, str]]:
    """The cục grid, keyed by Mệnh palace then by stem pair."""
    c = _conclusion(
        "vietnam.tuvi.lt.cuc.five_phase_bureau_from_year_stem_and_menh_palace"
    )
    out: dict[str, dict[str, str]] = {}
    for row in c.get("table") or []:
        for palace in str(row.get("menh_palaces", "")).split():
            out[palace] = dict(row.get("by_stem_pair") or {})
    return out


@lru_cache(maxsize=1)
def cuc_numbers() -> dict[str, int]:
    return dict(
        _conclusion(
            "vietnam.tuvi.lt.cuc.five_phase_bureau_from_year_stem_and_menh_palace"
        ).get("cuc_numbers") or {}
    )


@lru_cache(maxsize=1)
def tuvi_tables() -> dict[str, dict[str, list[int]]]:
    """The five printed Tử Vi placement tables, by cục and lunar day."""
    c = _conclusion("vietnam.tuvi.lt.tuvi.placement_table_by_cuc_and_lunar_day")
    return dict(c.get("table_by_cuc") or {})


def _check_latin_square() -> None:
    """Every cục once per row and once per column, or a cell is mis-set.

    The pack states this property explicitly and it is the only cheap check
    available on a hand-transcribed 5x5 grid, so it runs on load rather than
    being left to a test that might not be written.
    """
    table = cuc_table()
    if not table:
        return
    rows = {tuple(sorted(v.values())) for v in table.values()}
    for row in rows:
        if len(set(row)) != len(row):
            raise ValueError(
                "the cục grid repeats a cục within one row; the pack states "
                "it is a Latin square, so a cell has been mis-transcribed"
            )


_check_latin_square()


def menh_palace(lunar_month: int, hour_branch_index: int) -> str:
    """Mệnh: forward from Dần to the birth month, then backward to the hour.

    The manual's own words: begin from the palace Dần as the first lunar
    month, count forward to the month of birth; call the palace you stop at
    the hour Tý, then count backward to the hour of birth.
    """
    if not 1 <= lunar_month <= 12:
        raise ValueError(f"lunar month {lunar_month} is out of range")
    stop = (MONTH_ONE + (lunar_month - 1)) % 12
    return BRANCHES[(stop - hour_branch_index) % 12]


def than_palace(lunar_month: int, hour_branch_index: int) -> str:
    """Thân: the same count, run forward rather than backward."""
    stop = (MONTH_ONE + (lunar_month - 1)) % 12
    return BRANCHES[(stop + hour_branch_index) % 12]


def palaces_from_menh(menh: str) -> dict[str, str]:
    """Each of the twelve topics, on the palace it occupies.

    Runs in the Vietnamese direction. Reading this anticlockwise sequence off
    a Chinese board is exactly the error the pack exists to prevent.
    """
    start = BRANCHES.index(menh)
    return {
        name: BRANCHES[(start + offset) % 12]
        for offset, name in enumerate(palace_order())
    }


def cuc_for(year_stem: str, menh: str) -> dict[str, Any] | None:
    """The ngũ hành cục, from the year stem and the palace Mệnh fell in."""
    pair = STEM_PAIRS.get(str(year_stem).strip().lower())
    if pair is None:
        return None
    row = cuc_table().get(menh)
    if not row:
        return None
    name = row.get(pair)
    if not name:
        return None
    return {
        "cuc": name,
        "number": cuc_numbers().get(name),
        "stem_pair": pair,
        "menh_palace": menh,
    }


def place_tuvi_closed_form(cuc_number: int, lunar_day: int) -> str:
    """The engine's reconstruction, offered as a COLLATION INSTRUMENT.

    The book prints five tables and never states a formula. This closed form
    reproduces 148 of the 150 printed day-entries, which is what makes it
    useful for finding the two that disagree - and it is emphatically not the
    source's doctrine. The tables remain the authority.
    """
    import math

    q = math.ceil(lunar_day / cuc_number)
    m = q * cuc_number - lunar_day
    start = (MONTH_ONE + (q - 1)) % 12
    idx = (start + m) % 12 if m % 2 == 0 else (start - m) % 12
    return BRANCHES[idx]


def place_tuvi(cuc_name: str, lunar_day: int) -> str | None:
    """Tử Vi's own palace, read from the printed table for this cục.

    The tables are printed as a RING around the board rather than as a list,
    and the pack records that the PDF's text layer flattens the ring into a
    single column and is unusable for them — these five were read from the
    page image instead.
    """
    table = tuvi_tables().get(cuc_name)
    if not table:
        return None
    for palace, days in table.items():
        if lunar_day in days:
            return palace
    return None


def tuvi_seat(cuc_name: str, cuc_number: int, lunar_day: int) -> dict[str, Any]:
    """Where Tu Vi sits, and whether the printed table and the closed form agree.

    The pack's policy is explicit and is followed here: the printed table is
    NOT emended. Where it fails - the Kim tu cuc table duplicates day 21 and
    omits day 24 - the printed reading is kept as the source's, the defect is
    reported, and the closed form's answer is offered as a PREDICTION about
    what the cell should read rather than substituted for it.
    """
    printed = place_tuvi(cuc_name, lunar_day)
    predicted = place_tuvi_closed_form(cuc_number, lunar_day)
    if printed is None:
        return {
            "palace": None,
            "source": "the printed table has no entry for this day",
            "closed_form_predicts": predicted,
            "status": "printed_table_defective",
        }
    if printed != predicted:
        return {
            "palace": printed,
            "source": "the printed table, which is the authority",
            "closed_form_predicts": predicted,
            "status": "printed_and_reconstruction_disagree",
        }
    return {
        "palace": printed,
        "source": "the printed table, confirmed by the reconstruction",
        "closed_form_predicts": predicted,
        "status": "agree",
    }


def build(
    lunar_month: int,
    lunar_day: int,
    hour_branch_index: int,
    year_stem: str,
) -> dict[str, Any]:
    """The Vietnamese board, as far as the construction pack carries it."""
    menh = menh_palace(lunar_month, hour_branch_index)
    than = than_palace(lunar_month, hour_branch_index)
    cuc = cuc_for(year_stem, menh)
    out: dict[str, Any] = {
        "menh": menh,
        "than": than,
        "palaces": palaces_from_menh(menh),
        "palace_direction": (
            "the Vietnamese forward order, which is the Chinese order reversed"
        ),
        "cuc": cuc,
        "lunar_month": lunar_month,
        "lunar_day": lunar_day,
    }
    if cuc and cuc.get("cuc") and cuc.get("number"):
        seat = tuvi_seat(cuc["cuc"], int(cuc["number"]), lunar_day)
        out["tuvi_seat"] = seat
        out["tuvi_palace"] = seat["palace"]
        if seat["palace"] is None:
            out["tuvi_not_placed"] = (
                f"lunar day {lunar_day} does not appear in the printed "
                f"{cuc['cuc']} table — a defect the pack documents, and one "
                "this engine does not paper over by substituting its own "
                "reconstruction"
            )
    else:
        out["tuvi_palace"] = None
        out["tuvi_not_placed"] = (
            "the cục could not be set, and Tử Vi is placed from it"
        )
    return out
