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

The lunar DAY is a different matter, and the same check shows why. Day number
does move between regimes, so everything keyed to it - the five-phase bureau,
and therefore Zi Wei's own star sequence - stays refused.
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
        )

    section.disclose(
        DisclosureKind.REFUSAL,
        "Five-phase bureau, Zi Wei's own star, and the main-star sequences",
        "Refused, for two independent reasons either of which would be enough. "
        "The pack transcribes no five-phase bureau table and no Zi Wei placement "
        "table, so the arithmetic is simply absent. And the bureau is keyed to "
        "the lunar DAY, which - unlike the month - "
        + (
            "genuinely does move between calendar regimes for this birth."
            if len(lunar_days) > 1
            else "the pack fixes no day boundary for."
        )
        + " The palaces below are therefore an empty board: correct houses, with "
        "no main stars in them.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Five Tigers palace-stem sequence",
        "Refused, on the source's own instruction. This rule's publication limit "
        "reads 'Do not use this table until Chinese characters and pairings are "
        "collated against the selected facsimile', and the pack's vector sets "
        "implementation_allowed_before_facsimile_collation to false. It is the "
        "only rule in the pack that forbids its own use outright, and it is not "
        "computed here even though the year stem is known.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Decade and annual limits",
        "Refused. The direction of the decade limits depends on the birth-year "
        "stem's yin/yang parity combined with the subject's sex, and this panel "
        "does not collect a sex input. The audit additionally requires a declared "
        "historical convention and a safe modern input mapping before that rule "
        "may run at all. Nothing here guesses it.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Star meanings and any reading",
        "Refused. Every rule in the pack carries a publication limit forbidding "
        "prose meaning before construction reproduces facsimile-backed worked "
        "charts, and the source audit warns that a list of isolated star keywords "
        "is not a reading. Everything below is a position, not a judgment.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "The Daoist-canon homonym",
        "A different three-juan work in the Zhengtong Daozang shares the title "
        "Ziwei Doushu but differs in star names and construction. It is never used "
        "to fill a gap in this system, including the gaps named above.",
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
            "five-phase bureau (no table in pack; keyed to the lunar day)",
            "Zi Wei's own star and the fourteen main stars (no placement table)",
            "Five Tigers palace stems (source forbids use before collation)",
            "decade and annual limits (needs a sex input this panel does not take)",
            "brightness/temple table",
            "any meaning whatsoever",
        ],
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
