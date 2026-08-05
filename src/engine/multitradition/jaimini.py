"""Jaimini's system, computed - and refusing where the pack refuses.

This is not Parasari Jyotisha with different vocabulary. Jaimini nominates its
significators per chart rather than by nature, draws aspect lines between SIGNS
that have no counterpart in the Parasari scheme, and runs its periods on signs
rather than on grahas. The two are never merged into one verdict here; where
both are shown they are shown as two readings with their disagreements visible,
which is what the pack's own refusal rule requires.

Three things this module will not do, because the pack does not:

**It will not name a karaka below rank one without being told the scheme.**
The sutra itself says *saptanam astanam va* - "of seven or of eight" - and the
two best witnesses differ. The fork changes which graha carries the father, the
son and the kin. Rank one is unaffected and is therefore always safe to name;
everything below it requires the caller to declare.

**It will not issue chara dasa period lengths.** Three conventions the sutra
does not settle - whether one is subtracted from the count, what a lord in its
own sign yields, and which of Scorpio's and Aquarius' two lords is used -
change every number. The direction rules ARE settled and are given.

**It will not delineate the Varnada.** It computes and shows it as a figure,
because the commentator twice admits in as many words that he cannot explain
the rule he is transmitting: *parantu acaryena katham ojalagnetyadi krtam tan
na vidmah*. A figure whose derivation its own transmitter cannot account for
may be displayed. It may not be read.

The rasi drsti table below is the most load-bearing thing here, and it is the
best-validated: Abhyankar's Ranade chart confirms it three times and his Lokur
chart twice, five independent hits from inside the tradition's own worked
material, none of which is a Parasari aspect.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

RASIS = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)

MOVABLE = ("Aries", "Cancer", "Libra", "Capricorn")
FIXED = ("Taurus", "Leo", "Scorpio", "Aquarius")
DUAL = ("Gemini", "Virgo", "Sagittarius", "Pisces")

DOMICILE = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

#: Scorpio and Aquarius have a second, nodal lord in the tradition, and which
#: one a dasa length uses is one of the three undeclared conventions.
CO_LORDS = {"Scorpio": "Ketu", "Aquarius": "Rahu"}

BENEFICS = ("Jupiter", "Venus", "Mercury", "Moon")
MALEFICS = ("Sun", "Mars", "Saturn", "Rahu", "Ketu")

#: Ascending strength, Saturn weakest: mando 'jyayan grahesu. The Sun is
#: strongest. The same series is encoded on the Parasari side from
#: Brhajjataka, which makes this a genuine point of agreement between the
#: two branches rather than a coincidence.
STRENGTH_ASCENDING = (
    "Saturn", "Mars", "Mercury", "Jupiter", "Venus", "Moon", "Sun",
)

KARAKA_TITLES_SEVEN = (
    "Atmakaraka", "Amatyakaraka", "Bhratrkaraka", "Matrkaraka",
    "Putrakaraka", "Jnatikaraka", "Darakaraka",
)

#: The eight-karaka scheme inserts a Pitrkaraka between the mother and the son.
KARAKA_TITLES_EIGHT = (
    "Atmakaraka", "Amatyakaraka", "Bhratrkaraka", "Matrkaraka",
    "Pitrkaraka", "Putrakaraka", "Jnatikaraka", "Darakaraka",
)

KARAKA_SCHEME_FORK = (
    "The sutra offers both: saptanam astanam va, 'of seven or of eight'. In "
    "the seven-karaka scheme the Matrkaraka doubles as Putrakaraka and there "
    "is no distinct Pitrkaraka; in the eight-karaka scheme Rahu is admitted "
    "and the father gets a karaka of his own. The two best witnesses differ "
    "and the pack does not choose. Rank one is the same either way, which is "
    "why the Atmakaraka can be named without declaring the scheme and nothing "
    "below it can."
)

RAHU_CONVENTION_FORK = (
    "Where Rahu is admitted, one convention counts his degree-within-sign "
    "forward like any other graha and another counts it backward, so that his "
    "effective degree is 30 minus his longitude in sign. The worked charts "
    "settle this for Abhyankar's own practice and not for the tradition: in "
    "his Patel chart Rahu stands at 5 degrees, and reverse-counting would put "
    "him at 25 and make him the Atmakaraka, where Abhyankar names Saturn. The "
    "reverse convention is refuted for him; the vrddha verse carrying it is "
    "still quoted approvingly in the Sutrarthaprakasika, so both stay."
)

SPECIAL_LAGNA_ORIGIN_FORK = (
    "configured_method - the special lagnas' origin is disputed and the fork "
    "moves the Hora Lagna by whole signs. The pracinah and the vrddha karika "
    "count from the Sun's sign when the janma lagna is odd and from the janma "
    "lagna when it is even; the Sutrarthaprakasika counts always from the Sun, "
    "on the ground that at sunrise every lagna coincides and they diverge "
    "afterwards only by their own rates. Nilakantha rejects the karika "
    "outright. This engine takes the Sutrarthaprakasika's reading and says so."
)

#: The rates the vrddha verses state, in signs per hour of clock time.
SPECIAL_LAGNA_RATES = {
    "Hora Lagna": 1.0,        # one sign per 2.5 ghatikas = 60 minutes
    "Ghatika Lagna": 2.5,     # one sign per ghatika = 24 minutes
    "Bhava Lagna": 0.5,       # one sign per 5 ghatikas = 2 hours
}

CHARA_DASA_UNDECIDED = (
    "subtract one from the count or not",
    "what a lord standing in its own sign yields",
    "which of the two lords of Scorpio and Aquarius is used",
)

MAX_DASA_YEARS = 144  # yavad vivekam avrttir bhanam - viveka by katapayadi


def _index(rasi: str) -> int:
    return RASIS.index(rasi)


def modality(rasi: str) -> str:
    if rasi in MOVABLE:
        return "movable"
    if rasi in FIXED:
        return "fixed"
    return "dual"


# -- rasi drsti ----------------------------------------------------------


def rasi_drsti(rasi: str) -> list[str]:
    """The signs a sign aspects. A SIGN aspect, with no Parasari counterpart.

    A movable sign aspects the three fixed signs except the one next to it; a
    fixed sign the three movable except the one behind it; a dual sign the
    other three dual signs. Confirmed five times across two of Abhyankar's own
    worked charts.
    """
    i = _index(rasi)
    kind = modality(rasi)
    if kind == "movable":
        offsets, excluded = (4, 7, 10), 1
    elif kind == "fixed":
        offsets, excluded = (2, 5, 8), 11
    else:
        offsets, excluded = (3, 6, 9), 0
    del excluded  # the offsets already omit it; kept for the reader
    return [RASIS[(i + o) % 12] for o in offsets]


def graha_drsti(graha_rasi: str) -> list[str]:
    """tannisthas ca tadvat - a graha aspects what its sign aspects."""
    return rasi_drsti(graha_rasi)


def aspects_sign(from_rasi: str, to_rasi: str) -> bool:
    return to_rasi in rasi_drsti(from_rasi)


# -- chara karakas -------------------------------------------------------


@dataclass
class Karaka:
    graha: str
    degree_in_sign: float
    rank: int
    title: str | None
    title_certain: bool
    note: str = ""


def chara_karakas(
    degrees_in_sign: dict[str, float],
    scheme: str | None = None,
    rahu_counting: str = "forward",
) -> list[Karaka]:
    """Rank the grahas by degrees-within-sign, descending.

    ``scheme`` is ``"seven"``, ``"eight"``, or None. With None, only rank one
    is titled: the fork changes every title below it and the pack refuses to
    choose. This is the single most implementable rule in the text - pure
    arithmetic on the longitude mod 30, with minutes and finer units breaking
    ties (kaladibhih).
    """
    if scheme not in (None, "seven", "eight"):
        raise ValueError("scheme must be 'seven', 'eight' or None")
    candidates = dict(degrees_in_sign)
    if scheme == "seven":
        candidates.pop("Rahu", None)
    if "Rahu" in candidates and rahu_counting == "reverse":
        candidates["Rahu"] = 30.0 - candidates["Rahu"]
    candidates.pop("Ketu", None)  # Ketu holds Rahu's degrees; counted as one

    order = sorted(candidates.items(), key=lambda kv: -kv[1])
    titles = (
        KARAKA_TITLES_EIGHT if scheme == "eight"
        else KARAKA_TITLES_SEVEN if scheme == "seven"
        else None
    )
    out: list[Karaka] = []
    for rank, (graha, degree) in enumerate(order, start=1):
        if titles is not None and rank <= len(titles):
            title, certain = titles[rank - 1], True
        elif rank == 1:
            title, certain = "Atmakaraka", True
        else:
            title, certain = None, False
        out.append(
            Karaka(
                graha=graha, degree_in_sign=round(degree, 4), rank=rank,
                title=title, title_certain=certain,
                note=(
                    "" if certain else
                    "the seven/eight fork is undeclared and it changes which "
                    "topic this rank carries"
                ),
            )
        )
    return out


def atmakaraka(degrees_in_sign: dict[str, float], **kw) -> str | None:
    ranked = chara_karakas(degrees_in_sign, **kw)
    return ranked[0].graha if ranked else None


# -- arudha padas --------------------------------------------------------


def arudha_pada(bhava_rasi: str, lord_rasi: str) -> tuple[str, str | None]:
    """Count from the bhava to its lord, then as far again from the lord.

    Two exceptions the text states without giving a reason: a lord in the 4th
    from its own bhava puts the pada in the 4th rather than the 7th, and a
    lord in the 7th puts it in the 10th rather than back on the bhava itself.
    Returns the pada and the exception applied, if any.
    """
    span = (_index(lord_rasi) - _index(bhava_rasi)) % 12 + 1
    if span == 4:
        return bhava_rasi_at(bhava_rasi, 4), "lord in the 4th"
    if span == 7:
        return bhava_rasi_at(lord_rasi, 4), "lord in the 7th"
    pada = RASIS[(_index(lord_rasi) + span - 1) % 12]
    return pada, None


def bhava_rasi_at(rasi: str, offset: int) -> str:
    """The sign standing ``offset`` houses from a sign, itself counting as 1."""
    return RASIS[(_index(rasi) + offset - 1) % 12]


def pada_kundali(
    lagna_rasi: str, graha_rasis: dict[str, str]
) -> dict[str, dict[str, Any]]:
    """The twelve padas - an entirely separate frame Jaimini reads alongside.

    Arudha padas have no counterpart in the Parasari natal method, which is
    exactly why they are computed here rather than borrowed.
    """
    out: dict[str, dict[str, Any]] = {}
    for offset in range(1, 13):
        bhava = bhava_rasi_at(lagna_rasi, offset)
        lord = DOMICILE[bhava]
        lord_rasi = graha_rasis.get(lord)
        if lord_rasi is None:
            continue
        pada, exception = arudha_pada(bhava, lord_rasi)
        out[f"bhava_{offset}"] = {
            "bhava_rasi": bhava, "lord": lord, "lord_rasi": lord_rasi,
            "pada": pada, "exception": exception,
        }
    return out


# -- argala --------------------------------------------------------------

ARGALA_HOUSES = (4, 2, 11)
ARGALA_TRIKONA = (5, 9)
VIRODHI_PAIRING = {4: 10, 2: 12, 11: 3, 5: 9}

ARGALA_TARGET_FORK = (
    "The sutra's nidhyatuh is disputed. The Sutrarthaprakasika reads it as a "
    "reference point - the argala falls on the BHAVA under consideration - "
    "and argues that if the Subodhini's reading were right the sutra would "
    "have said 'darabhagyasulastha argala grahat'. The Subodhini reads it as "
    "the aspecting GRAHA itself. Both are recorded; neither is adopted."
)

VIRODHI_PAIRING_FORK = (
    "The sutra lists the obstructing houses - the 12th, the 10th and the 3rd "
    "- but does not say which obstructs which. The Sutrarthaprakasika pairs "
    "them in order; another reading pairs each obstructor with whichever "
    "argala it counts to. Recorded, not resolved."
)


def argala(
    reference_rasi: str, graha_rasis: dict[str, str]
) -> dict[str, Any]:
    """Which grahas throw a bolt across the reference point, and who blocks it.

    The 3rd-house argala forms only *bhuyasa*, by the many: three or more
    malefics on one witness's reading, malefics outnumbering benefics on the
    other. Both counts are reported rather than one being chosen, because the
    two readings disagree about what the word means, not about the arithmetic.
    """
    occupants: dict[int, list[str]] = {}
    for offset in (*ARGALA_HOUSES, *ARGALA_TRIKONA, 3, 10, 12):
        sign = bhava_rasi_at(reference_rasi, offset)
        occupants[offset] = sorted(
            g for g, r in graha_rasis.items() if r == sign
        )

    formed = []
    for offset in ARGALA_HOUSES:
        if occupants[offset]:
            formed.append({
                "from_house": offset,
                "grahas": occupants[offset],
                "obstructed_by_house": VIRODHI_PAIRING[offset],
                "obstructors": occupants.get(VIRODHI_PAIRING[offset], []),
                "obstruction_holds": _obstruction_holds(
                    occupants[offset], occupants.get(VIRODHI_PAIRING[offset], [])
                ),
            })
    for offset in ARGALA_TRIKONA:
        if offset == 5 and occupants[5]:
            formed.append({
                "from_house": 5,
                "grahas": occupants[5],
                "obstructed_by_house": 9,
                "obstructors": occupants.get(9, []),
                "obstruction_holds": _obstruction_holds(
                    occupants[5], occupants.get(9, [])
                ),
            })

    third = occupants.get(3, [])
    third_malefics = [g for g in third if g in MALEFICS]
    third_benefics = [g for g in third if g in BENEFICS]
    third_argala = {
        "grahas": third,
        "malefics": third_malefics,
        "benefics": third_benefics,
        "forms_on_three_or_more": len(third_malefics) >= 3,
        "forms_on_outnumbering": (
            bool(third_malefics) and len(third_malefics) > len(third_benefics)
        ),
        "reading_note": (
            "bhuyasa is read as 'three or more malefics' by the "
            "Sutrarthaprakasika and as 'malefics outnumber benefics' by "
            "Abhyankar; both counts are given because the two readings "
            "disagree about the word, not about the chart. Premanidhi's "
            "reading - the single malefic holding the greatest arc - is "
            "recorded as rejected by the Sutrarthaprakasika, which calls it "
            "asangata and argues bhuyasa counts bodies, not degrees."
        ),
    }
    return {
        "reference_rasi": reference_rasi,
        "argalas": formed,
        "third_house_argala": third_argala,
        "target_fork": ARGALA_TARGET_FORK,
        "pairing_fork": VIRODHI_PAIRING_FORK,
    }


def _obstruction_holds(makers: list[str], obstructors: list[str]) -> bool | None:
    """na nyuna vibalas ca - obstructors fewer in number do not obstruct.

    Returns None where the count is equal, because the remaining criterion is
    strength and the commentary is explicit that a graha exalted or in its own
    sign can be balin even when outnumbered - so 'na nyuna' and 'vibala' are
    not redundant and an equal count is not settled by number alone.
    """
    if not obstructors:
        return False
    if len(obstructors) < len(makers):
        return False
    if len(obstructors) == len(makers):
        return None
    return True


# -- special lagnas ------------------------------------------------------


def special_lagna(
    sunrise_to_birth_hours: float,
    sun_longitude: float,
    rate_signs_per_hour: float,
) -> float:
    """A special lagna's longitude, advancing uniformly from the Sun.

    Unlike the rising sign, these advance at a fixed rate and do not depend on
    oblique ascension at the birthplace. The origin is the Sun, per the
    Sutrarthaprakasika - see SPECIAL_LAGNA_ORIGIN_FORK for what that choice
    costs and what the alternative is.
    """
    return (sun_longitude + sunrise_to_birth_hours * rate_signs_per_hour * 30.0) % 360.0


def special_lagnas(
    sunrise_to_birth_hours: float, sun_longitude: float
) -> dict[str, dict[str, Any]]:
    out = {}
    for name, rate in SPECIAL_LAGNA_RATES.items():
        lon = special_lagna(sunrise_to_birth_hours, sun_longitude, rate)
        out[name] = {
            "longitude": round(lon, 4),
            "rasi": RASIS[int(lon // 30)],
            "degree_in_sign": round(lon % 30.0, 4),
            "rate_signs_per_hour": rate,
        }
    return out


def varnada(janma_lagna_rasi: str, hora_lagna_rasi: str) -> dict[str, Any]:
    """The Varnada - computed and shown, never delineated.

    From Aries forward for an odd janma lagna, from Pisces backward for an
    even one; likewise to the Hora Lagna; add the two counts if they agree in
    kind and subtract the smaller from the larger if they do not.

    The commentator transmits this rule and twice admits he cannot explain it:
    *parantu acaryena katham ojalagnetyadi krtam tan na vidmah*. He also notes
    that simply adding the two longitudes as they stand reaches the same sign,
    and cannot say why the odd/even reversal was prescribed. A figure whose
    own transmitter cannot account for its derivation is displayable; it is
    not readable, and nothing here delineates it.
    """
    janma_i, hora_i = _index(janma_lagna_rasi), _index(hora_lagna_rasi)
    janma_odd = janma_i % 2 == 0  # Aries is the first sign and so odd

    def count(idx: int, from_aries: bool) -> int:
        return (idx % 12) + 1 if from_aries else (11 - idx) % 12 + 1

    a = count(janma_i, janma_odd)
    b = count(hora_i, janma_odd)
    same_kind = (a % 2) == (b % 2)
    total = a + b if same_kind else abs(a - b)
    steps = total % 12 or 12
    idx = (steps - 1) % 12 if janma_odd else (11 - (steps - 1)) % 12
    return {
        "rasi": RASIS[idx],
        "counts": {"from_lagna": a, "from_hora_lagna": b},
        "combined": "added" if same_kind else "subtracted",
        "total": total,
        "output_policy": "displayable_figure_only",
        "why": (
            "The Sutrarthaprakasika twice admits it cannot explain the rule "
            "it transmits. The figure is shown; it is not delineated."
        ),
    }


# -- chara dasa ----------------------------------------------------------


def dasa_direction(rasi: str) -> str:
    """Forward for odd signs, reverse for even - suspended for the fixed four.

    Both witnesses agree that 'not so in some cases' means Taurus, Leo,
    Scorpio and Aquarius, where the parity rule does not hold.
    """
    i = _index(rasi)
    forward = i % 2 == 0
    if rasi in FIXED:
        forward = not forward
    return "forward" if forward else "reverse"


def chara_dasa_sequence(start_rasi: str) -> list[str]:
    """The order of the twelve sign-periods. Their LENGTHS are refused."""
    step = 1 if dasa_direction(start_rasi) == "forward" else -1
    i = _index(start_rasi)
    return [RASIS[(i + step * n) % 12] for n in range(12)]


def chara_dasa_lengths_refused() -> dict[str, Any]:
    """Why no period lengths are issued, stated as data rather than silence."""
    return {
        "output_policy": "refused",
        "undecided_conventions": list(CHARA_DASA_UNDECIDED),
        "what_is_settled": (
            "the direction of counting, and that the twelve periods total at "
            f"most {MAX_DASA_YEARS} years - yavad vivekam avrttir bhanam, "
            "viveka by katapayadi"
        ),
        "why_refused": (
            "Each of the three conventions changes every number in the "
            "sequence. A dasa table published without declaring them would "
            "look like a result and be an assumption."
        ),
    }


# -- assembly ------------------------------------------------------------


@dataclass
class JaiminiChart:
    lagna_rasi: str
    graha_rasis: dict[str, str]
    degrees_in_sign: dict[str, float]
    sun_longitude: float | None = None
    sunrise_to_birth_hours: float | None = None
    karaka_scheme: str | None = None
    rahu_counting: str = "forward"
    notes: list[str] = field(default_factory=list)


def build(chart: JaiminiChart) -> dict[str, Any]:
    """Everything Jaimini's own judgment order asks for, in that order.

    The order is taken from the sequence of the sutras: rasi drsti, then
    argala, then the chara karakas, then the arudha padas as a parallel frame,
    then the special lagnas, then the dasas. Strength is a tie-breaker applied
    inside those steps, not a step of its own.
    """
    karakas = chara_karakas(
        chart.degrees_in_sign,
        scheme=chart.karaka_scheme,
        rahu_counting=chart.rahu_counting,
    )
    ak = karakas[0].graha if karakas else None
    ak_rasi = chart.graha_rasis.get(ak) if ak else None

    out: dict[str, Any] = {
        "lagna_rasi": chart.lagna_rasi,
        "rasi_drsti": {
            r: rasi_drsti(r) for r in sorted(set(chart.graha_rasis.values()))
        },
        "graha_drsti": {
            g: graha_drsti(r) for g, r in sorted(chart.graha_rasis.items())
        },
        "chara_karakas": karakas,
        "karaka_scheme": chart.karaka_scheme,
        "karaka_scheme_fork": KARAKA_SCHEME_FORK,
        "rahu_convention": chart.rahu_counting,
        "rahu_convention_fork": RAHU_CONVENTION_FORK,
        "karaka_kundali_first_house": ak_rasi,
        "pada_kundali": pada_kundali(chart.lagna_rasi, chart.graha_rasis),
        "argala_from_lagna": argala(chart.lagna_rasi, chart.graha_rasis),
        "strength_order_ascending": list(STRENGTH_ASCENDING),
        "chara_dasa": {
            "sequence_from_lagna": chara_dasa_sequence(chart.lagna_rasi),
            "direction": dasa_direction(chart.lagna_rasi),
            "lengths": chara_dasa_lengths_refused(),
        },
    }
    if ak_rasi:
        out["argala_from_karaka_lagna"] = argala(ak_rasi, chart.graha_rasis)
        out["karaka_kundali"] = {
            f"house_{n}": bhava_rasi_at(ak_rasi, n) for n in range(1, 13)
        }
    if (
        chart.sun_longitude is not None
        and chart.sunrise_to_birth_hours is not None
    ):
        lagnas = special_lagnas(
            chart.sunrise_to_birth_hours, chart.sun_longitude
        )
        out["special_lagnas"] = lagnas
        out["special_lagna_origin_fork"] = SPECIAL_LAGNA_ORIGIN_FORK
        out["varnada"] = varnada(
            chart.lagna_rasi, lagnas["Hora Lagna"]["rasi"]
        )
    else:
        out["special_lagnas"] = None
        out["special_lagnas_withheld"] = (
            "the special lagnas advance from sunrise at fixed rates, and "
            "neither the sunrise nor the Sun's longitude was supplied"
        )
    return out
