"""Resolve Valens' condition vocabulary against a computed Hellenistic chart.

The Anthologiae's topical chapters (marriage in II.38, foreign travel in
II.29-31) state their conditions in Valens' own technical language: Venus
*chrematizon*, Saturn *epidekateia* to Venus, the lord of the place *under the
beams*.  The rule packs preserve that language verbatim, which means nothing in
those chapters can fire until something translates it into chart geometry.

This module is that translation, and it is deliberately tri-valued.  A
condition resolves to True, to False, or to UNKNOWN, and UNKNOWN never collapses
into False.  Valens leans heavily on his distribution/chronocrator system, which
this engine does not yet compute; a rule gated on a distribution must come back
undecided and be *reported* as undecided, not silently judged not to apply.
Collapsing unknown into false is how an engine ends up quietly asserting the
opposite of what the source says.
"""

from __future__ import annotations

from typing import Any

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Valens names the modalities by their seasonal behaviour.  Tropical signs turn
# the season, solid ones hold it, bicorporeal ones hand it over.
MODALITY = {
    "Aries": "tropical", "Cancer": "tropical",
    "Libra": "tropical", "Capricorn": "tropical",
    "Taurus": "solid", "Leo": "solid",
    "Scorpio": "solid", "Aquarius": "solid",
    "Gemini": "bicorporeal", "Virgo": "bicorporeal",
    "Sagittarius": "bicorporeal", "Pisces": "bicorporeal",
}

DOMICILE = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

EXALTATION = {
    "Sun": "Aries", "Moon": "Taurus", "Mercury": "Virgo", "Venus": "Pisces",
    "Mars": "Capricorn", "Jupiter": "Cancer", "Saturn": "Libra",
}

MALEFICS = ("Mars", "Saturn")
BENEFICS = ("Jupiter", "Venus")

ANGLES = (1, 4, 7, 10)
SUCCEDENTS = (2, 5, 8, 11)

#: Sign-distances that count as a configuration (Ptolemaic aspects, whole-sign).
ASPECT_BY_DISTANCE = {
    0: "conjunction", 2: "sextile", 3: "square", 4: "trine", 6: "opposition",
}

#: Sun-proximity in degrees under which a planet is "under the beams".  Valens
#: does not state a figure; 15 degrees is the standard Hellenistic convention.
UNDER_THE_BEAMS_ORB = 15.0

CONFIGURED_METHODS = {
    "chrematizon": (
        "Valens calls a place chrematizon (chi-rho-eta-mu-alpha-tau-iota-zeta"
        "-omega-nu, 'busy' or 'transacting') without ever enumerating which "
        "places qualify. This engine reads it as the angles and succedents "
        "(1, 4, 7, 10, 2, 5, 8, 11), the places from which a planet can act. "
        "The live fork: some readers of Valens restrict the operative places "
        "to 1, 10, 11, 7 and 4, and a stricter reading admits only the angles."
    ),
    "under_the_beams": (
        "Under the beams is taken as within 15 degrees of the Sun in "
        "longitude. Valens states the condition without a figure; the fork is "
        "8.5 degrees (the classical 'in the heart' distinction extended) "
        "through 17 degrees."
    ),
}

UNKNOWN = "unknown"


class _Unknown:
    """Sentinel for a fact this engine cannot decide.

    Deliberately falsy-hostile: it raises on ``bool()`` so that an unknown can
    never be accidentally swallowed by an ``if value:`` somewhere downstream.
    """

    __slots__ = ()

    def __bool__(self) -> bool:  # pragma: no cover - defensive
        raise TypeError(
            "an unknown Valens fact cannot be coerced to a boolean; handle "
            "the undecided case explicitly"
        )

    def __repr__(self) -> str:
        return "UNKNOWN"


UNKNOWN_VALUE = _Unknown()


def _sign_index(sign: str) -> int:
    return SIGNS.index(sign)


def _sign_distance(a: str, b: str) -> int:
    """Whole-sign separation, folded to 0-6 (sign order is symmetric here)."""
    raw = (_sign_index(a) - _sign_index(b)) % 12
    return min(raw, 12 - raw)


