"""Valens' condition vocabulary must resolve honestly, or not at all.

The point of these tests is the third value. An engine that answers False when
it means "I cannot tell" will quietly assert the opposite of what Valens says,
and the failure is invisible in the output: the rule simply never fires and the
report looks merely quiet rather than wrong.
"""

from __future__ import annotations

from datetime import date

import pytest

from src.engine.multitradition.types import BirthInput
from src.engine.traditions.hellenistic_report import build_report
from src.engine.traditions.valens_facts import (
    UNKNOWN_VALUE,
    ValensChart,
    _Unknown,
    evaluate,
    resolve,
)

BIRTH = BirthInput(
    name="Test",
    civil_date=date(1996, 8, 13),
    civil_time="07:18",
    utc_offset_hours=-7.0,
    latitude=38.2494,
    longitude=-122.04,
    place_label="Fairfield",
    sex="male",
)


def _chart() -> ValensChart:
    from src.engine.traditions.hellenistic_report import _facts

    return ValensChart(_facts(BIRTH))


def test_unknown_refuses_to_be_a_boolean():
    """An undecided fact must not slip through an ``if value:`` test."""
    with pytest.raises(TypeError):
        bool(UNKNOWN_VALUE)


def test_unresolvable_fact_returns_unknown_not_false():
    chart = _chart()
    # Valens' distributions are not computed by this engine.
    got = resolve("distribution", chart)
    assert isinstance(got, _Unknown)
    assert got is not False


def test_all_group_with_an_unknown_member_never_passes():
    rule = {
        "conditions": {
            "all": [
                {"fact": "sect", "operator": "equals", "value": "day"},
                {"fact": "distribution", "operator": "equals", "value": "x"},
            ]
        }
    }
    verdict, undecided = evaluate(rule, _chart())
    assert verdict == "unknown"
    assert "distribution" in undecided


def test_all_group_fails_outright_when_the_chart_denies_a_member():
    """A settled False decides the group even beside an unknown."""
    rule = {
        "conditions": {
            "all": [
                {"fact": "sect", "operator": "equals", "value": "night"},
                {"fact": "distribution", "operator": "equals", "value": "x"},
            ]
        }
    }
    verdict, _ = evaluate(rule, _chart())
    assert verdict == "fail"


def test_any_group_passes_on_one_settled_true():
    rule = {
        "conditions": {
            "any": [
                {"fact": "sect", "operator": "equals", "value": "day"},
                {"fact": "distribution", "operator": "equals", "value": "x"},
            ]
        }
    }
    assert evaluate(rule, _chart())[0] == "pass"


def test_overcoming_is_directional():
    """Epidekateia is not a folded distance: A overcomes B, or B overcomes A."""
    chart = _chart()
    pairs = [
        (a, b)
        for a in chart.by_body
        for b in chart.by_body
        if a != b and chart.overcomes(a, b) is True
    ]
    for a, b in pairs:
        assert chart.overcomes(b, a) is False, (
            f"{a} overcomes {b} and {b} overcomes {a}; the figure has lost "
            "its direction"
        )


def test_lot_of_travel_follows_valens_own_formula():
    """II.29: counted from Saturn to Mars, the same amount from the Ascendant."""
    chart = _chart()
    lot = chart.lot_of_travel()
    assert not isinstance(lot, _Unknown)

    from src.engine.traditions.valens_facts import SIGNS

    asc = chart.facts["ascendant"]
    asc_lon = SIGNS.index(asc["sign"]) * 30.0 + asc["degree_in_sign"]
    expected = (
        asc_lon + (chart.longitude("Mars") - chart.longitude("Saturn"))
    ) % 360.0
    got = SIGNS.index(lot["sign"]) * 30.0 + lot["degree_in_sign"]
    assert abs(got - expected) < 0.01
    # Valens prints no sect reversal for this lot, so none may be applied.
    assert 1 <= lot["whole_sign_house"] <= 12


def test_valens_topics_appear_in_the_report_and_are_quoted():
    report = build_report(BIRTH)
    titles = [s.title for s in report.sections]
    assert "Marriage, after Valens" in titles
    assert "Valens on Method" in titles

    fired = [
        d
        for s in report.sections
        for d in s.delineations
        if "valens" in d.rule_id
    ]
    assert fired, "the Valens pack loads but nothing fires"
    for d in fired:
        assert d.text.strip(), f"{d.rule_id} fired with empty text"
        assert d.source, f"{d.rule_id} fired without a source label"


def test_undecided_conditions_are_reported_not_hidden():
    """A chapter Valens gates on chronocrators must say so out loud."""
    report = build_report(BIRTH)
    travel = next(
        (s for s in report.sections if s.title.startswith("Foreign Travel")),
        None,
    )
    assert travel is not None
    blob = " ".join(travel.notes)
    assert "cannot be decided" in blob
    assert "distribution" in blob


def test_configured_methods_are_disclosed_wherever_they_are_used():
    """Any convention this engine supplies must be labelled where it acts."""
    report = build_report(BIRTH)
    for section in report.sections:
        if not section.title.endswith("after Valens"):
            continue
        chart = ValensChart(
            __import__(
                "src.engine.traditions.hellenistic_report",
                fromlist=["_facts"],
            )._facts(BIRTH)
        )
        if not chart.used_methods:
            continue
        blob = " ".join(section.notes)
        if section.delineations:
            assert "configured_method" in blob, (
                f"{section.title} relies on a supplied convention without "
                "disclosing it"
            )
