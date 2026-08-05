"""The divisional charts, checked against BPHS purva 3's own worked lagna.

The commentary works one nativity through several vargas - Cancer 8 degrees
4 minutes 5 seconds - and those are the only end-to-end checks the chapter
offers. Where a printed result does not follow from the printed procedure,
the test records the disagreement instead of bending the code to the example;
see test_d7_start_point_matches_but_its_named_result_does_not.
"""

from __future__ import annotations

import pytest

from src.engine.multitradition.jyotisha_varga import (
    UNMINED_VARGAS,
    VIMSOPAKA_SCHEMES,
    all_vargas,
    five_fold_relation,
    saptavargaja_dignities,
    varga_d2,
    varga_d3,
    varga_d4,
    varga_d7,
    varga_d9,
    varga_d10,
    varga_d12,
    varga_d30_lord,
    vimsopaka_bala,
)

CANCER = 3 * 30.0
WORKED_LAGNA = CANCER + 8 + 4 / 60 + 5 / 3600  # the commentary's own figure


# -- D2, the hora ---------------------------------------------------------


def test_hora_is_the_suns_in_the_first_half_of_an_odd_sign():
    assert varga_d2(0.0 + 5) == "Leo"       # Aries, an odd sign
    assert varga_d2(0.0 + 20) == "Cancer"


def test_hora_reverses_in_an_even_sign():
    assert varga_d2(30.0 + 5) == "Cancer"   # Taurus, an even sign
    assert varga_d2(30.0 + 20) == "Leo"


# -- D3, the drekkana -----------------------------------------------------


@pytest.mark.parametrize("deg,expected", [(5, 0), (15, 4), (25, 8)])
def test_drekkana_is_the_sign_the_fifth_and_the_ninth(deg, expected):
    from src.engine.multitradition.jyotisha_varga import RASIS

    assert varga_d3(CANCER + deg) == RASIS[(3 + expected) % 12]


