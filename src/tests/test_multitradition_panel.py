"""Tests for the multi-tradition panel.

These lock the properties that make the panel defendable: every section carries
disclosures, refusals are actually enforced, the known-good Fairfield values are
reproduced, and a broken section cannot take down the panel.
"""

from __future__ import annotations

from datetime import date

import pytest

from src.engine.multitradition import BirthInput, build_panel, render
from src.engine.multitradition.tibetan import year_character
from src.engine.multitradition.types import DisclosureKind

FAIRFIELD = BirthInput(
    name="Andrew",
    civil_date=date(1996, 8, 13),
    civil_time="07:18",
    utc_offset_hours=-7.0,
    latitude=38.2494,
    longitude=-122.0397,
    place_label="Fairfield, California, United States",
)
SYDNEY = BirthInput(
    name="Fixture: Sydney",
    civil_date=date(1978, 11, 3),
    civil_time="22:40",
    utc_offset_hours=11.0,
    latitude=-33.8688,
    longitude=151.2093,
    place_label="Sydney, New South Wales, Australia",
)
PARIS_1931 = BirthInput(
    name="Fixture: Paris 1931",
    civil_date=date(1931, 2, 3),
    civil_time="04:05",
    utc_offset_hours=0.0,
    latitude=48.8566,
    longitude=2.3522,
    place_label="Paris, France",
)
QUITO_LATE_ZI = BirthInput(
    name="Fixture: Quito late-Zi",
    civil_date=date(2004, 6, 21),
    civil_time="23:20",
    utc_offset_hours=-5.0,
    latitude=-0.1807,
    longitude=-78.4678,
    place_label="Quito, Ecuador",
)

ALL_FIXTURES = [FAIRFIELD, SYDNEY, PARIS_1931, QUITO_LATE_ZI]


@pytest.fixture(scope="module")
def fairfield_panel() -> dict:
    return build_panel(FAIRFIELD)


def _section(panel: dict, tradition_id: str) -> dict:
    return next(s for s in panel["sections"] if s["tradition_id"] == tradition_id)


@pytest.mark.parametrize("birth", ALL_FIXTURES, ids=lambda b: b.name)
def test_every_fixture_builds_every_section(birth: BirthInput) -> None:
    panel = build_panel(birth)
    failures = {s["tradition_id"]: s["error"] for s in panel["sections"] if s.get("error")}
    assert not failures, f"sections failed: {failures}"
    assert len(panel["sections"]) == 8


@pytest.mark.parametrize("birth", ALL_FIXTURES, ids=lambda b: b.name)
def test_every_section_discloses_something(birth: BirthInput) -> None:
    """A section with no disclosures is a section hiding its conventions."""
    panel = build_panel(birth)
    for section in panel["sections"]:
        assert section["disclosures"], f"{section['tradition_id']} discloses nothing"


@pytest.mark.parametrize("birth", ALL_FIXTURES, ids=lambda b: b.name)
def test_panel_is_not_customer_eligible(birth: BirthInput) -> None:
    panel = build_panel(birth)
    assert panel["customer_eligible"] is False
    assert panel["historical_use_only"] is True


def test_western_matches_known_values(fairfield_panel: dict) -> None:
    facts = _section(fairfield_panel, "western_traditional")["facts"]
    assert facts["ascendant"]["sign"] == "Virgo"
    assert facts["ascendant"]["degree_in_sign"] == pytest.approx(1.5017, abs=0.01)
    assert facts["sect"] == "day"
    sun = next(p for p in facts["placements"] if p["body"] == "Sun")
    assert sun["sign"] == "Leo"
    assert sun["whole_sign_house"] == 12


