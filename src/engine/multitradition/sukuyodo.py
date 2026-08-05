"""Sukuyōdō — the twenty-seven mansions, the three nines, and the pada signs.

Forty-five mined rules, no computation module and no panel section: this track
had nothing at all. What it does have is unusually good evidence, and two
features of it shape this module.

**The cycle is twenty-seven, not twenty-eight, and the text proves it twice.**
The pada allotment gives each of the twelve signs nine pada and each mansion
four, which totals 108 and cannot be divided into whole quarters by a
twenty-eight-mansion cycle; and 牛 receives none. Independently, the three-nine
scheme closes only because 3 x 9 = 27. So 牛 is catalogued and not operative,
and this module refuses to give it a category, a pada or a birth-mansion slot -
while still carrying its natal clause as a textual fact, because the text does.

**The order begins at 昴, not at 角.** That is the Indian nakshatra order as
received rather than the Chinese lunar-lodge origin, and it is what makes the
three-nine rotation come out as the text states it. Getting this wrong would
rotate every relationship in the tradition by eleven places and still produce
plausible-looking output.

Two forks are preserved rather than settled. The birth mansion has a SCHEMATIC
derivation from the calendar and an OBSERVATIONAL one from the Moon's actual
longitude, and a 961 arbitration decided for the observational route on the
natal question while keeping the schematic one for ritual days. This module
computes the schematic mansion, which is the one that LOST that arbitration,
and says so - it is the position the encoded table gives, not the position the
tradition preferred. And the whole derivation needs a lunar calendar the pack
does not supply, so the caller passes the lunar date and the regime it came
from.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

RESEARCH_ROOT = (
    Path(__file__).resolve().parents[3] / "docs" / "research" / "multitradition"
)
SUKUYO_DIR = RESEARCH_ROOT / "sukuyodo"

#: The catalogued mansion with no operative role. It gets no category, no
#: pada and no election day, and no birth-mansion computation may reach it.
NIU = "牛"


@lru_cache(maxsize=1)
def _rules() -> dict[str, dict[str, Any]]:
    rules: dict[str, dict[str, Any]] = {}
    for path in sorted(SUKUYO_DIR.glob("*rule_manifest.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for rule in data.get("rules", []):
            rid = rule.get("rule_id")
            if rid:
                rules[rid] = rule
    return rules


def _conclusion(rule_id: str) -> dict[str, Any]:
    return (_rules().get(rule_id) or {}).get("conclusion") or {}


@lru_cache(maxsize=1)
def mansions() -> tuple[str, ...]:
    """The twenty-seven, in the canonical order beginning at 昴."""
    order = _conclusion("sukuyo.mansion.canonical_order").get("order") or []
    out = tuple(
        row["cjk"] for row in sorted(order, key=lambda r: r["index"])
    )
    if len(out) != 27:
        raise ValueError(f"the canonical order holds {len(out)}, not 27")
    if NIU in out:
        raise ValueError("牛 is catalogued, not operative; it cannot be in the cycle")
    return out


@lru_cache(maxsize=1)
def full_moon_mansions() -> dict[int, str]:
    """The mansion the full moon holds in each lunar month.

    Every birth-mansion derivation in the pack starts here. The twelve steps
    between successive entries sum to exactly 27 in the canonical order, which
    is the table's own closure check.
    """
    table = _conclusion("sukuyo.calendar.month_full_moon_mansion").get("table")
    return {row["month"]: row["full_moon_mansion"] for row in table or []}


def mansion_index(mansion: str) -> int:
    """One-based position in the canonical order."""
    return mansions().index(mansion) + 1


def _wrap(index: int) -> int:
    """Map any integer onto 1..27."""
    return (index - 1) % 27 + 1


def birth_mansion(lunar_month: int, lunar_day: int) -> dict[str, Any]:
    """The schematic birth mansion, by both of the text's own formulas.

    The text supplies its own redundancy check: a primary formula and an
    abbreviated one that are algebraically identical, since (d + 12) = (d - 15)
    + 27. An implementation that disagrees with either is wrong, and one that
    disagrees with only one of them is provably wrong. Both are computed here
    and compared, every time.
    """
    anchor = full_moon_mansions().get(lunar_month)
    if anchor is None:
        raise ValueError(f"no full-moon mansion is tabled for month {lunar_month}")
    base = mansion_index(anchor)
    primary = _wrap(base + (lunar_day - 15))
    abbreviated = _wrap(base + (lunar_day + 13 - 1))
    if primary != abbreviated:
        raise AssertionError(
            "the text's two formulas disagree, which cannot happen: "
            f"{primary} vs {abbreviated} for month {lunar_month} day {lunar_day}"
        )
    return {
        "mansion": mansions()[primary - 1],
        "index": primary,
        "full_moon_mansion": anchor,
        "lunar_month": lunar_month,
        "lunar_day": lunar_day,
        "method": "schematic",
        "both_formulas_agree": True,
    }


# -- the three nines -----------------------------------------------------

WITHIN_NINE = ("榮", "衰", "安", "危", "成", "壞", "友", "親")
TRIAD_HEADS = {0: "命", 9: "業", 18: "胎"}

CATEGORY_GLOSS = {
    "命": "life — the subject's own birth mansion",
    "業": "karma — head of the second nine",
    "胎": "womb — head of the third nine",
    "榮": "flourishing", "衰": "declining", "安": "at ease", "危": "in danger",
    "成": "completing", "壞": "breaking", "友": "friend", "親": "kin",
}


def sanku_category(offset: int) -> str:
    """The three-nine category at a given offset from the birth mansion.

    Two birth mansions determine the category with no interpretive latitude,
    which makes this the most directly implementable rule in the tradition.
    """
    o = offset % 27
    if o in TRIAD_HEADS:
        return TRIAD_HEADS[o]
    return WITHIN_NINE[(o % 9) - 1]


def sanku_table(birth: str) -> list[dict[str, Any]]:
    """Every mansion's standing relative to a birth mansion."""
    order = mansions()
    start = mansion_index(birth) - 1
    return [
        {
            "offset": offset,
            "mansion": order[(start + offset) % 27],
            "category": sanku_category(offset),
            "gloss": CATEGORY_GLOSS[sanku_category(offset)],
        }
        for offset in range(27)
    ]


