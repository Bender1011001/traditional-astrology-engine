"""A full Parāśari Jyotiṣa report.

Not a Hellenistic report with Sanskrit vocabulary. The judgment order is the
tradition's own, and it is the order Phaladīpikā and the commentaries actually
use:

  1. the lagna, its lord, and the janma nakṣatra - who the chart belongs to
  2. the nine grahas, each in its rāśi, bhāva, dignity and D9
  3. the twelve bhāvas, each by its lord's condition and its occupants
  4. the yogas that are actually present, with their sourced results
  5. the daśā that is running now, and the ones on either side of it

Every delineation is quoted from the research corpus with its rule id. Where
Phaladīpikā's text was not recovered - Sun in bhāvas 1-5, 7 and 8 sit in an OCR
gap - the report says so in the place the delineation would have gone, instead
of substituting a different author or writing something plausible.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from ..multitradition import build_panel
from ..multitradition.jyotisha_strength import (
    ashtakavarga,
    sadbala,
    sarva_grade,
)
from ..multitradition.jyotisha_strength_inputs import (
    RASIS,
    build_strength_inputs,
    local_datetime,
)
from ..multitradition.jyotisha_varga import (
    VARGA_PURPOSE,
    all_vargas,
    vimsopaka_bala,
)
from ..multitradition.types import BirthInput
from .report import Delineation, ReportSection, TraditionReport

RESEARCH_ROOT = (
    Path(__file__).resolve().parents[3] / "docs" / "research" / "multitradition"
)
DELINEATION_MANIFEST = RESEARCH_ROOT / "jyotisha" / "delineation_rule_manifest.json"
BPHS_MANIFEST = RESEARCH_ROOT / "jyotisha" / "bphs_rule_manifest.json"
EXTRA_MANIFESTS = (
    RESEARCH_ROOT / "jyotisha" / "saravali_rule_manifest.json",
    RESEARCH_ROOT / "jyotisha" / "brhajjataka_delineation_rule_manifest.json",
)

ORDINAL = {
    1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th",
    7: "7th", 8: "8th", 9: "9th", 10: "10th", 11: "11th", 12: "12th",
}
BHAVA_NAMES = {
    1: "Tanu — body, self, and the whole life's measure",
    2: "Dhana — wealth, speech, family, sustenance",
    3: "Sahaja — siblings, courage, effort, short journeys",
    4: "Bandhu — mother, home, land, vehicles, inner contentment",
    5: "Putra — children, intellect, pūrva puṇya, counsel",
    6: "Ari — enemies, disease, debt, service, obstacles",
    7: "Yuvati — marriage, partnership, open dealings",
    8: "Randhra — longevity, hidden things, upheaval, inheritance",
    9: "Dharma — fortune, father, teacher, righteousness, pilgrimage",
    10: "Karma — action, profession, status, public standing",
    11: "Lābha — gains, elder siblings, desires fulfilled",
    12: "Vyaya — loss, expenditure, seclusion, liberation, foreign lands",
}
KENDRAS = (1, 4, 7, 10)
TRIKONAS = (1, 5, 9)
DUSTHANAS = (6, 8, 12)


@lru_cache(maxsize=1)
def _manifest() -> dict[str, Any]:
    return json.loads(DELINEATION_MANIFEST.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _rules_by_id() -> dict[str, dict[str, Any]]:
    rules = {r["rule_id"]: r for r in _manifest()["rules"]}
    for path in (BPHS_MANIFEST, *EXTRA_MANIFESTS):
        if path.exists():
            extra = json.loads(path.read_text(encoding="utf-8"))
            for r in extra["rules"]:
                rules[r["rule_id"]] = r
    return rules


def cell_delineation(
    rule_id: str, block: str, key: str, trigger: str
) -> tuple[Delineation | None, str | None]:
    """Read one delineation cell from a rule's results block.

    Cells are either plain strings (Phaladipika/BPHS style) or dicts carrying
    the Sanskrit, the rendering, the sloka, and possibly their own per-cell
    output_policy. A cell that refuses itself yields a refusal string naming
    the pack's reason - decided here, at fire time, in the one chart where it
    would otherwise read as a verdict.
    """
    rule = _rules_by_id().get(rule_id)
    if rule is None:
        return None, None
    cell = (rule.get("conclusion", {}).get(block) or {}).get(str(key))
    if cell is None:
        return None, None
    if isinstance(cell, str):
        return _delineate(rule_id, cell, trigger), None
    if not isinstance(cell, dict):
        return None, None
    if str(cell.get("output_policy", "")).lower() == "refused":
        reason = cell.get("output_policy_reason", "the pack refuses this cell")
        return None, (
            f"The source DOES state a result here ({trigger}) and it is "
            f"withheld: {reason}."
        )
    text = cell.get("engine_rendering")
    if not text:
        return None, None
    sloka = cell.get("sloka")
    return _delineate(
        rule_id, str(text),
        trigger + (f" · śloka {sloka}" if sloka else ""),
    ), None


def graha_rasi_rules(graha: str) -> list[str]:
    """Every author's graha-in-rasi rule for this graha, one voice each."""
    suffix = f".graha_in_rasi.{graha.lower()}"
    return sorted(rid for rid in _rules_by_id() if rid.endswith(suffix))


