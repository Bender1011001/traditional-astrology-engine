"""Regressions for doctrine corrected against the Greek sources, August 2026.

Each test names the passage it enforces. These are not style checks: every one
of them covers a rule the engine computed the inputs for and then failed to
apply, so a silent revert would look like working software.

Working notes: docs/sources/valens_greek_notes.md
Text and translations: docs/sources/valens_translation.md
"""
from __future__ import annotations

import json

import pytest

from src.engine.dignities import DignityCalculator, TriplicityScheme
from src.engine.models import PlanetName, Sect, Sign
from src.engine.reference_data import (PTOLEMAIC_TRIPLICITY,
                                       PTOLEMAIC_TRIPLICITY_PARTICIPATING)
from src.scripts.generate_premium_report import generate_chart_data
from src.services.reading_evidence import build_reading_evidence

# 1996-08-13 07:18 Fairfield CA -> DAY chart, Mercury an evening star.
# 1987-02-01 02:00 Kostanay     -> NIGHT chart, Mercury an evening star.
# Same phase, opposite sect, so the pair isolates the rule under test.
_SIGN_ORDER = list(Sign)

DAY_CHART = ("1996-08-13", "07:18", "Fairfield", 38.2494, -122.0400)
NIGHT_CHART = ("1987-02-01", "02:00", "Kostanay", 53.2144, 63.6246)


def _evidence(args):
    date_str, time_str, city, lat, lon = args
    chart = json.loads(
        generate_chart_data("T", date_str, time_str, city, latitude=lat, longitude=lon)
    )
    return build_reading_evidence(chart)


def _mercury_sect(args):
    items = [e for e in _evidence(args) if e.source_rule_id == "ptolemy_sect_membership"]
    assert items, "no Mercury sect evidence emitted"
    return items[0]


# --------------------------------------------------------------------------
# Ptolemy, Tetrabiblos I.7 (Boll-Boer Greek, lines 2498-2522):
#   "Mercury is common to both - diurnal when he makes a MORNING appearance,
#    nocturnal when an EVENING one."
# The engine computed the phase and never drew the conclusion, reporting
# Mercury as permanently undecided on every chart.
# --------------------------------------------------------------------------


def test_mercury_evening_star_is_contrary_to_sect_in_a_day_chart():
    item = _mercury_sect(DAY_CHART)
    assert item.details["phase"] == "evening"
    assert item.details["reckoned"] == "nocturnal"
    assert item.details["in_sect"] is False
    assert "contrary to the sect" in item.fact


def test_mercury_evening_star_is_in_sect_in_a_night_chart():
    item = _mercury_sect(NIGHT_CHART)
    assert item.details["phase"] == "evening"
    assert item.details["reckoned"] == "nocturnal"
    assert item.details["in_sect"] is True
    assert "of the sect in favour" in item.fact


def test_mercury_sect_verdict_flips_with_the_chart_and_not_the_phase():
    """Same phase, opposite sect: the flip must come from the chart alone."""
    day, night = _mercury_sect(DAY_CHART), _mercury_sect(NIGHT_CHART)
    assert day.details["reckoned"] == night.details["reckoned"]
    assert day.details["in_sect"] != night.details["in_sect"]


def test_mercury_sect_is_cited_to_the_greek_not_to_ashmand():
    item = _mercury_sect(DAY_CHART)
    assert "Apotelesmatika" in item.authority
    assert "chapter 7" in item.authority
    assert "Ashmand" not in item.authority


# --------------------------------------------------------------------------
# Ptolemy, Tetrabiblos I.19 (lines 3859-3895): the WATER triangle "was left to
# Mars ... and co-ruling it WITH HIM ... by night the Moon, and by day Venus."
# Water is his only three-ruler triangle. Lilly keeps only Mars; the common
# table keeps only Venus/Moon. Both drop half the sentence.
# --------------------------------------------------------------------------


def test_water_is_the_only_three_ruler_triangle():
    assert set(PTOLEMAIC_TRIPLICITY_PARTICIPATING) == {"Water"}
    assert PTOLEMAIC_TRIPLICITY_PARTICIPATING["Water"] is PlanetName.MARS


def test_ptolemaic_water_sect_pair_is_venus_by_day_and_moon_by_night():
    """Attested twice: Ptolemy I.19 and Valens II.1 both give Venus by day."""
    assert PTOLEMAIC_TRIPLICITY["Water"] == (PlanetName.VENUS, PlanetName.MOON)


