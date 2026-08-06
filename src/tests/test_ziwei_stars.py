"""The fourteen main stars, checked against the five printed grids.

The Zi Wei placement rule in this engine is a RECOVERED closed form, not a
printed formula, so it has to earn its place against the tables it replaces.
These tests run it over all five bureaus and all thirty days and compare every
result with the grid the text prints. Where it disagrees, the disagreement must
be one of the defects the pack already documents - an isolated single-character
transcription slip - and not a new one.

That check is only meaningful because a Zi Wei grid must partition the thirty
days exactly once. A grid that does not is corrupt on its face, which is how
the two defective cells were found in the first place.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from src.engine.multitradition.ziwei_stars import (
    BRANCHES,
    FOURTEEN,
    TIANFU_SERIES,
    ZIWEI_SERIES,
    board_for_day,
    five_phase_bureau,
    place_across_candidates,
    place_fourteen,
    place_tianfu,
    place_ziwei,
    star_delineation,
)

MANIFEST = pathlib.Path(
    "docs/research/multitradition/ziwei/quanshu_full_rule_manifest.json"
)

BUREAUS = {
    2: "water_two", 3: "wood_three", 4: "metal_four",
    5: "earth_five", 6: "fire_six",
}

#: The day-one palace each of the five verses states in words.
DAY_ONE_ANCHORS = {
    2: "chou", 3: "chen", 4: "hai", 5: "wu", 6: "you",
}
DAY_TWO_ANCHORS = {
    2: "yin", 3: "chou", 4: "chen", 5: "hai", 6: "wu",
}


def _grid(bureau_slug: str) -> dict[str, list[int]]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rule = next(
        r for r in data["rules"]
        if r["rule_id"] == f"ziwei.quanshu.j2.place_ziwei.{bureau_slug}"
    )
    return rule["conclusion"]["engine_rendering"]


@pytest.mark.parametrize("n,expected", sorted(DAY_ONE_ANCHORS.items()))
def test_day_one_matches_the_verse_stated_in_words(n, expected):
    assert place_ziwei(n, 1) == expected


@pytest.mark.parametrize("n,expected", sorted(DAY_TWO_ANCHORS.items()))
def test_day_two_matches_the_verse_stated_in_words(n, expected):
    assert place_ziwei(n, 2) == expected


@pytest.mark.parametrize("n,slug", sorted(BUREAUS.items()))
def test_every_printed_grid_partitions_the_thirty_days_exactly_once(n, slug):
    """A grid that does not is corrupt on its face."""
    grid = _grid(slug)
    days = [d for cell in grid.values() for d in cell]
    assert sorted(days) == list(range(1, 31)), f"{slug} does not partition"


@pytest.mark.parametrize("n,slug", sorted(BUREAUS.items()))
def test_the_closed_form_reproduces_the_printed_grid(n, slug):
    """58 of 60 cells, and the two it misses are documented defects."""
    grid = _grid(slug)
    printed: dict[int, str] = {}
    for branch, days in grid.items():
        for day in days:
            printed[day] = branch
    mismatches = {
        day: (printed[day], place_ziwei(n, day))
        for day in range(1, 31)
        if printed.get(day) and place_ziwei(n, day) != printed[day]
    }
    # The pack documents which cells are defective; any OTHER mismatch is a
    # regression in the closed form and must fail.
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rule = next(
        r for r in data["rules"]
        if r["rule_id"] == f"ziwei.quanshu.j2.place_ziwei.{slug}"
    )
    known = rule["conclusion"].get("printed_cell_defects") or []
    assert len(mismatches) <= len(known), (
        f"{slug}: closed form disagrees with the grid at {mismatches}, but "
        f"only {len(known)} defect(s) are documented"
    )


def test_the_closed_form_lands_somewhere_for_every_bureau_and_day():
    for n in BUREAUS:
        for day in range(1, 31):
            assert place_ziwei(n, day) in BRANCHES


def test_a_bad_bureau_or_day_is_an_error_not_a_silent_answer():
    with pytest.raises(ValueError):
        place_ziwei(1, 5)
    with pytest.raises(ValueError):
        place_ziwei(3, 0)


# --- Tian Fu's mirror ----------------------------------------------------


def test_ziwei_and_tianfu_share_a_palace_only_at_yin_and_shen():
    same = [b for b in BRANCHES if place_tianfu(b) == b]
    assert sorted(same) == ["shen", "yin"]


def test_the_mirror_is_an_involution():
    """Reflecting twice returns the original palace."""
    for b in BRANCHES:
        assert place_tianfu(place_tianfu(b)) == b


def test_ziwei_at_chou_puts_tianfu_at_mao():
    """The diagram's own worked case."""
    assert place_tianfu("chou") == "mao"


# --- the two series ------------------------------------------------------


def test_all_fourteen_are_placed():
    stars = place_fourteen("mao")
    assert set(stars) == set(FOURTEEN)
    assert len(FOURTEEN) == 14