def bhavesha_result(lorded_house: int, occupied_house: int) -> tuple[str | None, str | None, str | None]:
    """BPHS Adhyaya 15: the lord of house N placed in house M.

    Returns (text, suppression_reason, devanagari). A suppressed cell reports
    the pack's reason instead of the text - the suppression happens at fire
    time, in the one chart where it would otherwise read as a verdict.
    """
    rule = _rules_by_id().get(
        f"jyotisha.bphs.a15.bhavesa_in_bhava.lord_{lorded_house:02d}"
    )
    if rule is None:
        return None, None, None
    c = rule.get("conclusion", {}) or {}
    key = str(occupied_house)
    restricted = (c.get("restricted_by_house") or {}).get(key)
    if restricted:
        return None, restricted.get("reason", "restricted"), None
    text = (c.get("results_by_house") or {}).get(key)
    deva = (c.get("devanagari_by_house") or {}).get(key)
    return (str(text) if text else None), None, (str(deva) if deva else None)


def _source_label(rule: dict[str, Any]) -> str:
    passages = rule.get("source_passages") or []
    if not passages:
        return rule.get("rule_id", "unknown source")
    p = passages[0]
    work = p.get("work") or "Phaladīpikā"
    loc = p.get("location") or p.get("section") or ""
    return f"{work}, {loc}".strip().rstrip(",")


def _delineate(
    rule_id: str, text: str, trigger: str, caveat: str | None = None
) -> Delineation | None:
    rule = _rules_by_id().get(rule_id)
    if rule is None or not text:
        return None
    return Delineation(
        text=text.strip(),
        rule_id=rule_id,
        source=_source_label(rule),
        evidence_grade=rule.get("evidence_grade", "?"),
        trigger=trigger,
        caveat=caveat,
    )


def _planet_in_bhava(graha: str, house: int) -> tuple[str | None, str | None]:
    """Phaladīpikā's result for a graha in a bhāva, or the reason there is none."""
    rule_id = f"jyotisha.phaladeepika.08.planet_in_bhava.{graha.lower()}"
    rule = _rules_by_id().get(rule_id)
    if rule is None:
        return None, f"no Phaladīpikā bhāva-results rule is encoded for {graha}"
    conclusion = rule.get("conclusion", {}) or {}
    results = conclusion.get("results_by_house") or {}
    text = results.get(str(house)) or results.get(house)
    if text:
        return str(text), None
    missing = conclusion.get("houses_not_recovered")
    if missing:
        return None, (
            f"Phaladīpikā's text for {graha} in the {ORDINAL[house]} bhāva was not "
            f"recovered from the available scan (the pack records houses "
            f"{missing} as an OCR gap). No substitute author is used."
        )
    return None, (
        f"the encoded Phaladīpikā rule for {graha} carries no result for the "
        f"{ORDINAL[house]} bhāva"
    )


def _facts(birth: BirthInput) -> dict[str, Any]:
    panel = build_panel(birth)
    section = next(
        s for s in panel["sections"] if s["tradition_id"] == "indian_jyotisha"
    )
    if section.get("error"):
        raise RuntimeError(f"Jyotisha calculation failed: {section['error']}")
    return section["facts"]


def _house_of(facts: dict[str, Any], graha: str) -> int | None:
    for row in facts["grahas"]:
        if row["graha"] == graha:
            return row["house"]
    return None


def _graha_row(facts: dict[str, Any], graha: str) -> dict[str, Any] | None:
    return next((r for r in facts["grahas"] if r["graha"] == graha), None)


def build_report(birth: BirthInput) -> TraditionReport:
    facts = _facts(birth)
    report = TraditionReport(
        tradition_id="indian_jyotisha",
        display_name="Parāśari Jyotiṣa — Full Reading",
        birth=birth.to_dict(),
    )
    lagna = facts["lagna"]
    grahas = facts["grahas"]
    houses = {h["house"]: h for h in facts["houses"]}
    lordships = facts["house_lordships"]

    _opening(report, facts, lagna)
    _grahas_section(report, facts, grahas)
    # Synthesis runs over everything the graha sections fired; inserted after
    # they are built but positioned right after the opening in the reading.
    from .synthesis import synthesize

    fired = [d for s in report.sections for d in s.delineations]
    synthesis_section = synthesize(fired, facts, tradition="jyotisha")
    report.sections.insert(1, synthesis_section)
    _bhavas_section(report, facts, houses, lordships, grahas)
    strength = _strength_of(birth, facts)
    _strength_section(report, facts, strength)
    _yogas_section(report, facts, strength)
    _vargas_section(report, facts, grahas, strength)
    _dasha_section(report, facts)
    _navamsha_section(report, facts, grahas)
    _drishti_section(report, facts)
    _limits(report, facts)
    return report