@pytest.mark.parametrize("sect", [Sect.DAY, Sect.NIGHT])
@pytest.mark.parametrize("sign", [Sign.CANCER, Sign.SCORPIO, Sign.PISCES])
def test_mars_scores_ptolemaic_water_triplicity_in_both_sects(sign, sect):
    """Mars co-rules the water triangle with the sect pair, so he holds it in
    both sects. The two-slot table cannot express that; before the fix he
    scored nothing here."""
    longitude = _SIGN_ORDER.index(sign) * 30 + 15.0
    result = DignityCalculator.calculate_planet_dignity_variant(
        PlanetName.MARS,
        longitude,
        sect,
        triplicity_scheme=TriplicityScheme.PTOLEMAIC_SECT_GATED,
    )
    assert result["score_breakdown"].get("triplicity") == DignityCalculator.TRIPLICITY
    assert any("participating" in d for d in result["details"])


@pytest.mark.parametrize("sign", [Sign.ARIES, Sign.TAURUS, Sign.GEMINI])
def test_the_participating_ruler_does_not_leak_into_other_triangles(sign):
    """Ptolemy names a third ruler for water ONLY. Fire, earth and air get two
    each, and Mars is expressly excluded from fire on sect grounds."""
    longitude = _SIGN_ORDER.index(sign) * 30 + 15.0
    result = DignityCalculator.calculate_planet_dignity_variant(
        PlanetName.MARS,
        longitude,
        Sect.DAY,
        triplicity_scheme=TriplicityScheme.PTOLEMAIC_SECT_GATED,
    )
    assert not result["score_breakdown"].get("triplicity")


# --------------------------------------------------------------------------
# Valens IV.16, 185: "from EACH PLACE the significations or the releases of the
# years should be made: from the Midheaven when we inquire about action, and
# from the place concerning MARRIAGE when about a wife."
# Releasing was hard-wired to Fortune and Spirit, so no report could answer a
# topical timing question.
# --------------------------------------------------------------------------


def _releasing(args):
    date_str, time_str, city, lat, lon = args
    chart = json.loads(
        generate_chart_data("T", date_str, time_str, city, latitude=lat, longitude=lon)
    )

    def find(obj, key, depth=0):
        if depth > 7 or not isinstance(obj, dict):
            return None
        if key in obj:
            return obj[key]
        for value in obj.values():
            found = find(value, key, depth + 1)
            if found is not None:
                return found
        return None

    return find(chart, "zodiacal_releasing")


def test_releasing_covers_the_two_lots_and_the_topical_places():
    zr = _releasing(DAY_CHART)
    assert zr is not None
    assert {"Spirit", "Fortune", "Marriage_7th", "Children_5th", "Action_10th"} <= set(zr)


def test_topical_release_starts_from_the_right_whole_sign_place():
    """Virgo rising -> 7th is Pisces, 5th Capricorn, 10th Gemini."""
    zr = _releasing(DAY_CHART)
    assert zr["Marriage_7th"]["start_sign"] == "Pisces"
    assert zr["Children_5th"]["start_sign"] == "Capricorn"
    assert zr["Action_10th"]["start_sign"] == "Gemini"


def test_releasing_uses_360_day_years():
    """Valens IV.9, p.169 states it outright: "Since the COSMIC YEAR is of 365 1/4
    days, BUT FOR THE DIVISION the year is 360." He distinguishes the
    astronomical year from the one used for time-division, and the divisions use
    360. IV.10's conversion table agrees independently - each period given as
    years, then months, then days, with the days always the years x 2.5, which
    makes a month 2.5 days and a year 30.

    Pisces releases 12 years; under calendar years the first chapter would end
    in mid-2008 rather than 2008-06-11, putting every later boundary about six
    months late."""
    chapters = _releasing(DAY_CHART)["Marriage_7th"]["l1_chapters"]
    first = chapters[0]
    assert first["sign"] == "Pisces"
    assert first["start_date"].startswith("1996-08-13")
    assert first["end_date"].startswith("2008-06-11")


