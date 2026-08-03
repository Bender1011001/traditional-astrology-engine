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
# Hidden stems (藏干) per branch, main qi first. Transcription-grade: the
# standard table as carried by the inspected Yuanhai Ziping / Sanming Tonghui
# transcriptions. School tables differ occasionally on middle/residual qi;
# that variance is disclosed, and the MAIN qi (which no school disputes and
# which always matches the branch's own element) is the only one used for
# month-command and rooting judgments.
HIDDEN_STEMS: dict[str, list[str]] = {
    "zi": ["gui"],
    "chou": ["ji", "gui", "xin"],
    "yin_branch": ["jia", "bing", "wu_stem"],
    "mao": ["yi"],
    "chen": ["wu_stem", "yi", "gui"],
    "si": ["bing", "wu_stem", "geng"],
    "wu_branch": ["ding", "ji"],
    "wei": ["ji", "ding", "yi"],
    "shen": ["geng", "ren", "wu_stem"],
    "you": ["xin"],
    "xu": ["wu_stem", "xin", "ding"],
    "hai": ["ren", "jia"],
}

# Five-phase generation order for Ten-God and seasonal-state derivation.
ELEMENT_CYCLE = ["Wood", "Fire", "Earth", "Metal", "Water"]

# Ten Gods (十神): relation of another stem to the day master, by element
# relation and polarity agreement. Names follow the inspected Ziping usage.
TEN_GOD_NAMES = {
    (0, True): ("bi_jian", "比肩 Friend"),
    (0, False): ("jie_cai", "劫財 Rob Wealth"),
    (1, True): ("shi_shen", "食神 Eating God"),
    (1, False): ("shang_guan", "傷官 Hurting Officer"),
    (2, True): ("pian_cai", "偏財 Indirect Wealth"),
    (2, False): ("zheng_cai", "正財 Direct Wealth"),
    (3, True): ("qi_sha", "七殺 Seven Killings"),
    (3, False): ("zheng_guan", "正官 Direct Officer"),
    (4, True): ("pian_yin", "偏印 Indirect Resource"),
    (4, False): ("zheng_yin", "正印 Direct Resource"),
}

# Seasonal command states (旺相休囚死) of an element in a month branch's season.
# The season's own element is prosperous (wang); the element it generates is
# assisting (xiang); the element that generates it rests (xiu); the element
# that controls it is imprisoned (qiu); the element it controls is dead (si).
# Earth commands the four seasonal-transition months (chen, xu, chou, wei).
SEASON_ELEMENT = {
    "yin_branch": "Wood", "mao": "Wood",
    "si": "Fire", "wu_branch": "Fire",
    "shen": "Metal", "you": "Metal",
    "hai": "Water", "zi": "Water",
    "chen": "Earth", "xu": "Earth", "chou": "Earth", "wei": "Earth",
}
COMMAND_STATES = ["wang 旺 (prosperous)", "xiang 相 (assisting)",
                  "xiu 休 (resting)", "qiu 囚 (imprisoned)", "si 死 (dead)"]


def ten_god(day_stem: str, other_stem: str) -> tuple[str, str]:
    """Ten-God relation of other_stem to the day master."""
    day_element, day_yang = STEM_ELEMENT[day_stem]
    other_element, other_yang = STEM_ELEMENT[other_stem]
    relation = (
        ELEMENT_CYCLE.index(other_element) - ELEMENT_CYCLE.index(day_element)
    ) % 5
    return TEN_GOD_NAMES[(relation, day_yang == other_yang)]


def seasonal_state(element: str, month_branch: str) -> str:
    """Command state of an element in the month branch's season."""
    season = SEASON_ELEMENT[month_branch]
    season_index = ELEMENT_CYCLE.index(season)
    element_index = ELEMENT_CYCLE.index(element)
    offset = (element_index - season_index) % 5
    # offset 0: element IS the season -> wang; 1: season generates it -> xiang;
    # 4: it generates the season -> xiu; 3: it controls the season... careful:
    # states are defined FROM the season: generated-by-season = xiang,
    # generator-of-season = xiu, controller-of-season = qiu, controlled = si.
    if offset == 0:
        return COMMAND_STATES[0]
    if offset == 1:
        return COMMAND_STATES[1]
    if offset == 4:
        return COMMAND_STATES[2]
    if offset == 3:
        return COMMAND_STATES[3]
    return COMMAND_STATES[4]


