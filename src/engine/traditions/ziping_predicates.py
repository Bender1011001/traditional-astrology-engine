"""Ziping chart predicates: the judgments the delineation rules actually need.

The delineation pack's conditions ask questions like "is the Killing seasonally
strong", "is the Officer damaged or clashed", "is a Ten God rooted". None of
that is exotic - it is all derivable from the validated kernel's own tables
(stem elements, hidden stems, seasonal command states, the clash list) plus the
generation/control cycle. This module derives it.

One honesty rule governs everything here: where a classical term is broader
than the arithmetic used for it, the function returns the arithmetic AND the
operationalization as text, and the report prints both. "Damaged" in the
sources can mean more than "its root branch is clashed or its controller is
present"; the reader is told which reading was computed rather than being left
to assume the richer one.
"""

from __future__ import annotations

from typing import Any

from ..multitradition.bazi import (
    ELEMENT_CYCLE,
    HIDDEN_STEMS,
    LIU_HE,
    STEM_ELEMENT,
    seasonal_state,
    ten_god,
)

ALL_STEMS = list(STEM_ELEMENT)
STRONG_STATES = ("wang", "xiang")  # in command / assisting: the "timely" pair

# The four earth branches store the residual qi of a phase. Derived from the
# kernel's own HIDDEN_STEMS table rather than restated: the storage element IS
# the residual hidden stem's element.
STORAGE_BRANCHES = ("chen", "xu", "chou", "wei")


def element_playing(role: str, day_stem: str) -> str | None:
    """Which element plays a Ten-God role for this Day Master.

    Found by asking the kernel's own ten_god() for every stem rather than by a
    private table, so it cannot drift from the validated relation.
    """
    for stem in ALL_STEMS:
        key, _label = ten_god(day_stem, stem)
        if key == role:
            return STEM_ELEMENT[stem][0]  # (element, polarity) tuple
    return None


def generates(a: str, b: str) -> bool:
    """Five-phase production: does element a generate element b?"""
    return ELEMENT_CYCLE[(ELEMENT_CYCLE.index(a) + 1) % 5] == b


def controls(a: str, b: str) -> bool:
    """Five-phase control: does element a control element b?"""
    return ELEMENT_CYCLE[(ELEMENT_CYCLE.index(a) + 2) % 5] == b



def _stem_id(roman: str) -> str:
    """Kernel stem id from a display romanization ('wu' -> 'wu_stem')."""
    return "wu_stem" if roman == "wu" else roman


def _branch_id(roman: str) -> str:
    """Kernel branch id from a display romanization ('wu' -> 'wu_branch')."""
    if roman == "wu":
        return "wu_branch"
    if roman == "yin":
        return "yin_branch"
    return roman


