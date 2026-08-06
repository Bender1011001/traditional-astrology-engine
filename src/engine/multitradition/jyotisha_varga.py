"""The divisional charts, from BPHS purva adhyaya 3.

The engine computed D1 and D9 and nothing else, which is a narrower instrument
than the text describes. Adhyaya 3 names sixteen vargas and states plainly
which question each one answers: D10 for career and standing, D7 for children,
D12 for parents, D4 for fortune, D3 for siblings. A reader asked about work and
shown only D1 and D9 has been handed the wrong chart.

Nine computation rules were read verse-by-verse in the mining pass and are
implemented here (D1, D2, D3, D4, D7, D9, D10, D12, D30, D60). Six were not -
D16, D20, D24, D27, D40, D45 - and they are NOT blocked, merely unmined; their
slokas sit legible in the same scan. That distinction is kept because the two
have different remedies.

Two things the recension states that the handbooks often smooth over: the
drekkana rule is the SAME in odd and even signs (this text says so explicitly),
and the trimsamsa is an UNEQUAL division whose five arcs are 5/5/8/7/5 degrees.
"""

from __future__ import annotations

from typing import Any

RASIS = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)

DOMICILE = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

GRAHAS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")

#: Which question each varga answers, from the chapter's own list.
VARGA_PURPOSE = {
    "D1": "the body",
    "D2": "wealth and the like",
    "D3": "happiness arising from brothers and sisters",
    "D4": "fortune",
    "D7": "children and grandchildren",
    "D9": "the spouse",
    "D10": "the great result - work, standing, deeds",
    "D12": "the parents",
    "D30": "the evils",
    "D60": "all results together",
}

#: The vimsopaka weights. Only the two schemes whose vargas are all encoded.
VIMSOPAKA_SCHEMES = {
    "shadvarga": {"D1": 6, "D2": 2, "D3": 4, "D9": 5, "D12": 2, "D30": 1},
    "saptavarga": {
        "D1": 5, "D2": 2, "D3": 3, "D7": 2.5, "D9": 4.5, "D12": 2, "D30": 1
    },
}

VIMSOPAKA_DIGNITY_VISHVAS = {
    "uccha": 20.0, "svaksetra": 20.0, "moolatrikona": 20.0,
    "adhimitra": 20.0, "mitra": 15.0, "sama": 10.0,
    "satru": 7.0, "adhisatru": 5.0,
}

VIMSOPAKA_GRADES = (
    (15.0, "purna-phalada (full result)"),
    (10.0, "madhyama (middling)"),
    (5.0, "svalpa-phalada (slight result)"),
    (0.0, "phalado na hi (no result at all)"),
)

#: Sloka 126's second half is ambiguous and this scan does not settle it.
ADHIMITRA_FORK = (
    "The recension prints 'purnam vishvabalam vimsatih syad adhimitrake', "
    "which reads either as 'full strength is twenty, and likewise in the "
    "great friend's place' or as 'full strength is twenty, and in the great "
    "friend's place eighteen'. The modern handbooks take eighteen. This "
    "engine takes twenty, the plainer reading of the printed line, and the "
    "ambiguity is recorded rather than resolved."
)

UNMINED_VARGAS = ("D16", "D20", "D24", "D27", "D40", "D45")