class ValensChart:
    """A computed Hellenistic chart, queried in Valens' own vocabulary."""

    def __init__(self, facts: dict[str, Any]) -> None:
        self.facts = facts
        self.sect = facts.get("sect")
        self.by_body: dict[str, dict[str, Any]] = {
            p["body"]: p for p in facts.get("placements", [])
        }
        self.lots = facts.get("hermetic_lots", {}) or {}
        self.used_methods: set[str] = set()

    # -- primitives ------------------------------------------------------

    def longitude(self, body: str) -> float | None:
        p = self.by_body.get(body)
        if not p:
            return None
        return _sign_index(p["sign"]) * 30.0 + float(p["degree_in_sign"])

    def sign(self, body: str) -> str | None:
        p = self.by_body.get(body)
        return p["sign"] if p else None

    def house(self, body: str) -> int | None:
        p = self.by_body.get(body)
        return p.get("whole_sign_house") if p else None

    def aspect(self, a: str, b: str) -> str | None:
        """The whole-sign figure between two bodies, or None if averted."""
        sa, sb = self.sign(a), self.sign(b)
        if not sa or not sb:
            return None
        return ASPECT_BY_DISTANCE.get(_sign_distance(sa, sb))

    def configured(self, a: str, b: str) -> bool | _Unknown:
        """Whether two bodies regard each other at all (Valens: 'testifies')."""
        if a not in self.by_body or b not in self.by_body:
            return UNKNOWN_VALUE
        return self.aspect(a, b) is not None

    def overcomes(self, a: str, b: str) -> bool | _Unknown:
        """A overcomes B: A holds the tenth sign from B (superior square).

        This is Valens' epidekateia, and it is directional - the distinction
        between overcoming and being overcome is the whole point of the
        figure, so this must not be computed from a folded distance.
        """
        sa, sb = self.sign(a), self.sign(b)
        if not sa or not sb:
            return UNKNOWN_VALUE
        return (_sign_index(sa) - _sign_index(sb)) % 12 == 9

    def under_the_beams(self, body: str) -> bool | _Unknown:
        lon, sun = self.longitude(body), self.longitude("Sun")
        if lon is None or sun is None or body == "Sun":
            return UNKNOWN_VALUE
        self.used_methods.add("under_the_beams")
        sep = abs(lon - sun) % 360.0
        return min(sep, 360.0 - sep) <= UNDER_THE_BEAMS_ORB

    def is_chrematizon(self, body: str) -> bool | _Unknown:
        h = self.house(body)
        if h is None:
            return UNKNOWN_VALUE
        self.used_methods.add("chrematizon")
        return h in ANGLES or h in SUCCEDENTS

    def angular(self, body: str) -> bool | _Unknown:
        h = self.house(body)
        return UNKNOWN_VALUE if h is None else h in ANGLES

    def phase(self, body: str) -> str | _Unknown:
        """Oriental (rising before the Sun) or occidental (setting after it)."""
        lon, sun = self.longitude(body), self.longitude("Sun")
        if lon is None or sun is None or body == "Sun":
            return UNKNOWN_VALUE
        return "western/occidental" if (lon - sun) % 360.0 < 180.0 else (
            "eastern/oriental"
        )

    def lord_of(self, body: str) -> str | None:
        s = self.sign(body)
        return DOMICILE.get(s) if s else None

    def in_own_house_or_exaltation(self, body: str) -> bool | _Unknown:
        s = self.sign(body)
        if not s:
            return UNKNOWN_VALUE
        return DOMICILE.get(s) == body or EXALTATION.get(body) == s

    def in_exaltation(self, body: str) -> bool | _Unknown:
        s = self.sign(body)
        return UNKNOWN_VALUE if not s else EXALTATION.get(body) == s

    def lord_condition(self, body: str) -> list[str] | _Unknown:
        """The conditions Valens lists as spoiling a lord of the place."""
        lord = self.lord_of(body)
        if not lord or lord not in self.by_body:
            return UNKNOWN_VALUE
        out: list[str] = []
        beams = self.under_the_beams(lord)
        if isinstance(beams, bool) and beams:
            out.append("under the beams")
        h = self.house(lord)
        if h in (6, 12):
            out.append("in the 6th or 12th")
        for mal in MALEFICS:
            if mal in self.by_body and self.aspect(lord, mal) in (
                "square", "opposition", "conjunction"
            ):
                out.append("afflicted by a corrupter")
                break
        return out

    def in_sign_of(self, body: str, other: str) -> bool | _Unknown:
        """Whether a body sits in a sign that the other body rules."""
        s = self.sign(body)
        return UNKNOWN_VALUE if not s else DOMICILE.get(s) == other

    def bounds_lord(self, body: str) -> str | _Unknown:
        p = self.by_body.get(body)
        if not p:
            return UNKNOWN_VALUE
        return p.get("bound_lord_egyptian") or UNKNOWN_VALUE

    def lots_in_same_sign(self, a: str, b: str) -> bool | _Unknown:
        la, lb = self.lots.get(a), self.lots.get(b)
        if not la or not lb:
            return UNKNOWN_VALUE
        return la.get("sign") == lb.get("sign")

    # -- the Lot of Foreign Travel ---------------------------------------

    def lot_of_travel(self) -> dict[str, Any] | _Unknown:
        """Valens II.29: counted from Saturn to Mars, the same from the Asc.

        He prints one formula and no sect reversal, so none is applied. The
        chapter on travel is unusable without this lot, which is why it is
        computed here rather than left to the panel's Hermetic pair.
        """
        asc = self.facts.get("ascendant") or {}
        if not asc.get("sign"):
            return UNKNOWN_VALUE
        sat, mars = self.longitude("Saturn"), self.longitude("Mars")
        if sat is None or mars is None:
            return UNKNOWN_VALUE
        asc_lon = _sign_index(asc["sign"]) * 30.0 + float(
            asc.get("degree_in_sign", 0.0)
        )
        lon = (asc_lon + (mars - sat)) % 360.0
        idx = int(lon // 30)
        house = ((idx - _sign_index(asc["sign"])) % 12) + 1
        return {
            "sign": SIGNS[idx],
            "degree_in_sign": round(lon % 30.0, 4),
            "whole_sign_house": house,
            "lord": DOMICILE[SIGNS[idx]],
        }

    def lot_sign(self, key: str) -> str | None:
        """The sign of a lot, whether Hermetic or Valens' travel lot."""
        if key == "travel":
            lot = self.lot_of_travel()
            return None if isinstance(lot, _Unknown) else lot["sign"]
        got = self.lots.get(key)
        return got.get("sign") if got else None

    def lot_house(self, key: str) -> int | None:
        if key == "travel":
            lot = self.lot_of_travel()
            return None if isinstance(lot, _Unknown) else lot["whole_sign_house"]
        got = self.lots.get(key)
        return got.get("whole_sign_house") if got else None

    def regards_lot(self, body: str, key: str) -> bool | _Unknown:
        """Whether a body is upon, or configured to, a lot's sign."""
        ls, bs = self.lot_sign(key), self.sign(body)
        if not ls or not bs:
            return UNKNOWN_VALUE
        return _sign_distance(bs, ls) in ASPECT_BY_DISTANCE


# -- the fact vocabulary -------------------------------------------------

_PLANETS = ("Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn")


def _planet_of(token: str) -> str | None:
    t = token.lower()
    for p in _PLANETS:
        if p.lower() == t:
            return p
    return None


def resolve(fact: str, chart: ValensChart) -> Any:
    """Resolve one of Valens' named facts, or return UNKNOWN_VALUE.

    Anything Valens states in terms of his distribution/chronocrator system
    returns UNKNOWN_VALUE by design: this engine does not compute distributions,
    and a rule gated on one must be reported undecided rather than judged.
    """
    parts = fact.split(".")
    head = parts[0]

    if fact == "sect":
        return chart.sect
    if fact == "lot_of_fortune_and_lot_of_daimon":
        same = chart.lots_in_same_sign("fortune", "spirit")
        if isinstance(same, _Unknown):
            return same
        return "in one and the same sign" if same else "in different signs"

    # -- the travel chapter's own vocabulary -----------------------------

    if fact == "lot_computed":
        # This engine computes Valens' travel lot from his own formula, so the
        # chapter's framing condition is satisfied.
        return "lot_of_foreign_travel"
    if fact == "lot_of_travel":
        h = chart.lot_house("travel")
        if h is None:
            return UNKNOWN_VALUE
        return {1: ["Ascendant"], 10: ["Midheaven"],
                11: ["succedent of the Midheaven"]}.get(h, [])
    if fact == "mars_upon_or_regarding_lot_of_travel":
        return chart.regards_lot("Mars", "travel")
    if fact == "lord_of_fortune_in_lot_or_place_of_travel":
        lord = (chart.lots.get("fortune") or {}).get("lord")
        travel = chart.lot_sign("travel")
        if not lord or not travel:
            return UNKNOWN_VALUE
        return chart.sign(lord) == travel
    if fact == "lot_of_fortune_and_lot_of_travel_together_in_the_subterranean_angle":
        f, t = chart.lot_house("fortune"), chart.lot_house("travel")
        if f is None or t is None:
            return UNKNOWN_VALUE
        return f == 4 and t == 4
    if fact == "lot_of_fortune_and_lot_of_travel_have_malefics_upon_or_opposite":
        f, t = chart.lot_sign("fortune"), chart.lot_sign("travel")
        if not f or not t:
            return UNKNOWN_VALUE
        for mal in MALEFICS:
            ms = chart.sign(mal)
            if ms and any(
                _sign_distance(ms, lot) in (0, 6) for lot in (f, t)
            ):
                return True
        return False
    if fact == "benefics_upon_the_lots":
        signs = [
            s for s in (chart.lot_sign("fortune"), chart.lot_sign("spirit"),
                        chart.lot_sign("travel")) if s
        ]
        if not signs:
            return UNKNOWN_VALUE
        return any(chart.sign(b) in signs for b in BENEFICS)
    if fact == "most_planets_in_the_subterranean_hemisphere":
        houses = [
            chart.house(b) for b in _PLANETS if chart.house(b) is not None
        ]
        if len(houses) < 7:
            return UNKNOWN_VALUE
        return sum(1 for h in houses if 1 <= h <= 6) > len(houses) / 2
    if fact == "lights":
        hs = [chart.house("Sun"), chart.house("Moon")]
        if any(h is None for h in hs):
            return UNKNOWN_VALUE
        return "setting" if all(h == 7 for h in hs) else "not setting"
    if fact == "mars":
        # Both printed values turn on whether Mars is averted from the travel
        # lot and whether he rules it.
        regards = chart.regards_lot("Mars", "travel")
        travel = chart.lot_sign("travel")
        if isinstance(regards, _Unknown) or not travel:
            return UNKNOWN_VALUE
        rules = DOMICILE.get(travel) == "Mars"
        if not regards and not rules:
            return (
                "averted from the lot or from the place of foreign parts and "
                "lord of neither"
            )
        return "otherwise placed"

    planet = _planet_of(head)
    if planet is None or len(parts) < 2:
        return UNKNOWN_VALUE

    attr = ".".join(parts[1:])

    if attr == "house":
        h = chart.house(planet)
        return UNKNOWN_VALUE if h is None else str(h)
    if attr == "sign_modality":
        s = chart.sign(planet)
        return UNKNOWN_VALUE if not s else MODALITY[s]
    if attr == "is_chrematizon":
        return chart.is_chrematizon(planet)
    if attr == "angular":
        return chart.angular(planet)
    if attr == "phase":
        return chart.phase(planet)
    if attr == "in_exaltation":
        return chart.in_exaltation(planet)
    if attr == "in_own_house_or_exaltation":
        return chart.in_own_house_or_exaltation(planet)
    if attr == "in_own_house":
        return chart.in_sign_of(planet, planet)
    if attr == "bounds_lord":
        return chart.bounds_lord(planet)
    if attr == "lord.condition":
        return chart.lord_condition(planet)
    if attr in ("conjunct", "applies_to"):
        # Valens' "conjunct" here is co-presence in the sign; application
        # requires speeds this fact layer does not carry, so an applying
        # condition is answered only when the two are already co-present.
        out = [
            o for o in _PLANETS
            if o != planet and chart.aspect(planet, o) == "conjunction"
        ]
        return out
    if attr in ("aspects_venus", "opposes_venus", "testifies_to_venus",
                "afflicted_by_saturn", "aspects_or_is_akin_to_venus"):
        other = "Venus" if attr.endswith("venus") else "Saturn"
        subject = planet if attr.endswith("venus") else "Venus"
        asp = chart.aspect(subject if attr.endswith("venus") else planet, other)
        if planet not in chart.by_body or other not in chart.by_body:
            return UNKNOWN_VALUE
        if attr == "opposes_venus":
            return chart.aspect(planet, "Venus") == "opposition"
        if attr == "afflicted_by_saturn":
            return chart.aspect(planet, "Saturn") in (
                "square", "opposition", "conjunction"
            )
        return asp is not None
    if attr == "aspect_to_venus":
        return chart.aspect(planet, "Venus") or "averted"
    if attr in ("testifies", "co_testifies"):
        return UNKNOWN_VALUE  # testifies to *what* is left open by the chapter
    if attr in ("configured_with", "regarded_by", "testified_by",
                "receives_ray_from"):
        return [
            o for o in _PLANETS
            if o != planet and chart.aspect(planet, o) is not None
        ]
    if attr == "placement":
        out = []
        for o in _PLANETS:
            got = chart.in_sign_of(planet, o)
            if isinstance(got, bool) and got:
                out.append(f"{o}'s house")
                out.append(f"{o}'s sign")
        bl = chart.bounds_lord(planet)
        if isinstance(bl, str):
            out.append(f"{bl}'s bounds")
        return out
    if attr == "conjunct_or_ruled_by_or_overcome_by":
        out = []
        for o in _PLANETS:
            if o == planet:
                continue
            ruled = chart.in_sign_of(planet, o)
            over = chart.overcomes(o, planet)
            if chart.aspect(planet, o) == "conjunction" or (
                isinstance(ruled, bool) and ruled
            ) or (isinstance(over, bool) and over):
                out.append(o)
        return out

    return UNKNOWN_VALUE


def _test(cond: dict[str, Any], chart: ValensChart) -> bool | _Unknown:
    got = resolve(cond.get("fact", ""), chart)
    if isinstance(got, _Unknown):
        return UNKNOWN_VALUE
    op, want = cond.get("operator"), cond.get("value")
    if op == "equals":
        if isinstance(got, list):
            return want in got
        return got == want
    if op == "in":
        wants = want if isinstance(want, list) else [want]
        if isinstance(got, list):
            return any(w in got for w in wants)
        return got in wants
    return UNKNOWN_VALUE


def evaluate(rule: dict[str, Any], chart: ValensChart) -> tuple[str, list[str]]:
    """Judge one rule against the chart.

    Returns ``(verdict, undecided_facts)`` where verdict is ``"pass"``,
    ``"fail"`` or ``"unknown"``.  An ``all`` group with one false member fails
    outright even if others are unknown - a condition Valens requires and the
    chart denies is settled.  But an ``all`` group whose members are otherwise
    true and contain an unknown is unknown, never a pass.
    """
    conds = rule.get("conditions") or {}
    undecided: list[str] = []
    verdicts: list[bool | _Unknown] = []
    mode = "all" if "all" in conds else "any"
    for cond in conds.get(mode, []) or []:
        got = _test(cond, chart)
        if isinstance(got, _Unknown):
            undecided.append(cond.get("fact", "?"))
        verdicts.append(got)
    if not verdicts:
        return "unknown", undecided

    settled = [v for v in verdicts if isinstance(v, bool)]
    if mode == "all":
        if any(v is False for v in settled):
            return "fail", undecided
        if len(settled) == len(verdicts):
            return "pass", undecided
        return "unknown", undecided
    if any(v is True for v in settled):
        return "pass", undecided
    if len(settled) == len(verdicts):
        return "fail", undecided
    return "unknown", undecided