def _opening(report: TraditionReport, facts: dict, lagna: dict) -> None:
    s = report.add(ReportSection("The Lagna and Its Lord", level=2))
    lord = lagna["lord"]
    lord_row = _graha_row(facts, lord)
    s.notes.append(
        f"The lagna rises in **{lagna['rasi']}** at {lagna['degree_in_sign']:.2f}°, "
        f"in the nakṣatra **{lagna['nakshatra']} pāda {lagna['pada']}** "
        f"(lord {lagna['nakshatra_lord']}). Its navāṃśa is {lagna['navamsha']}"
        + (", vargottama." if lagna.get("vargottama") else ".")
    )
    s.notes.append(
        f"The lagneśa — lord of the lagna — is **{lord}**"
        + (
            f", standing in {lord_row['rasi']} in the {ORDINAL[lord_row['house']]} "
            f"bhāva, {lord_row['dignity']}."
            if lord_row else "."
        )
    )
    s.notes.append(
        f"The janma rāśi (Moon sign) is **{facts['janma_rasi']}** and the janma "
        f"nakṣatra is **{facts['janma_nakshatra']['name']} pāda "
        f"{facts['janma_nakshatra']['pada']}**, lord "
        f"{facts['janma_nakshatra']['lord']} — which is what sets the "
        f"Viṃśottarī daśā sequence below."
    )
    if lord_row:
        s.notes.append(
            f"{lord}'s own placement judgments are quoted in full in the graha "
            "section below; the lagneśa-specific result from BPHS follows here."
        )
        btext, brestrict, _deva = bhavesha_result(1, lord_row["house"])
        if btext:
            d = _delineate(
                "jyotisha.bphs.a15.bhavesa_in_bhava.lord_01",
                btext,
                f"lagneśa in the {ORDINAL[lord_row['house']]} bhāva (BPHS)",
            )
            if d:
                s.delineations.append(d)
        elif brestrict:
            s.refusals.append(
                "BPHS Adhyāya 15 does state a result for the lagneśa in the "
                f"{ORDINAL[lord_row['house']]} bhāva, and it is withheld here: "
                f"the pack marks that cell {brestrict!r} and forbids rendering "
                "it as a claim about a living person."
            )


def _grahas_section(report: TraditionReport, facts: dict, grahas: list) -> None:
    s = report.add(ReportSection("The Nine Grahas", level=2))
    s.table = [
        {
            "Graha": g["graha"],
            "Rāśi": f"{g['rasi']} {g['degree_in_sign']:.1f}°",
            "Bhāva": g["house"],
            "Nakṣatra": f"{g['nakshatra']} p{g['pada']}",
            "Dignity": g["dignity"],
            "D9": g["navamsha"],
            "Vargottama": "yes" if g.get("vargottama") else "",
            "Combust": "yes" if g.get("combust") else "",
        }
        for g in grahas
    ]
    for g in grahas:
        sub = report.add(
            ReportSection(
                f"{g['graha']} in {g['rasi']}, {ORDINAL[g['house']]} bhāva",
                level=3,
            )
        )
        bits = [
            f"{g['graha']} stands in **{g['rasi']}** at "
            f"{g['degree_in_sign']:.2f}°, in the {ORDINAL[g['house']]} bhāva "
            f"({g['dignity']}).",
            f"Nakṣatra {g['nakshatra']} pāda {g['pada']}, lord "
            f"{g['nakshatra_lord']}. In the navāṃśa it falls in "
            f"{g['navamsha']} ({g['navamsha_dignity']})"
            + (", vargottama — the same sign in D1 and D9, which strengthens it."
               if g.get("vargottama") else "."),
        ]
        if g.get("dispositor"):
            bits.append(
                f"Its dispositor is {g['dispositor']}, a {g['dispositor_relation']} "
                f"by naisargika relation."
            )
        if g.get("combust"):
            bits.append(
                f"It is combust — within {g.get('combustion_orb_degrees')}° of the "
                f"Sun ({g.get('solar_separation_degrees')}° actual separation)."
            )
        if g.get("retrograde"):
            bits.append("It is retrograde (vakrī).")
        if g.get("drishti_houses"):
            bits.append(
                "It casts drishti on "
                + ", ".join(ORDINAL[h] for h in g["drishti_houses"])
                + " bhāva."
            )
        sub.notes.append(" ".join(bits))
        for rid in graha_rasi_rules(g["graha"]):
            d, refusal = cell_delineation(
                rid, "results_by_rasi", g["rasi"],
                f"{g['graha']} in {g['rasi']}",
            )
            if d:
                sub.delineations.append(d)
            elif refusal:
                sub.refusals.append(refusal)
        text, why = _planet_in_bhava(g["graha"], g["house"])
        if text:
            d = _delineate(
                f"jyotisha.phaladeepika.08.planet_in_bhava.{g['graha'].lower()}",
                text,
                f"{g['graha']} in the {ORDINAL[g['house']]} bhāva",
            )
            if d:
                sub.delineations.append(d)
        elif why:
            sub.refusals.append(why)
        d, refusal = cell_delineation(
            f"jyotisha.saravali.30.graha_in_bhava.{g['graha'].lower()}",
            "results_by_house", str(g["house"]),
            f"{g['graha']} in the {ORDINAL[g['house']]} bhāva (Saravali, "
            "a second author kept as a separate voice)",
        )
        if d:
            sub.delineations.append(d)
        elif refusal:
            sub.refusals.append(refusal)