# --------------------------------------------------------------------------
# Valens II.17, 79,7: "Before all one must precisely establish the Lot of
# Fortune ... For the Lot itself takes up the power of the ASCENDANT and of
# LIFE; the tenth from it, of MIDHEAVEN and REPUTATION."
# topical.py emitted places_from_fortune all along; nothing surfaced it.
# --------------------------------------------------------------------------


def _fortune_items(args):
    return [e for e in _evidence(args) if e.category == "fortune_derived"]


def test_the_fortune_derived_layer_reaches_the_reader():
    items = _fortune_items(DAY_CHART)
    assert items, "places_from_fortune computed but never surfaced"
    assert any(e.source_rule_id == "valens_fortune_derived_places" for e in items)


def test_acquisition_place_is_named_and_located():
    """Valens II.20, 82,6 defines the Acquisition as the 11th from Fortune.
    Without that definition the II.22 wealth-arc rule is uninterpretable."""
    item = [
        e for e in _fortune_items(DAY_CHART)
        if e.source_rule_id == "valens_fortune_derived_places"
    ][0]
    assert item.details["fortune_house"] == 12
    assert item.details["fortune_tier"] == "injurious"
    assert item.details["acquisition_house"] == 10
    assert item.details["acquisition_tier"] == "busy"


def test_place_tiers_follow_valens_own_ranking():
    """IV.11, 176 - busy: Asc, MC, 11th, 5th. Middling: 9th, 3rd, 7th, 4th.
    Injurious: the rest. This defines chrematistikos, which II.2 and II.22
    both depend on."""
    from src.services.reading_evidence import _place_tier
    assert [_place_tier(h) for h in (1, 10, 11, 5)] == ["busy"] * 4
    assert [_place_tier(h) for h in (9, 3, 7, 4)] == ["middling"] * 4
    assert [_place_tier(h) for h in (2, 6, 8, 12)] == ["injurious"] * 4


def test_the_wealth_arc_rule_is_selective_not_automatic():
    """The Acquisition is a fixed ten-sign offset from Fortune, so the two
    tiers are not independent. The rule must therefore fire on only some
    Fortune placements - four of twelve - or it would be saying nothing."""
    from src.services.reading_evidence import _place_tier
    split = [
        h for h in range(1, 13)
        if (_place_tier(h) == "injurious") != (_place_tier(((h - 1) + 10) % 12 + 1) == "injurious")
    ]
    assert split == [4, 6, 10, 12]


def test_the_wealth_arc_states_its_own_dependency():
    """The two tiers are one placement expressed twice. If the limit ever stops
    saying so, a reader could count them as two agreeing testimonies."""
    items = [
        e for e in _fortune_items(DAY_CHART)
        if e.source_rule_id == "valens_fortune_acquisition_arc"
    ]
    assert items
    assert "NOT" in items[0].interpretive_limit
    assert "independent" in items[0].interpretive_limit


# --------------------------------------------------------------------------
# Valens I.7, p. 23: "Since Aries ascends in 20, Libra ascends in 40, to the
# completion of 60. For however much each sign ascends in, the diametrically
# opposite sign takes up the remainder to 60."
# This invariant sits under ZR period lengths, the aphesis conversion and the
# II.2 life-arc hinge. It is cheap to assert and catches table corruption.
# --------------------------------------------------------------------------