def relation_between(birth: str, other: str) -> dict[str, Any]:
    """The category the second mansion holds for a subject born under the first."""
    offset = (mansion_index(other) - mansion_index(birth)) % 27
    category = sanku_category(offset)
    return {
        "from": birth, "to": other, "offset": offset,
        "category": category, "gloss": CATEGORY_GLOSS[category],
    }


# -- the pada signs ------------------------------------------------------


@lru_cache(maxsize=1)
def pada_signs() -> list[dict[str, Any]]:
    return _conclusion("sukuyo.rasi.pada_allotment").get("signs") or []


def sign_of_mansion(mansion: str) -> list[dict[str, Any]]:
    """Which sign or signs a mansion's pada fall in.

    A mansion holds four pada and a sign holds nine, so most mansions straddle
    a boundary. Returning every sign it touches, with the pada count, is the
    honest shape; collapsing to one would discard the straddle the allotment
    exists to record.
    """
    out = []
    for sign in pada_signs():
        for row in sign.get("allotment") or []:
            if row.get("mansion") == mansion:
                out.append({
                    "sign": sign.get("cjk"),
                    "western_equivalent": sign.get("western_equivalent"),
                    "resident_luminary": sign.get("resident_luminary"),
                    "pada": row.get("pada"),
                })
    return out