def _bhavas_section(
    report: TraditionReport, facts: dict, houses: dict, lordships: dict, grahas: list
) -> None:
    report.add(ReportSection("The Twelve Bhāvas", level=2)).notes.append(
        "Each bhāva is judged by three things in this tradition: the sign on it, "
        "the condition of its lord, and whatever occupies it. All three are given "
        "below; the sourced delineation follows each occupant."
    )
    occupants: dict[int, list[dict]] = {}
    for g in grahas:
        occupants.setdefault(g["house"], []).append(g)
    for house in range(1, 13):
        info = houses[house]
        sub = report.add(
            ReportSection(f"Bhāva {house}: {BHAVA_NAMES[house]}", level=3)
        )
        lord = info["lord"]
        lord_row = _graha_row(facts, lord)
        kind = []
        if house in KENDRAS:
            kind.append("kendra")
        if house in TRIKONAS:
            kind.append("trikoṇa")
        if house in DUSTHANAS:
            kind.append("duḥsthāna")
        note = (
            f"**{info['rasi']}** occupies the {ORDINAL[house]} bhāva"
            + (f" ({', '.join(kind)})" if kind else "")
            + f". Its lord is **{lord}**"
        )
        if lord_row:
            note += (
                f", placed in {lord_row['rasi']} in the "
                f"{ORDINAL[lord_row['house']]} bhāva, {lord_row['dignity']}"
            )
        other = [h for h in lordships.get(lord, []) if h != house]
        if other:
            note += (
                f". {lord} also rules the "
                + ", ".join(ORDINAL[h] for h in other)
                + " bhāva, so those topics are tied to this one"
            )
        note += "."
        sub.notes.append(note)
        if lord_row and house == 1:
            sub.notes.append(
                "The lagneśa's BPHS result appears in the opening section and "
                "is not repeated here."
            )
        elif lord_row:
            btext, brestrict, _deva = bhavesha_result(house, lord_row["house"])
            if btext:
                d = _delineate(
                    f"jyotisha.bphs.a15.bhavesa_in_bhava.lord_{house:02d}",
                    btext,
                    f"lord of the {ORDINAL[house]} placed in the "
                    f"{ORDINAL[lord_row['house']]} bhāva",
                )
                if d:
                    sub.delineations.append(d)
            elif brestrict:
                sub.refusals.append(
                    f"BPHS Adhyāya 15 states a result for the {ORDINAL[house]} "
                    f"lord in the {ORDINAL[lord_row['house']]} bhāva and it is "
                    f"withheld: the pack marks that cell {brestrict!r} and "
                    "forbids rendering it as a claim about a living person."
                )
            else:
                sub.refusals.append(
                    f"BPHS Adhyāya 15's cell for the {ORDINAL[house]} lord in "
                    f"the {ORDINAL[lord_row['house']]} bhāva is one of the 12 "
                    "genuinely absent from this recension's printed text; "
                    "nothing was imported from later editions to fill it."
                )
        here = occupants.get(house, [])
        if here:
            # One claim, one appearance: the occupant judgments are quoted in
            # full in each graha's own section above. Repeating them here would
            # inflate the report and make one source statement look like two
            # corroborating witnesses.
            sub.notes.append(
                "Occupied by "
                + ", ".join(g["graha"] for g in here)
                + " — see "
                + ("its judgment" if len(here) == 1 else "their judgments")
                + " in the graha section above."
            )
        else:
            sub.notes.append(
                "No graha occupies it; it is judged from its lord's condition alone."
            )


def _strength_of(birth: BirthInput, facts: dict) -> dict[str, Any]:
    """Sadbala and Ashtakavarga for this nativity, or an honest blank.

    Wrapped because a strength failure must not take the report down with it:
    a chart that cannot be weighed is still a chart that can be read, and the
    section says so rather than the whole report vanishing.
    """
    try:
        moment = local_datetime(
            birth.civil_date, birth.civil_time, birth.utc_offset_hours
        )
        inputs, provenance = build_strength_inputs(
            facts, moment, birth.latitude, birth.longitude
        )
        pindas = sadbala(inputs)
        positions = {
            row["graha"]: RASIS.index(row["rasi"])
            for row in facts.get("grahas", [])
            if row.get("graha")
            in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
        }
        lagna_rasi = (facts.get("lagna") or {}).get("rasi")
        if lagna_rasi:
            positions["Lagna"] = RASIS.index(lagna_rasi)
        graha_rasis = {g: RASIS[i] for g, i in positions.items() if g != "Lagna"}
        av = ashtakavarga(positions, graha_rasis) if lagna_rasi else None
        return {
            "sadbala": pindas,
            "provenance": provenance,
            "ashtakavarga": av,
            "error": None,
        }
    except Exception as exc:  # the report survives a strength failure
        return {
            "sadbala": {},
            "provenance": {},
            "ashtakavarga": None,
            "error": f"{type(exc).__name__}: {exc}",
        }


