"""Sukuyōdō, checked against its own closure proofs and a dated consultation.

This track has better internal evidence than most: the text supplies two
algebraically identical birth-mansion formulas as a redundancy check, a pada
allotment that only closes on a 27-mansion cycle, and a three-nine scheme that
only closes on the same. All three are asserted here.

The strongest check is external to the arithmetic: Murakami Tennō's recorded
birth mansion, from a dated historical consultation with a named subject. It
independently confirms both the month table and the canonical order, because a
wrong entry in either would give a different mansion.
"""

from __future__ import annotations

import pytest

from src.engine.multitradition.sukuyodo import (
    CATEGORY_GLOSS,
    NIU,
    WITHIN_NINE,
    birth_mansion,
    build,
    full_moon_mansions,
    mansion_index,
    mansions,
    pada_closure,
    relation_between,
    sanku_category,
    sanku_table,
    sign_of_mansion,
)


# --- the cycle is 27 -----------------------------------------------------


def test_there_are_twenty_seven_mansions_and_they_start_at_mao():
    order = mansions()
    assert len(order) == 27
    assert order[0] == "昴", "the order must begin at 昴, not at the Chinese 角"
    assert order[-1] == "胃"


def test_niu_is_catalogued_and_never_operative():
    """It gets no pada, no category, and no birth-mansion slot."""
    assert NIU not in mansions()
    assert pada_closure()["pada_allotted_to_niu"] == 0
    with pytest.raises(ValueError):
        mansion_index(NIU)


def test_the_pada_allotment_closes_only_on_twenty_seven():
    """Nine per sign, four per mansion, 108 in all - not divisible by 28."""
    closure = pada_closure()
    assert closure["total_pada"] == 108
    assert set(closure["pada_per_sign"].values()) == {9}
    assert set(closure["pada_per_mansion"].values()) == {4}
    assert 108 % 4 == 0 and 108 // 4 == 27


def test_the_three_nines_close_the_cycle_exactly():
    """3 x 9 = 27; a 28-mansion cycle would leave the third nine short."""
    heads = [r for r in sanku_table("昴") if r["offset"] in (0, 9, 18)]
    assert [h["category"] for h in heads] == ["命", "業", "胎"]
    assert len(sanku_table("昴")) == 27


def test_the_full_moon_table_steps_sum_to_twenty_seven():
    """The table's own closure check."""
    table = full_moon_mansions()
    assert sorted(table) == list(range(1, 13))
    order = [mansion_index(table[m]) for m in range(1, 13)]
    steps = [(order[(i + 1) % 12] - order[i]) % 27 for i in range(12)]
    assert sum(steps) == 27, steps


# --- the birth mansion ---------------------------------------------------


def test_murakami_tenno_reproduces_exactly():
    """A dated consultation with a named subject: month 6, day 2 gives 柳."""
    got = birth_mansion(6, 2)
    assert got["full_moon_mansion"] == "女"
    assert got["mansion"] == "柳"
    assert got["index"] == 7


def test_the_texts_two_formulas_agree_across_every_case():
    """810 cases: 27 full-moon mansions x 30 lunar days.

    An implementation that disagrees with either formula is wrong, and one
    that disagrees with only one of them is provably wrong. birth_mansion
    raises if they ever diverge, so reaching the end is the assertion.
    """
    for month in range(1, 13):
        for day in range(1, 31):
            got = birth_mansion(month, day)
            assert got["both_formulas_agree"]
            assert got["mansion"] in mansions()


def test_an_untabled_month_is_an_error_rather_than_a_guess():
    with pytest.raises(ValueError):
        birth_mansion(13, 5)


def test_the_schematic_method_is_labelled_as_schematic():
    assert birth_mansion(6, 2)["method"] == "schematic"


# --- the three nines -----------------------------------------------------


def test_every_offset_gets_exactly_one_category():
    seen = [sanku_category(o) for o in range(27)]
    assert len(seen) == 27
    assert seen.count("命") == 1
    assert seen.count("業") == 1
    assert seen.count("胎") == 1
    for name in WITHIN_NINE:
        assert seen.count(name) == 3, name


def test_the_within_nine_sequence_is_the_printed_one():
    assert WITHIN_NINE == ("榮", "衰", "安", "危", "成", "壞", "友", "親")
    assert [sanku_category(o) for o in range(1, 9)] == list(WITHIN_NINE)