# --- Branch relations (Sanming Tonghui juan 1) -------------------------------
# Six harmonies. Each branch appears exactly once.
LIU_HE: list[tuple[str, str]] = [
    ("zi", "chou"), ("yin_branch", "hai"), ("mao", "xu"),
    ("chen", "you"), ("si", "shen"), ("wu_branch", "wei"),
]
# Six clashes: each branch against the branch six positions away.
LIU_CHONG: list[tuple[str, str]] = [
    ("zi", "wu_branch"), ("chou", "wei"), ("yin_branch", "shen"),
    ("mao", "you"), ("chen", "xu"), ("si", "hai"),
]
# Six harms.
LIU_HAI: list[tuple[str, str]] = [
    ("zi", "wei"), ("chou", "wu_branch"), ("yin_branch", "si"),
    ("mao", "chen"), ("shen", "hai"), ("you", "xu"),
]
# Six destructions.
LIU_PO: list[tuple[str, str]] = [
    ("zi", "you"), ("wu_branch", "mao"), ("shen", "si"),
    ("yin_branch", "hai"), ("chen", "chou"), ("xu", "wei"),
]
# Three-harmony frames (san he): each yields a transformed element.
SAN_HE: list[tuple[tuple[str, str, str], str]] = [
    (("shen", "zi", "chen"), "Water"),
    (("hai", "mao", "wei"), "Wood"),
    (("yin_branch", "wu_branch", "xu"), "Fire"),
    (("si", "you", "chou"), "Metal"),
]
# Directional/seasonal frames (san hui).
SAN_HUI: list[tuple[tuple[str, str, str], str]] = [
    (("yin_branch", "mao", "chen"), "Wood"),
    (("si", "wu_branch", "wei"), "Fire"),
    (("shen", "you", "xu"), "Metal"),
    (("hai", "zi", "chou"), "Water"),
]
# Punishments, by named type.
XING_GROUPS: list[tuple[tuple[str, ...], str]] = [
    (("yin_branch", "si", "shen"), "wu en zhi xing (ungrateful)"),
    (("chou", "xu", "wei"), "shi shi zhi xing (bullying)"),
    (("zi", "mao"), "wu li zhi xing (discourteous)"),
]
ZI_XING = ("chen", "wu_branch", "you", "hai")  # self-punishment when doubled


def _pairs_present(
    table: list[tuple[str, str]], present: dict[str, list[str]]
) -> list[dict[str, Any]]:
    found = []
    for first, second in table:
        if first in present and second in present:
            found.append({
                "branches": [BRANCH_LABELS[first], BRANCH_LABELS[second]],
                # present[branch] is a list of pillar names (a branch can occur
                # in more than one pillar), so flatten rather than nest.
                "pillars": sorted(present[first] + present[second]),
            })
    return found


