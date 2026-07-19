"""Build a chart-specific hierarchy for the premium reading composer.

The evidence packet is intentionally exhaustive.  A readable judgment needs a
second representation that answers a different question: which testimonies
govern the biography, which ones merely qualify it, and where do several
apparently separate topics belong to one configuration?  This module performs
that ranking without adding astrological facts that are absent from the packet.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Mapping


PLANET_ORDER = {
    "Sun": 0,
    "Moon": 1,
    "Mercury": 2,
    "Venus": 3,
    "Mars": 4,
    "Jupiter": 5,
    "Saturn": 6,
}

ANGULAR_HOUSES = {1, 4, 7, 10}
SUCCEDENT_HOUSES = {2, 5, 8, 11}
HARD_ASPECTS = {"Conjunction", "Square", "Opposition"}


@dataclass(frozen=True)
class RankedPlanet:
    name: str
    score: float
    house: int
    condition: str
    evidence_id: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class PressureNetwork:
    planets: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    hubs: tuple[str, ...]
    houses: tuple[int, ...]
    edge_count: int


@dataclass(frozen=True)
class ActiveRuler:
    name: str
    repetitions: int
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True)
class JudgmentPlan:
    subject: str
    sect: str
    helm_ruler: str | None
    public_ruler: str | None
    ranked_planets: tuple[RankedPlanet, ...]
    final_dispositor: str | None
    final_dispositor_count: int
    final_dispositor_evidence_id: str | None
    pressure_network: PressureNetwork | None
    active_rulers: tuple[ActiveRuler, ...]
    lights_share_house: bool
    lights_house: int | None

    @property
    def strongest_planet(self) -> RankedPlanet | None:
        return self.ranked_planets[0] if self.ranked_planets else None


def _evidence(packet: Mapping[str, Any], category: str) -> list[Mapping[str, Any]]:
    return [
        item
        for item in packet.get("evidence", [])
        if isinstance(item, Mapping) and item.get("category") == category
    ]


def _condition(details: Mapping[str, Any]) -> str:
    dignity = str(details.get("dignities") or "").lower()
    if "domicile" in dignity or "exaltation" in dignity:
        return "strong"
    if "fall" in dignity or "detriment" in dignity:
        return "debilitated"
    if "no recorded" in dignity or "peregrine" in dignity:
        return "unsupported"
    return "mixed"


def _planet_rank(
    name: str,
    details: Mapping[str, Any],
    *,
    helm_ruler: str | None,
    public_ruler: str | None,
    joy_planets: set[str],
) -> tuple[float, tuple[str, ...]]:
    condition = _condition(details)
    condition_score = {
        "strong": 7.0,
        "mixed": 2.0,
        "unsupported": -1.0,
        "debilitated": -5.0,
    }[condition]
    reasons = [{
        "strong": "essentially strong",
        "mixed": "mixed in essential condition",
        "unsupported": "without essential support",
        "debilitated": "essentially debilitated",
    }[condition]]
    house = int(details.get("house") or 0)
    if house in ANGULAR_HOUSES:
        condition_score += 4.0
        reasons.append("angular placement")
    elif house in SUCCEDENT_HOUSES:
        condition_score += 1.0
        reasons.append("succedent placement")
    elif house:
        condition_score -= 2.0
        reasons.append("cadent placement")
    if name == helm_ruler:
        condition_score += 4.0
        reasons.append("rules the Ascendant")
    if name == public_ruler:
        condition_score += 3.0
        reasons.append("rules the tenth place")
    if name in joy_planets:
        condition_score += 1.0
        reasons.append("occupies its planetary joy")
    if bool(details.get("retrograde")):
        condition_score -= 1.0
        reasons.append("retrograde")
    maltreatments = details.get("maltreatments")
    if isinstance(maltreatments, list) and maltreatments:
        condition_score -= min(3.0, float(len(maltreatments)))
        reasons.append(f"{len(maltreatments)} recorded maltreatment condition(s)")
    return condition_score, tuple(reasons)


def _build_pressure_network(
    aspects: list[Mapping[str, Any]],
    planet_houses: Mapping[str, int],
) -> PressureNetwork | None:
    adjacency: dict[str, set[str]] = defaultdict(set)
    edge_ids: dict[frozenset[str], str] = {}
    for item in aspects:
        details = item.get("details", {})
        if not isinstance(details, Mapping) or details.get("type") not in HARD_ASPECTS:
            continue
        first = str(details.get("planet_a") or "")
        second = str(details.get("planet_b") or "")
        if first not in PLANET_ORDER or second not in PLANET_ORDER or first == second:
            continue
        adjacency[first].add(second)
        adjacency[second].add(first)
        edge_ids[frozenset((first, second))] = str(item.get("id") or "")
    if not adjacency:
        return None

    components: list[set[str]] = []
    unseen = set(adjacency)
    while unseen:
        seed = min(unseen, key=lambda name: PLANET_ORDER[name])
        stack = [seed]
        component: set[str] = set()
        while stack:
            current = stack.pop()
            if current in component:
                continue
            component.add(current)
            stack.extend(adjacency[current] - component)
        unseen -= component
        components.append(component)

    component = max(
        components,
        key=lambda names: (
            sum(len(adjacency[name] & names) for name in names) // 2,
            len(names),
        ),
    )
    if len(component) < 2:
        return None
    degrees = {name: len(adjacency[name] & component) for name in component}
    maximum = max(degrees.values())
    hubs = tuple(
        sorted(
            (name for name, degree in degrees.items() if degree == maximum),
            key=lambda name: PLANET_ORDER[name],
        )
    )
    ids = []
    for pair, evidence_id in edge_ids.items():
        if pair.issubset(component) and evidence_id:
            ids.append(evidence_id)
    houses = tuple(sorted({planet_houses[name] for name in component if planet_houses.get(name)}))
    return PressureNetwork(
        planets=tuple(sorted(component, key=lambda name: PLANET_ORDER[name])),
        evidence_ids=tuple(dict.fromkeys(ids)),
        hubs=hubs,
        houses=houses,
        edge_count=sum(degrees.values()) // 2,
    )


def build_judgment_plan(packet: Mapping[str, Any]) -> JudgmentPlan:
    """Return a deterministic hierarchy derived only from admitted evidence."""
    topical = _evidence(packet, "topical")
    house_map = {
        int(item.get("details", {}).get("house")): item
        for item in topical
        if isinstance(item.get("details"), Mapping)
        and isinstance(item.get("details", {}).get("house"), int)
    }
    first = house_map.get(1, {}).get("details", {})
    tenth = house_map.get(10, {}).get("details", {})
    helm_ruler = str(first.get("ruler")) if isinstance(first, Mapping) and first.get("ruler") else None
    public_ruler = str(tenth.get("ruler")) if isinstance(tenth, Mapping) and tenth.get("ruler") else None

    joy_planets = {
        str(item.get("details", {}).get("name"))
        for item in _evidence(packet, "planetary_joy")
        if isinstance(item.get("details"), Mapping)
    }
    planets = _evidence(packet, "planetary_condition")
    planet_houses: dict[str, int] = {}
    ranked: list[RankedPlanet] = []
    for item in planets:
        details = item.get("details", {})
        if not isinstance(details, Mapping):
            continue
        name = str(details.get("name") or "")
        if name not in PLANET_ORDER:
            continue
        house = int(details.get("house") or 0)
        planet_houses[name] = house
        score, reasons = _planet_rank(
            name,
            details,
            helm_ruler=helm_ruler,
            public_ruler=public_ruler,
            joy_planets=joy_planets,
        )
        ranked.append(
            RankedPlanet(
                name=name,
                score=score,
                house=house,
                condition=_condition(details),
                evidence_id=str(item.get("id") or ""),
                reasons=reasons,
            )
        )
    ranked.sort(key=lambda row: (-row.score, PLANET_ORDER[row.name]))

    final_dispositor = None
    final_dispositor_count = 0
    final_dispositor_evidence_id = None
    dispositors = _evidence(packet, "dispositor_network")
    if dispositors:
        item = dispositors[0]
        counts: dict[str, int] = defaultdict(int)
        for row in item.get("details", {}).get("chains", []):
            if isinstance(row, Mapping) and isinstance(row.get("chain"), list) and row["chain"]:
                endpoint = str(row["chain"][-1])
                if endpoint in PLANET_ORDER:
                    counts[endpoint] += 1
        if counts:
            final_dispositor, final_dispositor_count = max(
                counts.items(), key=lambda pair: (pair[1], -PLANET_ORDER[pair[0]])
            )
            final_dispositor_evidence_id = str(item.get("id") or "")

    pressure_network = _build_pressure_network(
        _evidence(packet, "aspect"),
        planet_houses,
    )

    ruler_counts: dict[str, int] = defaultdict(int)
    ruler_ids: dict[str, list[str]] = defaultdict(list)
    sign_rulers = {
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
    for item in _evidence(packet, "timing"):
        details = item.get("details", {})
        if not isinstance(details, Mapping):
            continue
        active = [str(value) for value in details.get("rulers", []) if value]
        active.extend(
            sign_rulers[str(sign)]
            for sign in details.get("levels", [])
            if str(sign) in sign_rulers
        )
        for name in active:
            if name not in PLANET_ORDER:
                continue
            ruler_counts[name] += 1
            evidence_id = str(item.get("id") or "")
            if evidence_id:
                ruler_ids[name].append(evidence_id)
    active_rulers = tuple(
        ActiveRuler(name, count, tuple(dict.fromkeys(ruler_ids[name])))
        for name, count in sorted(
            ruler_counts.items(),
            key=lambda pair: (-pair[1], PLANET_ORDER[pair[0]]),
        )
    )

    sun_house = planet_houses.get("Sun")
    moon_house = planet_houses.get("Moon")
    foundation = _evidence(packet, "foundation")
    sect_fact = str(foundation[0].get("fact", "")) if foundation else ""
    sect = "Day" if "DAY" in sect_fact.upper() else "Night" if "NIGHT" in sect_fact.upper() else "Unknown"
    return JudgmentPlan(
        subject=str(packet.get("subject") or "the native"),
        sect=sect,
        helm_ruler=helm_ruler,
        public_ruler=public_ruler,
        ranked_planets=tuple(ranked),
        final_dispositor=final_dispositor,
        final_dispositor_count=final_dispositor_count,
        final_dispositor_evidence_id=final_dispositor_evidence_id,
        pressure_network=pressure_network,
        active_rulers=active_rulers,
        lights_share_house=sun_house is not None and sun_house == moon_house,
        lights_house=sun_house if sun_house is not None and sun_house == moon_house else None,
    )
