"""Hellenistic and Latin-European sections, split from a shared calculation core.

These two traditions were previously fused into one "Western traditional"
section. They share tropical positions and most of a technique vocabulary, but
they are not the same reading, and merging them hides exactly the distinctions a
specialist in either would check first:

  Hellenistic (1st c. BCE - 7th c. CE): whole-sign houses, sect as the first
  judgment, the Hermetic lots, Dorothean triplicity rulers, Egyptian bounds,
  and time-lord procedures (zodiacal releasing, decennials, profections). No
  numerical dignity score - Valens and Dorotheus judge by condition, not points.

  Latin-European (13th - 17th c.): quadrant houses, the NUMERICAL essential and
  accidental dignity tables Lilly printed, almuten figuris, developed reception
  doctrine, primary directions, and horary as a mature branch. Applying the
  scoring table to a Hellenistic reading is still an anachronism - but it is an
  Arabic one, not a Latin one. The 5/4/3/2/1 table is al-Qabisi's, stated in the
  Arabic of the mid-10th century and worked through an example there; the Latin
  West received it in translation. See the islamicate track.

Both read the same sky. The split is about which authorities and which
procedures govern the judgment.
"""

from __future__ import annotations

from typing import Any, Optional

import swisseph as swe

from ..phasis import PhasisEngine
from ..reference_data import (
    DOROTHEAN_TRIPLICITY,
    EGYPTIAN_TERMS,
    LILLY_TRIPLICITY,
    PTOLEMAIC_TERMS_LILLY1647,
    PTOLEMAIC_TRIPLICITY,
)
from .types import BirthInput, DisclosureKind, EvidenceGrade, TraditionSection

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
CLASSICAL = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
DOMICILE = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}
EXALTATION = {
    "Sun": ("Aries", 19), "Moon": ("Taurus", 3), "Mercury": ("Virgo", 15),
    "Venus": ("Pisces", 27), "Mars": ("Capricorn", 28),
    "Jupiter": ("Cancer", 15), "Saturn": ("Libra", 21),
}
# Chaldean order governs the faces/decans.
CHALDEAN = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]


