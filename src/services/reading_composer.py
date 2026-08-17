"""Evidence-first premium reading composer.

The deterministic draft is always available.  An LLM may edit that draft for
clarity and synthesis, but it receives only the bounded evidence packet and may
not introduce new astrological claims.  The final prose is then validated by
the publication contract.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime
from typing import Any, Callable, Mapping

from src.services.reading_contract import (
    ReadingContractError,
    ReadingViolation,
    enforce_customer_reading,
)
from src.services.reading_evidence import evidence_packet
from src.services.judgment_planner import JudgmentPlan, build_judgment_plan


REPORT_NOTICE = (
    "Historical Use Only - this is a study of pre-modern astrological doctrine, "
    "not medical, financial, legal, psychological, emergency, or safety advice."
)

EDITOR_SYSTEM_PROMPT = """You are the final judging astrologer and editorial layer for a traditional natal report.

The JSON evidence packet is the complete universe of facts you may use. You do
not calculate, infer missing placements, invent events, diagnose the reader, or
add doctrine from memory. Preserve every [E#] citation and add at least one
evidence citation to every substantive interpretive paragraph.

The deterministic draft contains a chart-specific hierarchy as well as the
complete proof. Preserve its facts, but do not preserve its mechanical wording.
Write as an astrologer who has reached a judgment: identify the strongest source
of agency, the governing contradiction, the principal pressure network, and the
few life topics that those structures control. Then state what kind of person
and biography those testimonies describe. Do not walk through evidence in the
order it arrived and do not turn every modifier into a separate paragraph.

Be direct. Source-supported harsh testimony is mandatory and must not be
softened into vague possibility language. Equally, do not intensify a rule past
its stated condition or methodological limit. Distinguishing what a technique
does not establish is doctrinal accuracy, not emotional reassurance. Reception
assists without cancellation; sect moderates a malefic without making it benefic.

The opening judgment must be memorable and specific to this chart. Prefer a
clear contrast such as "This is not a chart of effortless support; it is a chart
of skill forced to operate under pressure" when the evidence supports it. End
the life judgment with a blunt synthesis of the native's strongest capacity,
chief recurrent danger, and most credible form of achievement.

Use exactly these top-level headings, once each, in this order:
# Your Nativity at a Glance
# The Leading Testimonies
# Life Topics
# The Present Chapter
# Where the Sources Differ
# Method and Limits

Requirements:
- 7,000 to 14,000 words when the packet contains a complete forensic nativity.
- Plain, dignified English suitable for a paying reader.
- Seven visible planets only. Never mention Uranus, Neptune, or Pluto.
- Preserve supplied historical Hyleg, Alcocoden, planetary-years, Anareta, and
  longevity branches exactly, including severe results and failed rival methods.
  Do not convert them into medical advice or conceal their methodological limits.
- No medical, surgery, remediation, investment, estate, contract, legal, or
  safety direction.
- No retrodicted events presented as validation.
- No raw JSON paths, field names, enum names, scores with false precision, or
  claims that a technique overrides all other testimony.
- No guarantees, commands, cosmic demands, or fear-based language.
- When sources disagree, name both positions supplied by the packet.
- Begin with the historical-use notice supplied in the draft. The evidence ledger is appended after editorial validation.
"""


NATAL_EDITOR_SYSTEM_PROMPT = """You are the final judging astrologer and editorial layer for a free natal report.

The JSON evidence packet is the complete universe of facts you may use. You do
not calculate, infer missing placements, invent events, diagnose the reader, or
add doctrine from memory. Preserve every [E#] citation and add at least one
evidence citation to every substantive interpretive paragraph.

The deterministic draft contains a chart-specific hierarchy as well as the
complete natal proof. Preserve its facts, but do not preserve its mechanical wording.
Write as an astrologer who has reached a judgment: identify the strongest source
of agency, the governing contradiction, the principal pressure network, and the
few life topics that those structures control. Then state what kind of person
and biography those testimonies describe. Do not walk through evidence in the
order it arrived and do not turn every modifier into a separate paragraph.

Be direct. Source-supported harsh testimony is mandatory and must not be
softened into vague possibility language. Equally, do not intensify a rule past
its stated condition or methodological limit. Distinguishing what a technique
does not establish is doctrinal accuracy, not emotional reassurance. Reception
assists without cancellation; sect moderates a malefic without making it benefic.

The opening judgment must be memorable and specific to this chart. Prefer a
clear contrast such as "This is not a chart of effortless support; it is a chart
of skill forced to operate under pressure" when the evidence supports it. End
the life judgment with a blunt synthesis of the native's strongest capacity,
chief recurrent danger, and most credible form of achievement.

Use exactly these top-level headings, once each, in this order:
# Your Nativity at a Glance
# The Leading Testimonies
# Life Topics
# Where the Sources Differ
# Method and Limits

Write in present and past tense only. Make direct "you are" and "your life has"
statements about who the native is and how the life has gone so far.

Forbidden:
- Future predictions and the phrase "you will"
- Dated forecasts
- This year's profection as a coming chapter
- Firdaria, zodiacal releasing, or decennials as upcoming periods
- A ranked forecast
- "the coming years"
- The heading "# The Present Chapter"

Requirements:
- Roughly 2,500 to 8,000 words is enough. Do not pad to 7,000-14,000.
- Plain, dignified English suitable for a reader judging whether the chart is accurate.
- Seven visible planets only. Never mention Uranus, Neptune, or Pluto.
- Do not publish length-of-life arithmetic, Hyleg, Alcocoden, or anaretic windows.
- No medical, surgery, remediation, investment, estate, contract, legal, or
  safety direction.
- No retrodicted events presented as validation.
- No raw JSON paths, field names, enum names, scores with false precision, or
  claims that a technique overrides all other testimony.
- No guarantees, commands, cosmic demands, or fear-based language.
- When sources disagree, name both positions supplied by the packet.
- Begin with the historical-use notice supplied in the draft. The evidence ledger is appended after editorial validation.
"""


ALLOWED_READING_SCOPES = frozenset({"full", "natal"})


def _normalize_reading_scope(scope: str) -> str:
    normalized = str(scope or "full").strip().lower()
    if normalized not in ALLOWED_READING_SCOPES:
        raise ValueError(
            f"Unsupported reading scope {scope!r}; expected 'full' or 'natal'."
        )
    return normalized


def _group(packet: Mapping[str, Any], category: str) -> list[Mapping[str, str]]:
    return [
        item
        for item in packet.get("evidence", [])
        if isinstance(item, Mapping) and item.get("category") == category
    ]


def _evidence_sentence(item: Mapping[str, str]) -> str:
    fact = str(item.get("fact") or "")
    for source, replacement in (
        ("configured phasis test", "phasis test"),
        ("configured maltreatment condition(s)", "recorded maltreatment condition(s)"),
        ("configured condition status", "recorded condition"),
        ("The configured humoral tally", "The historical humoral tally"),
        ("in the configured Egyptian bound", "in the Egyptian bound used here"),
    ):
        fact = fact.replace(source, replacement)
    return f"{fact} [{item.get('id')}]"


HOUSE_CONTEXT = {
    1: "self and embodied presence",
    2: "livelihood and movable resources",
    3: "learning, messages, siblings, and local movement",
    4: "home and foundations",
    5: "creative work, pleasure, gifts, and children",
    6: "labor, service, and burdens",
    7: "partnership and open contest",
    8: "shared resources, fear, and endings",
    9: "religion, study, divination, and long journeys",
    10: "action, reputation, and career",
    11: "friends, patrons, hopes, and alliances",
    12: "retreat, loss, and hidden difficulty",
}
PLANET_ORDER = {name: index for index, name in enumerate(("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"))}
SIGN_RULERS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}
PLANET_FUNCTIONS = {
    "Sun": "direction, authority, visibility, and the organizing center",
    "Moon": "adaptation, continuity, embodiment, and changing circumstance",
    "Mercury": "reasoning, speech, exchange, craft, and mediation",
    "Venus": "union, agreement, attraction, pleasure, and social cohesion",
    "Mars": "separation, contest, urgency, force, and decisive action",
    "Jupiter": "increase, judgment, faith, patronage, and constructive breadth",
    "Saturn": "limit, duration, responsibility, exclusion, and consolidation",
}

# Customer-facing delineation language.  These are not free-floating modern
# personality keywords: each statement is joined to the planet's calculated
# place, condition, rulerships, and configurations before publication.
PLANET_HUMAN_TOPICS = {
    "Sun": "authority, purpose, honors, leadership, and the father or commanding figures",
    "Moon": "habit, belonging, family life, the mother or caregiving figures, and changes of circumstance",
    "Mercury": "judgment, speech, writing, calculation, trade, technical craft, and negotiation",
    "Venus": "love, friendship, agreement, pleasure, art, and social attachment",
    "Mars": "anger, courage, competition, severance, conflict, and force",
    "Jupiter": "faith, judgment, teachers, patrons, children, generosity, and expansion",
    "Saturn": "fear, duty, delay, scarcity, endurance, age, exclusion, and lasting structures",
}

PLANET_DIRECT_CAPACITIES = {
    "Sun": "You need to direct your own course and are diminished when forced to live entirely under another person's authority.",
    "Moon": "Your circumstances and attachments change in visible cycles; what you repeatedly return to matters more than a passing mood.",
    "Mercury": "You meet life through analysis, language, classification, bargaining, and the ability to understand how a system works.",
    "Venus": "Bonds, allies, aesthetic judgment, and the ability to reconcile competing interests materially affect your fortunes.",
    "Mars": "Conflict is not peripheral in your life: you are repeatedly required to contend, cut away, compete, or act under pressure.",
    "Jupiter": "Growth comes through judgment, instruction, patronage, belief, and the ability to enlarge a field beyond its present limits.",
    "Saturn": "You encounter consequential limits, delays, duties, and fears that cannot be escaped by optimism and must be carried over time.",
}

PLANET_EPITHETS = {
    "Sun": "The Hidden King",
    "Moon": "The Dark Witness",
    "Mercury": "The Architect at the Helm",
    "Venus": "The Besieged Ally",
    "Mars": "The Quarrel Among Friends",
    "Jupiter": "The Fallen Giver",
    "Saturn": "The Warden of Obligations",
}

HOUSE_DIRECT_JUDGMENTS = {
    1: "This place describes your manner, agency, appearance to others, and command of your own life.",
    2: "This place describes earnings, possessions, livelihood, and what can be retained or lost.",
    3: "This place describes siblings, messages, study, short journeys, and the daily circulation of information.",
    4: "This place describes home, land, ancestry, parents, foundations, and the condition of life's endings.",
    5: "This place describes children, creative production, pleasure, gifts, sexuality, and ventures undertaken for joy.",
    6: "This is a place of illness, exhausting labor, service, dependency, subordinates, and burdens that do not confer rank.",
    7: "This place describes marriage, binding partnership, contracts, opponents, and people who meet you face-to-face.",
    8: "This is a place of death, fear, debt, inheritance, other people's resources, and obligations that reduce personal freedom.",
    9: "This place describes religion, divination, higher learning, law as a field of study, dreams, and long journeys.",
    10: "This place describes career, rank, action in the world, reputation, superiors, and what becomes publicly known.",
    11: "This place describes friends, patrons, alliances, hopes, honors received from others, and the gains of one's work.",
    12: "This is a place of isolation, hidden enemies, confinement, self-undoing, grief, and work conducted outside public view.",
}

PAIR_JUDGMENTS = {
    frozenset(("Sun", "Moon")): (
        "Your will and your changing needs are fused rather than easily separated. "
        "Private conditions therefore affect confidence and direction more strongly than outsiders usually see."
    ),
    frozenset(("Moon", "Saturn")): (
        "You carry emotional weight for a long time and can function under deprivation, but familiarity with hardship can become a habit in its own right."
    ),
    frozenset(("Mercury", "Mars")): (
        "Your mind is quick in contest: speech can become a weapon, technical problems provoke action, and argument often clarifies what passive reflection does not."
    ),
    frozenset(("Venus", "Mars")): (
        "Affection and conflict arrive together. Attraction is strong, but friendship and love are repeatedly complicated by rivalry, anger, urgency, or competing desires."
    ),
    frozenset(("Venus", "Jupiter")): (
        "Pleasure, affection, generosity, and expectation easily exceed their container; relationships and creative ventures can promise more than circumstances deliver."
    ),
    frozenset(("Venus", "Saturn")): (
        "Love and friendship are tested by distance, duty, rejection, unequal burdens, or delay. Durable bonds are possible, but they are selected through disappointment rather than innocence."
    ),
    frozenset(("Mars", "Jupiter")): (
        "Conviction escalates conflict. You can fight hard for a belief or opportunity, but zeal, overreach, and conflict with allies are recurring hazards."
    ),
    frozenset(("Mars", "Saturn")): (
        "This is a stop-and-strike configuration: force meets obstruction, anger meets fear, and action repeatedly encounters delay or punishment. It gives endurance under pressure but makes conflict costly."
    ),
    frozenset(("Jupiter", "Saturn")): (
        "Expansion and contraction repeatedly cancel or correct one another. Growth tends to come late, after revision, loss of excess, or acceptance of a narrower but more durable form."
    ),
}

PLANET_PERIOD_EVENTS = {
    "Sun": "changes of authority, leadership, reputation, relations with commanding figures, and the need to act from your own purpose",
    "Moon": "changes of residence or family circumstance, fluctuating alliances, travel or movement, caregiving demands, and reversals of habit",
    "Mercury": "study, writing, trade, negotiation, technical work, documents, travel, calculation, and decisions that redirect your public course",
    "Venus": "relationships, alliances, agreements, patrons, income, artistic work, pleasures, and the formation or ending of attachments",
    "Mars": "competition, disputes, severance, urgent action, conflict with allies, damaged agreements, and efforts that require force",
    "Jupiter": "teachers, patrons, children, creative ventures, belief, education, travel, generosity, and opportunities that enlarge responsibility",
    "Saturn": "delay, duty, isolation, scarcity, fear, older people, debts or shared burdens, endings, and structures that must endure pressure",
}


def _readable_reasons(reasons: list[str]) -> str:
    replacements = {
        "maltreatment/kakosis": "recorded maltreatment conditions",
        "essential dignity net-neutral (minor dignities offset by fall/detriment)": (
            "mixed essential condition, with minor dignity offset by debility"
        ),
        "peregrine (no essential dignity, not in fall/detriment)": "without recorded essential dignity",
        "afflicted by the Sun (Dark Moon)": "in the dark lunar phase near the Sun",
    }
    cleaned = []
    for reason in reasons:
        value = reason
        for source, replacement in replacements.items():
            value = value.replace(source, replacement)
        cleaned.append(value)
    if not cleaned:
        return "no further condition factors supplied"
    if len(cleaned) == 1:
        return cleaned[0]
    if len(cleaned) == 2:
        return f"{cleaned[0]} and {cleaned[1]}"
    return ", ".join(cleaned[:-1]) + f", and {cleaned[-1]}"


def _join_names(names: list[str]) -> str:
    """Join names as natural English: 'A', 'A and B', 'A, B, and C'."""
    names = [str(n) for n in names]
    if len(names) <= 1:
        return names[0] if names else ""
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + f", and {names[-1]}"


def _condition_phrase(details: Mapping[str, Any]) -> str:
    """Condition class with its correct English article, e.g. 'an unsupported'."""
    cls = _condition_class(details)
    article = "an" if cls[0] in "aeiou" else "a"
    return f"{article} {cls}"


def _condition_class(details: Mapping[str, Any]) -> str:
    dignity = str(details.get("dignities") or "").lower()
    if "domicile" in dignity or "exaltation" in dignity:
        return "strong"
    if "fall" in dignity or "detriment" in dignity:
        return "debilitated"
    if "no recorded" in dignity or "peregrine" in dignity:
        return "unsupported"
    return "mixed"


_VALENS_MALEFICS = {"Saturn", "Mars"}
_VALENS_BENEFICS = {"Jupiter", "Venus"}
_VALENS_DIURNAL = {"Sun", "Jupiter", "Saturn"}
_VALENS_NOCTURNAL = {"Moon", "Venus", "Mars"}
# Valens IV.11, 176: the injurious places. Benefics falling here "help nothing",
# are "ineffective and weak", and "do not distribute their own goods".
_VALENS_INJURIOUS_PLACES = {2, 6, 8, 12}


def _valens_placement_verdict(
    name: str, details: Mapping[str, Any], sect_type: Optional[str]
) -> Optional[str]:
    """Valens I.1, printed p. 5 - the placement-and-sect test, run BEFORE the label.

        "The benefics, well placed and in their proper places, accomplish their
         own effects ... BUT WHEN FALLEN, THEY ARE INDICATIVE OF OPPOSITIONS.
         Likewise the malefics: when transacting in their proper places AND OF
         THE SECT, they are GIVERS OF GOOD THINGS, and indicative of greater
         rank and of advancement."

    And I.22, p. 49, as method: the delineation lists are "single-form and
    universal distinctions", but "THE POWER OF THE MATTERS WILL BE ALTERED" by
    placement.

    The composer previously read essential dignity alone and asserted the
    verdict from the label - "because X is debilitated, these matters do not
    operate cleanly" - which is the judgment order Valens forbids. Returns a
    verdict only where his test actually fires, so ordinary cases fall through
    to the existing prose unchanged.
    """
    dignity = str(details.get("dignities") or "").lower()
    try:
        house = int(details.get("house") or 0)
    except (TypeError, ValueError):
        house = 0
    if not house:
        return None

    in_own_place = "domicile" in dignity or "exaltation" in dignity
    is_day = str(sect_type or "").upper().startswith("DAY")
    of_sect = name in (_VALENS_DIURNAL if is_day else _VALENS_NOCTURNAL)
    injurious = house in _VALENS_INJURIOUS_PLACES

    if name in _VALENS_MALEFICS and in_own_place and of_sect and not injurious:
        return (
            f"{name} is a malefic by nature, but the test Valens applies before the label is "
            f"placement and sect, and {name} passes both: it stands in its own place and is of "
            f"the sect in favour. On that reckoning it is a giver of good things here, and "
            f"indicative of greater rank and advancement - not of damage. The nature is the raw "
            f"material; the placement decides."
        )
    if name in _VALENS_BENEFICS and injurious:
        return (
            f"{name} is a benefic by nature, but it has fallen into one of the places Valens "
            f"counts injurious, and there he is explicit that the benefics do not distribute "
            f"their own goods. On that reckoning its testimony here is of opposition and "
            f"ineffectiveness rather than support. The nature does not survive the placement."
        )
    if name in _VALENS_MALEFICS and of_sect and not injurious:
        return (
            f"{name} is a malefic by nature but is of the sect in favour and does not stand in "
            f"an injurious place. Valens moderates it accordingly: its testimony is the manner "
            f"and severity of a difficulty, not a guarantee of one."
        )
    return None


def _direct_planet_delineation(
    name: str, details: Mapping[str, Any], sect_type: Optional[str] = None
) -> str:
    """State what a calculated planetary condition says about the native."""
    placement_first = _valens_placement_verdict(name, details, sect_type)
    if placement_first:
        return placement_first
    condition = _condition_class(details)
    house = int(details.get("house") or 0)
    place = HOUSE_CONTEXT.get(house, f"house {house}")
    human_topics = PLANET_HUMAN_TOPICS.get(name, PLANET_FUNCTIONS.get(name, name))
    capacity = PLANET_DIRECT_CAPACITIES.get(name, "")

    if condition == "strong":
        verdict = (
            f"Because {name} has major essential authority, these matters are real capabilities: you can originate, "
            "organize, and recover their operation from your own resources."
        )
    elif condition == "debilitated":
        verdict = (
            f"Because {name} is debilitated, these matters do not operate cleanly. They tend to bring misjudgment, "
            "frustration, excess, deficiency, or dependence on circumstances outside your control before producing anything durable."
        )
    elif condition == "unsupported":
        verdict = (
            f"Because {name} lacks essential dignity, these matters are highly responsive to circumstance and to the planets that receive, command, or afflict it."
        )
    else:
        verdict = (
            f"Because {name}'s condition is mixed, these matters produce genuine ability together with a recurring price, compromise, or limitation."
        )

    place_verdicts = {
        1: "The planet acts through your manner and choices, so its condition is conspicuous in how you speak, decide, and take command.",
        2: "Its condition repeatedly enters earning, possessions, and the question of what you can keep.",
        3: "Its condition appears through siblings, study, messages, documents, and frequent movement.",
        4: "Its condition is rooted in family, home, ancestry, land, and private foundations.",
        5: "Its condition becomes visible in love affairs, children, creative work, risk, pleasure, and the pursuit of enjoyment.",
        6: "Its condition is worked out through toil, illness symbolism, unequal service, subordinates, and obligations that consume time without conferring honor.",
        7: "Its condition is delivered by partners, opponents, clients, contracts, and other people who confront you directly.",
        8: "Its condition is delivered through fear, loss, debt, inheritance, intimacy, mortality, and dependence on resources controlled by others.",
        9: "Its condition seeks expression through religion, divination, higher study, teaching, dreams, and distant journeys.",
        10: "Its condition becomes public through career, rank, reputation, command, and consequential action.",
        11: "Its condition is delivered through friends, patrons, alliances, groups, ambitions, and the gains or disappointments produced by them.",
        12: "Its condition works behind the visible life through solitude, confinement, hidden opposition, grief, self-undoing, and labor performed away from recognition.",
    }
    place_verdict = place_verdicts.get(house, "Its place makes the planet's condition concrete in the life.")
    place_verdict = place_verdict[:1].lower() + place_verdict[1:]
    return (
        f"In your life {name} governs {human_topics}. {capacity} {verdict} "
        f"Its placement in {place} makes this concrete: {place_verdict}"
    )


def _direct_house_capacity(house: int, band: str, topic: str) -> str:
    if band == "well-supported":
        return (
            f"This is one of the strongest areas of the nativity. You possess real leverage over {topic}, and repeated activation of its ruler is likely to produce visible results."
        )
    if band == "supported":
        return (
            f"This area can produce what it promises, although results are more private, delayed, or dependent on the ruler's circumstances than they first appear."
        )
    if band == "impaired":
        return (
            f"Expect {topic} to require revision and sustained effort. Gains occur, but rarely by the first route attempted and often after disappointment or changed terms."
        )
    if band == "severely impaired":
        return (
            f"This is a genuinely difficult area of the nativity. Expected manifestations include obstruction, loss, conflict, absence, or outcomes controlled by other people unless stronger testimony intervenes."
        )
    return (
        f"This area is mixed: it delivers both advantage and difficulty, making {topic} a recurring field of negotiation rather than a settled possession."
    )


def _topic_native_prediction(
    details: Mapping[str, Any],
    planets: Mapping[str, Mapping[str, Any]],
    *,
    include_route: bool = True,
) -> str:
    """Translate a ruler chain into a concrete topical judgment."""
    house = int(details.get("house") or 0)
    ruler = str(details.get("ruler") or "the ruler")
    ruler_house = int(details.get("ruler_house") or 0)
    band = str(details.get("condition_band") or "mixed")
    reasons = " ".join(str(value).lower() for value in details.get("reasons", []))
    difficult = band in {"impaired", "severely impaired"}
    ruler_item = planets.get(ruler)
    ruler_details = ruler_item.get("details", {}) if ruler_item else {}

    predictions = {
        1: (
            "You are capable of taking command of your own course and are most effective when judgment, speech, and deliberate skill precede action."
            if not difficult
            else "Self-direction is repeatedly interrupted by circumstances or people represented by the ruler; confidence and control are won through repeated correction rather than assumed."
        ),
        2: (
            "Earnings and possessions are capable of growth through the ruler's people and places, but money is tied to relationship, alliance, or circumstance rather than existing as an isolated stream."
            if not difficult
            else "Income and possessions are unstable or expensive to maintain. Loss, delayed payment, poor terms, or dependence on other people's cooperation recurs when the ruler is activated."
        ),
        3: (
            "Learning, writing, messages, and short journeys become practical instruments of advancement; siblings and peers are consequential participants in the story."
            if not difficult
            else "Communication with siblings or peers is prone to distance, conflict, secrecy, or repeated misunderstanding, and journeys or documents more often require correction."
        ),
        4: (
            "Home and ancestry provide a usable foundation, although the ruler's place shows where the family story continues to demand attention."
            if not difficult
            else "The private foundation is unsettled: family, home, land, or relations with parents carry disappointment, absence, reversal, or burdens that take time to resolve."
        ),
        5: (
            "Creative work, love affairs, pleasure, and children can become substantial sources of meaning and production."
            if not difficult
            else "Pleasure does not remain simple in this nativity. Love affairs, children, creative ventures, speculation, or the pursuit of enjoyment bring delay, responsibility, disappointment, or a heavier cost than expected."
        ),
        6: (
            "You can master demanding work and service, but this place still signifies labor performed under necessity rather than honor."
            if not difficult
            else "Toil is one of the chart's unavoidable burdens. Work can be exhausting, unequal, repetitive, or performed for people who hold more power; periods ruled by this place also carry traditional illness and incapacity symbolism."
        ),
        7: (
            "Partnership is capable of becoming a major vehicle of opportunity, and important people materially redirect the life."
            if not difficult
            else "Marriage and binding partnership are difficult testimonies in this chart. Partners can arrive with their own reversals, burdens, divided loyalties, or unstable circumstances; open opponents can prolong disputes and force changed terms."
        ),
        8: (
            "Inheritance, shared resources, and other people's support can become operative, although they always arrive with obligation and reduced freedom."
            if not difficult
            else "Debt, inheritance, shared property, fear, loss, and dependence on resources controlled by others are severe testimonies. They are prone to dispute, delay, depletion, or obligations that outlast the original event."
        ),
        9: (
            "Religion, divination, higher study, teaching, and distant travel are capable of producing real advantage and a coherent philosophy of life."
            if not difficult
            else "Belief, teachers, advanced study, or long journeys bring reversals, disappointment, controversy, or a repeated need to reject an inadequate doctrine."
        ),
        10: (
            "Career is a commanding part of the nativity. Skill, judgment, and the ruler's natural work can produce rank, recognition, and visible responsibility."
            if not difficult
            else "Career and reputation are exposed to reversals, obstruction by superiors, damaged standing, or work whose result is controlled by others."
        ),
        11: (
            "Friends, patrons, and alliances can produce real gains, but the occupants and ruler determine whether those gains endure."
            if not difficult
            else "Friends and alliances are a major source of disappointment, concealed tension, or conflict. Groups can offer opportunity and then impose obligation, rivalry, exclusion, or loss."
        ),
        12: (
            "Solitude and work outside public view are powerful and productive in this nativity; private command can exceed visible command."
            if not difficult
            else "Isolation, hidden enemies, confinement, grief, and self-undoing are recurring difficulties rather than decorative symbolism. Periods ruled by this place reduce visibility and expose what has been concealed."
        ),
    }
    base = predictions.get(house, "The ruler's condition gives this topic concrete consequences in the life.")

    route = (
        f" Because its ruler is lodged in house {ruler_house}, developments in {HOUSE_CONTEXT.get(ruler_house, 'that house')} "
        "are the usual cause, setting, or consequence of these events."
    ) if include_route else ""
    modifiers: list[str] = []
    if "retrograde" in reasons or ruler_details.get("retrograde"):
        modifiers.append("The ruler's retrogradation makes return, reversal, or a delayed second attempt part of the outcome")
    if details.get("aversion"):
        modifiers.append("Aversion separates the ruler from direct oversight, so consequences often become visible only after the matter has developed")
    occupants = [str(value) for value in details.get("occupants", [])]
    if occupants:
        occupant_topics = "; ".join(
            f"{name} adds {PLANET_HUMAN_TOPICS.get(name, PLANET_FUNCTIONS.get(name, name))}"
            for name in occupants
        )
        modifiers.append(occupant_topics)
    modifier_text = (" " + ". ".join(modifiers) + ".") if modifiers else ""
    return base + route + modifier_text


def _topic_cluster_paragraphs(topical: list[Mapping[str, Any]]) -> list[str]:
    clusters: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for item in topical:
        details = item.get("details")
        if not isinstance(details, Mapping) or not details.get("ruler"):
            continue
        clusters[str(details["ruler"])].append(item)

    paragraphs: list[str] = []
    for ruler, items in clusters.items():
        details = items[0]["details"]
        ruler_label = "the Moon" if ruler == "Moon" else "the Sun" if ruler == "Sun" else ruler
        topics = [str(item["details"].get("topic")) for item in items]
        citations = " ".join(f"[{item.get('id')}]" for item in items)
        if len(topics) == 1:
            opening = f"{ruler_label.capitalize()} governs {topics[0]} in this nativity."
        elif len(topics) == 2:
            opening = (
                f"{ruler_label.capitalize()} governs both {topics[0]} and {topics[1]}. Their shared ruler means these topics "
                "should be read together rather than as isolated chapters."
            )
        else:
            opening = (
                f"{ruler_label.capitalize()} governs both "
                + ", ".join(topics[:-1])
                + f", and {topics[-1]}"
                + ". Their shared ruler means these topics should be read together rather than as isolated chapters."
            )

        ruler_house = details.get("ruler_house")
        placement_topic = HOUSE_CONTEXT.get(ruler_house, f"house {ruler_house}")
        reasons = _readable_reasons([str(value) for value in details.get("reasons", [])])
        band = str(details.get("condition_band") or "mixed")
        if band == "well-supported":
            judgment = (
                "This is one of the chart's clearest lines of agency: the ruler has substantial resources "
                "and an effective place from which to act."
            )
        elif band == "severely impaired":
            judgment = (
                "This is one of the more constrained ruler chains. It points to reduced or indirect capacity, "
                "but it does not by itself establish deprivation, failure, or a fixed event."
            )
        elif band == "impaired":
            judgment = (
                "The ruler remains relevant but works under meaningful constraints, so the topic is more likely "
                "to require mediation and sustained effort than direct expression."
            )
        elif band == "supported":
            judgment = (
                "The ruler retains genuine resources, although its placement limits how openly or directly those "
                "resources are expressed."
            )
        else:
            judgment = (
                "The ruler carries real resources and real impediments at once; the testimony is mixed and should "
                "not be forced into a simple favorable or unfavorable verdict."
            )

        aversion_topics = [
            str(item["details"].get("topic"))
            for item in items
            if item["details"].get("aversion")
        ]
        aversion = ""
        if aversion_topics:
            aversion = (
                " For " + " and ".join(aversion_topics) + ", the ruler is also in whole-sign aversion to its place, "
                "which adds a traditional symbol of weak oversight or disconnection."
            )
        occupants = sorted(
            {
                str(occupant)
                for item in items
                for occupant in item["details"].get("occupants", [])
                if str(occupant) != ruler
            }
        , key=lambda name: PLANET_ORDER.get(name, 99))
        if len(occupants) == 1:
            occupant_note = f" The occupied topics also contain {occupants[0]}, which supplies additional testimony."
        elif occupants:
            occupant_note = f" The occupied topics also contain {' and '.join(occupants)}, which supply additional testimony."
        else:
            occupant_note = ""
        paragraphs.append(
            f"{opening} {ruler_label.capitalize()} is in {details.get('ruler_sign')}, house {ruler_house}, routing these matters through "
            f"{placement_topic}. The condition ledger records {reasons}. {judgment}{aversion}{occupant_note} {citations}"
        )
    return paragraphs


def _topic_full_paragraphs(
    topical: list[Mapping[str, Any]],
    planets: list[Mapping[str, Any]],
) -> list[str]:
    """Judge every place once, without forcing the reader through a repeated template."""
    planet_map = {
        str(item.get("details", {}).get("name")): item
        for item in planets
        if isinstance(item.get("details"), Mapping)
    }
    by_house = {
        int(item["details"]["house"]): item
        for item in topical
        if isinstance(item.get("details"), Mapping)
        and isinstance(item["details"].get("house"), int)
    }
    paragraphs: list[str] = []
    for house in range(1, 13):
        item = by_house.get(house)
        if not item:
            continue
        details = item["details"]
        ruler = str(details.get("ruler"))
        topic = str(details.get("topic"))
        reasons = _readable_reasons([str(value) for value in details.get("reasons", [])])
        band = str(details.get("condition_band") or "mixed")
        capacity = _direct_house_capacity(house, band, topic)
        occupants = [str(value) for value in details.get("occupants", [])]
        if len(occupants) == 1:
            occupant_text = f" {occupants[0]} also occupies the place and delivers its testimony directly."
        elif occupants:
            occupant_text = f" {', '.join(occupants)} also occupy the place and deliver their testimony directly."
        else:
            occupant_text = ""
        aversion = (
            " The ruler is in aversion to this place, so oversight is weak and consequences tend to emerge after the matter is already under way."
            if details.get("aversion")
            else ""
        )
        ruler_house = details.get("ruler_house")
        routed_context = HOUSE_CONTEXT.get(ruler_house, f"house {ruler_house}")
        paragraphs.extend(
            [
                f"## House {house}: {topic.title()}",
                (
                    f"{HOUSE_DIRECT_JUDGMENTS.get(house, '')} In this nativity it falls in {details.get('sign')} and is "
                    f"ruled by {ruler} from {details.get('ruler_sign')} in house {details.get('ruler_house')}: developments "
                    f"in {routed_context} become the cause, setting, or consequence of {topic}. The ruler has {reasons}. "
                    f"{capacity}{aversion}{occupant_text} {_topic_native_prediction(details, planet_map, include_route=False)} "
                    f"[{item.get('id')}]"
                ),
            ]
        )

    clusters: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for item in topical:
        details = item.get("details")
        if isinstance(details, Mapping) and details.get("ruler"):
            clusters[str(details["ruler"])].append(item)
    linked = [values for values in clusters.values() if len(values) > 1]
    if linked:
        paragraphs.extend(["## The Houses That Share a Ruler"])
        for items in linked:
            ruler = str(items[0]["details"].get("ruler"))
            topics = [str(item["details"].get("topic")) for item in items]
            houses = [str(item["details"].get("house")) for item in items]
            citations = " ".join(f"[{item.get('id')}]" for item in items)
            paragraphs.append(
                f"Houses {', '.join(houses)} share {ruler} as ruler, joining {', '.join(topics)}. A change in {ruler}'s "
                "condition or activation therefore speaks through all of these places at once. This is one of the "
                f"chart's strongest connective principles and is more informative than reading each house in isolation. {citations}"
            )
    return paragraphs


def _planetary_testimony_paragraphs(
    planets: list[Mapping[str, Any]],
    aspects: list[Mapping[str, Any]],
    chart_rulers: list[Mapping[str, Any]],
    sect_type: Optional[str] = None,
) -> list[str]:
    """Interpret every planet's full publishable condition and its configurations."""
    by_name = {
        str(item.get("details", {}).get("name")): item
        for item in planets
        if isinstance(item.get("details"), Mapping)
    }
    paragraphs: list[str] = []

    luminaries = [by_name[name] for name in ("Sun", "Moon") if name in by_name]
    if luminaries:
        paragraphs.append("## The Two Lights")
        sun = by_name.get("Sun")
        moon = by_name.get("Moon")
        houses = {item["details"].get("house") for item in luminaries}
        shared = (
            " Their shared house makes the condition of visibility, retreat, and public expression a central tension: "
            "the lights are substantial, yet their effects are not always expressed in the most exposed or immediate way."
            if len(houses) == 1
            else " Read together, the two lights describe the chart's basic alternation between outward direction and responsive adaptation."
        )
        if sun and moon:
            sd, md = sun["details"], moon["details"]
            solar_condition = str(md.get("solar_status") or "its recorded solar condition").replace("_", " ").lower()
            paragraphs.append(
                f"The Sun is strong in {sd.get('sign')} but hidden in house {sd.get('house')}; the Moon is in the same sign and place with "
                f"{md.get('dignities')}, {solar_condition}, and {md.get('phasis') or 'its recorded phase'}. "
                "The will has real command, while the responsive and familial life is more obscured and dependent."
                f"{shared} [{sun.get('id')}] [{moon.get('id')}]"
            )

    ruler_name = None
    if chart_rulers:
        match = re.search(r"ranks ([A-Za-z]+) first", str(chart_rulers[0].get("fact")))
        ruler_name = match.group(1) if match else None
    if ruler_name in by_name:
        item = by_name[ruler_name]
        details = item["details"]
        context = HOUSE_CONTEXT.get(details.get("house"), f"house {details.get('house')}")
        paragraphs.append(
            f"{ruler_name} deserves separate emphasis because the Almuten calculation also places it first. "
            f"Its location routes a large share of the chart's agency through {context}. "
            "This is a statement about available agency and coordination, not permission to ignore contrary testimony. "
            f"[{item.get('id')}] [{chart_rulers[0].get('id')}]"
        )

    paragraphs.append("## The Seven Planetary Cabinets")
    for name in ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
        item = by_name.get(name)
        if not item:
            continue
        details = item["details"]
        dignity = str(details.get("dignities") or "")
        context = HOUSE_CONTEXT.get(details.get("house"), f"house {details.get('house')}")
        if any(term in dignity for term in ("domicile", "exaltation")):
            weight = "It therefore has a comparatively direct and self-consistent way of acting"
        elif any(term in dignity for term in ("fall", "detriment")):
            weight = "Its action is consequential but less self-directed, so outcomes depend more heavily on context, reception, and support"
        elif "no recorded" in dignity:
            weight = "It has no strong essential claim of its own and must be judged mainly through placement and relationship"
        else:
            weight = "Its minor dignities provide usable resources without making its testimony uncomplicated"
        motion = (
            "Retrogradation turns its operation back on itself: repetition, revision, delay, return, or an indirect route "
            "belongs to the manner in which it acts. Retrogradation does not make the planet absent."
            if details.get("retrograde")
            else "Direct motion gives the planet a more continuous outward sequence, although dignity and place still decide its effectiveness."
        )
        phase = str(details.get("phasis") or "not supplied")
        orientation = details.get("is_oriental")
        if orientation is True:
            orientation_text = "It is oriental to the Sun in the configured calculation, adding a morning, initiating emphasis."
        elif orientation is False:
            orientation_text = "It is occidental to the Sun in the configured calculation, adding an evening, responsive emphasis."
        else:
            orientation_text = "Orientality is not applied to this luminary."
        disposer = details.get("dispositor")
        disposer_text = (
            f"Its domicile dispositor is {disposer}, so the planet's ability to deliver its topics ultimately depends on {disposer}'s condition."
            if disposer and disposer != name
            else f"{name} is in its own domicile chain and therefore does not need another planet for sign-level governance."
        )
        paragraphs.extend(
            [
                f"### {name} — {PLANET_EPITHETS[name]}",
                (
                    f"{_evidence_sentence(item)} {_direct_planet_delineation(name, details, sect_type)} {weight}. {motion} "
                    f"Its phase is {phase}. {orientation_text} {disposer_text} [{item.get('id')}]"
                ),
            ]
        )
        maltreatments = [
            value for value in details.get("maltreatments", []) if isinstance(value, Mapping)
        ]
        if maltreatments:
            descriptions = "; ".join(
                str(value.get("description") or value.get("condition"))
                for value in maltreatments
            )
            paragraphs.append(
                f"The hard testimony around {name} is explicit: {descriptions}. These afflictions make its difficult manifestations more frequent and costly; "
                "benefic intervention or reception can create help, but neither removes the affliction nor promises escape from its consequences. "
                f"[{item.get('id')}]"
            )

    if aspects:
        paragraphs.append("## The Configuration Pattern")
        applying = [item for item in aspects if item.get("details", {}).get("is_applying")]
        separating = [item for item in aspects if not item.get("details", {}).get("is_applying")]
        parts = ["The aspect pattern shows how these capacities negotiate with one another."]
        if applying:
            parts.append(
                "Applying contacts describe combinations still pressing toward completion in the natal figure: "
                + " ".join(_evidence_sentence(item) for item in applying)
            )
        if separating:
            parts.append(
                "Separating contacts remain part of the structure but describe combinations already moving apart: "
                + " ".join(_evidence_sentence(item) for item in separating)
            )
        parts.append(
            "Conjunction and opposition concentrate the exchange; square makes it more laborious; trine and sextile provide easier access. "
            "None of these geometries can be judged apart from the condition and topical rulership of both planets."
        )
        paragraphs.append(" ".join(parts))
        paragraphs.extend(_aspect_synthesis_paragraphs(aspects, by_name))

    return paragraphs


def _aspect_synthesis_paragraphs(
    aspects: list[Mapping[str, Any]],
    planets: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    """Turn the aspect list into relational and network-level judgments."""
    geometry = {
        "Conjunction": "fuses the two operations into one concentrated field",
        "Opposition": "places the operations across an axis that requires alternation, negotiation, or confrontation",
        "Square": "forces the operations to meet through friction, work, and repeated adjustment",
        "Trine": "allows the operations to recognize and support one another with comparatively little resistance",
        "Sextile": "opens a usable line of cooperation that still requires participation",
    }
    paragraphs = ["### Aspect-by-Aspect Judgment"]
    contact_count: dict[str, int] = defaultdict(int)
    hard_edges: dict[str, set[str]] = defaultdict(set)
    for item in aspects:
        details = item.get("details", {})
        if not isinstance(details, Mapping):
            continue
        a = str(details.get("planet_a"))
        b = str(details.get("planet_b"))
        aspect_type = str(details.get("type"))
        pa = planets.get(a)
        pb = planets.get(b)
        if not pa or not pb:
            continue
        ad = pa["details"]
        bd = pb["details"]
        contact_count[a] += 1
        contact_count[b] += 1
        if aspect_type in {"Conjunction", "Opposition", "Square"}:
            hard_edges[a].add(b)
            hard_edges[b].add(a)
        motion = (
            "Because the contact is applying, the combination has a pressing, assembling quality in the natal structure."
            if details.get("is_applying")
            else "Because the contact is separating, it remains structural but has a releasing or already-formed quality."
        )
        a_house = ad.get("house")
        b_house = bd.get("house")
        a_context = HOUSE_CONTEXT.get(a_house, f"house {a_house}")
        b_context = HOUSE_CONTEXT.get(b_house, f"house {b_house}")
        pair_judgment = PAIR_JUDGMENTS.get(frozenset((a, b)))
        if not pair_judgment:
            if aspect_type == "Conjunction":
                pair_judgment = f"You experience {a}'s matters and {b}'s matters as one combined problem or opportunity; separating them is difficult."
            elif aspect_type == "Opposition":
                pair_judgment = f"You repeatedly meet a conflict between {a}'s matters and {b}'s matters, often through another person or an external circumstance."
            elif aspect_type == "Square":
                pair_judgment = f"The matters of {a} and {b} repeatedly obstruct one another and demand effort before either can produce a stable result."
            elif aspect_type == "Trine":
                pair_judgment = f"You can combine {a}'s matters with {b}'s matters readily, sometimes so automatically that the ability is underestimated."
            else:
                pair_judgment = f"You have a usable opportunity to coordinate {a}'s matters with {b}'s matters when you actively employ the connection."

        a_condition = _condition_class(ad)
        b_condition = _condition_class(bd)
        if a_condition == "strong" and b_condition in {"debilitated", "unsupported"}:
            condition_verdict = f"{a} has the stronger command and tends to recruit, correct, or dominate {b}; {b}'s difficulties still enter the result."
        elif b_condition == "strong" and a_condition in {"debilitated", "unsupported"}:
            condition_verdict = f"{b} has the stronger command and tends to recruit, correct, or dominate {a}; {a}'s difficulties still enter the result."
        elif a_condition == "debilitated" and b_condition == "debilitated":
            condition_verdict = "Both planets are debilitated, so the difficult manifestation is more reliable than the easy one and mitigation must be demonstrated rather than assumed."
        else:
            condition_verdict = "Their relative condition produces a mixed result: the aspect operates, but neither geometry nor goodwill erases the weaker testimony."
        paragraphs.append(
            f"{a} and {b}: the {aspect_type.lower()} {geometry.get(aspect_type, 'connects their operations')}. "
            f"It links {PLANET_FUNCTIONS.get(a, a)} in {a_context} "
            f"with {PLANET_FUNCTIONS.get(b, b)} in {b_context}. "
            f"{motion} {pair_judgment} {condition_verdict} [{item.get('id')}] "
            f"[{pa.get('id')}] [{pb.get('id')}]"
        )

    # Connected components expose configurations that disappear in a flat list.
    seen: set[str] = set()
    components: list[set[str]] = []
    for start in hard_edges:
        if start in seen:
            continue
        stack = [start]
        component: set[str] = set()
        while stack:
            current = stack.pop()
            if current in component:
                continue
            component.add(current)
            stack.extend(hard_edges.get(current, set()) - component)
        seen.update(component)
        if len(component) >= 3:
            components.append(component)
    for component in components:
        ordered = sorted(component, key=lambda name: PLANET_ORDER.get(name, 99))
        houses = sorted(
            {planets[name]["details"].get("house") for name in ordered if name in planets}
        )
        citations = " ".join(f"[{planets[name].get('id')}]" for name in ordered)
        paragraphs.append(
            f"The hard-contact network joins {', '.join(ordered)} across houses {', '.join(map(str, houses))}. This is "
            "a configuration, not a set of unrelated pairings: trouble entering any one planet travels through the "
            "others. You should expect the joined topics to become entangled in actual life; a dispute, loss, attachment, "
            "or opportunity in one house activates consequences in the others. Dignity and reception provide resources, "
            "but the network remains one of the chart's chief sources of conflict and consequential change. "
            f"{citations}"
        )
    if contact_count:
        maximum = max(contact_count.values())
        hubs = [name for name, count in contact_count.items() if count == maximum]
        hub_citations = " ".join(
            f"[{planets[name].get('id')}]" for name in hubs if name in planets
        )
        if len(hubs) == 1:
            paragraphs.append(
                f"The most connected planet in the aspect graph is {hubs[0]}, carrying {maximum} "
                "major contacts. It is an unavoidable distribution hub in your life: when it is activated, it "
                f"draws several otherwise separate topics into the same period and makes their condition visible through events. {hub_citations}"
            )
        else:
            paragraphs.append(
                f"The most connected planets in the aspect graph are {_join_names(hubs)}, each carrying {maximum} "
                "major contacts. These planets are unavoidable distribution hubs in your life: when one is activated, it "
                f"draws several otherwise separate topics into the same period and makes their condition visible through events. {hub_citations}"
            )
    return paragraphs


def _antiscia_paragraphs(
    items: list[Mapping[str, Any]], planets: list[Mapping[str, Any]]
) -> list[str]:
    if not items:
        return []
    item = items[0]
    cards = [
        card
        for card in item.get("details", {}).get("cards", [])
        if isinstance(card, Mapping)
    ]
    if not cards:
        return [
            "## Antiscia: Configurations Through the Reflected Degree",
            (
                f"{_evidence_sentence(item)} No antiscial major configuration is close enough to publish under the one-degree rule. "
                "The calculation was performed; absence is not replaced with a loose-orb claim."
            ),
        ]
    planet_map = {
        str(planet.get("details", {}).get("name")): planet
        for planet in planets
        if isinstance(planet.get("details"), Mapping)
    }
    paragraphs = [
        "## Antiscia: Configurations Through the Reflected Degree",
        (
            "Firmicus judges major aspects through reflected degrees like ordinary configurations. "
            f"He gives no orb, so this report uses a disclosed one-degree limit. [{item.get('id')}]"
        ),
    ]
    for card in cards:
        first = str(card.get("planet_1"))
        second = str(card.get("planet_2"))
        aspect = str(card.get("aspect"))
        orb = float(card.get("orb", 0.0))
        first_item = planet_map.get(first)
        second_item = planet_map.get(second)
        citations = f"[{item.get('id')}]"
        if first_item:
            citations += f" [{first_item.get('id')}]"
        if second_item:
            citations += f" [{second_item.get('id')}]"
        pair = frozenset((first, second))
        if pair == frozenset(("Sun", "Jupiter")) and aspect == "Trine":
            judgment = (
                "The Sun-Jupiter trine connects authority with creation, teaching, children, and patronage, routing hidden labor toward recognition. "
                "Jupiter's fall makes expansion costly or delayed without removing the trine."
            )
        elif pair == frozenset(("Moon", "Mercury")) and aspect == "Trine":
            judgment = (
                "The Moon-Mercury trine connects family grief and retreat with speech, analysis, and technical skill. "
                "You turn hardship into skilled work; Mercury organizes what the Moon leaves isolated."
            )
        elif pair == frozenset(("Mercury", "Mars")) and aspect == "Square":
            judgment = (
                "The Mercury-Mars square corrects their bodily sextile: your sharp mind meets quarrels, haste, severance, and hostile allies. "
                "Strong Mercury commands the conflict; fallen, out-of-sect Mars still damages friendships and plans."
            )
        else:
            judgment = (
                f"The {first}-{second} antiscial {aspect.lower()} links {PLANET_HUMAN_TOPICS.get(first, first)} with "
                f"{PLANET_HUMAN_TOPICS.get(second, second)} and must be weighed like an ordinary {aspect.lower()}."
            )
        paragraphs.append(f"{judgment} Orb: {orb:.2f}°. {citations}")
    return paragraphs


def _doryphory_paragraphs(
    items: list[Mapping[str, Any]], planets: list[Mapping[str, Any]]
) -> list[str]:
    if not items:
        return []
    item = items[0]
    cards = [
        card
        for card in item.get("details", {}).get("cards", [])
        if isinstance(card, Mapping)
    ]
    if not cards:
        return [
            "## Doryphory: The Luminaries and Their Attendants",
            (
                f"{_evidence_sentence(item)} The chart has no bodily spear-bearer under the audited same-sign/next-sign and phase conditions. "
                "No rank promise is invented from a planet that fails those rules."
            ),
        ]
    luminaries = item.get("details", {}).get("luminaries", {})
    if not isinstance(luminaries, Mapping):
        luminaries = {}
    planet_map = {
        str(planet.get("details", {}).get("name")): planet
        for planet in planets
        if isinstance(planet.get("details"), Mapping)
    }
    paragraphs = [
        "## Doryphory: The Luminaries and Their Attendants",
        (
            "Ptolemy places a bodily attendant in the luminary's own sign or the sign next following, with oriental stars "
            "serving the Sun and occidental stars serving the Moon. The prior fixed 30-degree shortcut was wrong and is no longer used. "
            f"[{item.get('id')}]"
        ),
    ]
    for card in cards:
        guard = str(card.get("guard"))
        luminary = str(card.get("luminary"))
        guard_item = planet_map.get(guard)
        luminary_item = planet_map.get(luminary)
        citations = f"[{item.get('id')}]"
        if guard_item:
            citations += f" [{guard_item.get('id')}]"
        if luminary_item:
            citations += f" [{luminary_item.get('id')}]"
        relation = str(card.get("placement_relation") or "").replace("_", " ")
        guard_details = guard_item.get("details", {}) if guard_item else {}
        luminary_details = luminary_item.get("details", {}) if luminary_item else {}
        guard_condition = _condition_class(guard_details)
        guard_topics = PLANET_HUMAN_TOPICS.get(guard, PLANET_FUNCTIONS.get(guard, guard))
        luminary_topics = PLANET_HUMAN_TOPICS.get(luminary, PLANET_FUNCTIONS.get(luminary, luminary))
        guard_place = HOUSE_CONTEXT.get(guard_details.get("house"), f"house {guard_details.get('house')}")
        luminary_place = HOUSE_CONTEXT.get(luminary_details.get("house"), f"house {luminary_details.get('house')}")
        paragraphs.append(
            f"{guard} is the {luminary}'s spear-bearer: it is {card.get('phase')} and in the {relation}, even though the bodies are "
            f"{float(card.get('delta_deg') or 0.0):.2f} degrees apart. The guard occupies {guard_place} and is {guard_condition}; the attended light occupies {luminary_place}. "
            f"Consequently {guard_topics} serve {luminary_topics}: the guard gives the light a route to act through its own condition and place. "
            + ("The guard is angular, so the attendance has public force. " if card.get("guard_angular_wsh") else "The guard is not angular, so the attendance has less power to confer visible rank. ")
            + f"{citations}"
        )
    sun = luminaries.get("Sun", {}) if isinstance(luminaries.get("Sun"), Mapping) else {}
    moon = luminaries.get("Moon", {}) if isinstance(luminaries.get("Moon"), Mapping) else {}
    if not sun.get("angular_wsh") and not moon.get("angular_wsh"):
        masculine = [name for name, value in (("Sun", sun), ("Moon", moon)) if value.get("masculine_sign")]
        angular_guards = [str(card.get("guard")) for card in cards if card.get("guard_angular_wsh")]
        paragraphs.append(
            "Neither luminary is angular, so Ptolemy's royal or sovereign branch is not present. "
            + (f"The masculine-sign condition is present for {', '.join(masculine)}. " if masculine else "Neither light supplies the masculine-sign condition used in the higher rank branches. ")
            + (f"The angular attendant testimony belongs to {', '.join(dict.fromkeys(angular_guards))}; this can support a leading role in ordinary civil, organizational, educational, commercial, or administrative affairs without becoming the royal branch. " if angular_guards else "No attendant is angular enough to supply the stronger lower-rank testimony. ")
            + f"[{item.get('id')}]"
        )
    return paragraphs


def _dispositor_paragraphs(items: list[Mapping[str, Any]]) -> list[str]:
    if not items:
        return []
    item = items[0]
    chains = item.get("details", {}).get("chains", [])
    if not isinstance(chains, list):
        return []
    endpoints: dict[str, list[str]] = defaultdict(list)
    loops: list[list[str]] = []
    for record in chains:
        if not isinstance(record, Mapping):
            continue
        chain = [str(value) for value in record.get("chain", [])]
        if not chain:
            continue
        if record.get("outcome") == "closed_loop":
            loops.append(chain)
        else:
            endpoints[chain[-1]].append(chain[0])
    paragraphs = ["## The Dispositor Architecture", _evidence_sentence(item)]
    for endpoint, dependents in endpoints.items():
        if len(dependents) == 1:
            description = dependents[0]
        else:
            description = ", ".join(dependents[:-1]) + f", and {dependents[-1]}"
        paragraphs.append(
            f"{endpoint} is the terminal domicile ruler for {description}. This makes {endpoint}'s condition a chart-wide "
            "bottleneck: when it is supported, several testimonies gain a route to act; when it is constrained, those "
            f"same testimonies must work through its limitations. This is dependence, not cancellation. [{item.get('id')}]"
        )
    for chain in loops:
        paragraphs.append(
            f"The chain {' -> '.join(chain)} closes into a circuit. The planets exchange governance rather than reaching "
            f"an independent final dispositor, so their topics remain mutually entangled. [{item.get('id')}]"
        )
    return paragraphs


def _joy_paragraphs(
    joys: list[Mapping[str, Any]], planets: list[Mapping[str, Any]]
) -> list[str]:
    if not joys:
        return []
    planet_map = {
        str(item.get("details", {}).get("name")): item
        for item in planets
        if isinstance(item.get("details"), Mapping)
    }
    paragraphs = ["## Planetary Joys Present in This Nativity"]
    for joy in joys:
        details = joy.get("details", {})
        name = str(details.get("name"))
        planet = planet_map.get(name)
        if not planet:
            continue
        pd = planet["details"]
        paragraphs.append(
            f"{_evidence_sentence(joy)} This place-based affinity reinforces {name}'s ability to perform its natural "
            f"work in {HOUSE_CONTEXT.get(pd.get('house'), 'that place')}. Here it operates alongside {pd.get('dignities')} "
            "essential condition, motion, visibility, aspects, and rulerships; the joy strengthens the testimony without "
            f"becoming an override. [{planet.get('id')}]"
        )
    return paragraphs


def _sect_condition_paragraphs(
    items: list[Mapping[str, Any]], planets: list[Mapping[str, Any]]
) -> list[str]:
    if not items:
        return []
    planet_map = {
        str(item.get("details", {}).get("name")): item
        for item in planets
        if isinstance(item.get("details"), Mapping)
    }
    paragraphs = [
        "## Hayz and Halb",
        (
            "Hayz and halb refine sect through the planet's actual position above or below ground. Halb is the horizon "
            "accord; hayz adds agreement between planetary and sign gender. Mercury is not forced into either family "
            "because the inspected source makes its classification conditional."
        ),
    ]
    for item in items:
        details = item.get("details", {})
        name = str(details.get("name"))
        planet = planet_map.get(name)
        if not planet:
            continue
        pd = planet["details"]
        if details.get("status") == "Hayz":
            effect = (
                "The full agreement gives the planet a more coherent accidental setting in which to perform its own nature."
            )
        else:
            effect = (
                "The horizon agreement supplies partial accidental support, while sign gender does not complete hayz."
            )
        paragraphs.append(
            f"{_evidence_sentence(item)} {effect} Its {pd.get('dignities')} essential condition, house, motion, "
            f"visibility, and aspects still control what that support can accomplish. [{planet.get('id')}]"
        )
    return paragraphs


def _paulus_place_rule_paragraphs(
    items: list[Mapping[str, Any]], planets: list[Mapping[str, Any]]
) -> list[str]:
    """Apply only the chart-relevant planet-in-place rules inspected in Paulus.

    These are deliberately direct.  Modifiers describe how the promised event
    manifests; they never suppress a difficult source rule merely because the
    result is unpleasant.
    """
    if not items:
        return []
    by_name = {
        str(item.get("details", {}).get("name")): item
        for item in items
        if isinstance(item.get("details"), Mapping)
    }
    planet_map = {
        str(item.get("details", {}).get("name")): item
        for item in planets
        if isinstance(item.get("details"), Mapping)
    }
    paragraphs = [
        "## Paulus: The Planets in Their Places",
        (
            "The following judgments are the chart-specific rules printed in Paulus's chapter on the twelve places. "
            "They are not replaced with modern personality language. Dignity, sect, motion, and aspects decide how "
            "literally and how severely each rule manifests, but they do not erase a placement because its judgment is harsh."
        ),
    ]

    mercury = by_name.get("Mercury")
    if mercury:
        d = mercury["details"]
        contacts = d.get("malefic_contacts") or []
        dignity = str(d.get("dignities") or "without supplied dignity")
        contact_names = ", ".join(
            f"{value.get('other')} by {str(value.get('type')).lower()}"
            for value in contacts
            if isinstance(value, Mapping)
        )
        paragraphs.append(
            f"Mercury in the first activates Paulus's joy and preservation testimony. Its recorded essential condition is {dignity}. "
            "The native meets difficulty through intelligence, calculation, language, technical skill, trade, analysis, and the ability to understand a situation quickly. "
            + (
                f"Paulus's fuller preservation-and-good-fortune clause is qualified because Mercury is configured with {contact_names}. "
                "Cleverness must therefore operate inside conflict, urgency, fear, argument, or damage control rather than guaranteeing an untouched life of ease. "
                if contacts
                else "No malefic contact is recorded here, so Paulus's fuller preservation-and-good-fortune condition is intact. "
            )
            + f"[{mercury.get('id')}]"
        )

    jupiter = by_name.get("Jupiter")
    if jupiter:
        d = jupiter["details"]
        damaged = (
            "fall" in str(d.get("dignities", "")).lower()
            or bool(d.get("retrograde"))
            or bool(d.get("maltreatments"))
        )
        damage_reasons = []
        if "fall" in str(d.get("dignities", "")).lower():
            damage_reasons.append("fall")
        if d.get("retrograde"):
            damage_reasons.append("retrogradation")
        if d.get("maltreatments"):
            damage_reasons.append("recorded maltreatment")
        paragraphs.append(
            "Jupiter in the fifth preserves Paulus's promise that a benefic there gives fertility of creations, pleasures, gifts, "
            "and children. In your life the fifth place is not barren: it produces things, projects, attachments, or dependents that matter. "
            + (
                f"But the promise is damaged by {', '.join(damage_reasons)}. Joy can be followed by responsibility; "
                "creative ventures expand and then become costly or difficult to sustain; matters involving children, romance, speculation, "
                "or pleasure are liable to delay, reversal, disappointment, or burdens larger than first expected. The source promise remains, "
                "but it does not promise an easy or continuously fortunate fifth-place life. "
                if damaged
                else "Jupiter's condition does not record the major debilities that would seriously damage that promise. "
            )
            + f"[{jupiter.get('id')}]"
        )

    saturn = by_name.get("Saturn")
    if saturn:
        d = saturn["details"]
        condition = _condition_class(d)
        motion = "retrograde" if d.get("retrograde") else "direct"
        paragraphs.append(
            "Saturn in the eighth makes other people's resources, inheritances, obligations, fear, loss, and the consequences of endings "
            "a durable part of your biography. Paulus explicitly allows profit through death or inheritance even from a malefic in this place, "
            f"so material benefit can come through estates, settlements, or taking responsibility after a loss. Saturn is {condition} and {motion}; "
            "its actual dignity, sect condition, motion, and aspects decide whether what comes is durable, delayed, contested, diminished, or tied to duty and prolonged administration. "
            "No amount of essential strength turns the eighth into an uncomplicated place. The native can spend long periods carrying "
            "burdens that began with another person's crisis, absence, property, or unfinished obligation. This is historical inheritance-and-loss "
            f"judgment, not advice and not a prediction of a named person's death. [{saturn.get('id')}]"
        )

    mars = by_name.get("Mars")
    if mars:
        d = mars["details"]
        if d.get("day_chart"):
            mars_condition = _condition_class(d)
            paragraphs.append(
                "Mars in the eleventh must be judged by Paulus's daytime branch. The favorable nocturnal branch does not belong to your chart. "
                "The printed daytime result is loss of things, changes of place, accidents, reduction of vitality or longevity, and affliction involving "
                "children. In lived terms, friends, groups, patrons, alliances, and hoped-for futures repeatedly become the route through which conflict, "
                f"separation, expense, abrupt relocation, or physical danger enters. Mars is {mars_condition} and contrary to the day sect, so the printed day branch remains severe. "
                "Not every ally remains an ally; some associations can consume resources, turn hostile, "
                "or force you to abandon a plan. The statement about reduced life belongs to Paulus's historical rule, but this placement alone cannot "
                f"determine the duration of life or the time of death. [{mars.get('id')}]"
            )
        else:
            paragraphs.append(
                "Mars in the eleventh falls under Paulus's nocturnal branch, which is materially more favorable than his daytime judgment. "
                f"That sect distinction must govern the interpretation. [{mars.get('id')}]"
            )

    venus = by_name.get("Venus")
    if venus:
        d = venus["details"]
        afflicted = bool(d.get("malefic_regard_present")) or bool(d.get("maltreatments"))
        malefic_contacts = [
            str(value.get("other"))
            for value in d.get("malefic_contacts", [])
            if isinstance(value, Mapping) and value.get("other")
        ]
        paragraphs.append(
            "Venus in the eleventh carries Paulus's promise of fortunate partnership, orderly conduct, sufficiency, and improving fortune through time. "
            "You can receive real affection, social support, opportunity, and material help through friends or partners. "
            + (
                "But Paulus makes the clean result especially dependent on Venus not being struck by malefic rays, and that exception is active through "
                f"{', '.join(dict.fromkeys(malefic_contacts)) or 'the recorded malefic testimony'}. Love and friendship are therefore mixed with quarrels, divided loyalties, cooling, delay, "
                "jealousy, harsh circumstances, or having to choose between attachment and self-protection. The chart does not deny relationship or support; "
                "it says the support is repeatedly damaged by conflict and that apparently fortunate alliances can become the source of the loss promised by Mars. "
                if afflicted
                else "No recorded malefic configuration activates Paulus's stated exception, so the favorable branch stands relatively cleanly. "
            )
            + f"[{venus.get('id')}]"
        )

    sun = by_name.get("Sun")
    if sun:
        d = sun["details"]
        paragraphs.append(
            "The Sun in the twelfth activates Paulus's severe testimony concerning father, status, visibility, labor, and need. The father may be absent, "
            "far away, exiled from his proper role, impoverished, injured by circumstance, or unable to confer the protection and standing expected of him. "
            "For you, advancement is not simply handed over by family or authority: major work develops in obscurity, isolation, institutions, hidden conflict, "
            "or service that is not initially recognized. Periods of being overlooked, shut out, burdened by another person's trouble, or forced to work behind "
            f"the scenes are part of the life. The Sun's recorded condition is {_condition_class(d)} ({d.get('dignities')}); this does not erase "
            "the twelfth, but it decides whether the native can command hidden or difficult environments or is more completely subjected to them. "
            f"that Paulus otherwise describes as low and needy. [{sun.get('id')}]"
        )

    moon = by_name.get("Moon")
    if moon:
        d = moon["details"]
        regard = bool(d.get("malefic_regard_present"))
        contacts = [value for value in d.get("malefic_contacts", []) if isinstance(value, Mapping)]
        contact_text = ", ".join(
            f"{value.get('other')} by {str(value.get('type')).lower()} ({'applying' if value.get('is_applying') else 'separating'})"
            for value in contacts
        )
        paragraphs.append(
            "The Moon in the twelfth describes recurring withdrawal, loneliness, loss, hidden grief, confinement by circumstances, and difficulty receiving "
            "reliable care. "
            + (
                f"Paulus's harsher conditional branch is active because the Moon is regarded by {contact_text}. His text connects this with maternal illness, injury, shortened "
                "life, or impaired maternal support, and calls the native poor, struggling, and persistently unfortunate. This must be stated, but it must also be "
                "calculated through the actual aspect type, application, sect, and condition of the malefic. The rule signifies real maternal vulnerability, sorrow, distance, "
                "limitation, or loss of support, plus repeated periods of hardship; it does not by itself identify a particular ailment or determine a time of death. "
                "An easy aspect can make endurance and usable experience possible, but does not remove the malefic regard. "
                if regard
                else "No malefic regard or application is recorded, so Paulus's harsher conditional branch is not activated merely by the Moon's place. "
            )
            + f"[{moon.get('id')}]"
        )
    return paragraphs


def _dodecatemoria_paragraphs(
    x12_items: list[Mapping[str, Any]],
    x13_items: list[Mapping[str, Any]],
    planets: list[Mapping[str, Any]],
) -> list[str]:
    if not x12_items and not x13_items:
        return []
    x12 = {
        str(item.get("details", {}).get("name")): item
        for item in x12_items
        if isinstance(item.get("details"), Mapping)
    }
    x13 = {
        str(item.get("details", {}).get("name")): item
        for item in x13_items
        if isinstance(item.get("details"), Mapping)
    }
    planet_map = {
        str(item.get("details", {}).get("name")): item
        for item in planets
        if isinstance(item.get("details"), Mapping)
    }
    paragraphs = [
        "## Twelfth-Parts: A Visible Method Fork",
        (
            "The twelfth-part projects a planet's degree into a secondary zodiacal position. Paulus' thirteen-fold "
            "instruction is text-verified; the twelve-fold calculation remains a configured variant whose legacy "
            "attribution to Valens is unresolved. Both are shown because concealing the disagreement would create false precision."
        ),
    ]
    for name in ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"):
        standard = x12.get(name)
        paulus = x13.get(name)
        if not standard or not paulus:
            continue
        sd = standard["details"]
        pd = paulus["details"]
        natal = planet_map.get(name)
        natal_citation = f" [{natal.get('id')}]" if natal else ""
        if sd.get("sign") == pd.get("sign") and sd.get("house") == pd.get("house"):
            agreement = (
                f"Both methods place the projection in {sd.get('sign')}, house {sd.get('house')}. The agreement makes "
                "that secondary place stable across this particular fork"
            )
            if sd.get("term_ruler") != pd.get("term_ruler"):
                agreement += (
                    f", although the exact degree changes the bound ruler from {sd.get('term_ruler')} to {pd.get('term_ruler')}"
                )
            agreement += "."
        else:
            agreement = (
                f"The methods diverge: x12 gives {sd.get('sign')} in house {sd.get('house')}, while Paulus x13 gives "
                f"{pd.get('sign')} in house {pd.get('house')}. No single derived-place judgment is allowed here; the "
                "difference is itself the doctrinal result."
            )
        paragraphs.append(
            f"{name}: {_evidence_sentence(standard)} {_evidence_sentence(paulus)} {agreement} The natal planet remains "
            f"primary, and the twelfth-part can only qualify its already-established condition.{natal_citation}"
        )
    return paragraphs


def _monomoiria_paragraphs(
    zoidion_items: list[Mapping[str, Any]],
    trigonal_items: list[Mapping[str, Any]],
    planets: list[Mapping[str, Any]],
) -> list[str]:
    if not zoidion_items and not trigonal_items:
        return []
    planet_map = {
        str(item.get("details", {}).get("name")): item
        for item in planets
        if isinstance(item.get("details"), Mapping)
    }
    paragraphs = ["## Monomoiria: The Ruler of Each Degree"]
    if zoidion_items:
        item = zoidion_items[0]
        paragraphs.append(_evidence_sentence(item))
        cards = [
            value
            for value in item.get("details", {}).get("cards", [])
            if isinstance(value, Mapping)
        ]
        for card in cards:
            name = str(card.get("name"))
            ruler = str(card.get("ruler"))
            target = planet_map.get(name)
            ruler_item = planet_map.get(ruler)
            target_topics = PLANET_HUMAN_TOPICS.get(name, name)
            if card.get("self_ruled"):
                verdict = (
                    f"{name} occupies its own degree. This gives {target_topics} an additional layer of self-command and "
                    "makes the planet less dependent on another degree lord, although it does not cancel house placement or affliction."
                )
            elif ruler_item:
                ruler_details = ruler_item["details"]
                ruler_condition = _condition_class(ruler_details)
                verdict = (
                    f"{name}'s degree is governed by {ruler}. Consequently {target_topics} must obtain secondary permission "
                    f"through {PLANET_HUMAN_TOPICS.get(ruler, ruler)}. Because {ruler} is {ruler_condition} and placed in "
                    f"{HOUSE_CONTEXT.get(ruler_details.get('house'), 'its natal house')}, that condition enters {name}'s results."
                )
            else:
                verdict = f"{name}'s degree is governed by {ruler}, adding that planet as a secondary dependency."
            citations = [f"[{item.get('id')}]" ]
            if target:
                citations.append(f"[{target.get('id')}]" )
            if ruler_item and ruler_item is not target:
                citations.append(f"[{ruler_item.get('id')}]" )
            paragraphs.append(verdict + " " + " ".join(citations))
        paragraphs.append(
            "Paulus describes degree mastership but does not assign the modern project score of one point. Where a self-ruled "
            f"monomoiria contributes +1 to an internal ranking, that number is a disclosed configured weighting rather than a quotation from Paulus. [{item.get('id')}]"
        )
    if trigonal_items:
        item = trigonal_items[0]
        details = item.get("details", {})
        name = str(details.get("name"))
        ruler = str(details.get("ruler"))
        paragraphs.append(
            f"{_evidence_sentence(item)} This canon belongs to the sect light alone. In this chart it makes {ruler} the "
            f"degree-level trigonal master of {name}; it is not attached to the other six planets. "
            + (
                "Because the sect light and its trigonal degree ruler are the same planet, the chart's central light has unusually concentrated degree-level command. "
                if name == ruler
                else f"The sect light therefore depends secondarily on {ruler}'s natal condition. "
            )
            + f"[{item.get('id')}]"
        )
    return paragraphs


def _causative_place_paragraphs(items: list[Mapping[str, Any]]) -> list[str]:
    """Render Valens V.1, printed pp. 207-209.

    A Lot built from the two malefics alone. Valens names its subject outright -
    fears, dangers, confinement - but makes it conditional: what decides whether
    the place is live is malefic ownership of, or aspect to, the resulting sign.
    Where no malefic testifies, the emitter says his test is silent, and that
    silence is the finding. Printing the subject without the condition would be
    the same error the bounds made in reverse.
    """
    if not items:
        return []
    paragraphs = ["## The Causative Place (Valens V.1)"]
    for item in items:
        paragraphs.append(_evidence_sentence(item))
    return paragraphs


def _climacteric_year_paragraphs(items: list[Mapping[str, Any]]) -> list[str]:
    """Render Valens V.2, printed p. 210.

    Distinct from the III.15 climacteric rendered elsewhere: that one derives a
    PERIODICITY from a malefic's figure to the Lot of Fortune and names an
    interval; this profects from the ascendant against the pre-natal syzygy and
    names specific years.

    The lattice note in the prose is not padding. The rule marks four signs of
    twelve, so the marked years land every third year in every chart - only the
    offset differs. A bare list of thirty ages reads as a catalogue of disaster
    unless the arithmetic behind it is stated in the same breath.
    """
    if not items:
        return []
    paragraphs = ["## Climacteric Years from the Pre-Natal Syzygy (Valens V.2)"]
    paragraphs.append(
        "Valens marks a year as climacteric when the sign profected from the ascendant "
        "falls on the sign of the lunation before birth, or square or opposite it. Because "
        "that is four signs out of twelve, the marked years recur every third year in any "
        "chart and only their offset differs from one nativity to another. The count below "
        "is a property of the arithmetic, not a measure of how hard a life is, and Valens "
        "names one aggravating witness for such a year - transiting Saturn in a cadent "
        "place - which is a per-year transit and is not evaluated here."
    )
    for item in items:
        paragraphs.append(_evidence_sentence(item))
    return paragraphs


def _bound_delineation_paragraphs(items: list[Mapping[str, Any]]) -> list[str]:
    """Render Valens I.3, printed pp. 14-19.

    The emitter for these was added without a renderer, so the packet carried
    the delineations and the prose never printed them. The appendix still cited
    the items - which meant the report shipped the CAVEAT ("the domicile lord
    decides whether what the degree carries comes out base or good") with no
    statement of what the degree carries. A dangling condition is worse than
    silence: it points at a claim that was never made.

    The table is complete at 60 of 60, so every planet and the Ascendant have a
    delineation; a gap still renders nothing rather than inventing.
    """
    if not items:
        return []
    paragraphs = ["## The Bounds of the Degrees (Valens I.3)"]
    paragraphs.append(
        "Valens delineates each of the sixty bounds individually. What follows is the "
        "substrate of the degrees themselves, not a verdict on you. Valens closes the "
        "chapter by saying he set the degrees out one at a time for teaching, and that "
        "in a real nativity the domicile lord lying over them decides whether what the "
        "degree carries comes out base or good. Read every line below under that "
        "condition, and against placement and sect, which outweigh it."
    )
    for item in items:
        paragraphs.append(_evidence_sentence(item))
    return paragraphs


def _degree_quality_paragraphs(items: list[Mapping[str, Any]]) -> list[str]:
    if not items:
        return []
    item = items[0]
    cards = [
        value
        for value in item.get("details", {}).get("cards", [])
        if isinstance(value, Mapping)
    ]
    if not cards:
        return []
    paragraphs = ["## Lilly's Degree Qualities"]
    compact = []
    for card in cards:
        flags = [str(card.get("light_dark_smoky_void"))]
        if card.get("pitted"):
            flags.append("pitted")
        if card.get("azimene"):
            flags.append("azimene")
        if card.get("increasing_fortune"):
            flags.append("increasing fortune")
        compact.append(
            f"{card.get('body')} at one-based {card.get('sign')} degree {card.get('degree_one_based')} "
            f"({', '.join(value for value in flags if value and value != 'None')})"
        )
    paragraphs.append(
        "The chart's table entries are " + "; ".join(compact) + f". [{item.get('id')}]"
    )

    appearance = [card for card in cards if card.get("appearance_scope")]
    for card in appearance:
        quality = str(card.get("light_dark_smoky_void") or "")
        body = str(card.get("body"))
        if quality == "light":
            judgment = "Lilly gives the light degree a fairer, clearer, and more capable expression."
        elif quality == "dark":
            judgment = "Lilly gives the dark degree a darker or more obscure outward cast and treats existing imperfections as more conspicuous."
        elif quality == "smoky":
            judgment = "Lilly gives the smoky degree a mixed outward condition and mixed judgment, neither extreme in fairness, stature, or discernment."
        elif quality == "void":
            judgment = "Lilly treats the void degree as reduced judgment or an emptier expression than appearances first suggest."
        else:
            continue
        paragraphs.append(
            f"{body} is one of the significators to which Lilly actually applies this column. {judgment} "
            "This is Lilly's seventeenth-century physical and horary vocabulary, preserved as his judgment rather than converted into a modern identity category. "
            f"[{item.get('id')}]"
        )

    pitted = [card for card in cards if card.get("pitted")]
    if pitted:
        applicable = [str(card.get("body")) for card in pitted if card.get("pitted_scope")]
        outside = [str(card.get("body")) for card in pitted if not card.get("pitted_scope")]
        if applicable:
            paragraphs.append(
                f"The pitted-degree rule applies to {', '.join(applicable)} in Lilly's stated significator set. His judgment is direct: "
                "the person or matter comes to a stand, does not know which way to turn, and requires outside help to be drawn out. "
                f"[{item.get('id')}]"
            )
        if outside:
            paragraphs.append(
                f"{', '.join(outside)} carries a pitted table flag, but Lilly's pitted passage names the Ascendant, Moon, and Ascendant ruler. "
                "The flag is therefore recorded without falsely extending the 'at a stand' judgment to an unrelated planet. "
                f"[{item.get('id')}]"
            )

    azimene = [card for card in cards if card.get("azimene")]
    if azimene:
        applicable = [str(card.get("body")) for card in azimene if card.get("azimene_scope")]
        outside = [str(card.get("body")) for card in azimene if not card.get("azimene_scope")]
        if applicable:
            paragraphs.append(
                f"{', '.join(applicable)} falls within Lilly's azimene significator set. Lilly associates these degrees with bodily defect, lameness, blindness, deafness, or enduring disease, "
                "but presents the table as corroboration when such a condition is already known; it is not a standalone forecast from the degree alone. "
                f"[{item.get('id')}]"
            )
        if outside:
            paragraphs.append(
                f"{', '.join(outside)} carries an azimene table flag outside Lilly's stated natal significator set. It remains part of the calculation, "
                "but applying its bodily language directly to you would exceed the printed rule. "
                f"[{item.get('id')}]"
            )

    fortune_candidates = [card for card in cards if card.get("fortune_scope")]
    increasing = [card for card in fortune_candidates if card.get("increasing_fortune")]
    if increasing:
        paragraphs.append(
            "The increasing-fortune rule is active through "
            + ", ".join(str(card.get("body")) for card in increasing)
            + ". Lilly treats this as an argument for substantial wealth, to be weighed with the full second-place ruler chain. "
            + f"[{item.get('id')}]"
        )
    else:
        paragraphs.append(
            "None of the calculated second-ruler, Jupiter, or Fortune entries falls in an increasing-fortune degree, so this table adds no special wealth testimony. "
            f"[{item.get('id')}]"
        )

    paragraphs.append(
        "The masculine/feminine column is retained in the audit data. Lilly uses it to answer the sex of an unknown person or unborn child when other testimonies are equal; "
        "it is not a general personality classification and has no independent natal judgment here. "
        f"[{item.get('id')}]"
    )
    return paragraphs


def _fixed_star_paragraphs(items: list[Mapping[str, Any]]) -> list[str]:
    if not items:
        return []
    paragraphs = ["## Fixed-Star Testimony That Survives Source Audit"]
    for item in items:
        details = item.get("details", {})
        if not isinstance(details, Mapping):
            continue
        if details.get("star") != "Caput Algol" or details.get("angle") != "Midheaven":
            continue
        paragraphs.append(
            f"{_evidence_sentence(item)} The orb is inside the report's conservative one-degree limit, so this is a real "
            "angular contact rather than a loose catalog coincidence. Because the Midheaven signifies visible action, rank, "
            "reputation, and command, Algol places the Perseus testimony directly in your public life."
        )
        paragraphs.append(
            "Ptolemy gives Perseus generally the nature of Jupiter and Saturn. Applied to the Midheaven, this joins the "
            "possibility of prominence, patronage, judgment, and authority with Saturnian weight, resistance, delay, and reversal. "
            "Your public work can attract unusually intense attention and can place you in contact with feared, contested, or "
            "high-stakes subjects. Eminence and exposure are joined: the same visibility that raises the work also makes failures of "
            f"judgment public. [{item.get('id')}]"
        )
        paragraphs.append(
            "The harshest Gorgon rule is not silently omitted. In Ptolemy's violent-death chapter, the specific judgment requires "
            "Mars near the Gorgon together with control of the anaretic places. Mars is not the body in this Algol contact, and the "
            "Midheaven contact alone does not meet those conditions. Therefore the chart contains strong public Algol testimony, "
            f"but this calculation does not establish Ptolemy's violent-death configuration. [{item.get('id')}]"
        )
    return paragraphs


def _lot_paragraphs(
    lots: list[Mapping[str, Any]], planets: list[Mapping[str, Any]]
) -> list[str]:
    if not lots:
        return []
    by_name = {
        str(item.get("details", {}).get("name")): item
        for item in lots
        if isinstance(item.get("details"), Mapping)
    }
    planet_by_name = {
        str(item.get("details", {}).get("name")): item
        for item in planets
        if isinstance(item.get("details"), Mapping)
    }
    paragraphs = [
        "## The Lots: Fortune, Intention, and Derived Topics",
        (
            "The lots are mathematical points derived from the Ascendant and planets. They do not act like additional "
            "planets. Their meaning is carried by place, ruler, and the ruler's natal condition."
        ),
    ]
    meanings = {
        "Fortune": "body, life-course, possessions, reputation, and privilege",
        "Spirit": "soul, temper, mindfulness, power, and deliberate action",
        "Eros": "appetite, voluntary desire, friendship, and mutual favor",
        "Necessity": "constraint, submission, struggle, war, enmity, hatred, condemnation, and restriction",
        "Courage": "boldness, treachery, might, and villainy",
        "Victory": "trust, expectation, contest, association, penalties, and rewards",
        "Nemesis": "subterranean and cold fates, impotence, exile, destruction, grief, and the quality of death",
    }
    operations = {
        "Fortune": "Circumstance, bodily life, possessions, and public allotment are delivered through this place.",
        "Spirit": "Choice, intention, command, and the work deliberately undertaken are delivered through this place.",
        "Eros": "Desire, friendship, appetite, and voluntarily chosen attachments are delivered through this place.",
        "Necessity": "Constraint, compulsion, enmity, and circumstances that reduce freedom are delivered through this place.",
        "Courage": "Boldness, force, betrayal, and the consequences of risk are delivered through this place.",
        "Victory": "Contest, trust, penalties, rewards, and the expectation of success are delivered through this place.",
        "Nemesis": "Grief, deprivation, exile, destruction, and the cold consequences of reversal are delivered through this place.",
    }
    for name in ("Fortune", "Spirit", "Eros", "Necessity", "Courage", "Victory", "Nemesis"):
        item = by_name.get(name)
        if not item:
            continue
        details = item["details"]
        ruler = str(details.get("ruler"))
        ruler_item = planet_by_name.get(ruler)
        house = int(details.get("house") or 0)
        place = HOUSE_CONTEXT.get(house, f"house {house}")
        status = str(details.get("status") or "not supplied")
        damaged = "maltreat" in status.lower() or "afflict" in status.lower()
        ruler_context = "The ruler's condition was not supplied in the admitted planetary evidence."
        ruler_citation = ""
        if ruler_item:
            pd = ruler_item["details"]
            ruler_place = HOUSE_CONTEXT.get(pd.get("house"), f"house {pd.get('house')}")
            ruler_context = (
                f"{ruler} rules from {ruler_place} in {_condition_phrase(pd)} condition. "
                "That condition decides whether the lot's field can be directed, must negotiate a price, or repeatedly suffers obstruction."
            )
            ruler_citation = f" [{ruler_item.get('id')}]"
        status_judgment = (
            "The recorded maltreatment makes reversal, loss, conflict, or a result controlled by another person more reliable than the clean promise."
            if damaged
            else "No maltreatment status is recorded for the lot itself; its ruler and configurations still control the outcome."
        )
        paragraphs.append(
            f"Paulus defines the Lot of {name} through {meanings[name]}. {_evidence_sentence(item)} In {place}, {operations[name].lower()} "
            f"{ruler_context} {status_judgment} [{item.get('id')}]{ruler_citation}"
        )
    return paragraphs


def _lunar_cycle_paragraphs(items: list[Mapping[str, Any]]) -> list[str]:
    if not items:
        return []
    item = items[0]
    details = item.get("details", {})
    return [
        "## Lunar Phase and Prenatal Syzygy",
        _evidence_sentence(item),
        (
            f"A {details.get('phase_direction')} Moon carries the cycle from culmination toward release and renewal, while "
            f"the prenatal {details.get('type')} supplies the lunation background inherited by the nativity. Because the "
            "Moon is also a planet with its own dignity, place, dispositor, and aspects, phase is a modifier rather than "
            f"a complete judgment. [{item.get('id')}]"
        ),
    ]


def _angle_paragraphs(
    items: list[Mapping[str, Any]], topical: list[Mapping[str, Any]]
) -> list[str]:
    if not items:
        return []
    item = items[0]
    details = item.get("details", {})
    by_house = {
        value.get("details", {}).get("house"): value
        for value in topical
        if isinstance(value.get("details"), Mapping)
    }
    first = by_house.get(1)
    tenth = by_house.get(10)
    mc_house = by_house.get(details.get("midheaven_house"))
    citations = [f"[{item.get('id')}]" ]
    for value in (first, tenth, mc_house):
        if value:
            citations.append(f"[{value.get('id')}]" )
    paragraphs = ["## The Angles and the Chart's Two Public Indicators", _evidence_sentence(item)]
    if first:
        fd = first["details"]
        paragraphs.append(
            f"The rising sign makes {fd.get('ruler')} the helm-ruler by domicile. Because that ruler is in house "
            f"{fd.get('ruler_house')} in {fd.get('ruler_sign')}, the native's manner of entering situations and directing "
            f"the chart is routed through {HOUSE_CONTEXT.get(fd.get('ruler_house'), 'that place')}. [{first.get('id')}]"
        )
    if tenth and mc_house:
        td = tenth["details"]
        md = mc_house["details"]
        paragraphs.append(
            f"Whole-sign house 10 is {td.get('sign')} and ruled by {td.get('ruler')}; it judges action, rank, and visible "
            f"undertaking. The Midheaven degree itself falls in house {details.get('midheaven_house')}, {md.get('sign')}, "
            f"ruled by {md.get('ruler')}. Public action is therefore read through both rulers: one governs the tenth place, "
            "while the other governs the exact culminating degree. Their conditions and houses show how vocation, public "
            f"visibility, and the supporting field are joined rather than collapsed into one indicator. {' '.join(citations)}"
        )
    return paragraphs


def _lunar_mansion_scope_paragraphs(items: list[Mapping[str, Any]]) -> list[str]:
    if not items:
        return []
    item = items[0]
    details = item.get("details", {})
    if not isinstance(details, Mapping):
        return []
    robustness = (
        "The assignment is stable under the inspected boundary variants."
        if details.get("assignment_robust_to_boundary_variants")
        else "The assignment is retained as a configured tropical calculation and is not treated as an independent natal proof."
    )
    return [
        "## The Moon's Mansion: What the Source Does and Does Not Say",
        (
            f"{_evidence_sentence(item)} {robustness}"
        ),
        (
            "The truth of the source is narrower than modern natal mansion writing. Picatrix tells the practitioner when to fashion images "
            "or undertake elections. It does not say that a person born under this mansion has the corresponding electional traits or that its listed operations "
            "will happen to the native. Therefore no honest natal prediction is extracted from the mansion label. The Moon is judged natally through its sign, "
            f"place, ruler, phase, and admitted configurations—not through invented mansion personality keywords. [{item.get('id')}]"
        ),
    ]


def _executive_synthesis(
    planets: list[Mapping[str, Any]],
    topical: list[Mapping[str, Any]],
    dispositors: list[Mapping[str, Any]],
    aspects: list[Mapping[str, Any]],
    timing: list[Mapping[str, Any]],
) -> list[str]:
    """State the chart's hierarchy before the reader enters the full proof."""
    planet_map = {
        str(item.get("details", {}).get("name")): item
        for item in planets
        if isinstance(item.get("details"), Mapping)
    }
    topic_map = {
        item.get("details", {}).get("house"): item
        for item in topical
        if isinstance(item.get("details"), Mapping)
    }
    paragraphs = ["## The Governing Contradiction"]
    first = topic_map.get(1)
    tenth = topic_map.get(10)
    if first and tenth:
        fd = first["details"]
        td = tenth["details"]
        ruler = str(fd.get("ruler"))
        ruler_item = planet_map.get(ruler)
        if ruler_item and td.get("ruler") == ruler:
            pd = ruler_item["details"]
            twelfth = topic_map.get(12)
            hidden_lights = (
                twelfth
                and {"Sun", "Moon"}.issubset(set(twelfth.get("details", {}).get("occupants", [])))
            )
            if ruler == "Mercury" and hidden_lights:
                paragraphs.append(
                    "**You are built to master systems and make hidden complexity intelligible, but the life does not reward innocence. "
                    "Authority is won through private labor, conflict, and repeated correction; alliances and attachments open doors, then reveal the burden attached to them.** "
                    f"[{first.get('id')}] [{tenth.get('id')}] [{twelfth.get('id')}] [{ruler_item.get('id')}]"
                )
            paragraphs.append(
                f"The first and tenth places share {ruler}, directly joining self-direction with action and reputation. "
                f"{ruler} is in {pd.get('sign')}, house {pd.get('house')}, with {pd.get('dignities')}; the same planet is "
                "therefore both the helm of the nativity and the principal ruler of visible undertaking. Your identity and "
                "career cannot be separated: advancement comes from using this planet's actual skills, and damage to its "
                "matters immediately affects both confidence and public standing. This is the clearest line of agency in the chart, "
                "although it still operates inside the larger dispositor and aspect "
                f"structure. [{first.get('id')}] [{tenth.get('id')}] [{ruler_item.get('id')}]"
            )
    if dispositors:
        item = dispositors[0]
        chains = item.get("details", {}).get("chains", [])
        endpoint_counts: dict[str, int] = defaultdict(int)
        for record in chains if isinstance(chains, list) else []:
            if isinstance(record, Mapping) and record.get("chain"):
                endpoint_counts[str(record["chain"][-1])] += 1
        if endpoint_counts:
            endpoint, count = max(endpoint_counts.items(), key=lambda pair: pair[1])
            endpoint_item = planet_map.get(endpoint)
            if endpoint_item:
                pd = endpoint_item["details"]
                paragraphs.append(
                    f"At the same time, {count} of the seven planetary chains terminate in {endpoint}. {endpoint} is in "
                    f"{pd.get('sign')}, house {pd.get('house')}, with {pd.get('dignities')}. The chart therefore has a "
                    "two-level architecture: the angular helm shows where you exercise deliberate control, while the final "
                    f"dispositor shows where life repeatedly carries the result. In concrete terms, most planetary matters "
                    f"eventually return to {HOUSE_CONTEXT.get(pd.get('house'), 'the final dispositor place')}; that topic is "
                    "therefore a governing fact of the biography, not a minor background note. "
                    f"[{item.get('id')}] [{endpoint_item.get('id')}]"
                )
    hard_names: set[str] = set()
    hard_ids: list[str] = []
    for item in aspects:
        details = item.get("details", {})
        if isinstance(details, Mapping) and details.get("type") in {"Conjunction", "Opposition", "Square"}:
            hard_names.update((str(details.get("planet_a")), str(details.get("planet_b"))))
            hard_ids.append(f"[{item.get('id')}]" )
    if len(hard_names) >= 3:
        ordered = sorted(hard_names, key=lambda name: PLANET_ORDER.get(name, 99))
        paragraphs.append(
            f"The main pressure system is not one isolated aspect. It is a connected configuration involving "
            f"{', '.join(ordered)}. This network joins the places occupied and ruled by those planets, so social alliance, "
            "creative generation, shared obligation, communication, and retreat repeatedly feed into one another. Your "
            "major difficulties therefore arrive in clusters: relationship or group conflict can affect creative work and "
            "resources; burdens and losses can alter alliances; and an apparent opportunity can carry obligations with it. "
            f"Dignity and reception supply resources, but they do not remove this pattern. {' '.join(hard_ids)}"
        )
    ruler_mentions: dict[str, int] = defaultdict(int)
    ruler_ids: dict[str, list[str]] = defaultdict(list)
    for item in timing:
        details = item.get("details", {})
        if not isinstance(details, Mapping):
            continue
        active = [str(value) for value in details.get("rulers", []) if value]
        active.extend(
            SIGN_RULERS[sign]
            for sign in details.get("levels", [])
            if sign in SIGN_RULERS
        )
        for name in active:
            ruler_mentions[name] += 1
            ruler_ids[name].append(f"[{item.get('id')}]" )
    if ruler_mentions:
        ordered = sorted(ruler_mentions, key=lambda name: (-ruler_mentions[name], PLANET_ORDER.get(name, 99)))
        leaders = ordered[:2]
        descriptions = [f"{name} ({ruler_mentions[name]} repetitions)" for name in leaders]
        citations = " ".join(value for name in leaders for value in ruler_ids[name])
        leader_judgments = []
        for name in leaders:
            planet = planet_map.get(name)
            if not planet:
                continue
            pd = planet["details"]
            leader_house = pd.get("house")
            leader_context = HOUSE_CONTEXT.get(leader_house, f"house {leader_house}")
            leader_judgments.append(
                f"{name} activates {leader_context} from {_condition_phrase(pd)} natal condition"
            )
        paragraphs.append(
            f"The current clocks concentrate most strongly on {' and '.join(descriptions)}. Their natal houses, rulerships, "
            "and aspects identify the subjects under emphasis. "
            + "; ".join(leader_judgments)
            + ". These subjects are not merely possible during the current chapter: they recur until the active rulers change. "
            + citations
        )
    return paragraphs


def _direct_judgment(
    plan: JudgmentPlan,
    planets: list[Mapping[str, Any]],
    topical: list[Mapping[str, Any]],
) -> list[str]:
    """Turn the ranked evidence hierarchy into a person-level opening judgment."""
    planet_map = {
        str(item.get("details", {}).get("name")): item
        for item in planets
        if isinstance(item.get("details"), Mapping)
    }
    house_map = {
        int(item["details"]["house"]): item
        for item in topical
        if isinstance(item.get("details"), Mapping)
        and isinstance(item["details"].get("house"), int)
    }
    paragraphs = ["## The Direct Judgment"]
    strongest = plan.strongest_planet
    if strongest:
        item = planet_map.get(strongest.name)
        details = item.get("details", {}) if item else {}
        pressure = plan.pressure_network
        if pressure and len(pressure.planets) >= 3:
            paragraphs.append(
                f"**This is not a chart of effortless support or uncomplicated luck. It is a chart in which the work of {strongest.name}—"
                f"{PLANET_HUMAN_TOPICS.get(strongest.name, PLANET_FUNCTIONS.get(strongest.name, strongest.name))}—"
                "must repeatedly impose order on conflicts that arrive in clusters. The native's power is real, but it is earned through "
                "correction, endurance, and the refusal to let other people's disorder define the final result.** "
                f"[{strongest.evidence_id}] "
                + " ".join(f"[{value}]" for value in pressure.evidence_ids)
            )
        else:
            paragraphs.append(
                f"**The chart's clearest source of agency is {strongest.name}. Its {strongest.condition} condition in "
                f"{HOUSE_CONTEXT.get(strongest.house, f'house {strongest.house}')} makes "
                f"{PLANET_HUMAN_TOPICS.get(strongest.name, PLANET_FUNCTIONS.get(strongest.name, strongest.name))} the principal means by which "
                "the native gains command and recovers after reversals.** "
                f"[{strongest.evidence_id}]"
            )
        capacity = PLANET_DIRECT_CAPACITIES.get(strongest.name, "")
        paragraphs.append(
            f"{strongest.name} ranks first because it is " + ", ".join(strongest.reasons) + ". "
            f"{capacity} This does not make the life easy; it identifies the faculty that remains available when other topics are damaged. "
            f"In practice, the native succeeds by performing {strongest.name}'s work more exactly than the surrounding circumstances perform theirs. "
            f"[{strongest.evidence_id}]"
        )

    if plan.helm_ruler:
        first = house_map.get(1)
        tenth = house_map.get(10)
        helm_item = planet_map.get(plan.helm_ruler)
        citations = " ".join(
            f"[{item.get('id')}]" for item in (first, tenth, helm_item) if item
        )
        if plan.public_ruler == plan.helm_ruler:
            paragraphs.append(
                f"The Ascendant and tenth place answer to the same ruler, {plan.helm_ruler}. Identity and vocation therefore cannot be separated: "
                "damage to the work is experienced personally, while mastery of the ruler's craft makes the native publicly consequential. "
                "This is authorship rather than borrowed status. The most credible advancement comes when the native owns the method, can show the work, "
                f"and is not wholly dependent on another person's favor. {citations}"
            )
        else:
            paragraphs.append(
                f"The helm belongs to {plan.helm_ruler}, while public action belongs to {plan.public_ruler or 'a different ruler'}. "
                "The person and the vocation therefore require an exchange between two planetary agendas rather than moving as one. "
                f"The condition and houses of those rulers show where cooperation or conflict enters the public course. {citations}"
            )

    if plan.final_dispositor and plan.final_dispositor_count:
        endpoint = planet_map.get(plan.final_dispositor)
        details = endpoint.get("details", {}) if endpoint else {}
        strongest_name = strongest.name if strongest else None
        if strongest_name and strongest_name != plan.final_dispositor:
            paragraphs.append(
                f"The chart has a second center of gravity. {plan.final_dispositor_count} of the seven domicile chains end in {plan.final_dispositor}, "
                f"placed in {HOUSE_CONTEXT.get(details.get('house'), 'its natal place')}. {strongest_name} describes deliberate control; "
                f"{plan.final_dispositor} describes where the consequences of many other planetary matters are finally delivered. The biography is therefore "
                "not explained by the strongest planet alone. What the native can command and where life repeatedly carries the result are different questions. "
                f"[{plan.final_dispositor_evidence_id}]" + (f" [{endpoint.get('id')}]" if endpoint else "")
            )
        else:
            paragraphs.append(
                f"{plan.final_dispositor} is both a principal source of agency and the end of {plan.final_dispositor_count} domicile chains. "
                "Its condition therefore has unusual chart-wide reach: when it can act, many topics gain a route to completion; when it is constrained, "
                f"those same topics bottleneck through its house and condition. [{plan.final_dispositor_evidence_id}]"
            )

    if plan.lights_share_house and plan.lights_house:
        sun = planet_map.get("Sun")
        moon = planet_map.get("Moon")
        if sun and moon:
            sun_condition = _condition_class(sun.get("details", {}))
            moon_condition = _condition_class(moon.get("details", {}))
            paragraphs.append(
                f"Both lights occupy {HOUSE_CONTEXT.get(plan.lights_house, f'house {plan.lights_house}')}, so purpose and changing circumstance are fused in one field. "
                f"The Sun is {sun_condition}; the Moon is {moon_condition}. The stronger light tends to recruit or dominate the weaker one, but the weaker light's "
                "deprivation still enters the result. This is why outward command and private need can coexist without cancelling one another. "
                f"[{sun.get('id')}] [{moon.get('id')}]"
            )

    pressure = plan.pressure_network
    if pressure and len(pressure.planets) >= 3:
        house_text = ", ".join(
            HOUSE_CONTEXT.get(house, f"house {house}") for house in pressure.houses
        )
        hub_text = _join_names(list(pressure.hubs))
        paragraphs.append(
            f"The principal pressure network joins {_join_names(list(pressure.planets))} through {pressure.edge_count} hard contacts and distributes its effects through {house_text}. "
            f"{hub_text} " + ("are the hubs" if len(pressure.hubs) > 1 else "is the hub") + " of that network. When one joined topic is activated, trouble does not remain local: "
            "attachment can become conflict, opportunity can become obligation, and another person's crisis can alter work, resources, or reputation. "
            "This is the chart's chief mechanism of consequential change. Dignity and reception may provide tools inside the configuration, but neither makes the configuration disappear. "
            + " ".join(f"[{value}]" for value in pressure.evidence_ids)
        )

    if plan.active_rulers:
        leaders = plan.active_rulers[:3]
        descriptions = []
        citations = []
        for leader in leaders:
            item = planet_map.get(leader.name)
            house = item.get("details", {}).get("house") if item else None
            descriptions.append(
                f"{leader.name} ({leader.repetitions} repetitions, natally in {HOUSE_CONTEXT.get(house, f'house {house}')})"
            )
            citations.extend(f"[{value}]" for value in leader.evidence_ids)
        paragraphs.append(
            "The present clocks concentrate on " + "; ".join(descriptions) + ". These are not free-floating themes. Their natal houses and conditions name the "
            "people, conflicts, opportunities, and burdens through which the period becomes concrete. Repetition raises the probability of manifestation; "
            "it does not improve a debilitated ruler or damage a strong one. " + " ".join(dict.fromkeys(citations))
        )

    if strongest:
        danger = "allowing the pressure network to consume what the strongest planet creates" if pressure else "failing to use the strongest planet's actual craft"
        achievement = PLANET_HUMAN_TOPICS.get(strongest.name, PLANET_FUNCTIONS.get(strongest.name, strongest.name))
        paragraphs.extend([
            "### The Blunt Conclusion",
            f"The native's strongest capacity is {achievement}. The chief recurrent danger is {danger}. The most credible achievement is not effortless good fortune, "
            f"but a durable body of work, authority, or responsibility built through {strongest.name}'s actual skills and strong enough to survive the chart's repeated corrections. "
            f"[{strongest.evidence_id}]" + (" " + " ".join(f"[{value}]" for value in pressure.evidence_ids) if pressure else ""),
        ])
    return paragraphs


def _governing_promises(
    planets: list[Mapping[str, Any]],
    topical: list[Mapping[str, Any]],
    dispositors: list[Mapping[str, Any]],
    aspects: list[Mapping[str, Any]],
) -> list[str]:
    """Rank the chart's recurrent promises before presenting the technical proof."""
    planet_map = {
        str(item.get("details", {}).get("name")): item
        for item in planets
        if isinstance(item.get("details"), Mapping)
    }
    house_map = {
        int(item["details"]["house"]): item
        for item in topical
        if isinstance(item.get("details"), Mapping)
        and isinstance(item["details"].get("house"), int)
    }
    paragraphs = [
        "## The Five Governing Promises",
        "These are ranked by repetition across rulership, placement, condition, and configuration. They are the backbone of the biography; later details explain how and when they manifest.",
    ]
    first = house_map.get(1)
    tenth = house_map.get(10)
    if first and tenth:
        ruler = str(first["details"].get("ruler"))
        ruler_item = planet_map.get(ruler)
        if ruler_item:
            pd = ruler_item["details"]
            shared = tenth["details"].get("ruler") == ruler
            paragraphs.append(
                "1. **Skill is the principal route to command.** "
                + (f"The first and tenth places are both ruled by {ruler}, so identity and vocation answer to the same planet. " if shared else f"The helm-ruler is {ruler}. ")
                + f"From {pd.get('sign')} in house {pd.get('house')}, it makes {PLANET_HUMAN_TOPICS.get(ruler, PLANET_FUNCTIONS.get(ruler, ruler))} the means by which you gain control, recover after reversals, and become publicly consequential. "
                f"[{first.get('id')}] [{tenth.get('id')}] [{ruler_item.get('id')}]"
            )
    if dispositors:
        item = dispositors[0]
        chains = item.get("details", {}).get("chains", [])
        endpoints = [str(row.get("chain", [""])[-1]) for row in chains if isinstance(row, Mapping) and row.get("chain")]
        if endpoints:
            endpoint = max(set(endpoints), key=endpoints.count)
            endpoint_item = planet_map.get(endpoint)
            if endpoint_item:
                pd = endpoint_item["details"]
                paragraphs.append(
                    f"2. **Life repeatedly delivers its results through {HOUSE_CONTEXT.get(pd.get('house'), 'one governing place')}.** "
                    f"{endpoints.count(endpoint)} planetary chains terminate in {endpoint}. Whatever begins elsewhere tends to become a matter of "
                    f"{PLANET_HUMAN_TOPICS.get(endpoint, PLANET_FUNCTIONS.get(endpoint, endpoint))}; its {_condition_class(pd)} condition decides whether the result arrives as mastery, compromise, or loss. "
                    f"[{item.get('id')}] [{endpoint_item.get('id')}]"
                )
    twelfth = house_map.get(12)
    if twelfth:
        occupants = [str(value) for value in twelfth["details"].get("occupants", [])]
        citations = " ".join(f"[{planet_map[name].get('id')}]" for name in occupants if name in planet_map)
        paragraphs.append(
            "3. **The hidden life is not secondary.** "
            + (f"With {', '.join(occupants)} in the twelfth place, " if occupants else "Because the twelfth-place ruler is prominent, ")
            + "solitude, concealed work, grief, institutions, private enemies, and periods of reduced visibility materially redirect the life. The same testimony can produce formidable work away from recognition, but it also makes isolation and self-undoing real hazards rather than metaphors. "
            f"[{twelfth.get('id')}] {citations}"
        )
    venus = planet_map.get("Venus")
    relationship_ids: list[str] = []
    hard_partners: list[str] = []
    for item in aspects:
        details = item.get("details", {})
        pair = {str(details.get("planet_a")), str(details.get("planet_b"))}
        if "Venus" in pair and details.get("type") in {"Conjunction", "Square", "Opposition"}:
            hard_partners.extend(pair - {"Venus"})
            relationship_ids.append(f"[{item.get('id')}]")
    if venus:
        vd = venus["details"]
        paragraphs.append(
            "4. **Attachment brings opportunity and trouble together.** "
            f"Venus acts from {HOUSE_CONTEXT.get(vd.get('house'), 'its natal place')} in {_condition_phrase(vd)} condition"
            + (f" and is hard-configured with {', '.join(dict.fromkeys(hard_partners))}" if hard_partners else "")
            + ". Love, friendship, patronage, agreement, and creative pleasure are therefore consequential but not innocent: bonds open doors while also carrying rivalry, delay, unequal duty, disappointment, or changed terms. "
            f"[{venus.get('id')}] {' '.join(relationship_ids)}"
        )
    fifth = house_map.get(5)
    eighth = house_map.get(8)
    if fifth and eighth:
        paragraphs.append(
            "5. **Creation and increase are repeatedly checked by obligation.** "
            f"The fifth place of children, pleasure, and creative production is governed by {fifth['details'].get('ruler')} from {HOUSE_CONTEXT.get(fifth['details'].get('ruler_house'), 'its ruler place')}; "
            f"the eighth place of fear, endings, and shared burdens is governed by {eighth['details'].get('ruler')} from {HOUSE_CONTEXT.get(eighth['details'].get('ruler_house'), 'its ruler place')}. "
            "Promising ventures can grow, but they rarely remain free of cost, delay, responsibility, or another person's claim. The chart favors durable work produced through constraint over effortless luck. "
            f"[{fifth.get('id')}] [{eighth.get('id')}]"
        )
    return paragraphs


def _integrated_life_judgments(
    topical: list[Mapping[str, Any]],
    planets: list[Mapping[str, Any]],
    aspects: list[Mapping[str, Any]],
) -> list[str]:
    """Combine rulers and places into the life judgments a customer actually wants."""
    house_map = {
        int(item["details"]["house"]): item
        for item in topical
        if isinstance(item.get("details"), Mapping) and isinstance(item["details"].get("house"), int)
    }
    planet_map = {
        str(item.get("details", {}).get("name")): item
        for item in planets
        if isinstance(item.get("details"), Mapping)
    }

    def house_citations(*houses: int) -> str:
        return " ".join(f"[{house_map[h].get('id')}]" for h in houses if h in house_map)

    def planet_citations(*names: str) -> str:
        return " ".join(f"[{planet_map[n].get('id')}]" for n in names if n in planet_map)

    def hard_pair(a: str, b: str) -> tuple[str, str]:
        for item in aspects:
            details = item.get("details", {})
            if {str(details.get("planet_a")), str(details.get("planet_b"))} == {a, b} and details.get("type") in {"Conjunction", "Square", "Opposition"}:
                return str(details.get("type")).lower(), f"[{item.get('id')}]"
        return "", ""

    paragraphs = ["## The Life as a Whole"]
    first = house_map.get(1)
    sun = planet_map.get("Sun")
    moon = planet_map.get("Moon")
    if first:
        fd = first["details"]
        helm = str(fd.get("ruler"))
        helm_item = planet_map.get(helm)
        hd = helm_item.get("details", {}) if helm_item else {}
        mind_profiles = {
            "Sun": (
                "direct the course, preserve authority, and act from a coherent purpose",
                "command becomes pride, correction becomes domination, and dependence on recognition distorts judgment",
            ),
            "Moon": (
                "read changing conditions, remember what people need, and adapt before circumstances harden",
                "responsiveness becomes inconstancy, belonging overrides judgment, and other people's changes govern the course",
            ),
            "Mercury": (
                "understand the mechanism, name distinctions, test claims, and retain intellectual control",
                "analysis becomes argument, correction becomes severity, and the mind keeps working after the human situation is no longer solvable",
            ),
            "Venus": (
                "create agreement, judge proportion, attract support, and recognize what people will value",
                "the desire to preserve attachment compromises judgment or makes another person's approval too expensive",
            ),
            "Mars": (
                "act decisively, confront opposition, separate what cannot be repaired, and compete under pressure",
                "urgency becomes quarrel, force outruns judgment, and every obstacle begins to look like an enemy",
            ),
            "Jupiter": (
                "enlarge the field through judgment, teaching, counsel, faith, and the recognition of larger patterns",
                "confidence becomes overreach, promises exceed capacity, and moral certainty conceals poor terms",
            ),
            "Saturn": (
                "endure, define limits, preserve records, carry responsibility, and build structures that survive time",
                "prudence becomes fear, endurance becomes confinement, and scarcity governs decisions after the immediate danger has passed",
            ),
        }
        faculty, defect = mind_profiles.get(
            helm,
            ("act through the helm-ruler's natural faculty", "the same faculty becomes excessive or rigid"),
        )
        helm_place = HOUSE_CONTEXT.get(hd.get("house"), f"house {hd.get('house')}")
        paragraphs.extend([
            "### Mind, Character, and Agency",
            f"The helm is {helm}. It stands in {hd.get('sign')} in {helm_place} with {_condition_phrase(hd)} condition. "
            f"This describes a person who must {faculty}. The same faculty has a characteristic defect: {defect}. "
            f"Because the helm is {_condition_class(hd)}, its operation is one of the native's "
            + ("most dependable sources of agency." if _condition_class(hd) == "strong" else "recurrent fields of correction rather than an effortless possession.")
            + f" {house_citations(1)} {planet_citations(helm)}",
        ])
    if sun and moon:
        sd, md = sun["details"], moon["details"]
        if sd.get("house") == md.get("house"):
            paragraphs.append(
                f"The Sun and Moon are both rooted in {HOUSE_CONTEXT.get(sd.get('house'), 'the same place')}. Purpose and changing circumstance are therefore fused: "
                "private conditions affect direction more strongly than outsiders usually see, and the stronger light tends to recruit the weaker one into its agenda. "
                f"[{sun.get('id')}] [{moon.get('id')}]"
            )
        else:
            sun_place = HOUSE_CONTEXT.get(sd.get("house"), f"house {sd.get('house')}")
            moon_place = HOUSE_CONTEXT.get(md.get("house"), f"house {md.get('house')}")
            paragraphs.append(
                f"The Sun acts from {sun_place}, while the Moon acts from {moon_place}. Purpose and changing circumstance therefore pull through different topics, "
                "and their aspect relationship decides whether those topics cooperate, alternate, or contend. "
                f"[{sun.get('id')}] [{moon.get('id')}]"
            )
    fourth = house_map.get(4)
    if fourth:
        fd = fourth["details"]
        band = str(fd.get("condition_band") or "mixed")
        foundation_verdict = (
            "The private foundation can support later action, although the ruler's house still determines what family and home demand."
            if band in {"well-supported", "supported"}
            else "The private foundation requires correction, return, or sustained effort before it becomes dependable."
        )
        paragraphs.extend([
            "### Parents, Home, and Foundations",
            f"The fourth place is {fd.get('sign')} and answers to {fd.get('ruler')} in {HOUSE_CONTEXT.get(fd.get('ruler_house'), 'another place')}. "
            f"{foundation_verdict} {_topic_native_prediction(fd, planet_map, include_route=False)} The parental story must be divided between the two lights; "
            f"neither one's strength nor the other's affliction cancels the separate testimony. {house_citations(4)} {planet_citations('Sun', 'Moon')}",
        ])
    fifth, seventh = house_map.get(5), house_map.get(7)
    venus = planet_map.get("Venus")
    if fifth and seventh and venus:
        vd = venus["details"]
        vm, vm_id = hard_pair("Venus", "Mars")
        vs, vs_id = hard_pair("Venus", "Saturn")
        aspect_clause = ""
        if vm or vs:
            pieces = [f"Venus-{name} {kind}" for name, kind in (("Mars", vm), ("Saturn", vs)) if kind]
            verb = "makes" if len(pieces) == 1 else "make"
            aspect_clause = " Its " + " and ".join(pieces) + f" {verb} attraction inseparable from contest, frustration, distance, duty, or rejection."
        seventh_band = str(seventh["details"].get("condition_band") or "mixed")
        partnership_verdict = {
            "well-supported": "Binding partnership has a capable ruler and can produce a concrete, durable result.",
            "supported": "Partnership is broadly supported, though the ruler's house still supplies its price and obligations.",
            "mixed": "Partnership brings a real opening together with compromise, changed terms, or divided obligations.",
            "impaired": "Partnership requires revision and is vulnerable to delay, reversal, or dependence on another person's circumstances.",
            "severely impaired": "Partnership and open contest are among the chart's difficult topics, with obstruction, absence, conflict, or prolonged disputes more reliable than an easy result.",
        }.get(seventh_band, "Partnership carries mixed testimony.")
        venus_route = HOUSE_CONTEXT.get(vd.get("house"), f"house {vd.get('house')}")
        paragraphs.extend([
            "### Love, Marriage, Sexuality, and Children",
            f"The seventh ruler is {seventh['details'].get('ruler')} in {HOUSE_CONTEXT.get(seventh['details'].get('ruler_house'), 'its natal place')}. {partnership_verdict} "
            f"Venus is in {vd.get('sign')} in {venus_route} with {_condition_phrase(vd)} condition, so love, agreement, pleasure, and attachment enter through that place.{aspect_clause} "
            f"The ruler's condition describes whether a bond can carry its promise; Venus and its hard contacts describe how desire complicates the result. "
            f"{house_citations(7)} {planet_citations('Venus')} {vm_id} {vs_id}",
            f"The fifth place confirms that love, sex, pleasure, children, and creative work are joined to the same larger question of increase. {_topic_native_prediction(fifth['details'], planet_map, include_route=False)} This does not deny children or creation; it says they arrive with more responsibility, reversal, expense, or fear than the initial desire admits. Durable creation is possible precisely because the chart can continue after the romance of beginning has failed. {house_citations(5)}",
        ])
    second, eighth, eleventh = house_map.get(2), house_map.get(8), house_map.get(11)
    if second and eighth and eleventh:
        paragraphs.extend([
            "### Money, Allies, and Shared Obligations",
            f"Livelihood cannot be read as a private bank detached from relationships. The second ruler, {second['details'].get('ruler')}, acts from {HOUSE_CONTEXT.get(second['details'].get('ruler_house'), 'its natal place')}; the eleventh ruler, {eleventh['details'].get('ruler')}, governs friends, patrons, audiences, and gains; the eighth ruler, {eighth['details'].get('ruler')}, governs resources and burdens shared with others. This binds income to alliance. Friends, customers, collaborators, or a partner can create the opening, and the same network can create leakage, rivalry, unpaid labor, delayed payment, or obligations that survive the opportunity. The correct descriptive judgment is uneven accumulation: skill can earn, but attachment and shared burdens decide what is retained. {house_citations(2, 8, 11)}",
        ])
    tenth, ninth, sixth = house_map.get(10), house_map.get(9), house_map.get(6)
    if tenth:
        td = tenth["details"]
        ruler = str(td.get("ruler"))
        rd = planet_map.get(ruler, {}).get("details", {})
        vocation = {
            "Mercury": "analysis, writing, software or systems work, research, teaching, commerce, problem-finding, interpretation, and any craft where exact language or classification matters",
            "Venus": "design, art, mediation, social strategy, hospitality, beauty, alliance-building, and work whose value depends on taste or agreement",
            "Mars": "competition, engineering, operations, enforcement, crisis work, and fields requiring decisive separation",
            "Jupiter": "teaching, counsel, religion, law as a field, publishing, patronage, and institutional judgment",
            "Saturn": "administration, construction, land, history, records, regulation, long projects, and difficult structures others abandon",
            "Sun": "leadership, command, public office, performance, and work organized around personal authority",
            "Moon": "public service, logistics, travel, hospitality, caregiving fields, commodities, and work responsive to changing demand",
        }.get(ruler, "the natural work of its ruler")
        paragraphs.extend([
            "### Career, Reputation, and the Work Worth Doing",
            f"The vocational judgment is not 'anything is possible.' The tenth place is {td.get('sign')}, ruled by {ruler} from {HOUSE_CONTEXT.get(td.get('ruler_house'), 'its natal place')}. The first priority is {vocation}. Because the ruler is {_condition_class(rd)}, advancement is most credible when you own the method and can show the work, not when status depends entirely on another person's favor. The ninth place adds study, doctrine, divination, teaching, or distant reach; the sixth describes the labor price. The strongest career is therefore expert work that converts hidden complexity into an intelligible system and eventually carries your name, even if much of its production happens privately. {house_citations(10, 9, 6)} {planet_citations(ruler)}",
        ])
    return paragraphs


def _life_chapter_paragraphs(
    items: list[Mapping[str, Any]], planets: list[Mapping[str, Any]]
) -> list[str]:
    if not items:
        return []
    item = items[0]
    details = item.get("details", {})
    planet_by_name = {
        str(value.get("details", {}).get("name")): value
        for value in planets
        if isinstance(value.get("details"), Mapping)
    }
    paragraphs = ["## Sect-Light Fortune and the Course of Life", _evidence_sentence(item)]
    first_name = str(details.get("first"))
    second_name = str(details.get("second"))
    participant_name = str(details.get("participant"))
    first = planet_by_name.get(first_name)
    second = planet_by_name.get(second_name)
    participant = planet_by_name.get(participant_name)
    if not first or not second:
        return paragraphs

    good_places = {1, 4, 5, 7, 9, 10, 11}
    worst_places = {6, 12}
    first_details = first["details"]
    second_details = second["details"]
    first_house = int(first_details.get("house") or 0)
    second_house = int(second_details.get("house") or 0)
    first_good = first_house in good_places
    second_good = second_house in good_places

    if first_good and second_good:
        verdict = (
            "Dorotheus gives the strongest temporal verdict here: excellence, elevation, and material support can continue "
            "from the beginning through the later course of life."
        )
    elif first_good and not second_good:
        verdict = (
            "Dorotheus says this pattern begins better and deteriorates later. Early advantages are real, but later "
            "maintenance becomes harder and loss, frustration, or reduced livelihood must be expected."
        )
    elif not first_good and second_good:
        verdict = (
            "Dorotheus says this pattern does not promise an easy beginning. It can produce a middling rise later, but the "
            "improvement does not remain secure and eventually abates."
        )
    else:
        verdict = (
            "Dorotheus treats both principal rulers outside the good places as a severe testimony for fortune and livelihood: "
            "scarcity, dependence, or repeated reversals persist unless stronger contrary testimony intervenes."
        )

    first_place = "one of Dorotheus's worst places" if first_house in worst_places else (
        "a good place" if first_good else "a place not counted among his good places"
    )
    second_place = "one of Dorotheus's worst places" if second_house in worst_places else (
        "a good place" if second_good else "a place not counted among his good places"
    )
    first_house_context = HOUSE_CONTEXT.get(first_house, "the first ruler's place")
    second_house_context = HOUSE_CONTEXT.get(second_house, "the second ruler's place")
    paragraphs.append(
        f"The first ruler is {first_name} in house {first_house}, {first_place}; the second is {second_name} in house "
        f"{second_house}, {second_place}. {verdict} For you, this ties the beginning to "
        f"{first_house_context} and the later outcome to "
        f"{second_house_context}. "
        f"[{item.get('id')}] [{first.get('id')}] [{second.get('id')}]"
    )
    if participant:
        pd = participant["details"]
        house = int(pd.get("house") or 0)
        paragraphs.append(
            f"{participant_name}, the participating ruler, is in house {house} with {pd.get('dignities')}. It modifies the "
            "whole fortune judgment through "
            f"{HOUSE_CONTEXT.get(house, 'its natal place')}; it does not govern a fixed late-life third. "
            f"[{item.get('id')}] [{participant.get('id')}]"
        )
    for phase_item in items[1:]:
        if phase_item.get("source_rule_id") != "ibn_ezra_triplicity_life_thirds":
            continue
        phase_details = phase_item.get("details", {})
        if not isinstance(phase_details, Mapping):
            continue
        paragraphs.append(_evidence_sentence(phase_item))
        phase_rows = []
        for label, key in (("first", "first"), ("middle", "middle"), ("last", "last")):
            ruler_name = str(phase_details.get(key))
            ruler_item = planet_by_name.get(ruler_name)
            if not ruler_item:
                continue
            pd = ruler_item["details"]
            house = int(pd.get("house") or 0)
            condition_phrase = _condition_phrase(pd)
            phase_rows.append(
                f"The {label} relative phase belongs to {ruler_name} in house {house}, {condition_phrase} ruler, so it is organized through "
                f"{HOUSE_CONTEXT.get(house, 'that natal place')} and brings {PLANET_PERIOD_EVENTS.get(ruler_name, ruler_name + ' matters')}. "
                f"[{phase_item.get('id')}] [{ruler_item.get('id')}]"
            )
        paragraphs.extend(phase_rows)
        paragraphs.append(
            "These are relative phases only. Their exact boundaries are not invented here; the separate Hyleg and Alcocoden chapter publishes "
            "the numerical longevity branches that the engine actually calculated. The later Ibn Ezra phase scheme is shown beside, not substituted for, "
            f"Dorotheus's different first/second fortune rule. [{phase_item.get('id')}]"
        )
    return paragraphs


def _longevity_paragraphs(items: list[Mapping[str, Any]]) -> list[str]:
    """Publish every supplied longevity branch, including contradictory outcomes."""
    if len(items) < 2:
        return []
    source_item = items[0]
    branch_item = items[1]
    source_details = source_item.get("details", {})
    branch_details = branch_item.get("details", {})
    if not isinstance(source_details, Mapping) or not isinstance(branch_details, Mapping):
        return []

    hyleg = source_details.get("hyleg", {})
    strict_method = source_details.get("strict_method", {})
    points_method = source_details.get("points_method", {})
    strict_capacity = branch_details.get("strict_capacity", {})
    points_capacity = branch_details.get("points_capacity", {})
    anareta = branch_details.get("anareta", {})
    windows = branch_details.get("anaretic_windows", {})
    if not all(isinstance(value, Mapping) for value in (hyleg, strict_method, points_method, strict_capacity, points_capacity, anareta, windows)):
        return []

    def method_name(value: object) -> str:
        text = str(value or "unknown")
        return text.rsplit(".", 1)[-1].title()

    def format_years(value: object) -> str:
        if isinstance(value, (int, float)):
            return f"{float(value):.2f}".rstrip("0").rstrip(".")
        return str(value)

    paragraphs = [
        "## Vitality: Hyleg, Alcocoden, and the Allotment of Years",
        (
            "The old authors selected a giver of life (Hyleg) and a giver of years (Alcocoden) to judge the "
            "constitution: how robust the vital force is, where it is supported, and where it is undermined. "
            "They also produced a number of years. This report publishes that arithmetic in full, but it does "
            "**not** present it as a date of death, and you should not read it as one. The reason is empirical "
            "rather than squeamish: applied mechanically to real nativities, the numeric step is frequently "
            "falsified by the native's own survival, and Lilly himself writes that the Hyleg, Alcocoden, and "
            "Anareta cannot always be determined with certainty. What survives that scrutiny is the "
            "*constitutional* testimony — which planet carries the vital force, in what condition, and what "
            "presses on it. That is what is judged below. "
            f"[{source_item.get('id')}] [{branch_item.get('id')}]"
        ),
    ]
    paragraphs.append(
        f"The configured Hyleg is {hyleg.get('name')} at {float(hyleg.get('longitude', 0.0)):.2f}°. This is the giver of life used by both "
        "branches below; changing the Hyleg would change the entire calculation and must not be done silently in prose. "
        f"[{source_item.get('id')}]"
    )

    strict_found = bool(strict_capacity.get("alcocoden"))
    strict_lord = method_name(strict_capacity.get("alcocoden") or strict_method.get("name"))
    strict_total = strict_capacity.get("total_years")
    strict_total_text = format_years(strict_total)
    strict_type = str(strict_capacity.get("base_years_type") or "greater").lower()
    strict_breakdown = [
        str(value).rstrip(".") for value in strict_capacity.get("breakdown", [])
    ]
    strict_invalid = bool(strict_capacity.get("invalid_under_sanity"))
    strict_aspect_details = strict_method.get("details", {})
    strict_aspect = (
        str(strict_aspect_details.get("aspect") or "configured aspect rule")
        if isinstance(strict_aspect_details, Mapping)
        else "configured aspect rule"
    )
    if not strict_found:
        # The method legitimately produced no giver of years for this chart.
        # State the absence honestly instead of naming a placeholder planet.
        paragraphs.extend([
            "### Branch One — The Strict Bound-Lord Method Finds No Giver of Years",
            (
                "The strict-bound branch requires the bound lord of the Hyleg degree to aspect the Hyleg. In this "
                "nativity no planet satisfies that condition, so the method yields no Alcocoden and therefore no "
                "years figure. The old authors met this case as well: an inapplicable method is reported as "
                "inapplicable, not forced to produce a number. "
                f"[{source_item.get('id')}] [{branch_item.get('id')}]"
            ),
        ])
    else:
        paragraphs.extend([
            f"### Branch One — {strict_lord} Gives {strict_total_text} Years",
            (
                f"The strict-bound branch makes {strict_lord} Alcocoden. {strict_lord} is the bound lord used at the Hyleg and is admitted "
                f"through {strict_aspect.lower()}. It assigns the {strict_type} planetary-years value: **{strict_total_text} years**. "
                + ("Its ledger reads: " + "; ".join(strict_breakdown) + ". " if strict_breakdown else "")
                + ("The engine marks this result invalid under its attained-age sanity check. " if strict_invalid else f"The computed judgment of this branch is therefore a lifetime of {strict_total_text} years. ")
                + f"[{source_item.get('id')}] [{branch_item.get('id')}]"
            ),
        ])

    points_found = bool(points_capacity.get("alcocoden"))
    points_lord = method_name(points_capacity.get("alcocoden") or points_method.get("name"))
    point_breakdown = [
        str(value).rstrip(".") for value in points_capacity.get("breakdown", [])
    ]
    arithmetic_rows = [value for value in point_breakdown if value.startswith(("Base:", "Added", "Subtracted"))]
    points_total = points_capacity.get("total_years")
    points_total_text = format_years(points_total)
    failed_total_text = (
        f"The resulting figure is {float(points_total):.2f} years, below the native's already attained age, "
        if isinstance(points_total, (int, float))
        else "That arithmetic falls below the native's already attained age, "
    )
    points_invalid = bool(points_capacity.get("invalid_under_sanity"))
    points_aspect_details = points_method.get("details", {})
    points_aspect = (
        str(points_aspect_details.get("aspect") or "configured aspect rule")
        if isinstance(points_aspect_details, Mapping)
        else "configured aspect rule"
    )
    if not points_found:
        paragraphs.extend([
            "### Branch Two — The Dignity-Points Method Finds No Giver of Years",
            (
                "The dignity-points and degree-aspect branch likewise finds no planet that both holds sufficient "
                "essential dignity at the Hyleg and casts a qualifying aspect to it, so it yields no Alcocoden and "
                "no years figure. The absence is reported as such. "
                f"[{source_item.get('id')}] [{branch_item.get('id')}]"
            ),
        ])
    else:
        points_heading = (
            f"### Branch Two — {points_lord} Produces a Failed Result"
            if points_invalid
            else f"### Branch Two — {points_lord} Gives {points_total_text} Years"
        )
        paragraphs.extend([
            points_heading,
            (
                f"The dignity-points and degree-aspect branch instead selects {points_lord}, which actually casts the recorded "
                f"{points_aspect.lower()} to the Hyleg. "
                f"It begins with {points_capacity.get('base_years')} {str(points_capacity.get('base_years_type') or 'mean').lower()} years. "
                + ("Its ledger reads: " + "; ".join(arithmetic_rows) + ". " if arithmetic_rows else "")
                + (failed_total_text + "so the engine marks the branch invalid while preserving the result. " if points_invalid else f"The resulting figure is {points_total_text} years and remains a competing numerical judgment. ")
                + ("The contradiction is not concealed: either this branch is misapplied, the method requires rectification, or the technique fails on this nativity. " if points_invalid else "Both viable branches must remain visible because the method has not supplied a reason to suppress either one. ")
                + f"[{source_item.get('id')}] [{branch_item.get('id')}]"
            ),
        ])

    paragraphs.append(
        "### The Judgment Between the Branches"
    )
    viable = [
        (strict_lord, strict_total, strict_aspect, strict_invalid) if strict_found else None,
        (points_lord, points_total, points_aspect, points_invalid) if points_found else None,
    ]
    viable = [row for row in viable if row is not None and not row[3] and row[1] is not None]
    failed = [
        (strict_lord, strict_total) if strict_found and strict_invalid else None,
        (points_lord, points_total) if points_found and points_invalid else None,
    ]
    failed = [row for row in failed if row is not None]
    missing_methods = []
    if not strict_found:
        missing_methods.append("the strict bound-lord method")
    if not points_found:
        missing_methods.append("the dignity-points method")
    viable_text = "; ".join(f"{name} gives {format_years(years)} years" for name, years, _aspect, _invalid in viable)
    failed_text = "; ".join(f"{name}'s {format_years(years)}-year result fails the sanity check" for name, years in failed)
    missing_text = " and ".join(missing_methods)
    whole_sign_weakness = any(
        "whole sign" in aspect.lower() or "whole_sign" in aspect.lower()
        for _name, _years, aspect, _invalid in viable
    )
    if viable_text:
        opening = f"The internally viable result or results are: **{viable_text}.** "
    elif failed:
        opening = "Neither numerical branch survives the configured sanity check. "
    else:
        opening = "No numerical branch applies to this nativity. "
    paragraphs.append(
        opening
        + (f"The failed result or results remain part of the record: {failed_text}. " if failed_text else "")
        + (f"In this chart {missing_text} {'finds' if len(missing_methods) == 1 else 'find'} no qualifying Alcocoden at all, and that absence is part of the honest record. " if missing_text else "")
        + ("A surviving branch depends on whole-sign co-presence rather than a close degree aspect, which is a disclosed methodological weakness rather than a detail to conceal. " if whole_sign_weakness else "")
        + "Lilly himself says that the Hyleg, Anareta, and Alcocoden cannot always be selected with certainty. The truthful judgment therefore states the emitted years, the failed rivals, and the aspect mode without turning a branch into a fixed date of death. "
        f"[{source_item.get('id')}] [{branch_item.get('id')}]"
    )

    if anareta.get("name"):
        paragraphs.append(
            f"The static Anareta calculation selects {anareta.get('name')}: {anareta.get('reason')}. [{branch_item.get('id')}]"
        )
    else:
        paragraphs.append(
            f"The static Anareta test finds no qualifying body: {str(anareta.get('reason') or 'no tight malefic contact to the Hyleg is present').rstrip('.')}. [{branch_item.get('id')}]"
        )
    candidates = [value for value in windows.get("candidates", []) if isinstance(value, Mapping)]
    if candidates:
        candidate = candidates[0]
        paragraphs.append(
            f"The configured directional screen nevertheless identifies {candidate.get('promittor')} in {str(candidate.get('aspect')).lower()} to the Hyleg at age "
            f"{float(candidate.get('years', 0.0)):.2f}, approximately {candidate.get('date_offset')}. This is the model's anaretic candidate window. "
            f"It is not identical to the numerical allotment{'s' if len(viable) != 1 else ''} above and the direction model is the project's disclosed, partial zodiacal oblique-ascension implementation rather than a complete Placidus semi-arc direction. "
            f"[{branch_item.get('id')}]"
        )
    return paragraphs


def _annual_context_paragraphs(items: list[Mapping[str, Any]]) -> list[str]:
    paragraphs: list[str] = []
    for item in items:
        details = item.get("details", {})
        paragraphs.extend(["## The Solar-Return Layer", _evidence_sentence(item)])
        ascendant = details.get("return_ascendant", {})
        ruler = details.get("return_ascendant_ruler", {})
        if isinstance(ascendant, Mapping) and isinstance(ruler, Mapping):
            ruler_house = int(ruler.get("return_house") or 0)
            ruler_score = int(ruler.get("essential_score") or 0)
            if ruler_house in {6, 8, 12} and ruler_score <= 0:
                ruler_verdict = (
                    "This is a difficult annual governor: delays, obscurity, dependency, fear, loss, or work done under constraint "
                    "arrive before its useful results."
                )
            elif ruler_house in {1, 4, 5, 7, 9, 10, 11} and ruler_score > 0:
                ruler_verdict = (
                    "This is a capable annual governor, able to turn the year's openings into visible action and durable results."
                )
            else:
                ruler_verdict = (
                    "Its mixed condition gives an opening together with a cost, delay, dependency, or compromise."
                )
            paragraphs.append(
                f"At {details.get('return_datetime_utc')}, {ascendant.get('sign')} rises in the annual revolution, so {ruler.get('name')} is "
                f"Ibn Ezra's return-Ascendant witness. That ruler is in return house {ruler_house} in {ruler.get('return_sign')}, with an "
                f"essential score of {ruler_score} and retrograde={ruler.get('retrograde')}. {ruler_verdict} "
                f"[{item.get('id')}]"
            )
        triplicity = details.get("sect_light_triplicity_comparison", {})
        if isinstance(triplicity, Mapping) and triplicity.get("ruler"):
            natal_score = int(triplicity.get("natal_essential_score") or 0)
            return_score = int(triplicity.get("return_essential_score") or 0)
            natal_house = int(triplicity.get("natal_house") or 0)
            return_house = int(triplicity.get("return_house") or 0)
            natal_good = natal_score > 0 and natal_house not in {6, 8, 12}
            return_good = return_score > 0 and return_house not in {6, 8, 12}
            if natal_score > 0 and return_score > 0 and not natal_good and not return_good:
                comparison = (
                    "The ruler keeps real essential strength in both figures, but both place it in a difficult house. Capacity is repeated, "
                    "yet it must operate through concealment, loss, fear, dependency, or burdens rather than uncomplicated advancement."
                )
            elif natal_good and return_good:
                comparison = "Both figures support the ruler, so the natal promise is reinforced for the year."
            elif not natal_good and return_good:
                comparison = "The return improves a weak natal condition, so the year's difficulty is moderated but not erased."
            elif natal_good and not return_good:
                comparison = "The return weakens a strong natal condition, so expected advantages meet delay, cost, or obstruction this year."
            else:
                comparison = "Both figures leave the ruler weak, so the underlying difficulty is repeated and intensified for the year."
            paragraphs.append(
                f"Ibn Ezra specifically compares the sect-light triplicity ruler in the nativity and revolution. Here {triplicity.get('ruler')} "
                f"moves from natal house {triplicity.get('natal_house')} and essential score {natal_score} to return house "
                f"{triplicity.get('return_house')} and score {return_score}. {comparison} [{item.get('id')}]"
            )
        determinations = [
            value for value in details.get("determinations", []) if isinstance(value, Mapping)
        ]
        if determinations:
            text = "; ".join(str(value.get("judgment", "")).rstrip(".") for value in determinations)
            paragraphs.append(
                f"The seven-planet return overlays record: {text}. Repetition between these whole-sign placements, the profection, "
                f"and the time lords identifies the events most likely to dominate the year. {details.get('location_basis')} "
                f"[{item.get('id')}]"
            )
            by_planet = {
                str(value.get("planet")): value for value in determinations
            }
            sun = by_planet.get("Sun", {})
            mercury = by_planet.get("Mercury", {})
            moon = by_planet.get("Moon", {})
            saturn = by_planet.get("Saturn", {})
            mars = by_planet.get("Mars", {})
            venus = by_planet.get("Venus", {})
            jupiter = by_planet.get("Jupiter", {})
            if sun.get("sr_house") == 12 and mercury.get("sr_house") == 12:
                paragraphs.append(
                    "The Sun and Mercury both repeat the twelfth place. This predicts a year dominated by concealed work, withdrawal, "
                    "institutions, private authority, hidden opponents, delayed recognition, and decisions or documents handled away from public view. "
                    "Because Mercury is also the return-Ascendant ruler and the active decennial sublord, communication, calculation, trade, and technical work "
                    f"become the principal route through that confinement rather than an escape from it. [{item.get('id')}]"
                )
            if moon.get("sr_house") == 8 and saturn.get("sr_house") == 8:
                paragraphs.append(
                    "The Moon and Saturn repeat the eighth place. Shared obligations, another person's crisis, fear, endings, inheritance, debt, or resources "
                    "that cannot be controlled alone become a concrete annual burden. Saturn's return to this place makes delay and compulsory responsibility "
                    f"more likely than a clean resolution. [{item.get('id')}]"
                )
            if mars.get("sr_house") == 2:
                paragraphs.append(
                    "Mars in the return second place predicts conflict, urgency, waste, or forced expenditure around livelihood and movable resources. "
                    f"It is an activation of financial strain, not permission to make a financial decision from this report. [{item.get('id')}]"
                )
            if venus.get("sr_house") == 11 and jupiter.get("sr_house") == 11:
                paragraphs.append(
                    "Venus and Jupiter together emphasize the return eleventh place. Friends, patrons, alliances, audiences, and communities supply the year's "
                    "chief counterweight: help can arrive through social or professional networks, though it must be weighed against the repeated twelfth- and "
                    f"eighth-place burdens rather than treated as a universal rescue. [{item.get('id')}]"
                )
    return paragraphs


def _timing_paragraphs(
    timing: list[Mapping[str, Any]],
    planets: list[Mapping[str, Any]],
    topical: list[Mapping[str, Any]],
) -> list[str]:
    if not timing:
        return []
    paragraphs = ["## The Active Time Lords"]
    planet_map = {
        str(value.get("details", {}).get("name")): value
        for value in planets
        if isinstance(value.get("details"), Mapping)
    }
    topic_by_sign = {
        str(value.get("details", {}).get("sign")): value
        for value in topical
        if isinstance(value.get("details"), Mapping)
    }
    technique_labels = {
        "annual_profection": "Annual Profection",
        "ascendant_distributor": "Ascendant Prorogation and Distributor",
        "firdaria": "Firdaria",
        "zodiacal_releasing": "Zodiacal Releasing",
        "decennials": "Decennials",
    }
    for item in timing:
        details = item.get("details")
        if not isinstance(details, Mapping):
            continue
        technique = str(details.get("technique") or "timing")
        label = technique_labels.get(technique, technique.replace("_", " ").title())
        if technique == "zodiacal_releasing" and details.get("lot"):
            label += f" from {details.get('lot')}"
        paragraphs.extend([f"### {label}", _evidence_sentence(item)])
        if technique == "annual_profection":
            sign = str(details.get("sign"))
            topic_item = topic_by_sign.get(sign)
            topic_details = topic_item.get("details", {}) if topic_item else {}
            ruler = str(next(iter(details.get("rulers", [])), ""))
            ruler_item = planet_map.get(ruler)
            ruler_details = ruler_item.get("details", {}) if ruler_item else {}
            topic = str(topic_details.get("topic") or "the activated place")
            condition = _condition_phrase(ruler_details) if ruler_details else "a mixed"
            paragraphs.append(
                f"This birthday year activates {topic}, and {ruler} carries the year from {condition} natal condition. "
                f"The year's most likely manifestations are {PLANET_PERIOD_EVENTS.get(ruler, 'events governed by the Lord of the Year')}. "
                f"Because the ruler is natally placed in {HOUSE_CONTEXT.get(ruler_details.get('house'), 'its natal house')}, "
                "events in that field become the route through which the profected topic is delivered. "
                f"[{item.get('id')}]"
            )
        elif technique == "ascendant_distributor":
            bound_ruler = str(details.get("bound_ruler"))
            partner = str(details.get("partner"))
            bound_item = planet_map.get(bound_ruler)
            partner_item = planet_map.get(partner)
            bound_details = bound_item.get("details", {}) if bound_item else {}
            partner_details = partner_item.get("details", {}) if partner_item else {}
            start_age = details.get("previous_transition_age")
            end_age = details.get("next_transition_age")
            start_date = details.get("previous_transition_date")
            end_date = details.get("next_transition_date")
            next_ruler = details.get("next_bound_ruler")
            paragraphs.append(
                f"The Ascendant prorogation concerns your manner of proceeding, movement, travel, residence, and the "
                f"circumstances that act directly upon you. {bound_ruler} distributes the present stretch"
                + (
                    f" from configured age {float(start_age):.2f}"
                    + (f" ({start_date})" if start_date else "")
                    + f" until age {float(end_age):.2f}"
                    + (f" ({end_date})" if end_date else "")
                    if start_age is not None and end_age is not None
                    else ""
                )
                + f". {bound_ruler} is {_condition_class(bound_details) if bound_details else 'mixed'} and natally placed in "
                f"{HOUSE_CONTEXT.get(bound_details.get('house'), 'its natal house')}; its period therefore brings "
                f"{PLANET_PERIOD_EVENTS.get(bound_ruler, bound_ruler + ' matters')} into events that alter your immediate course. "
                f"[{item.get('id')}]"
            )
            if partner_item:
                transition_text = (
                    f"The numerically solved configured transition gives {next_ruler} at age {float(end_age):.2f}"
                    + (f" ({end_date})" if end_date else "")
                    if end_age is not None
                    else "No later bound transition falls inside the generated horizon"
                )
                paragraphs.append(
                    f"{partner} participates because it cast the last calculated ray to reach the Ascendant prorogation, "
                    f"not because the engine selected an arbitrary present-time orb. {partner} is {_condition_class(partner_details)} "
                    f"in {HOUSE_CONTEXT.get(partner_details.get('house'), 'its natal house')}. It modifies the {bound_ruler} period "
                    f"through {PLANET_PERIOD_EVENTS.get(partner, partner + ' matters')}, but it does not replace the distributor. "
                    + transition_text
                    + f". [{item.get('id')}]"
                )
            paragraphs.append(
                "This is the source-audited Ascendant distributor layer, not the entire primary-direction system. The report "
                "does not disguise the configured one-degree key, Egyptian bound table, numerical boundary solving, or "
                f"latitude-free zodiacal aspect points as a complete Placidus semi-arc calculation. [{item.get('id')}]"
            )
        elif technique == "firdaria":
            rulers = [str(value) for value in details.get("rulers", []) if value]
            if details.get("beyond_span") or not rulers:
                paragraphs.append(
                    "The classical Firdaria sequence spans 75 years and is complete for this "
                    "nativity. Rather than invent a continuation the inspected sources do not "
                    "state, this report reads the current years through the remaining time-lord "
                    f"layers above. [{item.get('id')}]"
                )
                continue
            major = rulers[0]
            sub = rulers[1] if len(rulers) > 1 else None
            event_text = PLANET_PERIOD_EVENTS.get(major, "the major lord's affairs")
            if sub:
                sub_events = PLANET_PERIOD_EVENTS.get(sub, "the sub-lord's affairs")
                event_text += f", filtered through {sub_events}"
            paragraphs.append(
                f"This period makes {event_text} recurrent rather than incidental. The major lord supplies the long chapter; "
                "the sub-lord describes the people, circumstances, and immediate occasions through which it becomes concrete. "
                f"[{item.get('id')}]"
            )
        elif technique == "zodiacal_releasing":
            level_dates = []
            for level, start_key, end_key in (
                ("L2", "start", "end"),
                ("L3", "level_3_start", "level_3_end"),
                ("L4", "level_4_start", "level_4_end"),
            ):
                if details.get(start_key) and details.get(end_key):
                    level_dates.append(f"{level} {details.get(start_key)} to {details.get(end_key)}")
            if level_dates:
                levels = [str(value) for value in details.get("levels", []) if value]
                level_rulers = [SIGN_RULERS[value] for value in levels if value in SIGN_RULERS]
                level_events = []
                for ruler in dict.fromkeys(level_rulers):
                    level_events.append(PLANET_PERIOD_EVENTS.get(ruler, ruler))
                paragraphs.append(
                    "The nested bounds are " + "; ".join(level_dates) + ". Shorter levels modulate the larger chapter; "
                    "they do not carry the same weight as L1 or L2. The active signs repeatedly bring "
                    + "; and ".join(level_events)
                    + f" into the same period. [{item.get('id')}]"
                )
        elif technique == "decennials":
            rulers = [str(value) for value in details.get("rulers", []) if value]
            event_text = "; and ".join(
                PLANET_PERIOD_EVENTS.get(ruler, ruler) for ruler in rulers
            )
            paragraphs.append(
                f"The decennial rulers add {event_text} to the long-form prediction. When the same rulers also govern "
                "profection, Firdaria, or releasing, their events are more likely to become visible and consequential. "
                f"[{item.get('id')}]"
            )
            upcoming = [
                value for value in details.get("upcoming_subperiods", []) if isinstance(value, Mapping)
            ]
            if upcoming:
                paragraphs.append(
                    "The remaining near-term sub-period sequence is "
                    + "; ".join(
                        f"{value.get('sub_lord')} from {value.get('start_date')} to {value.get('end_date')}"
                        for value in upcoming
                    )
                    + f". These boundaries show changes of sub-ruler inside the same major chapter. [{item.get('id')}]"
                )
    rulers: list[str] = []
    for item in timing:
        details = item.get("details")
        if not isinstance(details, Mapping):
            continue
        rulers.extend(str(value) for value in details.get("rulers", []) if value)
        rulers.extend(
            SIGN_RULERS[sign]
            for sign in details.get("levels", [])
            if sign in SIGN_RULERS
        )
    repeated = [
        name for name in PLANET_ORDER
        if rulers.count(name) >= 2
    ]
    if repeated:
        descriptions = []
        citations = []
        for name in repeated:
            item = planet_map.get(name)
            if not item:
                continue
            detail = item["details"]
            context = HOUSE_CONTEXT.get(detail.get("house"), f"house {detail.get('house')}")
            descriptions.append(
                f"{name}, returning across {rulers.count(name)} active rulership positions, carries the emphasis back to {context}"
            )
            citations.append(f"[{item.get('id')}]")
        if descriptions:
            paragraphs.append(
                "The most useful timing signal is repetition, not any isolated date. "
                + "; ".join(descriptions)
                + ". This convergence predicts that these subjects recur through several kinds of event during the period; "
                "the natal condition of each ruler determines whether they arrive as leverage, burden, conflict, delay, or mixed opportunity. "
                + " ".join(citations)
            )
    paragraphs.extend(["## Timing Convergence", (
        "When several independent clocks repeat the same ruler, the report treats the corresponding events as probable, not merely thematic. "
        "The date range identifies when the natal promise is most likely to become visible; the ruler's condition tells whether its first manifestation is constructive, obstructive, or mixed."
    )])
    return paragraphs


def _long_range_timing_paragraphs(
    maps: list[Mapping[str, Any]], planets: list[Mapping[str, Any]]
) -> list[str]:
    if not maps:
        return []
    planet_map = {
        str(item.get("details", {}).get("name")): item
        for item in planets
        if isinstance(item.get("details"), Mapping)
    }
    paragraphs = [
        "## The Longer Map",
        (
            "Long-range chapters are included to show changes of ruler and emphasis. Their scale matters: a multi-year "
            "chapter describes the background field and must not be read as a continuous event."
        ),
    ]
    for item in maps:
        details = item.get("details", {})
        if not isinstance(details, Mapping):
            continue
        technique = details.get("technique")
        if technique == "annual_profection_map":
            continue
        elif technique == "firdaria_map":
            paragraphs.extend(["### The Remaining Firdaria Chapters", _evidence_sentence(item)])
            for period in details.get("periods", []):
                if not isinstance(period, Mapping):
                    continue
                lord = str(period.get("lord"))
                planet = planet_map.get(lord)
                ruler_text = ""
                if planet:
                    pd = planet["details"]
                    ruler_text = (
                        f" {lord} is natally in house {pd.get('house')} with {pd.get('dignities')}, so this chapter is "
                        f"routed through {HOUSE_CONTEXT.get(pd.get('house'), 'that place')} and from "
                        f"{_condition_phrase(pd)} condition repeatedly produces "
                        f"{PLANET_PERIOD_EVENTS.get(lord, lord + ' matters')} [{planet.get('id')}]"
                    )
                elif lord in ("North Node", "South Node"):
                    ruler_text = (
                        " The nodal periods are the configured extension to the seven-planet core; they describe "
                        "increase and release respectively rather than a planet's own agenda."
                    )
                paragraphs.append(
                    f"{lord}, {period.get('start')} to {period.get('end')} ({period.get('years')} years).{ruler_text} "
                    f"[{item.get('id')}]"
                )
        elif technique == "zodiacal_releasing_map":
            lot = str(details.get("lot"))
            field = "action, direction, and reputation" if lot == "Spirit" else "circumstance and material allotment"
            paragraphs.extend([f"### Level-1 Releasing from {lot}", _evidence_sentence(item)])
            for chapter in details.get("chapters", []):
                if not isinstance(chapter, Mapping):
                    continue
                sign = str(chapter.get("sign"))
                ruler = SIGN_RULERS.get(sign)
                planet = planet_map.get(str(ruler))
                ruler_text = ""
                if planet:
                    pd = planet["details"]
                    condition = _condition_phrase(pd)
                    ruler_text = (
                        f" Its ruler, {ruler}, is natally in house {pd.get('house')} with {pd.get('dignities')}, routing "
                        f"the chapter through {HOUSE_CONTEXT.get(pd.get('house'), 'that place')}. From {condition} condition, "
                        f"it repeatedly produces {PLANET_PERIOD_EVENTS.get(str(ruler), str(ruler) + ' matters')}. [{planet.get('id')}]"
                    )
                peak = (
                    " The engine marks this as angular from Fortune, increasing activity and prominence without fixing the outcome."
                    if chapter.get("peak_from_fortune")
                    else ""
                )
                paragraphs.append(
                    f"{sign}, {chapter.get('start_date')} to {chapter.get('end_date')}, is a long chapter of {field}.{ruler_text}{peak} "
                    f"[{item.get('id')}]"
                )
    return paragraphs


# One full profection cycle returns the Ascendant to its starting place.
DETAILED_FORECAST_YEARS = 12


def _ranked_forecast_paragraphs(
    maps: list[Mapping[str, Any]],
    timing: list[Mapping[str, Any]],
    planets: list[Mapping[str, Any]],
) -> list[str]:
    """Turn converging chronocrators into a ranked six-year event forecast."""
    profection_map = next(
        (
            item for item in maps
            if item.get("details", {}).get("technique") == "annual_profection_map"
        ),
        None,
    )
    if not profection_map:
        return []
    decennial_map = next(
        (
            item for item in maps
            if item.get("details", {}).get("technique") == "decennial_map"
        ),
        None,
    )
    planet_map = {
        str(item.get("details", {}).get("name")): item
        for item in planets
        if isinstance(item.get("details"), Mapping)
    }

    def overlaps(start_a: str, end_a: str, start_b: str, end_b: str) -> bool:
        return bool(start_a and end_a and start_b and end_b and start_a < end_b and start_b < end_a)

    def overlap_days(start_a: str, end_a: str, start_b: str, end_b: str) -> int:
        try:
            start = max(datetime.fromisoformat(start_a[:10]), datetime.fromisoformat(start_b[:10]))
            end = min(datetime.fromisoformat(end_a[:10]), datetime.fromisoformat(end_b[:10]))
        except ValueError:
            return 0
        return max(0, (end - start).days)

    windows: list[dict[str, Any]] = []
    for chapter in profection_map.get("details", {}).get("chapters", []):
        if not isinstance(chapter, Mapping):
            continue
        start, end = str(chapter.get("start") or ""), str(chapter.get("end") or "")
        profection_ruler = str(chapter.get("ruler") or "")
        rulers = [profection_ruler]
        citations = [f"[{profection_map.get('id')}]" ]
        score = 4.0
        supporting_labels = [f"annual profection: {profection_ruler}"]
        decennial_labels: list[str] = []
        if decennial_map:
            for period in decennial_map.get("details", {}).get("periods", []):
                if not isinstance(period, Mapping) or not overlaps(start, end, str(period.get("start") or ""), str(period.get("end") or "")):
                    continue
                major = str(period.get("major_lord") or "")
                if major:
                    rulers.append(major)
                    decennial_labels.append(f"{major} major")
                    if major == profection_ruler:
                        score += 3.0
                        supporting_labels.append(f"decennial major: {major}")
                for sub in period.get("sub_periods", []):
                    if isinstance(sub, Mapping) and overlaps(start, end, str(sub.get("start") or ""), str(sub.get("end") or "")):
                        sub_lord = str(sub.get("sub_lord") or "")
                        if sub_lord:
                            rulers.append(sub_lord)
                            decennial_labels.append(f"{sub_lord} sub")
                            if sub_lord == profection_ruler:
                                score += 2.0
                                supporting_labels.append(f"decennial subperiod: {sub_lord}")
            citations.append(f"[{decennial_map.get('id')}]" )
        other_labels: list[str] = []
        for item in timing:
            details = item.get("details", {})
            if not isinstance(details, Mapping):
                continue
            technique = str(details.get("technique") or "")
            if technique == "decennials":
                continue
            item_start, item_end = str(details.get("start") or ""), str(details.get("end") or "")
            active = overlaps(start, end, item_start[:10], item_end[:10]) if item_start and item_end else False
            if technique == "ascendant_distributor":
                previous = str(details.get("previous_transition_date") or "")[:10]
                following = str(details.get("next_transition_date") or "")[:10]
                active = overlaps(start, end, previous, following)
                item_start, item_end = previous, following
            if active and item_start and item_end and overlap_days(start, end, item_start, item_end) < 30:
                active = False
            if not active:
                continue
            active_rulers = [str(value) for value in details.get("rulers", []) if value]
            active_rulers.extend(
                SIGN_RULERS[sign]
                for sign in details.get("levels", [])
                if sign in SIGN_RULERS
            )
            rulers.extend(active_rulers)
            if active_rulers:
                other_labels.append(f"{technique.replace('_', ' ')}: {'/'.join(active_rulers)}")
            if technique == "ascendant_distributor" and profection_ruler in active_rulers:
                score += 3.0
                supporting_labels.append(f"Ascendant distributor: {profection_ruler}")
            elif technique == "firdaria" and active_rulers:
                if active_rulers[0] == profection_ruler:
                    score += 3.0
                    supporting_labels.append(f"Firdaria major: {profection_ruler}")
                if len(active_rulers) > 1 and active_rulers[1] == profection_ruler:
                    score += 2.0
                    supporting_labels.append(f"Firdaria subperiod: {profection_ruler}")
            elif technique == "zodiacal_releasing":
                level_rulers = [
                    SIGN_RULERS[sign]
                    for sign in details.get("levels", [])
                    if sign in SIGN_RULERS
                ]
                for level_index, level_ruler in enumerate(level_rulers):
                    if level_ruler == profection_ruler:
                        level_weight = (3.0, 2.0, 1.0, 0.5)[min(level_index, 3)]
                        score += level_weight
                        supporting_labels.append(
                            f"releasing from {details.get('lot')} L{level_index + 1}: {profection_ruler}"
                        )
                        break
            citations.append(f"[{item.get('id')}]" )
        windows.append(
            {
                "chapter": chapter,
                "ruler": profection_ruler,
                "rulers": rulers,
                "score": score,
                "decennial_labels": list(dict.fromkeys(decennial_labels)),
                "other_labels": other_labels,
                "supporting_labels": supporting_labels,
                "citations": " ".join(dict.fromkeys(citations)),
            }
        )
    if not windows:
        return []
    # Detailed year-by-year judgment covers one complete profection cycle (12
    # years returns the Ascendant to its starting place). The remaining years
    # are published as a compact calendar below rather than as prose.
    all_windows = windows
    windows = windows[:DETAILED_FORECAST_YEARS]
    ranked = sorted(windows, key=lambda row: (-float(row["score"]), str(row["chapter"].get("start"))))
    rank_by_start = {str(row["chapter"].get("start")): index + 1 for index, row in enumerate(ranked)}
    first_year = str(windows[0]["chapter"].get("start"))[:4]
    last_year = str(windows[-1]["chapter"].get("end"))[:4]
    paragraphs = [
        f"## Ranked Forecast: {first_year}-{last_year}",
        "These are event judgments, not a list of themes. Rank measures agreement among independent clocks; it does not mean that a lower-ranked year is unimportant. Dates are activation windows, not promises that an event occurs on one exact day.",
    ]
    event_verdicts = {
        "Sun": "A change of command, visibility, or relations with authority requires you to claim direction rather than remain in another person's shadow.",
        "Moon": "A change involving family, residence, caregiving, belonging, or private circumstance pulls attention away from the public course and closes an old habit or attachment.",
        "Mercury": "A technical, commercial, written, educational, or negotiating project becomes the clearest route to advancement; a document or decision redirects reputation.",
        "Venus": "A relationship, alliance, audience, patron, or creative agreement becomes decisive. Attraction and opportunity arrive together with obligations or conflict that must be faced plainly.",
        "Mars": "A dispute, severance, competitive push, urgent expense, or break with an ally forces action. The gain comes through cutting away a failing arrangement, not preserving peace at any price.",
        "Jupiter": "An opening through a teacher, patron, child, creative venture, education, travel, or belief system enlarges the field, but poor terms or overreach can make the opportunity costlier than it first appears.",
        "Saturn": "A delayed obligation, ending, shared burden, older authority, fear, or period of isolation becomes unavoidable and demands a durable structure rather than a temporary escape.",
    }
    for row in sorted(windows, key=lambda value: str(value["chapter"].get("start"))):
        chapter = row["chapter"]
        ruler = str(row["ruler"])
        planet = planet_map.get(ruler)
        pd = planet.get("details", {}) if planet else {}
        activated_house = int(chapter.get("age") or 0) % 12 + 1
        condition = _condition_class(pd)
        if condition == "strong":
            consequence = "The ruler has the capacity to convert this into a visible result, provided its work is actually performed."
        elif condition == "debilitated":
            consequence = "Because the ruler is debilitated, the first version is likely to contain bad terms, excess, dependence, conflict, or reversal; improvement comes only after correction."
        elif condition == "unsupported":
            consequence = "Because the ruler lacks essential support, another person's choices or changing circumstances have unusual control over the result."
        else:
            consequence = "The result is mixed: a real opening arrives attached to a price, compromise, or continuing duty."
        support_text = "; ".join(dict.fromkeys(row["supporting_labels"]))
        background = [
            label for label in row["decennial_labels"] + row["other_labels"]
            if ruler not in label
        ]
        background_text = (
            " Other active rulers color the year without increasing its convergence rank: "
            + "; ".join(dict.fromkeys(background))
            + "."
            if background else ""
        )
        paragraphs.extend([
            f"### Rank {rank_by_start[str(chapter.get('start'))]} — {chapter.get('start')} to {chapter.get('end')}: {ruler} Year",
            f"Age {chapter.get('age')} activates {chapter.get('sign')} and {HOUSE_CONTEXT.get(activated_house, f'house {activated_house}')}. {event_verdicts.get(ruler, PLANET_PERIOD_EVENTS.get(ruler, ruler + ' matters'))} "
            f"{ruler}'s natal placement in {HOUSE_CONTEXT.get(pd.get('house'), 'its natal place')} shows where the event comes from or where its consequences land. {consequence} "
            f"Convergence score {row['score']:.1f}; direct support: {support_text}.{background_text} "
            f"{row['citations']}" + (f" [{planet.get('id')}]" if planet else ""),
        ])

    remaining = all_windows[DETAILED_FORECAST_YEARS:]
    if remaining:
        first = str(remaining[0]["chapter"].get("start"))[:4]
        last = str(remaining[-1]["chapter"].get("end"))[:4]
        paragraphs.extend([
            f"### The Full Profection Calendar: {first}-{last}",
            (
                "Beyond the detailed cycle above, the annual profection calendar continues as exact "
                "arithmetic. Each line gives the year, the activated place, and the Lord of that Year, "
                "whose natal condition (judged earlier in this report) decides how the year performs. "
                "These are ruler activations, not predicted events."
            ),
        ])
        rows: list[str] = []
        for row in remaining:
            chapter = row["chapter"]
            ruler = str(row["ruler"])
            house = int(chapter.get("age") or 0) % 12 + 1
            rows.append(
                f"- **{str(chapter.get('start'))[:4]}-{str(chapter.get('end'))[:4]}** (age "
                f"{chapter.get('age')}): {chapter.get('sign')}, house {house} — "
                f"{HOUSE_CONTEXT.get(house, f'house {house}')} — Lord of the Year: {ruler}"
            )
        paragraphs.append("\n".join(rows))
    return paragraphs


def compose_deterministic_draft(chart_data: Mapping[str, Any], scope: str = "full") -> tuple[str, dict[str, Any]]:
    """Return a safe, fully deterministic reading draft and its evidence packet."""
    scope = _normalize_reading_scope(scope)
    natal = scope == "natal"
    packet = evidence_packet(chart_data)
    judgment_plan = build_judgment_plan(packet)
    subject = packet.get("subject") or "the native"
    foundation = _group(packet, "foundation")
    angles = _group(packet, "angles")
    planets = _group(packet, "planetary_condition")
    topical = _group(packet, "topical")
    chart_rulers = _group(packet, "chart_ruler")
    aspects = _group(packet, "aspect")
    antiscia = _group(packet, "antiscia_configuration")
    doryphory = _group(packet, "doryphory")
    receptions = _group(packet, "reception")
    joys = _group(packet, "planetary_joy")
    hayz_halb = _group(packet, "hayz_halb")
    paulus_place_rules = _group(packet, "planet_in_place_source")
    dodecatemoria_x12 = _group(packet, "dodecatemoria_x12")
    dodecatemoria_x13 = _group(packet, "dodecatemoria_x13")
    monomoiria_zoidion = _group(packet, "monomoiria_zoidion")
    monomoiria_trigonal = _group(packet, "monomoiria_trigonal")
    degree_qualities = _group(packet, "degree_quality")
    bound_delineations = _group(packet, "bound_delineation")
    causative_place = _group(packet, "causative_place")
    climacteric_years = _group(packet, "climacteric_year")
    fixed_stars = _group(packet, "fixed_star")
    dispositors = _group(packet, "dispositor_network")
    lots = _group(packet, "lot")
    lunar_cycle = _group(packet, "lunar_cycle")
    lunar_mansion_scope = _group(packet, "lunar_mansion_scope")
    life_chapters = _group(packet, "life_chapters")
    longevity = _group(packet, "longevity")
    annual_context = _group(packet, "annual_context")
    timing = _group(packet, "timing")
    timing_maps = _group(packet, "timing_map")
    temperaments = _group(packet, "temperament")
    forks = _group(packet, "doctrinal_fork")

    lines = [REPORT_NOTICE, "", "# Your Nativity at a Glance", ""]
    if natal:
        lines.append(
            f"This is a judgment of {subject}'s nativity, not a list of placements. It states who you are and how "
            "the life has gone so far: capacities, difficulties, relationships, work, losses, and conflicts. It does "
            "not predict what happens next. Each conclusion is weighted through sect, planetary condition, rulership, "
            "configuration, and reception."
        )
    else:
        lines.append(
            f"This is a judgment of {subject}'s nativity, not a list of placements. It states what the chart says about "
            "your capacities, difficulties, relationships, work, losses, conflicts, and likely periods of change. Each "
            "conclusion is weighted through sect, planetary condition, rulership, configuration, reception, and time lords."
        )
    sect_label: Optional[str] = None
    if foundation:
        lines.append(_evidence_sentence(foundation[0]))
        sect_fact = str(foundation[0].get("fact", "")).upper()
        # Captured for _valens_placement_verdict: Valens I.1 p.5 runs the
        # placement-and-sect test BEFORE the benefic/malefic label, so the
        # planet paragraphs need to know the sect, not just this preamble.
        if "CHART IS DAY" in sect_fact:
            sect_label = "DAY"
        elif "CHART IS NIGHT" in sect_fact:
            sect_label = "NIGHT"
        if "CHART IS DAY" in sect_fact:
            lines.append(
                "Sect is applied before judging the malefics: Saturn is the more moderated malefic in this day figure, while Mars is less accommodated to the prevailing sect. This changes the manner and severity of their testimony; it does not make Saturn benefic or make every Mars testimony destructive. "
                f"[{foundation[0].get('id')}]"
            )
        elif "CHART IS NIGHT" in sect_fact:
            lines.append(
                "Sect is applied before judging the malefics: Mars is the more moderated malefic in this night figure, while Saturn is less accommodated to the prevailing sect. This changes the manner and severity of their testimony; it does not make Mars benefic or make every Saturn testimony destructive. "
                f"[{foundation[0].get('id')}]"
            )
    if chart_rulers:
        lines.append(
            _evidence_sentence(chart_rulers[0])
            + " This planet is the chart's strongest configured center of command. Its skills describe the means by "
            "which you recover agency when other parts of the nativity are afflicted; it is powerful, but it does not "
            "cancel the affliction or spare you from the events signified by it."
        )
    if temperaments:
        lines.append(
            _evidence_sentence(temperaments[0])
            + " In this report the humoral label is retained only to explain the "
            "historical model's preferred style of response; it does not classify "
            "the reader's body or mind."
        )
    lines.extend(_angle_paragraphs(angles, topical))
    lines.extend(_direct_judgment(judgment_plan, planets, topical))

    lines.extend(["", "# The Leading Testimonies", ""])
    lines.append(
        "Each planet acts in your life. Strength shows capacity; debility or maltreatment shows recurring failures, conflicts, "
        "losses, delays, and difficult people. Contrary testimony modifies rather than erases judgment."
    )
    lines.extend(
        _planetary_testimony_paragraphs(
            planets, aspects, chart_rulers, sect_type=sect_label
        )
    )
    lines.extend(_antiscia_paragraphs(antiscia, planets))
    lines.extend(_doryphory_paragraphs(doryphory, planets))
    lines.extend(_dispositor_paragraphs(dispositors))
    lines.extend(_paulus_place_rule_paragraphs(paulus_place_rules, planets))
    lines.extend(_fixed_star_paragraphs(fixed_stars))
    if receptions:
        lines.append(
            "Reception adds a second question: whether one planet can host or assist "
            "another. "
            + " ".join(_evidence_sentence(item) for item in receptions)
            + " Assistance makes a difficult exchange more workable, but does not "
            "erase the planets' natal condition or ensure a favorable outcome."
        )

    lines.extend(["", "# Life Topics", ""])
    lines.append(
        "Traditional topical judgment begins with the whole-sign place, its ruler, the ruler's condition and location, "
        "and planets occupying or aspecting the place. The following sections state the expected condition of each life "
        "topic directly. A difficult ruler means a difficult topic unless stronger, specifically identified testimony mitigates it."
    )
    lines.extend(_integrated_life_judgments(topical, planets, aspects))
    lines.extend(["## The Twelve Places: Complete Reference"])
    lines.extend(_topic_full_paragraphs(topical, planets))
    lines.extend(_lot_paragraphs(lots, planets))
    if not natal:
        lines.extend(_longevity_paragraphs(longevity))
    lines.extend(["## The Secondary Doctrine and Derived Degrees"])
    lines.append(
        "The main judgment is already complete. The following techniques are retained because they either confirm it, qualify it, or expose a real disagreement; none is allowed to replace the natal planets, places, and rulers."
    )
    lines.extend(_joy_paragraphs(joys, planets))
    lines.extend(_sect_condition_paragraphs(hayz_halb, planets))
    lines.extend(
        _dodecatemoria_paragraphs(
            dodecatemoria_x12,
            dodecatemoria_x13,
            planets,
        )
    )
    lines.extend(
        _monomoiria_paragraphs(
            monomoiria_zoidion,
            monomoiria_trigonal,
            planets,
        )
    )
    lines.extend(_bound_delineation_paragraphs(bound_delineations))
    lines.extend(_causative_place_paragraphs(causative_place))
    lines.extend(_degree_quality_paragraphs(degree_qualities))
    lines.extend(_lunar_cycle_paragraphs(lunar_cycle))
    lines.extend(_lunar_mansion_scope_paragraphs(lunar_mansion_scope))

    if not natal:
        lines.extend(["", "# The Present Chapter", ""])
        lines.append(
            "Timing activates the events promised by the nativity. One clock gives a broad subject; repetition across "
            "profection, Firdaria, releasing, decennials, and the solar return makes manifestation more likely. The report "
            "therefore names the probable event fields and distinguishes ordinary activation from severe convergence."
        )
        lines.extend(_life_chapter_paragraphs(life_chapters, planets))
        lines.extend(_timing_paragraphs(timing, planets, topical))
        lines.extend(_climacteric_year_paragraphs(climacteric_years))
        lines.extend(_ranked_forecast_paragraphs(timing_maps, timing, planets))
        lines.extend(_long_range_timing_paragraphs(timing_maps, planets))
        lines.extend(_annual_context_paragraphs(annual_context))

    lines.extend(["", "# Where the Sources Differ", ""])
    if forks:
        for item in forks:
            lines.append(
                _evidence_sentence(item)
                + " Both results remain visible because fidelity to traditional "
                "astrology requires preserving disagreement rather than silently "
                "combining incompatible tables."
            )
    else:
        lines.append(
            "No chart-specific dignity-table disagreement was emitted for the facts "
            "selected into this edition. That does not imply unanimity across the "
            "tradition; it means no configured fork changed these selected facts."
        )

    lines.extend(["", "# Method and Limits", ""])
    lines.append(
        "The astronomical positions come from the project's Swiss Ephemeris chart, "
        "with whole-sign houses used for topics and the seven visible planets used "
        "for core judgment. Each bracketed evidence identifier maps to a calculated "
        "fact, an authority label, a provenance path, and an explicit interpretive "
        "limit. Those identifiers are a verification aid, not decorative citations."
    )
    lines.append(
        "Historical texts disagree on important tables and methods. Where a supplied "
        "chart-specific fork changes a judgment, this report keeps both positions. "
        "Where an authority has not yet been verified against a stable primary-text "
        "edition, the system must describe it as a configured method rather than "
        "claiming universal or perfect textual authority."
    )
    if natal:
        lines.append(
            "This free edition is natal only: character and the life so far. Time lords, the present chapter, and "
            "dated forecasts belong to the $20 source-cited Complete Analysis — this edition does not publish "
            "length-of-life arithmetic. Protected professional domains, prescriptive remediation, and concrete "
            "practical instructions remain outside the customer report."
        )
    else:
        lines.append(
            "This edition publishes the supplied historical length-of-life arithmetic, including competing branches, "
            "failed results, and anaretic testimony. It does not convert that historical judgment into medical direction. "
            "Protected professional domains, prescriptive remediation, and concrete practical instructions remain outside "
            "the customer report."
        )
    lines.extend(["", REPORT_NOTICE])
    return "\n\n".join(lines), packet


def _citation_violations(markdown: str, allowed_ids: set[str]) -> list[ReadingViolation]:
    violations: list[ReadingViolation] = []
    cited = set(re.findall(r"\[(E\d+)\]", markdown))
    unknown = sorted(cited - allowed_ids)
    if unknown:
        violations.append(
            ReadingViolation(
                "unknown_evidence",
                "The report cites evidence identifiers not present in its packet.",
                ", ".join(unknown),
            )
        )
    if not cited:
        violations.append(
            ReadingViolation(
                "missing_evidence",
                "The report contains no evidence citations.",
                "Expected citations such as [E1].",
            )
        )
    return violations


def _coverage_violations(packet: Mapping[str, Any]) -> list[ReadingViolation]:
    """Require the complete premium evidence architecture, not a short fallback."""
    evidence = [item for item in packet.get("evidence", []) if isinstance(item, Mapping)]
    counts: dict[str, int] = defaultdict(int)
    timing_techniques: list[str] = []
    lot_names: set[str] = set()
    for item in evidence:
        counts[str(item.get("category"))] += 1
        details = item.get("details", {})
        if not isinstance(details, Mapping):
            continue
        if item.get("category") == "timing":
            timing_techniques.append(str(details.get("technique")))
        if item.get("category") == "lot" and details.get("name"):
            lot_names.add(str(details.get("name")))
    missing: list[str] = []
    expected_counts = {
        "foundation": 1,
        "angles": 1,
        "planetary_condition": 7,
        "dispositor_network": 1,
        "topical": 12,
        "antiscia_configuration": 1,
        "doryphory": 1,
        "lunar_mansion_scope": 1,
        "dodecatemoria_x12": 7,
        "dodecatemoria_x13": 7,
        "monomoiria_zoidion": 1,
        "monomoiria_trigonal": 1,
        "degree_quality": 1,
        "lunar_cycle": 1,
        "life_chapters": 1,
        "longevity": 2,
        "annual_context": 1,
    }
    for category, minimum in expected_counts.items():
        if counts.get(category, 0) < minimum:
            missing.append(f"{category} {counts.get(category, 0)}/{minimum}")
    if not {"Fortune", "Spirit"}.issubset(lot_names):
        missing.append("Lots of Fortune and Spirit")
    for technique, minimum in (
        ("annual_profection", 1),
        ("firdaria", 1),
        ("zodiacal_releasing", 2),
        ("decennials", 1),
    ):
        count = timing_techniques.count(technique)
        if count < minimum:
            missing.append(f"{technique} {count}/{minimum}")
    if not missing:
        return []
    return [
        ReadingViolation(
            "missing_evidence_coverage",
            "The premium chart is missing required comprehensive evidence layers.",
            ", ".join(missing),
        )
    ]


def _append_evidence_notes(markdown: str, packet: Mapping[str, Any]) -> str:
    """Attach a compact, source-grouped audit trail without repeating boilerplate."""
    body = markdown.strip()
    if body.endswith(REPORT_NOTICE):
        body = body[: -len(REPORT_NOTICE)].rstrip()
    notes = ["## Evidence Notes", ""]
    grouped: dict[tuple[str, str, str, str], list[str]] = defaultdict(list)
    for item in packet.get("evidence", []):
        if not isinstance(item, Mapping):
            continue
        key = (
            str(item.get("authority")),
            str(item.get("verification_status")),
            str(item.get("interpretive_limit")),
            str(item.get("source_rule_id")),
        )
        grouped[key].append(str(item.get("id")))
    for (authority, status, limit, _rule_id), ids in grouped.items():
        identifier = ", ".join(f"[{item_id}]" for item_id in ids)
        notes.append(
            f"- **{identifier} {authority}** - "
            f"{status.replace('_', ' ')}. {limit}"
        )
    # The full notice already opens the report and the PDF repeats the
    # historical-edition footer. Repeating it after the evidence ledger can
    # create a one-paragraph orphan page in long reports.
    return f"{body}\n\n" + "\n\n".join(notes)


def compose_customer_reading(
    chart_data: Mapping[str, Any],
    *,
    llm_request: Callable[..., str | None] | None = None,
    model: str | None = None,
    require_comprehensive: bool = False,
    scope: str = "full",
) -> tuple[str, dict[str, Any]]:
    """Compose and validate a customer report.

    With no ``llm_request`` the deterministic draft is returned.  When an editor
    is supplied, its output replaces the draft only after evidence and publication
    validation.  Invalid model output never silently falls back and ship as paid
    prose; it raises for retry or owner review.

    ``scope="full"`` is the paid report (Present Chapter and time lords).
    ``scope="natal"`` is the free edition: character and life so far, no future.
    """
    scope = _normalize_reading_scope(scope)
    natal = scope == "natal"
    draft, packet = compose_deterministic_draft(chart_data, scope=scope)
    if require_comprehensive and not natal:
        coverage_violations = _coverage_violations(packet)
        if coverage_violations:
            raise ReadingContractError(coverage_violations)
    final = draft
    if llm_request is not None:
        user_prompt = (
            "Edit the deterministic draft using only the evidence packet.\n\n"
            f"EVIDENCE PACKET:\n{json.dumps(packet, ensure_ascii=False, indent=2)}\n\n"
            f"DETERMINISTIC DRAFT:\n{draft}"
        )
        editor_prompt = NATAL_EDITOR_SYSTEM_PROMPT if natal else EDITOR_SYSTEM_PROMPT
        response = llm_request(
            messages=[
                {"role": "system", "content": editor_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            max_tokens=8_000 if natal else 14_000,
            top_p=0.8,
            model=model,
        )
        if not response or response.startswith(("Error:", "Oracle Communication Error")):
            raise RuntimeError(f"Reading editor failed: {response or 'empty response'}")
        final = response.strip()

    final = _append_evidence_notes(final, packet)
    allowed_ids = {str(item["id"]) for item in packet["evidence"]}
    citation_violations = _citation_violations(final, allowed_ids)
    if citation_violations:
        raise ReadingContractError(citation_violations)
    if natal:
        minimum_words = 900 if llm_request is None else 1_200
    else:
        minimum_words = 900 if llm_request is None else 1_200
    enforce_customer_reading(final, minimum_words=minimum_words, scope=scope)
    return final, packet
