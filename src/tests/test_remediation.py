"""Tests for the planetary remediation engine — correspondences + safety split."""
from src.engine.models import Sect
from src.engine.remediation import (PLANETARY_CORRESPONDENCES,
                                    RemediationEngine, _UNSAFE)


def test_canonical_days_and_hours():
    expected_day = {
        "Saturn": "Saturday", "Jupiter": "Thursday", "Mars": "Tuesday",
        "Sun": "Sunday", "Venus": "Friday", "Mercury": "Wednesday", "Moon": "Monday",
    }
    for planet, day in expected_day.items():
        rx = RemediationEngine.prescribe(planet)
        assert rx["election"]["day"] == day
        assert rx["election"]["planetary_hour"] == planet


def test_malefic_contrary_to_sect():
    assert RemediationEngine.malefic_contrary_to_sect(Sect.DAY) == "Mars"
    assert RemediationEngine.malefic_contrary_to_sect(Sect.NIGHT) == "Saturn"


def test_safety_split_never_recommends_toxic_metal():
    # Saturn (lead) and Mercury (quicksilver) are the toxic ones.
    for planet in ("Saturn", "Mercury"):
        rx = RemediationEngine.prescribe(planet)
        assert rx["historical_only"]["unsafe"] is True
        assert rx["historical_only"]["metal"] in _UNSAFE
        # The *recommended* metal must never be a toxic one.
        assert rx["safe_remedies"]["metal"] not in _UNSAFE


def test_no_recommended_item_is_unsafe_across_all_planets():
    for planet in PLANETARY_CORRESPONDENCES:
        rx = RemediationEngine.prescribe(planet)
        assert rx["safe_remedies"]["metal"] not in _UNSAFE
        assert rx["safe_remedies"]["stones"]  # non-empty
        assert rx["safe_remedies"]["charitable_acts"]


def test_prescribe_for_chart_day_targets_mars_first():
    out = RemediationEngine.prescribe_for_chart(Sect.DAY, afflicted_planets=["Saturn", "Venus"])
    assert out["primary_target"] == "Mars"
    targets = [p["planet"] for p in out["prescriptions"]]
    assert targets[0] == "Mars" and "Saturn" in targets
    assert len(targets) <= 3


def test_election_includes_mansion_when_supplied():
    rx = RemediationEngine.prescribe(
        "Saturn", moon_mansion={"name": "Al Sharatain", "intents": "journeys, beginnings"}
    )
    assert rx["election"]["lunar_mansion"] is not None
    assert "Al Sharatain" in rx["election"]["lunar_mansion"]
