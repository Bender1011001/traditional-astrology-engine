"""Jaimini, checked against the tradition's own worked charts.

Abhyankar prints fourteen karaka-kundalis and eight of them give
degrees-within-sign for every graha. Those, plus his Ranade and Lokur figures,
are the only independent checks the material offers, and they are what these
tests use. The rasi drsti table gets five of them - three from Ranade, two
from Lokur - and none of the five is a Parasari aspect, so the table cannot be
passing by accident.

The refusals are tested as hard as the computations. A pack that abstains and
an engine that quietly picks a default is worse than either alone: the number
looks sourced and is not.
"""

from __future__ import annotations

import pytest

from src.engine.multitradition.jaimini import (
    CHARA_DASA_UNDECIDED,
    DUAL,
    FIXED,
    MAX_DASA_YEARS,
    MOVABLE,
    RASIS,
    JaiminiChart,
    argala,
    arudha_pada,
    aspects_sign,
    atmakaraka,
    build,
    chara_dasa_lengths_refused,
    chara_dasa_sequence,
    chara_karakas,
    dasa_direction,
    graha_drsti,
    rasi_drsti,
    varnada,
)

# --- rasi drsti, against the worked charts -------------------------------


@pytest.mark.parametrize(
    "from_rasi,to_rasi",
    [
        # Ranade (para 117): Capricorn aspects Taurus and Leo; Aquarius
        # aspects Libra; Aries aspects Leo.
        ("Capricorn", "Taurus"),
        ("Capricorn", "Leo"),
        ("Aquarius", "Libra"),
        ("Aries", "Leo"),
        # Lokur (para 128): Aries aspects Leo; Cancer aspects Scorpio.
        ("Cancer", "Scorpio"),
    ],
)
def test_rasi_drsti_reproduces_abhyankars_worked_charts(from_rasi, to_rasi):
    assert aspects_sign(from_rasi, to_rasi), (
        f"{from_rasi} should aspect {to_rasi} per the worked chart"
    )


def test_a_movable_sign_aspects_three_fixed_signs():
    for rasi in MOVABLE:
        seen = rasi_drsti(rasi)
        assert len(seen) == 3
        assert all(r in FIXED for r in seen), seen


def test_a_fixed_sign_aspects_three_movable_signs():
    for rasi in FIXED:
        seen = rasi_drsti(rasi)
        assert len(seen) == 3
        assert all(r in MOVABLE for r in seen), seen


def test_a_dual_sign_aspects_the_other_three_dual_signs():
    for rasi in DUAL:
        seen = rasi_drsti(rasi)
        assert len(seen) == 3
        assert all(r in DUAL for r in seen)
        assert rasi not in seen, "a dual sign does not aspect itself"


def test_the_excluded_neighbour_is_really_excluded():
    """A movable sign skips the fixed sign immediately next to it."""
    assert "Taurus" not in rasi_drsti("Aries")
    assert "Leo" not in rasi_drsti("Cancer")
    # And a fixed sign skips the movable sign immediately behind it.
    assert "Aries" not in rasi_drsti("Taurus")
    assert "Cancer" not in rasi_drsti("Leo")


def test_rasi_drsti_is_not_the_parasari_scheme():
    """If these coincided the table would prove nothing."""
    # Parasari's universal aspect is the 7th; Jaimini's movable signs never
    # aspect their own opposite, which is a movable sign.
    for rasi in MOVABLE:
        opposite = RASIS[(RASIS.index(rasi) + 6) % 12]
        assert opposite not in rasi_drsti(rasi)


def test_a_graha_aspects_what_its_sign_aspects():
    """tannisthas ca tadvat."""
    assert graha_drsti("Capricorn") == rasi_drsti("Capricorn")


# --- chara karakas -------------------------------------------------------

# Patel (para 125): the only chart whose numbers discriminate the Rahu
# conventions. Saturn at 20 is Abhyankar's Atmakaraka; Rahu stands at 5.
PATEL = {
    "Saturn": 20.0, "Rahu": 5.0, "Sun": 12.0, "Moon": 8.0,
    "Mars": 3.0, "Mercury": 15.0, "Jupiter": 11.0, "Venus": 6.0,
}


def test_forward_counting_reproduces_abhyankars_patel_atmakaraka():
    assert atmakaraka(PATEL, scheme="eight", rahu_counting="forward") == "Saturn"


