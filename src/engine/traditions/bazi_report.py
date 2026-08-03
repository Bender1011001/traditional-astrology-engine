"""A full BaZi (子平 Ziping) report.

The judgment order is the one Ziping practice actually uses, and it is nothing
like a Western chart reading:

  1. the four pillars, and which hour pillar the birth time actually supports
  2. the Day Master - the whole chart is read *relative to* the day stem
  3. month command (得令): whether the season supports or drains the Day Master
  4. the hidden stems, because the branches are where the real strength lives
  5. the Ten Gods, which turn raw stems into roles
  6. branch relations - harmonies, clashes, punishments, frames
  7. the luck pillars, which is where the reading becomes a life rather than a
     snapshot

Every delineation is quoted from the Yuanhai Ziping / Sanming Tonghui research
pack with its rule id. The pack's conditions are matched against computed facts;
where a rule's condition cannot be decided from what the engine computes, the
rule is not fired and the report says which ones were skipped and why, rather
than firing them loosely because they sound apt.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from ..multitradition import build_panel
from ..multitradition.types import BirthInput
from .report import Delineation, ReportSection, TraditionReport

RESEARCH_ROOT = (
    Path(__file__).resolve().parents[3] / "docs" / "research" / "multitradition"
)
DELINEATION_MANIFEST = (
    RESEARCH_ROOT / "bazi" / "yuanhai_ziping_delineation_manifest.json"
)

# The Ten Gods as the pack names them, mapped to the labels the engine emits.
TEN_GOD_KEYS = {
    "qi_sha": "七殺",
    "zheng_guan": "正官",
    "zheng_yin": "正印",
    "pian_yin": "偏印",
    "zheng_cai": "正財",
    "pian_cai": "偏財",
    "shi_shen": "食神",
    "shang_guan": "傷官",
    "bi_jian": "比肩",
    "jie_cai": "劫財",
}
SUPPORTIVE = {"比肩", "劫財", "正印", "偏印"}
DRAINING = {"食神", "傷官", "正財", "偏財", "正官", "七殺"}


@lru_cache(maxsize=1)
def _manifest() -> dict[str, Any]:
    return json.loads(DELINEATION_MANIFEST.read_text(encoding="utf-8"))


def _source_label(rule: dict[str, Any]) -> str:
    passages = rule.get("source_passages") or []
    if not passages:
        return rule.get("rule_id", "unknown")
    p = passages[0]
    return f"{p.get('work', 'Yuanhai Ziping')}, {p.get('section') or p.get('location') or ''}".strip().rstrip(",")


def _text_of(rule: dict[str, Any]) -> str | None:
    c = rule.get("conclusion", {}) or {}
    for key in ("engine_rendering", "judgment", "if_favor"):
        if isinstance(c.get(key), str) and c[key].strip():
            return c[key].strip()
    return None


def _suppressed(rule: dict[str, Any]) -> str | None:
    """The rule's own reason for not being rendered, if it carries one.

    Several of these rules are gendered or moralising fate-claims that the pack
    keeps as historical quotation and forbids as output. A rule whose CONDITION
    matches this chart is exactly the dangerous case - it would otherwise read
    as a personal verdict - so the policy is checked at fire time, not at
    extraction time.
    """
    c = rule.get("conclusion", {}) or {}
    policy = c.get("output_policy") or rule.get("output_policy")
    limit = rule.get("publication_limit")
    if isinstance(policy, str) and "refus" in policy.lower():
        return policy
    if isinstance(limit, str) and (
        "never rendered" in limit.lower() or "historical quotation only" in limit.lower()
    ):
        return limit
    return None


def _facts(birth: BirthInput) -> dict[str, Any]:
    panel = build_panel(birth)
    section = next(
        s for s in panel["sections"] if s["tradition_id"] == "chinese_bazi"
    )
    if section.get("error"):
        raise RuntimeError(f"BaZi calculation failed: {section['error']}")
    return section["facts"]


def _all_ten_gods(facts: dict[str, Any]) -> set[str]:
    """Every Ten God present, from visible stems AND hidden stems.

    Ziping reads hidden stems as real. A chart with no visible Officer but a
    rooted Officer in a branch is not an Officer-less chart, and treating it as
    one is the commonest way to misread a pillar set.
    """
    found: set[str] = set()
    for row in facts.get("visible_stem_ten_gods", []) or []:
        label = row.get("ten_god") if isinstance(row, dict) else None
        if label:
            found.add(label.split()[0])
    for _pillar, stems in (facts.get("hidden_stems") or {}).items():
        for s in stems:
            label = s.get("ten_god")
            if label:
                found.add(label.split()[0])
    return found


# Pack condition keys that name a Ten God (or a group of them) by presence.
PRESENCE_ALIASES: dict[str, tuple[str, ...]] = {
    "qi_sha": ("七殺",),
    "zheng_guan": ("正官",),
    "yin_seal_resource": ("正印", "偏印"),
    "natal_officer_star": ("正官",),
    "natal_shang_guan": ("傷官",),
    "shi_shen": ("食神",),
    "zheng_guan_or_qi_sha": ("正官", "七殺"),
    "wealth_officer_seal": ("正財", "偏財", "正官", "正印", "偏印"),
}
NAME_TO_GLYPH = {
    "qi_sha": "七殺", "zheng_guan": "正官", "zheng_yin": "正印",
    "pian_yin": "偏印", "zheng_cai": "正財", "pian_cai": "偏財",
    "shi_shen": "食神", "shang_guan": "傷官", "bi_jian": "比肩",
    "jie_cai": "劫財",
}


BRANCH_IDS = {
    "zi", "chou", "yin", "yin_branch", "mao", "chen", "si",
    "wu", "wu_branch", "wei", "shen", "you", "xu", "hai",
}


def _chart_branches(facts: dict[str, Any]) -> set[str]:
    """The four pillars' branch ids, for station/frame conditions."""
    out: set[str] = set()
    for _name, p in (facts.get("pillars") or {}).items():
        branch = p.get("branch")
        if branch:
            out.add(branch)
            # The kernel disambiguates two branches against stem names; the
            # pack sometimes spells them plain.
            out.add(branch.replace("_branch", ""))
    return out


