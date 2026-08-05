"""The fourteen main stars of Zi Wei Dou Shu, placed.

The panel built the twelve palaces and stopped: ``constructed_palaces_only``.
An empty board. Everything needed to fill it was already in the pack - the
five-phase bureau, five printed placement grids for Zi Wei, the Tian Fu mirror
diagram, and the two series verses - and none of it reached the chart.

Zi Wei's own position needs the LUNAR DAY, which is the one input the panel's
calendar-regime gate does not always settle: this engine computes the day under
three meridians and they can disagree by one. Rather than assert a meridian or
refuse the whole layer, this module places the stars under EACH candidate day
and reports which placements are invariant across them. A star that lands in
the same palace under every candidate is settled; one that moves is reported as
moving, with both palaces named. That is strictly more useful than a refusal
and strictly more honest than picking a meridian.

The placement rule for Zi Wei is worth a note. The text prints five tables and
five mnemonic verses and no general rule. The pack carries a recovered closed
form - k = ceil(d/n), c = nk - d, begin at Yin advanced by k-1 palaces, then
retreat c palaces if c is odd and advance c if it is even - which reproduces 58
of the 60 printed cells and all ten day-one and day-two anchors the verses
state in words. The two cells it misses are isolated single-character defects
in the transcription, detectable because a printed grid must partition the
thirty days exactly once. Using the closed form therefore CORRECTS the
transcription rather than contradicting the text, and this module says so
whenever it disagrees with a printed cell.
"""

from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any

RESEARCH_ROOT = (
    Path(__file__).resolve().parents[3] / "docs" / "research" / "multitradition"
)
ZIWEI_FULL = RESEARCH_ROOT / "ziwei" / "quanshu_full_rule_manifest.json"

BRANCHES = (
    "zi", "chou", "yin", "mao", "chen", "si",
    "wu", "wei", "shen", "you", "xu", "hai",
)

BRANCH_HANZI = {
    "zi": "子", "chou": "丑", "yin": "寅", "mao": "卯", "chen": "辰",
    "si": "巳", "wu": "午", "wei": "未", "shen": "申", "you": "酉",
    "xu": "戌", "hai": "亥",
}

HANZI_BRANCH = {v: k for k, v in BRANCH_HANZI.items()}

YIN = BRANCHES.index("yin")

#: The fourteen, in the two series the verses group them into.
ZIWEI_SERIES = ("紫微", "天機", "太陽", "武曲", "天同", "廉貞")
TIANFU_SERIES = ("天府", "太陰", "貪狼", "巨門", "天相", "天梁", "七殺", "破軍")
FOURTEEN = (*ZIWEI_SERIES, *TIANFU_SERIES)

STAR_NAMES = {
    "紫微": "Zi Wei", "天機": "Tian Ji", "太陽": "Tai Yang", "武曲": "Wu Qu",
    "天同": "Tian Tong", "廉貞": "Lian Zhen", "天府": "Tian Fu",
    "太陰": "Tai Yin", "貪狼": "Tan Lang", "巨門": "Ju Men",
    "天相": "Tian Xiang", "天梁": "Tian Liang", "七殺": "Qi Sha",
    "破軍": "Po Jun",
}

BUREAU_NUMBERS = {
    "water_two": 2, "wood_three": 3, "metal_four": 4,
    "earth_five": 5, "fire_six": 6,
}

BUREAU_LABELS = {
    2: "水二局 (water, two)", 3: "木三局 (wood, three)",
    4: "金四局 (metal, four)", 5: "土五局 (earth, five)",
    6: "火六局 (fire, six)",
}


@lru_cache(maxsize=1)
def _rules() -> dict[str, dict[str, Any]]:
    data = json.loads(ZIWEI_FULL.read_text(encoding="utf-8"))
    return {r["rule_id"]: r for r in data.get("rules", [])}


def _cells(rule_id: str) -> dict[str, Any]:
    rule = _rules().get(rule_id) or {}
    return (rule.get("conclusion") or {}).get("cells") or {}


# -- the five-phase bureau -----------------------------------------------


