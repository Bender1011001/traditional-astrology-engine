"""Lilly's Book 1 on a nativity — and the horary half kept off it.

The distinguishing risk in this track is not translation. Lilly wrote in
English, so nothing here is an unreviewed rendering. The risk is CATEGORY: a
large part of Book 1 judges a question asked at a moment, and running it over a
person born at one produces output that looks exactly as authoritative as the
part that belongs there.
"""

from __future__ import annotations

from datetime import date

import pytest

from src.engine.multitradition.types import BirthInput
from src.engine.traditions.lilly_report import (
    HORARY_ONLY,
    build_report,
)
from src.engine.traditions.report_lint import lint

BIRTH = BirthInput(
    name="Fixture", civil_date=date(1996, 8, 13), civil_time="07:18",
    utc_offset_hours=-7.0, latitude=38.2494, longitude=-122.0400,
    place_label="Fairfield, California",
)


@pytest.fixture(scope="module")
def report():
    return build_report(BIRTH)


def test_the_report_builds_clean(report):
    assert not lint(report)
    assert report.delineation_count >= 15


def test_the_horary_apparatus_is_named_and_not_applied(report):
    """A consideration before judgment has nothing to say about a birth."""
    boundary = next(
        s for s in report.sections if "That This Is Not" in s.title
    )
    blob = " ".join(boundary.notes)
    assert "HORARY" in blob
    assert "not run over this nativity" in blob or "NOT run over" in blob
    # And none of those rules is quoted as though it applied.
    quoted = {d.rule_id for s in report.sections for d in s.delineations}
    for rule_id in HORARY_ONLY:
        assert rule_id not in quoted, rule_id


def test_the_conditions_that_do_apply_are_quoted(report):
    """Combustion and cazimi hold in any figure, so they belong here."""
    quoted = {d.rule_id for s in report.sections for d in s.delineations}
    assert "lilly.ca1.combustion" in quoted
    assert "lilly.ca1.cazimi" in quoted


def test_every_planet_gets_a_dignity_score_with_its_reasons(report):
    dignity = next(
        s for s in report.sections if "Essential Dignity" in s.title
    )
    scored = [n for n in dignity.notes if n.startswith("- **")]
    assert len(scored) == 7
    # A score with no stated reason is a number the reader cannot check.
    assert all("(" in n for n in scored)


def test_the_scores_are_cross_checked_against_a_third_party(report):
    dignity = next(
        s for s in report.sections if "Essential Dignity" in s.title
    )
    blob = " ".join(dignity.notes)
    assert "Cross-checked against" in blob
    # And where the two disagree the reason is given, not just the count.
    if "diverge" in blob:
        assert "reason" in blob


def test_nothing_here_carries_a_translation_caveat(report):
    """Lilly wrote in English; an unreviewed-rendering note would be false."""
    blob = " ".join(
        n for s in report.sections for n in (s.notes + s.refusals)
    )
    assert "engine_translation_unreviewed" not in blob
    assert "unreviewed" in blob  # it says WHY it carries none


def test_the_report_says_book_three_is_missing(report):
    """The apparatus without the judgment layer is not a reading of a person."""
    limits = next(s for s in report.sections if "Does Not Claim" in s.title)
    blob = " ".join(limits.notes)
    assert "Book 3" in blob


def test_lilly_uses_quadrant_houses_not_whole_sign(report):
    figure = next(s for s in report.sections if s.title == "The Figure")
    blob = " ".join(figure.notes)
    assert "Regiomontanus" in blob
    assert "not whole sign" in blob