def test_vedic_matches_known_values(fairfield_panel: dict) -> None:
    facts = _section(fairfield_panel, "indian_jyotisha")["facts"]
    assert facts["ayanamsa_degrees"] == pytest.approx(23.8098, abs=0.001)
    assert facts["lagna"]["rasi"] == "Leo"
    assert facts["lagna"]["nakshatra"] == "Magha"
    assert facts["janma_nakshatra"]["name"] == "Ashlesha"
    assert facts["janma_nakshatra"]["lord"] == "Mercury"
    # Vimshottari starts in the balance of the janma-nakshatra lord's period.
    assert facts["vimshottari_mahadashas"][0]["lord"] == "Mercury"
    assert facts["vimshottari_mahadashas"][0]["partial_at_birth"] is True
    jupiter = next(g for g in facts["grahas"] if g["graha"] == "Jupiter")
    assert jupiter["rasi"] == "Sagittarius"
    assert jupiter["dignity"] == "own sign"


def test_navamsha_structural_properties() -> None:
    """D9 must satisfy four properties the classical rule guarantees."""
    from collections import Counter

    from src.engine.multitradition.vedic import (
        NAVAMSHA_ARC,
        SIGNS,
        navamsha_sign,
    )

    # 1. The 108 divisions map onto the 12 signs exactly nine times each.
    counts = Counter(
        navamsha_sign((i + 0.5) * NAVAMSHA_ARC)[0] for i in range(108)
    )
    assert set(counts) == set(SIGNS)
    assert set(counts.values()) == {9}

    # 2. Movable signs begin their navamsha from themselves.
    for sign in ("Aries", "Cancer", "Libra", "Capricorn"):
        assert navamsha_sign(SIGNS.index(sign) * 30 + 0.01)[0] == sign

    # 3. Fixed signs begin from the ninth sign; dual signs from the fifth.
    assert navamsha_sign(30.01)[0] == "Capricorn"  # Taurus -> 9th
    assert navamsha_sign(60.01)[0] == "Libra"  # Gemini -> 5th

    # 4. The cycle closes: the final navamsha of Pisces is Pisces.
    assert navamsha_sign(359.99)[0] == "Pisces"


def test_navamsha_present_for_every_graha(fairfield_panel: dict) -> None:
    facts = _section(fairfield_panel, "indian_jyotisha")["facts"]
    assert "navamsha" in facts["lagna"]
    for graha in facts["grahas"]:
        assert graha["navamsha"] in _sign_names()
        assert 1 <= graha["navamsha_division"] <= 9
        assert isinstance(graha["vargottama"], bool)


def _sign_names() -> list[str]:
    from src.engine.multitradition.vedic import SIGNS

    return SIGNS


def test_bazi_matches_known_pillars(fairfield_panel: dict) -> None:
    facts = _section(fairfield_panel, "chinese_bazi")["facts"]
    assert facts["pillar_year_used"] == 1996
    pillars = facts["pillars"]
    assert pillars["year"]["stem"] == "bing" and pillars["year"]["branch"] == "zi"
    assert pillars["month"]["stem"] == "bing" and pillars["month"]["branch"] == "shen"
    assert pillars["day"]["stem"] == "ren" and pillars["day"]["branch"] == "wu_branch"
    assert facts["day_master"]["element"] == "Water"
    assert facts["day_master"]["polarity"] == "yang"
    assert facts["element_tally"]["Earth"] == 0


def test_bazi_day_anchor_cross_checks() -> None:
    """The day-count anchor must reproduce a second, independent known day."""
    from src.engine.multitradition.bazi import (
        DAY_ANCHOR_INDEX,
        DAY_ANCHOR_JDN,
        _pair,
    )

    # 2000-01-01 is JDN 2451545 and a Wu-Wu day (sexagenary index 54).
    index = (DAY_ANCHOR_INDEX + (2451545 - DAY_ANCHOR_JDN)) % 60
    assert index == 54
    assert _pair(index) == ("wu_stem", "wu_branch")


