"""The report-surface and polarity failures an external review found by reading.

Every test here corresponds to a defect that shipped in the 2026-08-05 reports
and that no existing test could see. They all had the same shape: the report
built, the section rendered, the sentence parsed, and the content was wrong or
was a debugger token.

The polarity cases are quoted from the review directly. They are the bar the
classifier has to clear, and two of them - "no sorrow" and "little scorched by
grief" - were being classified as unfavourable because the classifier counted
words and could not see negation.
"""

from __future__ import annotations

from datetime import date

import pytest

from src.engine.multitradition.types import BirthInput
from src.engine.traditions import REPORT_ENGINES, build_tradition_report
from src.engine.traditions.report_lint import lint
from src.engine.traditions.synthesis import author_of, clause_polarity

BIRTH = BirthInput(
    name="Fixture", civil_date=date(1996, 8, 13), civil_time="07:18",
    utc_offset_hours=-7.0, latitude=38.2494, longitude=-122.0400,
    place_label="Fairfield, California",
)


@pytest.fixture(scope="module")
def reports():
    return {t: build_tradition_report(t, BIRTH) for t in sorted(REPORT_ENGINES)}


# --- surface: nothing from a debugger reaches a reader -----------------------


@pytest.mark.parametrize("tradition_id", sorted(REPORT_ENGINES))
def test_no_report_leaks_implementation_detail(tradition_id, reports):
    findings = lint(reports[tradition_id])
    assert not findings, "\n  ".join(str(f) for f in findings)


def test_the_linter_would_catch_the_defects_that_shipped():
    """A linter that passes because it checks nothing is worse than none."""
    from src.engine.traditions.report import ReportSection, TraditionReport

    bad = TraditionReport(
        tradition_id="hellenistic", display_name="x", birth={},
    )
    s = bad.add(ReportSection("T", level=2))
    s.notes.extend([
        "The quadrant Midheaven falls at None 0.00 degrees.",
        "Adjudication uses precedence the sources state (Saravali 23.86).",
        "- Prenatal syzygy: place None, not eligible by place; aspect gate failed.",
        "see src/engine/multitradition/bazi.py for the disclosure",
        "Forms on the reading: False",
        "the cell core_nature_verses is untranslated",
    ])
    rules = {f.rule for f in lint(bad)}
    assert "null-quantity" in rules
    assert "foreign-source" in rules
    assert "uncertainty-collapse" in rules
    assert "implementation-leak" in rules


# --- polarity: the review's own cases ----------------------------------------


@pytest.mark.parametrize(
    "clause,expected",
    [
        # Negation. Counting words made these unfavourable.
        ("no sorrow", "favourable"),
        (
            "Attended by handsome servants, of much nobility, and but little "
            "scorched by grief.",
            "favourable",
        ),
        ("free from disease", "favourable"),
        # Mitigation is its own state, not a flat negative.
        (
            "even if she is afflicted, she is helped so that not everything "
            "is overthrown",
            "mitigating",
        ),
        # Procedure is not testimony about anybody.
        (
            "The topic concerning marriage is taken naturally from the "
            "seventh sign",
            "procedural",
        ),
        ("I return to the Lot of Fortune", "procedural"),
        # And the plain cases still work.
        ("poor and disliked by women", "unfavourable"),
        ("wealthy and learned", "favourable"),
    ],
)
def test_polarity_matches_ordinary_reading(clause, expected):
    assert clause_polarity(clause) == expected


def test_a_negated_misfortune_is_not_a_misfortune():
    """The general rule behind the specific cases above."""
    for bad in ("sorrow", "poverty", "disease", "grief"):
        assert clause_polarity(f"no {bad}") != "unfavourable", bad
        assert clause_polarity(f"free from {bad}") != "unfavourable", bad


# --- identity: a rule-id prefix is not a person ------------------------------


def test_an_unmapped_rule_never_becomes_an_author_name():
    """A report said "Single-witness testimony from hel"."""
    assert author_of("hel.something.unmapped") != "hel"
    assert author_of("zzz.unknown.rule") != "zzz"


def test_known_prefixes_resolve_to_named_authors():
    assert "Valens" in author_of("hel.valens.b2.marriage.x")
    assert "Firmicus" in author_of("hel.firmicus.x")
    assert "Kalyāṇavarma" in author_of("jyotisha.saravali.x")


# --- the topic index does not claim to be a judgment -------------------------


def test_the_topic_section_is_labelled_an_index_not_a_synthesis(reports):
    """Whole composite sentences are still filed under every matching topic.

    Until they are split into atomic propositions, no verdict downstream of
    that routing can be trusted, so none is issued.
    """
    for tradition_id in ("hellenistic", "indian_jyotisha"):
        report = reports[tradition_id]
        section = next(
            (s for s in report.sections if "Topic Index" in s.title), None
        )
        if section is None:
            continue
        blob = " ".join(section.notes)
        assert "index, not a judgment" in blob
        assert "CONTRADICTION" not in blob
        assert "Corroborated" not in blob


def test_procedural_clauses_never_enter_the_topic_index(reports):
    """A marriage chapter's opening line was once the whole Character topic."""
    for report in reports.values():
        section = next(
            (s for s in report.sections if "Topic Index" in s.title), None
        )
        if section is None:
            continue
        for note in section.notes:
            assert "is taken naturally from" not in note
            assert "I return to the Lot" not in note


def test_a_foreign_tradition_is_not_cited_as_this_one_s_method(reports):
    """A Hellenistic report cited Sāravalī's precedence rules as its own."""
    hellenistic = reports["hellenistic"]
    blob = " ".join(
        n for s in hellenistic.sections for n in (s.notes + s.refusals)
    )
    assert "Saravali" not in blob
    assert "Sāravalī" not in blob