def _luck_pillar_ten_gods(facts: dict[str, Any]) -> dict[str, set[str]]:
    """Ten God of each luck pillar's STEM, per direction.

    The pack keys several timing rules to "the luck pillar is X". Direction is
    undetermined without a sex input, so both sequences are computed and a rule
    fires only if the Ten God appears in a sequence - which is stated in the
    trigger so the reader knows it is direction-dependent.
    """
    from ..multitradition import bazi as _bazi

    day_stem = (facts.get("day_master") or {}).get("stem")
    out: dict[str, set[str]] = {}
    if not day_stem:
        return out
    for direction, seq in ((facts.get("luck_pillars") or {}).get("sequences") or {}).items():
        gods: set[str] = set()
        for row in seq:
            label = row.get("label", "")
            parts = label.split()
            if not parts:
                continue
            # The engine labels pillars as "丁 Ding 酉 You"; map the romanisation.
            roman = parts[1].lower() if len(parts) > 1 else ""
            try:
                key, _glyph = _bazi.ten_god(day_stem, roman)
                gods.add(key)
            except Exception:
                continue
        out[direction] = gods
    return out


def _condition_verdict(
    cond: Any, facts: dict[str, Any], present: set[str]
) -> tuple[bool | None, str]:
    """Decide a pack condition against computed facts.

    Returns (True/False/None, explanation). None means undecidable from what
    this engine computes - a real answer, and reported as one rather than
    quietly resolved in whichever direction would fire the rule.
    """
    if not isinstance(cond, dict):
        return None, "condition is not a structured mapping"

    checks: list[tuple[str, bool]] = []
    undecidable: list[str] = []
    hidden = facts.get("hidden_stems") or {}
    dm = facts.get("day_master") or {}

    for key, want in cond.items():
        if key.endswith("_present") and isinstance(want, bool):
            stem_key = key[: -len("_present")]
            glyphs = PRESENCE_ALIASES.get(stem_key)
            if glyphs is None and stem_key in NAME_TO_GLYPH:
                glyphs = (NAME_TO_GLYPH[stem_key],)
            if glyphs is None:
                undecidable.append(key)
                continue
            found = any(g in present for g in glyphs)
            checks.append((f"{'/'.join(glyphs)} present", found == want))

        elif key == "chart_contains_two_or_more_of" and isinstance(want, list):
            wanted = [str(w) for w in want]
            # These lists name BRANCHES (the four sisheng/siku/sibai stations)
            # far more often than Ten Gods. Check which vocabulary they use
            # rather than assuming - the branch case was silently reporting
            # zero because it was being matched against the Ten God set.
            if any(w in BRANCH_IDS for w in wanted):
                chart = _chart_branches(facts)
                found = [w for w in wanted if w in chart]
                checks.append((
                    f"two or more of branches {'/'.join(wanted)} "
                    f"(found {len(found)}: {'、'.join(found) or 'none'})",
                    len(found) >= 2,
                ))
            else:
                glyphs = [NAME_TO_GLYPH.get(w, w) for w in wanted]
                n = sum(1 for g in glyphs if g in present)
                checks.append(
                    (f"two or more of {'/'.join(glyphs)} (found {n})", n >= 2)
                )

        elif key == "hour_stem_ten_god_relative_to_day_master":
            actual = (facts.get("visible_stem_ten_gods") or {}).get("hour", "")
            glyph = NAME_TO_GLYPH.get(str(want), str(want))
            checks.append(
                (f"hour stem is {glyph} (is {actual.split()[0] if actual else '?'})",
                 actual.startswith(glyph))
            )

        elif key == "hour_branch_hidden_stems_include_day_master_element":
            elems = {s.get("element") for s in hidden.get("hour", [])}
            checks.append(
                (f"hour branch hides {dm.get('element')}",
                 (dm.get("element") in elems) == bool(want))
            )

        elif key == "day_stem":
            checks.append((f"day stem is {want}", dm.get("stem") == want))

        elif key == "month_branch":
            actual = ((facts.get("pillars") or {}).get("month") or {}).get("branch")
            checks.append((f"month branch is {want}", actual == want))

        elif key == "day_master_seasonal_state":
            actual = (facts.get("month_command") or {}).get("day_master_state", "")
            checks.append(
                (f"day master state {want} (is {actual})", str(want) in actual)
            )

        elif key in ("luck_pillar_ten_god", "first_luck_pillar_ten_god"):
            by_dir = _luck_pillar_ten_gods(facts)
            if not by_dir:
                undecidable.append(key)
                continue
            hits = [d for d, gods in by_dir.items() if str(want) in gods]
            checks.append(
                (f"a {NAME_TO_GLYPH.get(str(want), want)} luck pillar occurs "
                 f"({', '.join(hits) if hits else 'in neither direction'})",
                 bool(hits))
            )
        else:
            undecidable.append(key)

    if undecidable and not checks:
        return None, "; ".join(undecidable)
    if undecidable:
        return None, (
            "partly decidable ("
            + ", ".join(f"{n}={'yes' if v else 'no'}" for n, v in checks)
            + ") but blocked on: " + "; ".join(undecidable)
        )
    if all(v for _n, v in checks):
        return True, ", ".join(n for n, _v in checks)
    return False, ", ".join(
        f"{n}: {'yes' if v else 'no'}" for n, v in checks
    )