def test_the_drekkana_rule_is_the_same_in_odd_and_even_signs():
    """This recension states that explicitly; some handbooks do not."""
    from src.engine.multitradition.jyotisha_varga import RASIS

    for base in (0.0, 30.0, 60.0, 90.0):
        idx = int(base // 30)
        assert varga_d3(base + 15) == RASIS[(idx + 4) % 12]


def test_the_worked_lagna_falls_in_the_first_drekkana():
    assert varga_d3(WORKED_LAGNA) == "Cancer"


# -- D4, the turyamsa -----------------------------------------------------


@pytest.mark.parametrize(
    "deg,offset", [(3, 0), (10, 3), (18, 6), (25, 9)]
)
def test_turyamsa_takes_the_kendras_from_the_sign(deg, offset):
    from src.engine.multitradition.jyotisha_varga import RASIS

    assert varga_d4(CANCER + deg) == RASIS[(3 + offset) % 12]


def test_the_worked_lagna_gives_libra_in_the_turyamsa():
    """The commentary's second quarter of Cancer: the 4th from it."""
    assert varga_d4(WORKED_LAGNA) == "Libra"


# -- D7, the saptamsa -----------------------------------------------------


def test_saptamsa_counts_from_the_sign_itself_in_an_odd_rasi():
    assert varga_d7(0.0 + 1) == "Aries"


def test_d7_start_point_matches_but_its_named_result_does_not():
    """The chapter's start point reproduces; its named saptamsa does not.

    The commentary says to count from Capricorn, the 7th from Cancer, and
    then names Pisces - the third saptamsa. But a saptamsa is 4 degrees
    17 minutes, so 8 degrees 4 minutes of Cancer falls in the SECOND, which
    is Aquarius. The start point is what the rule states and it is what this
    engine implements; the named result cannot be derived from the printed
    procedure and the degree, and is recorded here rather than reproduced by
    special-casing the example.
    """
    # The stated start point is honoured.
    assert varga_d7(CANCER + 0.5) == "Capricorn"
    # And the arithmetic that follows from it.
    assert varga_d7(WORKED_LAGNA) == "Aquarius"


# -- D9, D10, D12 ---------------------------------------------------------


def test_navamsa_starts_from_the_movable_sign_of_the_trine():
    assert varga_d9(0.0 + 1) == "Aries"          # Aries, movable
    assert varga_d9(30.0 + 1) == "Capricorn"     # Taurus, fixed
    assert varga_d9(60.0 + 1) == "Libra"         # Gemini, dual
    assert varga_d9(90.0 + 1) == "Cancer"        # Cancer, movable


def test_dasamsa_reproduces_the_commentarys_taurus():
    """Cancer is even, so count from Pisces, the 9th; the third dasamsa."""
    assert varga_d10(WORKED_LAGNA) == "Taurus"


def test_dasamsa_counts_from_the_sign_itself_in_an_odd_rasi():
    assert varga_d10(0.0 + 1) == "Aries"


def test_dvadasamsa_counts_from_the_sign_in_every_rasi_alike():
    from src.engine.multitradition.jyotisha_varga import RASIS

    for base in (0.0, 30.0):
        idx = int(base // 30)
        assert varga_d12(base + 1) == RASIS[idx]
        assert varga_d12(base + 3) == RASIS[(idx + 1) % 12]


# -- D30, the unequal division -------------------------------------------


@pytest.mark.parametrize(
    "deg,lord",
    [(2, "Mars"), (7, "Saturn"), (14, "Jupiter"), (20, "Mercury"),
     (27, "Venus")],
)
def test_trimsamsa_arcs_in_an_odd_sign_are_5_5_8_7_5(deg, lord):
    assert varga_d30_lord(0.0 + deg) == lord


@pytest.mark.parametrize(
    "deg,lord",
    [(2, "Venus"), (7, "Mercury"), (15, "Jupiter"), (22, "Saturn"),
     (27, "Mars")],
)
def test_trimsamsa_reverses_in_an_even_sign(deg, lord):
    assert varga_d30_lord(30.0 + deg) == lord


def test_the_sun_and_moon_own_no_trimsamsa():
    lords = {varga_d30_lord(d) for d in range(0, 360)}
    assert "Sun" not in lords
    assert "Moon" not in lords


def test_the_worked_lagna_gives_mercury_in_the_trimsamsa():
    """8 degrees of Cancer, an even sign: the second arc, 5 to 12."""
    assert varga_d30_lord(WORKED_LAGNA) == "Mercury"


# -- the five-fold relation and vimsopaka --------------------------------


NAISARGIKA = {
    "Sun": {"friends": ["Moon", "Mars", "Jupiter"], "enemies": ["Venus", "Saturn"]},
    "Saturn": {"friends": ["Mercury", "Venus"], "enemies": ["Sun", "Moon", "Mars"]},
}


def test_a_graha_in_its_own_sign_is_svaksetra():
    assert five_fold_relation("Sun", "Sun", NAISARGIKA, {"Sun": 4}) == "svaksetra"


def test_the_compound_relation_needs_both_halves():
    """Natural friend plus temporal friend is adhimitra; plus enemy, only sama."""
    # Saturn is the Sun's natural enemy, but in the 3rd it is a temporal
    # friend, and the two cancel to neutrality rather than to enmity.
    assert five_fold_relation(
        "Sun", "Saturn", NAISARGIKA, {"Sun": 0, "Saturn": 2}
    ) == "sama"
    # The same natural enemy, temporally averted, sinks to adhisatru.
    assert five_fold_relation(
        "Sun", "Saturn", NAISARGIKA, {"Sun": 0, "Saturn": 5}
    ) == "adhisatru"
    # A natural friend in a temporally friendly house.
    assert five_fold_relation(
        "Sun", "Mars", NAISARGIKA, {"Sun": 0, "Mars": 2}
    ) == "adhimitra"
    # The same natural friend, temporally averted.
    assert five_fold_relation(
        "Sun", "Mars", NAISARGIKA, {"Sun": 0, "Mars": 5}
    ) == "sama"


def test_saptavargaja_returns_one_dignity_per_varga():
    got = saptavargaja_dignities(
        "Sun", WORKED_LAGNA, NAISARGIKA, {"Sun": 3}
    )
    assert len(got) == 7


def test_vimsopaka_totals_are_out_of_twenty():
    for scheme in VIMSOPAKA_SCHEMES:
        got = vimsopaka_bala(
            "Sun", WORKED_LAGNA, NAISARGIKA, {"Sun": 3}, scheme=scheme
        )
        assert 0.0 <= got["total_vishvas"] <= 20.0
        assert got["out_of"] == 20


def test_the_scheme_weights_sum_to_twenty():
    for scheme, weights in VIMSOPAKA_SCHEMES.items():
        assert sum(weights.values()) == 20, scheme


def test_only_the_schemes_whose_vargas_are_encoded_are_offered():
    """dasavarga and shodasavarga need the six vargas nobody has read yet."""
    assert set(VIMSOPAKA_SCHEMES) == {"shadvarga", "saptavarga"}
    with pytest.raises(KeyError):
        vimsopaka_bala("Sun", 0.0, NAISARGIKA, {"Sun": 0}, scheme="dasavarga")


def test_the_supplied_relation_convention_is_disclosed_on_every_result():
    got = vimsopaka_bala("Sun", WORKED_LAGNA, NAISARGIKA, {"Sun": 3})
    assert "configured_method" in got["relation_disclosure"]
    assert "adhimitra" in got["adhimitra_fork"]


def test_the_unmined_vargas_are_named_rather_than_quietly_absent():
    assert set(UNMINED_VARGAS) == {"D16", "D20", "D24", "D27", "D40", "D45"}
    computed = all_vargas(WORKED_LAGNA)
    for divisor in UNMINED_VARGAS:
        assert divisor not in computed