def test_excluding_rahu_also_reproduces_it():
    assert atmakaraka(PATEL, scheme="seven") == "Saturn"


def test_reverse_counting_contradicts_him_which_is_why_it_is_refuted():
    """30 - 5 = 25 would outrank Saturn at 20, and Abhyankar names Saturn."""
    assert atmakaraka(
        PATEL, scheme="eight", rahu_counting="reverse"
    ) == "Rahu"


def test_ranking_is_by_degree_within_sign_descending():
    ranked = chara_karakas(PATEL, scheme="eight")
    degrees = [k.degree_in_sign for k in ranked]
    assert degrees == sorted(degrees, reverse=True)
    assert ranked[0].graha == "Saturn"


def test_ketu_is_never_ranked_separately():
    """Rahu and Ketu hold the same degrees and count as one karaka."""
    with_ketu = dict(PATEL, Ketu=29.0)
    ranked = chara_karakas(with_ketu, scheme="eight")
    assert "Ketu" not in [k.graha for k in ranked]


# --- the refusals --------------------------------------------------------


def test_no_karaka_below_rank_one_is_titled_without_a_declared_scheme():
    """The fork changes which graha carries the father, the son and the kin."""
    ranked = chara_karakas(PATEL)  # scheme undeclared
    assert ranked[0].title == "Atmakaraka"
    assert ranked[0].title_certain
    for k in ranked[1:]:
        assert k.title is None
        assert not k.title_certain
        assert "fork" in k.note


def test_declaring_the_scheme_titles_everything():
    seven = chara_karakas(PATEL, scheme="seven")
    eight = chara_karakas(PATEL, scheme="eight")
    assert all(k.title for k in seven)
    assert all(k.title for k in eight)
    # And the fork really does move the titles.
    assert [k.title for k in seven] != [k.title for k in eight[:7]]


def test_the_seven_scheme_has_no_pitrkaraka_and_the_eight_scheme_does():
    seven = {k.title for k in chara_karakas(PATEL, scheme="seven")}
    eight = {k.title for k in chara_karakas(PATEL, scheme="eight")}
    assert "Pitrkaraka" not in seven
    assert "Pitrkaraka" in eight


def test_an_unknown_scheme_is_an_error_not_a_silent_default():
    with pytest.raises(ValueError):
        chara_karakas(PATEL, scheme="nine")


def test_chara_dasa_lengths_are_refused_with_their_reasons_named():
    got = chara_dasa_lengths_refused()
    assert got["output_policy"] == "refused"
    assert len(got["undecided_conventions"]) == len(CHARA_DASA_UNDECIDED)
    assert str(MAX_DASA_YEARS) in got["what_is_settled"]


def test_the_dasa_sequence_is_given_even_though_the_lengths_are_not():
    """The direction is settled; only the period lengths are not."""
    seq = chara_dasa_sequence("Aries")
    assert len(seq) == 12
    assert len(set(seq)) == 12
    assert seq[0] == "Aries"


def test_varnada_is_marked_displayable_but_not_delineable():
    got = varnada("Aries", "Leo")
    assert got["output_policy"] == "displayable_figure_only"
    assert "cannot explain" in got["why"]
    assert got["rasi"] in RASIS


# --- dasa direction ------------------------------------------------------


def test_odd_signs_run_forward_and_even_signs_reverse():
    assert dasa_direction("Aries") == "forward"
    assert dasa_direction("Gemini") == "forward"
    assert dasa_direction("Cancer") == "reverse"
    assert dasa_direction("Virgo") == "reverse"


def test_the_four_fixed_signs_suspend_the_parity_rule():
    """Both witnesses agree that 'not so in some cases' means these four."""
    assert dasa_direction("Leo") == "reverse"       # odd, but fixed
    assert dasa_direction("Aquarius") == "reverse"  # odd, but fixed
    assert dasa_direction("Taurus") == "forward"    # even, but fixed
    assert dasa_direction("Scorpio") == "forward"   # even, but fixed


# --- arudha padas --------------------------------------------------------


def test_arudha_counts_as_far_again_from_the_lord():
    """Lagna Aries, lord Mars in Gemini: 3 signs on, 3 more gives Leo."""
    assert arudha_pada("Aries", "Gemini")[0] == "Leo"


def test_a_lord_in_the_fourth_puts_the_pada_in_the_fourth():
    pada, exception = arudha_pada("Aries", "Cancer")
    assert pada == "Cancer"
    assert exception == "lord in the 4th"