def _strength_section(
    report: TraditionReport, facts: dict, strength: dict[str, Any]
) -> None:
    """Shadbala and Ashtakavarga - the arbiter the text itself supplies."""
    s = report.add(ReportSection("Strength: Sadbala and Ashtakavarga", level=2))
    if strength.get("error"):
        s.refusals.append(
            "The strength of the grahas could not be computed for this "
            f"nativity: {strength['error']}. Nothing below is weighed."
        )
        return
    pindas = strength["sadbala"]
    prov = strength["provenance"]
    s.notes.append(
        "BPHS uttara 2 makes strength the arbiter: among the grahas that "
        "cause a yoga, the strongest of them is the one that gives its "
        "result. Every figure below is in rupas, one rupa being sixty "
        "virupas, as the 1899 printing writes them."
    )
    for graha, v in pindas.items():
        pinda = v["sadbala_pinda"]
        if pinda is None:
            s.notes.append(f"- **{graha}** - undecided; some limb has no input.")
            continue
        verdict = "at or above" if v["meets_minimum"] else "below"
        s.notes.append(
            f"- **{graha}** - {v['sadbala_pinda_rupas']} rupas, {verdict} the "
            f"{v['required_minimum_virupas']:.0f}-virupa minimum this "
            f"recension sets for the {v['minimum_class']} class."
        )
    s.notes.append(
        "The minima are this recension's, which groups the seven into three "
        "classes at 6|32, 5|53 and 4|13 rupas. The modern handbooks give each "
        "graha its own figure and disagree with it; nothing here is "
        "normalised to them."
    )
    for item in prov.get("withheld", []):
        s.notes.append(f"Not supplied - {item}.")
    lords = prov.get("time_lords") or {}
    if any(lords.values()):
        s.notes.append(
            "The time-lords this chart's kala-bala rests on: year "
            f"{lords.get('varshesa')}, month {lords.get('masesa')}, day "
            f"{lords.get('dinesa')}, hora {lords.get('horesa')}."
        )

    av = strength.get("ashtakavarga")
    if not av:
        return
    sub = report.add(ReportSection("Ashtakavarga", level=3))
    sub.notes.append(
        "Rekha is the scored mark and karana/bindu is the blank. Much popular "
        "writing has this exactly backwards, and the chapter lists the blanks "
        "first, so a reader who takes the first list for the scoring list "
        "builds every table inverted."
    )
    sarva = av["sarvashtakavarga"]
    sub.notes.append(
        f"Sarvashtakavarga totals {av['sarva_total']} rekhas across the twelve "
        "rasis, which is the figure the seven tables must sum to."
    )
    ranked = sorted(sarva.items(), key=lambda kv: -kv[1])
    for rasi, n in ranked[:3]:
        sub.notes.append(f"- {rasi}: {n} rekhas - {sarva_grade(n)}.")
    weakest = ranked[-1]
    sub.notes.append(
        f"- {weakest[0]}: {weakest[1]} rekhas - {sarva_grade(weakest[1])}, the "
        "least supported rasi in this chart."
    )
    thin = [g for g, n in (av.get("own_varga_rekhas") or {}).items() if n < 4]
    if thin:
        sub.notes.append(
            "Below four rekhas in its own varga, which the chapter marks for "
            "distress rather than comfort: " + ", ".join(sorted(thin)) + "."
        )


def _vargas_section(
    report: TraditionReport,
    facts: dict,
    grahas: list,
    strength: dict[str, Any],
) -> None:
    """The divisional charts, and the question each one answers.

    The engine computed D1 and D9 and nothing else. A reader asked about work
    and shown only those two has been handed the wrong instrument: the chapter
    names D10 for career, D7 for children, D12 for parents, D4 for fortune.
    """
    s = report.add(ReportSection("Divisional Charts (Vargas)", level=2))
    if not (facts.get("lagna") or {}).get("rasi"):
        return
    s.notes.append(
        "Nine of the sixteen vargas have their computation rule read from "
        "BPHS purva 3 and are given here. Six more - D16, D20, D24, D27, D40, "
        "D45 - are named by the chapter but their defining slokas were not "
        "read in the mining pass. They are unmined, not unavailable."
    )
    s.notes.append(
        "What each answers: "
        + "; ".join(f"{d} {p}" for d, p in VARGA_PURPOSE.items())
        + "."
    )
    naisargika = facts.get("naisargika_relations", {}) or {}
    rasi_index = {
        row["graha"]: RASIS.index(row["rasi"])
        for row in grahas
        if row.get("rasi") and row.get("graha")
    }
    for row in grahas:
        graha = row.get("graha")
        if graha not in rasi_index or graha not in VIMSOPAKA_GRAHAS:
            continue
        lon = rasi_index[graha] * 30.0 + float(row["degree_in_sign"])
        places = all_vargas(lon)
        sub = report.add(ReportSection(f"{graha} across the vargas", level=3))
        sub.notes.append(
            ", ".join(
                f"{d} {places[d]}"
                for d in ("D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12",
                          "D60")
                if d in places
            )
            + f"; D30 lord {places['D30']}."
        )
        vim = vimsopaka_bala(graha, lon, naisargika, rasi_index)
        sub.notes.append(
            f"Vimsopaka (saptavarga): {vim['total_vishvas']:.2f} of 20 - "
            f"{vim['grade']}."
        )
        if graha == "Sun":
            s.notes.append(vim["relation_disclosure"])
    s.notes.append(
        "Only the shadvarga and saptavarga vimsopaka schemes are offered. The "
        "dasavarga and shodasavarga schemes need the six unmined vargas, and "
        "a total computed without them would carry a precise-looking "
        "denominator it had not earned."
    )


