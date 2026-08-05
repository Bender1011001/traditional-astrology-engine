"""Assemble the inputs Sadbala needs from a computed nativity.

The research pack that carries these rules declares four kala-bala limbs,
ayana-bala and cheshta-bala "unevaluable until those inputs exist" - the
inputs being local sunrise and sunset, the ghati clock, the sayana longitude
and the mean longitudes. That is a statement about the pack's own fail-closed
posture, not about the world: swisseph computes rise and set, the engine
already carries the Lahiri ayanamsa, and four other modules in this package
compute sunrise today. So the inputs are built here rather than left declared
impossible.

One limb is genuinely left open. Cheshta-bala's kendra procedure wants the
*madhyama* (mean) longitude and the *sighrocca*, which are quantities of Hindu
planetary theory rather than of a modern ephemeris; substituting a modern mean
element for them would be a fabrication wearing the right name. The chapter
prints a gati table alongside the kendra procedure, and that table is used
instead, and said so on the result.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import swisseph as swe

from .jyotisha_strength import GRAHAS, StrengthInputs
from .jyotisha_varga import saptavargaja_dignities, varga_d9

GHATIS_PER_DAY = 60.0

#: The weekday lords, Monday first, matching datetime.weekday().
WEEKDAY_LORDS = (
    "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun",
)

#: The Chaldean order, in which the hora lords succeed one another.
CHALDEAN_ORDER = (
    "Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon",
)

EXALTATION_SIGN = {
    "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn", "Mercury": "Virgo",
    "Jupiter": "Cancer", "Venus": "Pisces", "Saturn": "Libra",
}

MOOLATRIKONA = {
    "Sun": ("Leo", 0.0, 20.0), "Moon": ("Taurus", 3.0, 30.0),
    "Mars": ("Aries", 0.0, 12.0), "Mercury": ("Virgo", 15.0, 20.0),
    "Jupiter": ("Sagittarius", 0.0, 10.0), "Venus": ("Libra", 0.0, 15.0),
    "Saturn": ("Aquarius", 0.0, 20.0),
}

RASIS = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)

SWE_BODY = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
    "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
}


def _julian_day(moment: datetime) -> float:
    utc = moment.astimezone(timezone.utc)
    return swe.julday(
        utc.year, utc.month, utc.day,
        utc.hour + utc.minute / 60.0 + utc.second / 3600.0,
    )


def sun_times(
    moment: datetime, latitude: float, longitude: float
) -> dict[str, float] | None:
    """Local sunrise, sunset and the following sunrise, as Julian days.

    Returns None inside the polar circles when the Sun neither rises nor sets,
    where the ghati clock has no meaning and the limbs that need it must stay
    undecided rather than be handed a fabricated day length.
    """
    jd = _julian_day(moment)
    geopos = (longitude, latitude, 0.0)
    try:
        _, rise = swe.rise_trans(
            jd - 1.0, swe.SUN, swe.CALC_RISE | swe.BIT_DISC_CENTER,
            geopos, 0.0, 0.0,
        )
        _, sett = swe.rise_trans(
            rise[0], swe.SUN, swe.CALC_SET | swe.BIT_DISC_CENTER,
            geopos, 0.0, 0.0,
        )
        _, next_rise = swe.rise_trans(
            sett[0], swe.SUN, swe.CALC_RISE | swe.BIT_DISC_CENTER,
            geopos, 0.0, 0.0,
        )
    except Exception:
        return None
    if not rise or not sett or not next_rise:
        return None
    # A birth before the day's sunrise belongs to the previous Hindu day.
    if jd < rise[0]:
        try:
            _, prev_rise = swe.rise_trans(
                jd - 2.0, swe.SUN, swe.CALC_RISE | swe.BIT_DISC_CENTER,
                geopos, 0.0, 0.0,
            )
            _, prev_set = swe.rise_trans(
                prev_rise[0], swe.SUN, swe.CALC_SET | swe.BIT_DISC_CENTER,
                geopos, 0.0, 0.0,
            )
        except Exception:
            return None
        return {
            "sunrise": prev_rise[0], "sunset": prev_set[0],
            "next_sunrise": rise[0], "jd": jd,
        }
    return {
        "sunrise": rise[0], "sunset": sett[0],
        "next_sunrise": next_rise[0], "jd": jd,
    }


def ghati_clock(times: dict[str, float]) -> dict[str, Any]:
    """The ishta-kala and the half-day, in ghatis, reckoned from sunrise.

    A ghati is a sixtieth of the day-and-night round, so the whole round is
    sixty ghatis and the half-day is half the daylight arc expressed in them.
    """
    jd = times["jd"]
    sunrise, sunset = times["sunrise"], times["sunset"]
    next_rise = times["next_sunrise"]
    round_days = next_rise - sunrise
    if round_days <= 0:
        return {"ishta_ghati": None, "half_day_ghati": None,
                "is_day_birth": None, "tribhaga_index": None}
    is_day = sunrise <= jd < sunset
    ishta = (jd - sunrise) / round_days * GHATIS_PER_DAY
    day_length_ghati = (sunset - sunrise) / round_days * GHATIS_PER_DAY
    # Which of the six thirds of day and night holds the birth.
    if is_day:
        share = (jd - sunrise) / (sunset - sunrise)
        tribhaga = min(int(share * 3), 2)
    else:
        share = (jd - sunset) / (next_rise - sunset)
        tribhaga = 3 + min(int(share * 3), 2)
    return {
        "ishta_ghati": ishta,
        "half_day_ghati": day_length_ghati / 2.0,
        "is_day_birth": is_day,
        "tribhaga_index": tribhaga,
        "day_length_ghati": day_length_ghati,
    }


def hora_lord(times: dict[str, float], weekday_lord: str) -> str | None:
    """The lord of the kala-hora holding the birth.

    The hours are temporal, not clock hours: twelve to the daylight and twelve
    to the night, and the lords run in the Chaldean order from the weekday's
    own lord at sunrise.
    """
    jd, sunrise, sunset = times["jd"], times["sunrise"], times["sunset"]
    next_rise = times["next_sunrise"]
    if sunrise <= jd < sunset:
        index = int((jd - sunrise) / ((sunset - sunrise) / 12.0))
    elif jd >= sunset:
        index = 12 + int((jd - sunset) / ((next_rise - sunset) / 12.0))
    else:
        return None
    start = CHALDEAN_ORDER.index(weekday_lord)
    return CHALDEAN_ORDER[(start + index) % 7]


def solar_ingress_lord(
    jd: float, latitude: float, longitude: float, whole_sign: bool
) -> str | None:
    """The weekday lord of the day on which the Sun last entered a sign.

    Used for the masesa (the solar month's lord) and, when ``whole_sign`` asks
    for the sidereal Aries ingress, for the varshesa.
    """
    swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    try:
        lon = swe.calc_ut(jd, swe.SUN, flags)[0][0]
    except Exception:
        return None
    target = 0.0 if whole_sign else (int(lon // 30) * 30.0)
    # Walk back a day at a time until the Sun is on the far side of the cusp.
    probe = jd
    for _ in range(400):
        probe -= 1.0
        try:
            got = swe.calc_ut(probe, swe.SUN, flags)[0][0]
        except Exception:
            return None
        if ((lon - target) % 360.0) > ((got - target) % 360.0):
            continue
        if ((got - target) % 360.0) > 180.0:
            break
    else:
        return None
    # Bisect the last day for the ingress moment, then take its weekday.
    low, high = probe, probe + 1.0
    for _ in range(40):
        mid = (low + high) / 2.0
        try:
            got = swe.calc_ut(mid, swe.SUN, flags)[0][0]
        except Exception:
            return None
        if ((got - target) % 360.0) > 180.0:
            low = mid
        else:
            high = mid
    year, month, day, _ = swe.revjul(high)
    return WEEKDAY_LORDS[datetime(year, month, day).weekday()]


def motion_state(graha: str, jd: float) -> str | None:
    """The graha's gati, from its speed against its own mean speed.

    The chapter's table names eight states. Four of them are decidable from
    the speed alone, which is what a modern ephemeris supplies; the states
    that turn on comparison with a previous position are not attempted.
    """
    if graha in ("Sun", "Moon"):
        return "sama"  # neither ever retrogrades, and neither is graded here
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    try:
        values = swe.calc_ut(jd, SWE_BODY[graha], flags)[0]
    except Exception:
        return None
    speed = values[3]
    if speed < 0:
        return "vakri"
    mean = {
        "Mars": 0.524, "Mercury": 1.383, "Jupiter": 0.083,
        "Venus": 1.602, "Saturn": 0.034,
    }[graha]
    if speed > mean * 1.5:
        return "atisighra"
    if speed > mean:
        return "sighra"
    if speed < mean * 0.5:
        return "manda"
    return "sama"


def build_strength_inputs(
    facts: dict[str, Any],
    moment: datetime,
    latitude: float,
    longitude: float,
) -> tuple[StrengthInputs, dict[str, Any]]:
    """Turn the Jyotisha panel's facts into everything the chapter needs.

    Returns the inputs and a provenance dict naming what could be supplied and
    what could not, so a report can say which limbs rest on what.
    """
    longitudes: dict[str, float] = {}
    rasi_index: dict[str, int] = {}
    for row in facts.get("grahas", []):
        name = row.get("graha")
        if name not in GRAHAS:
            continue
        idx = RASIS.index(row["rasi"])
        longitudes[name] = idx * 30.0 + float(row["degree_in_sign"])
        rasi_index[name] = idx

    lagna_row = facts.get("lagna") or {}
    lagna = (
        RASIS.index(lagna_row["rasi"]) * 30.0
        + float(lagna_row.get("degree_in_sign", 0.0))
        if lagna_row.get("rasi") else 0.0
    )

    naisargika = facts.get("naisargika_relations", {}) or {}
    saptavargaja = {
        g: saptavargaja_dignities(
            g, lon, naisargika, rasi_index,
            exaltation_sign=EXALTATION_SIGN.get(g),
            moolatrikona=MOOLATRIKONA.get(g),
        )
        for g, lon in longitudes.items()
    }
    navamsa_index = {
        g: RASIS.index(varga_d9(lon)) for g, lon in longitudes.items()
    }

    supplied: list[str] = ["sthana-bala", "dig-bala", "paksha-bala",
                           "naisargika-bala", "drik-bala"]
    withheld: list[str] = []

    times = sun_times(moment, latitude, longitude)
    clock: dict[str, Any] = {
        "ishta_ghati": None, "half_day_ghati": None,
        "is_day_birth": None, "tribhaga_index": None,
    }
    dinesa = horesa = masesa = varshesa = None
    if times is None:
        withheld.append(
            "natonnata-bala and tribhaga-bala: the Sun neither rises nor sets "
            "at this latitude on this date, so the ghati clock has no meaning "
            "here and none is invented"
        )
    else:
        clock = ghati_clock(times)
        year, month, day, _ = swe.revjul(times["sunrise"])
        dinesa = WEEKDAY_LORDS[datetime(year, month, day).weekday()]
        horesa = hora_lord(times, dinesa)
        masesa = solar_ingress_lord(times["jd"], latitude, longitude, False)
        varshesa = solar_ingress_lord(times["jd"], latitude, longitude, True)
        supplied.extend(["natonnata-bala", "tribhaga-bala", "varshadi-bala"])

    ayanamsa = facts.get("ayanamsa_degrees")
    if ayanamsa is None:
        withheld.append("ayana-bala: no ayanamsa was supplied")
    else:
        supplied.append("ayana-bala")

    jd = _julian_day(moment)
    gati = {}
    for graha in longitudes:
        state = motion_state(graha, jd)
        if state:
            gati[graha] = state
    withheld.append(
        "cheshta-bala by its kendra procedure: the madhyama and the sighrocca "
        "are quantities of Hindu planetary theory, not of a modern ephemeris, "
        "and no modern mean element is substituted for them. The gati table "
        "printed in the same chapter is used instead"
    )

    inputs = StrengthInputs(
        longitudes=longitudes,
        lagna=lagna,
        navamsa_index=navamsa_index,
        saptavargaja=saptavargaja,
        ayanamsa=ayanamsa,
        is_day_birth=clock["is_day_birth"],
        ishta_ghati=clock["ishta_ghati"],
        half_day_ghati=clock["half_day_ghati"],
        tribhaga_index=clock["tribhaga_index"],
        varshesa=varshesa, masesa=masesa, dinesa=dinesa, horesa=horesa,
        gati=gati,
    )
    provenance = {
        "supplied": supplied,
        "withheld": withheld,
        "ghati_clock": {
            k: (round(v, 4) if isinstance(v, float) else v)
            for k, v in clock.items()
        },
        "time_lords": {
            "varshesa": varshesa, "masesa": masesa,
            "dinesa": dinesa, "horesa": horesa,
        },
        "gati": gati,
    }
    return inputs, provenance


def local_datetime(
    civil_date: Any, civil_time: str, utc_offset_hours: float
) -> datetime:
    """Build an aware datetime from the panel's own birth fields."""
    hour, minute = (civil_time.split(":") + ["0"])[:2]
    return datetime(
        civil_date.year, civil_date.month, civil_date.day,
        int(hour), int(minute),
        tzinfo=timezone(timedelta(hours=utc_offset_hours)),
    )