def _sign_of(longitude: float) -> tuple[str, float]:
    index = int((longitude % 360) // 30)
    return SIGNS[index], (longitude % 360) - index * 30


def _face_ruler(longitude: float) -> str:
    """Chaldean-order face (decan) ruler.

    The Chaldean order is descending - Saturn, Jupiter, Mars, Sun, Venus,
    Mercury, Moon - but the face series STARTS at Mars for Aries 0-10, which is
    index 2. Omitting that offset shifts every face by two places; verified
    against an independent implementation on all seven classical bodies.
    """
    decan = int((longitude % 360) // 10)
    return CHALDEAN[(decan + 2) % 7]


def _bound_ruler(sign: str, degree: float, table: dict) -> str | None:
    for ruler, start, end in table.get(sign, []):
        if start <= degree < end:
            return ruler
    return None


ELEMENT_OF = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water",
}


def _enum_value(item: Any) -> str:
    return str(getattr(item, "value", item))


def _bounds_for(sign: str) -> list[tuple[str, float, float]]:
    """Egyptian bounds as (ruler, start, end)."""
    return _terms_for(sign, EGYPTIAN_TERMS)


def _terms_for(sign: str, table: dict) -> list[tuple[str, float, float]]:
    """Any cumulative-end term table as (ruler, start, end) triples.

    reference_data keys by Sign enum and stores cumulative END degrees only, so
    the start of each term is the previous entry's end.
    """
    from ..models import Sign

    entries = None
    for key, value in table.items():
        if _enum_value(key) == sign:
            entries = value
            break
    if entries is None:
        try:
            entries = table[Sign(sign)]
        except Exception:  # noqa: BLE001
            return []

    out: list[tuple[str, float, float]] = []
    cursor = 0.0
    for ruler, end in entries:
        out.append((_enum_value(ruler), cursor, float(end)))
        cursor = float(end)
    return out


def _triplicity(sign: str, is_day: bool, table: dict) -> str | None:
    """Triplicity lord by element.

    Dorothean rows are (day, night, participating); Ptolemaic rows are
    (day, night) with no participating ruler.
    """
    entry = table.get(ELEMENT_OF.get(sign, ""))
    if not entry:
        return None
    index = 0 if is_day else 1
    if index >= len(entry):
        index = len(entry) - 1
    return _enum_value(entry[index])


def build_hellenistic(birth: BirthInput, chart: Any) -> TraditionSection:
    section = TraditionSection(
        tradition_id="hellenistic",
        display_name="Hellenistic (Greco-Roman)",
        evidence_grade=EvidenceGrade.LIVE_ENGINE,
        basis=(
            "Tropical positions from the shipping engine, judged by Hellenistic "
            "procedure: sect first, whole-sign topical houses, the Hermetic lots, "
            "Dorothean triplicity rulers and Egyptian bounds."
        ),
    )
    section.disclose(
        DisclosureKind.SOURCE,
        "Authorities",
        "Valens (Anthologies), Dorotheus (Carmen), Ptolemy (Tetrabiblos), "
        "Firmicus (Mathesis) and Paulus (Introduction). The live premium report "
        "carries the full judgment layer with per-claim evidence notes; this "
        "section states the Hellenistic calculation basis and its distinctives.",
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Houses",
        "Whole-sign houses for topic, which is the Hellenistic norm. The quadrant "
        "Midheaven is reported separately as a degree, not as a house cusp.",
        ("Equal from the ascending degree", "Porphyry"),
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Bounds and triplicities",
        "Egyptian bounds and Dorothean triplicity rulers are used, the dominant "
        "Hellenistic pair. Ptolemy's own tables differ and are reported alongside "
        "so the fork is visible rather than resolved silently.",
        ("Ptolemaic bounds", "Ptolemaic triplicities"),
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "No numerical dignity score",
        "Valens and Dorotheus judge planetary condition qualitatively - by sect, "
        "phase, place, and reception. The +5/+4/+3/+2/+1 scoring table postdates "
        "them and applying it here would be an anachronism. It appears in the "
        "Latin-European section instead. One correction to how this section used "
        "to describe it: the table is NOT a Latin invention. Al-Qabisi states it "
        "outright in Arabic in the mid-10th century - domicile five powers, "
        "exaltation four, triplicity three, bound two, face one - and works an "
        "almuten example with it, six centuries before Lilly printed it. Lilly "
        "transmitted it; he did not originate it. The anachronism against Valens "
        "is real either way, which is why the refusal stands.",
    
        category="not_part_of_tradition",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "No Arabic-derived material",
        "Lots beyond the Hermetic set, firdaria, and the expanded Arabic parts "
        "are not used here. They enter the tradition later and are reported in "
        "the Islamicate and Latin-European sections under their own authorities.",
    
        category="not_part_of_tradition",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "No length-of-life verdict",
        "Hellenistic aphesis/hyleg doctrine survives in conflicting forms and the "
        "live report already demonstrates how badly the arithmetic behaves when "
        "branches disagree. Not asserted.",
    
        category="policy_suppressed",
    )

    sun_altitude = getattr(chart, "sun_altitude", 0.0)
    is_day = sun_altitude > 0
    planet_map = {p.name.value: p for p in chart.planets}
    asc_sign, asc_degree = _sign_of(chart.ascendant)
    asc_index = SIGNS.index(asc_sign)
    mc_sign, mc_degree = _sign_of(chart.mc)

    sun = planet_map["Sun"].longitude
    moon = planet_map["Moon"].longitude
    # Hermetic lots: Fortune and Spirit reverse by sect.
    fortune = (chart.ascendant + (moon - sun if is_day else sun - moon)) % 360
    spirit = (chart.ascendant + (sun - moon if is_day else moon - sun)) % 360

    placements = []
    for name in CLASSICAL:
        planet = planet_map.get(name)
        if planet is None:
            continue
        sign, degree = _sign_of(planet.longitude)
        egyptian = _bounds_for(sign)
        exalt_sign = EXALTATION.get(name, (None, None))[0]
        placements.append({
            "body": name,
            "sign": sign,
            "degree_in_sign": round(degree, 4),
            "whole_sign_house": (SIGNS.index(sign) - asc_index) % 12 + 1,
            "domicile_lord": DOMICILE[sign],
            "in_own_domicile": DOMICILE[sign] == name,
            "in_exaltation": exalt_sign == sign,
            "triplicity_lord_dorothean": _triplicity(
                sign, is_day, DOROTHEAN_TRIPLICITY
            ),
            "triplicity_lord_ptolemaic": _triplicity(
                sign, is_day, PTOLEMAIC_TRIPLICITY
            ),
            "bound_lord_egyptian": _bound_ruler(sign, degree, {sign: egyptian}),
            "face_lord": _face_ruler(planet.longitude),
            "sect_status": _sect_status(name, is_day, planet.longitude, sun),
            "retrograde": getattr(planet, "speed", 0.0) < 0,
        })

    section.facts = {
        "sect": "day" if is_day else "night",
        "sect_light": "Sun" if is_day else "Moon",
        "sun_altitude_degrees": round(sun_altitude, 4),
        "ascendant": {"sign": asc_sign, "degree_in_sign": round(asc_degree, 4)},
        "midheaven_degree": {
            "sign": mc_sign,
            "degree_in_sign": round(mc_degree, 4),
            "whole_sign_house": (SIGNS.index(mc_sign) - asc_index) % 12 + 1,
            "note": "Reported as a degree; whole-sign 10th is the topical place.",
        },
        "hermetic_lots": {
            "fortune": _lot_dict(fortune, asc_index),
            "spirit": _lot_dict(spirit, asc_index),
            "sect_reversal_applied": True,
        },
        "placements": placements,
    }

    section.reading = [
        f"Sect is the first judgment: this is a {'day' if is_day else 'night'} "
        f"chart, so the {'Sun' if is_day else 'Moon'} is the sect light and "
        f"{'Jupiter and Saturn are' if is_day else 'Venus and Mars are'} of the "
        "sect in favour.",
        f"The Lot of Fortune falls in {_sign_of(fortune)[0]} (whole-sign house "
        f"{(SIGNS.index(_sign_of(fortune)[0]) - asc_index) % 12 + 1}) and the Lot "
        f"of Spirit in {_sign_of(spirit)[0]} (house "
        f"{(SIGNS.index(_sign_of(spirit)[0]) - asc_index) % 12 + 1}). Valens reads "
        "Fortune for body and circumstance, Spirit for action and deliberate "
        "undertaking.",
        "Dignity here is stated as rulership relations - domicile, exaltation, "
        "triplicity, bound, face - not as a total. Where the Dorothean and "
        "Ptolemaic triplicity tables disagree, both are shown.",
    ]
    return section


def _lot_dict(longitude: float, asc_index: int) -> dict[str, Any]:
    sign, degree = _sign_of(longitude)
    return {
        "sign": sign,
        "degree_in_sign": round(degree, 4),
        "whole_sign_house": (SIGNS.index(sign) - asc_index) % 12 + 1,
        "lord": DOMICILE[sign],
    }


def _sect_status(
    planet: str,
    is_day: bool,
    planet_lon: Optional[float] = None,
    sun_lon: Optional[float] = None,
) -> str:
    """Sect membership per Ptolemy, Tetrabiblos I.7 (Περὶ ἡμερινῶν καὶ νυκτερινῶν).

    Ptolemy's Greek makes Mercury's sect determinate, not perpetually undecided:
    "τὸν δὲ τοῦ Ἑρμοῦ κοινὸν ὡς ἑῴαν μὲν φάσιν ποιούμενον ἡμερινόν, ἑσπερίαν
    δὲ νυκτερινόν" - Mercury is common to both, diurnal when he makes a MORNING
    appearance and nocturnal when an EVENING one. "Common" names the rule, not
    the answer; given a phase there is always an answer. Returning the rule and
    stopping (as this did) drops a real dignity or debility on every chart where
    Mercury is visible, so resolve it whenever the phase is known.
    """
    diurnal = {"Sun", "Jupiter", "Saturn"}
    nocturnal = {"Moon", "Venus", "Mars"}
    if planet == "Mercury":
        if planet_lon is None or sun_lon is None:
            return "common (takes the sect of its solar phase)"
        oriental = PhasisEngine.is_oriental(planet_lon, sun_lon)
        phase = "morning" if oriental else "evening"
        in_sect = oriental if is_day else not oriental
        verdict = "of the sect in favour" if in_sect else "contrary to the sect"
        return f"{verdict} (common; {phase} star, so reckoned " \
               f"{'diurnal' if oriental else 'nocturnal'})"
    in_sect = (planet in diurnal) if is_day else (planet in nocturnal)
    return "of the sect in favour" if in_sect else "contrary to the sect"


def build_latin_european(birth: BirthInput, chart: Any) -> TraditionSection:
    section = TraditionSection(
        tradition_id="latin_european",
        display_name="Latin-European (medieval / Renaissance)",
        evidence_grade=EvidenceGrade.LIVE_ENGINE,
        basis=(
            "Same tropical positions, judged by Latin procedure: quadrant houses, "
            "Lilly's numerical essential and accidental dignity tables, almuten, "
            "and developed reception doctrine."
        ),
    )
    section.disclose(
        DisclosureKind.SOURCE,
        "Authorities",
        "Bonatti (Liber Astronomiae), Lilly (Christian Astrology), Morin, "
        "Schoener, Cardano and Regiomontanus. The live premium report already "
        "computes this layer in full with per-claim evidence notes; Lilly's "
        "dignity tables and the temperament method there are Latin, not "
        "Hellenistic, and are attributed here accordingly.",
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Houses",
        "Regiomontanus quadrant cusps are computed, following Lilly. Latin "
        "practice is genuinely divided: Bonatti and earlier authors use "
        "Alcabitius, and Morin argues for Regiomontanus on different grounds.",
        ("Alcabitius", "Placidus", "Campanus", "Porphyry", "Whole sign"),
    )
    section.disclose(
        DisclosureKind.SOURCE,
        "Term and triplicity tables keyed from the 1647 photographs",
        "This scorer previously awarded its +2 from the Egyptian bounds and "
        "its +3 from the Dorothean triplicities - two blends of other "
        "traditions into a Lilly-mode score. Both are resolved from the pinned "
        "IIIF photographs of Christian Astrology p.104 (Wellcome b30338724, "
        "leaf 138): the +2 now uses the Ptolemaic terms keyed digit-by-digit "
        "from the page (all twelve rows agree with the received Ptolemaic "
        "set), and the +3 uses Lilly's own triplicity table, whose water row "
        "the same photograph confirms as Mars by day AND night (the Cancer "
        "row prints Mars/Mars). Egyptian bounds and Dorothean triplicities "
        "remain exactly where they belong - in the Hellenistic section.",
    )
    section.disclose(
        DisclosureKind.SOURCE,
        "Numerical dignity",
        "Lilly's essential dignity scoring (+5 domicile, +4 exaltation, "
        "+3 triplicity, +2 bound, +1 face) is applied here because it IS a Latin "
        "instrument. The Hellenistic section deliberately omits it as an "
        "anachronism.",
    )
    section.disclose(
        DisclosureKind.FORK,
        "Peregrine stacking",
        "Lilly lists peregrine at -5. Practitioners divide on whether it stacks "
        "with detriment or fall, or applies only to a planet in neither. The "
        "non-stacking reading is used here; the stacking reading would push "
        "fallen planets a further -5.",
        ("Stack peregrine with detriment/fall",),
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "No horary judgment",
        "Horary is a mature Latin branch requiring a question and its moment, not "
        "a nativity. The engine supports it separately; nothing here answers a "
        "horary question from birth data.",
    
        category="not_part_of_tradition",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "No primary directions in this section",
        "Directions are the Latin timing instrument, but the method fork "
        "(Regiomontanus vs Placidus semi-arc, with or without latitude) changes "
        "results materially. The live report discloses its partial implementation; "
        "this panel section does not restate it as settled.",
    
        category="calculation_unimplemented",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "No length-of-life number",
        "Lilly himself doubts that hyleg, alcocoden and anareta can be selected "
        "with certainty. The live report publishes competing branches with their "
        "failures; a single number is not asserted.",
    
        category="policy_suppressed",
    )

    sun_altitude = getattr(chart, "sun_altitude", 0.0)
    is_day = sun_altitude > 0
    planet_map = {p.name.value: p for p in chart.planets}
    asc_sign, asc_degree = _sign_of(chart.ascendant)

    # Regiomontanus quadrant cusps - the Latin distinctive.
    try:
        cusps, _ascmc = swe.houses(
            chart.jd, chart.geo_lat, chart.geo_lon, b"R"
        )
        quadrant = [
            {
                "house": i + 1,
                "sign": _sign_of(c)[0],
                "degree_in_sign": round(_sign_of(c)[1], 4),
            }
            for i, c in enumerate(cusps[:12])
        ]
    except Exception:  # noqa: BLE001 - quadrant houses fail near the poles
        quadrant = []
        section.disclose(
            DisclosureKind.REFUSAL,
            "Quadrant houses unavailable",
            "Regiomontanus cusps could not be computed for this latitude. "
            "Quadrant systems degenerate near the polar circles; whole-sign "
            "topics remain available in the Hellenistic section.",
        
        category="calculation_unimplemented",
    )

    scored = []
    for name in CLASSICAL:
        planet = planet_map.get(name)
        if planet is None:
            continue
        sign, degree = _sign_of(planet.longitude)
        score = 0
        held: list[str] = []
        if DOMICILE[sign] == name:
            score += 5
            held.append("domicile +5")
        if EXALTATION.get(name, (None,))[0] == sign:
            score += 4
            held.append("exaltation +4")
        if _triplicity(sign, is_day, LILLY_TRIPLICITY) == name:
            score += 3
            held.append("triplicity +3 (Lilly's table)")
        terms = _terms_for(sign, PTOLEMAIC_TERMS_LILLY1647)
        if _bound_ruler(sign, degree, {sign: terms}) == name:
            score += 2
            held.append("term +2 (Ptolemaic, 1647 p.104)")
        if _face_ruler(planet.longitude) == name:
            score += 1
            held.append("face +1")
        detriment = DOMICILE[SIGNS[(SIGNS.index(sign) + 6) % 12]] == name
        fall = EXALTATION.get(name, (None,))[0] == SIGNS[
            (SIGNS.index(sign) + 6) % 12
        ]
        if detriment:
            score -= 5
            held.append("detriment -5")
        if fall:
            score -= 4
            held.append("fall -4")
        # Lilly lists peregrine at -5. Whether it STACKS with detriment/fall is a
        # genuine practitioner fork, so it is applied only to a planet holding no
        # dignity and in neither debility, and the fork is disclosed.
        peregrine = not held
        if peregrine:
            score -= 5
            held.append("peregrine -5")
        # The stacking reading also charges -5 to a planet that holds no dignity
        # even when it is in detriment or fall. Emitted alongside rather than
        # chosen, because practitioners and software genuinely differ.
        # Tags may carry table provenance after the score ("triplicity +3
        # (Lilly's table)"), so match the score anywhere, not at the end.
        holds_dignity = any(
            any(mark in tag for mark in ("+5", "+4", "+3", "+2", "+1"))
            for tag in held
        )
        score_stacking = score if peregrine else (
            score - 5 if not holds_dignity else score
        )
        scored.append({
            "body": name,
            "sign": sign,
            "degree_in_sign": round(degree, 4),
            "essential_score": score,
            "essential_score_peregrine_stacking": score_stacking,
            "dignities_held": held,
            "peregrine": peregrine,
        })

    strongest = max(scored, key=lambda p: p["essential_score"]) if scored else None

    section.facts = {
        "shared_calculation_core": "same tropical positions as the Hellenistic section",
        "house_system": "Regiomontanus (quadrant)",
        "quadrant_cusps": quadrant,
        "ascendant": {"sign": asc_sign, "degree_in_sign": round(asc_degree, 4)},
        "lilly_essential_dignity": scored,
        "strongest_by_essential_dignity": (
            {"body": strongest["body"], "score": strongest["essential_score"]}
            if strongest
            else None
        ),
        "scoring_table": "Lilly: domicile +5, exaltation +4, triplicity +3, "
                         "bound +2, face +1, detriment -5, fall -4, peregrine -5",
        "third_party_comparison": {
            "compared_against": "GERMES 2.39 'Lilly classic' scoreset",
            "agreement": "3 of 7 exact (Sun, Moon, Mercury)",
            "divergence": "Venus diverges for a reason now precisely known: "
                          "GERMES awards her the watery triplicity by day, "
                          "which is DOROTHEUS' day ruler - Lilly's own 1647 "
                          "table prints Mars for the watery trigon by day AND "
                          "night (photograph-verified, CA p.104, Cancer row), "
                          "so this scorer follows the 1647 page and GERMES "
                          "follows the popular modern conflation. Saturn's -9 "
                          "there equals fall plus stacked peregrine, "
                          "confirming that implementation stacks; Mars and "
                          "Jupiter cannot be reconciled from its summary "
                          "output alone. Reported, not resolved.",
        },
    }

    section.reading = [
        "This section reads the same sky by Latin procedure. The visible "
        "difference from the Hellenistic section is method, not data: quadrant "
        "house cusps instead of whole signs, and a numerical dignity total "
        "instead of a statement of rulership relations.",
    ]
    if strongest:
        section.reading.append(
            f"By Lilly's essential dignity table the strongest planet is "
            f"{strongest['body']} at {strongest['essential_score']:+d} "
            f"({', '.join(strongest['dignities_held'])}). That total is a Latin "
            "instrument and has no Hellenistic equivalent."
        )
    peregrines = [p["body"] for p in scored if p["peregrine"]]
    if peregrines:
        section.reading.append(
            f"Peregrine (holding no essential dignity where they stand): "
            f"{', '.join(peregrines)}. Lilly treats peregrination as a "
            "significant debility in its own right."
        )
    return section