class ZipingChart:
    """Predicate layer over one chart's computed facts."""

    def __init__(self, facts: dict[str, Any]):
        self.facts = facts
        self.day_stem: str = facts["day_master"]["stem"]
        self.day_element: str = facts["day_master"]["element"]
        self.month_branch: str = facts["pillars"]["month"]["branch"]
        self.pillars: dict[str, dict] = facts["pillars"]
        self.hidden: dict[str, list[dict]] = facts.get("hidden_stems") or {}

    # -- inventory ----------------------------------------------------------

    def natal_branches(self) -> list[str]:
        return [p["branch"] for p in self.pillars.values() if p.get("branch")]

    def visible_ten_gods(self) -> set[str]:
        """Ten-God keys of the visible year/month/hour stems."""
        out: set[str] = set()
        for pillar in ("year", "month", "hour"):
            stem = (self.pillars.get(pillar) or {}).get("stem")
            if stem:
                key, _ = ten_god(self.day_stem, stem)
                out.add(key)
        return out

    def hidden_ten_gods(self) -> set[str]:
        out: set[str] = set()
        for stems in self.hidden.values():
            for s in stems:
                key, _ = ten_god(self.day_stem, s["stem"])
                out.add(key)
        return out

    def present(self, role: str) -> bool:
        return role in (self.visible_ten_gods() | self.hidden_ten_gods())

    def visible(self, role: str) -> bool:
        return role in self.visible_ten_gods()

    # -- rootedness ---------------------------------------------------------

    def roots_of(self, role: str) -> list[str]:
        """Pillars whose BRANCH hides a stem playing this role."""
        found = []
        for pillar, stems in self.hidden.items():
            for s in stems:
                key, _ = ten_god(self.day_stem, s["stem"])
                if key == role:
                    found.append(pillar)
                    break
        return found

    def rooted(self, role: str) -> bool:
        return bool(self.roots_of(role))

    def hour_branch_roots_of_day_master(self) -> int:
        """How many hour-branch hidden stems share the Day Master's element."""
        return sum(
            1 for s in self.hidden.get("hour", [])
            if s.get("element") == self.day_element
        )

    # -- seasonal strength --------------------------------------------------

    def state_of_element(self, element: str) -> str:
        return seasonal_state(element, self.month_branch)

    def seasonally_strong(self, role: str) -> tuple[bool, str]:
        element = element_playing(role, self.day_stem)
        if element is None:
            return False, f"no element plays {role} for {self.day_stem}"
        state = self.state_of_element(element)
        token = state.split()[0]
        return token in STRONG_STATES, f"{role} is {element}, state {state}"

    def day_master_strong(self) -> tuple[bool, str]:
        """The pack's own note points at the engine's month_command for this."""
        mc = self.facts.get("month_command") or {}
        assessment = str(mc.get("support_assessment", ""))
        state = str(mc.get("day_master_state", ""))
        token = state.split()[0] if state else ""
        strong = assessment.startswith("supported") or token in STRONG_STATES
        return strong, f"month command: {assessment or state}"

    def phase_direction(self) -> tuple[str, str]:
        """Advancing (coming into season) or retreating (leaving it).

        The season cycle runs with ELEMENT_CYCLE. The Day Master's element is
        advancing if it commands the NEXT season, retreating if it commanded
        the previous one, otherwise neither.
        """
        season = seasonal_state(self.day_element, self.month_branch)
        # xiang = the season generates it = it commands next season = advancing
        # xiu   = it generated the season = it commanded last season = retreating
        token = season.split()[0]
        if token == "xiang":
            return "advancing", f"day master {self.day_element} is {season}"
        if token == "xiu":
            return "retreating", f"day master {self.day_element} is {season}"
        return "neither", f"day master {self.day_element} is {season}"

    # -- damage and clash ---------------------------------------------------

    def clashed_pillars(self) -> set[str]:
        rel = self.facts.get("branch_relations") or {}
        out: set[str] = set()
        for clash in rel.get("six_clashes") or []:
            out.update(clash.get("pillars") or [])
        return out

    def damaged_or_clashed(self, role: str) -> tuple[bool, str]:
        """Operationalized damage: root branch clashed, or controller present.

        The sources' 'damaged' is broader; this is the computable core of it,
        and the operationalization is returned as text for the report.
        """
        roots = self.roots_of(role)
        clashed = sorted(set(roots) & self.clashed_pillars())
        element = element_playing(role, self.day_stem)
        controller_present = False
        controller_desc = ""
        if element:
            for other in self.visible_ten_gods() | self.hidden_ten_gods():
                other_element = element_playing(other, self.day_stem)
                if other_element and controls(other_element, element):
                    controller_present = True
                    controller_desc = f"{other} ({other_element}) controls it"
                    break
        damaged = bool(clashed) or controller_present
        parts = []
        if clashed:
            parts.append(f"root branch clashed ({', '.join(clashed)} pillar)")
        if controller_present:
            parts.append(controller_desc)
        return damaged, (
            "; ".join(parts) if parts
            else "no root clash and no controlling Ten God present"
        )

    def month_branch_clashed(self) -> bool:
        return "month" in self.clashed_pillars()

    def clash_proportional_case(self) -> tuple[bool, str]:
        """One branch of a clash pair twice or more, its opposite exactly once."""
        from ..multitradition.bazi import LIU_CHONG

        counts: dict[str, int] = {}
        for b in self.natal_branches():
            counts[b] = counts.get(b, 0) + 1
        for a, b in LIU_CHONG:
            if counts.get(a, 0) >= 2 and counts.get(b, 0) == 1:
                return True, f"{a} x{counts[a]} against single {b}"
            if counts.get(b, 0) >= 2 and counts.get(a, 0) == 1:
                return True, f"{b} x{counts[b]} against single {a}"
        return False, "no clash pair has the 2-against-1 shape"

    # -- storage ------------------------------------------------------------

    def storage_holdings(self) -> list[dict[str, str]]:
        """Wealth or Officer sitting as residual qi in a storage branch."""
        out = []
        for pillar, p in self.pillars.items():
            branch = p.get("branch")
            if branch not in STORAGE_BRANCHES:
                continue
            for s in self.hidden.get(pillar, []):
                if s.get("qi") != "residual":
                    continue
                key, label = ten_god(self.day_stem, s["stem"])
                if key in ("zheng_cai", "pian_cai", "zheng_guan"):
                    out.append({
                        "pillar": pillar, "branch": branch,
                        "role": key, "label": label,
                    })
        return out

    # -- luck pillars -------------------------------------------------------

    def luck_pillar_branches(self) -> dict[str, list[str]]:
        """Romanized branch of each luck pillar, per direction."""
        out: dict[str, list[str]] = {}
        lp = self.facts.get("luck_pillars") or {}
        for direction, seq in (lp.get("sequences") or {}).items():
            branches = []
            for row in seq:
                parts = row.get("label", "").split()
                # "丁 Ding 酉 You" -> roman branch is the 4th token
                if len(parts) >= 4:
                    branches.append(_branch_id(parts[3].lower()))
            out[direction] = branches
        return out

    def luck_harmony_with_natal(self) -> tuple[bool, str]:
        """Does any luck-pillar branch form a liu he with a natal branch?"""
        natal = set(self.natal_branches())
        pairs = {frozenset(p) for p in LIU_HE}
        for direction, branches in self.luck_pillar_branches().items():
            for lb in branches:
                for nb in natal:
                    if frozenset((lb, nb)) in pairs:
                        return True, (
                            f"luck branch {lb} harmonizes natal {nb} "
                            f"({direction} sequence)"
                        )
        return False, "no luck-pillar branch harmonizes a natal branch"

    def first_luck_pillar_roles(self) -> dict[str, tuple[str, str]]:
        """(ten_god_key, seasonal state of its element) of the first pillar."""
        out: dict[str, tuple[str, str]] = {}
        lp = self.facts.get("luck_pillars") or {}
        for direction, seq in (lp.get("sequences") or {}).items():
            if not seq:
                continue
            parts = seq[0].get("label", "").split()
            if len(parts) < 2:
                continue
            key, _ = ten_god(self.day_stem, _stem_id(parts[1].lower()))
            element = element_playing(key, self.day_stem)
            state = self.state_of_element(element) if element else "?"
            out[direction] = (key, state)
        return out

    def luck_ten_gods(self) -> dict[str, set[str]]:
        out: dict[str, set[str]] = {}
        lp = self.facts.get("luck_pillars") or {}
        for direction, seq in (lp.get("sequences") or {}).items():
            gods: set[str] = set()
            for row in seq:
                parts = row.get("label", "").split()
                if len(parts) >= 2:
                    key, _ = ten_god(self.day_stem, _stem_id(parts[1].lower()))
                    gods.add(key)
            out[direction] = gods
        return out


__all__ = [
    "ZipingChart",
    "element_playing",
    "generates",
    "controls",
    "HIDDEN_STEMS",
    "STORAGE_BRANCHES",
]