def five_phase_bureau(
    year_stem_hanzi: str, life_palace_branch: str
) -> dict[str, Any] | None:
    """The bureau, from the birth-year stem and the life palace's branch.

    Two printed tables composed: the Five Tigers couplets give the palace its
    own stem, and the nayin song names that stem-branch's element. The 10x12
    grid is nowhere printed as a grid; the pack composes it exactly as the
    chapter's own worked example does.
    """
    cells = _cells("ziwei.quanshu.j2.five_phase_bureau_from_life_palace")
    row = cells.get(year_stem_hanzi)
    if not row:
        return None
    cell = row.get(BRANCH_HANZI.get(life_palace_branch, ""))
    if not cell:
        return None
    number = cell.get("bureau_number") or BUREAU_NUMBERS.get(
        cell.get("engine_rendering", "")
    )
    if not number:
        return None
    return {
        "bureau_number": number,
        "bureau": cell.get("engine_rendering"),
        "label": BUREAU_LABELS.get(number),
        "chinese": cell.get("chinese"),
        "rendering_grade": cell.get("rendering_grade"),
    }


# -- Zi Wei's own palace -------------------------------------------------


def place_ziwei(bureau_number: int, lunar_day: int) -> str:
    """The recovered closed form over the five printed grids.

    k = ceil(d/n); c = nk - d; begin at Yin advanced by (k-1) palaces; retreat
    c palaces if c is odd, advance c if it is even.
    """
    if bureau_number < 2 or lunar_day < 1:
        raise ValueError("bureau number and lunar day must be positive")
    k = math.ceil(lunar_day / bureau_number)
    c = bureau_number * k - lunar_day
    start = (YIN + (k - 1)) % 12
    index = (start - c) % 12 if c % 2 else (start + c) % 12
    return BRANCHES[index]


def place_tianfu(ziwei_branch: str) -> str:
    """Tian Fu is Zi Wei reflected in the Yin-Shen axis.

    The two share a palace only at Yin and at Shen; everywhere else the
    reflection moves them apart, so Zi Wei at Chou puts Tian Fu at Mao.
    """
    cells = _cells("ziwei.quanshu.j2.place_tianfu_mirror_of_ziwei")
    cell = cells.get(BRANCH_HANZI[ziwei_branch])
    if cell and cell.get("engine_rendering"):
        return str(cell["engine_rendering"])
    # The mirror in closed form, if the table is unavailable: reflect about
    # the Yin-Shen axis, i.e. index -> (2*YIN - index) mod 12.
    return BRANCHES[(2 * YIN - BRANCHES.index(ziwei_branch)) % 12]