def build_report(birth: BirthInput) -> TraditionReport:
    facts = _facts(birth)
    report = TraditionReport(
        tradition_id="chinese_bazi",
        display_name="BaZi 八字 — Full Reading (Ziping method)",
        birth=birth.to_dict(),
    )
    _pillars(report, facts)
    _day_master(report, facts)
    _hidden(report, facts)
    _ten_gods(report, facts)
    _relations(report, facts)
    _luck(report, facts)
    _delineations(report, facts)
    _limits(report, facts)
    return report


def _pillars(report: TraditionReport, facts: dict) -> None:
    s = report.add(ReportSection("The Four Pillars", level=2))
    p = facts["pillars"]
    s.table = [
        {
            "Pillar": name.title(),
            "Stem": p[name]["label"].split()[0] + " " + p[name]["label"].split()[1],
            "Branch": " ".join(p[name]["label"].split()[2:]),
            "Animal": p[name]["animal"],
            "Stem element": p[name]["stem_element"],
            "Branch element": p[name]["branch_element"],
            "Na Yin": facts["na_yin"][name]["image"],
        }
        for name in ("year", "month", "day", "hour")
        if name in p
    ]
    cands = facts.get("hour_pillar_candidates") or {}
    labels = {v["label"] for v in cands.values()}
    if len(labels) > 1:
        s.refusals.append(
            "The hour pillar is NOT settled. True solar time gives "
            f"{cands['true_solar_time']['label']} while clock time gives "
            f"{cands['clock_time']['label']}, because the birth sits near a "
            "double-hour boundary. Every judgment below that depends on the hour "
            "pillar therefore has two answers, and this report does not pick one. "
            "A practitioner would resolve it by rectification against known life "
            "events, which is outside what a birth record supports."
        )
    else:
        s.notes.append(
            "All three time bases (true solar, local mean, clock) fall in the "
            "same double-hour, so the hour pillar is unambiguous."
        )
    s.notes.append(
        f"Year pillar reckoned from Li Chun at {facts['li_chun_boundary_utc']}; "
        f"month pillar from the solar term beginning {facts['month_term_start_utc']}. "
        "Ziping uses the solar year, not the lunar new year."
    )