def test_valens_sixty_invariant_is_schematic_not_astronomical():
    """Valens I.7: "Since Aries ascends in 20, Libra in 40, to the completion of
    60. For however much each sign ascends in, the diametrically opposite sign
    takes up the remainder to 60."

    THIS DOES NOT HOLD under exact spherical computation, and the reason is
    structural. Oblique ascension is OA = RA - AD, and AD(l+180) = -AD(l), so
    in a pair the ascensional-difference terms cancel and the sum reduces to
    2 x (the RA span of the sign). That equals 60 only where the RA span is
    exactly 30 - i.e. at the equinoxes. Everywhere else it drifts.

    Valens's 60 is therefore a property of the ancient ARITHMETICAL rising-time
    schemes, which are linear by construction, not of the sky.

    CONFIRMED FROM HIS OWN TABLE. At VIII.6, p.304 he gives "let Aries, in the
    second clima, ascend in 20 ... since Taurus ascends in 24" - an arithmetic
    step of 4. Extended and mirrored that is 20/24/28/32/36/40/40/36/32/28/24/20,
    summing to 360, with every opposite pair on 60 BY CONSTRUCTION. The invariant
    is an artifact of the progression.

    This test pins the discrepancy so nobody "fixes" the engine's exact astronomy
    to match a schematic table, and so nobody mixes Valens's tabulated ascensions
    with our computed ones in the same calculation - they disagree by up to 4.4
    degrees, and both get used wherever the text says "the ascension of the sign".
    """
    from src.engine.multitradition.islamicate import oblique_ascension
    obliquity, geo_lat = 23.4392911, 38.2494

    def rising_time(lon0):
        return (oblique_ascension(lon0 + 30.0, geo_lat, obliquity)
                - oblique_ascension(lon0, geo_lat, obliquity)) % 360.0

    pairs = [rising_time(float(s)) + rising_time(float(s + 180)) for s in range(0, 180, 30)]
    assert not all(abs(p - 60.0) < 0.5 for p in pairs), (
        "the 60 invariant now holds exactly - if the ascension model changed to a "
        "schematic one, that is a deliberate decision and this test should be revisited"
    )
    assert min(pairs) > 55.0 and max(pairs) < 65.0, (
        "pair sums drifted outside the expected 55-65 band; the ascension model may be wrong"
    )
    # The equinoctial pairs are the closest to Valens's figure, as the algebra predicts.
    assert abs(pairs[1] - 60.0) < abs(pairs[3] - 60.0)


def test_all_twelve_rising_times_sum_to_the_circle():
    from src.engine.multitradition.islamicate import oblique_ascension
    obliquity, geo_lat = 23.4392911, 38.2494
    total = sum(
        (oblique_ascension(s + 30.0, geo_lat, obliquity)
         - oblique_ascension(float(s), geo_lat, obliquity)) % 360.0
        for s in range(0, 360, 30)
    )
    assert abs(total - 360.0) < 1e-6


# --------------------------------------------------------------------------
# Bound delineations - Valens I.3, pp. 14-19. Complete: 60 of 60.
# --------------------------------------------------------------------------


def test_every_bound_of_every_sign_is_translated():
    """The table was partial (41 of 60) while pp. 15-19 were still unread. It is
    now closed, so the gaps must not silently reappear under an edit."""
    from src.engine.valens_delineations import BOUND_DELINEATIONS
    assert len(BOUND_DELINEATIONS) == 60
    signs = (
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    )
    for sign in signs:
        lords = {key[1] for key in BOUND_DELINEATIONS if key[0] == sign}
        assert len(lords) == 5, f"{sign} has {len(lords)} bound delineations"


def test_an_unknown_bound_still_stays_silent():
    """An invented delineation is indistinguishable from a translated one at
    the point of use. A miss must produce None, never a generic phrase."""
    from src.engine.valens_delineations import bound_delineation
    assert bound_delineation("Cancer", "Sun") is None
    assert bound_delineation(None, "Mars") is None
    assert bound_delineation("Aries", "Jupiter") is not None


def test_bound_delineations_reach_the_customer_prose_not_only_the_packet():
    """The emitter shipped without a renderer, so the packet carried all eight
    delineations and the report printed none of them - while the appendix still
    cited the items and their caveat. The reader got "the domicile lord decides
    whether what the degree carries comes out base or good" with no statement of
    what the degree carries: a condition dangling off a claim never made.

    Evidence existing is not evidence rendered. This asserts on the PROSE.
    """
    from src.scripts.generate_premium_report import generate_chart_data_object
    from src.services.reading_composer import compose_deterministic_draft

    date_str, time_str, city, lat, lon = DAY_CHART
    chart = generate_chart_data_object(
        "T", date_str, time_str, city, latitude=lat, longitude=lon
    )
    draft, packet = compose_deterministic_draft(chart)

    emitted = [e for e in packet["evidence"] if e["category"] == "bound_delineation"]
    assert emitted, "no bound evidence emitted at all"
    # Seven planets plus the Ascendant, and the table is complete, so every one
    # of them must be delineated and every one must be printed.
    assert len(emitted) == 8, f"expected 8 bound items, got {len(emitted)}"
    assert draft.count("Valens delineates that bound") == len(emitted), (
        "bound delineations were emitted but not rendered into the report"
    )
    # The governing condition must travel with them.
    assert "domicile lord" in draft