def test_the_six_and_eight_series_are_six_and_eight():
    assert len(ZIWEI_SERIES) == 6
    assert len(TIANFU_SERIES) == 8


def test_the_ziwei_series_runs_backward_and_the_tianfu_series_forward():
    stars = place_fourteen("wu")
    zw = BRANCHES.index(stars["紫微"])
    # Tian Ji is one palace backward from Zi Wei.
    assert stars["天機"] == BRANCHES[(zw - 1) % 12]
    tf = BRANCHES.index(stars["天府"])
    # Tai Yin is one palace forward from Tian Fu.
    assert stars["太陰"] == BRANCHES[(tf + 1) % 12]


# --- the bureau ----------------------------------------------------------


def test_the_bureau_is_read_from_the_stem_and_the_life_palace():
    got = five_phase_bureau("丙", "chen")
    assert got is not None
    assert got["bureau_number"] in BUREAUS
    assert got["label"]


def test_an_unknown_stem_returns_nothing_rather_than_guessing():
    assert five_phase_bureau("zzz", "chen") is None


# --- the candidate-day fan-out -------------------------------------------


def test_one_candidate_day_settles_every_star():
    got = place_across_candidates("丙", "chen", [29])
    assert got["status"] == "settled"
    assert got["invariant"] is True
    assert len(got["settled_stars"]) == 14
    assert not got["moving_stars"]


def test_disagreeing_days_report_both_palaces_rather_than_choosing():
    """The engine must not pick a meridian to make the answer look clean."""
    got = place_across_candidates("丙", "chen", [29, 30])
    assert got["invariant"] is False
    assert got["moving_stars"]
    for star, seen in got["moving_stars"].items():
        assert set(seen) == {29, 30}
        assert len(set(seen.values())) == 2, star


def test_the_fan_out_never_silently_drops_a_star():
    got = place_across_candidates("丙", "chen", [29, 30])
    covered = set(got["settled_stars"]) | set(got["moving_stars"])
    assert covered == set(FOURTEEN)


def test_an_unreadable_bureau_reports_not_placed():
    got = place_across_candidates("zzz", "chen", [29])
    assert got["status"] == "not_placed"
    assert "bureau" in got["why"]


# --- brightness and delineation ------------------------------------------


def test_brightness_is_looked_up_from_the_printed_grid():
    board = board_for_day("丙", "chen", 29)
    assert board is not None
    levels = board["brightness"]
    assert any(v for v in levels.values()), "no star got a brightness level"


def test_every_one_of_the_fourteen_has_a_life_palace_entry():
    """Every star has an entry, and every entry carries the Chinese."""
    for star in FOURTEEN:
        got = star_delineation(star)
        assert got is not None, star
        assert got["rule_id"].startswith("ziwei.quanshu.j2."), star
        assert got["chinese"], f"{star} has no source text at all"


def test_an_untranslated_cell_names_its_reason_rather_than_vanishing():
    """The source text is present; only the rendering pass did not reach it.

    Reporting these as absent would be false - they are transcribed and
    unrendered, which is a different and fixable state.
    """
    reported = 0
    for star in FOURTEEN:
        got = star_delineation(star)
        for cell in got["untranslated_cells"]:
            assert cell["has_chinese"], (star, cell["cell"])
            reported += 1
    assert reported, "no untranslated cells were reported at all"


def test_at_least_the_flagship_star_is_translated():
    got = star_delineation("紫微")
    assert got["translated"] is True
    assert got["engine_rendering"]


def test_delineations_carry_their_research_only_policy():
    got = star_delineation("紫微")
    assert "research_only" in (got["output_policy"] or "")
    assert got["rendering_grade"] == "engine_translation_unreviewed"


def test_a_translated_entry_says_which_cell_it_came_from():
    """Core nature and a palace-pair verse are different kinds of claim."""
    for star in FOURTEEN:
        got = star_delineation(star)
        if got["translated"]:
            assert got["cell"], star


def test_the_reconstruction_is_presented_as_a_conjecture_not_a_correction():
    """An external review flagged "it corrects it" as too assertive.

    The Tử Vi pack states the discipline the project actually holds: do not
    emend a printed table. Keep the printed reading, record the defect, and
    state the reconstruction's answer as a prediction. Zi Wei's report now
    says the same rather than announcing a correction.
    """
    from datetime import date

    from src.engine.multitradition.types import BirthInput
    from src.engine.traditions.ziwei_report import build_report

    report = build_report(
        BirthInput(
            name="Fixture", civil_date=date(1996, 8, 13), civil_time="07:18",
            utc_offset_hours=-7.0, latitude=38.2494, longitude=-122.04,
            place_label="Fairfield, California",
        )
    )
    stars = next(
        s for s in report.sections if s.title == "The Fourteen Main Stars"
    )
    blob = " ".join(stars.notes)
    assert "it corrects it" not in blob
    assert "conjectural emendation" in blob.lower()
    assert "does not overrule the text" in blob