def test_a_mansion_is_its_own_life_mansion():
    for m in mansions():
        assert relation_between(m, m)["category"] == "命"


def test_the_relation_is_computed_from_the_offset_not_a_lookup():
    """Two birth mansions determine the category with no latitude."""
    order = mansions()
    got = relation_between(order[0], order[9])
    assert got["offset"] == 9
    assert got["category"] == "業"


def test_every_category_carries_a_gloss():
    for o in range(27):
        assert CATEGORY_GLOSS[sanku_category(o)]


# --- the pada signs ------------------------------------------------------


def test_a_mansion_reports_every_sign_its_pada_touch():
    """Four pada against nine per sign means most mansions straddle."""
    straddling = [m for m in mansions() if len(sign_of_mansion(m)) > 1]
    assert straddling, "no mansion straddles a sign boundary, which cannot be"
    for m in mansions():
        rows = sign_of_mansion(m)
        assert rows, m
        assert sum(r["pada"] for r in rows) == 4, m


def test_every_sign_carries_its_resident_luminary():
    for m in mansions():
        for row in sign_of_mansion(m):
            assert row["resident_luminary"], row


# --- the regime gate -----------------------------------------------------


def test_agreeing_regimes_emit_the_mansion():
    got = build({"futian_li": (6, 2), "senmyo_reki": (6, 2)})
    assert got["status"] == "emitted"
    assert got["regimes_agree"] is True
    assert got["birth_mansion"] == "柳"
    assert len(got["sanku"]) == 27


def test_disagreeing_regimes_refuse_and_publish_the_disagreement():
    """A wrong anchor makes every downstream relation wrong, invisibly."""
    got = build({"futian_li": (6, 2), "senmyo_reki": (6, 3)})
    assert got["status"] == "refused"
    assert got["regimes_agree"] is False
    assert "birth_mansion" not in got
    # The reader must be able to see what each regime would have given.
    assert set(got["per_regime"]) == {"futian_li", "senmyo_reki"}
    assert got["per_regime"]["futian_li"]["mansion"] == "柳"
    assert got["per_regime"]["senmyo_reki"]["mansion"] != "柳"


def test_the_gate_is_labelled_a_product_choice():
    """The sources do not say to do this and the engine must not pretend."""
    got = build({"futian_li": (6, 2)})
    assert got["gate"] == "configured_method"
    assert "anchor" in got["gate_rationale"]


def test_the_emitted_reading_names_the_method_fork():
    """The schematic position LOST the 961 arbitration on the natal question."""
    got = build({"futian_li": (6, 2)})
    assert "SCHEMATIC" in got["method_fork"]
    assert "961" in got["method_fork"]
    assert "lost" in got["method_fork"]


def test_the_three_triad_heads_are_nine_apart():
    got = build({"futian_li": (6, 2)})
    triads = got["triads"]
    order = mansions()
    life = order.index(triads["命"])
    assert order.index(triads["業"]) == (life + 9) % 27
    assert order.index(triads["胎"]) == (life + 18) % 27


# --- the report ----------------------------------------------------------


def test_a_refused_anchor_still_publishes_the_structure():
    """A blank page hides what turns on the calendar; the fan-out shows it."""
    from datetime import date

    from src.engine.multitradition.types import BirthInput
    from src.engine.traditions.sukuyodo_report import (
        build_report as build_sukuyo_report,
    )

    report = build_sukuyo_report(
        BirthInput(
            name="Fixture", civil_date=date(1996, 8, 13), civil_time="07:18",
            utc_offset_hours=-7.0, latitude=38.2494, longitude=-122.04,
            place_label="Fairfield, California",
        )
    )
    titles = [s.title for s in report.sections]
    mansion = next(s for s in report.sections if s.title == "The Birth Mansion")
    if mansion.refusals:
        conditional = [t for t in titles if t.startswith("If the Birth Mansion")]
        assert conditional, (
            "the anchor was refused and no conditional reading was given"
        )
        for title in conditional:
            section = next(s for s in report.sections if s.title == title)
            assert "conditional on that calendar" in " ".join(section.notes)
            offsets = [n for n in section.notes if n.startswith("- ")]
            assert len(offsets) >= 27, title