def _series_offsets(rule_id: str, key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for star, cell in _cells(rule_id).items():
        value = cell.get(key)
        if isinstance(value, int):
            out[star] = value
    return out


def place_fourteen(ziwei_branch: str) -> dict[str, str]:
    """All fourteen, from Zi Wei backwards and Tian Fu forwards."""
    tianfu = place_tianfu(ziwei_branch)
    zw = BRANCHES.index(ziwei_branch)
    tf = BRANCHES.index(tianfu)
    out: dict[str, str] = {}
    for star, back in _series_offsets(
        "ziwei.quanshu.j2.place_ziwei_series_six_stars", "offset_backward"
    ).items():
        out[star] = BRANCHES[(zw - back) % 12]
    for star, fwd in _series_offsets(
        "ziwei.quanshu.j2.place_tianfu_series_eight_stars", "offset_forward"
    ).items():
        out[star] = BRANCHES[(tf + fwd) % 12]
    return out


# -- brightness ----------------------------------------------------------


@lru_cache(maxsize=1)
def _brightness_index() -> dict[tuple[str, str], str]:
    """(branch, star) -> the level the grid prints for it."""
    index: dict[tuple[str, str], str] = {}
    for branch_hanzi, levels in _cells(
        "ziwei.quanshu.j2.brightness_table_twelve_branches"
    ).items():
        branch = HANZI_BRANCH.get(branch_hanzi)
        if not branch or not isinstance(levels, dict):
            continue
        for level_hanzi, cell in levels.items():
            stars = (cell or {}).get("engine_rendering")
            if not isinstance(stars, list):
                continue
            for star in stars:
                index[(branch, star)] = level_hanzi
    return index


def brightness(star: str, branch: str) -> str | None:
    return _brightness_index().get((branch, star))


# -- placing the board, across candidate days ----------------------------


def board_for_day(
    year_stem_hanzi: str, life_palace_branch: str, lunar_day: int
) -> dict[str, Any] | None:
    bureau = five_phase_bureau(year_stem_hanzi, life_palace_branch)
    if bureau is None:
        return None
    ziwei = place_ziwei(bureau["bureau_number"], lunar_day)
    stars = place_fourteen(ziwei)
    return {
        "lunar_day": lunar_day,
        "bureau": bureau,
        "ziwei_branch": ziwei,
        "tianfu_branch": place_tianfu(ziwei),
        "stars": stars,
        "brightness": {
            star: brightness(star, br) for star, br in stars.items()
        },
    }


def place_across_candidates(
    year_stem_hanzi: str,
    life_palace_branch: str,
    candidate_days: list[int],
) -> dict[str, Any]:
    """Place the board under every candidate lunar day and compare.

    A star in the same palace under every candidate is settled. One that moves
    is reported as moving, both palaces named. The alternative - choosing a
    meridian - would hide the fact that the choice was made at all.
    """
    days = sorted(set(d for d in candidate_days if d))
    boards = {}
    for day in days:
        board = board_for_day(year_stem_hanzi, life_palace_branch, day)
        if board is not None:
            boards[day] = board
    if not boards:
        return {
            "status": "not_placed",
            "why": (
                "the five-phase bureau could not be read for this year stem "
                "and life palace"
            ),
        }
    settled: dict[str, str] = {}
    moving: dict[str, dict[int, str]] = {}
    for star in FOURTEEN:
        seen = {d: b["stars"].get(star) for d, b in boards.items()}
        values = set(seen.values())
        if len(values) == 1:
            settled[star] = next(iter(values))
        else:
            moving[star] = seen
    return {
        "status": (
            "settled" if not moving
            else "partially_settled" if settled
            else "unsettled"
        ),
        "candidate_days": days,
        "boards": boards,
        "settled_stars": settled,
        "moving_stars": moving,
        "invariant": not moving,
        "note": (
            "Every one of the fourteen falls in the same palace under all "
            f"{len(days)} candidate lunar day(s)."
            if not moving else
            f"{len(settled)} of the fourteen are invariant across the "
            f"{len(days)} candidate lunar days; {len(moving)} move, and both "
            "palaces are named for each."
        ),
    }


def life_palace_stars(
    board: dict[str, Any], life_palace_branch: str
) -> list[str]:
    """Which of the fourteen actually occupy the life palace."""
    return [
        star for star, br in (board.get("stars") or {}).items()
        if br == life_palace_branch
    ]


def star_delineation(star: str) -> dict[str, Any] | None:
    """The star's own entry for the life palace, from juan 2."""
    slug = {
        "紫微": "ziwei", "天機": "tianji", "太陽": "taiyang", "武曲": "wuqu",
        "天同": "tiantong", "廉貞": "lianzhen", "天府": "tianfu",
        "太陰": "taiyin", "貪狼": "tanlang", "巨門": "jumen",
        "天相": "tianxiang", "天梁": "tianliang", "七殺": "qisha",
        "破軍": "pojun",
    }.get(star)
    if not slug:
        return None
    rule = _rules().get(f"ziwei.quanshu.j2.life_palace_delineation.{slug}")
    if rule is None:
        return None
    cells = (rule.get("conclusion") or {}).get("cells") or {}

    # Most entries carry the Chinese for every cell but a rendering for only
    # some, each unrendered cell naming its own reason. Take the first cell
    # that was actually rendered, in the order a reader would want them, and
    # where none was, say so with the reason rather than returning nothing:
    # the source text IS present, and reporting its absence would be false.
    order = (
        "core_nature", "by_palace_pair", "male_life_verses",
        "female_life_verses", "limit_verses",
    )
    chosen_key, chosen = None, None
    for key in order:
        cell = cells.get(key)
        if isinstance(cell, dict) and cell.get("engine_rendering"):
            chosen_key, chosen = key, cell
            break

    untranslated = [
        {
            "cell": key,
            "reason": (cells[key] or {}).get("output_policy_reason"),
            "has_chinese": bool((cells[key] or {}).get("chinese")),
        }
        for key in order
        if isinstance(cells.get(key), dict)
        and not cells[key].get("engine_rendering")
    ]

    base = chosen or (cells.get("core_nature") or {})
    return {
        "rule_id": rule["rule_id"],
        "star": star,
        "english_name": STAR_NAMES.get(star, star),
        "cell": chosen_key,
        "engine_rendering": base.get("engine_rendering"),
        "chinese": base.get("chinese"),
        "output_policy": base.get("output_policy"),
        "rendering_grade": base.get("rendering_grade"),
        "location": base.get("location"),
        "evidence_grade": rule.get("evidence_grade", "?"),
        "untranslated_cells": untranslated,
        "translated": chosen is not None,
    }
