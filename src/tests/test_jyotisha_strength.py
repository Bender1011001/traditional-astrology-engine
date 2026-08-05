"""Every figure the 1899 printing works, reproduced by the engine.

The commentary works the Sun's sadbala right through: five components, their
sum, the drik correction and the pinda. If this module cannot reproduce those
printed numbers it is not implementing the recension, whatever else it is
doing. The same applies to the ashtakavarga row-sums, which are the only check
that eight hand-transcribed tables were transcribed correctly.
"""

from __future__ import annotations

import pytest

from src.engine.multitradition.jyotisha_strength import (
    BHINNA_TABLES,
    BHINNA_TOTALS,
    GRAHAS,
    RASIS,
    SARVA_TOTAL,
    StrengthInputs,
    as_rupas,
    ashtakavarga,
    ayana_bala,
    bhinnashtakavarga,
    dig_bala,
    drsti_virupas,
    ekadhipatya_sodhana,
    natonnata_bala,
    paksha_bala,
    pindotpatti,
    rasi_deg_to_degrees,
    sarvashtakavarga,
    strongest,
    to_virupas,
    trikona_sodhana,
    uccha_bala,
)

# The chapter's own worked nativity, so far as its figures are printed.
SUN = rasi_deg_to_degrees("10|4|14")
MOON = rasi_deg_to_degrees("8|25|29")


def _sun_inputs(**over) -> StrengthInputs:
    base = dict(
        longitudes={"Sun": SUN, "Moon": MOON},
        lagna=rasi_deg_to_degrees("0|6|3|42"),
        ayanamsa=rasi_deg_to_degrees("0|22|1"),
        is_day_birth=True,
        ishta_ghati=8 + 16 / 60,
        half_day_ghati=13 + 54 / 60,
    )
    base.update(over)
    return StrengthInputs(**base)


# -- notation ------------------------------------------------------------


def test_the_leading_place_is_the_rupa_not_the_virupa():
    """Reading it as virupas is wrong by a factor of sixty, and looks fine."""
    assert to_virupas("1|0|0") == 60.0
    assert to_virupas("0|49|1") == pytest.approx(49 + 1 / 60)
    assert as_rupas(60.0) == "1|0|00"


def test_rupa_rendering_carries_instead_of_printing_sixty():
    assert as_rupas(to_virupas("4|59|59.6")).endswith("|00")


# -- drik-bala -----------------------------------------------------------


@pytest.mark.parametrize(
    "arc,expected",
    [
        # The commentary's own example: Moon 3|5|2|1 aspecting Sun 9|7|5|43.
        (182.0617, "58|58|09"),
        # Remainder over five rasis: drop the rasis and double 2|3|42.
        (150 + 2 + 3 / 60 + 42 / 3600, "4|7|24"),
    ],
)
def test_drsti_reproduces_the_printed_examples(arc, expected):
    got = drsti_virupas(arc)
    want = to_virupas("0|" + expected) if expected.count("|") == 2 else None
    assert want is not None
    assert got == pytest.approx(want, abs=0.001)


def test_the_worked_arc_is_the_one_the_text_states():
    aspecting = rasi_deg_to_degrees("3|5|2|1")
    aspected = rasi_deg_to_degrees("9|7|5|43")
    assert (aspected - aspecting) % 360.0 == pytest.approx(182.0617, abs=0.001)


def test_drsti_is_zero_where_the_text_supplies_no_rule():
    assert drsti_virupas(15.0) == 0.0
    assert drsti_virupas(320.0) == 0.0


# -- the Sun's five components -------------------------------------------


def test_uccha_bala_reproduces_38_04():
    got = uccha_bala("Sun", _sun_inputs())
    assert got.virupas == pytest.approx(to_virupas("0|38|04"), abs=0.02)


def test_dig_bala_reproduces_49_01():
    """The printed arc is 147|05; the Sun is subtracted from the 4th bhava."""
    inputs = _sun_inputs(
        bhava_madhyas={4: (SUN - (147 + 5 / 60)) % 360.0}
    )
    got = dig_bala("Sun", inputs)
    assert got.virupas == pytest.approx(to_virupas("0|49|01"), abs=0.02)


