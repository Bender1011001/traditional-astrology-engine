"""Zi Wei Dou Shu section.

The pack behind this section is a transcription candidate, not a controlling
edition: seven grade-D rules read off the Chinese Wikisource text of
`Ziwei Doushu Quanshu` juan 2, whose base facsimile is unidentified. That grade
governs what may be computed here, and the answer is: almost nothing.

Chart construction in this system starts from the *lunar* birth month. The pack
supplies no civil-to-lunisolar conversion and its source audit forbids a
`ziwei_default` configuration, so the life palace, the body palace, the twelve
topic palaces and the month-keyed auxiliary stars are all unreachable - the
chart does not exist without its first input. The only placement whose sole
input is the double-hour is Wenchang/Wenqu, and it is emitted here with no
meaning attached, under both clock time and true solar time, because the pack
declines to fix the double-hour boundary too.
"""

from __future__ import annotations

import json
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

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


@lru_cache(maxsize=3)
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


def topic_palaces(life_palace_branch: str) -> dict[str, str]:
    """The twelve topics assigned in reverse branch order from the life palace.

    Pure source arithmetic. It has no birth input here because the life palace
    itself is unreachable; it exists so the pack's own vector can be reproduced.
    """
    topics = _rule("ziwei.quanshu.j2.place_twelve_topic_palaces")["conclusion"][
        "topics"
    ]
    start = BRANCHES.index(life_palace_branch)
    return {topic: BRANCHES[(start - i) % 12] for i, topic in enumerate(topics)}


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


def build(birth: BirthInput, bases: TimeBases) -> TraditionSection:
    manifest = _pack(ZIWEI_MANIFEST)
    section = TraditionSection(
        tradition_id="ziwei_doushu",
        display_name="Zi Wei Dou Shu (Purple Star)",
        evidence_grade=EvidenceGrade.TRANSCRIPTION,
        basis=(
            "Grade-D construction candidates transcribed from Ziwei Doushu Quanshu "
            "juan 2 on Chinese Wikisource, base facsimile unidentified. Only the "
            "hour-keyed Wenchang/Wenqu placement has all of its inputs; the chart "
            "proper does not, and is refused."
        ),
    )
    section.disclose(
        DisclosureKind.SOURCE,
        "Pack provenance and grade",
        "All seven rules come from "
        f"{manifest['source_pack_id']}, transcribed from Chinese Wikisource juan 2. "
        "The page identifies no base scan, collation history or relation to the "
        "Quanji or Jielan printings, so every rule carries evidence grade D and "
        "review status 'facsimile collation and Chinese review pending'. This is a "
        "transcription, not a controlling edition.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "The chart itself",
        "Refused - and not for want of effort. Life and body palace placement "
        "begins from the LUNAR birth month; the pack registers no approved "
        "civil-to-lunisolar conversion, and its source audit forbids a "
        "ziwei_default configuration, "
        "requiring instead a declared calendar version, leap-month convention and "
        "day boundary. Without the chart month there is no life palace; without the "
        "life palace there are no twelve topic palaces; and Zuofu/Youbi are keyed "
        "to the month as well. The Vietnamese lunisolar kernel elsewhere in this "
        "panel is NOT a substitute: it is a modern Vietnamese profile referenced to "
        "105 degrees east, and both audits forbid relabeling one tradition's "
        "calendar as another's.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Five Tigers and the Four Transformations",
        "Refused. The pack's own validation vector for the Five Tigers table sets "
        "implementation_allowed_before_facsimile_collation to false, so the table "
        "is not encoded here at all. The Four Transformations need the birth-year "
        "stem on the Zi Wei year boundary, which this pack does not fix, and the "
        "transcription's table is explicitly in conflict with later-school tables; "
        "keying it to this birth would assert a lineage the sources have not yet "
        "settled.",
    )
    section.disclose(
        DisclosureKind.REFUSAL,
        "Star meanings and any reading",
        "Refused. Every rule in the pack carries a publication limit forbidding "
        "prose meaning before construction reproduces facsimile-backed worked "
        "charts, and the source audit warns that a list of isolated star keywords "
        "is not a reading. The placement below is a position, not a judgment.",
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
    placements: dict[str, dict[str, str]] = {}
    for label, moment in candidates.items():
        branch = double_hour_branch(moment)
        placements[label] = {
            "time": moment.strftime("%H:%M:%S"),
            "double_hour_branch": branch,
            "double_hour_label": BRANCH_LABELS[branch],
            "wenchang_branch": wenchang_branch(branch),
            "wenqu_branch": wenqu_branch(branch),
        }

    primary = placements["true_solar_time"]
    if primary["double_hour_branch"] != placements["clock_time"]["double_hour_branch"]:
        section.disclose(
            DisclosureKind.FORK,
            "Double-hour basis",
            f"True solar time ({primary['time']}) and clock time "
            f"({placements['clock_time']['time']}) fall in different shichen, so "
            "Wenchang and Wenqu land on different branches under each. Both are "
            "shown; neither is asserted, because the pack fixes no boundary.",
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
        "chart_construction": {
            "status": "blocked_no_lunisolar_profile",
            "blocking_input": "chart lunar month (regular or intercalary)",
            "blocked_operations": [
                "life palace placement",
                "body palace placement",
                "twelve topic palace assignment",
                "Zuofu / Youbi placement (month-keyed)",
                "five-phase bureau and main-star sequences",
                "Four Transformations by birth-year stem",
                "Five Tigers palace-stem sequence",
                "decade and annual limits",
            ],
        },
        "hour_keyed_placements": placements,
        "twelve_topic_palace_order": _rule(
            "ziwei.quanshu.j2.place_twelve_topic_palaces"
        )["conclusion"]["topics"],
        "vector_selfcheck": _vector_selfcheck(),
    }
    return section


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
    topic_vector = _vector("ziwei.quanshu.topic_palaces.reverse_from_zi")
    computed = topic_palaces(topic_vector["inputs"]["life_palace_branch"])
    results["ziwei.quanshu.topic_palaces.reverse_from_zi"] = {
        "input_life_palace": topic_vector["inputs"]["life_palace_branch"],
        "matches_source_example": computed == topic_vector["expected"]["assignments"],
        "hypothetical_only": True,
    }
    results["five_tigers_table"] = "not_implemented_by_pack_instruction"
    return results