VIMSOPAKA_GRAHAS = (
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn",
)


def _pinda(strength: dict[str, Any] | None, graha: str) -> float | None:
    if not strength:
        return None
    row = (strength.get("sadbala") or {}).get(graha)
    return row.get("sadbala_pinda") if row else None


def _adjudicate_yogas(
    section: ReportSection, yogas: list, strength: dict[str, Any] | None
) -> None:
    """Execute BPHS uttara 2.44-45 across the whole set of yogas.

    "Where many yogas are obtained, this is declared to be the rule" - the
    strongest of the grahas causing them is the one whose result arrives. A
    composer that lists every yoga side by side has detected them without
    judging them, which is the step the text says not to skip.
    """
    causes: dict[str, list[str]] = {}
    for y in yogas:
        for graha in y.get("grahas", []) or []:
            causes.setdefault(graha, []).append(y["yoga"])
    weighed = {
        g: _pinda(strength, g) for g in causes if _pinda(strength, g) is not None
    }
    if len(weighed) < 2:
        if causes and not weighed:
            section.notes.append(
                "The text ranks these by strength, and the strength of the "
                "grahas that cause them could not be computed here, so they "
                "are listed unranked - which is a gap, not a reading."
            )
        return
    order = sorted(weighed.items(), key=lambda kv: -kv[1])
    top, top_value = order[0]
    section.notes.append(
        "BPHS uttara 2.44-45: among the grahas that cause a yoga, the "
        "strongest of them is the one that gives its result. By Ṣaḍbala the "
        "causes here rank "
        + ", ".join(
            f"{g} ({strength['sadbala'][g]['sadbala_pinda_rupas']})"
            for g, _ in order
        )
        + f". So **{top}** carries this chart's yogas: "
        + ", ".join(sorted(set(causes[top])))
        + "."
    )
    unweighed = [g for g in causes if g not in weighed]
    if unweighed:
        section.notes.append(
            "Left out of that ranking because their strength is undecided: "
            + ", ".join(sorted(unweighed))
            + ". They are not ranked last; they are not ranked at all."
        )


def _rank_within_yoga(
    section: ReportSection, yoga: dict, strength: dict[str, Any] | None
) -> None:
    """Name the strongest cause of a single yoga, where it has more than one."""
    grahas = yoga.get("grahas") or []
    if len(grahas) < 2:
        return
    weighed = {g: _pinda(strength, g) for g in grahas}
    if any(v is None for v in weighed.values()):
        section.notes.append(
            "The strongest of this yoga's causes cannot be named: "
            + ", ".join(g for g, v in weighed.items() if v is None)
            + " has no decidable Ṣaḍbala."
        )
        return
    winner = max(weighed.items(), key=lambda kv: kv[1])[0]
    section.notes.append(
        f"- Of its causes, **{winner}** is the strongest by Ṣaḍbala "
        f"({strength['sadbala'][winner]['sadbala_pinda_rupas']} rūpas), and by "
        "uttara 2.44 it is the one that gives the result."
    )


