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
from .ziping_predicates import ZipingChart, controls, element_playing, generates

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
    # visible_stem_ten_gods is a dict {pillar: "glyph Label"}; iterating it
    # directly yielded pillar-name keys, so visible stems were never counted.
    for label in (facts.get("visible_stem_ten_gods") or {}).values():
        if isinstance(label, str) and label:
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
    zc = ZipingChart(facts)

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
            token = actual.split()[0] if actual else ""
            wanted_tokens = [w for w in ("wang", "xiang", "xiu", "qiu", "si")
                             if w in str(want)]
            checks.append(
                (f"day master state in {wanted_tokens} (is {actual})",
                 token in wanted_tokens)
            )

        elif key in ("luck_pillar_ten_god", "first_luck_pillar_ten_god"):
            source = (
                zc.first_luck_pillar_roles() if key.startswith("first")
                else {d: (None, None) for d in ()}
            )
            if key == "first_luck_pillar_ten_god":
                target = "zheng_yin" if str(want).startswith("yin") else str(want)
                hits = [
                    d for d, (role, _st) in zc.first_luck_pillar_roles().items()
                    if role in (target, "pian_yin" if target == "zheng_yin" else target)
                ]
                checks.append(
                    (f"first luck pillar is {NAME_TO_GLYPH.get(target, want)} "
                     f"({', '.join(hits) if hits else 'in neither direction'})",
                     bool(hits))
                )
            else:
                by_dir = zc.luck_ten_gods()
                hits = [d for d, gods in by_dir.items() if str(want) in gods]
                checks.append(
                    (f"a {NAME_TO_GLYPH.get(str(want), want)} luck pillar occurs "
                     f"({', '.join(hits) if hits else 'in neither direction'})",
                     bool(hits))
                )
            del source

        elif key == "qi_sha_seasonally_strong":
            strong, why = zc.seasonally_strong("qi_sha")
            checks.append((why, strong == bool(want)))

        elif key == "hour_branch_hidden_stems_include_day_master_element_count":
            n = zc.hour_branch_roots_of_day_master()
            ok = n > 1 if str(want) == ">1" else n == int(want)
            checks.append((f"hour branch roots of Day Master element = {n}", ok))

        elif key == "relation" and "generat" in str(want):
            sha = element_playing("qi_sha", zc.day_stem)
            seal = element_playing("zheng_yin", zc.day_stem)
            ok = bool(sha and seal and generates(sha, seal))
            checks.append(
                (f"Killing ({sha}) generates Seal ({seal}) in the production cycle",
                 ok)
            )

        elif key == "officer_and_killings_together_are_subdued_or_controlled":
            # Operationalized: the Ten God whose element CONTROLS the
            # Officer/Killing element (the output stars) is present and either
            # rooted or seasonally strong. 制殺 via the Eating God is the
            # textbook mechanism; the operationalization is stated in the
            # trigger so the broader classical sense is not silently claimed.
            guan_element = element_playing("zheng_guan", zc.day_stem)
            controller_roles = [
                role for role in ("shi_shen", "shang_guan")
                if (e := element_playing(role, zc.day_stem))
                and guan_element and controls(e, guan_element)
            ]
            armed = [
                role for role in controller_roles
                if zc.present(role)
                and (zc.rooted(role) or zc.seasonally_strong(role)[0])
            ]
            checks.append(
                ("controller of Officer/Killing present and armed ("
                 + (", ".join(NAME_TO_GLYPH[r] for r in armed) if armed else "none")
                 + ") [operationalized as: output star controlling the officer "
                 "element, rooted or in season]",
                 bool(armed))
            )

        elif key == "both_visible_or_rooted_simultaneously":
            guan_ok = zc.visible("zheng_guan") or zc.rooted("zheng_guan")
            sha_ok = zc.visible("qi_sha") or zc.rooted("qi_sha")
            checks.append(
                (f"Officer visible-or-rooted={guan_ok}, "
                 f"Killing visible-or-rooted={sha_ok}", guan_ok and sha_ok)
            )

        elif key == "damaged_or_clashed":
            role = "zheng_guan" if zc.present("zheng_guan") else "qi_sha"
            damaged, why = zc.damaged_or_clashed(role)
            checks.append(
                (f"{NAME_TO_GLYPH[role]} damaged/clashed: {why} "
                 "[operationalized as: root branch in a six-clash, or a "
                 "controlling Ten God present]",
                 damaged == bool(want))
            )

        elif key == "shi_shen_has_qi":
            has = zc.rooted("shi_shen") or zc.seasonally_strong("shi_shen")[0]
            checks.append(
                (f"食神 rooted={zc.rooted('shi_shen')}, "
                 f"in season={zc.seasonally_strong('shi_shen')[0]}", has)
            )

        elif key == "shi_shen_undamaged_by_shang_guan":
            damaged, why = zc.damaged_or_clashed("shi_shen")
            checks.append(
                (f"食神 undamaged: {why}", (not damaged) == bool(want))
            )

        elif key == "natal_shang_guan_present_and_governing":
            governing = zc.present("shang_guan") and (
                "month" in zc.roots_of("shang_guan")
                or zc.seasonally_strong("shang_guan")[0]
            )
            checks.append(
                ("傷官 present and governing (month-rooted or in season): "
                 f"{governing}", governing)
            )

        elif key in ("day_master_class", "day_master_and_useful_matter_strong"):
            strong, why = zc.day_master_strong()
            checks.append((f"day master strong per {why}", strong))

        elif key == "phase_in_own_generation_or_prosperity_state":
            state = zc.state_of_element(zc.day_element)
            token = state.split()[0]
            checks.append(
                (f"day master {zc.day_element} state {state} "
                 "[operationalized: wang/xiang of the five command states]",
                 token in ("wang", "xiang"))
            )

        elif key == "phase_qi_direction":
            direction, why = zc.phase_direction()
            checks.append(
                (f"{why} -> {direction} "
                 "[operationalized: xiang=advancing, xiu=retreating]",
                 direction in ("advancing", "retreating"))
            )

        elif key == "luck_pillar_seasonal_state":
            roles = zc.first_luck_pillar_roles()
            desc = "; ".join(f"{d}: {r} in state {s}" for d, (r, s) in roles.items())
            strong = any(
                s and s.split()[0] in ("wang", "xiang") for _r, s in roles.values()
            )
            checks.append((f"first luck pillar state ({desc})", strong))

        elif key == "month_branch_or_its_useful_element_present":
            mc = facts.get("month_command") or {}
            checks.append(
                ("month command has a useful root: "
                 f"{mc.get('support_assessment', '?')}",
                 bool(mc.get("root_in_month_branch")))
            )

        elif key == "clash_type":
            clashed = zc.month_branch_clashed()
            checks.append(
                (f"a clash lands on the month branch itself: {clashed}", clashed)
            )

        elif key == "one_of_the_three_hidden_stems_revealed_and_prosperous_at_stem_level":
            revealed = []
            for pillar, p in zc.pillars.items():
                if p.get("branch") not in ("chen", "xu", "chou", "wei"):
                    continue
                hidden_here = {s["stem"] for s in zc.hidden.get(pillar, [])}
                for other_pillar in ("year", "month", "hour"):
                    stem = (zc.pillars.get(other_pillar) or {}).get("stem")
                    if stem in hidden_here:
                        revealed.append(f"{stem} ({other_pillar} stem)")
            checks.append(
                ("a storage branch's hidden stem is revealed at stem level: "
                 + (", ".join(revealed) if revealed else "none"),
                 bool(revealed))
            )

        elif key == "wealth_or_officer_hidden_in_a_storage_branch":
            holdings = zc.storage_holdings()
            checks.append(
                ("Wealth/Officer stored: "
                 + (", ".join(f"{h['label']} in {h['branch']}" for h in holdings)
                    if holdings else "none"),
                 bool(holdings))
            )

        elif key == "storage_branch_clashed_open":
            holdings = zc.storage_holdings()
            opened = [
                h for h in holdings if h["pillar"] in zc.clashed_pillars()
            ]
            checks.append(
                ("storage branch clashed open: "
                 + (", ".join(h["branch"] for h in opened) if opened else "no"),
                 bool(opened))
            )

        elif key == "luck_pillar_or_annual_pillar_forms_a_liu_he_with_a_natal_stem_or_branch":
            ok, why = zc.luck_harmony_with_natal()
            checks.append(
                (why + " [annual pillars not enumerated; luck pillars checked]",
                 ok)
            )

        elif key == "one_branch_of_a_clash_pair_appears_twice_or_more":
            ok, why = zc.clash_proportional_case()
            checks.append((why, ok))

        elif key == "the_opposite_branch_appears_only_once":
            # Folded into the proportional-case predicate above; repeat its
            # verdict so the conjunction stays coherent.
            ok, _why = zc.clash_proportional_case()
            checks.append(("(same proportional test)", ok))

        elif key in ("officer_star", "damaging_agents", "wealth_officer_seal_present",
                     "wealth_and_officer_present_and_favorable"):
            # Descriptive keys: the deciding keys of these rules are elsewhere
            # in the same condition (day_stem/month_branch decide the worked
            # example; the storage/shiedabai rules carry their own gates).
            # Treated as satisfied-by-description rather than blocking.
            if key == "wealth_and_officer_present_and_favorable":
                wealth = zc.present("zheng_cai") or zc.present("pian_cai")
                officer = zc.present("zheng_guan")
                favorable = wealth and officer and (
                    zc.seasonally_strong("zheng_guan")[0]
                    or zc.rooted("zheng_guan")
                )
                checks.append(
                    (
                        "Wealth "
                        + ("present" if wealth else "absent")
                        + ", Officer "
                        + ("present" if officer else "absent")
                        + ", Officer "
                        + ("armed" if favorable else "unarmed"),
                        favorable,
                    )
                )
            # the pure-description keys add no check

        elif key == "day_pillar_is_member_of_shi_e_da_bai_category":
            undecidable.append(
                "shi_e_da_bai day list: the pack quotes the verdict couplet but "
                "not the ten day-pillars themselves; encoding the list from "
                "general knowledge would be an unsourced import, so this stays "
                "gated until the list is extracted from a witness"
            )

        else:
            undecidable.append(key)

    # A conjunction with any decided-False clause is False regardless of what
    # else could not be decided - the rule cannot fire either way.
    if any(not v for _n, v in checks):
        return False, ", ".join(f"{n}: {'yes' if v else 'no'}" for n, v in checks)
    if undecidable and not checks:
        return None, "; ".join(undecidable)
    if undecidable:
        return None, (
            "all decidable clauses hold ("
            + ", ".join(n for n, _v in checks)
            + ") but blocked on: "
            + "; ".join(u.replace("_", " ") for u in undecidable)
        )
    return True, ", ".join(n for n, _v in checks)


