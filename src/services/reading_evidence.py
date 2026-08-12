"""Build the auditable evidence packet used to compose a premium nativity.

The customer narrative receives the complete *publishable* traditional chart,
not a miniature personality summary.  Every admitted fact carries an authority
label, a precise JSON provenance path, and an interpretive limit.  Direct
medical, legal, financial, emergency, and prescriptive remediation
material remains excluded; ordinary historical discussion of all twelve places
does not.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Any, Mapping
from src.engine.valens_delineations import (BOUND_QUALIFIER,
                                          BOUND_SIGN_NOTES,
                                          PLANET_COLOUR_TASTE,
                                          bound_delineation,
                                          lord_of_hour_delineation,
                                          lunar_phase_for)


SEPTENER = ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn")
PLANETARY_JOY_HOUSES = {
    "Mercury": 1,
    "Moon": 3,
    "Venus": 5,
    "Mars": 6,
    "Sun": 9,
    "Jupiter": 11,
    "Saturn": 12,
}
SIGN_RULERS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}
CUSTOMER_TOPICS = {
    1: "self, manner of action, and embodied presence",
    2: "livelihood and movable resources",
    3: "siblings, learning, messages, and local movement",
    4: "home, ancestry, land, and foundations",
    5: "creative work, pleasure, gifts, and children",
    6: "labor, service, dependency, toil, and burdens",
    7: "partnership and open contest",
    8: "shared obligations, inheritance, fear, and endings",
    9: "religion, study, divination, and long journeys",
    10: "action, rank, reputation, and career",
    11: "friends, patrons, hopes, and alliances",
    12: "retreat, confinement, loss, and hidden difficulty",
}
PAULUS_LOT_MEANINGS = {
    "Fortune": "body, life-course, possessions, reputation, and privilege",
    "Spirit": "soul, temper, mindfulness, power, and deliberate action",
    "Eros": "appetite, voluntary desire, friendship, and mutual favor",
    "Necessity": "constraint, submission, struggle, war, enmity, hatred, condemnation, and restriction",
    "Courage": "boldness, treachery, might, and villainy",
    "Victory": "trust, expectation, contest, association, penalties, and rewards",
    "Nemesis": "subterranean and cold fates, impotence, exile, destruction, grief, and the quality of death",
}
SOURCE_REGISTRY_PATH = Path(__file__).resolve().parents[1] / "database" / "data" / "doctrine_sources.json"

# Long-range timing coverage. The classical techniques are exact arithmetic and
# cost nothing to project forward, so the report covers the native's realistic
# remaining life rather than an arbitrary short slice. These are activation
# calendars, not event guarantees; the composer states that limit in prose.
#
# The horizon prefers the chart's own Alcocoden allotment of years, which is the
# tradition's own answer to "how far ahead does this nativity run". It is used
# only to bound a calendar; the report never presents it as a date of death, and
# a figure the engine marked invalid (below the native's attained age) is not
# used at all.
DEFAULT_HORIZON_AGE = 90
MIN_HORIZON_YEARS_AHEAD = 12


def _alcocoden_horizon_age(chart_data: Mapping[str, Any]) -> int:
    """Age at which the long-range activation calendars stop.

    DELIBERATELY INDEPENDENT OF THE LONGEVITY JUDGMENT.

    An earlier version bounded these calendars at the chart's own Alcocoden
    allotment. That was wrong on two counts:

      1. It published a death date by implication. A reader whose profection
         table simply stops at 2056 has been told something about 2056, and
         every inspected authority forbids exactly that. Lilly: the native may
         live the allotted years "if he met with no very obfiruftive
         direftions in the interim, or efcaped ludden caltuJties" — and he adds
         that "its not in Mans power politicly to fet downe the certaine number
         of yeeres". al-Biruni and Valens both frame the figure as a ceiling
         that stands only until an anaereta interferes.
      2. It made the calendar hostage to a technique this project has since
         shown to be unreliable in implementation (see scripts/validate_longevity.py).

    Profections, Firdaria, decennials and Zodiacal Releasing are deterministic
    calendars of activation. They cost nothing to project and carry no claim
    about survival, so they run to a fixed generous age for every native.
    """
    return DEFAULT_HORIZON_AGE


def _load_source_registry() -> Mapping[str, Any]:
    with SOURCE_REGISTRY_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


SOURCE_REGISTRY = _load_source_registry()


@dataclass(frozen=True)
class ReadingEvidence:
    id: str
    category: str
    fact: str
    authority: str
    source_rule_id: str
    verification_status: str
    provenance: str
    interpretive_limit: str
    details: dict[str, Any]

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _position(planet: Mapping[str, Any]) -> str:
    formatted = _mapping(planet.get("longitude_fmt"))
    return str(formatted.get("string") or planet.get("sign") or "unknown position")


def _dignity_description(planet: Mapping[str, Any]) -> str:
    dignity = _mapping(planet.get("dignities"))
    breakdown = _mapping(dignity.get("score_breakdown"))
    labels: list[str] = []
    for key, label in (
        ("domicile", "domicile"),
        ("exaltation", "exaltation"),
        ("triplicity", "triplicity"),
        ("term", "bound"),
        ("face", "face"),
        ("detriment", "detriment"),
        ("fall", "fall"),
    ):
        value = breakdown.get(key)
        if isinstance(value, (int, float)) and value != 0:
            labels.append(label)
    return ", ".join(labels) if labels else "no recorded essential dignity"


def _planet_condition_details(planet: Mapping[str, Any]) -> dict[str, Any]:
    """Select readable, non-sensitive condition fields from a forensic planet."""
    accidental = _mapping(planet.get("accidental"))
    phasis = _mapping(planet.get("phasis"))
    maltreatments = []
    for item in _sequence(planet.get("maltreatments")):
        if not isinstance(item, Mapping):
            continue
        maltreatments.append(
            {
                "condition": item.get("condition"),
                "malefic": item.get("malefic"),
                "description": item.get("description"),
                "severity": item.get("severity"),
            }
        )
    return {
        "dispositor": planet.get("dispositor"),
        "accidental_score": accidental.get("total_score"),
        "speed": planet.get("speed"),
        "is_oriental": planet.get("is_oriental"),
        "solar_elongation_deg": planet.get("solar_elongation_deg"),
        "phasis": phasis.get("phase"),
        "is_visible": phasis.get("is_visible"),
        "maltreatments": maltreatments,
        "sect_condition": dict(_mapping(planet.get("sect_condition"))),
    }


# Egyptian bounds as plain data, so the Ascendant's bound can be found without
# importing the dignity calculator into the evidence layer. Cumulative END
# degrees, mirroring EGYPTIAN_TERMS.
_SIGN_SEQUENCE = ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                  "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces")

# Valens III.15, p. 156: "In the OPPOSITION, through sevens of years; in the
# RIGHT TRINE, through the 9th; in the LEFT TRINE, through the 5th; in the
# RIGHT SQUARE, through the 10th; in the LEFT, through the 4th."
# Keyed by whole-sign separation from the Lot of Fortune to the malefic.
# Right-hand figures are the earlier (dexter) side, counted backwards in
# zodiacal order; left-hand the later (sinister) side.
_CLIMACTERIC_BY_FIGURE = {
    6: ("opposition", "sevens of years"),
    8: ("right trine", "the 9th year"),
    4: ("left trine", "the 5th year"),
    9: ("right square", "the 10th year"),
    3: ("left square", "the 4th year"),
}


_DOMICILE_BY_SIGN = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}


_EGYPTIAN_BOUNDS = {}


def _load_egyptian_bounds() -> None:
    from src.engine.reference_data import EGYPTIAN_TERMS
    for sign_key, rows in EGYPTIAN_TERMS.items():
        name = str(getattr(sign_key, "value", sign_key))
        _EGYPTIAN_BOUNDS[name] = [
            (str(getattr(p, "value", p)), float(limit)) for p, limit in rows
        ]


_load_egyptian_bounds()


def _place_tier(house: Any) -> str:
    """Valens's potency ranking of the places, IV.11, printed p. 176.

    "The BUSY and ACTIVE places are: the Ascendant, the Midheaven, the Good
     Daimon [11th], Good Fortune [5th], the Lot of Fortune, the Daimon, Eros,
     Necessity. MIDDLING: the God [9th], the Goddess [3rd], and the remaining
     two angles [7th, 4th]. MODERATE and INJURIOUS: the rest."

    This is the definition of chrematistikos, the term II.2 and II.22 both hang
    on; without it neither rule can be evaluated. Note Valens rates the 6th
    above the 12th "inasmuch as it holds a trine figure to the Midheaven",
    which this coarse three-way split does not express.
    """
    try:
        h = int(house)
    except (TypeError, ValueError):
        return "unranked"
    if h in (1, 10, 11, 5):
        return "busy"
    if h in (9, 3, 7, 4):
        return "middling"
    if h in (2, 6, 8, 12):
        return "injurious"
    return "unranked"


def _dispositor_chain(
    start: str, planets: Mapping[str, Mapping[str, Any]]
) -> tuple[list[str], str]:
    """Follow domicile dispositors until a final ruler, loop, or missing datum."""
    chain = [start]
    seen = {start}
    current = start
    for _ in range(len(SEPTENER) + 1):
        planet = planets.get(current)
        if not planet:
            return chain, "incomplete"
        disposer = planet.get("dispositor")
        if not disposer or disposer not in SEPTENER:
            return chain, "incomplete"
        disposer = str(disposer)
        if disposer == current:
            return chain, "final_dispositor"
        chain.append(disposer)
        if disposer in seen:
            return chain, "closed_loop"
        seen.add(disposer)
        current = disposer
    return chain, "incomplete"


_FIRDARIA_DAY_ORDER = [
    ("Sun", 10), ("Venus", 8), ("Mercury", 13), ("Moon", 9),
    ("Saturn", 11), ("Jupiter", 12), ("Mars", 7),
    ("North Node", 3), ("South Node", 2),
]
_FIRDARIA_NIGHT_ORDER = [
    ("Moon", 9), ("Saturn", 11), ("Jupiter", 12), ("Mars", 7),
    ("Sun", 10), ("Venus", 8), ("Mercury", 13),
    ("North Node", 3), ("South Node", 2),
]


def _firdaria_remaining_majors(
    chart_data: Mapping[str, Any], report_date: str
) -> list[dict[str, Any]]:
    """Project the Firdaria major-period sequence forward from the report date.

    The engine returns only the currently active period. The full sequence is
    fixed arithmetic from the birth date and sect, so the remaining chapters
    are derived here rather than left unanswerable for the customer.
    """
    analysis = _mapping(chart_data.get("analysis"))
    sect_type = str(_mapping(analysis.get("sect")).get("type") or "").upper()
    order = _FIRDARIA_DAY_ORDER if sect_type.startswith("DAY") else _FIRDARIA_NIGHT_ORDER
    birth_iso = str(_mapping(_mapping(chart_data.get("meta")).get("chart")).get("date") or "")
    if not birth_iso:
        return []
    try:
        birth = datetime.fromisoformat(birth_iso[:10])
        now = datetime.fromisoformat(report_date[:10])
    except ValueError:
        return []

    rows: list[dict[str, Any]] = []
    cursor_age = 0.0
    for lord, duration in order:
        start = birth + timedelta(days=cursor_age * 365.25)
        end = birth + timedelta(days=(cursor_age + duration) * 365.25)
        cursor_age += duration
        if end <= now:
            continue
        rows.append(
            {
                "lord": lord,
                "start": start.date().isoformat(),
                "end": end.date().isoformat(),
                "years": duration,
            }
        )
    return rows


def build_reading_evidence(chart_data: Mapping[str, Any]) -> list[ReadingEvidence]:
    analysis = _mapping(chart_data.get("analysis"))
    chart_meta = _mapping(_mapping(chart_data.get("meta")).get("chart"))
    report_date = str(chart_meta.get("report_date") or datetime.now(timezone.utc).isoformat())
    evidence: list[ReadingEvidence] = []

    def add(
        category: str,
        fact: str,
        fallback_authority: str,
        source_rule_id: str,
        provenance: str,
        limit: str,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        rule = _mapping(_mapping(SOURCE_REGISTRY.get("verified_rules")).get(source_rule_id))
        if rule:
            edition = _mapping(_mapping(SOURCE_REGISTRY.get("editions")).get(rule.get("edition_id")))
            authority = f"{edition.get('author')}, {edition.get('title')}, {rule.get('location')}"
            verification_status = str(rule.get("verification") or "text_verified")
        else:
            authority = fallback_authority
            verification_status = "configured_method_pending_primary_text_verification"
        evidence.append(
            ReadingEvidence(
                id=f"E{len(evidence) + 1}",
                category=category,
                fact=fact,
                authority=authority,
                source_rule_id=source_rule_id,
                verification_status=verification_status,
                provenance=provenance,
                interpretive_limit=limit,
                details=dict(details or {}),
            )
        )

    sect = _mapping(analysis.get("sect"))
    if sect.get("type"):
        add(
            "foundation",
            f"The chart is {sect['type']}; the computed Sun altitude is {float(sect.get('sun_altitude_deg', 0.0)):.2f} degrees.",
            "Ptolemy, Tetrabiblos; Dorotheus, Carmen",
            "sect_malefic_moderation",
            "analysis.sect",
            "Sect changes planetary moderation; it does not turn a malefic into a benefic.",
        )

    angles = _mapping(analysis.get("angles"))
    ascendant = _mapping(angles.get("Ascendant"))
    midheaven = _mapping(angles.get("Midheaven"))
    if ascendant and midheaven:
        asc_position = _mapping(ascendant.get("longitude_fmt")).get("string")
        mc_position = _mapping(midheaven.get("longitude_fmt")).get("string")
        add(
            "angles",
            (
                f"The Ascendant is {asc_position}. The astronomical Midheaven is {mc_position} in whole-sign house "
                f"{midheaven.get('house_wsh')}; whole-sign house 10 remains the topical place of action and rank."
            ),
            "Configured whole-sign angular framework",
            "whole_sign_topical_chain",
            "analysis.angles",
            (
                "The Ascendant begins the places. In whole-sign practice the degree of the Midheaven may fall outside "
                "the tenth sign, so its degree and the tenth place supply related but distinct testimony."
            ),
            {
                "ascendant_position": asc_position,
                "ascendant_sign": ascendant.get("sign"),
                "midheaven_position": mc_position,
                "midheaven_sign": midheaven.get("sign"),
                "midheaven_house": midheaven.get("house_wsh"),
            },
        )
    planets = {
        str(item.get("name")): item
        for item in _sequence(analysis.get("planets_forensic"))
        if isinstance(item, Mapping) and item.get("name") in SEPTENER
    }

    # Ptolemy, Tetrabiblos I.7, read from the Boll-Boer Greek: Mercury is common
    # to both sects, "diurnal when he makes a MORNING appearance, nocturnal when
    # an EVENING one." The phase is already computed; only the conclusion was
    # missing, so every chart reported Mercury as permanently undecided and
    # silently dropped a real dignity or debility.
    mercury = planets.get("Mercury")
    if mercury is not None and sect.get("type"):
        oriental = _planet_condition_details(mercury).get("is_oriental")
        if oriental is not None:
            is_day = str(sect["type"]).upper().startswith("DAY")
            mercury_diurnal = bool(oriental)
            in_sect = mercury_diurnal == is_day
            phase_word = "morning" if mercury_diurnal else "evening"
            verdict = "of the sect in favour" if in_sect else "contrary to the sect"
            add(
                "foundation",
                (
                    f"Mercury is {'a morning' if mercury_diurnal else 'an evening'} star, "
                    f"and is therefore reckoned "
                    f"{'diurnal' if mercury_diurnal else 'nocturnal'}; in this "
                    f"{str(sect['type']).lower()} chart Mercury is {verdict}."
                ),
                "Claudius Ptolemy, Apotelesmatika I.7, Boll-Boer Greek, source file lines 2498-2522",
                "ptolemy_sect_membership",
                "analysis.planets_forensic[Mercury].is_oriental",
                (
                    "Ptolemy makes Mercury's sect determinate from its solar phase. "
                    "'Common' names the rule, not the answer: given a phase there is always "
                    "an answer. This modifies Mercury's condition; it does not by itself "
                    "make Mercury strong or weak."
                ),
                {
                    "phase": phase_word,
                    "reckoned": "diurnal" if mercury_diurnal else "nocturnal",
                    "chart_sect": str(sect["type"]),
                    "in_sect": in_sect,
                },
            )

    # ------------------------------------------------------------------
    # The Lot of Fortune as a second Ascendant. Valens II.17, 79,7:
    #   "Before all one must precisely establish the Lot of Fortune ... For the
    #    Lot itself takes up the power of the ASCENDANT and of LIFE; the tenth
    #    from it, of MIDHEAVEN and REPUTATION."
    # topical.py has emitted places_from_fortune all along and nothing ever
    # surfaced it, so the layer Valens says to consult "before all" never
    # reached a reader.
    fortune_places = _mapping(_mapping(analysis.get("topical")).get("places_from_fortune"))
    fortune_entries = [
        _mapping(p) for p in _sequence(fortune_places.get("places")) if isinstance(p, Mapping)
    ]
    if fortune_entries:
        by_place = {int(p.get("place_from_fortune", 0)): p for p in fortune_entries}
        lot_itself = by_place.get(1)
        acquisition = by_place.get(11)

        if lot_itself and acquisition:
            lot_house = _place_tier(lot_itself.get("radical_house"))
            acq_house = _place_tier(acquisition.get("radical_house"))
            add(
                "fortune_derived",
                (
                    f"The Lot of Fortune falls in {lot_itself.get('sign')}, whole-sign house "
                    f"{lot_itself.get('radical_house')} ({lot_house}), ruled by "
                    f"{lot_itself.get('ruler')}. The Place of Acquisition — the eleventh from "
                    f"Fortune — is {acquisition.get('sign')}, whole-sign house "
                    f"{acquisition.get('radical_house')} ({acq_house}), ruled by "
                    f"{acquisition.get('ruler')}."
                ),
                "Vettius Valens, Anthologiae II.17 (79,7), II.20 (82,6) and II.22 (89), Kroll 1908 Greek",
                "valens_fortune_derived_places",
                "analysis.topical.places_from_fortune",
                (
                    "Valens judges the Lot of Fortune as a second Ascendant and reads wealth "
                    "over time by comparing it against the eleventh place from it. Place tiers "
                    "are his: busy (Asc, MC, 11th, 5th), middling (9th, 3rd, 7th, 4th), "
                    "injurious (2nd, 6th, 8th, 12th) - IV.11, 176. This is a placement "
                    "testimony, not a prediction of wealth."
                ),
                {
                    "fortune_sign": fortune_places.get("fortune_sign"),
                    "fortune_house": lot_itself.get("radical_house"),
                    "fortune_tier": lot_house,
                    "fortune_ruler": lot_itself.get("ruler"),
                    "acquisition_sign": acquisition.get("sign"),
                    "acquisition_house": acquisition.get("radical_house"),
                    "acquisition_tier": acq_house,
                    "acquisition_ruler": acquisition.get("ruler"),
                },
            )

            # Valens II.22, 89 reads the pair as a life-arc, and it is the only
            # rule in the corpus that uses the Acquisition place. It was
            # uninterpretable until II.20 defined the term.
            lot_ok = lot_house != "injurious"
            acq_ok = acq_house != "injurious"
            if lot_ok != acq_ok:
                if acq_ok:
                    verdict = (
                        "Fortune falls in an injurious place while the Acquisition does not. "
                        "Valens reads that as becoming better from a young age: what arrives "
                        "unbidden is obstructed, what is built through the Acquisition place is not."
                    )
                else:
                    verdict = (
                        "Fortune falls well while the Acquisition is afflicted. Valens reads "
                        "that as possessions diminishing as age advances."
                    )
                add(
                    "fortune_derived",
                    verdict,
                    "Vettius Valens, Anthologiae II.22, printed p. 89, Kroll 1908 Greek",
                    "valens_fortune_acquisition_arc",
                    "analysis.topical.places_from_fortune",
                    (
                        "A comparative placement rule about the direction of material fortune "
                        "over a life, not a promise of wealth or poverty. It says nothing about "
                        "amounts and nothing about a date. NOTE: the Acquisition place is a "
                        "fixed ten-sign offset from Fortune, so the two tiers are NOT "
                        "independent testimonies - they are one placement stated twice, and "
                        "must not be counted as separate agreeing evidence. The split occurs "
                        "for only four of the twelve possible Fortune placements (houses 4, 6, "
                        "10 and 12); on the other eight the rule is silent."
                    ),
                    {
                        "fortune_tier": lot_house,
                        "acquisition_tier": acq_house,
                        "direction": "improving" if acq_ok else "diminishing",
                    },
                )

    # Valens I.3, pp. 14-19 delineates all sixty bounds. We have always reported
    # the bound lord and said nothing about what it means. Only translated
    # bounds are emitted; an untranslated one produces silence rather than a
    # generic phrase, because at the point of use an invented delineation is
    # indistinguishable from a translated one.
    for name in SEPTENER:
        planet = planets.get(name)
        if not planet:
            continue
        variants = _mapping(_mapping(planet.get("dignities")).get("variants"))
        egyptian = _mapping(_mapping(variants.get("terms")).get("egyptian"))
        bound_lord = egyptian.get("ruler")
        sign_name = planet.get("sign")
        delineation = bound_delineation(sign_name, bound_lord)
        if not delineation:
            continue
        note = BOUND_SIGN_NOTES.get(str(sign_name))
        add(
            "bound_delineation",
            (
                f"{name} stands in {sign_name}, in the bound of {bound_lord}. "
                f"Valens delineates that bound: {delineation}."
                + (" " + note if note else "")
            ),
            "Vettius Valens, Anthologiae I.3, printed pp. 14-19, Kroll 1908 Greek",
            "valens_bound_delineations",
            f"analysis.planets_forensic[{name}].dignities.variants.terms.egyptian.ruler",
            (
                "A delineation of the DEGREES, not a verdict on the person. Valens attaches "
                "conditions constantly and they decide the outcome - Sagittarius in Mercury's "
                "bound gives philosophers 'when Mercury inclines' and soldiers 'when Mars'; "
                "Capricorn in Jupiter's bound produces BOTH reputation and disrepute. Quoting "
                "the substrate without the condition is quoting half a sentence. The bound is "
                "one testimony among many and is outweighed by placement and sect. "
                + BOUND_QUALIFIER
            ),
            {
                "planet": name,
                "sign": sign_name,
                "bound_lord": bound_lord,
                "bound_system": "Egyptian (the set Valens uses)",
            },
        )

    # Valens II.4, pp. 60-62: the planet "allotted the hour" (ruling the
    # Ascendant) or ruling the Lot of Fortune, with witness clauses that
    # double, redirect or reverse the base verdict.
    _asc_lon_early = _mapping(_mapping(analysis.get("angles")).get("Ascendant")).get("longitude")
    try:
        asc_sign_for_lord = (
            _SIGN_SEQUENCE[int(float(_asc_lon_early) // 30) % 12]
            if _asc_lon_early is not None
            else None
        )
    except (TypeError, ValueError):
        asc_sign_for_lord = None
    fortune_sign_name = str(fortune_places.get("fortune_sign") or "") or None
    for role, sign_name in (("Ascendant", asc_sign_for_lord), ("Lot of Fortune", fortune_sign_name)):
        if not sign_name:
            continue
        ruler = _DOMICILE_BY_SIGN.get(sign_name)
        ruler_planet = planets.get(str(ruler)) if ruler else None
        if ruler_planet is None or not ruler_planet.get("sign"):
            continue
        r_sign = str(ruler_planet.get("sign"))
        if r_sign not in _SIGN_SEQUENCE:
            continue
        witnesses = []
        for other in SEPTENER:
            if other == ruler:
                continue
            op = planets.get(other)
            if not op or not op.get("sign") or str(op.get("sign")) not in _SIGN_SEQUENCE:
                continue
            d = (_SIGN_SEQUENCE.index(str(op.get("sign"))) - _SIGN_SEQUENCE.index(r_sign)) % 12
            if d in (0, 2, 3, 4, 6, 8, 9, 10):
                witnesses.append(other)
        found = lord_of_hour_delineation(ruler, witnesses)
        if not found:
            continue
        base, clauses = found
        add(
            "lord_of_hour",
            (
                f"{ruler} rules the {role}. Valens: {base}."
                + ("".join(" " + c.capitalize() + "." for c in clauses) if clauses else "")
            ),
            "Vettius Valens, Anthologiae II.4, printed pp. 60-62, Kroll 1908 Greek",
            "valens_lord_of_hour_or_lot",
            f"analysis.planets_forensic[{ruler}]",
            (
                "The base verdict and the witness clauses are reported separately because "
                "Valens's clauses reverse the outcome as often as they strengthen it - Saturn "
                "prospers 'provided Mars does not oppose', and with Mars gives disturbances "
                "instead. A modified verdict must never be presented as the base one."
            ),
            {
                "role": role,
                "ruler": ruler,
                "witnesses": witnesses,
                "clauses_applied": len(clauses),
            },
        )

    # Valens II.37 (pp. 114-117) and II.38 (pp. 119-121). Marriage is judged
    # from the 7th sign AND from Venus's condition, dispositor and witnesses.
    # Each test below is one of his named conditions; all inputs were already
    # computed and none were being applied to this topic.
    venus = planets.get("Venus")
    if venus is not None:
        tests: list[str] = []
        details_out: Dict[str, Any] = {}

        # "if her lord is setting, or in the BAD-DAIMON place ... it makes
        #  people unfortunate about marriages and transactions"
        v_disp = _planet_condition_details(venus).get("dispositor")
        disp_planet = planets.get(str(v_disp)) if v_disp else None
        if disp_planet is not None and disp_planet.get("house") == 12:
            tests.append(
                f"Venus's dispositor {v_disp} stands in the twelfth place, which Valens names "
                f"the Bad Daimon. He reads that as unfortunate about marriages and transactions"
            )
            details_out["dispositor_in_12th"] = v_disp

        # "The Moon set under the beams is not good for marriage."
        moon_p = planets.get("Moon")
        if moon_p is not None:
            solar = str(moon_p.get("solar_status") or "").upper()
            if "COMBUST" in solar or "UNDER" in solar:
                tests.append(
                    "the Moon is under the Sun's beams, which Valens states is not good for marriage"
                )
                details_out["moon_under_beams"] = True

        # "Saturn OVERLOOKING Venus makes people for the most part unmarried
        #  and hard to deal with." Overcoming = Saturn in the 10th sign from her.
        saturn_p = planets.get("Saturn")
        v_sign, s_sign = str(venus.get("sign") or ""), str((saturn_p or {}).get("sign") or "")
        if v_sign in _SIGN_SEQUENCE and s_sign in _SIGN_SEQUENCE:
            sep = (_SIGN_SEQUENCE.index(s_sign) - _SIGN_SEQUENCE.index(v_sign)) % 12
            if sep == 9:
                tests.append(
                    "Saturn stands in the tenth sign from Venus, overcoming her - the figure "
                    "Valens says makes people for the most part unmarried and hard to deal with"
                )
                details_out["saturn_overcomes_venus"] = True
            elif sep in (3, 6):
                tests.append(
                    "Saturn regards Venus by "
                    + ("opposition" if sep == 6 else "square")
                    + ", which Valens counts as Saturn overlooking her"
                )
                details_out["saturn_regards_venus"] = "opposition" if sep == 6 else "square"
            elif sep == 0:
                # Co-presence, not an aspect. Valens keeps the two distinct
                # (synparousia vs epiblepein), so it is named as what it is.
                tests.append(
                    "Saturn is co-present with Venus in the same sign - closer contact than the "
                    "aspects Valens names, though he treats co-presence as a separate category"
                )
                details_out["saturn_copresent_with_venus"] = True

        # "Venus in SATURN'S SIGN OR BOUNDS" is one of the named conditions of
        # II.37's severe branch, alongside the aspect. Omitting it missed the
        # single most specific Saturn-Venus contact a chart can have.
        v_terms = _mapping(_mapping(_mapping(venus.get("dignities")).get("variants")).get("terms"))
        v_bound_lord = _mapping(v_terms.get("egyptian")).get("ruler")
        if str(v_bound_lord) == "Saturn":
            tests.append(
                "Venus stands in Saturn's own bound, a condition Valens names explicitly "
                "alongside the aspect"
            )
            details_out["venus_in_saturn_bound"] = True
        if v_sign in ("Capricorn", "Aquarius"):
            tests.append(f"Venus stands in Saturn's own sign, {v_sign}")
            details_out["venus_in_saturn_sign"] = True

        if tests:
            # The escape clause. Valens attaches it ONLY to the extreme outcome
            # ("altogether widows and virgins"), which requires the absence of
            # ALL THREE of Mars, Jupiter and Mercury. It does not soften the
            # milder statements, and reading it onto them is a documented error.
            witnesses = []
            for w in ("Mars", "Jupiter", "Mercury"):
                wp = planets.get(w)
                if wp is None or not wp.get("sign"):
                    continue
                w_sign = str(wp.get("sign"))
                if w_sign not in _SIGN_SEQUENCE or v_sign not in _SIGN_SEQUENCE:
                    continue
                d = (_SIGN_SEQUENCE.index(w_sign) - _SIGN_SEQUENCE.index(v_sign)) % 12
                if d in (0, 2, 3, 4, 6, 8, 9, 10):
                    witnesses.append(w)
            details_out["mitigating_witnesses"] = witnesses
            clause = (
                (
                    " Valens's severest outcome requires that NONE of Mars, Jupiter or Mercury "
                    "witness Venus; here " + ", ".join(witnesses) + " "
                    + ("does" if len(witnesses) == 1 else "do")
                    + ", so that branch is closed by his own wording."
                )
                if witnesses
                else (
                    " None of Mars, Jupiter or Mercury witnesses Venus, so Valens's severest "
                    "branch is not excluded by the condition he attaches to it."
                )
            )
            add(
                "marriage_testimony",
                "On the place of marriage: " + "; ".join(tests) + "." + clause,
                "Vettius Valens, Anthologiae II.37 (pp. 114-117) and II.38 (pp. 119-121), Kroll 1908 Greek",
                "valens_marriage_tests",
                "analysis.planets_forensic[Venus]",
                (
                    "Named placement tests, not a forecast about any relationship. The escape "
                    "clause governs ONLY the sentence it appears in - Valens attaches it to the "
                    "extreme outcome alone, and carrying it up to the milder statements is "
                    "unsupported. Marriage is also read from the 7th sign, which these tests do "
                    "not replace."
                ),
                details_out,
            )

    # Valens II.2, printed pp. 56-57. The sect light's triplicity rulers divide
    # the life: the FIRST governs the earlier portion, the SECOND the later.
    # analysis.triplicity_periods already returns exactly these three rulers and
    # even labels their temporal roles; nothing read them.
    trip = _mapping(analysis.get("triplicity_periods"))
    rulers = _mapping(trip.get("rulers"))
    first_r, second_r = rulers.get("first"), rulers.get("second")
    if first_r and second_r:
        def _standing(pname: str) -> tuple[str, Optional[int]]:
            pl = planets.get(str(pname))
            if not pl:
                return "unranked", None
            house = pl.get("house")
            return _place_tier(house), house

        first_tier, first_house = _standing(first_r)
        second_tier, second_house = _standing(second_r)
        order = {"busy": 2, "middling": 1, "injurious": 0, "unranked": 1}
        arc = None
        if order[first_tier] < order[second_tier]:
            arc = (
                "The first ruler stands in a weaker place than the second. Valens reads that as "
                "irregularities in the earlier portion of life, becoming effective afterwards - "
                "though passed, in his words, unstably and fearfully."
            )
        elif order[first_tier] > order[second_tier]:
            arc = (
                "The first ruler stands in a stronger place than the second. Valens reads that as "
                "being brought out well in the earlier years and afterwards pulled down."
            )
        add(
            "life_arc",
            (
                f"The sect light is {trip.get('sect_light')} in {trip.get('sect_light_sign')}, "
                f"the {str(trip.get('element') or '').lower()} triangle. Its rulers are "
                f"{first_r} (first, governing the earlier portion of life, in house "
                f"{first_house} - {first_tier}) and {second_r} (second, governing the later, "
                f"in house {second_house} - {second_tier}), with {rulers.get('participant')} "
                f"participating." + (" " + arc if arc else "")
            ),
            "Vettius Valens, Anthologiae II.1 (54,4) and II.2 (56,16-57), Kroll 1908 Greek",
            "valens_triplicity_life_arc",
            "analysis.triplicity_periods",
            (
                "Valens judges each ruler by place - angular or busy gives fortunate and brilliant, "
                "succedent middling, cadent low and unfortunate - and divides the life between the "
                "first and second. It describes a SHAPE, not dated events, and it names no hinge "
                "year: Valens puts the turn at 'the ascension of the sign', which depends on the "
                "birth latitude and is not computed here."
            ),
            {
                "sect_light": trip.get("sect_light"),
                "element": trip.get("element"),
                "first_ruler": first_r,
                "first_tier": first_tier,
                "second_ruler": second_r,
                "second_tier": second_tier,
                "participant": rulers.get("participant"),
                "direction": (
                    "improving" if arc and "afterwards" in arc and "pulled down" not in arc
                    else "declining" if arc else "level"
                ),
            },
        )

    # Valens II.27, printed pp. 94-95: a distinct timing system, and it splits
    # the significators by QUESTION - life from the Ascendant and Moon, action
    # and reputation from Fortune, Spirit, the Sun and the syzygy. We run one
    # undifferentiated timeline.
    add(
        "timing_method",
        (
            "Valens assigns different significators to different questions of timing: for the "
            "times OF LIFE, the Ascendant and the Moon, or the signs their lords occupy; for "
            "ACTION and REPUTATION, the Lot of Fortune, the Lot of Spirit, the Sun, the prenatal "
            "syzygy, and the exaltation and its lord. Period lengths come from the ascensional "
            "time of the sign or the planet's own cyclic period, and the places hand over in "
            "rank order - the angles first, then the succedents, then the cadents, empty places "
            "being skipped."
        ),
        "Vettius Valens, Anthologiae II.27, printed pp. 94-95, Kroll 1908 Greek",
        "valens_time_distribution",
        "analysis.enhanced_profections",
        (
            "A statement of METHOD - which significators answer which question - not a forecast. "
            "Valens carries at least eight distinct timing systems and ranks none of them, "
            "because he held that the method must be fitted to the chart and said he ran out of "
            "life to determine which was right."
        ),
        {
            "life_significators": ["Ascendant", "Moon"],
            "action_significators": ["Fortune", "Spirit", "Sun", "syzygy", "exaltation lord"],
            "handover_order": ["angles", "succedents", "cadents"],
        },
    )

    # Valens I.1 (pp. 1-5) and II.30 (p. 101): several topics carry MORE THAN
    # ONE significator, and the engine has been treating each too narrowly.
    # The Moon signifies the mother AND Venus "signifies mother and nourishment";
    # II.30 confirms it - "likewise VENUS the maternal place, AND THE MOON".
    # Siblings run three deep: the Moon (elder brother), Jupiter (brotherhood)
    # and Mercury, "lord of brothers and of younger children".
    add(
        "second_significators",
        (
            "The mother has two significators in this tradition, not one: the Moon, and Venus, "
            "who 'signifies mother and nourishment'. Siblings have three: the Moon for the elder "
            "brother, Jupiter for brotherhood, and Mercury, 'lord of brothers and of younger "
            "children'. The father is the Sun, and in second place Saturn."
        ),
        "Vettius Valens, Anthologiae I.1 (pp. 1-5) and II.30 (p. 101), Kroll 1908 Greek",
        "valens_second_significators",
        "reference: Valens I.1, II.30",
        (
            "A rule about WHICH planets to weigh for a topic, not a statement about the reader's "
            "family. Valens judges the parents by asking which of Sun, Saturn, Moon and Venus is "
            "more afflicted or has fallen away - a comparison that is impossible if only one "
            "significator per parent is admitted."
        ),
        {
            "mother": ["Moon", "Venus"],
            "father": ["Sun", "Saturn"],
            "siblings": ["Moon", "Jupiter", "Mercury"],
        },
    )

    # Valens III.15, printed p. 156: the climacteric PERIODICITY is set by which
    # aspect a malefic throws at the Lot of Fortune. Not implemented anywhere.
    if fortune_entries:
        lot_sign = str(fortune_places.get("fortune_sign") or "")
        lot_idx = _SIGN_SEQUENCE.index(lot_sign) if lot_sign in _SIGN_SEQUENCE else None
        if lot_idx is not None:
            cycles = []
            for malefic in ("Saturn", "Mars"):
                mp = planets.get(malefic)
                if not mp or not mp.get("sign"):
                    continue
                msign = str(mp.get("sign"))
                if msign not in _SIGN_SEQUENCE:
                    continue
                sep = (_SIGN_SEQUENCE.index(msign) - lot_idx) % 12
                figure = _CLIMACTERIC_BY_FIGURE.get(sep)
                if figure:
                    cycles.append((malefic, figure[0], figure[1]))
            if cycles:
                described = "; ".join(
                    f"{m} stands in {fig} to the Lot, giving a cycle of {per}"
                    for m, fig, per in cycles
                )
                add(
                    "climacteric",
                    (
                        f"Valens derives the climacteric periodicity from the figure a malefic "
                        f"throws at the Lot of Fortune. {described}."
                    ),
                    "Vettius Valens, Anthologiae III.15, printed p. 156, Kroll 1908 Greek",
                    "valens_lot_climacterics",
                    "analysis.topical.places_from_fortune",
                    (
                        "A periodicity, not a list of dated events. Valens gives it as 'especially "
                        "when malefics are with, or witness, Fortune' - so it applies where such a "
                        "figure exists and is silent otherwise. It names an interval, never an outcome."
                    ),
                    {"cycles": [{"malefic": m, "figure": f, "period": p} for m, f, p in cycles]},
                )

    # Valens V.1, printed pp. 207-209, Kroll 1908 Greek: the "causative place"
    # (αἰτιατικὸς τόπος), a Lot built from Saturn and Mars alone - day the arc
    # Saturn->Mars projected from the Ascendant, night Mars->Saturn - which
    # Valens says is "responsible for fears and dangers and bonds/imprisonment."
    # He tests it the same way III.15 tests the Lot of Fortune: whether a
    # malefic owns the resulting sign, or aspects it.
    saturn_p = planets.get("Saturn")
    mars_p = planets.get("Mars")
    if saturn_p and mars_p and saturn_p.get("sign") and mars_p.get("sign"):
        is_day_causative = str(sect.get("type") or "").upper().startswith("DAY")
        try:
            sat_lon = float(saturn_p.get("longitude", 0.0))
            mar_lon = float(mars_p.get("longitude", 0.0))
            asc_lon = float(_mapping(_mapping(analysis.get("angles")).get("Ascendant")).get("longitude", 0.0))
        except (TypeError, ValueError):
            asc_lon = None
        if asc_lon is not None:
            if is_day_causative:
                cp_lon = (asc_lon + mar_lon - sat_lon) % 360.0
            else:
                cp_lon = (asc_lon + sat_lon - mar_lon) % 360.0
            cp_sign = _SIGN_SEQUENCE[int(cp_lon / 30.0) % 12]
            owner_malefic = None
            for malefic, msign in (("Saturn", str(saturn_p.get("sign"))), ("Mars", str(mars_p.get("sign")))):
                if msign == cp_sign:
                    owner_malefic = malefic
            add(
                "causative_place",
                (
                    f"The causative place (Saturn-Mars, projected from the Ascendant by sect) "
                    f"falls in {cp_sign} at {cp_lon:.2f} degrees."
                    + (
                        f" {owner_malefic} owns that sign, which is the testimony Valens says makes "
                        f"the place active rather than latent."
                        if owner_malefic
                        else " Neither malefic owns that sign; Valens's own test for whether this "
                        "place is active is silent here."
                    )
                ),
                "Vettius Valens, Anthologiae V.1, printed pp. 207-209, Kroll 1908 Greek",
                "valens_causative_place",
                "analysis.planets_forensic[Saturn,Mars]; analysis.angles.Ascendant",
                (
                    "A place Valens tests for malefic ownership or aspect, not a verdict about the "
                    "reader. He states its topic directly - fears, dangers, confinement - as the "
                    "SUBJECT the place concerns when active; whether it activates depends on the "
                    "malefic testimony, which this reports rather than assumes."
                ),
                {"sign": cp_sign, "longitude": round(cp_lon, 2), "owner_malefic": owner_malefic},
            )

    # Valens V.2, printed p. 210: the climacteric YEAR. Profect one sign per
    # year from the ascendant; where the profected sign is the pre-natal
    # syzygy's sign, or its square or opposition, Valens calls the year
    # "climacteric and disturbed". Distinct from III.15 above, which derives a
    # climacteric PERIODICITY from a malefic's figure to the Lot of Fortune -
    # that names an interval, this names specific years.
    syzygy_lon_raw = _mapping(
        _mapping(analysis.get("syzygy")).get("prenatal_syzygy")
    ).get("longitude")
    asc_sign_name = str(ascendant.get("sign") or "")
    if syzygy_lon_raw is not None and asc_sign_name in _SIGN_SEQUENCE:
        try:
            syz_lon = float(syzygy_lon_raw)
        except (TypeError, ValueError):
            syz_lon = None
        if syz_lon is not None:
            syz_sign = _SIGN_SEQUENCE[int(syz_lon / 30.0) % 12]
            asc_idx = _SIGN_SEQUENCE.index(asc_sign_name)
            syz_idx = _SIGN_SEQUENCE.index(syz_sign)
            # Ages 0-90 whose profected sign is conjunct/square/opposite the syzygy.
            hits = []
            for age in range(0, 91):
                prof_idx = (asc_idx + age) % 12
                sep = (prof_idx - syz_idx) % 12
                if sep in (0, 3, 6, 9):
                    hits.append(age)
            if hits:
                shown = ", ".join(str(a) for a in hits[:14])
                more = f" (and {len(hits) - 14} further)" if len(hits) > 14 else ""
                add(
                    "climacteric_year",
                    (
                        f"The lunation before birth was a {str(_mapping(_mapping(analysis.get('syzygy')).get('prenatal_syzygy')).get('type', '')).lower() or 'syzygy'} "
                        f"moon in {syz_sign}. Profecting one sign per year from the {asc_sign_name} "
                        f"ascendant, the years that fall on that sign or its square or opposition "
                        f"are ages {shown}{more}."
                    ),
                    "Vettius Valens, Anthologiae V.2, printed p. 210, Kroll 1908 Greek",
                    "valens_syzygy_climacteric",
                    "analysis.syzygy.prenatal_syzygy; analysis.angles.Ascendant",
                    (
                        "A list of years the method marks, not a forecast of events in them. "
                        "Valens calls such a year 'climacteric and disturbed' and names one "
                        "aggravating witness - transiting Saturn in a cadent place - which is a "
                        "per-year transit and is not evaluated here. The years recur on a fixed "
                        "three-year lattice because the rule is arithmetic, so their number says "
                        "nothing about how hard a life is."
                    ),
                    {
                        "syzygy_sign": syz_sign,
                        "ascendant_sign": asc_sign_name,
                        "climacteric_ages": hits,
                    },
                )

    # Valens VI.5-6, printed pp. 251-254: the decennial cascade. Major periods
    # of 129 months (10y 9m) in Chaldean order from the sect light, each
    # subdivided among all seven in proportion to their minor years. The
    # arithmetic self-verifies - the minor years sum to 129, which IS the major
    # period in months - and reproduces Valens's own worked Saturn example.
    sect_light_planet = "Sun" if str(sect.get("type") or "").upper().startswith("DAY") else "Moon"
    try:
        from src.engine.valens_periods import decennial_cascade

        cascade = decennial_cascade(sect_light=sect_light_planet, levels=1, count=7)
    except Exception:  # pragma: no cover - defensive, never blocks a reading
        cascade = None
    if cascade:
        seq = " -> ".join(
            f"{p['ruler']} (from age {p['start_age']:.2f})" for p in cascade["periods"][:5]
        )
        add(
            "decennial_cascade",
            (
                f"Valens's decennial division runs in periods of 10 years 9 months - 129 months, "
                f"which is exactly the sum of the seven planets' minor years. Ordered from the "
                f"sect light ({sect_light_planet}): {seq}."
            ),
            "Vettius Valens, Anthologiae VI.5-6, printed pp. 251-254, Kroll 1908 Greek",
            "valens_decennial_cascade",
            "analysis.sect",
            (
                "A division of time, not a set of predictions. Valens presents this as a method he "
                "recovered himself after finding it discarded. The SUBDIVISION arithmetic is "
                "confirmed against his own worked example, but WHICH planet opens the sequence is "
                "configured from the sect light and is not yet verified against the Greek - so the "
                "order of the rulers should be treated as provisional even though the period "
                "lengths are exact."
            ),
            {
                "major_period_months": cascade["major_period_months"],
                "order": cascade["order"],
                "starting_planet_verified": False,
            },
        )

    # Valens II.35, pp. 106-108: eleven lunar configurations, each with the
    # topic it signifies and the planet prevailing through it. The engine
    # emitted a single undifferentiated lunar_cycle item.
    moon = planets.get("Moon")
    if moon is not None:
        elongation = _planet_condition_details(moon).get("solar_elongation_deg")
        phase = lunar_phase_for(elongation)
        if phase:
            lord_clause = (
                f" {phase['lord']} prevails through it."
                if phase.get("lord")
                else ""
            )
            add(
                "lunar_phase",
                (
                    f"The Moon stands at the {phase['name']}, "
                    f"{float(elongation):.1f} degrees from the Sun. "
                    f"Valens assigns that configuration to {phase['signifies']}.{lord_clause}"
                ),
                "Vettius Valens, Anthologiae II.35, printed pp. 106-108, Kroll 1908 Greek",
                "valens_lunar_configurations",
                "analysis.planets_forensic[Moon].solar_elongation_deg",
                (
                    "Valens divides the lunar month into eleven named configurations and gives "
                    "each a topic and a ruling planet. The waxing half-moon carries injury and "
                    "violent happenings; the waning half-moon carries old matters and "
                    "long-lasting afflictions, under Saturn - acute against chronic. This is a "
                    "topical assignment, not a prediction."
                ),
                {
                    "phase": phase["name"],
                    "elongation_deg": round(float(elongation), 2),
                    "lord": phase.get("lord"),
                },
            )

    # Valens I.1, pp. 1-5. Each planet's schema closes with sect, colour and
    # taste. The pair is complete across all seven and had never been carried.
    colour_lines = []
    for name in SEPTENER:
        entry = PLANET_COLOUR_TASTE.get(name) or {}
        if entry.get("colour") and entry.get("taste"):
            colour_lines.append(
                f"{name}: in colour {entry['colour']}, in taste {entry['taste']}"
            )
    if colour_lines:
        add(
            "planetary_qualities",
            "Valens closes each planet's account with a colour and a taste. " + "; ".join(colour_lines) + ".",
            "Vettius Valens, Anthologiae I.1, printed pp. 1-5, Kroll 1908 Greek",
            "valens_planet_colour_taste",
            "reference: src/engine/valens_delineations.PLANET_COLOUR_TASTE",
            (
                "A complete and systematic attribute set in the source, recorded for fidelity. "
                "It is a property of the PLANETS, not of the reader, and carries no judgment "
                "about the chart. Mercury's pair was not preserved in the passage as read and "
                "is therefore omitted rather than guessed."
            ),
            {"planets_carried": len(colour_lines), "planets_total": len(SEPTENER)},
        )

    # The Ascendant's own bound. Valens singles it out at I.3, p.15 for Virgo -
    # "generally the whole of Virgo, but ESPECIALLY these degrees" - and it is
    # the most personal degree in the figure, so it must not be omitted just
    # because the loop above walks planets.
    asc_map = _mapping(_mapping(analysis.get("angles")).get("Ascendant"))
    asc_lon = asc_map.get("longitude")
    if asc_lon is not None:
        try:
            asc_sign_name = _SIGN_SEQUENCE[int(float(asc_lon) // 30) % 12]
            asc_deg = float(asc_lon) % 30.0
            asc_bound = None
            for planet_name, limit in _EGYPTIAN_BOUNDS.get(asc_sign_name, []):
                if asc_deg < limit:
                    asc_bound = planet_name
                    break
            asc_delineation = bound_delineation(asc_sign_name, asc_bound)
            if asc_delineation:
                add(
                    "bound_delineation",
                    (
                        f"The Ascendant stands in {asc_sign_name}, in the bound of {asc_bound}. "
                        f"Valens delineates that bound: {asc_delineation}."
                    ),
                    "Vettius Valens, Anthologiae I.3, printed pp. 14-19, Kroll 1908 Greek",
                    "valens_bound_delineations",
                    "analysis.angles.Ascendant",
                    (
                        "The bound of the rising degree, delineated. A statement about the "
                        "DEGREES, not a verdict on the person, and one testimony among many. "
                        + BOUND_QUALIFIER
                    ),
                    {
                        "point": "Ascendant",
                        "sign": asc_sign_name,
                        "bound_lord": asc_bound,
                        "bound_system": "Egyptian (the set Valens uses)",
                    },
                )
        except (TypeError, ValueError):
            pass

    for name in SEPTENER:
        planet = planets.get(name)
        if not planet:
            continue
        conditions = [
            f"{name} is at {_position(planet)} in whole-sign house {planet.get('house')}",
            f"essential condition: {_dignity_description(planet)}",
        ]
        if planet.get("retrograde"):
            conditions.append("retrograde")
        solar_status = planet.get("solar_status")
        if solar_status and solar_status not in ("FREE", "SUN"):
            conditions.append(f"solar condition: {str(solar_status).replace('_', ' ').lower()}")
        extended = _planet_condition_details(planet)
        if extended.get("phasis"):
            conditions.append(f"phasis: {extended['phasis']}")
        if extended.get("is_visible") is not None:
            conditions.append(
                "visible by the configured phasis test"
                if extended["is_visible"]
                else "not visible by the configured phasis test"
            )
        if extended.get("dispositor"):
            conditions.append(f"domicile dispositor: {extended['dispositor']}")
        if extended.get("maltreatments"):
            conditions.append(
                f"{len(extended['maltreatments'])} configured maltreatment condition(s)"
            )
        add(
            "planetary_condition",
            "; ".join(conditions) + ".",
            "Ptolemy, Tetrabiblos; Lilly, Christian Astrology, dignity tables",
            "lilly_planetary_conditions",
            f"analysis.planets_forensic[{name}]",
            "Condition describes capacity and manner of action, not a concrete event or a classification of the reader.",
            {
                "name": name,
                "position": _position(planet),
                "sign": planet.get("sign"),
                "house": planet.get("house"),
                "dignities": _dignity_description(planet),
                "retrograde": bool(planet.get("retrograde")),
                "solar_status": solar_status,
                **extended,
            },
        )
        joy_house = PLANETARY_JOY_HOUSES.get(name)
        if planet.get("house") == joy_house:
            add(
                "planetary_joy",
                f"{name} is in whole-sign house {joy_house}, its planetary joy.",
                "Paulus Alexandrinus, Introductory Matters",
                "paulus_planetary_joys",
                f"analysis.planets_forensic[{name}].house",
                (
                    "Joy is a place-based affinity and modifier of activity. It does not erase essential debility, "
                    "sect, maltreatment, or contrary testimony."
                ),
                {"name": name, "house": joy_house},
            )
        sect_condition = _mapping(extended.get("sect_condition"))
        if sect_condition.get("status") in {"Hayz", "Halb"}:
            horizon = "above" if sect_condition.get("is_above_horizon") else "below"
            add(
                "hayz_halb",
                (
                    f"{name} is in {sect_condition.get('status')}: it is {horizon} the horizon at "
                    f"{float(sect_condition.get('altitude_deg') or 0.0):.2f} degrees altitude, and the configured "
                    f"gender agreement is {sect_condition.get('gender_match')}."
                ),
                "Al-Biruni, Book of Instruction",
                "al_biruni_hayz_halb",
                f"analysis.planets_forensic[{name}].sect_condition",
                (
                    "Hayz and halb modify accidental condition. They do not make a malefic benefic, cancel essential "
                    "debility, or establish an event."
                ),
                {
                    "name": name,
                    "status": sect_condition.get("status"),
                    "is_above_horizon": sect_condition.get("is_above_horizon"),
                    "gender_match": sect_condition.get("gender_match"),
                    "horizon_method": sect_condition.get("horizon_method"),
                    "altitude_deg": sect_condition.get("altitude_deg"),
                },
            )
        dodecatemoria = _mapping(_mapping(planet.get("classical")).get("dodecatemoria"))
        for key, category, source_rule_id, fallback_authority in (
            (
                "valens",
                "dodecatemoria_x12",
                "configured_dodecatemoria_x12",
                "Configured 12-fold twelfth-part variant; historical attribution unresolved",
            ),
            (
                "paul",
                "dodecatemoria_x13",
                "paulus_dodecatemoria_x13",
                "Paulus Alexandrinus, Introductory Matters",
            ),
        ):
            projection = _mapping(dodecatemoria.get(key))
            if not projection:
                continue
            position = _mapping(projection.get("longitude_fmt")).get("string")
            add(
                category,
                (
                    f"By {projection.get('method')}, {name}'s twelfth-part is {position} in whole-sign house "
                    f"{projection.get('house')}, in the configured Egyptian bound of {projection.get('term_ruler')}."
                ),
                fallback_authority,
                source_rule_id,
                f"analysis.planets_forensic[{name}].classical.dodecatemoria.{key}",
                (
                    "A twelfth-part is a derived subdivision used as a secondary testimony. Method forks must remain "
                    "visible, and the projection does not replace or override the planet's natal position."
                ),
                {
                    "name": name,
                    "method": projection.get("method"),
                    "position": position,
                    "sign": projection.get("sign"),
                    "house": projection.get("house"),
                    "term_ruler": projection.get("term_ruler"),
                },
            )

    zoidion_monomoiria: list[dict[str, Any]] = []
    sect_light_name = "Sun" if str(sect.get("type")).upper() == "DAY" else "Moon"
    trigonal_monomoiria: dict[str, Any] | None = None
    for name in SEPTENER:
        planet = planets.get(name)
        if not planet:
            continue
        mono = _mapping(_mapping(planet.get("classical")).get("monomoiria"))
        if mono.get("zoidion_ruler"):
            zoidion_monomoiria.append(
                {
                    "name": name,
                    "position": _position(planet),
                    "ruler": mono.get("zoidion_ruler"),
                    "self_ruled": mono.get("zoidion_ruler") == name,
                }
            )
        if (
            name == sect_light_name
            and mono.get("trigonal_scope") == "sect_light"
            and mono.get("trigonal_ruler")
        ):
            trigonal_monomoiria = {
                "name": name,
                "position": _position(planet),
                "ruler": mono.get("trigonal_ruler"),
            }
    if zoidion_monomoiria:
        add(
            "monomoiria_zoidion",
            "Paulus's sign-based degree rulers are "
            + "; ".join(
                f"{card['name']} at {card['position']} ruled by {card['ruler']}"
                for card in zoidion_monomoiria
            )
            + ".",
            "Paulus Alexandrinus, Introductory Matters",
            "paulus_zoidion_monomoiria",
            "analysis.planets_forensic[*].classical.monomoiria.zoidion_ruler",
            (
                "A monomoiria ruler is secondary degree-level governance. The engine's +1 self-rulership score is a "
                "configured weighting and must not be presented as a number supplied by Paulus."
            ),
            {"cards": zoidion_monomoiria},
        )
    if trigonal_monomoiria:
        add(
            "monomoiria_trigonal",
            (
                f"For this {sect.get('type')} nativity, the sect light {trigonal_monomoiria['name']} at "
                f"{trigonal_monomoiria['position']} has {trigonal_monomoiria['ruler']} as its trigonal monomoiria ruler."
            ),
            "Paulus Alexandrinus, Introductory Matters",
            "paulus_trigonal_monomoiria",
            f"analysis.planets_forensic[{sect_light_name}].classical.monomoiria.trigonal_ruler",
            (
                "Paulus applies the trigonal canon to the degree of the sect light. It is not a general second "
                "monomoiria ruler for every planet."
            ),
            trigonal_monomoiria,
        )

    degree_qualities = _mapping(analysis.get("degree_qualities"))
    degree_cards: list[dict[str, Any]] = []
    if degree_qualities and not degree_qualities.get("error"):
        asc_ruler = SIGN_RULERS.get(str(ascendant.get("sign")))
        principal_lord = _mapping(
            _mapping(analysis.get("dignity")).get("almuten")
        ).get("winner")
        second_ruler = None
        for topos in _sequence(_mapping(analysis.get("topical")).get("twelve_topoi")):
            if isinstance(topos, Mapping) and topos.get("house") == 2:
                second_ruler = topos.get("ruler")
                break
        for body, raw_card in degree_qualities.items():
            if body not in {*SEPTENER, "Ascendant", "Midheaven", "Lot of Fortune"}:
                continue
            card = _mapping(raw_card)
            if not card or not card.get("data_available"):
                continue
            pitted_scope = body in {"Ascendant", "Moon", asc_ruler}
            azimene_scope = body in {
                "Ascendant",
                "Moon",
                asc_ruler,
                principal_lord,
            }
            appearance_scope = body in {"Ascendant", "Moon"}
            fortune_scope = body in {second_ruler, "Jupiter", "Lot of Fortune"}
            degree_cards.append(
                {
                    "body": body,
                    "sign": card.get("sign"),
                    "degree_one_based": card.get("degree_one_based"),
                    "masculine_feminine": card.get("masculine_feminine"),
                    "light_dark_smoky_void": card.get("light_dark_smoky_void"),
                    "pitted": bool(card.get("pitted")),
                    "azimene": bool(card.get("azimene")),
                    "increasing_fortune": bool(card.get("increasing_fortune")),
                    "appearance_scope": appearance_scope,
                    "pitted_scope": pitted_scope,
                    "azimene_scope": azimene_scope,
                    "fortune_scope": fortune_scope,
                }
            )
        if degree_cards:
            card_text = "; ".join(
                (
                    f"{card['body']} {card['sign']} degree {card['degree_one_based']} "
                    f"({card['masculine_feminine']}, {card['light_dark_smoky_void']}, "
                    f"pitted={card['pitted']}, azimene={card['azimene']}, "
                    f"increasing-fortune={card['increasing_fortune']})"
                )
                for card in degree_cards
            )
            add(
                "degree_quality",
                f"Lilly's one-based degree table yields: {card_text}.",
                "William Lilly, Christian Astrology (1647)",
                "lilly_degree_quality_tables",
                "analysis.degree_qualities",
                (
                    "Apply each column only to the significators Lilly names. An unrelated planet's pitted or "
                    "azimene flag is recorded but does not authorize a natal obstruction or bodily conclusion."
                ),
                {
                    "cards": degree_cards,
                    "ascendant_ruler": asc_ruler,
                    "principal_lord": principal_lord,
                    "second_house_ruler": second_ruler,
                },
            )

    for index, contact in enumerate(
        _sequence(_mapping(analysis.get("supplemental")).get("stars"))
    ):
        if not isinstance(contact, Mapping):
            continue
        if (
            contact.get("star_name") != "Caput Algol"
            or contact.get("planet_name") != "Midheaven"
            or contact.get("contact_type") != "ANGULAR_PRESENCE"
        ):
            continue
        orb = contact.get("orb_deg")
        if not isinstance(orb, (int, float)) or float(orb) > 1.0:
            continue
        add(
            "fixed_star",
            (
                f"Caput Algol is in ecliptic conjunction with the Midheaven at {float(orb):.2f} degrees orb. "
                f"The contact record gives the nature {contact.get('nature')}."
            ),
            "Ptolemy, Tetrabiblos",
            "ptolemy_perseus_algol",
            f"analysis.supplemental.stars[{index}]",
            (
                "Ptolemy assigns Perseus generally to Jupiter and Saturn. His violent Gorgon delineation requires "
                "Mars near the Gorgon inside a larger anaretic configuration; an Algol-Midheaven contact alone does not satisfy it."
            ),
            {
                "star": "Caput Algol",
                "angle": "Midheaven",
                "orb_deg": float(orb),
                "nature": contact.get("nature"),
                "mythology": contact.get("mythology"),
                "configured_orb_limit_deg": 1.0,
            },
        )

    chains = []
    for name in SEPTENER:
        if name not in planets:
            continue
        chain, outcome = _dispositor_chain(name, planets)
        chains.append({"planet": name, "chain": chain, "outcome": outcome})
    if chains:
        chain_text = "; ".join(
            f"{item['planet']}: {' -> '.join(item['chain'])} ({item['outcome'].replace('_', ' ')})"
            for item in chains
        )
        add(
            "dispositor_network",
            f"The domicile-dispositor network is {chain_text}.",
            "Configured traditional domicile-rulership chain",
            "configured_domicile_dispositor_chain",
            "analysis.planets_forensic[*].dispositor",
            (
                "A dispositor chain shows where a planet must obtain governance or resources. "
                "It establishes structural dependence rather than a fixed outcome."
            ),
            {"chains": chains},
        )

    topical = _mapping(analysis.get("topical"))
    for topos in _sequence(topical.get("twelve_topoi")):
        if not isinstance(topos, Mapping):
            continue
        house = topos.get("house")
        if not isinstance(house, int) or house not in CUSTOMER_TOPICS:
            continue
        condition = _mapping(topos.get("ruler_condition"))
        reasons = [str(item) for item in _sequence(condition.get("reasons"))]
        reason_text = ", ".join(reasons) if reasons else "no condition reasons supplied"
        occupants = [str(item) for item in _sequence(topos.get("occupants"))]
        occupant_text = f" Occupants: {', '.join(occupants)}." if occupants else ""
        aversion_text = (
            " The ruler is in whole-sign aversion to its own place."
            if topos.get("ruler_in_aversion_to_its_house")
            else ""
        )
        add(
            "topical",
            (
                f"For {CUSTOMER_TOPICS[house]}, house {house} is {topos.get('sign')} and is ruled by "
                f"{topos.get('ruler')}. Its ruler is in {condition.get('sign')}, house {condition.get('house')}; "
                f"the configured condition band is {condition.get('condition_band')} because {reason_text}."
                f"{aversion_text}{occupant_text}"
            ),
            "Configured whole-sign topical chain attributed to Hellenistic and medieval practice",
            "whole_sign_topical_chain",
            f"analysis.topical.twelve_topoi[{house}]",
            (
                "The condition band is a project ranking aid. Cite its listed reasons; it indicates relative "
                "capacity and connection to the topic, not a promised biography or outcome."
            ),
            {
                "house": house,
                "topic": CUSTOMER_TOPICS[house],
                "sign": topos.get("sign"),
                "ruler": topos.get("ruler"),
                "ruler_sign": condition.get("sign"),
                "ruler_house": condition.get("house"),
                "condition_band": condition.get("condition_band"),
                "reasons": reasons,
                "aversion": bool(topos.get("ruler_in_aversion_to_its_house")),
                "occupants": occupants,
            },
        )

    almuten = _mapping(_mapping(analysis.get("dignity")).get("almuten"))
    almuten_rule = _mapping(_mapping(SOURCE_REGISTRY.get("verified_rules")).get("almuten_figuris_five_point"))
    if almuten.get("winner") and almuten_rule:
        add(
            "chart_ruler",
            f"The configured Almuten Figuris method ranks {almuten['winner']} first with {almuten.get('score')} points.",
            "Configured Ibn Ezra-style five hylegiacal-point method",
            "almuten_figuris_five_point",
            "analysis.dignity.almuten",
            "This is a configured medieval weighting method, not a planet that cancels all contrary testimony.",
        )

    vitality = _mapping(analysis.get("vitality"))
    hyleg = _mapping(vitality.get("hyleg"))
    methods = _mapping(vitality.get("alcocoden_methods"))
    capacities = _mapping(vitality.get("years_capacity"))
    strict_method = _mapping(methods.get("valens_term"))
    points_method = _mapping(methods.get("bonatti_points"))
    strict_capacity = _mapping(capacities.get("valens_term"))
    points_capacity = _mapping(capacities.get("bonatti_points"))
    if hyleg.get("name") and (strict_method or points_method):
        add(
            "longevity",
            (
                f"The historical length-of-life calculation takes {hyleg.get('name')} at "
                f"{float(hyleg.get('longitude', 0.0)):.2f} degrees as Hyleg. The supplied Alcocoden branches "
                f"select {strict_method.get('name')} by the configured strict-bound branch and "
                f"{points_method.get('name')} by the dignity-points and degree-aspect branch."
            ),
            "William Lilly, Christian Astrology, Book III, Chapter CIV",
            "lilly_hyleg_alcocoden_and_years",
            "analysis.vitality.hyleg + analysis.vitality.alcocoden_methods",
            (
                "Lilly preserves the Arabic years doctrine but explicitly doubts that the Hyleg, Anareta, and Alcocoden "
                "can be selected with certainty. Show competing branches and the exact aspect mode."
            ),
            {
                "technique": "historical_longevity",
                "hyleg": dict(hyleg),
                "strict_method": dict(strict_method),
                "points_method": dict(points_method),
            },
        )
        add(
            "longevity",
            (
                f"The configured strict-bound branch assigns {strict_capacity.get('alcocoden')} the "
                f"{strict_capacity.get('base_years_type')} years value of {strict_capacity.get('total_years')}. "
                f"The dignity-points branch assigns {points_capacity.get('alcocoden')} a base of "
                f"{points_capacity.get('base_years')} years but is marked invalid under the engine's sanity check."
            ),
            "Configured application of Lilly's Hyleg, Alcocoden, and planetary-years doctrine",
            "configured_lilly_alcocoden_branches",
            "analysis.vitality.years_capacity",
            (
                "Each numerical figure is the exact output of its disclosed branch, not a universal result. A branch admitted "
                "through whole-sign co-presence must identify that fallback because it is not stated in Lilly's inspected chapter. "
                "Every rival branch, aspect mode, sanity failure, and arithmetic adjustment must remain visible."
            ),
            {
                "technique": "historical_longevity_branches",
                "strict_capacity": dict(strict_capacity),
                "points_capacity": dict(points_capacity),
                "anareta": dict(_mapping(vitality.get("anareta"))),
                "anaretic_windows": dict(_mapping(vitality.get("anaretic_windows"))),
            },
        )

    for aspect in _sequence(analysis.get("aspects")):
        if not isinstance(aspect, Mapping):
            continue
        a = aspect.get("planet_a")
        b = aspect.get("planet_b")
        if a not in SEPTENER or b not in SEPTENER:
            continue
        add(
            "aspect",
            f"{a} forms a {aspect.get('type')} with {b} at an orb of {float(aspect.get('orb', 0.0)):.2f} degrees, "
            f"{'applying' if aspect.get('is_applying') else 'separating'}.",
            "Ptolemy, Tetrabiblos, aspect doctrine",
            "ptolemaic_aspects",
            f"analysis.aspects[{len([e for e in evidence if e.category == 'aspect'])}]",
            "An aspect joins testimonies; it must be interpreted through both planets' condition and topics.",
            {
                "planet_a": a,
                "planet_b": b,
                "type": aspect.get("type"),
                "orb": float(aspect.get("orb", 0.0)),
                "is_applying": bool(aspect.get("is_applying")),
            },
        )

    antiscia_cards: list[dict[str, Any]] = []
    for configuration in _sequence(analysis.get("antiscia_configurations")):
        if not isinstance(configuration, Mapping):
            continue
        first = str(configuration.get("planet_1"))
        second = str(configuration.get("planet_2"))
        if first not in SEPTENER or second not in SEPTENER:
            continue
        if configuration.get("source_rule_id") != "firmicus_antiscia_major_configurations":
            continue
        antiscia_cards.append(
            {
                "planet_1": first,
                "planet_2": second,
                "antiscion_of": configuration.get("antiscion_of"),
                "aspect": configuration.get("aspect"),
                "orb": float(configuration.get("orb", 0.0)),
                "orb_limit": float(configuration.get("orb_limit", 1.0)),
            }
        )
    if "antiscia_configurations" in analysis:
        add(
            "antiscia_configuration",
            (
                "Firmicus's reflected-degree configurations within the configured one-degree limit are "
                + "; ".join(
                    f"{card['planet_1']}-{card['planet_2']} {card['aspect']} at {card['orb']:.2f} degrees orb"
                    for card in antiscia_cards
                )
                + "."
                if antiscia_cards
                else "No septener configuration through an antiscion falls within the configured one-degree limit."
            ),
            "Julius Firmicus Maternus, Mathesis",
            "firmicus_antiscia_major_configurations",
            "analysis.antiscia_configurations",
            (
                "Firmicus treats major configurations through the reflected degree like ordinary configurations. "
                "The one-degree publication limit is a conservative configured choice because the inspected passage gives no numerical orb."
            ),
            {"cards": antiscia_cards, "configured_orb_limit_deg": 1.0},
        )

    doryphory_cards: list[dict[str, Any]] = []
    for guard in _sequence(_mapping(analysis.get("advanced_mechanics")).get("doryphory")):
        if not isinstance(guard, Mapping):
            continue
        guard_name = str(guard.get("guard"))
        luminary = str(guard.get("luminary"))
        if guard_name not in SEPTENER or luminary not in {"Sun", "Moon"}:
            continue
        if guard.get("source_rule_id") != "ptolemy_doryphory_rank":
            continue
        doryphory_cards.append(
            {
                "guard": guard_name,
                "luminary": luminary,
                "phase": guard.get("phase"),
                "placement_relation": guard.get("placement_relation"),
                "guard_house_wsh": guard.get("guard_house_wsh"),
                "guard_angular_wsh": bool(guard.get("guard_angular_wsh")),
                "delta_deg": guard.get("delta_deg"),
            }
        )
    advanced_mechanics = _mapping(analysis.get("advanced_mechanics"))
    if "doryphory" in advanced_mechanics:
        luminary_cards = {
            name: {
                "sign": planets[name].get("sign"),
                "house": planets[name].get("house"),
                "masculine_sign": planets[name].get("sign")
                in {"Aries", "Gemini", "Leo", "Libra", "Sagittarius", "Aquarius"},
                "angular_wsh": planets[name].get("house") in {1, 4, 7, 10},
            }
            for name in ("Sun", "Moon")
            if name in planets
        }
        add(
            "doryphory",
            (
                "Ptolemaic bodily attendants are "
                + "; ".join(
                    f"{card['guard']} attending the {card['luminary']} as {card['phase']} in the {str(card['placement_relation']).replace('_', ' ')}"
                    for card in doryphory_cards
                )
                + "."
                if doryphory_cards
                else "No septener planet satisfies the audited Ptolemaic bodily-attendance rule."
            ),
            "Claudius Ptolemy, Tetrabiblos",
            "ptolemy_doryphory_rank",
            "analysis.advanced_mechanics.doryphory + analysis.planets_forensic[Sun,Moon]",
            (
                "Attendance contributes to rank only through the complete hierarchy of luminary gender and angularity, "
                "attendant angular testimony, and the guard's nature and condition. A single guard is not a royal configuration."
            ),
            {"cards": doryphory_cards, "luminaries": luminary_cards},
        )

    # Paulus chapter 24 gives chart-specific planet-in-place judgments whose
    # conditions cannot be reduced to the generic house-topic heuristic.  Keep
    # the source branch (especially sect and malefic regard) in the evidence so
    # the composer cannot silently choose the more pleasant alternative.
    aspect_records = [
        item
        for item in _sequence(analysis.get("aspects"))
        if isinstance(item, Mapping)
        and item.get("planet_a") in SEPTENER
        and item.get("planet_b") in SEPTENER
    ]

    def contacts(name: str, other_names: set[str]) -> list[dict[str, Any]]:
        found: list[dict[str, Any]] = []
        for aspect in aspect_records:
            a = str(aspect.get("planet_a"))
            b = str(aspect.get("planet_b"))
            if name == a and b in other_names:
                other = b
            elif name == b and a in other_names:
                other = a
            else:
                continue
            found.append(
                {
                    "other": other,
                    "type": aspect.get("type"),
                    "orb": float(aspect.get("orb", 0.0)),
                    "is_applying": bool(aspect.get("is_applying")),
                }
            )
        return found

    place_rules = {
        ("Mercury", 1): (
            "Paulus makes Hermes rejoice in the first and gives a preservation-and-good-fortune promise when a benefic, light, or Hermes occupies the Ascendant apart from malefic configurations.",
            "The joy is active. The fuller preservation clause is conditional on separation from malefic figures and must be tested against the recorded aspects.",
        ),
        ("Jupiter", 5): (
            "Paulus says benefics in the fifth rejoice there and signify a goodly number of children.",
            "This is a base benefic promise, not an unconditional count. Essential fall, retrogradation, maltreatment, and contrary testimony show damage or delay without erasing the printed rule.",
        ),
        ("Saturn", 8): (
            "Paulus calls the eighth idle and dysfunctional and gives planets there inheritance and profit-from-death testimony; he includes malefics in that result.",
            "This is historical inheritance, loss, and mortality testimony. It is not financial advice or a standalone prediction of anyone's death.",
        ),
        ("Mars", 11): (
            "For Mars in the eleventh by day, Paulus gives reduction of life, loss of things, changes of place, accidents, and affliction involving children; his favorable branch belongs to night charts.",
            "Sect controls the branch. The day branch must be printed for a day chart; the favorable night branch must not be substituted.",
        ),
        ("Venus", 11): (
            "Paulus gives Venus in the eleventh fortunate marriage, orderliness, sufficiency, and improving fortune, especially when she is not scrutinized by a malefic ray.",
            "The favorable promise and its exception must both be judged. A recorded Mars or Saturn configuration activates the exception and damages the clean result.",
        ),
        ("Sun", 12): (
            "Paulus gives the Sun in the twelfth severe testimony concerning the father and the native: absence or hardship of the father, obscurity, labor, need, and low circumstances.",
            "Print the severe place rule, then weigh the Sun's actual dignity, sect, and configurations. Strength modifies capacity and outcome; it does not relocate the Sun or erase the rule.",
        ),
        ("Moon", 12): (
            "When the Moon in the twelfth is regarded by or applying to a malefic, Paulus gives maternal illness, injury, or shortened life and makes the native poor, struggling, and persistently unfortunate.",
            "The harsh branch is conditional on malefic regard or application. Aspect type, application, sect, and the malefic's condition modify severity but do not make an existing regard disappear.",
        ),
    }
    is_day = str(sect.get("type") or "").upper() == "DAY"
    for (name, house), (rule_text, limit) in place_rules.items():
        planet = planets.get(name)
        if not planet or planet.get("house") != house:
            continue
        malefic_contacts = contacts(name, {"Mars", "Saturn"} - {name})
        details = {
            "name": name,
            "house": house,
            "position": _position(planet),
            "day_chart": is_day,
            "dignities": _dignity_description(planet),
            "retrograde": bool(planet.get("retrograde")),
            "maltreatments": _planet_condition_details(planet).get("maltreatments", []),
            "sect_condition": dict(
                _mapping(_planet_condition_details(planet).get("sect_condition"))
            ),
            "malefic_contacts": malefic_contacts,
            "malefic_regard_present": bool(malefic_contacts),
            "malefic_application_present": any(
                bool(contact.get("is_applying")) for contact in malefic_contacts
            ),
        }
        add(
            "planet_in_place_source",
            f"{name} is in whole-sign house {house}. {rule_text}",
            "Paulus Alexandrinus, Introductory Matters",
            "paulus_planets_in_places_chart_rules",
            f"analysis.planets_forensic[{name}].house + analysis.aspects",
            limit,
            details,
        )

    for reception in _sequence(_mapping(analysis.get("teams")).get("receptions")):
        if not isinstance(reception, Mapping):
            continue
        operative_sides = []
        for side in ("a_in_b", "b_in_a"):
            detail = _mapping(reception.get(side))
            if detail.get("is_operative"):
                operative_sides.append(
                    f"{detail.get('host')} receives {detail.get('guest')} by {', '.join(map(str, _sequence(detail.get('dignities'))))}"
                )
        if not operative_sides:
            continue
        add(
            "reception",
            "; ".join(operative_sides) + ".",
            "Lilly, Christian Astrology; Bonatti, Liber Astronomiae",
            "lilly_reception",
            "analysis.teams.receptions",
            "Reception can provide assistance or exchange; it does not erase debility or ensure resolution.",
        )

    fate = _mapping(analysis.get("fate"))
    lots = _mapping(fate.get("hermetic_lots"))
    for lot_name in ("Fortune", "Spirit", "Eros", "Necessity", "Courage", "Victory", "Nemesis"):
        lot = _mapping(lots.get(lot_name))
        if not lot:
            continue
        position = _mapping(lot.get("longitude_fmt")).get("string") or lot.get("sign")
        add(
            "lot",
            (
                f"The Lot of {lot_name} is at {position} in whole-sign house {lot.get('house')}, "
                f"ruled by {lot.get('ruler')}; the configured condition status is {lot.get('status') or 'not supplied'}."
            ),
            "Paulus Alexandrinus, Introductory Matters",
            "paulus_seven_hermetic_lots",
            f"analysis.fate.hermetic_lots.{lot_name}",
            (
                f"Paulus defines this lot through {PAULUS_LOT_MEANINGS[lot_name]}. It must still be judged through place, ruler, ruler condition, and configurations; its label alone does not establish an event."
            ),
            {
                "name": lot_name,
                "position": position,
                "sign": lot.get("sign"),
                "house": lot.get("house"),
                "ruler": lot.get("ruler"),
                "status": lot.get("status"),
                "maltreatment_details": _sequence(lot.get("maltreatment_details")),
                "paulus_meaning": PAULUS_LOT_MEANINGS[lot_name],
            },
        )

    mansion = _mapping(_mapping(analysis.get("supplemental")).get("lunar_mansion"))
    if (
        mansion.get("mansion_id")
        and mansion.get("source_rule_id") == "picatrix_lunar_mansions_electional_scope"
    ):
        moon = planets.get("Moon", {})
        add(
            "lunar_mansion_scope",
            (
                f"The Moon at {_position(moon)} calculates to tropical mansion {mansion.get('mansion_id')}, "
                f"{mansion.get('name')} (Azobra in the inspected Picatrix translation)."
            ),
            "Picatrix, Book I, Chapter IV",
            "picatrix_lunar_mansions_electional_scope",
            "analysis.supplemental.lunar_mansion + analysis.planets_forensic[Moon]",
            (
                "Picatrix supplies electional and image-making operations here, not natal personality or destiny rules. "
                "The mansion may be named, but its operations must not be converted into a statement about the native."
            ),
            {
                "mansion_id": mansion.get("mansion_id"),
                "name": mansion.get("name"),
                "source_name_variant": mansion.get("inspected_source_name_variant"),
                "moon_position": _position(moon),
                "calculation_method": mansion.get("calculation_method"),
                "usage_scope": mansion.get("usage_scope"),
                "natal_delineation_supported": bool(
                    mansion.get("natal_delineation_supported")
                ),
                "assignment_robust_to_boundary_variants": bool(
                    mansion.get("assignment_robust_to_inspected_boundary_variants")
                ),
            },
        )

    syzygy = _mapping(analysis.get("syzygy"))
    prenatal = _mapping(syzygy.get("prenatal_syzygy"))
    natal_phase = _mapping(syzygy.get("natal_phase"))
    if prenatal or natal_phase:
        prenatal_position = _mapping(prenatal.get("longitude_fmt")).get("string")
        phase_direction = "waning" if natal_phase.get("is_waning") else "waxing"
        add(
            "lunar_cycle",
            (
                f"The prenatal syzygy was a {prenatal.get('type')} at {prenatal_position} on "
                f"{prenatal.get('datetime_utc')}; at birth the Moon was {phase_direction}, "
                f"{float(natal_phase.get('moon_sun_elongation_min_deg', 0.0)):.2f} degrees from the Sun."
            ),
            "Configured traditional prenatal-syzygy calculation",
            "configured_prenatal_syzygy",
            "analysis.syzygy",
            (
                "The syzygy supplies lunar-cycle context. It does not independently determine character, "
                "health, longevity, or a concrete event."
            ),
            {
                "type": prenatal.get("type"),
                "position": prenatal_position,
                "datetime_utc": prenatal.get("datetime_utc"),
                "phase_direction": phase_direction,
                "elongation_deg": natal_phase.get("moon_sun_elongation_min_deg"),
            },
        )

    triplicity = _mapping(analysis.get("triplicity_periods"))
    rulers = _mapping(triplicity.get("rulers"))
    if rulers:
        add(
            "life_chapters",
            (
                f"For this {triplicity.get('sect')} nativity, Dorotheus's sect-light triplicity judgment uses "
                f"{rulers.get('first')} first and {rulers.get('second')} second, with {rulers.get('participant')} participating. "
                "The first and second rulers describe the beginning and later outcome of fortune/property; "
                "the participant supports the whole judgment rather than ruling an invented final third of life."
            ),
            "Dorotheus of Sidon, Carmen Astrologicum I.1, I.5, and I.22-I.24",
            "dorotheus_sect_light_triplicity_fortune",
            "analysis.triplicity_periods",
            "This is a broad judgment of fortune, property, and elevation. It supplies no equal age thirds or event dates, and the participating ruler has no fixed final third or late-life period in the inspected passage.",
            {
                "sect": triplicity.get("sect"),
                "element": triplicity.get("element"),
                "first": rulers.get("first"),
                "second": rulers.get("second"),
                "participant": rulers.get("participant"),
                "temporal_roles": triplicity.get("temporal_roles"),
            },
        )
        add(
            "life_chapters",
            (
                f"In a later medieval method, Ibn Ezra explicitly divides the sect-light triplicity rulers into three relative life phases: "
                f"{rulers.get('first')} first, {rulers.get('second')} middle, and {rulers.get('participant')} last. "
                "This is a distinct later doctrine, not the wording of Dorotheus's first/second fortune judgment."
            ),
            "Abraham Ibn Ezra, Book of Revolution section 4",
            "ibn_ezra_triplicity_life_thirds",
            "analysis.triplicity_periods",
            "The source supports relative first, middle, and last phases but does not itself supply numerical age boundaries. Keep this phase doctrine separate from the Lilly-scoped Hyleg and Alcocoden branches published elsewhere in the report.",
            {
                "method": "ibn_ezra_relative_life_thirds",
                "sect": triplicity.get("sect"),
                "first": rulers.get("first"),
                "middle": rulers.get("second"),
                "last": rulers.get("participant"),
            },
        )

    profection = _mapping(analysis.get("enhanced_profections"))
    if profection.get("annual_sign"):
        add(
            "timing",
            f"At age {profection.get('age')}, the annual profection is {profection.get('annual_sign')} and the Lord of the Year is {profection.get('lord_of_year')}.",
            "Configured annual profection method attributed to Valens",
            "annual_profection_sign_rotation",
            "analysis.enhanced_profections",
            "A profection activates natal topics; it does not independently promise an event.",
            {
                "technique": "annual_profection",
                "age": profection.get("age"),
                "sign": profection.get("annual_sign"),
                "rulers": [profection.get("lord_of_year")],
            },
        )
        # Valens IV.14, printed p. 182: a retrograde time-lord DEFERS rather
        # than denies - "they put the expected things, the matters, the benefits
        # and the undertakings into POSTPONEMENT". That is a distinct verdict
        # from affliction, and we had no way to say it.
        loy_name = profection.get("lord_of_year")
        loy = planets.get(str(loy_name)) if loy_name else None
        if loy is not None and loy.get("retrograde"):
            add(
                "timing",
                (
                    f"The Lord of the Year, {loy_name}, is retrograde. Valens reads a "
                    f"retrograde time-lord as postponement rather than denial: it puts the "
                    f"expected matters, benefits and undertakings into deferral."
                ),
                "Vettius Valens, Anthologiae IV.14, printed p. 182, Kroll 1908 Greek",
                "valens_retrograde_timelord_postponement",
                f"analysis.planets_forensic[{loy_name}].retrograde",
                (
                    "Postponement is a distinct verdict from affliction: the matter is deferred, "
                    "not refused. Valens sets it against the oriental time-lord who 'accomplishes "
                    "actions manifestly'. It does not name a date on which the deferral ends."
                ),
                {
                    "technique": "annual_profection",
                    "lord_of_year": loy_name,
                    "verdict": "postponement",
                },
            )

        # Valens IV.22, p. 195: a malefic ruling its own period is judged by
        # SECT, not by its label. "Mars distributing to himself BY DAY will be
        # unpleasant and troublesome ... BUT BY NIGHT HE IS NOT BAD, but
        # successful and beneficial - especially if he stands in the transacting
        # signs." IV.19 says the same of the Ascendant handing to a malefic:
        # worst "especially to SATURN BY NIGHT and to MARS BY DAY" - in each
        # case the OUT-OF-SECT one. We had implemented this for the natal
        # paragraphs and left the timing layer asserting from the label.
        if loy_name in {"Saturn", "Mars"}:
            is_day_chart = str(sect.get("type") or "").upper().startswith("DAY")
            loy_of_sect = (loy_name == "Saturn") if is_day_chart else (loy_name == "Mars")
            loy_tier = _place_tier((loy or {}).get("house"))
            if loy_of_sect and loy_tier != "injurious":
                verdict_text = (
                    f"{loy_name} rules the year and is a malefic by nature, but is of the sect "
                    f"in favour and does not stand in an injurious place. Valens reads a malefic "
                    f"governing its own period under those conditions as not bad but effective "
                    f"and beneficial - the more so for work of that planet's own kind."
                )
                verdict = "effective"
            else:
                verdict_text = (
                    f"{loy_name} rules the year and is contrary to the sect"
                    + (
                        f", standing in the {loy_tier} place of house {(loy or {}).get('house')}"
                        if loy_tier == "injurious"
                        else ""
                    )
                    + ". Valens marks the out-of-sect malefic as the harder time-lord: it "
                    "describes the manner and severity of a difficulty, not a guaranteed event."
                )
                verdict = "harder"
            add(
                "timing",
                verdict_text,
                "Vettius Valens, Anthologiae IV.22 (p. 195) and IV.19 (p. 192), Kroll 1908 Greek",
                "valens_malefic_timelord_by_sect",
                f"analysis.planets_forensic[{loy_name}]",
                (
                    "Sect decides the verdict on a malefic time-lord, not the malefic label. "
                    "Valens gives the same planet opposite readings by day and by night, so a "
                    "period ruled by Saturn or Mars cannot be judged from the planet's name "
                    "alone. It still describes manner and severity, never a specific event."
                ),
                {
                    "lord_of_year": loy_name,
                    "of_sect": loy_of_sect,
                    "place_tier": loy_tier,
                    "verdict": verdict,
                },
            )

        # Valens IV.16, p. 184: the natal foundation caps what any period can
        # do. "When we find a notable and brilliant foundation ... with malefics
        # holding the times ... we say the nativity will suffer nothing out of
        # place; but the affairs will be managed disorderly." And the standing
        # instruction: "not as though for the greater and the glorious alike,
        # BUT DISTINGUISH."
        add(
            "timing",
            (
                "Any verdict on this period is bounded by the foundation of the nativity itself. "
                "Valens states it three times across three books: whatever figure the stars make "
                "at the birth, according to the foundation of the casting, is what they accomplish "
                "when they become lords of the times. A strong foundation under difficult times "
                "produces disorder, blame and fear rather than catastrophe; a weak one under "
                "favourable times does not produce greatness. And nothing arrives unmixed - even "
                "a strong benefic period, he says, brings its action or reputation together with "
                "oppositions and expenditures."
            ),
            "Vettius Valens, Anthologiae IV.16 (p. 184), VII.1 (p. 266) and VII.2 (p. 267), Kroll 1908 Greek",
            "valens_hypostasis_caps_timing",
            "analysis.enhanced_profections",
            (
                "A constraint on interpretation, not a prediction. It is the doctrinal guard "
                "against the commonest predictive error - treating a hard period as meaning the "
                "same thing in every chart. Valens states it as an instruction: 'but distinguish'."
            ),
            {"technique": "interpretive_constraint", "source": "hypostasis"},
        )

        signs = (
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
        )
        current_sign = str(profection.get("annual_sign"))
        current_age = int(profection.get("age") or 0)
        birth_date = str(chart_meta.get("date") or "")
        try:
            birth_year, birth_month, birth_day = (int(value) for value in birth_date.split("-")[:3])
        except (TypeError, ValueError):
            birth_year = birth_month = birth_day = 0
        sequence = []
        if current_sign in signs and birth_year:
            sign_index = signs.index(current_sign)
            # Cover the native's realistic remaining life, not a six-year slice:
            # profections are exact arithmetic and cost nothing to extend.
            horizon_age = _alcocoden_horizon_age(chart_data)
            span = max(MIN_HORIZON_YEARS_AHEAD, horizon_age - current_age)
            for offset in range(span):
                age = current_age + offset
                start_year = birth_year + age
                sequence.append(
                    {
                        "age": age,
                        "sign": signs[(sign_index + offset) % 12],
                        "ruler": {
                            "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
                            "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
                            "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
                        }[signs[(sign_index + offset) % 12]],
                        "start": f"{start_year:04d}-{birth_month:02d}-{birth_day:02d}",
                        "end": f"{start_year + 1:04d}-{birth_month:02d}-{birth_day:02d}",
                    }
                )
        if sequence:
            add(
                "timing_map",
                f"The profection map covers ages {sequence[0]['age']} through "
                f"{sequence[-1]['age']} ({sequence[0]['start'][:4]}-{sequence[-1]['end'][:4]}) and runs "
                + "; ".join(
                    f"age {item['age']} {item['sign']} / {item['ruler']} ({item['start']} to {item['end']})"
                    for item in sequence
                )
                + ".",
                "Annual profection sign rotation",
                "annual_profection_sign_rotation",
                "analysis.enhanced_profections + meta.chart.date",
                "This is a ruler-activation calendar rather than a calendar of fixed events.",
                {"technique": "annual_profection_map", "chapters": sequence},
            )

    distributor = _mapping(fate.get("primary_direction_distributor"))
    circumambulations = [
        value
        for value in _sequence(fate.get("circumambulations"))
        if isinstance(value, Mapping)
    ]
    current_age = profection.get("age")
    if distributor.get("planet") and isinstance(current_age, int):
        transitions = [
            value for value in circumambulations if value.get("is_transition")
        ]

        def transition_age(value: Mapping[str, Any]) -> float | None:
            exact = value.get("exact_transition_age")
            if isinstance(exact, (int, float)):
                return float(exact)
            sampled = value.get("age")
            return float(sampled) if isinstance(sampled, (int, float)) else None

        previous_transition = next(
            (
                value
                for value in reversed(transitions)
                if transition_age(value) is not None
                and float(transition_age(value) or 0.0) <= current_age
            ),
            None,
        )
        next_transition = next(
            (
                value
                for value in transitions
                if transition_age(value) is not None
                and float(transition_age(value) or 0.0) > current_age
            ),
            None,
        )
        birth_date = None
        try:
            birth_date = datetime.fromisoformat(str(chart_meta.get("date"))).date()
        except (TypeError, ValueError):
            birth_date = None

        def transition_date(value: Mapping[str, Any] | None) -> str | None:
            if not value or birth_date is None:
                return None
            age_value = transition_age(value)
            if age_value is None:
                return None
            return (birth_date + timedelta(days=age_value * 365.2425)).isoformat()

        period_text = ""
        if previous_transition and next_transition:
            previous_age = float(transition_age(previous_transition) or 0.0)
            next_age = float(transition_age(next_transition) or 0.0)
            previous_date = transition_date(previous_transition)
            next_date = transition_date(next_transition)
            period_text = (
                f" The configured model solves the bound period from age {previous_age:.2f}"
                + (f" ({previous_date})" if previous_date else "")
                + f" until {next_transition.get('bound_ruler')} takes over at age {next_age:.2f}"
                + (f" ({next_date})" if next_date else "")
                + "."
            )
        add(
            "timing",
            (
                f"The configured Ascendant prorogation places the directed Ascendant at "
                f"{float(distributor.get('directed_ascendant_deg', 0.0)):.2f} degrees, in the bound of "
                f"{distributor.get('planet')}. The participating planet is {distributor.get('partner')} because "
                f"{distributor.get('partner_reason')}.{period_text}"
            ),
            "Ptolemy, Tetrabiblos",
            "ptolemy_prorogation_distributor",
            "analysis.fate.primary_direction_distributor + analysis.fate.circumambulations",
            (
                "This is the Ascendant distributor only, calculated through a configured zodiacal oblique-ascension "
                "method, one-degree-per-year key, Egyptian bounds, and latitude-free aspect points. Transition ages are "
                "a configured key. Bound transitions are numerically solved inside the sampled brackets, but remain model dates rather than observed guarantees."
            ),
            {
                "technique": "ascendant_distributor",
                "rulers": [distributor.get("planet"), distributor.get("partner")],
                "directed_ascendant_deg": distributor.get("directed_ascendant_deg"),
                "arc": distributor.get("arc"),
                "bound_ruler": distributor.get("planet"),
                "partner": distributor.get("partner"),
                "partner_reason": distributor.get("partner_reason"),
                "previous_transition_age": transition_age(previous_transition or {}),
                "previous_transition_date": transition_date(previous_transition),
                "next_transition_age": transition_age(next_transition or {}),
                "next_transition_date": transition_date(next_transition),
                "next_bound_ruler": (
                    next_transition.get("bound_ruler") if next_transition else None
                ),
            },
        )

    firdaria = _mapping(fate.get("firdaria"))
    if firdaria.get("Major Period"):
        dates = ""
        if firdaria.get("Sub Start") and firdaria.get("Sub End"):
            dates = f", active from {firdaria.get('Sub Start')} through {firdaria.get('Sub End')}"
        source_rule_id = str(
            firdaria.get("Source Rule ID") or "configured_firdaria_node_extension"
        )
        add(
            "timing",
            f"The current Firdaria rulers are {firdaria.get('Major Period')} major and {firdaria.get('Sub Period')} sub{dates}.",
            "Configured medieval Firdaria sequence",
            source_rule_id,
            "analysis.fate.firdaria",
            "Firdaria supplies period rulers whose natal condition must be judged before topical conclusions.",
            {
                "technique": "firdaria",
                "rulers": [firdaria.get("Major Period"), firdaria.get("Sub Period")],
                "start": firdaria.get("Sub Start"),
                "end": firdaria.get("Sub End"),
            },
        )
        # The remaining major periods to the end of the 75-year cycle. The
        # current-period item above answers "now"; this answers "what comes
        # after", which the customer cannot derive from a single period.
        remaining = _firdaria_remaining_majors(chart_data, report_date)
        if remaining:
            add(
                "timing_map",
                f"The remaining Firdaria major periods run "
                + "; ".join(
                    f"{row['lord']} ({row['start']} to {row['end']})" for row in remaining
                )
                + ".",
                "Configured medieval Firdaria sequence",
                source_rule_id,
                "analysis.fate.firdaria + meta.chart.date",
                "Each major period hands the chapter to a new lord; its natal condition decides how that chapter performs.",
                {"technique": "firdaria_map", "periods": remaining},
            )
    else:
        # The classical Firdaria sequence spans 75 years. For a native beyond
        # that span (or when the engine returns no current period), the honest
        # testimony is the doctrinal limit itself — the layer must still be
        # covered rather than silently omitted.
        add(
            "timing",
            "No current Firdaria period applies: the classical 75-year Firdaria "
            "sequence is complete for this native, and the inspected sources do "
            "not agree on a single continuation scheme beyond it.",
            "Configured medieval Firdaria sequence",
            "configured_firdaria_span_limit",
            "analysis.fate.firdaria",
            "The medieval Firdaria cycle covers 75 years of life; beyond that "
            "span this report declines to invent a continuation rather than "
            "attribute one to a source that does not state it.",
            {
                "technique": "firdaria",
                "rulers": [],
                "beyond_span": True,
            },
        )

    releasing = _mapping(fate.get("zodiacal_releasing"))
    for lot_name in ("Spirit", "Fortune"):
        layer = _mapping(releasing.get(lot_name))
        current = _mapping(layer.get("current"))
        if not current:
            continue
        levels = [
            str(current.get(label))
            for label in ("Level 1", "Level 2", "Level 3", "Level 4")
            if current.get(label)
        ]
        period_dates = ""
        if current.get("L2_Start") and current.get("L2_End"):
            period_dates = f"; the level-two chapter runs from {current.get('L2_Start')} through {current.get('L2_End')}"
        status = current.get("Status") or current.get("L3_Status")
        status_text = f"; recorded status: {status}" if status else ""
        add(
            "timing",
            f"Zodiacal Releasing from {lot_name} is currently {' / '.join(levels)}{period_dates}{status_text}.",
            "Configured Zodiacal Releasing method attributed to Valens",
            "valens_zodiacal_releasing",
            f"analysis.fate.zodiacal_releasing.{lot_name}.current",
            "Releasing describes chapters and relative activation, not automatic eminence, crisis, or concrete events.",
            {
                "technique": "zodiacal_releasing",
                "lot": lot_name,
                "levels": levels,
                "status": status,
                "start": current.get("L2_Start"),
                "end": current.get("L2_End"),
                "level_3_start": current.get("L3_Start"),
                "level_3_end": current.get("L3_End"),
                "level_4_start": current.get("L4_Start"),
                "level_4_end": current.get("L4_End"),
            },
        )
        l1_chapters = []
        for chapter in _sequence(layer.get("l1_chapters")):
            if not isinstance(chapter, Mapping):
                continue
            if str(chapter.get("end_date") or "") <= report_date[:10]:
                continue
            l1_chapters.append(dict(chapter))
        if l1_chapters:
            add(
                "timing_map",
                f"The long-range Level-1 releasing map from {lot_name} runs "
                + "; ".join(
                    f"{chapter.get('sign')} ({chapter.get('start_date')} to {chapter.get('end_date')})"
                    + (" [peak from Fortune]" if chapter.get("peak_from_fortune") else "")
                    for chapter in l1_chapters
                )
                + ".",
                "Configured Zodiacal Releasing method attributed to Valens",
                "valens_zodiacal_releasing",
                f"analysis.fate.zodiacal_releasing.{lot_name}.l1_chapters",
                "Level 1 supplies broad chapters. Peak status raises activity but does not guarantee eminence or crisis.",
                {
                    "technique": "zodiacal_releasing_map",
                    "lot": lot_name,
                    "chapters": l1_chapters,
                },
            )

    decennials = _sequence(fate.get("decennials"))
    current_date = report_date
    decennial_map: list[dict[str, Any]] = []
    try:
        _profection_now = _mapping(analysis.get("enhanced_profections")).get("age")
        _age_now = float(_profection_now) if isinstance(_profection_now, (int, float)) else 0.0
        _years_ahead = max(
            MIN_HORIZON_YEARS_AHEAD, _alcocoden_horizon_age(chart_data) - _age_now
        )
        horizon_end = (
            datetime.fromisoformat(report_date.replace("Z", "+00:00"))
            + timedelta(days=365.2425 * _years_ahead)
        ).date().isoformat()
    except ValueError:
        horizon_end = "9999-12-31"
    for period in decennials:
        if not isinstance(period, Mapping):
            continue
        period_start = str(period.get("start_date") or "")
        period_end = str(period.get("end_date") or "")
        if period_end <= report_date[:10] or period_start >= horizon_end:
            continue
        decennial_map.append(
            {
                "major_lord": period.get("major_lord"),
                "start": period_start,
                "end": period_end,
                "sub_periods": [
                    {
                        "sub_lord": sub.get("sub_lord"),
                        "start": sub.get("start_date"),
                        "end": sub.get("end_date"),
                    }
                    for sub in _sequence(period.get("sub_periods"))
                    if isinstance(sub, Mapping)
                    and str(sub.get("end_date") or "") > report_date[:10]
                    and str(sub.get("start_date") or "") < horizon_end
                ],
            }
        )
    if decennial_map:
        add(
            "timing_map",
            f"The long-range decennial map ({decennial_map[0].get('start')} to "
            f"{decennial_map[-1].get('end')}) contains "
            + "; ".join(
                f"{period.get('major_lord')} major ({period.get('start')} to {period.get('end')})"
                for period in decennial_map
            )
            + ".",
            "Vettius Valens tradition, 129-month decennial transmission",
            "valens_decennials_129_months",
            "analysis.fate.decennials",
            "This map identifies overlapping chronocrators only. Concrete prediction requires convergence with the nativity and another independent clock.",
            {"technique": "decennial_map", "periods": decennial_map},
        )
    for period in decennials:
        if not isinstance(period, Mapping):
            continue
        start = str(period.get("start_date") or "")
        end = str(period.get("end_date") or "")
        if not (start <= str(current_date) < end):
            continue
        sub_lord = None
        sub_start = None
        sub_end = None
        upcoming_subperiods = []
        for sub in _sequence(period.get("sub_periods")):
            if not isinstance(sub, Mapping):
                continue
            if str(sub.get("start_date") or "") <= str(current_date) < str(sub.get("end_date") or ""):
                sub_lord = sub.get("sub_lord")
                sub_start = sub.get("start_date")
                sub_end = sub.get("end_date")
            if str(sub.get("end_date") or "") > str(current_date):
                upcoming_subperiods.append(dict(sub))
        add(
            "timing",
            (
                f"The 129-month decennial sequence is in the {period.get('major_lord')} major period "
                f"from {start} through {end}; its current sub-period ruler is {sub_lord} "
                f"from {sub_start} through {sub_end}."
            ),
            "Vettius Valens tradition, 129-month decennial transmission",
            "valens_decennials_129_months",
            "analysis.fate.decennials",
            "The 129-month structure and planetary month shares are text-inspected, but the detailed computational exposition is transmitted in a section Riley labels a fifth-century addition. Calendar dates are a modern civil-month rendering. Decennials identify chronocrators; they do not independently promise an event.",
            {
                "technique": "decennials",
                "rulers": [period.get("major_lord"), sub_lord],
                "aphetic_lord": period.get("aphetic_lord"),
                "duration_months": period.get("duration_months"),
                "start": start,
                "end": end,
                "sub_start": sub_start,
                "sub_end": sub_end,
                "upcoming_subperiods": upcoming_subperiods[:3],
            },
        )
        break

    solar_return = _mapping(analysis.get("solar_return"))
    if solar_return:
        determinations = [
            item
            for item in _sequence(solar_return.get("determinations"))
            if isinstance(item, Mapping) and item.get("planet") in SEPTENER
        ]
        add(
            "annual_context",
            (
                f"The exact annual revolution at {solar_return.get('return_datetime_utc')} has {solar_return.get('return_ascendant', {}).get('sign')} rising; "
                f"its return-Ascendant ruler is {solar_return.get('return_ascendant_ruler', {}).get('name')}. "
                "The return planets are compared with the natal whole-sign places rather than mixed with a Tajika Muntha or arbitrary point score."
            ),
            "Abraham Ibn Ezra, Book of Revolution",
            "ibn_ezra_annual_revolution_core",
            "analysis.solar_return",
            (
                "Ibn Ezra treats the annual revolution as shorter-lived testimony that must be compared with the nativity, directions, profection, and repeated rulers. Return houses depend on location; this report uses the natal coordinates as a proxy because no return-location coordinates were supplied."
            ),
            {
                "year": solar_return.get("year"),
                "return_datetime_utc": solar_return.get("return_datetime_utc"),
                "return_ascendant": dict(_mapping(solar_return.get("return_ascendant"))),
                "return_ascendant_ruler": dict(_mapping(solar_return.get("return_ascendant_ruler"))),
                "sect_light_triplicity_comparison": dict(_mapping(solar_return.get("sect_light_triplicity_comparison"))),
                "determinations": [dict(item) for item in determinations],
                "location_basis": solar_return.get("location_basis"),
            },
        )

    temperament = _mapping(analysis.get("temperament"))
    if temperament.get("primary_temperament"):
        balance = _mapping(temperament.get("net_balance"))
        hot_cold = balance.get("Hot_vs_Cold")
        moist_dry = balance.get("Moist_vs_Dry")
        balance_text = (
            f"the hot/cold balance is {hot_cold} and the moist/dry balance is {moist_dry}"
            if hot_cold is not None and moist_dry is not None
            else "the detailed balance is unavailable"
        )
        add(
            "temperament",
            f"The configured humoral tally is {temperament.get('primary_temperament')}; {balance_text}.",
            "Lilly, Christian Astrology, planetary and elemental natures",
            "lilly_planetary_conditions",
            "analysis.temperament",
            "This is a historical temperament classification only; it does not classify the reader's body or mind.",
        )

    disagreements = _mapping(analysis.get("doctrinal_disagreements"))
    for fork in _sequence(disagreements.get("chart_specific")):
        if not isinstance(fork, Mapping) or fork.get("error"):
            continue
        positions = []
        for position in _sequence(fork.get("positions")):
            if isinstance(position, Mapping):
                positions.append(f"{position.get('authority')}: {position.get('value')}")
        add(
            "doctrinal_fork",
            f"For {fork.get('planet')}, authorities differ on {fork.get('factor')}: " + "; ".join(positions) + ".",
            "Competing authorities named in the computed doctrine payload",
            "computed_doctrinal_fork",
            "analysis.doctrinal_disagreements.chart_specific",
            "State both positions; do not silently merge or select them as universally correct.",
        )

    return evidence


def evidence_packet(chart_data: Mapping[str, Any]) -> dict[str, Any]:
    meta = _mapping(_mapping(chart_data.get("meta")).get("chart"))
    items = build_reading_evidence(chart_data)
    return {
        "subject": meta.get("name") or "Native",
        "birth": {
            "date": meta.get("date"),
            "time": meta.get("time"),
            "city": meta.get("city"),
            "state": meta.get("state"),
            "house_system": _mapping(meta.get("house_system")).get("label"),
            "zodiac_system": _mapping(meta.get("zodiac_system")).get("label"),
        },
        "scope": {
            "core_planets": list(SEPTENER),
            "excluded": [
                "outer planets",
                "medical and surgery material",
                "financial or legal direction",
                "planetary remediation prescriptions",
            ],
            "included_historical_techniques": [
                "Hyleg, Alcocoden, planetary years, Anareta, and competing longevity branches"
            ],
        },
        "evidence": [item.to_dict() for item in items],
    }