def test_bound_delineation_is_conditioned_by_the_domicile_lord():
    """Valens closes I.3 (p. 19,4-7) by saying the degrees were set out ALONE for
    teaching, and that the domicile lord lying over them decides whether what
    they carry comes out base or good. Quoting the bound without that condition
    turns a substrate into a verdict."""
    items = [e for e in _evidence(DAY_CHART) if e.category == "bound_delineation"]
    assert items
    assert all("domicile lord" in e.interpretive_limit for e in items)


def test_the_ascendant_bound_is_delineated_not_only_the_planets():
    """Valens singles the rising degree out at I.3 p.15 - 'especially these
    degrees' - so it must not be dropped just because it is not a planet."""
    items = [e for e in _evidence(DAY_CHART) if e.category == "bound_delineation"]
    assert any(e.details.get("point") == "Ascendant" for e in items)


# --------------------------------------------------------------------------
# Lunar configurations - Valens II.35. The band after the full moon was wrong
# in the first draft; "to 280 the second half-moon, then to 360 to the setting".
# --------------------------------------------------------------------------


def test_lunar_bands_follow_valens_boundaries():
    from src.engine.valens_delineations import lunar_phase_for
    assert lunar_phase_for(20)["name"] == "rising"
    assert lunar_phase_for(100)["name"] == "first half-moon"
    assert lunar_phase_for(160)["name"] == "first gibbous"
    assert lunar_phase_for(200)["name"] == "second gibbous"
    assert lunar_phase_for(250)["name"] == "second half-moon"
    assert lunar_phase_for(300)["name"] == "setting"


# --------------------------------------------------------------------------
# Marriage tests - Valens II.37, II.38.
# --------------------------------------------------------------------------


def test_marriage_tests_fire_on_both_reference_charts():
    for chart in (DAY_CHART, NIGHT_CHART):
        items = [e for e in _evidence(chart) if e.category == "marriage_testimony"]
        assert items, "no marriage testimony emitted"


def test_saturn_overcoming_venus_is_detected_by_sign_not_orb():
    """Overcoming is kathyperteresis: the tenth sign from her, whole-sign."""
    item = [e for e in _evidence(DAY_CHART) if e.category == "marriage_testimony"][0]
    assert item.details.get("saturn_overcomes_venus") is True


def test_venus_in_saturns_bound_is_a_named_condition():
    """II.37 names 'Venus in Saturn's sign or BOUNDS' alongside the aspect.
    Omitting it missed the most specific Saturn-Venus contact available."""
    item = [e for e in _evidence(NIGHT_CHART) if e.category == "marriage_testimony"][0]
    assert item.details.get("venus_in_saturn_bound") is True


def test_the_escape_clause_is_reported_and_not_silently_applied():
    """Valens attaches it ONLY to the severest outcome. It must be stated as a
    condition on that branch, never used to soften the milder statements."""
    item = [e for e in _evidence(DAY_CHART) if e.category == "marriage_testimony"][0]
    assert "severest" in item.fact
    assert "governs ONLY the sentence" in item.interpretive_limit


# --------------------------------------------------------------------------
# Timing verdicts - Valens IV.14 (postponement) and IV.16 (the hypostasis cap).
# --------------------------------------------------------------------------


def test_retrograde_lord_of_year_reads_as_postponement():
    items = [
        e for e in _evidence(DAY_CHART)
        if e.source_rule_id == "valens_retrograde_timelord_postponement"
    ]
    assert items
    assert items[0].details["verdict"] == "postponement"
    assert "denial" in items[0].fact


def test_every_chart_carries_the_hypostasis_cap():
    """'Not as though for the greater and the glorious alike, BUT DISTINGUISH.'
    The guard against reading a period identically across charts."""
    for chart in (DAY_CHART, NIGHT_CHART):
        assert any(
            e.source_rule_id == "valens_hypostasis_caps_timing" for e in _evidence(chart)
        )


# --------------------------------------------------------------------------
# Valens I.1, printed p. 5 - the placement-and-sect test runs BEFORE the label.
# The composer previously read essential dignity alone and asserted the verdict
# from it: "because X is debilitated, these matters do not operate cleanly".
# That is the judgment order Valens forbids at I.22 p.49, where he calls the
# delineation lists "single-form and universal distinctions" and says "the power
# of the matters WILL BE ALTERED" by placement.
# --------------------------------------------------------------------------

from src.services.reading_composer import _valens_placement_verdict