def _rasi_index(longitude: float) -> int:
    return int(longitude % 360.0 // 30)


def _is_odd_rasi(index: int) -> bool:
    """Aries is the first sign and therefore odd."""
    return index % 2 == 0


def varga_d1(longitude: float) -> str:
    return RASIS[_rasi_index(longitude)]


def varga_d2(longitude: float) -> str:
    """Hora. In an odd sign the first half is the Sun's, in an even the Moon's."""
    idx = _rasi_index(longitude)
    first_half = (longitude % 30.0) < 15.0
    suns = first_half if _is_odd_rasi(idx) else not first_half
    return "Leo" if suns else "Cancer"


def varga_d3(longitude: float) -> str:
    """Drekkana: the sign itself, the 5th, the 9th - odd and even alike."""
    idx = _rasi_index(longitude)
    third = int((longitude % 30.0) // 10)
    return RASIS[(idx + third * 4) % 12]


def varga_d4(longitude: float) -> str:
    """Turyamsa: the sign itself, then the 4th, 7th and 10th from it."""
    idx = _rasi_index(longitude)
    quarter = int((longitude % 30.0) // 7.5)
    return RASIS[(idx + quarter * 3) % 12]


def varga_d7(longitude: float) -> str:
    """Saptamsa: counted from the sign in an odd rasi, from the 7th in an even."""
    idx = _rasi_index(longitude)
    part = int((longitude % 30.0) // (30.0 / 7))
    start = idx if _is_odd_rasi(idx) else (idx + 6) % 12
    return RASIS[(start + part) % 12]


def varga_d9(longitude: float) -> str:
    """Navamsa, counted from the movable sign of the same element."""
    idx = _rasi_index(longitude)
    part = int((longitude % 30.0) // (30.0 / 9))
    # Movable signs count from themselves, fixed from the 9th, dual from the
    # 5th - which is the same as starting at Aries, Capricorn, Libra, Cancer.
    start = {0: 0, 1: 9, 2: 6, 3: 3}[idx % 4]
    return RASIS[(start + part) % 12]


def varga_d10(longitude: float) -> str:
    """Dasamsa: from the sign in an odd rasi, from the 9th in an even."""
    idx = _rasi_index(longitude)
    part = int((longitude % 30.0) // 3.0)
    start = idx if _is_odd_rasi(idx) else (idx + 8) % 12
    return RASIS[(start + part) % 12]


def varga_d12(longitude: float) -> str:
    """Dvadasamsa: counted from the sign itself, in every rasi alike."""
    idx = _rasi_index(longitude)
    part = int((longitude % 30.0) // 2.5)
    return RASIS[(idx + part) % 12]


#: The trimsamsa's five arcs are UNEQUAL. Odd: Mars 5, Saturn 5, Jupiter 8,
#: Mercury 7, Venus 5. Even: the same five reversed.
TRIMSAMSA_ODD = ((5.0, "Mars"), (10.0, "Saturn"), (18.0, "Jupiter"),
                 (25.0, "Mercury"), (30.0, "Venus"))
TRIMSAMSA_EVEN = ((5.0, "Venus"), (12.0, "Mercury"), (20.0, "Jupiter"),
                  (25.0, "Saturn"), (30.0, "Mars"))


def varga_d30_lord(longitude: float) -> str:
    """Trimsamsa. This varga yields a LORD directly, not a rasi.

    The Sun and the Moon own no trimsamsa, which is why the five lords are the
    five star-grahas only.
    """
    idx = _rasi_index(longitude)
    deg = longitude % 30.0
    table = TRIMSAMSA_ODD if _is_odd_rasi(idx) else TRIMSAMSA_EVEN
    for bound, lord in table:
        if deg < bound:
            return lord
    return table[-1][1]


def varga_d60(longitude: float) -> str:
    """Shashtyamsa: drop the rasis, double, divide by twelve, add one."""
    idx = _rasi_index(longitude)
    within = longitude % 30.0
    step = int((within * 2.0) // 1.0) % 12 + 1
    if _is_odd_rasi(idx):
        return RASIS[(idx + step - 1) % 12]
    return RASIS[(idx - step + 1) % 12]


VARGA_FUNCTIONS = {
    "D1": varga_d1, "D2": varga_d2, "D3": varga_d3, "D4": varga_d4,
    "D7": varga_d7, "D9": varga_d9, "D10": varga_d10, "D12": varga_d12,
    "D60": varga_d60,
}


def varga_lord(divisor: str, longitude: float) -> str:
    """The lord of the varga place, which is what every strength rule wants."""
    if divisor == "D30":
        return varga_d30_lord(longitude)
    return DOMICILE[VARGA_FUNCTIONS[divisor](longitude)]


def all_vargas(longitude: float) -> dict[str, str]:
    """Every encoded varga's place for one longitude, D30 given as its lord."""
    out = {d: fn(longitude) for d, fn in VARGA_FUNCTIONS.items()}
    out["D30"] = varga_d30_lord(longitude)
    return out


# -- the five-fold relation ----------------------------------------------

#: The temporal friendship, and it is SOURCED, not supplied: Varahamihira
#: states the houses outright at Brhajjataka 2.18 - friend in the 2nd, 12th,
#: 11th, 3rd, 10th and 4th, enemy in the 1st, 5th, 6th, 7th, 8th and 9th.
#: An earlier version of this module called the whole five-fold relation a
#: configured method. That was an overstatement, made by checking the strength
#: and varga packs and not the Brhajjataka planetary one.
TATKALIKA_FRIENDLY_HOUSES = (2, 3, 4, 10, 11, 12)
TATKALIKA_SOURCE = "Varahamihira, Brhajjataka 2.18"

#: The compound rule is a DISCLOSED CONVENTION, not a mined rule. The corpus
#: names adhimitra and adhisatru in its strength tables but no manifest in it
#: encodes how the two relations compound. This table is the standard one and
#: is labelled as supplied so a later source pass can confirm or replace it.
COMPOUND_RELATION = {
    ("friend", True): "adhimitra",
    ("friend", False): "sama",
    ("neutral", True): "mitra",
    ("neutral", False): "satru",
    ("enemy", True): "sama",
    ("enemy", False): "adhisatru",
}

COMPOUND_RELATION_DISCLOSURE = (
    "The five-fold relation (adhimitra ... adhisatru) is built from two "
    "SOURCED inputs and one supplied step. The natural relations are "
    "Varahamihira's at Brhajjataka 2.16-17, and the temporal ones are his at "
    "2.18 - friend in the 2nd, 12th, 11th, 3rd, 10th and 4th from a graha, "
    "enemy in the rest. What no manifest in this corpus states is how the two "
    "COMPOUND into the five tiers: natural friend plus temporal friend giving "
    "adhimitra, natural enemy plus temporal friend giving sama, and so on. "
    "That table alone is configured_method, and a source pass on BPHS "
    "adhyaya 3's maitri slokas can confirm or replace it."
)


def tatkalika_relation(a_rasi: int, b_rasi: int) -> bool:
    """True where the second graha stands in a temporally friendly house."""
    house = (b_rasi - a_rasi) % 12 + 1
    return house in TATKALIKA_FRIENDLY_HOUSES


def five_fold_relation(
    graha: str,
    lord: str,
    naisargika: dict[str, dict[str, list[str]]],
    rasi_index: dict[str, int],
) -> str:
    """The compound dignity of a graha toward the lord of a place."""
    if graha == lord:
        return "svaksetra"
    natural = naisargika.get(graha, {})
    if lord in natural.get("friends", []):
        base = "friend"
    elif lord in natural.get("enemies", []):
        base = "enemy"
    else:
        base = "neutral"
    a, b = rasi_index.get(graha), rasi_index.get(lord)
    if a is None or b is None:
        return {"friend": "mitra", "enemy": "satru", "neutral": "sama"}[base]
    return COMPOUND_RELATION[(base, tatkalika_relation(a, b))]


def saptavargaja_dignities(
    graha: str,
    longitude: float,
    naisargika: dict[str, Any],
    rasi_index: dict[str, int],
    exaltation_sign: str | None = None,
    moolatrikona: tuple[str, float, float] | None = None,
) -> list[str]:
    """The graha's dignity in each of the seven vargas sthana-bala wants.

    The recension is explicit that where the varga place is the graha's own
    exaltation the exaltation value is taken instead of the moolatrikona one,
    which is why exaltation is tested before anything else.
    """
    out: list[str] = []
    for divisor in ("D1", "D2", "D3", "D7", "D9", "D12", "D30"):
        if divisor == "D30":
            lord = varga_d30_lord(longitude)
            place = None
        else:
            place = VARGA_FUNCTIONS[divisor](longitude)
            lord = DOMICILE[place]
        if place is not None and exaltation_sign and place == exaltation_sign:
            out.append("uccha")
            continue
        if (
            place is not None
            and moolatrikona
            and place == moolatrikona[0]
            and graha == lord
        ):
            # Only the D1 place can fall inside the stated moolatrikona arc.
            if divisor == "D1" and moolatrikona[1] <= (longitude % 30.0) < moolatrikona[2]:
                out.append("moolatrikona")
                continue
        out.append(five_fold_relation(graha, lord, naisargika, rasi_index))
    return out


def vimsopaka_bala(
    graha: str,
    longitude: float,
    naisargika: dict[str, Any],
    rasi_index: dict[str, int],
    scheme: str = "saptavarga",
    exaltation_sign: str | None = None,
) -> dict[str, Any]:
    """The varga-vishva strength, out of twenty, for an encoded scheme.

    Only shadvarga and saptavarga are offered. The dasavarga and shodasavarga
    schemes need the six vargas whose computation slokas were not read, and
    an engine that quietly substituted for them would be inventing a number
    with a precise-looking denominator.
    """
    weights = VIMSOPAKA_SCHEMES[scheme]
    total = 0.0
    per_varga: dict[str, Any] = {}
    for divisor, weight in weights.items():
        if divisor == "D30":
            lord, place = varga_d30_lord(longitude), None
        else:
            place = VARGA_FUNCTIONS[divisor](longitude)
            lord = DOMICILE[place]
        if place is not None and exaltation_sign and place == exaltation_sign:
            dignity = "uccha"
        else:
            dignity = five_fold_relation(graha, lord, naisargika, rasi_index)
        vishvas = VIMSOPAKA_DIGNITY_VISHVAS[dignity] * weight / 20.0
        total += vishvas
        per_varga[divisor] = {
            "place": place, "lord": lord, "dignity": dignity,
            "vishvas": round(vishvas, 4),
        }
    grade = next(g for threshold, g in VIMSOPAKA_GRADES if total > threshold
                 or threshold == 0.0)
    return {
        "scheme": scheme,
        "total_vishvas": round(total, 4),
        "out_of": 20,
        "grade": grade,
        "per_varga": per_varga,
        "adhimitra_fork": ADHIMITRA_FORK,
        "relation_disclosure": COMPOUND_RELATION_DISCLOSURE,
    }