def test_paksha_bala_reproduces_both_sides_of_the_printed_figure():
    inputs = _sun_inputs()
    # The Sun is reckoned among the others, so it takes sixty less the arc.
    assert paksha_bala("Sun", inputs).virupas == pytest.approx(
        to_virupas("0|47|05"), abs=0.02
    )
    assert paksha_bala("Moon", inputs).virupas == pytest.approx(
        to_virupas("0|12|55"), abs=0.02
    )


def test_natonnata_reproduces_48_44_and_its_complement():
    inputs = _sun_inputs()
    assert natonnata_bala("Sun", inputs).virupas == pytest.approx(
        to_virupas("0|48|44"), abs=0.02
    )
    assert natonnata_bala("Moon", inputs).virupas == pytest.approx(
        to_virupas("0|11|16"), abs=0.02
    )


def test_mercury_takes_sixty_always():
    assert natonnata_bala("Mercury", _sun_inputs()).virupas == 60.0
    # Even with no clock supplied at all.
    bare = StrengthInputs(longitudes={"Mercury": 0.0}, lagna=0.0)
    assert natonnata_bala("Mercury", bare).virupas == 60.0


def test_ayana_bala_reproduces_the_doubled_27_15():
    """Sayana 10|26|15, bhuja 1|3|45, khandas to 49.125, then 90 less that."""
    got = ayana_bala("Sun", _sun_inputs())
    assert got.virupas == pytest.approx(to_virupas("0|27|15"), abs=0.05)


def test_the_khandas_produce_the_printed_intermediate():
    from src.engine.multitradition.jyotisha_strength import _khanda_arc

    bhuja = rasi_deg_to_degrees("1|3|45")
    # The printing's intermediate is 1|19|7|30 = 49.125 degrees.
    assert _khanda_arc(bhuja) == pytest.approx(49.125, abs=0.001)


# -- undecided limbs stay undecided --------------------------------------


def test_a_missing_clock_leaves_natonnata_undecided_not_zero():
    bare = StrengthInputs(longitudes={"Sun": SUN, "Moon": MOON}, lagna=0.0)
    got = natonnata_bala("Sun", bare)
    assert got.virupas is None
    assert not got.known
    assert str(got) == "undecided"


def test_a_pinda_with_an_undecided_limb_is_undecided_not_partial():
    from src.engine.multitradition.jyotisha_strength import sadbala

    bare = StrengthInputs(longitudes={"Sun": SUN, "Moon": MOON}, lagna=0.0)
    result = sadbala(bare)
    assert result["Sun"]["sadbala_pinda"] is None
    assert result["Sun"]["meets_minimum"] is None


def test_strongest_refuses_to_rank_against_an_unknown():
    """BPHS 2.44's rule is a comparison; a comparison to an unknown is not one."""
    result = {
        "Mars": {"sadbala_pinda": 400.0},
        "Venus": {"sadbala_pinda": None},
    }
    assert strongest(result, ["Mars", "Venus"]) is None
    assert strongest(result, ["Mars"]) == "Mars"


# -- Ashtakavarga --------------------------------------------------------


def test_every_bhinna_table_sums_to_its_printed_total():
    for varga, table in BHINNA_TABLES.items():
        got = sum(len(v) for v in table.values())
        assert got == BHINNA_TOTALS[varga], f"{varga} sums to {got}"


def test_the_seven_graha_tables_sum_to_337():
    assert sum(BHINNA_TOTALS[g] for g in GRAHAS) == SARVA_TOTAL


def test_sarva_is_337_for_any_chart_whatever():
    """The total is a property of the tables, so it holds for every nativity."""
    for shift in (0, 1, 5, 7, 11):
        positions = {p: (i * 3 + shift) % 12 for i, p in enumerate(
            ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn",
             "Lagna")
        )}
        assert sum(sarvashtakavarga(positions).values()) == SARVA_TOTAL


def test_a_bhinna_row_sums_to_its_total_for_any_chart():
    positions = {p: i for i, p in enumerate(
        ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn",
         "Lagna")
    )}
    for varga in BHINNA_TABLES:
        assert sum(bhinnashtakavarga(varga, positions).values()) == (
            BHINNA_TOTALS[varga]
        )


