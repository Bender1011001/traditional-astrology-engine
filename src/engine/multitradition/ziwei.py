"""Zi Wei Dou Shu section.

The pack behind this section is a transcription candidate, not a controlling
edition: seven grade-D rules read off the Chinese Wikisource text of
`Ziwei Doushu Quanshu` juan 2, whose base facsimile is unidentified. That grade
governs what may be *said* here - no star meanings, no judgment - but it does
not by itself decide what may be *computed*.

What used to block the whole chart was the first input. Zi Wei begins from the
LUNAR birth month, and the pack registers no civil-to-lunisolar conversion; its
source audit forbids a `ziwei_default`, so the pack fails closed and stays that
way. The product layer supplies the conversion instead, as a disclosed
configured method - and then checks whether the choice actually matters.

For the chart month it usually does not, and that is provable rather than
assumed. This module runs the panel's validated lunisolar kernel under every
calendar regime that could plausibly govern the birth - Purple Mountain at 120
degrees east (official since 1929), Beijing local mean time (the Qing Shixian
regime it replaced), and the Indochina profile at 105 degrees east - and only
emits the chart when all of them return the same chart month. When they
disagree, the section falls back to the old refusal. The gate is what makes the
configuration defendable: the reader is not asked to trust the meridian, only
to check that no available meridian changes the answer.

The lunar DAY is a different matter, and the same check now does real work. Day
number can move between regimes, and everything keyed to it - the five-phase
bureau, and therefore Zi Wei's own star and the fourteen main stars with it -
is emitted only when it does not.

That is a change of 2026-08-04. This module used to call its own output "an
empty board" on the grounds that the pack held no bureau table and no Zi Wei
placement table. It held both. They are printed in the same juan the seven-rule
pack was read from, as ASCII-art grids inside `<nowiki>` blocks and as a
captioned diagram, and a prose-oriented extraction walked past them. The wider
pack - `quanshu_full_rule_manifest.json`, 83 rules across all three juan -
supplies the bureau (a composition of the Five Tigers couplets with the
sixty-jiazi nayin song, exactly as the chapter's own worked example composes
them), Zi Wei by bureau and lunar day, Tian Fu's reflection, both main-star
couplets, and the seven-level brightness grid.

What has NOT changed is what may be said. Every meaning in that pack is either
refused outright or held at research grade, and none of it reaches this section.
The board now has pieces on it. It still renders no judgment about them.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import swisseph as swe

from . import vietnamese
from .timebase import TimeBases
from .types import BirthInput, DisclosureKind, EvidenceGrade, TraditionSection

RESEARCH_ROOT = (
    Path(__file__).resolve().parents[3] / "docs" / "research" / "multitradition"
)
ZIWEI_MANIFEST = RESEARCH_ROOT / "ziwei" / "calculation_rule_manifest.json"
ZIWEI_VECTORS = RESEARCH_ROOT / "ziwei" / "validation_vectors.json"
# The wider pack: all three juan, hash-pinned by Wikisource revision. It carries
# the bureau, the Zi Wei day tables, Tian Fu, both main-star couplets and the
# brightness grid - none of which the seven-rule pack above contains.
ZIWEI_FULL = RESEARCH_ROOT / "ziwei" / "quanshu_full_rule_manifest.json"
# The double-hour partition is the ordinary shichen partition, taken from the
# validated BaZi kernel rather than restated privately here.
BAZI_KERNEL = RESEARCH_ROOT / "bazi" / "sexagenary_kernel_spec.json"

# Branch romanizations exactly as the Zi Wei pack's vectors spell them. The BaZi
# kernel disambiguates two of them (yin_branch, wu_branch) against stem names;
# the two lists are the same twelve branches in the same order.
BRANCHES = [
    "zi", "chou", "yin", "mao", "chen", "si",
    "wu", "wei", "shen", "you", "xu", "hai",
]
BRANCH_LABELS = {
    "zi": "子", "chou": "丑", "yin": "寅", "mao": "卯",
    "chen": "辰", "si": "巳", "wu": "午", "wei": "未",
    "shen": "申", "you": "酉", "xu": "戌", "hai": "亥",
}
# Anchors stated in the transcription, as branch indices.
WENCHANG_ZI_ANCHOR = BRANCHES.index("xu")
WENQU_ZI_ANCHOR = BRANCHES.index("chen")
MONTH_ONE_ANCHOR = BRANCHES.index("yin")
ZUOFU_MONTH_ONE_ANCHOR = BRANCHES.index("chen")
YOUBI_MONTH_ONE_ANCHOR = BRANCHES.index("xu")

TOPIC_LABELS = {
    "life": "命宮",
    "siblings": "兄弟宮",
    "wife_and_concubines_historical_label": "夫妻宮",
    "children": "子女宮",
    "wealth": "財帛宮",
    "illness": "疾厄宮",
    "travel": "遷移宮",
    "servants_historical_label": "奴僕宮",
    "office_and_career": "官祿宮",
    "property": "田宅宮",
    "fortune_and_virtue": "福德宮",
    "parents": "父母宮",
}

# Every calendar regime that could plausibly govern a Chinese lunisolar date.
# Each is a real historical or contemporary authority, not a tuning knob: the
# point of listing them is to test whether the chart month survives all of them.
CALENDAR_REGIMES = (
    {
        "regime_id": "purple_mountain_120e",
        "label": "Purple Mountain Observatory, 120°E (UTC+8)",
        "offset_hours": 8.0,
        "authority": (
            "The official Chinese农历 rule since the 1929 standard-time reform: "
            "true new moon and true solar terms reckoned at 120 degrees east."
        ),
    },
    {
        "regime_id": "beijing_local_mean_time",
        "label": "Beijing local mean time, 116°25'E (UTC+7:45)",
        "offset_hours": 116.4167 / 15.0,
        "authority": (
            "The meridian the Qing Shixian calendar used before 1929, i.e. the "
            "regime any pre-Republican worked chart would have been cast under."
        ),
    },
    {
        "regime_id": "indochina_105e",
        "label": "Indochina, 105°E (UTC+7)",
        "offset_hours": 7.0,
        "authority": (
            "The Vietnamese profile already validated elsewhere in this panel. "
            "Included as an adversarial case, not as a proposal: if the chart "
            "month survives even this meridian, no plausible one moves it."
        ),
    },
)


@lru_cache(maxsize=8)
def _pack(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _shichen_starts() -> list[float]:
    """Decimal start hour of each double-hour, in branch order, from the kernel."""
    branches = sorted(_pack(BAZI_KERNEL)["cycle"]["branches"], key=lambda b: b["index"])
    starts: list[float] = []
    for branch in branches:
        hour, minute = (int(part) for part in branch["shichen_start"].split(":"))
        starts.append(hour + minute / 60)
    return starts


def double_hour_branch(moment: datetime) -> str:
    """Which shichen a wall-clock moment falls in.

    Zi opens at 23:00 in the kernel's partition, so the day's first hour spans
    midnight; shifting by one hour before the two-hour division handles that.
    """
    starts = _shichen_starts()
    hour = moment.hour + moment.minute / 60 + moment.second / 3600
    offset = (hour - starts[0]) % 24
    return BRANCHES[int(offset // 2)]


def wenchang_branch(hour_branch: str) -> str:
    """Zi hour at Xu, counting branches backward to the birth double-hour."""
    return BRANCHES[(WENCHANG_ZI_ANCHOR - BRANCHES.index(hour_branch)) % 12]


def wenqu_branch(hour_branch: str) -> str:
    """Zi hour at Chen, counting branches forward to the birth double-hour."""
    return BRANCHES[(WENQU_ZI_ANCHOR + BRANCHES.index(hour_branch)) % 12]


def month_palace_branch(chart_month: int) -> str:
    """Lunar month 1 at Yin, counting branches forward to the chart month."""
    return BRANCHES[(MONTH_ONE_ANCHOR + chart_month - 1) % 12]


def life_palace_branch(chart_month: int, hour_branch: str) -> str:
    """Month palace treated as the Zi hour, counting backward to the birth hour."""
    start = BRANCHES.index(month_palace_branch(chart_month))
    return BRANCHES[(start - BRANCHES.index(hour_branch)) % 12]


def body_palace_branch(chart_month: int, hour_branch: str) -> str:
    """Month palace treated as the Zi hour, counting forward to the birth hour."""
    start = BRANCHES.index(month_palace_branch(chart_month))
    return BRANCHES[(start + BRANCHES.index(hour_branch)) % 12]


def zuofu_branch(chart_month: int) -> str:
    """Lunar month 1 at Chen, counting branches forward to the birth month."""
    return BRANCHES[(ZUOFU_MONTH_ONE_ANCHOR + chart_month - 1) % 12]


def youbi_branch(chart_month: int) -> str:
    """Lunar month 1 at Xu, counting branches backward to the birth month."""
    return BRANCHES[(YOUBI_MONTH_ONE_ANCHOR - (chart_month - 1)) % 12]


def normalize_chart_month(month_number: int, is_intercalary: bool) -> int:
    """A birth in an intercalary month uses the FOLLOWING month number.

    The pack's own worked example: intercalary month 1 charts as month 2.
    """
    return month_number + 1 if is_intercalary else month_number


def topic_palaces(life_palace: str) -> dict[str, str]:
    """The twelve topics assigned in reverse branch order from the life palace."""
    topics = _rule("ziwei.quanshu.j2.place_twelve_topic_palaces")["conclusion"][
        "topics"
    ]
    start = BRANCHES.index(life_palace)
    return {topic: BRANCHES[(start - i) % 12] for i, topic in enumerate(topics)}


def four_transformations(year_stem: str) -> dict[str, str]:
    """Lu / Quan / Ke / Ji for a birth-year stem, in the transcription's lineage.

    The rule's publication limit does not forbid computing this - unlike the
    Five Tigers table, which says outright not to use it. It requires that the
    table's lineage always be displayed and that no later school be merged in.
    Both conditions are met by the disclosures on this section.
    """
    rule = _rule("ziwei.quanshu.j2.four_transformations_by_year_stem")
    keys = rule["conclusion"]["ordered_transformation_keys"]
    return dict(zip(keys, rule["conclusion"]["table"][year_stem], strict=True))


def _calendar_regime_readings(civil_day: date) -> list[dict[str, Any]]:
    """The lunar date under every plausible regime, with its chart month."""
    readings: list[dict[str, Any]] = []
    for regime in CALENDAR_REGIMES:
        lunar = vietnamese.lunar_date(civil_day, regime["offset_hours"])
        month_number = lunar["month_number"]
        is_intercalary = bool(lunar.get("is_intercalary") or lunar.get("leap"))
        readings.append({
            "regime_id": regime["regime_id"],
            "label": regime["label"],
            "authority": regime["authority"],
            "utc_offset_hours": round(regime["offset_hours"], 4),
            "lunar_month_number": month_number,
            "is_intercalary_month": is_intercalary,
            "lunar_day": lunar["day"],
            "chart_month": normalize_chart_month(month_number, is_intercalary),
        })
    return readings


def _rule(rule_id: str) -> dict[str, Any]:
    return next(
        rule for rule in _pack(ZIWEI_MANIFEST)["rules"] if rule["rule_id"] == rule_id
    )


# --- the wider pack -------------------------------------------------------
# Every table below is read out of the manifest rather than restated here, so
# the passage citation and the arithmetic can never drift apart.

STEM_LABELS = {
    "jia": "甲", "yi": "乙", "bing": "丙", "ding": "丁", "wu": "戊",
    "ji": "己", "geng": "庚", "xin": "辛", "ren": "壬", "gui": "癸",
}
# Chinese label -> the pack's romanized branch id (BRANCH_LABELS inverted).
_BRANCH_BY_LABEL = {label: branch for branch, label in BRANCH_LABELS.items()}
# The fourteen main stars, in the order the two couplets name them.
MAIN_STAR_IDS = {
    "紫微": "ziwei", "天機": "tianji", "太陽": "taiyang", "武曲": "wuqu",
    "天同": "tiantong", "廉貞": "lianzhen", "天府": "tianfu", "太陰": "taiyin",
    "貪狼": "tanlang", "巨門": "jumen", "天相": "tianxiang", "天梁": "tianliang",
    "七殺": "qisha", "破軍": "pojun",
}
BUREAU_LABELS = {
    "water_two": "水二局", "wood_three": "木三局", "metal_four": "金四局",
    "earth_five": "土五局", "fire_six": "火六局",
}


def _full_rule(rule_id: str) -> dict[str, Any]:
    return next(
        rule for rule in _pack(ZIWEI_FULL)["rules"] if rule["rule_id"] == rule_id
    )


def bureau(year_stem: str, life_palace: str) -> dict[str, Any]:
    """Five-phase bureau from the life palace's own stem-branch nayin.

    Two printed tables composed, as the chapter composes them itself: the Five
    Tigers couplet fixes the stem at Yin, the stems run forward to the life
    palace, and the sixty-jiazi nayin song names the element of the resulting
    pair. The chapter's worked example - Jia year, life palace at Yin, 丙寅,
    furnace fire, the six bureau - is the whole rule in one sentence.
    """
    cell = _full_rule("ziwei.quanshu.j2.five_phase_bureau_from_life_palace")[
        "conclusion"
    ]["cells"][STEM_LABELS[year_stem]][BRANCH_LABELS[life_palace]]
    palace_stem_branch, nayin, bureau_label = cell["chinese"].split("・")
    return {
        "bureau_id": cell["engine_rendering"],
        "bureau_label": bureau_label,
        "bureau_number": cell["bureau_number"],
        "life_palace_stem_branch": palace_stem_branch,
        "nayin": nayin,
    }


@lru_cache(maxsize=8)
def _ziwei_day_table(bureau_id: str) -> dict[int, str]:
    """Lunar day -> Zi Wei's branch, inverted from the pack's printed grid."""
    rendering = _full_rule("ziwei.quanshu.j2.place_ziwei." + bureau_id)["conclusion"][
        "engine_rendering"
    ]
    return {day: branch for branch, days in rendering.items() for day in days}


def ziwei_star_branch(bureau_id: str, lunar_day: int) -> str:
    return _ziwei_day_table(bureau_id)[lunar_day]


def tianfu_star_branch(ziwei_star: str) -> str:
    """Tian Fu reflects Zi Wei in the Yin-Shen axis; they share only those two."""
    cell = _full_rule("ziwei.quanshu.j2.place_tianfu_mirror_of_ziwei")["conclusion"][
        "cells"
    ][BRANCH_LABELS[ziwei_star]]
    return cell["engine_rendering"]


def main_star_branches(ziwei_star: str) -> dict[str, dict[str, str]]:
    """All fourteen, from the two couplets of An nanbeidou zhuxing jue."""
    tianfu = tianfu_star_branch(ziwei_star)
    out: dict[str, dict[str, str]] = {}
    back = _full_rule("ziwei.quanshu.j2.place_ziwei_series_six_stars")["conclusion"][
        "cells"
    ]
    forward = _full_rule("ziwei.quanshu.j2.place_tianfu_series_eight_stars")[
        "conclusion"
    ]["cells"]
    for label, cell in back.items():
        index = (BRANCHES.index(ziwei_star) - cell["offset_backward"]) % 12
        out[MAIN_STAR_IDS[label]] = {"chinese": label, "branch": BRANCHES[index]}
    for label, cell in forward.items():
        index = (BRANCHES.index(tianfu) + cell["offset_forward"]) % 12
        out[MAIN_STAR_IDS[label]] = {"chinese": label, "branch": BRANCHES[index]}
    return out


@lru_cache(maxsize=1)
def _brightness_index() -> dict[tuple[str, str], str]:
    """(star label, branch) -> the printed brightness level, as Chinese."""
    cells = _full_rule("ziwei.quanshu.j2.brightness_table_twelve_branches")[
        "conclusion"
    ]["cells"]
    index: dict[tuple[str, str], str] = {}
    for branch_label, levels in cells.items():
        branch = _BRANCH_BY_LABEL[branch_label]
        for level, cell in levels.items():
            for star in cell["engine_rendering"]:
                index[(star, branch)] = level
    return index


def brightness(star_label: str, branch: str) -> str | None:
    """The seven-level 廟旺得地利益平和不得地落陷 grading, or None if unlisted.

    The grid covers twenty-one stars and no others. A star it does not list has
    no brightness in this source, and none may be imported from a later school.
    """
    return _brightness_index().get((star_label, branch))


# Every auxiliary table in the wider pack that this section places, with the
# chart fact each is keyed to. The tables themselves stay in the manifest; only
# the key is named here, because only the key is engine knowledge.
AUXILIARY_TABLES: tuple[tuple[str, str, str], ...] = (
    ("tiankui_tianyue", "ziwei.quanshu.j2.place_tiankui_tianyue_by_year_stem", "year_stem"),
    ("lucun", "ziwei.quanshu.j2.place_lucun_by_year_stem", "year_stem"),
    ("jielu_kongwang", "ziwei.quanshu.j2.place_jielu_kongwang_by_year_stem", "year_stem"),
    ("tianma", "ziwei.quanshu.j2.place_tianma_by_year_branch", "year_branch"),
    ("huoxing_lingxing", "ziwei.quanshu.j2.place_huoxing_lingxing_by_year_branch", "year_branch"),
    ("tianku_tianxu", "ziwei.quanshu.j2.place_tianku_tianxu_by_year_branch", "year_branch"),
    ("longchi_fengge", "ziwei.quanshu.j2.place_longchi_fengge_by_year_branch", "year_branch"),
    ("hongluan_tianxi", "ziwei.quanshu.j2.place_honglun_tianxi_by_year_branch", "year_branch"),
    ("shen_zhu", "ziwei.quanshu.j2.assign_shen_zhu", "year_branch"),
    ("tiankong_dijie", "ziwei.quanshu.j2.place_tiankong_dijie_by_hour", "hour_branch"),
    ("taifu_fenggao", "ziwei.quanshu.j2.place_taifu_fenggao_by_hour", "hour_branch"),
    ("tianxing_tianyao", "ziwei.quanshu.j2.place_tianxing_tianyao_by_month", "chart_month"),
    ("ming_zhu", "ziwei.quanshu.j2.assign_ming_zhu", "life_palace"),
    ("qingyang_tuoluo", "ziwei.quanshu.j2.place_qingyang_tuoluo_from_lucun", "lucun_branch"),
)


def _aux_key(kind: str, keys: dict[str, Any]) -> str:
    if kind == "year_stem":
        return STEM_LABELS[keys["year_stem"]]
    if kind == "chart_month":
        return str(keys["chart_month"])
    return BRANCH_LABELS[keys[kind]]


def auxiliary_placements(**keys: Any) -> dict[str, dict[str, Any]]:
    """Every auxiliary table the wider pack supplies, resolved for one chart.

    Qing Yang and Tuo Luo follow Lu Cun rather than the birth data, so Lu Cun is
    resolved first and fed back in - which is also the order the source states.
    """
    out: dict[str, dict[str, Any]] = {}
    for name, rule_id, kind in AUXILIARY_TABLES:
        if kind == "lucun_branch" and "lucun" in out:
            keys = {**keys, "lucun_branch": out["lucun"]["engine_rendering"]}
        rule = _full_rule(rule_id)
        cell = rule["conclusion"]["cells"][_aux_key(kind, keys)]
        out[name] = {
            "chinese": cell["chinese"],
            "engine_rendering": cell["engine_rendering"],
            "keyed_to": kind,
            "source_section": rule["source_passages"][0]["section"],
        }
    return out


def xunzhong_kongwang(year_stem: str, year_branch: str) -> dict[str, Any]:
    """The two branches left unpaired by the birth year's run of ten.

    Six runs of ten sexagenary pairs over twelve branches leaves two branches
    out of each run; the pack lists all six and they cover the circle exactly.
    """
    stems, branches = _sexagenary()
    index = next(
        i for i in range(60)
        if stems[i % 10] == year_stem and branches[i % 12] == year_branch
    )
    head = "甲" + BRANCH_LABELS[branches[(index - index % 10) % 12]]
    cell = _full_rule("ziwei.quanshu.j2.place_xunzhong_kongwang")["conclusion"][
        "cells"
    ][head]
    return {"run": head, "chinese": cell["chinese"],
            "engine_rendering": cell["engine_rendering"]}


def santai_bazuo(zuofu: str, youbi: str, lunar_day: int) -> dict[str, str]:
    """Day one sits on the anchor star itself; count forward, then backward."""
    return {
        "santai": BRANCHES[(BRANCHES.index(zuofu) + lunar_day - 1) % 12],
        "bazuo": BRANCHES[(BRANCHES.index(youbi) - (lunar_day - 1)) % 12],
    }


def tianshang_tianshi(topics: dict[str, str]) -> dict[str, str]:
    """The passage's verse and its prose disagree; the named palaces win.

    The verse says six palaces before and after the life palace, which would
    put both stars in the travel palace. The prose names the servants and
    illness palaces, and the pack records the contradiction rather than hiding
    it. Nothing is judged from either star here.
    """
    return {
        "tianshang": topics["servants_historical_label"],
        "tianshi": topics["illness"],
    }


def star_attributions(star_labels: list[str]) -> dict[str, dict[str, str]]:
    """Element, Dipper and office for the placed stars, from the printed list."""
    cells = _full_rule("ziwei.quanshu.j2.star_five_phase_and_dipper_attributions")[
        "conclusion"
    ]["cells"]
    return {
        MAIN_STAR_IDS[label]: {
            "chinese": cells[label]["chinese"],
            "engine_rendering": cells[label]["engine_rendering"],
        }
        for label in star_labels
        if label in cells
    }


def judgment_hierarchy() -> list[dict[str, str]]:
    """The order juan 3 numbers for itself, as an ordered list."""
    cells = _full_rule("ziwei.quanshu.j3.judgment_hierarchy")["conclusion"]["cells"]
    return [
        {"step": key, "chinese": cell["chinese"],
         "engine_rendering": cell["engine_rendering"]}
        for key, cell in cells.items()
        if cell.get("output_policy") != "refused"
    ]


def _vector(vector_id: str) -> dict[str, Any]:
    return next(
        vector
        for vector in _pack(ZIWEI_VECTORS)["vectors"]
        if vector["vector_id"] == vector_id
    )


@lru_cache(maxsize=1)
def _sexagenary() -> tuple[list[str], list[str]]:
    """Stem/branch ids in the Zi Wei pack's plain spelling.

    The BaZi kernel disambiguates the stem Wu (戊) from the branch Wu (午) - and
    the branch Yin (寅) from nothing, since only the branch collides - by
    suffixing `wu_stem`/`wu_branch`. BaZi's own module keeps that spelling
    throughout its tables; the Zi Wei pack's vectors and its Four
    Transformations table are written in the plain form ("wu" for both), so the
    suffix is stripped here at the one place this module reads the kernel.
    """
    cycle = _pack(BAZI_KERNEL)["cycle"]
    stems = [
        s["id"].removesuffix("_stem")
        for s in sorted(cycle["stems"], key=lambda s: s["index"])
    ]
    branches = [
        b["id"].removesuffix("_branch")
        for b in sorted(cycle["branches"], key=lambda b: b["index"])
    ]
    return stems, branches


def year_stem_branch(label_year: int) -> tuple[str, str]:
    """Sexagenary year from the kernel's cycle, anchored at 1984 = Jia-Zi.

    Pure cycle arithmetic on an already-resolved sui label year. It does not
    decide which boundary turns the year - see `_lunar_sui_year` and
    `_year_boundary_fork` for that, since a civil Gregorian year number is
    right for most of the year and wrong for everything born before its
    lunar new year.
    """
    stems, branches = _sexagenary()
    index = (label_year - 1984) % 60
    return stems[index % 10], branches[index % 12]


def _lunar_sui_year(civil_day: date) -> int:
    """The Gregorian year label conventionally paired with this birth's sui.

    A Chinese sexagenary year is named for the Gregorian year its lunar new
    year falls in ("1996" is Bing-Zi from 1996-02-19 to the next new year).
    The panel's lunisolar kernel keys `LunarYear.anchor_year` to the December
    solstice that opens month 11, one calendar year earlier than that label,
    so the label is `anchor_year + 1` - not `civil_day.year`, which is only
    right after the year's own new year has passed.
    """
    lunar = vietnamese.lunar_date(civil_day, 8.0)
    return lunar["lunar_year"].anchor_year + 1


def build(birth: BirthInput, bases: TimeBases) -> TraditionSection:
    manifest = _pack(ZIWEI_MANIFEST)
    section = TraditionSection(
        tradition_id="ziwei_doushu",
        display_name="Zi Wei Dou Shu (Purple Star)",
        evidence_grade=EvidenceGrade.TRANSCRIPTION,
        basis=(
            "Grade-D construction rules transcribed from Ziwei Doushu Quanshu "
            "juan 2, base facsimile unidentified. The chart month comes from the "
            "panel's validated lunisolar kernel as a disclosed configured method, "
            "gated on agreeing across every plausible calendar regime."
        ),
    )
    section.disclose(
        DisclosureKind.SOURCE,
        "Pack provenance and grade",
        "All seven construction rules come from "
        f"{manifest['source_pack_id']}, transcribed from Chinese Wikisource juan 2. "
        "The page identifies no base scan, collation history or relation to the "
        "Quanji or Jielan printings, so every rule carries evidence grade D and "
        "review status 'facsimile collation and Chinese review pending'. This is a "
        "transcription, not a controlling edition. It is strong enough to place a "
        "palace and far too weak to say what a palace means.",
    )

    regimes = _calendar_regime_readings(birth.civil_date)
    chart_months = {reading["chart_month"] for reading in regimes}
    lunar_days = {reading["lunar_day"] for reading in regimes}
    month_is_invariant = len(chart_months) == 1

    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Civil-to-lunisolar conversion",
        "The research pack registers no calendar and its audit forbids a "
        "ziwei_default, so the pack fails closed and is unchanged. The conversion "
        "is supplied here instead, at the product layer, by the same true-new-moon "
        "and true-solar-term kernel the panel already validates: month 11 anchored "
        "to the winter solstice, leap month inserted where no principal term "
        "falls. That is the substance of the Chinese 农历 rule; what the sources "
        "leave open is the meridian it is reckoned at, so rather than pick one, "
        "this section computes all three and reports whether the pick matters.",
        tuple(reading["label"] for reading in regimes),
    )

    if month_is_invariant:
        chart_month = next(iter(chart_months))
        section.disclose(
            DisclosureKind.FORK,
            "Calendar regime - tested and empty for this birth",
            "All three regimes return chart month "
            f"{chart_month}, so the meridian does not move the life palace, the "
            "body palace, the twelve topics, or Zuofu/Youbi. The configuration "
            "above is disclosed for honesty, but for this birth there is nothing "
            "for it to decide. "
            + (
                "The lunar DAY does differ across regimes ("
                + ", ".join(
                    f"{reading['regime_id']}={reading['lunar_day']}"
                    for reading in regimes
                )
                + "), which is exactly why everything keyed to the day stays "
                "refused below."
                if len(lunar_days) > 1
                else "The lunar day agrees across regimes too, but the day-keyed "
                "placements stay refused for a separate reason: the pack supplies "
                "no five-phase bureau table."
            ),
        )
    else:
        chart_month = None
        section.disclose(
            DisclosureKind.REFUSAL,
            "The chart itself",
            "Refused. The calendar regimes disagree about this birth's chart "
            "month ("
            + ", ".join(
                f"{reading['regime_id']}={reading['chart_month']}"
                for reading in regimes
            )
            + "), so the life palace is not determined and neither is anything "
            "downstream of it. This is the gate working, not a missing feature: "
            "a birth within a day or two of a new moon can land here.",
        
        category="school_fork_unresolved",
    )

    day_is_invariant = len(lunar_days) == 1
    if day_is_invariant:
        section.disclose(
            DisclosureKind.SOURCE,
            "Five-phase bureau, Zi Wei, and the fourteen main stars",
            "Computed. These used to be refused here on the stated ground that "
            "the pack held no bureau table and no Zi Wei placement table. It "
            "held both, in the same juan: five verses with five twelve-palace "
            "day grids for Zi Wei, a captioned diagram for Tian Fu, two couplets "
            "for the fourteen main stars, and a seven-level brightness grid. The "
            "bureau is not printed as a grid at all - it is the Five Tigers "
            "couplets composed with the sixty-jiazi nayin song, which is exactly "
            "what the chapter's own worked example does. All three juan are now "
            "encoded as quanshu_full_rule_manifest.json (83 rules, 100 vectors).",
            (
                f"Lunar day {next(iter(lunar_days))} is the same under all three "
                "calendar regimes, which is what lets the bureau be computed at all.",
            ),
        )
        section.disclose(
            DisclosureKind.CONFIGURED_METHOD,
            "Zi Wei's day table - printed grid against derived rule",
            "The five printed grids are the authority; a closed form recovered "
            "from them is used to check them. It reproduces 58 of the 60 printed "
            "cells and all ten day anchors the verses state in words. The two "
            "cells it does not reproduce are single-character defects in the "
            "transcription, each detectable because a bureau grid must partition "
            "the thirty days exactly once: 木三局 at Yin prints a day that already "
            "stands elsewhere, and 金四局 at Hai leaves the grid one day short. "
            "The closed form is followed at those two cells and the disagreement "
            "is disclosed rather than hidden.",
            ("The printed cell as transcribed, at the two defective positions",),
        )
    else:
        section.disclose(
            DisclosureKind.REFUSAL,
            "Five-phase bureau, Zi Wei's own star, and the main-star sequences",
            "Refused - and for this birth the reason is real rather than "
            "bibliographic. The tables exist and are encoded; the INPUT does not "
            "survive. The bureau is keyed to the lunar DAY, and the day differs "
            "between calendar regimes for this birth ("
            + ", ".join(
                f"{reading['regime_id']}={reading['lunar_day']}"
                for reading in regimes
            )
            + "). Zi Wei's palace is therefore not determined, and neither is any "
            "of the fourteen main stars that follow from it. The palaces below "
            "are an empty board for this birth only.",
            category="school_fork_unresolved",
        )
    section.disclose(
        DisclosureKind.FORK,
        "Five Tigers palace-stem sequence",
        "The earlier seven-rule pack forbade this table outright - 'do not use "
        "until Chinese characters and pairings are collated' - and it was not "
        "computed here. The characters are now recorded, and the chapter's own "
        "worked example (Jia year, life palace at Yin, 丙寅, furnace fire, the six "
        "bureau) exercises the Jia/Ji row end to end inside the source. The "
        "prohibition is narrowed rather than lifted: the table drives the bureau "
        "above, and its derivation is shown every time rather than just its answer.",
        ("The older pack's blanket refusal, kept in calculation_rule_manifest.json",),
    )
    if birth.sex in ("male", "female"):
        section.disclose(
            DisclosureKind.REFUSAL,
            "Decade and annual limits",
            "Refused, and the reason has narrowed. The birth input now carries a "
            f"sex ({birth.sex}), so the direction of the decade limits IS "
            "decidable from the year-stem parity - that half of the blocker is "
            "gone. What remains is the pack's own audit requirement: a declared "
            "historical convention and a safe modern input mapping must be fixed "
            "before the rule may run. That is a source and policy gate, not a "
            "missing field.",
            category="school_fork_unresolved",
        )
    else:
        section.disclose(
            DisclosureKind.REFUSAL,
            "Decade and annual limits",
            "Refused. The direction of the decade limits depends on the "
            "birth-year stem's yin/yang parity combined with the subject's sex, "
            "and no sex was supplied for this birth. The input contract accepts "
            "one; supplying it removes half this blocker. The audit additionally "
            "requires a declared historical convention and a safe modern input "
            "mapping before the rule may run at all. Nothing here guesses it.",
            category="missing_user_input",
        )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Star meanings and any reading",
        "Refused. Every rule in the pack carries a publication limit forbidding "
        "prose meaning before construction reproduces facsimile-backed worked "
        "charts, and the source audit warns that a list of isolated star keywords "
        "is not a reading. Everything below is a position, not a judgment.",
    
        category="policy_suppressed",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "The Daoist-canon homonym",
        "A different three-juan work in the Zhengtong Daozang shares the title "
        "Ziwei Doushu but differs in star names and construction. It is never used "
        "to fill a gap in this system, including the gaps named above.",
    
        category="not_part_of_tradition",
    )
    section.disclose(
        DisclosureKind.CONFIGURED_METHOD,
        "Double-hour partition and boundary",
        "The twelve shichen are taken from the validated BaZi sexagenary kernel "
        "(Zi opening at 23:00), because the Zi Wei pack states its own "
        "double-hour boundary must be established from golden examples and "
        "declines to default it. Two of the twelve double-hours - Zi and Chou - "
        "have golden vectors in this pack; the other ten rest on the stated "
        "counting rule alone.",
        ("Zi centred on midnight (23:00-01:00 split across days)",
         "A printed almanac's shichen table"),
    )

    candidates = {
        "true_solar_time": bases.true_solar_time,
        "clock_time": birth.civil_datetime,
        "local_mean_time": bases.local_mean_time,
    }
    placements: dict[str, dict[str, Any]] = {}
    for label, moment in candidates.items():
        branch = double_hour_branch(moment)
        entry: dict[str, Any] = {
            "time": moment.strftime("%H:%M:%S"),
            "double_hour_branch": branch,
            "double_hour_label": BRANCH_LABELS[branch],
            "wenchang_branch": wenchang_branch(branch),
            "wenqu_branch": wenqu_branch(branch),
        }
        if chart_month is not None:
            entry["life_palace_branch"] = life_palace_branch(chart_month, branch)
            entry["body_palace_branch"] = body_palace_branch(chart_month, branch)
        placements[label] = entry

    primary = placements["true_solar_time"]
    if primary["double_hour_branch"] != placements["clock_time"]["double_hour_branch"]:
        section.disclose(
            DisclosureKind.FORK,
            "Double-hour basis",
            f"True solar time ({primary['time']}) and clock time "
            f"({placements['clock_time']['time']}) fall in different shichen, so "
            "the life palace, the body palace, Wenchang and Wenqu all land on "
            "different branches under each. Both are shown; neither is asserted, "
            "because the pack fixes no boundary.",
            ("Clock time", "Local mean time"),
        )
    else:
        section.disclose(
            DisclosureKind.CONFIGURED_METHOD,
            "Double-hour basis",
            "True solar time is listed first. For this birth all three time bases "
            "fall in the same shichen, so the choice does not move the stars.",
            ("Clock time", "Local mean time"),
        )

    section.facts = {
        "source_profile": {
            "source_pack_id": manifest["source_pack_id"],
            "source_edition_id": manifest["source_edition_id"],
            "implementation_status": manifest["implementation_status"],
            "publication_status": manifest["publication_status"],
            "evidence_grade_of_every_rule": "D",
            "review_status": "facsimile_collation_and_chinese_review_pending",
        },
        "calendar_regime_check": {
            "purpose": (
                "The chart month is the whole chart's first input and the pack "
                "supplies no calendar. Rather than assert a meridian, run every "
                "plausible one and require agreement."
            ),
            "regimes": regimes,
            "chart_month_invariant": month_is_invariant,
            "chart_month": chart_month,
            "lunar_day_invariant": len(lunar_days) == 1,
            "kernel": (
                "Panel lunisolar kernel: true new moon for month starts, winter "
                "solstice anchoring month 11, no-principal-term leap insertion."
            ),
        },
        "hour_keyed_placements": placements,
        "twelve_topic_palace_order": _rule(
            "ziwei.quanshu.j2.place_twelve_topic_palaces"
        )["conclusion"]["topics"],
        "vector_selfcheck": _vector_selfcheck(),
    }

    if chart_month is None:
        section.facts["chart_construction"] = {
            "status": "blocked_calendar_regimes_disagree",
            "blocking_input": "chart lunar month (regular or intercalary)",
        }
        return section

    hour_branch = primary["double_hour_branch"]
    life = life_palace_branch(chart_month, hour_branch)
    body = body_palace_branch(chart_month, hour_branch)
    topics = topic_palaces(life)
    sui_year = _lunar_sui_year(birth.civil_date)
    year_stem, year_branch = year_stem_branch(sui_year)

    section.facts["chart_construction"] = {
        "status": "constructed_palaces_only",
        "chart_month": chart_month,
        "month_palace_branch": month_palace_branch(chart_month),
        "life_palace": {"branch": life, "label": BRANCH_LABELS[life]},
        "body_palace": {"branch": body, "label": BRANCH_LABELS[body]},
        "topic_palaces": {
            topic: {
                "branch": branch,
                "branch_label": BRANCH_LABELS[branch],
                "topic_label": TOPIC_LABELS[topic],
            }
            for topic, branch in topics.items()
        },
        "month_keyed_stars": {
            "zuofu": {
                "branch": zuofu_branch(chart_month),
                "label": BRANCH_LABELS[zuofu_branch(chart_month)],
            },
            "youbi": {
                "branch": youbi_branch(chart_month),
                "label": BRANCH_LABELS[youbi_branch(chart_month)],
            },
        },
        "hour_keyed_stars": {
            "wenchang": {
                "branch": primary["wenchang_branch"],
                "label": BRANCH_LABELS[primary["wenchang_branch"]],
            },
            "wenqu": {
                "branch": primary["wenqu_branch"],
                "label": BRANCH_LABELS[primary["wenqu_branch"]],
            },
        },
        "still_absent": [
            (
                "decade and annual limits (sex supplied; blocked now only on the "
                "pack's declared-convention requirement)"
                if birth.sex in ("male", "female") else
                "decade and annual limits (no sex supplied for this birth)"
            ),
            "the twelve-stage cycle and the twelve gods (same gate)",
            "any meaning whatsoever",
        ]
        + (
            []
            if len(lunar_days) == 1
            else [
                "five-phase bureau (table exists; the lunar day differs between "
                "calendar regimes for this birth, so the input does not)",
                "Zi Wei's own star and the fourteen main stars (downstream of "
                "the bureau)",
                "brightness (nothing placed to grade)",
            ]
        ),
    }

    section.facts["auxiliary_placements"] = {
        "note": (
            "Fourteen further tables from the wider pack, none of them keyed to "
            "the lunar day, so all of them survive whatever the calendar regimes "
            "do to the day. Positions only."
        ),
        "tables": auxiliary_placements(
            year_stem=year_stem,
            year_branch=year_branch,
            hour_branch=hour_branch,
            chart_month=chart_month,
            life_palace=life,
        ),
        "xunzhong_kongwang": xunzhong_kongwang(year_stem, year_branch),
        "tianshang_tianshi": {
            "placement": tianshang_tianshi(topics),
            "internal_contradiction": (
                "The verse counts six palaces either side of the life palace, "
                "which would put both stars in the travel palace; the prose "
                "immediately names the servants and illness palaces. The named "
                "form is followed and the disagreement is published."
            ),
        },
        "not_placed_here": {
            "target_year_layer": (
                "The four annual flying stars, Dou Jun, Tian De / Yue De / Jie "
                "Shen, the flying three slayers and the flowing Lu, Yang and Tuo "
                "are all keyed to a TARGET year. This panel reads a birth, not a "
                "year, so their tables are encoded in the pack and not placed."
            ),
            "sex_gated": (
                "The twelve-stage cycle, the twelve gods, the decade limits and "
                "the small limits are fully transcribed and all four have a "
                "direction that depends on sex as a historical binary category. "
                "This panel collects no such input and guesses none."
            ),
        },
    }
    section.facts["judgment_hierarchy"] = {
        "source": "Ziwei Doushu Quanshu juan 3, 谈星要论 - the chapter numbers its own steps",
        "steps": judgment_hierarchy(),
        "executed_here": False,
        "why_not": (
            "The hierarchy is the order a reading would be built in. This section "
            "renders no reading, so it publishes the order as a source fact and "
            "stops. The chapter's closing grade ladder, which sorts whole lives "
            "from noble down to 'a beast's fate', is refused in the pack."
        ),
    }
    section.facts["child_limit_sequence"] = {
        "chinese": _full_rule("ziwei.quanshu.j2.place_tong_xian_child_limits")[
            "conclusion"
        ]["cells"]["sequence"]["chinese"],
        "engine_rendering": _full_rule(
            "ziwei.quanshu.j2.place_tong_xian_child_limits"
        )["conclusion"]["cells"]["sequence"]["engine_rendering"],
        "note": (
            "The one limit rule in the work that is not sex-gated. The sequence "
            "is published; nothing is predicted from it, and this panel's own "
            "refusal of child prediction stands regardless."
        ),
    }

    if len(lunar_days) == 1:
        lunar_day = next(iter(lunar_days))
        bureau_facts = bureau(year_stem, life)
        ziwei_star = ziwei_star_branch(bureau_facts["bureau_id"], lunar_day)
        stars = main_star_branches(ziwei_star)
        topic_of = {branch: topic for topic, branch in topics.items()}
        section.facts["main_star_board"] = {
            "lunar_day": lunar_day,
            "lunar_day_invariant_across_regimes": True,
            "bureau": bureau_facts,
            "bureau_derivation": (
                f"Five Tigers puts {bureau_facts['life_palace_stem_branch'][0]} at "
                f"Yin, so the life palace at {BRANCH_LABELS[life]} is "
                f"{bureau_facts['life_palace_stem_branch']}; the nayin song calls "
                f"that {bureau_facts['nayin']}, and that element is the "
                f"{bureau_facts['bureau_label']}."
            ),
            "ziwei_branch": ziwei_star,
            "tianfu_branch": tianfu_star_branch(ziwei_star),
            "same_palace_pair": ziwei_star in ("yin", "shen"),
            "stars": {
                star_id: {
                    "chinese": entry["chinese"],
                    "branch": entry["branch"],
                    "branch_label": BRANCH_LABELS[entry["branch"]],
                    "topic_palace": topic_of.get(entry["branch"]),
                    "brightness": brightness(entry["chinese"], entry["branch"]),
                    "meaning": "refused",
                }
                for star_id, entry in stars.items()
            },
            "life_palace_stars": sorted(
                entry["chinese"] for entry in stars.values()
                if entry["branch"] == life
            ),
            "star_attributions": star_attributions(
                [entry["chinese"] for entry in stars.values()]
            ),
            "day_keyed_auxiliaries": {
                "note": (
                    "San Tai and Ba Zuo count from Zuo Fu and You Bi by the "
                    "lunar day, so they sit behind the same day gate as the "
                    "bureau and appear only here."
                ),
                **santai_bazuo(
                    zuofu_branch(chart_month), youbi_branch(chart_month), lunar_day
                ),
            },
            "meaning": (
                "refused - the wider pack's 355 delineation cells are research "
                "evidence with per-cell output policy, and 193 of them are refused "
                "outright. None of them reaches this section."
            ),
        }
    section.facts["four_transformations"] = {
        "birth_year_stem": year_stem,
        "birth_year_branch": year_branch,
        "year_boundary_fork": _year_boundary_fork(birth, bases, sui_year),
        "lineage": (
            "Ziwei Doushu Quanshu juan 2, Wikisource transcription candidate - "
            "displayed under the rule's own publication limit, which requires the "
            "lineage be shown and forbids merging any later school's table."
        ),
        "transformations": four_transformations(year_stem),
        "meaning": "refused - the pack permits the table, not its interpretation",
    }
    section.disclose(
        DisclosureKind.FORK,
        "Four Transformations table lineage",
        "The table below is this transcription's. Its own rule records "
        "conflicts_with 'ziwei.other_school.four_transformations_table' and warns "
        "that later schools use variant tables. This section holds exactly one "
        "witness, so it cannot tell you whether the row it used is among the "
        "disputed ones - only that the row shown is the one this text prints. "
        "The stars are named and left unread.",
        ("Later-school Four Transformations tables (not held here)",),
    )
    return section


def _year_boundary_fork(
    birth: BirthInput, bases: TimeBases, lunar_new_year_sui: int
) -> dict[str, Any]:
    """Does the Zi Wei year boundary change this birth's year stem?

    Two live conventions exist and this pack picks neither. Most Zi Wei
    transmission turns the sui at the lunar new year, matching the system's own
    lunisolar chart month; some modern practice borrows BaZi's Li Chun
    (solar longitude 315 degrees) boundary instead, to keep the two systems'
    year pillars aligned. They disagree only in whichever short window falls
    between the two boundaries in a given year - which can run either order,
    since Li Chun (~Feb 4) and lunar new year (Jan 21 - Feb 20) both move.
    Rather than assert one, both are computed and compared directly.
    """
    from .bazi import _find_term  # precise solar-term search; not restated here

    li_chun_jd = _find_term(315, swe.julday(birth.civil_date.year, 1, 1, 0.0))
    li_chun_sui = (
        birth.civil_date.year
        if bases.julian_day_ut >= li_chun_jd
        else birth.civil_date.year - 1
    )
    agree = li_chun_sui == lunar_new_year_sui
    return {
        "lunar_new_year_convention_sui_year": lunar_new_year_sui,
        "li_chun_convention_sui_year": li_chun_sui,
        "conventions_agree": agree,
        "verdict": (
            "empty - both candidate year boundaries assign the same sexagenary "
            "year to this birth"
            if agree
            else "LIVE - the two candidate year boundaries disagree for this "
            "birth, so the year stem and the Four Transformations table row "
            "depend on which convention is followed"
        ),
    }


def _vector_selfcheck() -> dict[str, Any]:
    """Reproduce the pack's published examples. None of this is this birth."""
    results: dict[str, Any] = {
        "note": (
            "Reproduction of the pack's own transcription vectors, to show the "
            "arithmetic matches the source examples. Not this birth's chart."
        )
    }
    for vector_id in (
        "ziwei.quanshu.wenchang_wenqu.zi",
        "ziwei.quanshu.wenchang_wenqu.chou",
    ):
        vector = _vector(vector_id)
        hour = vector["inputs"]["double_hour_branch"]
        results[vector_id] = {
            "input_double_hour": hour,
            "wenchang": wenchang_branch(hour),
            "wenqu": wenqu_branch(hour),
            "matches_source_example": (
                wenchang_branch(hour) == vector["expected"]["wenchang_branch"]
                and wenqu_branch(hour) == vector["expected"]["wenqu_branch"]
            ),
        }
    for vector_id in (
        "ziwei.quanshu.life_body.month1_zi",
        "ziwei.quanshu.life_body.month1_chou",
        "ziwei.quanshu.life_body.month1_yin",
    ):
        vector = _vector(vector_id)
        month = vector["inputs"]["chart_lunar_month"]
        hour = vector["inputs"]["double_hour_branch"]
        results[vector_id] = {
            "input_chart_month": month,
            "input_double_hour": hour,
            "life_palace": life_palace_branch(month, hour),
            "body_palace": body_palace_branch(month, hour),
            "matches_source_example": (
                life_palace_branch(month, hour) == vector["expected"][
                    "life_palace_branch"
                ]
                and body_palace_branch(month, hour) == vector["expected"][
                    "body_palace_branch"
                ]
            ),
        }
    for vector_id in (
        "ziwei.quanshu.zuofu_youbi.month1",
        "ziwei.quanshu.zuofu_youbi.month2",
    ):
        vector = _vector(vector_id)
        month = vector["inputs"]["source_scoped_lunar_month"]
        results[vector_id] = {
            "input_month": month,
            "zuofu": zuofu_branch(month),
            "youbi": youbi_branch(month),
            "matches_source_example": (
                zuofu_branch(month) == vector["expected"]["zuofu_branch"]
                and youbi_branch(month) == vector["expected"]["youbi_branch"]
            ),
        }
    leap_vector = _vector("ziwei.quanshu.leap_month1_normalization")
    normalized = normalize_chart_month(
        leap_vector["inputs"]["recorded_lunar_month"],
        leap_vector["inputs"]["is_intercalary"],
    )
    results["ziwei.quanshu.leap_month1_normalization"] = {
        "input": leap_vector["inputs"],
        "chart_month": normalized,
        "matches_source_example": (
            normalized == leap_vector["expected"]["chart_lunar_month_for_life_body"]
        ),
    }
    trans_vector = _vector("ziwei.quanshu.four_transformations.jia")
    computed = four_transformations(trans_vector["inputs"]["birth_year_stem"])
    results["ziwei.quanshu.four_transformations.jia"] = {
        "input_year_stem": trans_vector["inputs"]["birth_year_stem"],
        "transformations": computed,
        "matches_source_example": computed == trans_vector["expected"],
    }
    topic_vector = _vector("ziwei.quanshu.topic_palaces.reverse_from_zi")
    computed_topics = topic_palaces(topic_vector["inputs"]["life_palace_branch"])
    results["ziwei.quanshu.topic_palaces.reverse_from_zi"] = {
        "input_life_palace": topic_vector["inputs"]["life_palace_branch"],
        "matches_source_example": (
            computed_topics == topic_vector["expected"]["assignments"]
        ),
    }
    results["five_tigers_table"] = "not_implemented_by_pack_instruction"
    return results
