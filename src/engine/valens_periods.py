"""Valens Book V-VI period techniques, read from the Kroll 1908 Greek.

Two techniques live here. Both were found by reading Books V and VI directly,
and neither existed in the engine before that reading.

  V.2 (Kroll p. 210) - the climacteric YEAR. Profect one sign per year from the
      ascendant; if the profected sign is the sign of the pre-natal syzygy, or
      its square or opposition, the year is "climacteric and disturbed",
      especially when transiting Saturn is in one of the four cadent places.

      This is NOT III.15. That one derives a climacteric PERIODICITY from the
      figure a malefic throws at the Lot of Fortune - a static natal figure
      naming an interval. This one names a specific year, from profection and a
      transit. They share only the word.

VI.5-6's decennial cascade was ALSO read this session and is deliberately NOT
implemented here - `src/engine/decennials.py` already had it, and had it better:
it resolves the starting planet by zodiacal order from the Ascendant (the one
piece a fresh reading left unverified) and advances by real calendar months
rather than flat 30-day months. Building a second copy was a mistake, caught by
running the result against live output. What the reading did contribute is the
CITATION - see docs/sources/valens_greek_notes.md.

The minor years are kept below because V.2 shares nothing with them but they
document the 129 identity that makes the decennial period self-checking.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .models import Sign

# Valens's minor years (ἐλάχιστοι χρόνοι). Their sum is 129, and 129 months is
# the 10-year-9-month major period of VI.5 - the two facts are the same fact.
VALENS_MINOR_YEARS: Dict[str, int] = {
    "Saturn": 30,
    "Jupiter": 12,
    "Mars": 15,
    "Sun": 19,
    "Venus": 8,
    "Mercury": 20,
    "Moon": 25,
}

MINOR_YEARS_TOTAL = sum(VALENS_MINOR_YEARS.values())  # 129

# The order Valens hands the sub-periods round in his own VI.6 worked example:
# Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon - the descending Chaldean
# order. Read off the example itself, not assumed from convention.
CHALDEAN_ORDER: tuple[str, ...] = (
    "Saturn",
    "Jupiter",
    "Mars",
    "Sun",
    "Venus",
    "Mercury",
    "Moon",
)

DAYS_PER_MONTH = 30.0
MAJOR_PERIOD_MONTHS = float(MINOR_YEARS_TOTAL)  # 129 months = 10y 9m

_SIGNS: List[Sign] = list(Sign)


def _sign_index(longitude: float) -> int:
    return int((longitude % 360.0) / 30.0) % 12


def _sign_at(longitude: float) -> Sign:
    return _SIGNS[_sign_index(longitude)]


def climacteric_year(
    *,
    ascendant_sign: Sign,
    prenatal_syzygy_longitude: float,
    age: int,
    transiting_saturn_longitude: Optional[float] = None,
) -> Dict[str, Any]:
    """Valens V.2, Kroll p. 210. Is this year of life climacteric?

    "One must always release the years from the ascending sign. If the year so
    brought down terminates in the sign of the conjunction or full moon, or in
    their squares or oppositions, the year is climacteric and disturbed -
    especially if, these conditions holding, transiting Saturn is also found in
    one of the four cadent places from the nativity."

    Returns the finding and the reason for it. A year that does not meet the
    condition is reported as not meeting it; the function never grades severity
    beyond the aggravating Saturn witness Valens himself names.
    """
    profected = _SIGNS[(_SIGNS.index(ascendant_sign) + int(age)) % 12]
    syzygy_sign = _sign_at(prenatal_syzygy_longitude)

    separation = (_SIGNS.index(profected) - _SIGNS.index(syzygy_sign)) % 12
    figure = {
        0: "the syzygy sign itself",
        3: "square to the syzygy",
        6: "opposite the syzygy",
        9: "square to the syzygy",
    }.get(separation)

    is_climacteric = figure is not None

    # The aggravating witness: transiting Saturn in a cadent place, counted
    # whole-sign from the natal ascendant. Cadent = houses 3, 6, 9, 12, which
    # are sign-offsets 2, 5, 8, 11.
    saturn_cadent = False
    saturn_house: Optional[int] = None
    if transiting_saturn_longitude is not None:
        offset = (_sign_index(transiting_saturn_longitude) - _SIGNS.index(ascendant_sign)) % 12
        saturn_house = offset + 1
        saturn_cadent = offset in (2, 5, 8, 11)

    return {
        "age": int(age),
        "profected_sign": profected.value,
        "syzygy_sign": syzygy_sign.value,
        "syzygy_longitude": round(float(prenatal_syzygy_longitude), 4),
        "figure_to_syzygy": figure,
        "is_climacteric": is_climacteric,
        "saturn_transit_house": saturn_house,
        "saturn_in_cadent_place": saturn_cadent,
        "aggravated": bool(is_climacteric and saturn_cadent),
    }


def climacteric_years_in_range(
    *,
    ascendant_sign: Sign,
    prenatal_syzygy_longitude: float,
    start_age: int,
    end_age: int,
) -> List[Dict[str, Any]]:
    """Every climacteric year in an age range, by the V.2 rule.

    Saturn is not consulted here - its position is a per-year transit and the
    caller supplies it if wanted. This returns the profection-and-syzygy
    condition alone, which is the part that is fixed at birth.
    """
    found = []
    for age in range(int(start_age), int(end_age) + 1):
        result = climacteric_year(
            ascendant_sign=ascendant_sign,
            prenatal_syzygy_longitude=prenatal_syzygy_longitude,
            age=age,
        )
        if result["is_climacteric"]:
            found.append(result)
    return found
