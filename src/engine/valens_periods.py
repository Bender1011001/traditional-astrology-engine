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

  VI.5-6 (Kroll pp. 251-254) - the decennial cascade. Valens presents it as
      something he recovered himself, "cast aside because its points of entry
      are riddling".

The arithmetic of VI.5-6 is self-verifying, which is why it can be implemented
with confidence from a single reading: the seven planets' minor years sum to
129, and 129 months is exactly the 10-years-9-months major period VI.5 names.
Subdividing a parent period by (minor_years / 129) reproduces six of the seven
figures in Valens's own worked Saturn example to the day. The seventh
(Jupiter) is off by ~3 days against the transcription, which is far more
likely an OCR slip on the numeral than a different rule, given the other six.
That discrepancy is recorded rather than smoothed over.

Months are 30 days here, matching the 360-day year Valens uses for releasing
(confirmed at IV.10 by his own conversion table).
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


def _subdivide(parent_months: float, order: tuple[str, ...]) -> List[Dict[str, Any]]:
    """VI.6: split a period among the seven, each taking minor_years/129 of it.

    Verified against Valens's own Saturn example (parent = 30 months): six of
    the seven sub-periods reproduce his figures to the day.
    """
    out = []
    for planet in order:
        months = parent_months * VALENS_MINOR_YEARS[planet] / MINOR_YEARS_TOTAL
        whole_months = int(months)
        days = (months - whole_months) * DAYS_PER_MONTH
        out.append(
            {
                "planet": planet,
                "months_decimal": round(months, 6),
                "months": whole_months,
                "days": round(days, 2),
            }
        )
    return out


def decennial_cascade(
    *,
    sect_light: str,
    levels: int = 2,
    count: int = 3,
) -> Dict[str, Any]:
    """Valens VI.5-6, Kroll pp. 251-254. The 10-year-9-month cascade.

    Each major period runs 129 months (10y 9m) and is ruled by a planet in the
    Chaldean order. Within it, all seven planets take a sub-period proportional
    to their minor years. VI.6 calls a further subdivision of those sub-periods
    "the third subdivision"; `levels=3` produces it.

    CAVEAT, recorded rather than hidden: VI.5 says the sequence runs from the
    sect light, and that is what `sect_light` sets here - but the exact rule for
    which planet opens the cascade is the one part of this technique not
    confirmed by internal arithmetic the way the subdivision is. Treat the
    starting planet as configured, not verified, until VI.5's opening lines are
    read again. Everything downstream of the start is self-checking; the start
    itself is not.
    """
    if sect_light not in VALENS_MINOR_YEARS:
        raise ValueError(f"sect_light must be one of the seven, got {sect_light!r}")

    start = CHALDEAN_ORDER.index(sect_light)
    order_from_light = tuple(
        CHALDEAN_ORDER[(start + i) % 7] for i in range(7)
    )

    periods = []
    for i in range(int(count)):
        ruler = order_from_light[i % 7]
        entry: Dict[str, Any] = {
            "index": i,
            "ruler": ruler,
            "months": MAJOR_PERIOD_MONTHS,
            "years": round(MAJOR_PERIOD_MONTHS / 12.0, 4),
            "start_age": round(i * MAJOR_PERIOD_MONTHS / 12.0, 4),
        }
        if levels >= 2:
            subs = _subdivide(MAJOR_PERIOD_MONTHS, order_from_light)
            if levels >= 3:
                for sub in subs:
                    sub["sub_periods"] = _subdivide(
                        sub["months_decimal"], order_from_light
                    )
            entry["sub_periods"] = subs
        periods.append(entry)

    return {
        "technique": "Valens decennial cascade (VI.5-6)",
        "sect_light": sect_light,
        "order": list(order_from_light),
        "major_period_months": MAJOR_PERIOD_MONTHS,
        "major_period_label": "10 years 9 months",
        "periods": periods,
        "starting_planet_verified": False,
    }


def decennial_ruler_at_age(
    *, sect_light: str, age: float
) -> Dict[str, Any]:
    """Which planet rules a given age, at both cascade levels.

    Walks the cascade rather than using VI.7's arithmetical shortcut. That
    shortcut (reduce elapsed days by cycles of 129) was read but its exact
    arithmetic is not yet pinned down well enough to implement - see the notes.
    Walking gives the same answer without guessing at it.
    """
    months_elapsed = float(age) * 12.0
    major_index = int(months_elapsed // MAJOR_PERIOD_MONTHS)
    into_major = months_elapsed - major_index * MAJOR_PERIOD_MONTHS

    start = CHALDEAN_ORDER.index(sect_light)
    order_from_light = tuple(CHALDEAN_ORDER[(start + i) % 7] for i in range(7))

    major_ruler = order_from_light[major_index % 7]

    cursor = 0.0
    sub_ruler = None
    sub_start = 0.0
    for planet in order_from_light:
        span = MAJOR_PERIOD_MONTHS * VALENS_MINOR_YEARS[planet] / MINOR_YEARS_TOTAL
        if cursor <= into_major < cursor + span:
            sub_ruler = planet
            sub_start = cursor
            break
        cursor += span

    return {
        "age": float(age),
        "major_ruler": major_ruler,
        "major_index": major_index,
        "months_into_major": round(into_major, 4),
        "sub_ruler": sub_ruler,
        "months_into_sub": round(into_major - sub_start, 4) if sub_ruler else None,
        "starting_planet_verified": False,
    }
