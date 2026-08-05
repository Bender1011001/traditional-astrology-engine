"""Sadbala and Ashtakavarga, after the Subodhini recension of BPHS (1899).

Until this module existed the Jyotisha track held thousands of delineation
cells from four authors and no way to weigh any of them. That was not a
decorative gap. BPHS uttara 2.44-45 states the arbiter in as many words -
among the grahas causing a yoga, *the strongest of them is the one that gives
its result* - so a composer that lists every detected yoga side by side has not
executed the rule the text supplies. Strength is how the tradition chooses.

Two things about this implementation are load-bearing:

**Units.** Every strength here is carried in VIRUPAS and rendered in rupas.
The 1899 printing writes strengths as a sexagesimal triple whose leading place
is the rupa (60 virupas), so the Sun's naisargika-bala prints as ``1|0|0``.
Reading the leading place as virupas is wrong by a factor of sixty throughout,
and the error is invisible because the numbers still look plausible.

**Bindu means the blank.** In this recension *karana/bindu* is the dot standing
for nought and *sthana/rekha* is the scored mark. Much popular writing has this
exactly backwards, and the chapter lists the blanks first. This module stores
rekha counts and never uses the word bindu unqualified.

Where this recension differs from the modern handbooks it is followed, not
normalised: the saptavargaja series is 45/30/20/15/10/4/2 rather than the
handbooks' halving series, the Moon's paksha-bala is not doubled, kala-bala
has four limbs rather than six, and the required minima group the seven grahas
into three classes instead of giving each its own figure. Each divergence is
recorded on the result so a report can name its recension.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

GRAHAS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
REFERENCE_POINTS = (*GRAHAS, "Lagna")

RASIS = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)

RUPA_IN_VIRUPAS = 60.0

# -- sexagesimal notation ------------------------------------------------


def to_virupas(text: str) -> float:
    """Read the printing's ``rupa|virupa|sixtieth`` triple as virupas."""
    parts = [float(p) for p in text.split("|")]
    total = parts[0] * RUPA_IN_VIRUPAS
    for i, p in enumerate(parts[1:], start=0):
        total += p / (60.0**i)
    return total