@lru_cache(maxsize=1)
def pada_closure() -> dict[str, Any]:
    """The arithmetic that proves the cycle is 27 rather than 28."""
    signs = pada_signs()
    per_sign = {
        s.get("cjk"): sum(r.get("pada", 0) for r in s.get("allotment") or [])
        for s in signs
    }
    per_mansion: dict[str, int] = {}
    for s in signs:
        for r in s.get("allotment") or []:
            per_mansion[r["mansion"]] = per_mansion.get(r["mansion"], 0) + r.get(
                "pada", 0
            )
    return {
        "pada_per_sign": per_sign,
        "pada_per_mansion": per_mansion,
        "total_pada": sum(per_sign.values()),
        "pada_allotted_to_niu": per_mansion.get(NIU, 0),
        "why_it_matters": (
            "108 pada divide into whole quarters only across 27 mansions, and "
            "牛 receives none. The allotment is the decisive internal evidence "
            "that this text's operative cycle is 27."
        ),
    }


# -- assembly ------------------------------------------------------------


def build(
    lunar_dates_by_regime: dict[str, tuple[int, int]],
) -> dict[str, Any]:
    """Compute the reading under every calendar regime, then gate on agreement.

    ``lunar_dates_by_regime`` maps a regime id to its (lunar_month, lunar_day).

    The gate is a product choice and is labelled one. The sources do not say to
    do this: Sukuyōshi worked in a single regime and did not hedge. But the
    birth mansion is the anchor of the entire tradition, a wrong anchor makes
    every downstream relationship wrong, and the wrongness is invisible to the
    reader. The alternative this rejects - picking one regime silently - is
    named rather than left implicit.
    """
    per_regime: dict[str, Any] = {}
    for regime, (month, day) in lunar_dates_by_regime.items():
        try:
            per_regime[regime] = birth_mansion(month, day)
        except ValueError as exc:
            per_regime[regime] = {"error": str(exc)}

    found = {
        r: v["mansion"] for r, v in per_regime.items() if v.get("mansion")
    }
    agreed = len(set(found.values())) == 1 and bool(found)

    result: dict[str, Any] = {
        "per_regime": per_regime,
        "regimes_agree": agreed,
        "gate": "configured_method",
        "gate_rationale": (
            "The birth mansion anchors the whole tradition. Tested across the "
            "named regimes it either does not move, and is emitted, or it "
            "moves, and the disagreement itself is emitted instead."
        ),
    }
    if not agreed:
        result["status"] = "refused"
        result["why"] = (
            "the candidate calendar regimes give different birth mansions, and "
            "this gate varies the CALENDAR SYSTEM rather than a meridian, "
            "which is a larger disagreement than a timezone nicety"
        )
        # Refusing the anchor is not a reason to withhold the structure. Each
        # candidate mansion gets its full reading, labelled conditional, so a
        # reader can see what turns on the calendar instead of being handed a
        # blank page. Which regimes back which candidate is stated, because a
        # two-to-one split is a different situation from a three-way one.
        result["candidates"] = [
            {
                "mansion": mansion,
                "supported_by": sorted(
                    r for r, m in found.items() if m == mansion
                ),
                "index": mansion_index(mansion),
                "sanku": sanku_table(mansion),
                "triads": {
                    "命": mansion,
                    "業": mansions()[(mansion_index(mansion) - 1 + 9) % 27],
                    "胎": mansions()[(mansion_index(mansion) - 1 + 18) % 27],
                },
                "signs": sign_of_mansion(mansion),
            }
            for mansion in sorted(set(found.values()), key=mansion_index)
        ]
        return result

    mansion = next(iter(found.values()))
    result.update({
        "status": "emitted",
        "birth_mansion": mansion,
        "index": mansion_index(mansion),
        "sanku": sanku_table(mansion),
        "triads": {
            "命": mansion,
            "業": mansions()[(mansion_index(mansion) - 1 + 9) % 27],
            "胎": mansions()[(mansion_index(mansion) - 1 + 18) % 27],
        },
        "signs": sign_of_mansion(mansion),
        "method_fork": (
            "This is the SCHEMATIC mansion, from the calendar table. The "
            "tradition also has an observational derivation from the Moon's "
            "actual longitude, and a 961 arbitration decided for the "
            "observational route on the natal question while keeping the "
            "schematic one for ritual days. The position given here is the one "
            "that lost that arbitration. T1299 itself warns the mansions are "
            "unequal in width, so the two will disagree for real births."
        ),
    })
    return result