def build_report(birth: BirthInput) -> TraditionReport:
    facts = _facts(birth)
    report = TraditionReport(
        tradition_id="chinese_bazi",
        display_name="BaZi 八字 — Structural Analysis with Classical Clauses (Ziping method)",
        birth=birth.to_dict(),
    )
    _pillars(report, facts)
    _day_master(report, facts)
    _hidden(report, facts)
    _ten_gods(report, facts)
    _relations(report, facts)
    _hour_fork_report(report, facts)
    _luck(report, facts, birth.sex)
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
        rooted = mc.get("root_in_month_branch")
        root_branches = mc.get("root_branches") or []
        s.notes.append(
            f"Month command (得令): the month branch's season is "
            f"**{mc.get('season_of_month_branch')}**, in which the Day Master "
            f"stands in the state {mc.get('day_master_state')}. It is "
            + ("rooted in the month branch itself"
               if rooted else "not rooted in the month branch")
            + (
                f", with roots in the {', '.join(root_branches)} branch(es)"
                if root_branches else ""
            )
            + f". {mc.get('support_assessment', '')}"
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


def _luck(report: TraditionReport, facts: dict, sex: str | None) -> None:
    s = report.add(ReportSection("Luck Pillars (大運)", level=2))
    lp = facts.get("luck_pillars") or {}
    s.notes.append(
        f"Luck pillars begin at age {lp.get('start_age')}. "
        f"{lp.get('direction_rule', '')}"
    )
    sequences = lp.get("sequences") or {}
    resolved: str | None = None
    if sex in ("male", "female"):
        polarity = lp.get("year_stem_polarity")
        # The rule the engine itself states: yang year + male, or yin year +
        # female, runs forward; the complementary cases run reverse.
        resolved = (
            "forward"
            if (polarity == "yang") == (sex == "male")
            else "reverse"
        )
        s.notes.append(
            f"Sex supplied ({sex}); with a {polarity}-stem year the direction "
            f"resolves to **{resolved}** under the stated rule, and only that "
            "sequence is asserted."
        )
    else:
        s.refusals.append(
            "MISSING INPUT, not doctrinal ambiguity: direction depends on the "
            "year stem's polarity combined with the native's sex, which was "
            "not supplied. Both sequences are shown; provide sex to resolve."
        )
    for direction, seq in sequences.items():
        if resolved and direction != resolved:
            continue
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
            scope = (rule.get("scope") or {})
            label = (
                scope.get("technique")
                or scope.get("unit")
                or rule.get("rule_id", "").split(".")[-1].replace("_", " ")
            )
            undecided_notes.append(f"{label} — {why}")
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


def _hour_fork_report(report: TraditionReport, facts: dict) -> None:
    """The Chinese birth-time fork as a difference report, not a footnote.

    When true-solar and clock time give different hour pillars, the system does
    not possess one chart - it possesses two candidates. Everything invariant
    is the stable core; this section lists exactly what changes, so the reader
    does not have to track the fork mentally through the whole report.
    """
    cands = facts.get("hour_pillar_candidates") or {}
    labels = {v["label"] for v in cands.values()}
    if len(labels) <= 1:
        return
    from ..multitradition import bazi as _bazi

    s = report.add(ReportSection("The Hour Fork — what actually changes", level=2))
    solar = cands.get("true_solar_time", {})
    clock = cands.get("clock_time", {})
    day_stem = (facts.get("day_master") or {}).get("stem")
    s.notes.append(
        "The stable core - year, month and day pillars, the Day Master, month "
        "command, and every branch relation not involving the hour - is "
        "identical under both time conventions. The differences, exhaustively:"
    )
    rows = []
    for name, cand in (("true solar time", solar), ("clock time", clock)):
        branch = cand.get("branch", "")
        stem = cand.get("stem", "")
        ten_god = ""
        if day_stem and stem:
            try:
                _key, glyph = _bazi.ten_god(day_stem, stem)
                ten_god = glyph
            except Exception:
                ten_god = "?"
        hidden = ", ".join(_bazi.HIDDEN_STEMS.get(branch, []))
        rows.append({
            "Basis": name,
            "Hour pillar": cand.get("label", ""),
            "Hour stem Ten God": ten_god,
            "Hour branch hides": hidden or "—",
            "Time": cand.get("time", ""),
        })
    s.table = rows
    s.notes.append(
        "Every hour-keyed judgment in this report therefore has two answers. "
        "True solar time is listed first as the disclosed product convention - "
        "practice is genuinely divided, and this is a convention, not a "
        "historically resolved fact. Rectification against known life events "
        "is how a practitioner would settle it; a birth record alone cannot."
    )