def branch_relations(pillars: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """All classical branch relations among the four pillars.

    Reports what is present; it does not adjudicate which relation dominates
    when several apply to one branch, because precedence is school-specific and
    the spec keeps that gated.
    """
    present: dict[str, list[str]] = {}
    for pillar_name, pillar in pillars.items():
        present.setdefault(pillar["branch"], []).append(pillar_name)

    counts = {branch: len(names) for branch, names in present.items()}

    san_he_found = []
    for frame, element in SAN_HE:
        members = [b for b in frame if b in present]
        if len(members) == 3:
            san_he_found.append({
                "type": "complete",
                "frame": [BRANCH_LABELS[b] for b in frame],
                "transforms_to": element,
            })
        elif len(members) == 2:
            san_he_found.append({
                "type": "half",
                "present": [BRANCH_LABELS[b] for b in members],
                "missing": [BRANCH_LABELS[b] for b in frame if b not in present],
                "reinforces": element,
            })

    san_hui_found = []
    for frame, element in SAN_HUI:
        members = [b for b in frame if b in present]
        if len(members) == 3:
            san_hui_found.append({
                "frame": [BRANCH_LABELS[b] for b in frame],
                "seasonal_element": element,
            })

    xing_found = []
    for group, label in XING_GROUPS:
        members = [b for b in group if b in present]
        if len(members) == len(group):
            xing_found.append({
                "type": label,
                "complete": True,
                "branches": [BRANCH_LABELS[b] for b in group],
            })
        elif len(group) == 3 and len(members) == 2:
            xing_found.append({
                "type": label,
                "complete": False,
                "present": [BRANCH_LABELS[b] for b in members],
            })
    for branch in ZI_XING:
        if counts.get(branch, 0) >= 2:
            xing_found.append({
                "type": "zi xing (self-punishment)",
                "complete": True,
                "branches": [BRANCH_LABELS[branch]] * counts[branch],
            })

    return {
        "six_harmonies": _pairs_present(LIU_HE, present),
        "six_clashes": _pairs_present(LIU_CHONG, present),
        "six_harms": _pairs_present(LIU_HAI, present),
        "six_destructions": _pairs_present(LIU_PO, present),
        "three_harmony_frames": san_he_found,
        "directional_frames": san_hui_found,
        "punishments": xing_found,
        "precedence_note": (
            "Relations are reported, not ranked. When several apply to one "
            "branch, which prevails is school-specific and stays gated."
        ),
    }


# --- Na Yin (纳音), Sanming Tonghui juan 1 -----------------------------------
# Thirty melodic-element assignments, one per consecutive PAIR of sexagenary
# positions. Each of the five elements takes exactly six pairs (twelve pillars).
NA_YIN: list[tuple[str, str]] = [
    ("Metal", "海中金 Metal in the Sea"),
    ("Fire", "爐中火 Fire in the Furnace"),
    ("Wood", "大林木 Wood of the Great Forest"),
    ("Earth", "路旁土 Earth by the Roadside"),
    ("Metal", "劍鋒金 Metal of the Sword Blade"),
    ("Fire", "山頭火 Fire on the Mountain Top"),
    ("Water", "澗下水 Water Below the Ravine"),
    ("Earth", "城頭土 Earth on the City Wall"),
    ("Metal", "白蠟金 White Wax Metal"),
    ("Wood", "楊柳木 Willow Wood"),
    ("Water", "泉中水 Water in the Spring"),
    ("Earth", "屋上土 Earth on the Roof"),
    ("Fire", "霹靂火 Thunderbolt Fire"),
    ("Wood", "松柏木 Pine and Cypress Wood"),
    ("Water", "長流水 Long Flowing Water"),
    ("Metal", "沙中金 Metal in the Sand"),
    ("Fire", "山下火 Fire at the Mountain Foot"),
    ("Wood", "平地木 Wood of the Plain"),
    ("Earth", "壁上土 Earth on the Wall"),
    ("Metal", "金箔金 Gold Foil Metal"),
    ("Fire", "覆燈火 Lamp Fire"),
    ("Water", "天河水 Water of the Heavenly River"),
    ("Earth", "大驛土 Earth of the Great Post Station"),
    ("Metal", "釵釧金 Hairpin Metal"),
    ("Wood", "桑柘木 Mulberry Wood"),
    ("Water", "大溪水 Water of the Great Stream"),
    ("Earth", "沙中土 Earth in the Sand"),
    ("Fire", "天上火 Fire in the Heavens"),
    ("Wood", "石榴木 Pomegranate Wood"),
    ("Water", "大海水 Water of the Great Sea"),
]


def na_yin(sexagenary_index: int) -> dict[str, str]:
    """Na Yin element and its image for a 0-based sexagenary index."""
    element, image = NA_YIN[(sexagenary_index % 60) // 2]
    return {"element": element, "image": image}


def _sexagenary_index(stem: str, branch: str) -> int:
    stems, branches = _stems(), _branches()
    target = (stems.index(stem), branches.index(branch))
    return next(
        i for i in range(60) if (i % 10, i % 12) == target
    )


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
        DisclosureKind.SOURCE,
        "Hidden stems and Ten Gods",
        "The hidden-stem table and Ten-God relations follow the inspected "
        "Yuanhai Ziping / Sanming Tonghui transcriptions (transcription grade: "
        "the Wikisource witnesses cannot control wording). Only the undisputed "
        "MAIN qi of each branch - which always matches the branch's own element "
        "- is used for month-command and rooting judgments; middle and residual "
        "qi are reported but carry no judgment weight here.",
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Month command",
        "Seasonal command states (wang/xiang/xiu/qiu/si) computed from the month "
        "branch's season under the standard five-phase cycle, with Earth "
        "commanding the four transition months. The Ziping hierarchy makes this "
        "the first substantive judgment, before any strength or pattern claim.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Pattern and useful god",
        "Pattern (geju) eligibility and useful-element (yongshen) selection are "
        "school-specific and stay refused pending edition control. The support "
        "assessment below states seasonal state and roots - the facts every "
        "school agrees precede those judgments - and draws a summary conclusion "
        "only where the testimony is unanimous.",
    
        category="extraction_incomplete",
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

    hidden = {
        name: [
            {
                "stem": s,
                "label": STEM_LABELS[s],
                "element": STEM_ELEMENT[s][0],
                "qi": ("main", "middle", "residual")[i],
                "ten_god": ten_god(day_stem, s)[1],
            }
            for i, s in enumerate(HIDDEN_STEMS[p["branch"]])
        ]
        for name, p in pillars.items()
    }
    visible_gods = {
        name: ten_god(day_stem, p["stem"])[1]
        for name, p in pillars.items()
        if name != "day"
    }

    command = seasonal_state(day_master_element, month_branch)
    root_branches = [
        name
        for name, p in pillars.items()
        if any(
            STEM_ELEMENT[s][0] == day_master_element
            for s in HIDDEN_STEMS[p["branch"]]
        )
    ]
    month_root = "month" in root_branches
    timely = command.startswith(("wang", "xiang"))
    if timely and month_root:
        support = (
            "supported: the day master is in seasonal command "
            "and rooted in the month branch itself"
        )
    elif not timely and not root_branches:
        support = (
            "unsupported: out of season with no root in any branch"
        )
    else:
        support = (
            "mixed: seasonal state and rooting point different ways; "
            "the final strength class is school-dependent and not asserted"
        )

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
        "month_command": {
            "season_of_month_branch": SEASON_ELEMENT[month_branch],
            "day_master_state": command,
            "root_in_month_branch": month_root,
            "root_branches": root_branches,
            "support_assessment": support,
        },
        "hidden_stems": hidden,
        "visible_stem_ten_gods": visible_gods,
        "branch_relations": branch_relations(pillars),
        "na_yin": {
            name: na_yin(_sexagenary_index(p["stem"], p["branch"]))
            for name, p in pillars.items()
        },
        "element_tally": _element_tally(pillars),
        "luck_pillars": _luck_pillars(
            birth, jd, year_stem, month_stem, month_branch
        ),
    }

    section.reading = _bazi_reading(
        day_stem, day_master_element, day_master_yang, command, month_root,
        root_branches, support, visible_gods, hidden,
        _element_tally(pillars), section.facts["branch_relations"],
    )
    return section


def _bazi_reading(
    day_stem: str,
    element: str,
    yang: bool,
    command: str,
    month_root: bool,
    root_branches: list[str],
    support: str,
    visible_gods: dict[str, str],
    hidden: dict[str, list[dict[str, Any]]],
    tally: dict[str, int],
    relations: dict[str, Any],
) -> list[str]:
    """Structural reading in the Ziping order: subject, command, roots, relations.

    Describes what the chart IS in the tradition's own categories. No pattern
    verdict, no fortune - those stay behind the edition-control gate.
    """
    polarity = "yang" if yang else "yin"
    reading = [
        f"Day master (the subject of the chart): {STEM_LABELS[day_stem]}, "
        f"{polarity} {element}. The Ziping hierarchy judges everything else "
        "relative to this stem.",
        f"Month command, the first judgment: the day master stands in state "
        f"{command} for this month's season, "
        f"{'with' if month_root else 'without'} a root in the month branch"
        + (
            f"; rooted also in {', '.join(b for b in root_branches if b != 'month')}"
            if [b for b in root_branches if b != "month"]
            else ""
        )
        + f". Assessment: {support}.",
    ]
    god_list = ", ".join(f"{pillar}: {god}" for pillar, god in visible_gods.items())
    reading.append(f"Visible stems relative to the day master - {god_list}.")

    # Branch relations, stated before any absence claim because a clash or frame
    # changes what the branches are doing in the first place.
    relation_lines: list[str] = []
    for frame in relations["three_harmony_frames"]:
        if frame["type"] == "complete":
            relation_lines.append(
                f"complete three-harmony frame {'-'.join(frame['frame'])} "
                f"transforming toward {frame['transforms_to']}"
            )
        else:
            relation_lines.append(
                f"half three-harmony frame {'-'.join(frame['present'])} "
                f"(missing {'-'.join(frame['missing'])}) reinforcing "
                f"{frame['reinforces']}"
            )
    for frame in relations["directional_frames"]:
        relation_lines.append(
            f"directional frame {'-'.join(frame['frame'])} "
            f"({frame['seasonal_element']})"
        )
    for label, key in (
        ("clash", "six_clashes"),
        ("harmony", "six_harmonies"),
        ("harm", "six_harms"),
        ("destruction", "six_destructions"),
    ):
        for item in relations[key]:
            relation_lines.append(
                f"{label} between {' and '.join(item['branches'])} "
                f"({'/'.join(item['pillars'])} pillars)"
            )
    for punishment in relations["punishments"]:
        branches = punishment.get("branches") or punishment.get("present") or []
        relation_lines.append(
            f"{'complete' if punishment['complete'] else 'partial'} punishment, "
            f"{punishment['type']}: {'-'.join(branches)}"
        )

    if relation_lines:
        reading.append(
            "Branch relations present: " + "; ".join(relation_lines) + ". "
            + relations["precedence_note"]
        )
    else:
        reading.append(
            "No classical branch relations (harmony, clash, harm, destruction, "
            "frame, or punishment) are present among these four branches."
        )

    missing = [element_name for element_name, count in tally.items() if count == 0]
    if missing:
        reading.append(
            f"Absent element(s) among visible stems and branch main qi: "
            f"{', '.join(missing)}. In Ziping terms the related Ten-God "
            "relations lack visible carriers; hidden-stem presence, if any, is "
            "listed in the calculation block and carries less force."
        )
    return reading


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
