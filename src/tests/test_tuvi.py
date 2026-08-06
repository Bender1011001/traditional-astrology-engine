"""Tử Vi, whose whole point is that it is not Zi Wei relabelled.

The reversal of the palace order is the load-bearing fact. An engine that got
it wrong would produce a board that looks entirely correct — twelve palaces,
right names, right branches — with every topic in the wrong place, and nothing
about the output would betray it.
"""

from __future__ import annotations

from datetime import date

import pytest

from src.engine.multitradition.tuvi import (
    BRANCHES,
    build,
    cuc_for,
    cuc_numbers,
    cuc_table,
    menh_palace,
    palace_order,
    palaces_from_menh,
    place_tuvi,
    than_palace,
    tuvi_tables,
)
from src.engine.multitradition.types import BirthInput

BIRTH = BirthInput(
    name="Fixture", civil_date=date(1996, 8, 13), civil_time="07:18",
    utc_offset_hours=-7.0, latitude=38.2494, longitude=-122.0400,
    place_label="Fairfield, California",
)


# --- the reversal ---------------------------------------------------------


def test_the_palace_order_is_the_chinese_order_reversed():
    """Two independent Vietnamese witnesses state this."""
    order = palace_order()
    assert len(order) == 12
    assert order[0] == "Mệnh"
    # Phúc Đức is SECOND here and eleventh in the Chinese sequence.
    assert order[1] == "Phúc Đức"
    assert order[-1] == "Phụ Mẫu"


def test_the_reversal_actually_moves_topics():
    """The check that would catch a board built the Chinese way."""
    placed = palaces_from_menh("Tý")
    # Vietnamese: Phúc Đức is one step forward of Mệnh.
    assert placed["Phúc Đức"] == "Sửu"
    # Chinese would put Huynh Đệ there instead; here it is eleven steps on.
    assert placed["Huynh Đệ"] != "Sửu"


def test_every_palace_gets_exactly_one_cell():
    placed = palaces_from_menh("Ngọ")
    assert len(placed) == 12
    assert len(set(placed.values())) == 12


# --- the board ------------------------------------------------------------


def test_the_board_is_twelve_branches_clockwise_from_ty():
    assert len(BRANCHES) == 12
    assert BRANCHES[0] == "Tý"
    assert BRANCHES[2] == "Dần"


def test_menh_counts_forward_to_the_month_then_backward_to_the_hour():
    """Month 1 at the hour Tý must land on Dần, where the count begins."""
    assert menh_palace(1, 0) == "Dần"
    # Each later month advances the stopping palace by one.
    assert menh_palace(2, 0) == "Mão"
    # Each later hour retreats it by one.
    assert menh_palace(1, 1) == "Sửu"


def test_than_runs_forward_where_menh_runs_backward():
    assert than_palace(1, 1) == "Mão"
    assert menh_palace(1, 1) == "Sửu"


def test_an_impossible_month_is_an_error_not_a_guess():
    with pytest.raises(ValueError):
        menh_palace(13, 0)


# --- the cục grid ---------------------------------------------------------


def test_the_cuc_grid_is_a_latin_square():
    """The pack states the property; it is the only check on a 5x5 transcription."""
    table = cuc_table()
    assert table, "the cục grid did not load"
    for palace, row in table.items():
        assert len(set(row.values())) == len(row), palace
    # And every column also holds each cục once.
    pairs = sorted({p for row in table.values() for p in row})
    for pair in pairs:
        column = {row[pair] for row in table.values()}
        assert len(column) == len(cuc_numbers()), pair


def test_every_cuc_carries_its_number():
    numbers = cuc_numbers()
    assert set(numbers.values()) == {2, 3, 4, 5, 6}


def test_the_cuc_needs_both_the_stem_and_the_menh_palace():
    got = cuc_for("bing", "Mão")
    assert got is not None
    assert got["number"] in (2, 3, 4, 5, 6)
    assert cuc_for("not-a-stem", "Mão") is None


# --- Tử Vi's seat ---------------------------------------------------------


def test_four_of_five_printed_tables_partition_the_thirty_days():
    """And the fifth does not, which the pack documents and this confirms."""
    broken = []
    for cuc, table in tuvi_tables().items():
        days = sorted(d for cell in table.values() for d in cell)
        if days != list(range(1, 31)):
            broken.append(cuc)
    assert broken == ["Kim tứ cục"], broken


def test_the_documented_defect_is_exactly_two_cells():
    """The pack says 148 of 150 entries agree with the closed form."""
    from src.engine.multitradition.tuvi import cuc_numbers, tuvi_seat

    disagreeing = [
        (cuc, day)
        for cuc, number in cuc_numbers().items()
        for day in range(1, 31)
        if tuvi_seat(cuc, number, day)["status"] != "agree"
    ]
    assert disagreeing == [("Kim tứ cục", 21), ("Kim tứ cục", 24)]


def test_the_printed_table_is_not_emended():
    """The pack's policy: keep the printed reading, predict the correction.

    Day 21 is printed at Mùi and the reconstruction says Thìn. The printed
    reading is what is returned; the reconstruction is reported alongside it
    as a prediction, not substituted for it.
    """
    from src.engine.multitradition.tuvi import tuvi_seat

    got = tuvi_seat("Kim tứ cục", 4, 21)
    assert got["palace"] == "Mùi"
    assert got["closed_form_predicts"] == "Thìn"
    assert got["status"] == "printed_and_reconstruction_disagree"


def test_a_day_the_table_omits_is_reported_not_filled():
    from src.engine.multitradition.tuvi import tuvi_seat

    got = tuvi_seat("Kim tứ cục", 4, 24)
    assert got["palace"] is None
    assert got["closed_form_predicts"] == "Mùi"
    assert got["status"] == "printed_table_defective"


def test_tuvi_is_placed_for_every_day_the_tables_carry():
    for cuc in tuvi_tables():
        for day in range(1, 31):
            seat = place_tuvi(cuc, day)
            if seat is None:
                assert (cuc, day) == ("Kim tứ cục", 24)
                continue
            assert seat in BRANCHES, (cuc, day)


def test_an_unknown_cuc_places_nothing_rather_than_guessing():
    assert place_tuvi("not a cục", 5) is None


# --- assembly and the report ---------------------------------------------


def test_build_produces_a_complete_board():
    got = build(6, 30, 4, "bing")
    assert got["menh"] in BRANCHES
    assert got["than"] in BRANCHES
    assert len(got["palaces"]) == 12
    assert got["cuc"]["number"] in (2, 3, 4, 5, 6)
    assert got["tuvi_palace"] in BRANCHES


def test_a_missing_stem_refuses_the_cuc_and_says_why():
    got = build(6, 30, 4, "")
    assert got["cuc"] is None
    assert got["tuvi_palace"] is None
    assert "cục" in got["tuvi_not_placed"]


def test_the_report_builds_and_names_the_meridian():
    from src.engine.traditions.readiness import classify
    from src.engine.traditions.report_lint import lint
    from src.engine.traditions.tuvi_report import build_report

    report = build_report(BIRTH)
    assert not lint(report)
    assert classify(report).kind
    blob = " ".join(n for s in report.sections for n in s.notes)
    assert "105E" in blob or "105°E" in blob


def test_the_report_says_it_is_not_the_chinese_board():
    from src.engine.traditions.tuvi_report import build_report

    report = build_report(BIRTH)
    section = next(
        s for s in report.sections if "Chinese Board" in s.title
    )
    assert section.delineations
    blob = " ".join(section.notes)
    assert "reversed" in blob or "anticlockwise" in blob
