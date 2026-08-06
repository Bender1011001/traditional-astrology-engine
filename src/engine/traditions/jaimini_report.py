"""A Jaimini report, read from the karaka-kundali rather than the birth lagna.

Jaimini was the largest track in the corpus with no engine at all: 116 rules
across two packs, 100 validation vectors, and nothing that turned any of it
into a page. Not a computation module either - unlike al-Qabisi, where the
arithmetic existed and only the report was missing, this track had neither.

The judgment order is the one the sutras themselves run in, recorded in the
pack as jaimini.judgment.hierarchy: rasi drsti first, then argala, then the
chara karakas, then the sthira karakas alongside them, then the arudha padas
as a parallel frame, then the special lagnas, then the dasas. Strength is a
tie-breaker inside those steps and not a step of its own.

The reading frame is Abhyankar's, taken from all fourteen of his worked
charts: a karaka-kundali cast with the Atmakaraka's sign as its first house.
Every delineation in Adhyaya 1 Pada 2 is read from that frame, not from the
birth ascendant, and this report follows him.

What it will not do is merge with the Parasari report. The two nominate
different significators, draw different aspect lines and open different
periods; the pack's own refusal rule says that where both are shown they are
shown as two readings with their disagreements visible. So the Vedic report
and this one are separate documents, and this one says where they differ.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from ..multitradition import build_panel
from ..multitradition.jaimini import (
    JaiminiChart,
    build as build_jaimini,
)
from ..multitradition.jyotisha_strength_inputs import (
    local_datetime,
    sun_times,
)
from ..multitradition.types import BirthInput
from .report import Delineation, ReportSection, TraditionReport

ORDINAL = {
    1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th",
    7: "7th", 8: "8th", 9: "9th", 10: "10th", 11: "11th", 12: "12th",
}

RESEARCH_ROOT = (
    Path(__file__).resolve().parents[3] / "docs" / "research" / "multitradition"
)
JAIMINI_DIR = RESEARCH_ROOT / "jaimini"

RASIS_INDEX = {
    r: i
    for i, r in enumerate((
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    ))
}


@lru_cache(maxsize=1)
def _rules_by_id() -> dict[str, dict[str, Any]]:
    rules: dict[str, dict[str, Any]] = {}
    for path in sorted(JAIMINI_DIR.glob("*rule_manifest.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for rule in data.get("rules", []):
            rid = rule.get("rule_id")
            if rid:
                rules[rid] = rule
    return rules


def _source_label(rule: dict[str, Any]) -> str:
    passages = rule.get("source_passages") or []
    if passages:
        p = passages[0]
        work = p.get("work") or "Jaimini Sutras"
        loc = p.get("location") or p.get("section") or ""
        return f"{work}, {loc}".strip().rstrip(",")
    return "Jaimini Upadesa Sutras, with the Sutrarthaprakasika"


def _fire(rule_id: str, trigger: str) -> Delineation | None:
    """Quote a rule, honouring the pack's abstentions.

    A rule marked ``abstain`` is a deliberate refusal to decide, not a missing
    result, and firing it as a delineation would turn the abstention into a
    verdict. Those are surfaced as notes by their callers instead.
    """
    rule = _rules_by_id().get(rule_id)
    if rule is None:
        return None
    c = rule.get("conclusion", {}) or {}
    if c.get("abstain") or "refus" in str(c.get("ctype", "")).lower():
        return None
    if "refus" in str(c.get("output_policy") or "").lower():
        return None
    text = c.get("engine_rendering")
    if not isinstance(text, str) or not text.strip():
        return None
    return Delineation(
        text=text.strip(),
        rule_id=rule_id,
        source=_source_label(rule),
        evidence_grade=rule.get("evidence_grade", "?"),
        trigger=trigger,
    )


def _sunrise_offset(
    birth: BirthInput, facts: dict[str, Any]
) -> tuple[float | None, float | None]:
    """Hours from sunrise to the birth, and the Sun's sidereal longitude.

    The special lagnas all start at sunrise and advance at fixed rates, so
    without this they cannot be computed at all. This package already finds
    sunrise for Sadbala's ghati clock; there is no reason for Jaimini to
    refuse for want of the same number.
    """
    sun_row = next(
        (r for r in facts.get("grahas", []) if r.get("graha") == "Sun"), None
    )
    if sun_row is None:
        return None, None
    sun_longitude = (
        RASIS_INDEX[sun_row["rasi"]] * 30.0 + float(sun_row["degree_in_sign"])
    )
    try:
        moment = local_datetime(
            birth.civil_date, birth.civil_time, birth.utc_offset_hours
        )
        times = sun_times(moment, birth.latitude, birth.longitude)
    except Exception:
        return None, sun_longitude
    if times is None:
        return None, sun_longitude
    return (times["jd"] - times["sunrise"]) * 24.0, sun_longitude


def _chart_from_panel(birth: BirthInput) -> JaiminiChart:
    """Jaimini reads the same sidereal positions the Parasari section computes.

    Sharing the calculation is not merging the readings: the longitudes are
    astronomy and belong to neither branch. What the two do with them diverges
    from the next line onward.
    """
    panel = build_panel(birth)
    section = next(
        (
            s for s in panel["sections"]
            if s["tradition_id"] == "indian_jyotisha" and not s.get("error")
        ),
        None,
    )
    if section is None:
        raise RuntimeError("the Jyotisha calculation produced no facts")
    facts = section["facts"]
    graha_rasis: dict[str, str] = {}
    degrees: dict[str, float] = {}
    for row in facts.get("grahas", []):
        name = row.get("graha")
        if not name or not row.get("rasi"):
            continue
        graha_rasis[name] = row["rasi"]
        degrees[name] = float(row["degree_in_sign"])
    lagna = (facts.get("lagna") or {}).get("rasi")
    if not lagna:
        raise RuntimeError("no lagna was computed")
    offset, sun_longitude = _sunrise_offset(birth, facts)
    return JaiminiChart(
        lagna_rasi=lagna,
        graha_rasis=graha_rasis,
        degrees_in_sign=degrees,
        sun_longitude=sun_longitude,
        sunrise_to_birth_hours=offset,
    )


def build_report(
    birth: BirthInput,
    karaka_scheme: str | None = None,
    rahu_counting: str = "forward",
) -> TraditionReport:
    """Build the report.

    ``karaka_scheme`` is left None by default and that is the point: the
    sutra's own *saptanam astanam va* leaves it open, so an engine that
    defaulted would be making the choice silently on the reader's behalf.
    """
    chart = _chart_from_panel(birth)
    chart.karaka_scheme = karaka_scheme
    chart.rahu_counting = rahu_counting
    j = build_jaimini(chart)

    report = TraditionReport(
        tradition_id="jaimini",
        display_name="Jaimini — Chara Karakas, Rasi Drsti, and the Padas",
        birth=birth.to_dict(),
    )
    _opening(report, birth, chart, j)
    _drsti_section(report, j)
    _argala_section(report, j)
    _katapayadi_section(report)
    _karaka_section(report, j)
    _sthira_karaka_section(report)
    _pada_section(report, j)
    _lagna_section(report, j)
    _dasa_section(report, j)
    _limits(report, j)
    return report


def _opening(
    report: TraditionReport, birth: BirthInput, chart: JaiminiChart, j: dict
) -> None:
    s = report.add(ReportSection("The Frame This Chart Is Read From", level=2))
    s.notes.append(
        f"Born {birth.civil_date} at {birth.civil_time} in "
        f"{birth.place_label}. The birth lagna is {chart.lagna_rasi}."
    )
    ak_rasi = j.get("karaka_kundali_first_house")
    karakas = j.get("chara_karakas") or []
    if ak_rasi and karakas:
        s.notes.append(
            f"But the reading runs from the **karaka-kundali**, whose first "
            f"house is the Atmakaraka's sign — {karakas[0].graha} in "
            f"{ak_rasi}. This is Abhyankar's own frame in all fourteen of his "
            "worked charts, and every delineation in Adhyaya 1 Pada 2 is read "
            "from it rather than from the birth ascendant."
        )
    d = _fire(
        "jaimini.worked-example.frame.karaka-kundali",
        "the frame every Jaimini delineation is read from",
    )
    if d:
        s.delineations.append(d)
    d = _fire(
        "jaimini.judgment.hierarchy",
        "the order the sutras themselves run in",
    )
    if d:
        s.delineations.append(d)


def _drsti_section(report: TraditionReport, j: dict) -> None:
    """Rasi drsti: the aspect scheme that has no Parasari counterpart."""
    s = report.add(ReportSection("Rasi Drsti — Signs Aspecting Signs", level=2))
    for rule_id, trigger in (
        ("jaimini.drsti.rasi.movable", "a movable sign's aspect"),
        ("jaimini.drsti.rasi.fixed", "a fixed sign's aspect"),
        ("jaimini.drsti.rasi.dual", "a dual sign's aspect"),
        ("jaimini.graha-drsti.inherits-rasi-drsti",
         "a graha aspects what its sign aspects"),
    ):
        d = _fire(rule_id, trigger)
        if d:
            s.delineations.append(d)

    s.notes.append(
        "This is a SIGN aspect. It is not the Parasari scheme with different "
        "names: a movable sign never aspects its own opposite, and Mars' "
        "fourth and eighth do not appear here at all."
    )
    for graha, seen in (j.get("graha_drsti") or {}).items():
        s.notes.append(f"- **{graha}** aspects {', '.join(seen)}.")
    for rule_id, trigger in (
        ("jaimini.worked-example.ranade.rasi-drsti-confirmed",
         "the Ranade chart, confirming the table three times"),
        ("jaimini.worked-example.lokur.rasi-drsti-confirmed",
         "the Lokur chart, confirming it twice more"),
    ):
        d = _fire(rule_id, trigger)
        if d:
            s.delineations.append(d)


def _argala_section(report: TraditionReport, j: dict) -> None:
    """Argala: the bolt thrown across a place, and what obstructs it."""
    s = report.add(ReportSection("Argala — Intervention and Obstruction", level=2))
    for rule_id, trigger in (
        ("jaimini.argala.from-2nd-4th-11th", "where an argala forms"),
        ("jaimini.argala.from-3rd-malefic-majority",
         "the argala from the 3rd, which forms only by the many"),
        ("jaimini.argala.virodha-houses", "which houses obstruct"),
        ("jaimini.argala.virodha-fails-when-weaker",
         "when the obstruction fails"),
        ("jaimini.argala.from-trikona", "the trikona argala"),
    ):
        d = _fire(rule_id, trigger)
        if d:
            s.delineations.append(d)

    for label, key in (
        ("the birth lagna", "argala_from_lagna"),
        ("the karaka lagna", "argala_from_karaka_lagna"),
    ):
        block = j.get(key)
        if not block:
            continue
        sub = report.add(ReportSection(f"Argala on {label}", level=3))
        sub.notes.append(f"Reference sign: {block['reference_rasi']}.")
        if not block["argalas"]:
            sub.notes.append("No argala forms on this point.")
        for a in block["argalas"]:
            holds = a["obstruction_holds"]
            verdict = (
                "obstructed" if holds is True
                else "unobstructed" if holds is False
                else "obstructors equal in number — undecided, because the "
                "commentary is explicit that strength still decides and a "
                "graha exalted or in its own sign can be balin when outnumbered"
            )
            sub.notes.append(
                f"- From the {ORDINAL[a['from_house']]}: "
                f"{', '.join(a['grahas'])}. Obstructors in the "
                f"{ORDINAL[a['obstructed_by_house']]}: "
                f"{', '.join(a['obstructors']) or 'none'} — {verdict}."
            )
        third = block["third_house_argala"]
        if third["grahas"]:
            sub.notes.append(
                f"- From the 3rd: {', '.join(third['grahas'])} "
                f"({len(third['malefics'])} malefic, "
                f"{len(third['benefics'])} benefic). On the 'three or more "
                "malefics' reading it "
                + ("forms" if third["forms_on_three_or_more"] else "does not form")
                + "; on the 'malefics outnumber benefics' reading it "
                + ("forms" if third["forms_on_outnumbering"] else "does not form")
                + "."
            )
            sub.notes.append(third["reading_note"])

    lagna_block = j.get("argala_from_lagna") or {}
    if lagna_block:
        s.notes.append(lagna_block["target_fork"])
        s.notes.append(lagna_block["pairing_fork"])


def _sutra_delineation(rule_id: str, text: str, trigger: str) -> Delineation | None:
    """Fire from the analytical pack, which states the sutra and not a rendering.

    The base manifest holds the sutra text under its own key and the substance
    under a per-rule field name. Nothing in it carries engine_rendering, which
    is exactly why every one of its 41 rules was unreachable.
    """
    rule = _rules_by_id().get(rule_id)
    if rule is None or not text.strip():
        return None
    c = rule.get("conclusion") or {}
    sutra = c.get("sutra") or c.get("stated_as")
    body = text.strip()
    if isinstance(sutra, str) and sutra.strip():
        body = f"{body} (*{sutra.strip()}*)"
    return Delineation(
        text=body,
        rule_id=rule_id,
        source=_source_label(rule),
        evidence_grade=rule.get("evidence_grade", "?"),
        trigger=trigger,
    )


def _katapayadi_section(report: TraditionReport) -> None:
    """Step one of the tradition's own judgment order: decode the text.

    The report followed the hierarchy from step two onward, which is a strange
    place to begin when the sutras are written in numeric code.
    """
    rule = _rules_by_id().get("jaimini.katapayadi.bhava-and-rasi")
    if rule is None:
        return
    c = rule.get("conclusion") or {}
    s = report.add(ReportSection("Reading the Sūtras (Kaṭapayādi)", level=2))
    d = _sutra_delineation(
        "jaimini.katapayadi.bhava-and-rasi",
        str(c.get("decoding", "")),
        "the sūtras are written in numeric code",
    )
    if d:
        s.delineations.append(d)
    worked = c.get("worked_example_in_commentary")
    if worked:
        s.notes.append(f"The commentary's own worked example: {worked}.")
    if c.get("second_example"):
        s.notes.append(f"And a second: {c['second_example']}.")
    if c.get("why_this_matters"):
        s.notes.append(str(c["why_this_matters"]))
    limit = _rules_by_id().get("jaimini.katapayadi.not-grahas")
    if limit:
        lc = limit.get("conclusion") or {}
        s.notes.append(
            "The code does not extend everywhere: "
            + str(lc.get("decoding", "")).rstrip(".")
            + "."
        )


def _sthira_karaka_section(report: TraditionReport) -> None:
    """The FIXED significators, which the chara karakas do not replace.

    Jaimini uses both. A report that computes the variable set and never says
    the fixed one exists has quietly halved the tradition's significator
    apparatus.
    """
    s = report.add(ReportSection("The Sthira Kārakas", level=2))
    s.notes.append(
        "These are fixed by nature and do not change from chart to chart. "
        "They coexist with the chara kārakas above rather than being replaced "
        "by them — Jaimini uses both, and the report would be reading with "
        "one of the two if this section were absent."
    )
    for rule_id, graha in (
        ("jaimini.sthira-karaka.mars", "Mars"),
        ("jaimini.sthira-karaka.mercury", "Mercury"),
    ):
        rule = _rules_by_id().get(rule_id)
        if rule is None:
            continue
        c = rule.get("conclusion") or {}
        signifies = c.get("signifies") or []
        d = _sutra_delineation(
            rule_id,
            f"{graha} fixedly signifies " + ", ".join(signifies),
            f"the sthira kāraka of {graha}",
        )
        if d:
            s.delineations.append(d)
        if c.get("note"):
            s.notes.append(str(c["note"]))

    disputed = _rules_by_id().get(
        "jaimini.sthira-karaka.jupiter-venus-saturn.disputed"
    )
    if disputed is None:
        return
    c = disputed.get("conclusion") or {}
    sub = report.add(
        ReportSection("Grandfather, Husband and Son — Disputed", level=3)
    )
    sub.notes.append(
        "The two readings assign the SAME three topics to DIFFERENT grahas, "
        "so this is a fork that changes who signifies what, not a wording "
        "quibble. Both are given; neither is adopted."
    )
    sub.notes.append(f"Abhyankar reads: {c.get('reading_abhyankar')}.")
    sub.notes.append(
        f"The Sūtrārthaprakāśikā reads: {c.get('reading_sutrarthaprakasika')}."
    )
    if c.get("textual_basis_of_the_split"):
        sub.notes.append(
            f"The basis of the split: {c['textual_basis_of_the_split']}."
        )
    if c.get("sutra"):
        sub.notes.append(f"The sūtra itself: *{c['sutra']}*.")


def _karaka_section(report: TraditionReport, j: dict) -> None:
    """The chara karakas - assigned per chart, not fixed by nature."""
    s = report.add(ReportSection("The Chara Karakas", level=2))
    for rule_id, trigger in (
        ("jaimini.chara-karaka.atmakaraka.by-degree",
         "how the Atmakaraka is found"),
        ("jaimini.chara-karaka.descending-order",
         "and how the rest follow from it"),
    ):
        d = _fire(rule_id, trigger)
        if d:
            s.delineations.append(d)

    s.notes.append(
        "Parasari karakas are fixed by nature — the Sun is always the father, "
        "the Moon always the mother. Jaimini's are assigned per chart by "
        "degree, so the same graha signifies different topics in different "
        "nativities. That is the deepest difference between the two branches."
    )
    for k in j.get("chara_karakas") or []:
        if k.title:
            s.notes.append(
                f"- Rank {k.rank}: **{k.graha}** at {k.degree_in_sign:.4f}° "
                f"within its sign — {k.title}."
            )
        else:
            s.notes.append(
                f"- Rank {k.rank}: **{k.graha}** at {k.degree_in_sign:.4f}° "
                f"within its sign — untitled, because {k.note}."
            )
    if j.get("karaka_scheme") is None:
        s.refusals.append(
            "No karaka below rank one is named. " + j["karaka_scheme_fork"]
        )
    else:
        s.notes.append(
            f"The **{j['karaka_scheme']}**-karaka scheme was declared for this "
            "reading. " + j["karaka_scheme_fork"]
        )
    s.notes.append(
        f"Rahu is counted **{j['rahu_convention']}**. "
        + j["rahu_convention_fork"]
    )
    for rule_id, trigger in (
        ("jaimini.worked-example.suite.result",
         "how the rule fares against the editor's own fourteen charts"),
        ("jaimini.worked-example.suite.rahu-convention-discriminated",
         "the one chart whose numbers settle the Rahu convention"),
        ("jaimini.worked-example.suite.karaka-scheme-not-settled",
         "and the question the worked charts cannot settle"),
    ):
        d = _fire(rule_id, trigger)
        if d:
            s.delineations.append(d)


def _pada_section(report: TraditionReport, j: dict) -> None:
    """The arudha padas - a second twelve-house frame read alongside the first."""
    s = report.add(ReportSection("The Arudha Padas", level=2))
    for rule_id, trigger in (
        ("jaimini.arudha.general", "how a pada is found"),
        ("jaimini.arudha.exception.lord-in-4th",
         "the exception when the lord stands in the 4th"),
        ("jaimini.arudha.exception.lord-in-7th",
         "and when it stands in the 7th"),
    ):
        d = _fire(rule_id, trigger)
        if d:
            s.delineations.append(d)
    s.notes.append(
        "The padas have no counterpart in the Parasari natal method. They "
        "produce an entirely separate twelve-house frame — the pada-kundali — "
        "that Jaimini reads alongside the rasi chart, not instead of it."
    )
    for key, row in (j.get("pada_kundali") or {}).items():
        n = key.split("_")[1]
        note = f" ({row['exception']})" if row["exception"] else ""
        s.notes.append(
            f"- Bhava {n} ({row['bhava_rasi']}), lord {row['lord']} in "
            f"{row['lord_rasi']} → pada **{row['pada']}**{note}."
        )


def _lagna_section(report: TraditionReport, j: dict) -> None:
    """The special lagnas, which advance uniformly rather than by ascension."""
    s = report.add(ReportSection("The Special Lagnas", level=2))
    for rule_id, trigger in (
        ("jaimini.special-lagna.hora-lagna.rate", "the Hora Lagna's rate"),
        ("jaimini.special-lagna.ghatika-lagna.rate",
         "the Ghatika Lagna's rate"),
        ("jaimini.special-lagna.bhava-lagna.rate", "the Bhava Lagna's rate"),
    ):
        d = _fire(rule_id, trigger)
        if d:
            s.delineations.append(d)

    lagnas = j.get("special_lagnas")
    if not lagnas:
        s.refusals.append(
            "The special lagnas are not computed for this report: "
            + str(j.get("special_lagnas_withheld", "inputs missing"))
            + ". They advance from sunrise at fixed rates, and a lagna "
            "computed from a guessed sunrise would be a guess wearing a "
            "degree sign."
        )
        return
    for name, row in lagnas.items():
        s.notes.append(
            f"- **{name}** — {row['degree_in_sign']:.2f}° {row['rasi']} "
            f"(one sign per {1 / row['rate_signs_per_hour']:.2g} hour(s))."
        )
    s.notes.append(j["special_lagna_origin_fork"])

    v = j.get("varnada")
    if v:
        s.notes.append(
            f"The Varnada falls in **{v['rasi']}** (counts "
            f"{v['counts']['from_lagna']} and "
            f"{v['counts']['from_hora_lagna']}, {v['combined']})."
        )
        s.refusals.append(
            "The Varnada is shown as a figure and is NOT read. " + v["why"]
        )


def _dasa_section(report: TraditionReport, j: dict) -> None:
    """Chara dasa: the sequence is settled, the period lengths are not."""
    s = report.add(ReportSection("Chara Dasa", level=2))
    for rule_id, trigger in (
        ("jaimini.dasa.direction.odd-forward", "the direction for odd signs"),
        ("jaimini.dasa.direction.even-reverse", "and for even signs"),
        ("jaimini.dasa.chara.direction.fixed-sign-exception",
         "the four signs where the parity rule is suspended"),
        ("jaimini.dasa.cycle.144-year-bound", "the bound on the whole cycle"),
        ("jaimini.dasa.chara.length.sign-to-its-lord",
         "how a period's length is counted"),
    ):
        d = _fire(rule_id, trigger)
        if d:
            s.delineations.append(d)

    dasa = j.get("chara_dasa") or {}
    s.notes.append(
        "Jaimini's dasas run on SIGNS, not on grahas. Vimsottari is a "
        "nakshatra-seeded planetary dasa; this is a sign sequence whose "
        "lengths are computed per sign."
    )
    s.notes.append(
        f"From the lagna the sequence runs **{dasa.get('direction')}**: "
        + " → ".join(dasa.get("sequence_from_lagna") or [])
        + "."
    )
    lengths = dasa.get("lengths") or {}
    s.refusals.append(
        "No period LENGTHS are issued. "
        + str(lengths.get("why_refused", ""))
        + " The three the sutra does not settle: "
        + "; ".join(lengths.get("undecided_conventions") or [])
        + ". What is settled is "
        + str(lengths.get("what_is_settled", ""))
        + "."
    )


def _limits(report: TraditionReport, j: dict) -> None:
    s = report.add(ReportSection("What This Report Does Not Claim", level=2))
    d = _fire(
        "jaimini.refusal.no-parasari-merge",
        "why this report stands apart from the Parasari one",
    )
    if d:
        s.delineations.append(d)
    s.notes.append(
        "Jaimini and Parasari nominate different significators, draw "
        "different aspect lines and open different periods. This report and "
        "the Jyotisha report are two readings of one chart, and where they "
        "disagree the disagreement is the finding — neither is folded into "
        "the other."
    )
    s.notes.append(
        "The strength order this branch uses runs "
        + " < ".join(j.get("strength_order_ascending") or [])
        + " — Saturn weakest, the Sun strongest. The same series is encoded "
        "on the Parasari side from Brhajjataka, which makes it a genuine "
        "point of agreement between the two branches rather than a "
        "coincidence."
    )
    s.notes.append(
        "Every rendering from the Sanskrit is unreviewed. Rule ids are given "
        "throughout so any line can be taken back to the sutra and its "
        "commentary."
    )
