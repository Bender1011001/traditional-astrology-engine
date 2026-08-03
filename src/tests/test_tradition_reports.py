"""Regression tests for the per-tradition report engines.

These exist because each guarded failure actually happened:

- "short-lived"/"long-lived" reached the rendered Vedic report through ordinary
  placement aphorisms, despite a declared longevity refusal (rule-category
  suppression alone cannot catch semantic content).
- The same source quotation was rendered under both the graha section and the
  bhava section, making one witness look like two.
- The al-Qabisi hyleg settlement treated the uncomputed prenatal syzygy as a
  FAILED candidate and declared the Ascendant settled - unknown collapsed into
  false.
"""

from __future__ import annotations

import re
from collections import Counter
from datetime import date

import pytest

from src.engine.multitradition import build_panel
from src.engine.multitradition.types import BirthInput
from src.engine.traditions.bazi_report import build_report as build_bazi
from src.engine.traditions.report import (
    Delineation,
    redact_refused_topics,
    render_markdown,
)
from src.engine.traditions.vedic_report import build_report as build_vedic

BIRTH = BirthInput(
    name="Fixture", civil_date=date(1996, 8, 13), civil_time="07:18",
    utc_offset_hours=-7.0, latitude=38.2494, longitude=-122.0400,
    place_label="Fairfield, California",
)

LIFESPAN_LEAK = re.compile(
    r"\b(short-?lived|long-?lived|span of life|long lease of life"
    r"|medium life|longevity)\b",
    re.IGNORECASE,
)


@pytest.fixture(scope="module")
def vedic():
    return build_vedic(BIRTH)


@pytest.fixture(scope="module")
def bazi():
    return build_bazi(BIRTH)


# --- clause-level policy -----------------------------------------------------


def test_redaction_removes_only_the_offending_clause():
    text, topics = redact_refused_topics(
        "long-lived; speaks sweetly and clearly; sharp-witted"
    )
    assert topics == ["longevity"]
    assert "long-lived" not in text
    assert "speaks sweetly and clearly" in text
    assert "withheld per publication policy" in text


def test_clean_text_is_untouched():
    original = "learned, witty in speech, happy and possessed of friends"
    text, topics = redact_refused_topics(original)
    assert text == original and topics == []


def test_delineation_cannot_carry_a_refused_clause_on_any_path():
    d = Delineation(
        text="short-lived; brave and wealthy", rule_id="x", source="s",
        evidence_grade="B", trigger="t",
    )
    assert "short-lived" not in d.text
    assert d.topics_redacted == ("longevity",)
    # the serialized form is the same object - no unredacted escape hatch
    assert "short-lived" not in str(d.to_dict())


@pytest.mark.parametrize("engine", ["vedic", "bazi"])
def test_no_lifespan_claim_reaches_a_rendered_report(engine, vedic, bazi):
    """Claims are what leak - quoted delineations and prose notes.

    Section headings name what a house is ABOUT (Bhava 8 is literally the
    longevity house), and suppression notices quote the policy that did the
    withholding; both legitimately contain topic words and are excluded.
    """
    report = vedic if engine == "vedic" else bazi
    for line in render_markdown(report).splitlines():
        stripped = line.strip()
        if (
            stripped.startswith("#")                      # headings: topic labels
            or stripped.startswith("**Not stated here.**")  # suppression notices
            or "withheld" in stripped                     # redaction markers
        ):
            continue
        m = LIFESPAN_LEAK.search(stripped)
        assert not m, f"lifespan claim leaked: {m.group(0)!r} in {stripped[:90]!r}"


def test_redactions_actually_occurred_in_the_vedic_report(vedic):
    """If the sources ever stop tripping the policy, this test forces a look:
    either the extraction changed or the lexicon silently broke."""
    redacted = [
        d for s in vedic.sections for d in s.delineations if d.topics_redacted
    ]
    assert redacted, "expected at least one policy redaction in this chart"


# --- deduplication -----------------------------------------------------------


def test_no_source_quotation_is_rendered_twice(vedic):
    quotes = [
        d.text for s in vedic.sections for d in s.delineations
        if len(d.text) > 30
    ]
    dupes = {q for q, n in Counter(quotes).items() if n > 1}
    assert not dupes, f"duplicated evidence: {sorted(dupes)[:2]}"


def test_bhava_sections_reference_rather_than_requote(vedic):
    for section in vedic.sections:
        if not section.title.startswith("Bhāva"):
            continue
        for d in section.delineations:
            # only the lord-in-bhava doctrine may quote here; occupant results
            # live in the graha sections
            assert "bhavesa_in_bhava" in d.rule_id, d.rule_id


# --- unknown never collapses into false --------------------------------------


@pytest.fixture(scope="module")
def qabisi_facts():
    panel = build_panel(BIRTH)
    section = next(
        s for s in panel["sections"]
        if s["tradition_id"] == "islamicate_al_qabisi"
    )
    return section["facts"]


def test_hyleg_settlement_is_tri_valued(qabisi_facts):
    settled = qabisi_facts["hyleg_settled"]
    assert settled["status"] in {"settled", "conditional"}
    ledger = qabisi_facts["hyleg_candidate_ledger"]
    uncomputed = [
        e["candidate"] for e in ledger if e.get("longitude") is None
    ]
    if uncomputed:
        # an uncomputed candidate earlier in the order forbids "settled"
        assert settled["status"] == "conditional"
        assert set(settled["conditional_on"]) == set(uncomputed)
        assert "unknown" in settled["chosen_because"].lower() or \
            "not computed" in settled["chosen_because"].lower()


def test_settle_hyleg_unit_unknown_vs_failed():
    from src.engine.multitradition.islamicate import settle_hyleg

    # earlier candidate uncomputed -> conditional even though a later one passes
    conditional = settle_hyleg([
        {"candidate": "Sun", "longitude": 10.0, "eligible": False},
        {"candidate": "Prenatal syzygy", "longitude": None},
        {"candidate": "Ascendant", "longitude": 150.0, "eligible": True,
         "lords_that_behold_it": {"Mercury": "conjunction"}},
    ])
    assert conditional["status"] == "conditional"
    assert conditional["conditional_on"] == ["Prenatal syzygy"]

    # every earlier candidate computed-and-failed -> genuinely settled
    settled = settle_hyleg([
        {"candidate": "Sun", "longitude": 10.0, "eligible": False},
        {"candidate": "Moon", "longitude": 40.0, "eligible": False},
        {"candidate": "Ascendant", "longitude": 150.0, "eligible": True,
         "lords_that_behold_it": {}},
    ])
    assert settled["status"] == "settled"
    assert "conditional_on" not in settled


# --- presentation ------------------------------------------------------------


def test_no_raw_json_in_rendered_prose(vedic, bazi):
    for report in (vedic, bazi):
        for section in report.sections:
            for note in section.notes:
                assert not re.search(r'\{"[a-z_]+":', note), (
                    f"raw JSON leaked into prose: {note[:80]}"
                )


def test_bazi_title_does_not_overclaim(bazi):
    assert "Full Reading" not in bazi.display_name
