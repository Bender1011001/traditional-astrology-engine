"""Tests for the cross-tradition convergence layer.

The failure mode this layer must never have: reporting agreement between
sections that share a calculation basis, which would manufacture false
corroboration. These tests lock the independence accounting.
"""

from __future__ import annotations

from datetime import date

import pytest

from src.engine.multitradition import BirthInput, build_panel, render
from src.engine.multitradition import convergence as conv

FAIRFIELD = BirthInput(
    name="Andrew",
    civil_date=date(1996, 8, 13),
    civil_time="07:18",
    utc_offset_hours=-7.0,
    latitude=38.2494,
    longitude=-122.0397,
    place_label="Fairfield, California, United States",
)


@pytest.fixture(scope="module")
def panel() -> dict:
    return build_panel(FAIRFIELD)


@pytest.fixture(scope="module")
def convergence(panel: dict) -> dict:
    return conv.build(panel)


def test_shared_basis_collapses_to_one_voice(convergence: dict) -> None:
    """Western/Islamicate/Jewish share a chart; they must not count as three."""
    assert convergence["independent_voice_count"] < len(
        [t for group in convergence["shared_basis_groups"].values() for t in group]
    )
    hellenistic = convergence["shared_basis_groups"].get("hellenistic_core", [])
    assert "western_traditional" in hellenistic
    assert len(hellenistic) > 1, "shared-basis grouping not detected"


def test_basis_lookup_groups_correctly() -> None:
    assert conv._basis_of("western_traditional") == "hellenistic_core"
    assert conv._basis_of("islamicate_persian") == "hellenistic_core"
    assert conv._basis_of("medieval_jewish") == "hellenistic_core"
    assert conv._basis_of("chinese_bazi") == "sexagenary_core"
    assert conv._basis_of("maya") == "mesoamerican_count"
    # An unknown tradition stands alone.
    assert conv._basis_of("indian_jyotisha") == "indian_jyotisha"


def test_voices_counts_bases_not_sections() -> None:
    same_basis = ["western_traditional", "islamicate_persian", "medieval_jewish"]
    assert conv._voices(same_basis) == 1
    mixed = ["western_traditional", "chinese_bazi", "maya"]
    assert conv._voices(mixed) == 3


def test_no_agreement_claims_more_voices_than_exist(convergence: dict) -> None:
    total = convergence["independent_voice_count"]
    for item in convergence["agreements"]:
        assert item["independent_voices"] <= total
        assert item["independent_voices"] == conv._voices(item["supporting_traditions"])


def test_method_note_states_the_independence_rule(convergence: dict) -> None:
    note = convergence["method_note"].lower()
    assert "share no mathematics" in note
    assert "one independent voice" in note
    # The Western/Vedic house-number identity must be called out explicitly.
    assert "whole-sign house numbers coincide" in note


def test_distinctions_are_reported_not_only_agreements(convergence: dict) -> None:
    """A convergence page that only lists agreements is a horoscope."""
    assert "distinctions" in convergence
    assert isinstance(convergence["distinctions"], list)


def test_sect_polarity_is_flagged_as_non_equivalent(convergence: dict) -> None:
    topics = [d["topic"] for d in convergence["distinctions"]]
    if "Day/night and polarity" in topics:
        item = next(
            d for d in convergence["distinctions"]
            if d["topic"] == "Day/night and polarity"
        )
        assert "NOT" in item["statement"] or "not" in item["statement"]
        assert "equivalen" in item["statement"].lower()


def test_convergence_invents_no_new_claims(panel: dict, convergence: dict) -> None:
    """Every supporting tradition must be a section that actually built."""
    built = {s["tradition_id"] for s in panel["sections"] if not s.get("error")}
    for bucket in ("agreements", "distinctions"):
        for item in convergence[bucket]:
            for tradition in item["supporting_traditions"]:
                assert tradition in built, f"{tradition} cited but did not build"


def test_render_includes_convergence_when_present(panel: dict, convergence: dict) -> None:
    enriched = dict(panel)
    enriched["convergence"] = convergence
    text = render(enriched)
    assert "## Across traditions" in text
    assert "Independent voices:" in text
    assert "share one calculation basis" in text