def test_a_lord_in_the_seventh_puts_the_pada_in_the_tenth():
    pada, exception = arudha_pada("Aries", "Libra")
    assert pada == "Capricorn"
    assert exception == "lord in the 7th"


# --- argala --------------------------------------------------------------


def test_argala_forms_from_the_fourth_second_and_eleventh():
    graha_rasis = {"Jupiter": "Cancer", "Venus": "Taurus", "Mars": "Aquarius"}
    got = argala("Aries", graha_rasis)
    houses = {a["from_house"] for a in got["argalas"]}
    assert houses == {4, 2, 11}


def test_an_obstruction_by_fewer_grahas_does_not_hold():
    """na nyuna vibalas ca."""
    graha_rasis = {
        "Jupiter": "Cancer", "Venus": "Cancer",   # two in the 4th
        "Saturn": "Capricorn",                     # one in the 10th
    }
    got = argala("Aries", graha_rasis)
    fourth = next(a for a in got["argalas"] if a["from_house"] == 4)
    assert fourth["obstruction_holds"] is False


def test_an_equal_count_is_undecided_rather_than_settled_by_number():
    """The commentary is explicit that strength still decides, so not False."""
    graha_rasis = {"Jupiter": "Cancer", "Saturn": "Capricorn"}
    got = argala("Aries", graha_rasis)
    fourth = next(a for a in got["argalas"] if a["from_house"] == 4)
    assert fourth["obstruction_holds"] is None


def test_the_third_house_argala_reports_both_readings_of_bhuyasa():
    graha_rasis = {"Sun": "Gemini", "Mars": "Gemini", "Saturn": "Gemini"}
    got = argala("Aries", graha_rasis)["third_house_argala"]
    assert got["forms_on_three_or_more"] is True
    assert got["forms_on_outnumbering"] is True
    graha_rasis = {"Sun": "Gemini", "Jupiter": "Gemini"}
    got = argala("Aries", graha_rasis)["third_house_argala"]
    assert got["forms_on_three_or_more"] is False
    assert got["forms_on_outnumbering"] is False


def test_both_disputed_forks_are_carried_on_the_result():
    got = argala("Aries", {"Jupiter": "Cancer"})
    assert "nidhyatuh" in got["target_fork"]
    assert "does not say which obstructs which" in got["pairing_fork"]


# --- assembly ------------------------------------------------------------


def _chart(**kw) -> JaiminiChart:
    base = dict(
        lagna_rasi="Virgo",
        graha_rasis={
            "Sun": "Cancer", "Moon": "Cancer", "Mars": "Gemini",
            "Mercury": "Virgo", "Jupiter": "Capricorn", "Venus": "Leo",
            "Saturn": "Pisces",
        },
        degrees_in_sign={
            "Sun": 27.3, "Moon": 13.2, "Mars": 4.1, "Mercury": 1.9,
            "Jupiter": 20.5, "Venus": 8.8, "Saturn": 11.0,
        },
    )
    base.update(kw)
    return JaiminiChart(**base)


def test_build_produces_the_karaka_kundali_from_the_atmakarakas_sign():
    got = build(_chart())
    assert got["karaka_kundali_first_house"] == "Cancer"  # the Sun at 27.3
    assert got["karaka_kundali"]["house_1"] == "Cancer"


def test_build_withholds_the_special_lagnas_when_sunrise_is_absent():
    got = build(_chart())
    assert got["special_lagnas"] is None
    assert "sunrise" in got["special_lagnas_withheld"]


def test_build_computes_the_special_lagnas_when_sunrise_is_supplied():
    got = build(_chart(sun_longitude=117.3, sunrise_to_birth_hours=1.5))
    assert set(got["special_lagnas"]) == {
        "Hora Lagna", "Ghatika Lagna", "Bhava Lagna"
    }
    assert "configured_method" in got["special_lagna_origin_fork"]
    assert got["varnada"]["output_policy"] == "displayable_figure_only"


def test_the_ghatika_lagna_moves_fastest_and_the_bhava_lagna_slowest():
    got = build(_chart(sun_longitude=0.0, sunrise_to_birth_hours=2.0))
    lagnas = got["special_lagnas"]
    assert lagnas["Ghatika Lagna"]["longitude"] > (
        lagnas["Hora Lagna"]["longitude"]
    )
    assert lagnas["Hora Lagna"]["longitude"] > (
        lagnas["Bhava Lagna"]["longitude"]
    )
