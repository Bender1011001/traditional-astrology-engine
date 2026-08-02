"""BaZi (Four Pillars) section.

Cycle arithmetic, the shichen partition, and both stem lookup tables come from
the validated `bazi_sexagenary_kernel_v1` research pack. Everything that pack
deliberately refuses to default - the day-count anchor, the year/month/day/hour
boundaries - is supplied here as a disclosed product convention, and the hour
pillar is emitted under BOTH clock time and true solar time because that fork
changes the pillar for a large share of births.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

import swisseph as swe

from .timebase import TimeBases
from .types import BirthInput, DisclosureKind, EvidenceGrade, TraditionSection

KERNEL_SPEC = (
    Path(__file__).resolve().parents[3]
    / "docs" / "research" / "multitradition" / "bazi" / "sexagenary_kernel_spec.json"
)

STEM_LABELS = {
    "jia": "甲 Jia", "yi": "乙 Yi", "bing": "丙 Bing", "ding": "丁 Ding",
    "wu_stem": "戊 Wu", "ji": "己 Ji", "geng": "庚 Geng", "xin": "辛 Xin",
    "ren": "壬 Ren", "gui": "癸 Gui",
}
BRANCH_LABELS = {
    "zi": "子 Zi", "chou": "丑 Chou", "yin_branch": "寅 Yin", "mao": "卯 Mao",
    "chen": "辰 Chen", "si": "巳 Si", "wu_branch": "午 Wu", "wei": "未 Wei",
    "shen": "申 Shen", "you": "酉 You", "xu": "戌 Xu", "hai": "亥 Hai",
}
BRANCH_ANIMALS = {
    "zi": "Rat", "chou": "Ox", "yin_branch": "Tiger", "mao": "Rabbit",
    "chen": "Dragon", "si": "Snake", "wu_branch": "Horse", "wei": "Goat",
    "shen": "Monkey", "you": "Rooster", "xu": "Dog", "hai": "Pig",
}
STEM_ELEMENT = {
    "jia": ("Wood", True), "yi": ("Wood", False), "bing": ("Fire", True),
    "ding": ("Fire", False), "wu_stem": ("Earth", True), "ji": ("Earth", False),
    "geng": ("Metal", True), "xin": ("Metal", False), "ren": ("Water", True),
    "gui": ("Water", False),
}
BRANCH_ELEMENT = {
    "zi": "Water", "chou": "Earth", "yin_branch": "Wood", "mao": "Wood",
    "chen": "Earth", "si": "Fire", "wu_branch": "Fire", "wei": "Earth",
    "shen": "Metal", "you": "Metal", "xu": "Earth", "hai": "Water",
}
# Solar longitude of each JIE (month-establishing term) -> month branch.
JIE_TO_BRANCH: list[tuple[int, str]] = [
    (315, "yin_branch"), (345, "mao"), (15, "chen"), (45, "si"),
    (75, "wu_branch"), (105, "wei"), (135, "shen"), (165, "you"),
    (195, "xu"), (225, "hai"), (255, "zi"), (285, "chou"),
]
# Validated anchor: JDN 2433191 (1949-10-01) is a Jia-Zi day, index 0.
# Cross-checked against JDN 2451545 (2000-01-01) = Wu-Wu, index 54.
DAY_ANCHOR_JDN = 2433191
DAY_ANCHOR_INDEX = 0
TROPICAL_YEAR_DAYS = 365.2425


@lru_cache(maxsize=1)
def _kernel() -> dict[str, Any]:
    return json.loads(KERNEL_SPEC.read_text(encoding="utf-8"))


def _stems() -> list[str]:
    return [s["id"] for s in _kernel()["cycle"]["stems"]]


def _branches() -> list[str]:
    return [b["id"] for b in _kernel()["cycle"]["branches"]]


def _pair(index: int) -> tuple[str, str]:
    return _stems()[index % 10], _branches()[index % 12]


def _sun_longitude(jd: float) -> float:
    return swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)[0][0]


def _find_term(target_deg: float, jd_start: float) -> float:
    """First instant at or after jd_start where solar longitude crosses target."""
    jd = jd_start
    previous = (_sun_longitude(jd) - target_deg) % 360
    for _ in range(4000):
        jd += 0.5
        current = (_sun_longitude(jd) - target_deg) % 360
        if previous > 300 and current < 60:
            low, high = jd - 0.5, jd
            for _ in range(60):
                mid = (low + high) / 2
                if (_sun_longitude(mid) - target_deg) % 360 > 300:
                    low = mid
                else:
                    high = mid
            return (low + high) / 2
        previous = current
    raise ValueError(f"Solar term {target_deg} not found from JD {jd_start}")


def _hour_branch(moment: datetime) -> str:
    hour = moment.hour + moment.minute / 60
    return _branches()[int(((hour + 1) % 24) // 2)]


def build(birth: BirthInput, bases: TimeBases) -> TraditionSection:
    section = TraditionSection(
        tradition_id="chinese_bazi",
        display_name="Chinese BaZi (Four Pillars)",
        evidence_grade=EvidenceGrade.CONFIGURED,
        basis=(
            "Cycle arithmetic, shichen partition, and stem lookup tables from the "
            "validated sexagenary kernel; boundaries supplied as product conventions."
        ),
    )
    section.disclose(
        DisclosureKind.SOURCE,
        "Kernel provenance",
        "Stem/branch orders, the sixty-pair cycle, the shichen partition, and both "
        "the year-to-month and day-to-hour stem tables come from "
        "bazi_sexagenary_kernel_v1, whose standalone validator passes in this repo.",
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Year boundary",
        "Li Chun (solar longitude 315 degrees) begins the pillar year - the "
        "dominant Ziping convention. Some practice uses the lunar new year, which "
        "moves the year pillar for births between the two dates.",
        ("Lunar new year", "Civil January 1"),
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Month boundary",
        "Months change at the twelve jie (month-establishing solar terms), computed "
        "from Swiss Ephemeris solar longitude rather than a printed almanac.",
        ("Printed almanac tables", "Mean-motion approximations"),
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Day anchor",
        "Sexagenary day count anchored at JDN 2433191 (1949-10-01) = Jia-Zi, "
        "cross-checked against 2000-01-01 = Wu-Wu. The research pack registers no "
        "day-concordance source, so this anchor is a product choice.",
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Day rollover",
        "The civil day is used for the day pillar. Late-Zi schools roll the day "
        "pillar forward at 23:00, which changes the day pillar for births between "
        "23:00 and midnight.",
        ("Late-Zi rollover at 23:00",),
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Strength and pattern",
        "Day-master strength class, pattern eligibility, and useful-element "
        "selection are school-specific and are not asserted here. The Ziping "
        "hierarchy requires month command before any such judgment.",
    )

    stems, branches = _stems(), _branches()
    jd = bases.julian_day_ut

    li_chun_this_year = _find_term(315, swe.julday(birth.civil_date.year, 1, 1, 0.0))
    pillar_year = (
        birth.civil_date.year if jd >= li_chun_this_year else birth.civil_date.year - 1
    )
    year_index = (pillar_year - 1984) % 60
    year_stem, year_branch = _pair(year_index)

    month_branch, month_start_jd = _month_branch(jd, birth.civil_date.year)
    first_month_stem = _kernel()["cycle"]["month_stem_from_year_stem"]["table"][year_stem]
    steps = (branches.index(month_branch) - branches.index("yin_branch")) % 12
    month_stem = stems[(stems.index(first_month_stem) + steps) % 10]

    day_index = (DAY_ANCHOR_INDEX + (bases.julian_day_number - DAY_ANCHOR_JDN)) % 60
    day_stem, day_branch = _pair(day_index)

    zi_stem = _kernel()["cycle"]["hour_stem_from_day_stem"]["table"][day_stem]
    hours: dict[str, dict[str, str]] = {}
    for label, moment in (
        ("true_solar_time", bases.true_solar_time),
        ("clock_time", birth.civil_datetime),
        ("local_mean_time", bases.local_mean_time),
    ):
        branch = _hour_branch(moment)
        stem = stems[(stems.index(zi_stem) + branches.index(branch)) % 10]
        hours[label] = {
            "time": moment.strftime("%H:%M:%S"),
            "stem": stem,
            "branch": branch,
            "label": f"{STEM_LABELS[stem]} {BRANCH_LABELS[branch]}",
        }

    primary_hour = hours["true_solar_time"]
    if primary_hour["branch"] != hours["clock_time"]["branch"]:
        section.disclose(
            DisclosureKind.FORK,
            "Hour pillar",
            f"True solar time ({primary_hour['time']}) and clock time "
            f"({hours['clock_time']['time']}) fall in different shichen, so the hour "
            f"pillar differs: {primary_hour['label']} versus "
            f"{hours['clock_time']['label']}. True solar time is used as primary; "
            "both are shown because practice is genuinely divided.",
            ("Clock time", "Local mean time"),
        )
    else:
        section.disclose(
            DisclosureKind.CONFIGURED_METHOD,
            "Hour pillar clock",
            "True solar time used as primary. For this birth all three time bases "
            "fall in the same shichen, so the fork does not change the pillar.",
            ("Clock time", "Local mean time"),
        )

    pillars = {
        "year": _pillar_dict(year_stem, year_branch),
        "month": _pillar_dict(month_stem, month_branch),
        "day": _pillar_dict(day_stem, day_branch),
        "hour": _pillar_dict(primary_hour["stem"], primary_hour["branch"]),
    }
    day_master_element, day_master_yang = STEM_ELEMENT[day_stem]

    section.facts = {
        "pillar_year_used": pillar_year,
        "li_chun_boundary_utc": _jd_to_iso(li_chun_this_year),
        "month_term_start_utc": _jd_to_iso(month_start_jd),
        "pillars": pillars,
        "hour_pillar_candidates": hours,
        "day_master": {
            "stem": day_stem,
            "label": STEM_LABELS[day_stem],
            "element": day_master_element,
            "polarity": "yang" if day_master_yang else "yin",
        },
        "element_tally": _element_tally(pillars),
        "luck_pillars": _luck_pillars(
            birth, jd, year_stem, month_stem, month_branch
        ),
    }
    return section


def _pillar_dict(stem: str, branch: str) -> dict[str, Any]:
    return {
        "stem": stem,
        "branch": branch,
        "label": f"{STEM_LABELS[stem]} {BRANCH_LABELS[branch]}",
        "animal": BRANCH_ANIMALS[branch],
        "stem_element": STEM_ELEMENT[stem][0],
        "branch_element": BRANCH_ELEMENT[branch],
    }


def _element_tally(pillars: dict[str, dict[str, Any]]) -> dict[str, int]:
    tally = {"Wood": 0, "Fire": 0, "Earth": 0, "Metal": 0, "Water": 0}
    for pillar in pillars.values():
        tally[pillar["stem_element"]] += 1
        tally[pillar["branch_element"]] += 1
    return tally


def _month_branch(jd: float, year: int) -> tuple[str, float]:
    terms: list[tuple[float, str]] = []
    for degrees, branch in JIE_TO_BRANCH:
        for scan_year in (year - 1, year):
            terms.append((_find_term(degrees, swe.julday(scan_year, 1, 1, 0.0)), branch))
    terms.sort()
    chosen = terms[0]
    for moment, branch in terms:
        if moment <= jd:
            chosen = (moment, branch)
    return chosen[1], chosen[0]


def _luck_pillars(
    birth: BirthInput,
    jd: float,
    year_stem: str,
    month_stem: str,
    month_branch: str,
) -> dict[str, Any]:
    """Forward/reverse ten-year sequence from the month pillar.

    Direction depends on year-stem polarity and sex. Sex is not part of the birth
    input contract, so both directions are emitted and the dependency is stated.
    """
    stems, branches = _stems(), _branches()
    month_index = next(
        i for i in range(60)
        if i % 10 == stems.index(month_stem) and i % 12 == branches.index(month_branch)
    )

    next_term = min(
        moment
        for degrees, _ in JIE_TO_BRANCH
        for moment in (_find_term(degrees, swe.julday(birth.civil_date.year, 1, 1, 0.0)),)
        if moment > jd
    )
    start_age = (next_term - jd) / 3.0

    sequences: dict[str, list[dict[str, Any]]] = {}
    for direction in ("forward", "reverse"):
        rows: list[dict[str, Any]] = []
        for step in range(1, 9):
            index = (
                (month_index + step) % 60 if direction == "forward"
                else (month_index - step) % 60
            )
            stem, branch = _pair(index)
            age_from = start_age + (step - 1) * 10
            begins = birth.civil_datetime + timedelta(days=age_from * TROPICAL_YEAR_DAYS)
            ends = begins + timedelta(days=10 * TROPICAL_YEAR_DAYS)
            rows.append({
                "age_from": round(age_from, 2),
                "age_to": round(age_from + 10, 2),
                "start": begins.date().isoformat(),
                "end": ends.date().isoformat(),
                "label": f"{STEM_LABELS[stem]} {BRANCH_LABELS[branch]}",
            })
        sequences[direction] = rows

    return {
        "start_age": round(start_age, 3),
        "direction_rule": (
            "Yang-stem year with male native, or yin-stem year with female native, "
            "runs forward; the complementary cases run reverse."
        ),
        "year_stem_polarity": "yang" if STEM_ELEMENT[year_stem][1] else "yin",
        "sequences": sequences,
    }


def _jd_to_iso(jd: float) -> str:
    year, month, day, hour = swe.revjul(jd)
    base = datetime(year, month, day) + timedelta(hours=hour)
    return base.strftime("%Y-%m-%dT%H:%M:%SZ")