def _day_master(report: TraditionReport, facts: dict) -> None:
    s = report.add(ReportSection("The Day Master (日主)", level=2))
    dm = facts["day_master"]
    s.notes.append(
        f"The Day Master is **{dm['label']}** — {dm['polarity']} "
        f"{dm['element']}. Everything else in the chart is read relative to it: "
        "the same stem is a Friend to one chart and a Killing to another, and it "
        "is the Day Master that decides which."
    )
    mc = facts.get("month_command")
    if mc:
        s.notes.append(
            f"Month command (得令): {json.dumps(mc, ensure_ascii=False)[:400]}"
        )
    tally = facts.get("element_tally") or {}
    s.table = [{"Element": k, "Count": v} for k, v in tally.items()]
    s.notes.append(
        "Element counts are a crude first look, not a strength verdict — a "
        "single rooted stem in season outweighs three unrooted ones out of it."
    )
    s.refusals.append(
        "No strength classification (身強/身弱) and no useful-god (用神) "
        "selection is made. Those are the central Ziping judgments and the "
        "research pack marks them source-gated: the encoded material is "
        "qualitative doctrine, not a decision procedure, and inventing the "
        "threshold would be inventing the reading."
    )


def _hidden(report: TraditionReport, facts: dict) -> None:
    s = report.add(ReportSection("Hidden Stems (藏干)", level=2))
    s.notes.append(
        "The branches conceal stems, and Ziping treats them as real. Strength "
        "comes from being rooted in a branch, not from appearing on the surface."
    )
    rows = []
    for pillar, stems in (facts.get("hidden_stems") or {}).items():
        for st in stems:
            rows.append({
                "Pillar": pillar.title(),
                "Hidden stem": st["label"],
                "Element": st["element"],
                "Qi": st["qi"],
                "Ten God": st.get("ten_god", ""),
            })
    s.table = rows


def _ten_gods(report: TraditionReport, facts: dict) -> None:
    s = report.add(ReportSection("The Ten Gods (十神)", level=2))
    present = _all_ten_gods(facts)
    s.notes.append(
        "The Ten Gods convert each stem into a role relative to the Day Master. "
        "Both visible and hidden stems are counted here."
    )
    s.notes.append(
        "Present in this chart: " + ("、".join(sorted(present)) if present else "none")
    )
    supportive = sorted(present & SUPPORTIVE)
    draining = sorted(present & DRAINING)
    s.notes.append(
        f"Supporting the Day Master: {'、'.join(supportive) or 'none'}. "
        f"Drawing on it: {'、'.join(draining) or 'none'}."
    )
    visible = facts.get("visible_stem_ten_gods") or []
    if visible:
        s.table = [
            r if isinstance(r, dict) else {"value": r} for r in visible
        ]


def _relations(report: TraditionReport, facts: dict) -> None:
    s = report.add(ReportSection("Branch Relations (刑冲合害)", level=2))
    rel = facts.get("branch_relations") or {}
    labels = {
        "six_harmonies": "Six Harmonies 六合",
        "six_clashes": "Six Clashes 六冲",
        "six_harms": "Six Harms 六害",
        "six_destructions": "Six Destructions 六破",
        "three_harmony_frames": "Three Harmony frames 三合",
        "directional_frames": "Directional frames 三會",
        "punishments": "Punishments 刑",
    }
    for key, label in labels.items():
        items = rel.get(key) or []
        if not items:
            continue
        for it in items:
            branches = "、".join(it.get("branches") or it.get("present") or [])
            extra = []
            if it.get("pillars"):
                extra.append("pillars: " + "/".join(it["pillars"]))
            if it.get("type"):
                extra.append(it["type"])
            if it.get("missing"):
                extra.append("missing " + "、".join(it["missing"]))
            if it.get("reinforces"):
                extra.append("reinforces " + it["reinforces"])
            s.notes.append(
                f"**{label}** — {branches}" + (f" ({'; '.join(extra)})" if extra else "")
            )
    if rel.get("precedence_note"):
        s.notes.append(f"*{rel['precedence_note']}*")
    if not any(rel.get(k) for k in labels):
        s.notes.append("No branch relation in the encoded set is formed.")