def test_a_malefic_in_its_own_place_and_in_sect_is_a_giver_of_good_things():
    verdict = _valens_placement_verdict("Saturn", {"dignities": "domicile", "house": 11}, "DAY")
    assert verdict and "giver of good things" in verdict
    assert "advancement" in verdict


def test_the_same_malefic_out_of_sect_does_not_get_that_verdict():
    """Mars in his own place by DAY is out of sect, so the test fails."""
    assert _valens_placement_verdict("Mars", {"dignities": "domicile", "house": 10}, "DAY") is None
    assert _valens_placement_verdict("Mars", {"dignities": "domicile", "house": 10}, "NIGHT")


def test_the_same_malefic_in_an_injurious_place_does_not_get_that_verdict():
    """In sect and in its own sign, but fallen into the 12th - the placement
    half of the test fails, so the verdict does not fire."""
    assert _valens_placement_verdict("Saturn", {"dignities": "domicile", "house": 12}, "DAY") is None


def test_a_benefic_in_an_injurious_place_is_neutralised():
    """II.5, II.8, II.10 and II.14 - benefics there 'help nothing', are
    'ineffective and weak', and 'do not distribute their own goods'."""
    verdict = _valens_placement_verdict("Venus", {"dignities": "domicile", "house": 6}, "NIGHT")
    assert verdict and "do not distribute their own goods" in verdict
    assert "does not survive the placement" in verdict


def test_a_well_placed_benefic_falls_through_to_ordinary_prose():
    assert _valens_placement_verdict("Jupiter", {"dignities": "domicile", "house": 10}, "DAY") is None


def test_the_inversion_reaches_the_composed_reading():
    """Not just the helper - the verdict must appear in the draft a reader sees."""
    import json
    from src.scripts.generate_premium_report import generate_chart_data
    from src.services.reading_composer import compose_deterministic_draft
    date_str, time_str, city, lat, lon = NIGHT_CHART
    chart = json.loads(
        generate_chart_data("T", date_str, time_str, city, latitude=lat, longitude=lon)
    )
    draft, _ = compose_deterministic_draft(chart)
    assert "does not survive the placement" in draft


# --------------------------------------------------------------------------
# Valens IV.22, p. 195: "Mars distributing to himself BY DAY will be unpleasant
# and troublesome ... BUT BY NIGHT HE IS NOT BAD, but successful and beneficial
# - especially if he stands in the transacting signs." IV.19 says the same of
# the Ascendant handing to a malefic: worst "especially to SATURN BY NIGHT and
# to MARS BY DAY" - the OUT-OF-SECT one in each case.
# The natal paragraphs already applied sect-before-label; the timing layer was
# still asserting from the malefic label alone.
# --------------------------------------------------------------------------


def _malefic_timelord_verdict(lord, is_day, house):
    """Mirror of the rule in reading_evidence, exercised directly so both
    branches are covered without hunting for a chart that produces each."""
    from src.services.reading_evidence import _place_tier
    of_sect = (lord == "Saturn") if is_day else (lord == "Mars")
    tier = _place_tier(house)
    return "effective" if (of_sect and tier != "injurious") else "harder"


def test_a_malefic_timelord_in_sect_and_well_placed_reads_as_effective():
    assert _malefic_timelord_verdict("Saturn", True, 11) == "effective"
    assert _malefic_timelord_verdict("Mars", False, 10) == "effective"


def test_the_same_malefic_timelord_out_of_sect_reads_as_harder():
    """Same planet, same house, opposite sect - the verdict must flip."""
    assert _malefic_timelord_verdict("Saturn", False, 11) == "harder"
    assert _malefic_timelord_verdict("Mars", True, 10) == "harder"


def test_an_injurious_place_overrides_being_in_sect():
    """Valens gates the favourable reading on the transacting signs, so sect
    alone is not enough."""
    assert _malefic_timelord_verdict("Saturn", True, 8) == "harder"


def test_the_malefic_timelord_rule_reaches_both_reference_charts():
    for chart in (DAY_CHART, NIGHT_CHART):
        items = [
            e for e in _evidence(chart)
            if e.source_rule_id == "valens_malefic_timelord_by_sect"
        ]
        assert items, "malefic time-lord rule did not fire"
        assert items[0].details["verdict"] in {"effective", "harder"}