def _yogas_section(
    report: TraditionReport, facts: dict, strength: dict[str, Any] | None = None
) -> None:
    s = report.add(ReportSection("Yogas Present in This Chart", level=2))
    yogas = facts.get("yogas") or []
    if not yogas:
        s.notes.append("No yoga in the engine's encoded set is formed here.")
        return
    s.notes.append(
        f"{len(yogas)} yoga(s) are formed. Each is listed with the placements "
        "that constitute it, so the claim can be checked rather than taken."
    )
    fired_rule_ids: set[str] = set()
    yoga_rule_map = {
        "Pancha Mahapurusha": "jyotisha.phaladeepika.06.pancha_mahapurusha_yoga",
        "Kesari": "jyotisha.phaladeepika.06.kesari_and_sakata_yoga",
        "Gajakesari": "jyotisha.phaladeepika.06.kesari_and_sakata_yoga",
        "Sakata": "jyotisha.phaladeepika.06.kesari_and_sakata_yoga",
        "Sunapha": "jyotisha.phaladeepika.05.sunapha_anapha_durudhara_kemadruma",
        "Anapha": "jyotisha.phaladeepika.05.sunapha_anapha_durudhara_kemadruma",
        "Durudhara": "jyotisha.phaladeepika.05.sunapha_anapha_durudhara_kemadruma",
        "Kemadruma": "jyotisha.phaladeepika.05.sunapha_anapha_durudhara_kemadruma",
        "Neechabhanga": "jyotisha.phaladeepika.neechabhanga_rajayoga",
        "Raja Yoga": "jyotisha.phaladeepika.four_rajayogas",
    }
    _adjudicate_yogas(s, yogas, strength)
    for y in yogas:
        sub = report.add(ReportSection(y["yoga"], level=3))
        sub.notes.append(f"**{y.get('summary', '')}** Rule: {y.get('rule', '')}")
        for fact in y.get("constituent_facts", []):
            sub.notes.append(f"- {fact}")
        _rank_within_yoga(sub, y, strength)
        rule_id = next(
            (rid for key, rid in yoga_rule_map.items() if key.lower() in y["yoga"].lower()),
            None,
        )
        if rule_id and rule_id in fired_rule_ids:
            sub.notes.append(
                "The classical judgment for this configuration is quoted under "
                "the yoga above that first invoked it; one source statement is "
                "not shown twice."
            )
        elif rule_id and rule_id in _rules_by_id():
            fired_rule_ids.add(rule_id)
            rule = _rules_by_id()[rule_id]
            c = rule.get("conclusion", {}) or {}
            text = None
            for key in ("judgment", "kesari_result", "graded_result",
                        "one_directional_result", "sunapha_result"):
                if isinstance(c.get(key), str):
                    text = c[key]
                    break
            if text:
                d = _delineate(rule_id, text, f"{y['yoga']} formed in this chart")
                if d:
                    sub.delineations.append(d)
        else:
            sub.refusals.append(
                f"The engine detects {y['yoga']} structurally, but no Phaladīpikā "
                "result for it is encoded in the corpus yet, so no classical "
                "verdict is quoted."
            )


def _dasha_section(report: TraditionReport, facts: dict) -> None:
    s = report.add(ReportSection("Viṃśottarī Daśā", level=2))
    current = facts.get("vimshottari_current") or {}
    maha = current.get("mahadasha") or {}
    antar = current.get("antardasha") or {}
    s.notes.append(
        "Viṃśottarī runs from the janma nakṣatra, so the whole timing layer is "
        "downstream of the Moon's longitude — a few minutes of birth-time error "
        "moves every date below."
    )
    if maha:
        s.notes.append(
            f"As of {current.get('as_of')}, the running mahādaśā is "
            f"**{maha['lord']}** ({maha['start']} → {maha['end']}), with "
            f"**{antar.get('antardasha_lord')}** antardaśā "
            f"({antar.get('start')} → {antar.get('end')})."
        )
    s.table = [
        {
            "Mahādaśā": m["lord"],
            "From": m["start"],
            "To": m["end"],
            "Years": m["years"],
            "At birth": "partial" if m.get("partial_at_birth") else "",
        }
        for m in facts.get("vimshottari_mahadashas", [])
    ]
    rule_id = "jyotisha.phaladeepika.19.vimshottari_mahadasha_significations"
    rule = _rules_by_id().get(rule_id)
    if rule and maha:
        results = (rule.get("conclusion", {}) or {}).get("results_by_graha") or {}
        text = results.get(maha["lord"]) or results.get(maha["lord"].lower())
        if text:
            d = _delineate(
                rule_id, str(text),
                f"{maha['lord']} mahādaśā running as of {current.get('as_of')}",
                caveat=(
                    "Phaladīpikā states the daśā's general significations. It does "
                    "not, in the encoded chapter, condition them on the daśā "
                    "lord's placement in this particular chart — that refinement "
                    "belongs to the commentaries and is not sourced here."
                ),
            )
            if d:
                s.delineations.append(d)
    running = maha.get("lord")
    if running:
        row = _graha_row(facts, running)
        well_placed = None
        placement_desc = ""
        if row:
            house = row["house"]
            dignity = row["dignity"]
            good_house = house in (1, 4, 5, 7, 9, 10, 11)
            bad_house = house in (6, 8, 12)
            good_dign = dignity in ("own sign", "exalted")
            bad_dign = dignity == "debilitated"
            placement_desc = (
                f"{running} stands in the {ORDINAL[house]} bhāva, {dignity}"
            )
            if (good_house or good_dign) and not (bad_house or bad_dign):
                well_placed = True
            elif bad_house or bad_dign:
                well_placed = False
        for rid, applies, label in (
            ("jyotisha.bphs.a36.vimsottari_mahadasa_utkrsta", True, "general grade"),
            ("jyotisha.bphs.a36.vimsottari_mahadasa_lord_well_placed",
             well_placed is True, "lord well placed"),
            ("jyotisha.bphs.a36.vimsottari_mahadasa_lord_badly_placed",
             well_placed is False, "lord badly placed"),
        ):
            if not applies:
                continue
            rule = _rules_by_id().get(rid)
            if not rule:
                continue
            text = (rule.get("conclusion", {}).get("results_by_graha") or {}).get(
                running
            )
            if not text:
                continue
            d = _delineate(
                rid,
                str(text),
                f"{running} mahādaśā; {placement_desc} [{label}; well/badly "
                "placed operationalized as kendra/trikoṇa/11th or own/exalted "
                "vs duḥsthāna or debilitated]",
            )
            if d:
                s.delineations.append(d)
    if not s.delineations:
        s.refusals.append(
            "No sourced signification for the running mahādaśā lord is encoded."
        )