@pytest.mark.parametrize(
    "trine,expected",
    [
        # A trine holding a zero is left alone entirely.
        ({"Taurus": 2, "Virgo": 5, "Capricorn": 0}, (2, 5, 0)),
        ({"Gemini": 4, "Libra": 6, "Aquarius": 5}, (0, 2, 1)),
        ({"Cancer": 3, "Scorpio": 4, "Pisces": 4}, (0, 1, 1)),
        # All three equal: zero in all three.
        ({"Taurus": 5, "Virgo": 5, "Capricorn": 5}, (0, 0, 0)),
    ],
)
def test_trikona_sodhana_reproduces_the_worked_trines(trine, expected):
    counts = {r: 0 for r in RASIS}
    counts.update(trine)
    got = trikona_sodhana(counts)
    assert tuple(got[r] for r in trine) == expected


def test_ekadhipatya_leaves_both_alone_when_both_are_occupied():
    """The text is flat about it: na samsodhyah kadachana."""
    counts = {r: 0 for r in RASIS}
    counts.update({"Sagittarius": 2, "Pisces": 1})
    got = ekadhipatya_sodhana(counts, occupied={"Sagittarius", "Pisces"})
    assert (got["Sagittarius"], got["Pisces"]) == (2, 1)


def test_ekadhipatya_zeroes_both_when_neither_is_occupied_and_they_are_equal():
    counts = {r: 0 for r in RASIS}
    counts.update({"Taurus": 1, "Libra": 1})
    got = ekadhipatya_sodhana(counts, occupied=set())
    assert (got["Taurus"], got["Libra"]) == (0, 0)


def test_ekadhipatya_unoccupied_unequal_leaves_the_difference():
    counts = {r: 0 for r in RASIS}
    counts.update({"Taurus": 3, "Libra": 1})
    got = ekadhipatya_sodhana(counts, occupied=set())
    assert (got["Taurus"], got["Libra"]) == (2, 0)


def test_ekadhipatya_occupied_higher_zeroes_the_unoccupied_one():
    counts = {r: 0 for r in RASIS}
    counts.update({"Pisces": 4, "Sagittarius": 1})
    got = ekadhipatya_sodhana(counts, occupied={"Pisces"})
    assert (got["Pisces"], got["Sagittarius"]) == (4, 0)


def test_cancer_and_leo_are_exempt_from_ekadhipatya():
    counts = {r: 0 for r in RASIS}
    counts.update({"Cancer": 3, "Leo": 3})
    got = ekadhipatya_sodhana(counts, occupied=set())
    assert (got["Cancer"], got["Leo"]) == (3, 3)


def test_pindotpatti_reproduces_the_printed_91():
    """The Sun's varga: graha pinda 40, rasi pinda 51, yoga pinda 91."""
    reduced = {r: 0 for r in RASIS}
    reduced.update(
        {"Aquarius": 1, "Pisces": 1, "Leo": 1, "Sagittarius": 2}
    )
    graha_rasis = {
        "Sun": "Aquarius", "Jupiter": "Aquarius",
        "Venus": "Pisces", "Mars": "Pisces",
        "Moon": "Sagittarius",
        "Saturn": "Capricorn", "Mercury": "Capricorn",
    }
    got = pindotpatti(reduced, graha_rasis)
    assert got["graha_pinda"] == 40
    assert got["rasi_pinda"] == 51
    assert got["yoga_pinda"] == 91


def test_the_pipeline_sums_the_sarva_before_it_reduces():
    """Reducing before summing reports a total that is not 337."""
    positions = {p: (i * 2) % 12 for i, p in enumerate(
        ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn",
         "Lagna")
    )}
    graha_rasis = {g: RASIS[positions[g]] for g in GRAHAS}
    got = ashtakavarga(positions, graha_rasis)
    assert got["sarva_total"] == SARVA_TOTAL
    # And the reductions really did happen to the per-graha tables.
    assert sum(got["after_reductions"]["Sun"].values()) < BHINNA_TOTALS["Sun"]