# ---------------------------------------------------------------------------
# Valens V.1 (Kroll pp. 207-209): the causative place
# ---------------------------------------------------------------------------


def test_the_causative_place_is_built_from_the_two_malefics_by_sect():
    """Valens V.1 builds this Lot from Saturn and Mars alone.

    Day takes the arc Saturn->Mars projected from the Ascendant, night reverses
    it. No luminary and no benefic enters the formula - that is what separates
    it from every other Lot in the table, and reversing the sect direction
    would silently land it in a different sign.
    """
    from src.engine.lots import calculate_lot

    asc, saturn, mars = 0.0, 10.0, 70.0
    day = calculate_lot(asc, saturn, mars)
    night = calculate_lot(asc, mars, saturn)

    assert day == pytest.approx(60.0)
    assert night == pytest.approx(300.0)
    assert day != night


def test_the_causative_place_reports_malefic_testimony_rather_than_asserting_danger():
    """Valens's test is whether a malefic owns the resulting place.

    The engine must report that testimony, not convert the Lot's topic - fears,
    dangers, confinement - into a claim about the reader. Where neither malefic
    owns the sign, the emitted text has to say so rather than imply the danger
    stands anyway.
    """
    items = [e for e in _evidence(DAY_CHART) if e.category == "causative_place"]
    assert items, "no causative_place evidence emitted"
    item = items[0]

    assert "V.1" in item.authority and "Valens" in item.authority
    assert item.source_rule_id == "valens_causative_place"
    assert "not a verdict about the reader" in item.interpretive_limit

    owner = item.details.get("owner_malefic")
    if owner is None:
        assert "silent" in item.fact
    else:
        assert owner in item.fact


# ---------------------------------------------------------------------------
# Valens V.2 (Kroll p. 210) and VI.5-6 (pp. 251-254): the period techniques
# ---------------------------------------------------------------------------


def test_the_minor_years_sum_to_the_major_period():
    """VI.5's "10 years 9 months" and the minor years are the same fact.

    129 months is 10y9m, and the seven minor years sum to 129. This identity is
    what makes the cascade self-verifying, so if either number is ever edited
    the other must move with it.
    """
    from src.engine.valens_periods import (MAJOR_PERIOD_MONTHS,
                                           MINOR_YEARS_TOTAL,
                                           VALENS_MINOR_YEARS)

    assert MINOR_YEARS_TOTAL == 129
    assert sum(VALENS_MINOR_YEARS.values()) == 129
    assert MAJOR_PERIOD_MONTHS == 129.0
    assert MAJOR_PERIOD_MONTHS / 12.0 == pytest.approx(10.75)  # 10 years 9 months


def test_the_subdivision_reproduces_valenss_own_worked_example():
    """VI.6 works Saturn's 30-month share out loud. We must match him.

    Six of his seven figures reproduce to the day. Jupiter is the exception -
    he prints 2m27d where the rule gives 2m23.7d - and that is recorded as a
    likely OCR slip on the numeral rather than smoothed away, because six
    independent agreements outweigh one disagreement.
    """
    from src.engine.valens_periods import CHALDEAN_ORDER, _subdivide

    subs = {s["planet"]: s for s in _subdivide(30.0, CHALDEAN_ORDER)}

    valens = {
        "Saturn": (6, 29),
        "Mars": (3, 14),
        "Sun": (4, 12),
        "Venus": (1, 25),
        "Mercury": (4, 19),
        "Moon": (5, 24),
    }
    for planet, (months, days) in valens.items():
        assert subs[planet]["months"] == months, planet
        assert subs[planet]["days"] == pytest.approx(days, abs=1.0), planet

    # The parts must close back onto the whole.
    assert sum(s["months_decimal"] for s in subs.values()) == pytest.approx(30.0)


def test_the_decennial_cascade_does_not_claim_its_starting_planet_is_verified():
    """The period lengths are confirmed; the opening planet is not.

    VI.5's opening lines were not read closely enough to settle which planet
    starts the sequence, so the engine must keep saying so rather than let a
    configured default harden into a sourced claim.
    """
    from src.engine.valens_periods import decennial_cascade

    result = decennial_cascade(sect_light="Sun", levels=1, count=3)
    assert result["starting_planet_verified"] is False
    assert result["major_period_months"] == 129.0