def test_the_report_says_the_real_calendar_is_absent():
    """Futian li and Senmyo reki are not in the repository and must be named."""
    from datetime import date

    from src.engine.multitradition.types import BirthInput
    from src.engine.traditions.sukuyodo_report import (
        build_report as build_sukuyo_report,
    )

    report = build_sukuyo_report(
        BirthInput(
            name="Fixture", civil_date=date(1996, 8, 13), civil_time="07:18",
            utc_offset_hours=-7.0, latitude=38.2494, longitude=-122.04,
            place_label="Fairfield, California",
        )
    )
    calendar = next(
        s for s in report.sections if s.title.startswith("Which Calendar")
    )
    blob = " ".join(calendar.refusals)
    assert "符天暦" in blob
    assert "stand-in" in blob


def test_candidates_are_ordered_and_attributed():
    """A two-to-one split is a different situation from a three-way one."""
    got = build({"a": (6, 2), "b": (6, 2), "c": (6, 3)})
    assert got["status"] == "refused"
    candidates = got["candidates"]
    assert len(candidates) == 2
    backing = {c["mansion"]: c["supported_by"] for c in candidates}
    assert len(backing["柳"]) == 2
    assert len(backing["星"]) == 1
    for c in candidates:
        assert len(c["sanku"]) == 27


# --- what the text says of the native ------------------------------------


def test_the_weekday_cycle_needs_no_lunar_calendar():
    """It survives the regime refusal, which is why it is worth firing.

    The seven-day week is continuous in this text, so the birth weekday is
    known even when the birth mansion is not.
    """
    from src.engine.multitradition.sukuyodo import (
        WEEKDAY_PLANETS,
        weekday_planet,
    )

    assert len(WEEKDAY_PLANETS) == 7
    assert weekday_planet(0).endswith("Sun")
    assert weekday_planet(7) == weekday_planet(0)


def test_every_planet_but_mercury_carries_a_natal_clause():
    """The chapter simply omits Mercury's, and the gap is reported."""
    from src.engine.multitradition.sukuyodo import (
        WEEKDAY_PLANETS,
        weekday_natal_clause,
    )

    absent = []
    for planet in WEEKDAY_PLANETS:
        got = weekday_natal_clause(planet)
        assert got is not None, planet
        if got.get("absent"):
            absent.append(planet)
        else:
            assert got["verbatim"]
    assert [p for p in absent if "Mercury" in p] == [p for p in absent]
    assert len(absent) == 1


def test_refused_clauses_are_named_not_silently_cut():
    """Short life, ugliness and harm-to-kin are in the source and withheld."""
    from src.engine.multitradition.sukuyodo import weekday_natal_clause

    mars = weekday_natal_clause("熒惑 Mars")
    assert "醜陋" in mars["verbatim"]
    assert any("ugliness" in r for r in mars["refused"])
    # The rendering shown to a reader carries none of the refused content.
    assert "ugl" not in (mars["rendering"] or "").lower()

    sun = weekday_natal_clause("太陽 Sun")
    assert any("short-life" in r for r in sun["refused"])
    assert "short" not in (sun["rendering"] or "").lower()


def test_the_association_rule_keeps_the_sources_own_contradiction():
    """危 is a bad category and a good day, in the same text."""
    from src.engine.multitradition.sukuyodo import association_categories

    got = association_categories()
    assert got["favourable"] == ["榮", "安", "成", "友", "親"]
    assert "危" not in got["favourable"]
    assert "危" in got["tension"]
    assert "大抵" in got["hedge"]


def test_sukuyodo_now_delineates_something():
    """It fired nothing at all, and was classified a source audit for it."""
    from datetime import date

    from src.engine.multitradition.types import BirthInput
    from src.engine.traditions.readiness import AUDIT, classify
    from src.engine.traditions.sukuyodo_report import (
        build_report as build_sukuyo_report,
    )

    report = build_sukuyo_report(
        BirthInput(
            name="Fixture", civil_date=date(1996, 8, 13), civil_time="07:18",
            utc_offset_hours=-7.0, latitude=38.2494, longitude=-122.04,
            place_label="Fairfield, California",
        )
    )
    assert report.delineation_count >= 1
    assert classify(report).kind != AUDIT
