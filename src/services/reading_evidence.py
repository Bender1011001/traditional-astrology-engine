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
            f"{a} forms a {aspect.get('type')} with {b}, orb {float(aspect.get('orb', 0.0)):.2f} degrees; applying: {bool(aspect.get('is_applying'))}.",
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
            for offset in range(6):
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
                "The six-year profection map runs "
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
            if len(l1_chapters) == 3:
                break
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
        horizon_end = (datetime.fromisoformat(report_date.replace("Z", "+00:00")) + timedelta(days=365.2425 * 6)).date().isoformat()
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
            "The six-year decennial map contains "
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