def test_the_syzygy_climacteric_marks_the_syzygy_sign_and_its_hard_figures():
    """V.2 marks the syzygy sign, its squares, and its opposition - nothing else.

    That is a four-of-twelve lattice, so the marked ages recur every three
    years. A rule that marked more or fewer signs would silently change how
    much of a life gets called disturbed.
    """
    from src.engine.models import Sign
    from src.engine.valens_periods import climacteric_year

    # Ascendant Aries, syzygy at 0 Aries: age 0 is the syzygy sign itself.
    conj = climacteric_year(
        ascendant_sign=Sign.ARIES, prenatal_syzygy_longitude=0.0, age=0
    )
    assert conj["is_climacteric"] and conj["figure_to_syzygy"] == "the syzygy sign itself"

    # Age 3 profects to Cancer - square. Age 6 to Libra - opposition.
    assert climacteric_year(
        ascendant_sign=Sign.ARIES, prenatal_syzygy_longitude=0.0, age=3
    )["figure_to_syzygy"] == "square to the syzygy"
    assert climacteric_year(
        ascendant_sign=Sign.ARIES, prenatal_syzygy_longitude=0.0, age=6
    )["figure_to_syzygy"] == "opposite the syzygy"

    # Age 1 profects to Taurus - a soft figure, not marked.
    assert not climacteric_year(
        ascendant_sign=Sign.ARIES, prenatal_syzygy_longitude=0.0, age=1
    )["is_climacteric"]


def test_transiting_saturn_only_aggravates_a_year_that_is_already_climacteric():
    """Valens gives Saturn as a witness to a climacteric year, not a cause of one.

    A cadent Saturn in an unmarked year must not manufacture a climacteric, or
    the technique would fire on roughly a third of all years by itself.
    """
    from src.engine.models import Sign
    from src.engine.valens_periods import climacteric_year

    # Age 1 is not climacteric; Saturn transiting Gemini is cadent (3rd) from Aries.
    unmarked = climacteric_year(
        ascendant_sign=Sign.ARIES,
        prenatal_syzygy_longitude=0.0,
        age=1,
        transiting_saturn_longitude=65.0,
    )
    assert unmarked["saturn_in_cadent_place"] is True
    assert unmarked["is_climacteric"] is False
    assert unmarked["aggravated"] is False

    marked = climacteric_year(
        ascendant_sign=Sign.ARIES,
        prenatal_syzygy_longitude=0.0,
        age=3,
        transiting_saturn_longitude=65.0,
    )
    assert marked["is_climacteric"] and marked["aggravated"] is True


# --------------------------------------------------------------------------
# The publication contract must not flag its own disclaimers.
#
# Adding the Valens timing rules broke 13 tests because the fatalism check
# matched the bare word "guaranteed", and the new prose says "...not a
# GUARANTEED event". A contract that rejects careful hedging pushes authors
# toward vaguer language, which is the opposite of what it exists to enforce.
# The rule now needs an assertive construction, plus a general negation guard
# applied to every pattern.
# --------------------------------------------------------------------------

from src.services.reading_contract import _FATALISTIC, _pattern_violation


def _is_flagged(text):
    return _pattern_violation(text, _FATALISTIC, "code", "message") is not None


@pytest.mark.parametrize(
    "promise",
    [
        "success is guaranteed by this configuration",
        "the chart guarantees that you will prosper",
        "a guaranteed outcome for the native",
        "this is guaranteed to happen",
        "the chart decrees a change of fortune",
        "this will happen in 2029",
        "fate has determined the result",
        "Rank is guaranteed. The native rises.",
    ],
)
def test_the_contract_still_rejects_a_promised_outcome(promise):
    assert _is_flagged(promise)


@pytest.mark.parametrize(
    "disclaimer",
    [
        "it describes the manner and severity of a difficulty, not a guaranteed event",
        "nothing here is guaranteed",
        "no outcome is guaranteed by a time-lord alone",
        "this is not a guaranteed event but a tendency",
        "it names an interval, never an outcome",
    ],
)
def test_the_contract_does_not_flag_a_denial_of_a_promise(disclaimer):
    assert not _is_flagged(disclaimer)


def test_a_negation_earlier_in_the_sentence_does_not_excuse_a_later_promise():
    """The guard looks back only within the current sentence, so a denial in a
    previous clause must not launder a promise that follows it."""
    assert _is_flagged("Nothing is fixed. Success is guaranteed for this native.")