def as_rupas(virupas: float) -> str:
    """Render virupas back into the printing's triple, e.g. ``9|41|14``."""
    neg = virupas < 0
    v = abs(virupas)
    rupa = int(v // RUPA_IN_VIRUPAS)
    rem = v - rupa * RUPA_IN_VIRUPAS
    vir = int(rem)
    sixtieth = int(round((rem - vir) * 60))
    if sixtieth == 60:  # carry, so 4|59|60 never prints
        sixtieth, vir = 0, vir + 1
    if vir == 60:
        vir, rupa = 0, rupa + 1
    return f"{'-' if neg else ''}{rupa}|{vir}|{sixtieth:02d}"


def rasi_deg_to_degrees(text: str) -> float:
    """Read ``rasi|deg|min|sec`` (or ``rasi|deg|min``) as absolute degrees."""
    parts = [float(p) for p in text.split("|")]
    total = parts[0] * 30.0
    for i, p in enumerate(parts[1:]):
        total += p / (60.0**i)
    return total % 360.0


# -- the tables the text prints ------------------------------------------

NAISARGIKA_BALA = {
    "Sun": 60.0, "Moon": 51.0, "Mars": 17.0, "Mercury": 26.0,
    "Jupiter": 34.0, "Venus": 43.0, "Saturn": 9.0,
}

#: Sthana-bala component 2. This recension's own series, NOT the handbooks'.
SAPTAVARGAJA_VIRUPAS = {
    "uccha": 100.0, "moolatrikona": 45.0, "svaksetra": 30.0,
    "adhimitra": 20.0, "mitra": 15.0, "sama": 10.0,
    "satru": 4.0, "adhisatru": 2.0,
}

#: The arcs the commentary states for each graha's moolatrikona.
MOOLATRIKONA = {
    "Sun": ("Leo", 0.0, 20.0), "Moon": ("Taurus", 3.0, 30.0),
    "Mars": ("Aries", 0.0, 12.0), "Mercury": ("Virgo", 15.0, 20.0),
    "Jupiter": ("Sagittarius", 0.0, 10.0), "Venus": ("Libra", 0.0, 15.0),
    "Saturn": ("Aquarius", 0.0, 20.0),
}

EXALTATION_DEGREE = {
    "Sun": 10.0, "Moon": 33.0, "Mars": 298.0, "Mercury": 165.0,
    "Jupiter": 95.0, "Venus": 357.0, "Saturn": 200.0,
}

DOMICILE = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

#: Dig-bala: the bhava each graha is subtracted FROM (its weak point).
DIGBALA_WEAK_BHAVA = {
    "Sun": 4, "Mars": 4, "Jupiter": 7, "Mercury": 7,
    "Saturn": 1, "Moon": 10, "Venus": 10,
}

#: Kala-bala limb 1. Mercury is exempt: always sixty, in every case.
NATONNATA_DAY_STRONG = ("Sun", "Venus", "Jupiter")
NATONNATA_NIGHT_STRONG = ("Mars", "Moon", "Saturn")

#: Kala-bala limb 3: the lords of the six thirds of day and night, in order.
TRIBHAGA_LORDS = (
    "Mercury", "Sun", "Saturn",   # the three parts of the day
    "Moon", "Venus", "Mars",      # the three parts of the night
)

VARSHADI_VIRUPAS = {"year": 15.0, "month": 30.0, "day": 45.0, "hora": 60.0}

#: Ayana-bala's dhruvanka khandas, applied to successive 30-degree segments.
AYANA_KHANDAS = (45.0, 33.0, 12.0)
AYANA_REVERSED = ("Moon", "Saturn")

#: Cheshta-bala's gati table, the limb evaluable without mean longitudes.
GATI_BALA_VIRUPAS = {
    "vakri": 60.0, "atisighra": 30.0, "sighra": 45.0, "sama": 30.0,
    "manda": 15.0, "alpagati": 7.5, "astangata": 15.0,
}

#: Sadbala's required minima. Three classes, not seven figures - see the
#: divergence note: the modern handbooks disagree, and a product that says
#: "BPHS calls a graha strong above N" must name which recension it means.
REQUIRED_MINIMA = {
    "Sun": 392.0, "Mercury": 392.0, "Jupiter": 392.0,
    "Moon": 353.0, "Venus": 353.0,
    "Mars": 253.0, "Saturn": 253.0,
}

MINIMA_CLASS = {
    "Sun": "Sun/Mercury/Jupiter", "Mercury": "Sun/Mercury/Jupiter",
    "Jupiter": "Sun/Mercury/Jupiter", "Moon": "Moon/Venus",
    "Venus": "Moon/Venus", "Mars": "Mars/Saturn", "Saturn": "Mars/Saturn",
}

# -- Ashtakavarga ---------------------------------------------------------

#: For each varga, which house-offsets each reference point gives a rekha to.
#: Offsets count the reference point's own rasi as 1.
BHINNA_TABLES: dict[str, dict[str, tuple[int, ...]]] = {
    "Sun": {
        "Sun": (1, 2, 4, 7, 8, 9, 10, 11),
        "Moon": (3, 6, 10, 11),
        "Mars": (1, 2, 4, 7, 8, 9, 10, 11),
        "Mercury": (3, 5, 6, 9, 10, 11, 12),
        "Jupiter": (5, 6, 9, 11),
        "Venus": (6, 7, 12),
        "Saturn": (1, 2, 4, 7, 8, 9, 10, 11),
        "Lagna": (3, 4, 6, 10, 11, 12),
    },
    "Moon": {
        "Sun": (3, 6, 7, 8, 10, 11),
        "Moon": (1, 3, 6, 7, 9, 10, 11),
        "Mars": (2, 3, 5, 6, 10, 11),
        "Mercury": (1, 3, 4, 5, 7, 8, 10, 11),
        "Jupiter": (1, 2, 4, 7, 8, 10, 11),
        "Venus": (3, 4, 5, 7, 9, 10, 11),
        "Saturn": (3, 5, 6, 11),
        "Lagna": (3, 6, 10, 11),
    },
    "Mars": {
        "Sun": (3, 5, 6, 10, 11),
        "Moon": (3, 6, 11),
        "Mars": (1, 2, 4, 7, 8, 10, 11),
        "Mercury": (3, 5, 6, 11),
        "Jupiter": (6, 10, 11, 12),
        "Venus": (6, 8, 11, 12),
        "Saturn": (1, 4, 7, 8, 9, 10, 11),
        "Lagna": (1, 3, 6, 10, 11),
    },
    "Mercury": {
        "Sun": (5, 6, 9, 11, 12),
        "Moon": (2, 4, 6, 8, 10, 11),
        "Mars": (1, 2, 4, 7, 8, 9, 10, 11),
        "Mercury": (1, 3, 5, 6, 9, 10, 11, 12),
        "Jupiter": (6, 8, 11, 12),
        "Venus": (1, 2, 3, 4, 5, 8, 9, 11),
        "Saturn": (1, 2, 4, 7, 8, 9, 10, 11),
        "Lagna": (1, 2, 4, 6, 8, 10, 11),
    },
    "Jupiter": {
        "Sun": (1, 2, 3, 4, 7, 8, 9, 10, 11),
        "Moon": (2, 5, 7, 9, 11),
        "Mars": (1, 2, 4, 7, 8, 10, 11),
        "Mercury": (1, 2, 4, 5, 6, 9, 10, 11),
        "Jupiter": (1, 2, 3, 4, 7, 8, 10, 11),
        "Venus": (2, 5, 6, 9, 10, 11),
        "Saturn": (3, 5, 6, 12),
        "Lagna": (1, 2, 4, 5, 6, 7, 9, 10, 11),
    },
    "Venus": {
        "Sun": (8, 11, 12),
        "Moon": (1, 2, 3, 4, 5, 8, 9, 11, 12),
        "Mars": (3, 4, 6, 9, 11, 12),
        "Mercury": (3, 5, 6, 9, 11),
        "Jupiter": (5, 8, 9, 10, 11),
        "Venus": (1, 2, 3, 4, 5, 8, 9, 10, 11),
        "Saturn": (3, 4, 5, 8, 9, 10, 11),
        "Lagna": (1, 2, 3, 4, 5, 8, 9, 11),
    },
    "Saturn": {
        "Sun": (1, 2, 4, 7, 8, 10, 11),
        "Moon": (3, 6, 11),
        "Mars": (3, 5, 6, 10, 11, 12),
        "Mercury": (6, 8, 9, 10, 11, 12),
        "Jupiter": (5, 6, 11, 12),
        "Venus": (6, 11, 12),
        "Saturn": (3, 5, 6, 11),
        "Lagna": (1, 3, 4, 6, 10, 11),
    },
    "Lagna": {
        "Sun": (3, 4, 6, 10, 11, 12),
        "Moon": (3, 6, 10, 11, 12),
        "Mars": (1, 3, 6, 10, 11),
        "Mercury": (1, 2, 4, 6, 8, 10, 11),
        "Jupiter": (1, 2, 4, 5, 6, 7, 9, 10, 11),
        "Venus": (1, 2, 3, 4, 5, 8, 9),
        "Saturn": (1, 3, 4, 6, 10, 11),
        "Lagna": (3, 6, 10, 11),
    },
}

#: The row-sums the recension prints. Checked at import: a mistyped table is
#: caught here rather than surfacing as a subtly wrong chart.
BHINNA_TOTALS = {
    "Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
    "Jupiter": 56, "Venus": 52, "Saturn": 39, "Lagna": 49,
}

SARVA_TOTAL = 337

TRIKONAS = (
    ("Aries", "Leo", "Sagittarius"),
    ("Taurus", "Virgo", "Capricorn"),
    ("Gemini", "Libra", "Aquarius"),
    ("Cancer", "Scorpio", "Pisces"),
)

#: The six two-sign lords. Cancer and Leo are exempt: their lords own one each.
EKADHIPATYA_PAIRS = (
    ("Aries", "Scorpio"), ("Taurus", "Libra"), ("Gemini", "Virgo"),
    ("Sagittarius", "Pisces"), ("Capricorn", "Aquarius"),
)

RASI_GUNAKA = {
    "Aries": 7, "Taurus": 10, "Gemini": 8, "Cancer": 4, "Leo": 10,
    "Virgo": 5, "Libra": 7, "Scorpio": 8, "Sagittarius": 9,
    "Capricorn": 5, "Aquarius": 11, "Pisces": 12,
}

GRAHA_GUNAKA = {
    "Sun": 5, "Moon": 5, "Mars": 8, "Mercury": 5,
    "Jupiter": 10, "Venus": 7, "Saturn": 5,
}


def _check_tables() -> None:
    for varga, table in BHINNA_TABLES.items():
        got = sum(len(v) for v in table.values())
        want = BHINNA_TOTALS[varga]
        if got != want:
            raise ValueError(
                f"the {varga} ashtakavarga table sums to {got} rekhas, but the "
                f"recension prints {want}"
            )
    graha_sum = sum(BHINNA_TOTALS[g] for g in GRAHAS)
    if graha_sum != SARVA_TOTAL:
        raise ValueError(
            f"the seven graha tables sum to {graha_sum}, not {SARVA_TOTAL}"
        )


_check_tables()


# -- inputs ---------------------------------------------------------------


@dataclass
class StrengthInputs:
    """Everything the chapter needs, stated once so nothing is guessed.

    Fields left as ``None`` are honestly absent, and every limb that needs one
    reports itself unevaluable rather than substituting a default. The pack
    that carries these rules declares four kala-bala limbs, ayana-bala and
    cheshta-bala 'unevaluable until those inputs exist'; they exist here, but
    only when the caller supplies them.
    """

    #: Sidereal longitude of each graha, in degrees.
    longitudes: dict[str, float]
    #: Sidereal longitude of the lagna, in degrees.
    lagna: float
    #: Sidereal longitude of each bhava-madhya, 1-12. Whole-sign charts may
    #: pass the sign starts; the text's own example uses cusps.
    bhava_madhyas: dict[int, float] = field(default_factory=dict)
    #: Navamsa (D9) sign index 0-11 per graha, for the ojayugma limb.
    navamsa_index: dict[str, int] = field(default_factory=dict)
    #: Saptavargaja dignity per graha per varga, keyed by the names in
    #: SAPTAVARGAJA_VIRUPAS.
    saptavargaja: dict[str, list[str]] = field(default_factory=dict)
    ayanamsa: float | None = None
    is_day_birth: bool | None = None
    #: Ishta-kala and the half-day, both in ghatis, for natonnata-bala.
    ishta_ghati: float | None = None
    half_day_ghati: float | None = None
    #: Which sixth of the day-night round holds the birth, 0-5.
    tribhaga_index: int | None = None
    varshesa: str | None = None
    masesa: str | None = None
    dinesa: str | None = None
    horesa: str | None = None
    #: Motion state per graha, keyed by GATI_BALA_VIRUPAS.
    gati: dict[str, str] = field(default_factory=dict)
    #: Mean longitude and sighrocca, when the caller can supply them.
    madhyama: dict[str, float] = field(default_factory=dict)
    sighrocca: dict[str, float] = field(default_factory=dict)
    #: Pairs of grahas at war, for the yuddha correction.
    yuddha_pairs: tuple[tuple[str, str], ...] = ()


@dataclass
class Bala:
    """One limb, which may honestly be undecided."""

    virupas: float | None
    rule_id: str
    note: str = ""

    @property
    def known(self) -> bool:
        return self.virupas is not None

    def __str__(self) -> str:
        return "undecided" if self.virupas is None else as_rupas(self.virupas)


def _arc_over_three(a: float, b: float) -> float:
    """The chapter's recurring move: fold the arc, then divide by three."""
    arc = (a - b) % 360.0
    return min(arc, 360.0 - arc) / 3.0


# -- drik-bala ------------------------------------------------------------


def drsti_virupas(arc_degrees: float) -> float:
    """The graded drsti value of an arc, BPHS uttara 2.2-7.

    This is a CONTINUOUS function of the arc, not the flat special-aspect
    scheme (Mars 4/7/8, Jupiter 5/7/9, Saturn 3/7/10) the engine uses
    elsewhere. The two conflict; the conflict is recorded in the pack and is
    not resolved here.
    """
    d = arc_degrees % 360.0
    if 180.0 < d <= 300.0:
        return (300.0 - d) / 2.0
    if 150.0 < d <= 180.0:
        return (d - 150.0) * 2.0
    if 120.0 < d <= 150.0:
        return 150.0 - d
    if 90.0 < d <= 120.0:
        return (120.0 - d) / 2.0 + 30.0
    if 60.0 < d <= 90.0:
        return (d - 60.0) + 15.0
    if 30.0 < d <= 60.0:
        return (d - 30.0) / 2.0
    # The text supplies no rule below one rasi or above ten.
    return 0.0


def drsti_on(point: float, inputs: StrengthInputs) -> dict[str, float]:
    """Every graha's drsti upon a point, in virupas."""
    return {
        g: drsti_virupas((point - lon) % 360.0)
        for g, lon in inputs.longitudes.items()
    }


def net_drsti_quarter(point: float, inputs: StrengthInputs) -> float:
    """A quarter of the benefic surplus over the malefic, signed.

    The commentary fixes the two parties explicitly: benefics are counted
    from the Moon onward, malefics from the Sun onward.
    """
    values = drsti_on(point, inputs)
    benefic = sum(
        v for g, v in values.items() if g in ("Moon", "Mercury", "Jupiter", "Venus")
    )
    malefic = sum(
        v for g, v in values.items() if g in ("Sun", "Mars", "Saturn")
    )
    return (benefic - malefic) / 4.0


# -- sthana-bala ----------------------------------------------------------


def uccha_bala(graha: str, inputs: StrengthInputs) -> Bala:
    lon = inputs.longitudes.get(graha)
    if lon is None:
        return Bala(None, "jyotisha.bphs.u02.sthanabala.uccha")
    debilitation = (EXALTATION_DEGREE[graha] + 180.0) % 360.0
    return Bala(
        _arc_over_three(lon, debilitation),
        "jyotisha.bphs.u02.sthanabala.uccha",
    )


def saptavargaja_bala(graha: str, inputs: StrengthInputs) -> Bala:
    dignities = inputs.saptavargaja.get(graha)
    if not dignities:
        return Bala(
            None, "jyotisha.bphs.u02.sthanabala.saptavargaja",
            "the seven varga dignities were not supplied",
        )
    return Bala(
        sum(SAPTAVARGAJA_VIRUPAS[d] for d in dignities),
        "jyotisha.bphs.u02.sthanabala.saptavargaja",
        "this recension prints 45/30/20/15/10/4/2 and 100 for a varga place "
        "that is the graha's own exaltation; the handbooks halve instead",
    )


def ojayugma_bala(graha: str, inputs: StrengthInputs) -> Bala:
    """Fifteen for the rasi and fifteen for the navamsa, by parity."""
    lon = inputs.longitudes.get(graha)
    amsa = inputs.navamsa_index.get(graha)
    if lon is None or amsa is None:
        return Bala(
            None, "jyotisha.bphs.u02.sthanabala.ojayugma",
            "the navamsa placement was not supplied",
        )
    wants_even = graha in ("Moon", "Venus")
    rasi_even = (int(lon // 30) % 2) == 1  # index 1 = Taurus = an even rasi
    amsa_even = (amsa % 2) == 1
    total = 0.0
    if rasi_even == wants_even:
        total += 15.0
    if amsa_even == wants_even:
        total += 15.0
    return Bala(
        total, "jyotisha.bphs.u02.sthanabala.ojayugma",
        "the commentary states that the rasi limb is imported from other "
        "works (granthantara-pramanyat); that attribution is carried",
    )


def kendradi_bala(graha: str, inputs: StrengthInputs) -> Bala:
    lon = inputs.longitudes.get(graha)
    if lon is None:
        return Bala(None, "jyotisha.bphs.u02.sthanabala.kendradi")
    house = int((lon - inputs.lagna) % 360.0 // 30) + 1
    if house in (1, 4, 7, 10):
        value = 60.0
    elif house in (2, 5, 8, 11):
        value = 30.0
    else:
        value = 15.0
    return Bala(value, "jyotisha.bphs.u02.sthanabala.kendradi")


def drekkana_bala(graha: str, inputs: StrengthInputs) -> Bala:
    lon = inputs.longitudes.get(graha)
    if lon is None:
        return Bala(None, "jyotisha.bphs.u02.sthanabala.drekkana")
    third = int((lon % 30.0) // 10)
    male, neuter, female = 0, 1, 2
    wanted = {
        "Sun": male, "Mars": male, "Jupiter": male,
        "Mercury": neuter, "Saturn": neuter,
        "Moon": female, "Venus": female,
    }[graha]
    return Bala(
        15.0 if third == wanted else 0.0,
        "jyotisha.bphs.u02.sthanabala.drekkana",
    )


def sthana_bala(graha: str, inputs: StrengthInputs) -> tuple[Bala, list[Bala]]:
    limbs = [
        uccha_bala(graha, inputs),
        saptavargaja_bala(graha, inputs),
        ojayugma_bala(graha, inputs),
        kendradi_bala(graha, inputs),
        drekkana_bala(graha, inputs),
    ]
    if any(not limb.known for limb in limbs):
        return Bala(None, "jyotisha.bphs.u02.sthanabala",
                    "one or more of the five components is undecided"), limbs
    return Bala(
        sum(limb.virupas for limb in limbs), "jyotisha.bphs.u02.sthanabala"
    ), limbs


# -- dig-bala -------------------------------------------------------------


def dig_bala(graha: str, inputs: StrengthInputs) -> Bala:
    lon = inputs.longitudes.get(graha)
    weak_bhava = DIGBALA_WEAK_BHAVA[graha]
    point = inputs.bhava_madhyas.get(weak_bhava)
    if point is None and inputs.lagna is not None:
        # Whole-sign fallback: the bhava's own start from the lagna's sign.
        point = (int(inputs.lagna // 30) * 30.0 + (weak_bhava - 1) * 30.0) % 360.0
    if lon is None or point is None:
        return Bala(None, "jyotisha.bphs.u02.digbala")
    return Bala(_arc_over_three(lon, point), "jyotisha.bphs.u02.digbala")


# -- kala-bala ------------------------------------------------------------


def natonnata_bala(graha: str, inputs: StrengthInputs) -> Bala:
    rule = "jyotisha.bphs.u02.kalabala.natonnata"
    if graha == "Mercury":
        return Bala(60.0, rule, "Mercury takes sixty always, in every case")
    if (
        inputs.ishta_ghati is None
        or inputs.half_day_ghati is None
        or inputs.is_day_birth is None
    ):
        return Bala(None, rule, "the ghati clock was not supplied")
    nata = abs(inputs.ishta_ghati - inputs.half_day_ghati)
    unnata = 30.0 - nata
    diva = 2.0 * unnata
    if graha in NATONNATA_DAY_STRONG:
        return Bala(diva if inputs.is_day_birth else 60.0 - diva, rule)
    return Bala(60.0 - diva if inputs.is_day_birth else diva, rule)


def paksha_bala(graha: str, inputs: StrengthInputs) -> Bala:
    rule = "jyotisha.bphs.u02.kalabala.paksha"
    moon, sun = inputs.longitudes.get("Moon"), inputs.longitudes.get("Sun")
    if moon is None or sun is None:
        return Bala(None, rule)
    value = _arc_over_three(moon, sun)
    if graha in ("Moon", "Mercury", "Venus", "Jupiter"):
        return Bala(
            value, rule,
            "this recension does NOT double the Moon's paksha-bala; several "
            "modern handbooks do",
        )
    return Bala(60.0 - value, rule)


def tribhaga_bala(graha: str, inputs: StrengthInputs) -> Bala:
    rule = "jyotisha.bphs.u02.kalabala.tribhaga"
    if graha == "Jupiter":
        return Bala(60.0, rule, "Jupiter receives the full strength always")
    if inputs.tribhaga_index is None:
        return Bala(None, rule, "the thirds of day and night were not supplied")
    lord = TRIBHAGA_LORDS[inputs.tribhaga_index]
    return Bala(60.0 if graha == lord else 0.0, rule)


def varshadi_bala(graha: str, inputs: StrengthInputs) -> Bala:
    rule = "jyotisha.bphs.u02.kalabala.varsha_masa_dina_hora"
    lords = {
        "year": inputs.varshesa, "month": inputs.masesa,
        "day": inputs.dinesa, "hora": inputs.horesa,
    }
    if all(v is None for v in lords.values()):
        return Bala(None, rule, "the year, month, day and hora lords were "
                                "not supplied")
    return Bala(
        sum(VARSHADI_VIRUPAS[k] for k, v in lords.items() if v == graha), rule
    )


def kala_bala(graha: str, inputs: StrengthInputs) -> tuple[Bala, list[Bala]]:
    limbs = [
        natonnata_bala(graha, inputs),
        paksha_bala(graha, inputs),
        tribhaga_bala(graha, inputs),
        varshadi_bala(graha, inputs),
    ]
    rule = "jyotisha.bphs.u02.kalabala.assembly"
    note = (
        "this recension's kala-bala has FOUR limbs; the handbooks give it six "
        "or seven by folding in ayana and yuddha, which this text keeps apart"
    )
    if any(not limb.known for limb in limbs):
        return Bala(None, rule, note), limbs
    return Bala(sum(limb.virupas for limb in limbs), rule, note), limbs


# -- ayana-bala and the fourth bala ---------------------------------------


def _khanda_arc(bhuja: float) -> float:
    """Apply the dhruvanka khandas 45, 33, 12 to the bhuja, with carry."""
    remaining, arc = bhuja, 0.0
    for khanda in AYANA_KHANDAS:
        segment = min(remaining, 30.0)
        arc += khanda * segment / 30.0
        remaining -= segment
        if remaining <= 0:
            break
    return arc


def ayana_bala(graha: str, inputs: StrengthInputs) -> Bala:
    rule = "jyotisha.bphs.u02.ayanabala"
    lon = inputs.longitudes.get(graha)
    if lon is None or inputs.ayanamsa is None:
        return Bala(None, rule, "the sayana longitude was not supplied")
    sayana = (lon + inputs.ayanamsa) % 360.0
    # The bhuja is the arc to the nearer equinox, 0 to 90.
    bhuja = sayana % 180.0
    if bhuja > 90.0:
        bhuja = 180.0 - bhuja
    arc = _khanda_arc(bhuja)
    northern = sayana < 180.0  # Aries..Virgo
    if graha in AYANA_REVERSED:
        northern = not northern
    if graha == "Mercury":
        northern = True  # for Mercury the text says always add
    total = (90.0 + arc if northern else 90.0 - arc) / 3.0
    if graha == "Sun":
        total *= 2.0
    return Bala(total, rule)


def cheshta_bala(graha: str, inputs: StrengthInputs) -> Bala:
    """The fourth bala for the star-grahas.

    Two routes are printed in the same chapter. The cheshta-kendra procedure
    needs the mean longitude and the sighrocca; where the caller supplies them
    it is used. Where it does not, the gati table printed alongside it is used
    and said so, because that table is the text's own and needs no input the
    engine lacks. What is never done is to invent a mean longitude.
    """
    rule = "jyotisha.bphs.u02.cheshtabala"
    if graha == "Sun":
        doubled = ayana_bala("Sun", inputs)
        return Bala(
            doubled.virupas, rule,
            "for the Sun this recension's fourth-bala cell IS the doubled "
            "ayana-bala; its own tally prints 0|27|15 in the cheshta column",
        )
    madhyama = inputs.madhyama.get(graha)
    sighrocca = inputs.sighrocca.get(graha)
    if madhyama is not None and sighrocca is not None:
        sphuta = inputs.longitudes[graha]
        half = abs(madhyama - sphuta) / 2.0
        corrected = madhyama + half if madhyama > sphuta else madhyama - half
        kendra = (sighrocca - corrected) % 360.0
        if graha in ("Sun", "Moon"):
            kendra = (kendra + 90.0) % 360.0
        if kendra > 180.0:
            kendra = 360.0 - kendra
        return Bala(kendra / 3.0, rule, "computed from the cheshta-kendra")
    state = inputs.gati.get(graha)
    if state is None:
        return Bala(
            None, rule,
            "neither the mean longitude nor a motion state was supplied",
        )
    return Bala(
        GATI_BALA_VIRUPAS[state], rule,
        "taken from the gati table printed in the same chapter, the mean "
        "longitude and sighrocca not having been supplied",
    )


# -- assembly -------------------------------------------------------------


def sadbala(inputs: StrengthInputs) -> dict[str, dict[str, Any]]:
    """The six strengths of every graha, with the drik correction applied.

    The five additive balas are summed; drik-bala is then applied as a QUARTER
    of the signed surplus, which is what makes it the sixth and why the
    chapter states it first.
    """
    out: dict[str, dict[str, Any]] = {}
    for graha in GRAHAS:
        if graha not in inputs.longitudes:
            continue
        sthana, sthana_limbs = sthana_bala(graha, inputs)
        kala, kala_limbs = kala_bala(graha, inputs)
        dig = dig_bala(graha, inputs)
        fourth = cheshta_bala(graha, inputs)
        ayana = ayana_bala(graha, inputs)
        naisargika = Bala(
            NAISARGIKA_BALA[graha], "jyotisha.bphs.u02.naisargikabala"
        )
        five = [sthana, dig, kala, fourth, naisargika]
        if any(not b.known for b in five):
            pinda = None
            drik = None
        else:
            drik = net_drsti_quarter(inputs.longitudes[graha], inputs)
            pinda = sum(b.virupas for b in five) + drik
        out[graha] = {
            "sthana_bala": sthana, "sthana_limbs": sthana_limbs,
            "dig_bala": dig, "kala_bala": kala, "kala_limbs": kala_limbs,
            "fourth_bala": fourth, "ayana_bala": ayana,
            "naisargika_bala": naisargika,
            "drik_correction": drik,
            "sadbala_pinda": pinda,
            "sadbala_pinda_rupas": None if pinda is None else as_rupas(pinda),
            "required_minimum_virupas": REQUIRED_MINIMA[graha],
            "minimum_class": MINIMA_CLASS[graha],
            "meets_minimum": (
                None if pinda is None else pinda >= REQUIRED_MINIMA[graha]
            ),
        }
    _apply_yuddha(out, inputs)
    return out


def _apply_yuddha(
    result: dict[str, dict[str, Any]], inputs: StrengthInputs
) -> None:
    """The war correction: the difference is taken from one and given to the other.

    The recension prints no orb for yuddha in this chapter. The conventional
    one-degree criterion is NOT stated here and must not be attributed to it,
    so the pairs at war are an input, never inferred.
    """
    for a, b in inputs.yuddha_pairs:
        pa, pb = result.get(a, {}), result.get(b, {})
        if pa.get("sadbala_pinda") is None or pb.get("sadbala_pinda") is None:
            continue
        diff = abs(pa["sadbala_pinda"] - pb["sadbala_pinda"])
        victor, vanquished = (a, b) if pa["sadbala_pinda"] > pb["sadbala_pinda"] else (b, a)
        result[victor]["sadbala_pinda"] += diff
        result[vanquished]["sadbala_pinda"] -= diff
        for g in (victor, vanquished):
            result[g]["sadbala_pinda_rupas"] = as_rupas(result[g]["sadbala_pinda"])
            result[g]["meets_minimum"] = (
                result[g]["sadbala_pinda"] >= REQUIRED_MINIMA[g]
            )
            result[g]["yuddha_applied"] = True


def strongest(result: dict[str, dict[str, Any]], among: list[str]) -> str | None:
    """BPHS uttara 2.44-45: among the causes of a yoga, the strongest gives it.

    Returns None when any candidate's strength is undecided - the text's rule
    is a comparison, and a comparison against an unknown is not a result.
    """
    known = [
        (g, result[g]["sadbala_pinda"])
        for g in among
        if g in result and result[g]["sadbala_pinda"] is not None
    ]
    if len(known) != len(among) or not known:
        return None
    return max(known, key=lambda kv: kv[1])[0]


# -- Ashtakavarga ---------------------------------------------------------


def bhinnashtakavarga(
    varga: str, positions: dict[str, int]
) -> dict[str, int]:
    """One graha's ashtakavarga: rekhas per rasi, keyed by rasi name.

    ``positions`` gives each reference point's rasi index, 0-11, the Lagna
    included.
    """
    counts = {r: 0 for r in RASIS}
    for point, offsets in BHINNA_TABLES[varga].items():
        base = positions.get(point)
        if base is None:
            continue
        for offset in offsets:
            counts[RASIS[(base + offset - 1) % 12]] += 1
    return counts


def sarvashtakavarga(positions: dict[str, int]) -> dict[str, int]:
    """The sum of the SEVEN graha tables. The lagna's is kept separate.

    Taken from the UNREDUCED tables: an implementation that reduces before
    summing reports a total that is not 337.
    """
    total = {r: 0 for r in RASIS}
    for graha in GRAHAS:
        for rasi, n in bhinnashtakavarga(graha, positions).items():
            total[rasi] += n
    return total


def trikona_sodhana(counts: dict[str, int]) -> dict[str, int]:
    """The trinal reduction, first of the two and never second."""
    out = dict(counts)
    for trine in TRIKONAS:
        values = [out[r] for r in trine]
        if 0 in values:
            continue  # no reduction is performed in a trine holding a zero
        if len(set(values)) == 1:
            for r in trine:
                out[r] = 0
            continue
        least = min(values)
        for r in trine:
            out[r] -= least
    return out


def ekadhipatya_sodhana(
    counts: dict[str, int], occupied: set[str]
) -> dict[str, int]:
    """The single-lordship reduction, performed AFTER the trinal one.

    Cancer and Leo are exempt: their lords own one sign each.
    """
    out = dict(counts)
    for a, b in EKADHIPATYA_PAIRS:
        va, vb = out[a], out[b]
        oa, ob = a in occupied, b in occupied
        if oa and ob:
            continue  # both occupied: no reduction, ever
        if not oa and not ob:
            if va == vb:
                out[a] = out[b] = 0
            elif va > vb:
                out[a], out[b] = va - vb, 0
            else:
                out[b], out[a] = vb - va, 0
            continue
        # exactly one is occupied
        occ, unocc = (a, b) if oa else (b, a)
        if out[occ] < out[unocc]:
            out[unocc] = out[unocc] - out[occ]
        elif out[occ] > out[unocc]:
            out[unocc] = 0
        else:
            out[unocc] = 0
    return out


def pindotpatti(
    reduced: dict[str, int], graha_rasis: dict[str, str]
) -> dict[str, int]:
    """Rasi pinda, graha pinda and their sum, from the TWICE-reduced figures."""
    rasi_pinda = sum(reduced[r] * RASI_GUNAKA[r] for r in RASIS)
    graha_pinda = sum(
        reduced[graha_rasis[g]] * GRAHA_GUNAKA[g]
        for g in GRAHAS
        if g in graha_rasis
    )
    return {
        "rasi_pinda": rasi_pinda,
        "graha_pinda": graha_pinda,
        "yoga_pinda": rasi_pinda + graha_pinda,
    }


def sarva_grade(rekhas: int) -> str:
    """The chapter's own three grades for a sign's sarva total."""
    if rekhas > 30:
        return "uttama (highest)"
    if rekhas >= 25:
        return "madhya (middling)"
    return "kanishtha (least)"


def ashtakavarga(
    positions: dict[str, int], graha_rasis: dict[str, str]
) -> dict[str, Any]:
    """The whole technique, in the order the recension performs it.

    The order is not optional: the reductions change the figures the pinda is
    computed from, and the sarva is taken before them.
    """
    bhinnas = {v: bhinnashtakavarga(v, positions) for v in BHINNA_TABLES}
    sarva = sarvashtakavarga(positions)
    occupied = set(graha_rasis.values())
    reduced, pindas = {}, {}
    for varga, counts in bhinnas.items():
        step1 = trikona_sodhana(counts)
        step2 = ekadhipatya_sodhana(step1, occupied)
        reduced[varga] = step2
        pindas[varga] = pindotpatti(step2, graha_rasis)
    return {
        "bhinnashtakavarga": bhinnas,
        "sarvashtakavarga": sarva,
        "sarva_total": sum(sarva.values()),
        "sarva_grades": {r: sarva_grade(n) for r, n in sarva.items()},
        "after_reductions": reduced,
        "pindas": pindas,
        "own_varga_rekhas": {
            g: bhinnas[g][graha_rasis[g]]
            for g in GRAHAS
            if g in graha_rasis
        },
        "notation_warning": (
            "rekha is the scored mark and karana/bindu is the blank; much "
            "popular writing has this exactly backwards"
        ),
    }