def _luck(report: TraditionReport, facts: dict) -> None:
    s = report.add(ReportSection("Luck Pillars (大運)", level=2))
    lp = facts.get("luck_pillars") or {}
    s.notes.append(
        f"Luck pillars begin at age {lp.get('start_age')}. "
        f"{lp.get('direction_rule', '')}"
    )
    s.refusals.append(
        "Direction depends on the year stem's polarity combined with the "
        "native's SEX, which this engine does not take as input. Both sequences "
        "are therefore shown below and neither is asserted."
    )
    for direction, seq in (lp.get("sequences") or {}).items():
        sub = report.add(
            ReportSection(f"{direction.title()} sequence", level=3)
        )
        sub.table = [
            {
                "Ages": f"{r['age_from']}–{r['age_to']}",
                "From": r["start"],
                "To": r["end"],
                "Pillar": r["label"],
            }
            for r in seq
        ]


def _delineations(report: TraditionReport, facts: dict) -> None:
    s = report.add(ReportSection("Classical Judgments That Apply", level=2))
    present = _all_ten_gods(facts)
    fired = skipped = undecided = suppressed = 0
    undecided_notes: list[str] = []
    for rule in _manifest()["rules"]:
        verdict, why = _condition_verdict(rule.get("conditions"), facts, present)
        text = _text_of(rule)
        reason = _suppressed(rule)
        if verdict is True and reason:
            # The condition matches this chart, which is precisely why the
            # suppression matters: rendering it here would be a personal verdict.
            suppressed += 1
            s.refusals.append(
                f"One judgment ({rule['rule_id']}) DOES match this chart and is "
                f"deliberately not shown. The pack's own policy: {reason} It is "
                "kept in the corpus as historical quotation and suppressed here "
                "rather than quietly dropped at extraction time, so the "
                "suppression is auditable."
            )
            continue
        if verdict is True and text:
            fired += 1
            s.delineations.append(
                Delineation(
                    text=text,
                    rule_id=rule["rule_id"],
                    source=_source_label(rule),
                    evidence_grade=rule.get("evidence_grade", "?"),
                    trigger=why,
                    caveat=(
                        rule.get("publication_limit")
                        if isinstance(rule.get("publication_limit"), str) else None
                    ),
                )
            )
        elif verdict is None:
            undecided += 1
            undecided_notes.append(f"`{rule['rule_id']}` — {why}")
        else:
            skipped += 1
    s.notes.insert(
        0,
        f"{len(_manifest()['rules'])} classical judgments were tested against this "
        f"chart: **{fired} apply**, {skipped} do not, {suppressed} match but are "
        f"suppressed by the pack's own output policy, and {undecided} could not "
        "be decided from what this engine computes.",
    )
    if undecided_notes:
        sub = report.add(
            ReportSection("Judgments that could not be decided", level=3)
        )
        sub.notes.append(
            "These rules exist in the pack and were NOT fired, because deciding "
            "them needs a fact this engine does not produce. They are listed so "
            "the omission is visible rather than silent."
        )
        for n in undecided_notes[:40]:
            sub.notes.append(f"- {n}")


def _limits(report: TraditionReport, facts: dict) -> None:
    report.method_notes.extend([
        "Year boundary is Li Chun (solar longitude 315°), the dominant Ziping "
        "convention. Some practice uses the lunar new year, which moves the year "
        "pillar for births between the two dates.",
        "Month boundaries are the twelve jie, computed from Swiss Ephemeris solar "
        "longitude rather than a printed almanac.",
        "The sexagenary day count is anchored at JDN 2433191 (1949-10-01) = "
        "Jia-Zi, cross-checked against 2000-01-01 = Wu-Wu. No day-concordance "
        "source is registered, so this anchor is a product choice.",
        "The civil day is used for the day pillar. Late-Zi schools roll it "
        "forward at 23:00, which changes the day pillar for births between 23:00 "
        "and midnight.",
        "Hidden-stem and Ten-God tables follow the inspected Yuanhai Ziping and "
        "Sanming Tonghui transcriptions. Sanming Tonghui juan 10-12 are now "
        "traceable to the Qing-court Siku Quanshu recension, but page-image "
        "collation has not been done, so these remain transcription-grade.",
        "No strength class, no useful god, no pattern (格局) determination. Those "
        "are the heart of Ziping judgment and the corpus does not yet hold a "
        "decision procedure for them from a controlling edition.",
    ])