def _navamsha_section(report: TraditionReport, facts: dict, grahas: list) -> None:
    s = report.add(ReportSection("Navāṃśa (D9)", level=2))
    s.notes.append(
        "The D9 is the tradition's own check on the D1: a graha strong in the rāśi "
        "chart but weak in navāṃśa is held to promise more than it delivers. "
        "Vargottama grahas — same sign in both — are the exception."
    )
    varg = [g["graha"] for g in grahas if g.get("vargottama")]
    s.notes.append(
        ("Vargottama here: " + ", ".join(varg) + ".") if varg
        else "No graha is vargottama in this chart."
    )
    s.table = [
        {
            "Graha": g["graha"],
            "D1 rāśi": g["rasi"],
            "D1 dignity": g["dignity"],
            "D9 rāśi": g["navamsha"],
            "D9 dignity": g["navamsha_dignity"],
        }
        for g in grahas
    ]
    s.refusals.append(
        "Only D1 and D9 are computed. The wider ṣoḍaśavarga — D10 for career, D7 "
        "for children, D12 for parents — is not, so no varga-specific judgment is "
        "made on those topics."
    )


def _drishti_section(report: TraditionReport, facts: dict) -> None:
    s = report.add(ReportSection("Drishti (Aspects)", level=2))
    s.notes.append(
        "Jyotiṣa drishti is whole-sign and mostly forward-looking: every graha "
        "aspects the 7th from itself, with Mars adding the 4th and 8th, Jupiter "
        "the 5th and 9th, and Saturn the 3rd and 10th."
    )
    s.table = [
        {
            "Graha": d["graha"],
            "From bhāva": d["from_house"],
            "Aspects": "; ".join(d.get("aspects", [])) or "—",
            "Special": d.get("special_drishti", "none"),
        }
        for d in facts.get("drishti", [])
    ]


def _limits(report: TraditionReport, facts: dict) -> None:
    report.method_notes.extend([
        f"Sidereal, Lahiri ayanāṃśa {facts['ayanamsa_degrees']:.4f}° at birth. "
        "Other ayanāṃśas (Raman, Krishnamurti) shift every position and are not "
        "computed here.",
        "Whole-sign bhāvas, which is the Parāśari norm. Śrīpati and other cusp "
        "systems would move grahas near a sign boundary into adjacent bhāvas.",
        "Delineations are quoted from four witnesses, each kept as its own "
        "voice and never merged: Phaladīpikā (grade B, translation-mediated), "
        "BPHS 1899 Subodhini (Devanāgarī read directly), Saravali 1907 Nirnaya "
        "Sagar (Devanāgarī read directly, with the edition's own printed "
        "pāṭhabheda apparatus carried where it exists), and Bṛhajjātaka (grade "
        "B via Aiyar 1905). Every Devanāgarī rendering is graded "
        "engine_translation_unreviewed; independent Sanskrit review is "
        "outstanding on all of it.",
        "The second Saravali witness is corrupt at the akṣara level, so no "
        "cross-witness collation could be established in either direction - "
        "agreement is NOT claimed. Known scan gaps are reported in place: Mars "
        "in Leo through Pisces is a lost leaf in the Saravali print, and "
        "Rāhu/Ketu have no graha-in-rāśi chapters in either author - that is "
        "the texts, not the mining.",
        "Bṛhat Parāśara Horā Śāstra now speaks in this report: Adhyāya 15's "
        "lord-in-bhāva results and Adhyāya 36's daśā gradings are quoted from "
        "the 1899 Subodhini printing (which titles itself the sārāṃśa - a "
        "compiled recension of uncertain unity, ordered Jaimini-inflected, and "
        "differing substantially from modern editions; every citation names "
        "it). An earlier version of this note called that scan unusable, which "
        "was false and is corrected: it is ordinary noisy Devanāgarī and it "
        "reads. 12 of the 144 lord-in-bhāva cells are genuinely absent from "
        "this printing and are reported as absent, not filled from later "
        "editions.",
        "The same BPHS recension grades EVERY graha's dṛṣṭi on all seven "
        "houses (3/4/5/7/8/9/10) in quarter-strengths, where this engine "
        "implements the received flat rule (all aspect the 7th; Mars adds "
        "4/8, Jupiter 5/9, Saturn 3/10). The root text and the engine "
        "disagree, the conflict is recorded in the corpus, and the flat rule "
        "is retained here as the disclosed convention rather than silently "
        "switching doctrine mid-report.",
        "Ṣaḍbala, Aṣṭakavarga and the wider vargas are not computed, so no "
        "strength-number or transit-scoring claim is made.",
        "No remedial measures (upāya), no gemstone, mantra or ritual prescription "
        "is issued. Those are religious instruction, not chart judgment.",
    ])