def test_bazi_emits_all_three_hour_time_bases(fairfield_panel: dict) -> None:
    candidates = _section(fairfield_panel, "chinese_bazi")["facts"][
        "hour_pillar_candidates"
    ]
    assert set(candidates) == {"true_solar_time", "clock_time", "local_mean_time"}
    # Fairfield sits far west of its zone meridian, so the fork is real here.
    assert candidates["true_solar_time"]["branch"] != candidates["clock_time"]["branch"]


def test_bazi_hour_fork_is_disclosed_when_it_changes_the_pillar(
    fairfield_panel: dict,
) -> None:
    section = _section(fairfield_panel, "chinese_bazi")
    forks = [d for d in section["disclosures"] if d["kind"] == DisclosureKind.FORK.value]
    assert any("Hour pillar" in d["subject"] for d in forks)


def test_maya_emits_both_correlations(fairfield_panel: dict) -> None:
    facts = _section(fairfield_panel, "maya")["facts"]
    profiles = facts["correlation_profiles"]
    assert set(profiles) == {"gmt_584283", "gmt_584285"}
    assert profiles["gmt_584283"]["long_count"] == "12.19.3.7.6"
    assert profiles["gmt_584283"]["tzolkin"] == "10 Kimi"
    # The two correlations differ by exactly two days.
    assert (
        profiles["gmt_584283"]["total_day"] - profiles["gmt_584285"]["total_day"] == 2
    )


def test_nahua_refuses_a_correlation(fairfield_panel: dict) -> None:
    section = _section(fairfield_panel, "nahua_central_mexican")
    assert section["facts"]["correlation_status"] == "unresolved_no_approved_epoch"
    refusals = [
        d for d in section["disclosures"] if d["kind"] == DisclosureKind.REFUSAL.value
    ]
    assert any("correlation" in d["subject"].lower() for d in refusals)
    # The fixture position must never be presented as a real day sign.
    assert "fixture" in section["facts"]["fixture_anchor_note"].lower()


def test_tibetan_year_character_anchors() -> None:
    assert year_character(1027) == {
        "element": "Fire",
        "animal": "Rabbit",
        "polarity": "female",
        "sexagenary_index": 3,
    }
    assert year_character(1984)["element"] == "Wood"
    assert year_character(1984)["animal"] == "Mouse"
    assert year_character(1996)["element"] == "Fire"
    assert year_character(1996)["animal"] == "Mouse"


def test_tibetan_refuses_mewa_and_parkha(fairfield_panel: dict) -> None:
    section = _section(fairfield_panel, "tibetan")
    assert "mewa" not in section["facts"]
    assert "parkha_male_line" not in section["facts"]
    refusals = [
        d for d in section["disclosures"] if d["kind"] == DisclosureKind.REFUSAL.value
    ]
    assert any("Mewa" in d["subject"] for d in refusals)


def test_islamicate_gates_firdaria_durations(fairfield_panel: dict) -> None:
    section = _section(fairfield_panel, "islamicate_persian")
    gated = section["facts"]["distinctive_layers_gated"]
    assert any("firdaria period" in item for item in gated)


def test_render_produces_markdown_with_labels(fairfield_panel: dict) -> None:
    text = render(fairfield_panel)
    assert text.startswith("# Multi-tradition panel")
    assert "Refused" in text
    assert "Configured" in text
    for section in fairfield_panel["sections"]:
        assert section["display_name"] in text


def test_broken_section_does_not_kill_panel(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.engine.multitradition import panel as panel_module

    def explode(*_args, **_kwargs):
        raise RuntimeError("simulated failure")

    monkeypatch.setattr(panel_module.mesoamerican, "build_maya", explode)
    result = panel_module.build_panel(FAIRFIELD)
    maya = _section(result, "maya")
    assert maya["error"] and "simulated failure" in maya["error"]
    # Every other section still built.
    others = [s for s in result["sections"] if s["tradition_id"] != "maya"]
    assert all(not s.get("error") for s in others)
