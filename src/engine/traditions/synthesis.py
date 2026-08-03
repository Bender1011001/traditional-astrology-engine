"""Synthesis: from activated rules to an adjudicated reading.

The external review's deepest finding (19): the engines could prove why a
quotation was selected but could not combine conflicting quotations. This
module is the first synthesis layer, and its discipline is that it ADJUDICATES
ONLY WITH RULES THE SOURCES THEMSELVES STATE, and otherwise reports conflict as
conflict. No invented weights, no silent averaging.

What it does:

  1. Topic-tags every fired delineation, clause by clause (wealth, children,
     learning, character, health, career, family, marriage, fame, speech).
  2. Assigns clause polarity (favourable / unfavourable / descriptive).
  3. Tracks witness identity by author, so two quotes from one author are one
     witness and shared lineage never counts as corroboration (review, 11).
  4. Surfaces per-topic agreement (distinct authors, same polarity) and
     contradiction (distinct authors or placements, opposite polarity) - and
     when nothing in the corpus resolves a contradiction, says so.
  5. Applies the tradition's OWN stated qualifiers where the corpus carries
     them. For Jyotisha these are Saravali's judgment-order gates:
       23.86 - a rasi result is realised in full only when the rasi lord and
               the graha are strong; otherwise it is qualified.
       24.23 - the rasi result is checked when the navamsa lord is strong:
               D9 explicitly outranks the D1 verdict, in the author's words.
       30.86-87 - occupancy effects invert in the 6th, 8th and 12th, and the
               bhava table is defeasible by yoga, drishti and exaltation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .report import Delineation, ReportSection

# --- topics ------------------------------------------------------------------

TOPIC_PATTERNS: dict[str, re.Pattern[str]] = {
    "wealth": re.compile(
        r"\b(wealth\w*|rich(es)?|poor|poverty|money|treasur\w*|prosper\w*|"
        r"indigen\w*|gains?|income|fortune|affluen\w*|penniless)\b", re.I),
    "children": re.compile(
        r"\b(child(ren)?|sons?|daughters?|progeny|offspring|barren|issue)\b", re.I),
    "learning": re.compile(
        r"\b(learn(ed|ing)?|intellect\w*|intelligen\w*|wise|wisdom|knowledge|"
        r"scholar\w*|sastra\w*|shastra\w*|poet\w*|calculation|eloquen\w*|"
        r"speech|witty|ignoran\w*|stupid|dull)\b", re.I),
    "character": re.compile(
        r"\b(virtuo\w*|cruel\w*|kind|angry|anger|gentle|honest\w*|sinful|"
        r"wicked\w*|liberal|miser\w*|generous|proud|humble|brave\w*|coward\w*|"
        r"steady|unsteady|grateful|deceit\w*|thie(f|ves)|gambl\w*)\b", re.I),
    "health": re.compile(
        r"\b(disease[sd]?|sick\w*|health\w*|ill|body|limbs?|eyes?|blind\w*|"
        r"deaf|strong constitution|weak\w*|injur\w*|wound\w*|pain\w*|"
        r"afflict\w*)\b", re.I),
    "career": re.compile(
        r"\b(kings?|minister\w*|command\w*|arm(y|ies)|servants?|service|"
        r"profession\w*|occupation\w*|rank|status|honou?r\w*|authority|"
        r"rulers?|lord(ship)?s?|employ\w*|agricultur\w*|trade\w*)\b", re.I),
    "family": re.compile(
        r"\b(father\w*|mother\w*|brothers?|siblings?|family|kinsmen|"
        r"relations)\b", re.I),
    "marriage": re.compile(
        r"\b(wife|wives|husbands?|spouses?|marri\w*|damsels?|women|"
        r"conjugal)\b", re.I),
    "fame": re.compile(
        r"\b(fame|famous|renown\w*|celebrat\w*|reputation|known|disgrace\w*|"
        r"humiliat\w*|insult\w*|odious|despised|hated|praised)\b", re.I),
    "happiness": re.compile(
        r"\b(happy|happiness|unhappy|miser(y|able)|sorrow\w*|joy\w*|"
        r"comforts?|content\w*|distress\w*|grie(f|ved))\b", re.I),
}

FAVOURABLE = re.compile(
    r"\b(wealthy|rich(es)?|prosper\w*|happy|happiness|learned|wise|"
    r"intelligen\w*|famous|renown\w*|virtuo\w*|blessed|good|strong|brave|"
    r"liberal|generous|honou?r\w*|success\w*|gains?|victor\w*|comforts?|"
    r"lovely|beautiful|healthy|praised|respected|eloquen\w*|sweet\w*|kings?|"
    r"minister\w*|affluen\w*|endowed)\b", re.I)
UNFAVOURABLE = re.compile(
    r"\b(poor|poverty|loses?|loss|miser(y|able|ly)|unhappy|sorrow\w*|"
    r"disease[sd]?|sick\w*|ignoran\w*|stupid|cruel\w*|wicked\w*|sinful|"
    r"hated|odious|despised|disgrace\w*|humiliat\w*|insult\w*|barren|"
    r"deform\w*|defect\w*|weak\w*|afflict\w*|distress\w*|grie(f|ved)|"
    r"enem(y|ies)|quarrels?|idle|indolent|thie(f|ves)|gambl\w*|angry|harsh|"
    r"without\s+wealth|devoid|bereft|destruction|ruin\w*)\b", re.I)

_CLAUSE = re.compile(r"[;.!?]")


@dataclass
class Claim:
    """One clause of one fired delineation, normalized for adjudication."""

    text: str
    topic: str
    polarity: str          # favourable | unfavourable | descriptive
    author: str            # witness identity - the independence unit
    rule_id: str
    trigger: str
    qualifiers: list[str] = field(default_factory=list)


AUTHOR_OF_PREFIX = (
    ("jyotisha.bphs.", "Parāśara (BPHS, 1899 Subodhini recension)"),
    ("jyotisha.saravali.", "Kalyāṇavarma (Saravali)"),
    ("jyotisha.brhajjataka.", "Varāhamihira (Bṛhajjātaka)"),
    ("jyotisha.phaladeepika.", "Mantreśvara (Phaladīpikā)"),
    ("bazi.delin.", "Yuanhai Ziping / Sanming Tonghui"),
    ("hel.firmicus.", "Firmicus Maternus (Mathesis)"),
    ("hel.ptolemy", "Ptolemy (Apotelesmatika)"),
    ("islam.qabisi.", "al-Qabīsī (Mudkhal)"),
)


def author_of(rule_id: str) -> str:
    for prefix, author in AUTHOR_OF_PREFIX:
        if rule_id.startswith(prefix):
            return author
    return rule_id.split(".")[0]


def clause_polarity(clause: str) -> str:
    fav = len(FAVOURABLE.findall(clause))
    unfav = len(UNFAVOURABLE.findall(clause))
    if fav > unfav:
        return "favourable"
    if unfav > fav:
        return "unfavourable"
    return "descriptive"


def claims_from(delineations: list[Delineation]) -> list[Claim]:
    out: list[Claim] = []
    for d in delineations:
        for clause in _CLAUSE.split(d.text):
            clause = clause.strip()
            if len(clause) < 4 or clause.startswith("["):
                continue
            for topic, pattern in TOPIC_PATTERNS.items():
                if pattern.search(clause):
                    out.append(Claim(
                        text=clause,
                        topic=topic,
                        polarity=clause_polarity(clause),
                        author=author_of(d.rule_id),
                        rule_id=d.rule_id,
                        trigger=d.trigger,
                    ))
    return out


# --- Jyotisha's own qualifiers (sourced, not invented) -----------------------

DUSTHANAS = (6, 8, 12)
STRONG_DIGNITIES = {"own sign", "exalted"}
WEAK_DIGNITIES = {"debilitated"}


def apply_saravali_gates(claims: list[Claim], facts: dict[str, Any]) -> None:
    """Attach the tradition's own qualification rules to affected claims.

    Nothing is deleted or down-weighted by fiat: each gate quotes its source
    and states what the source says about THIS claim's reliability.
    """
    grahas = {g["graha"]: g for g in facts.get("grahas", [])}

    for claim in claims:
        graha = next((g for g in grahas if claim.trigger.startswith(g)), None)
        if graha is None:
            continue
        row = grahas[graha]

        if "graha_in_rasi" in claim.rule_id:
            # 23.86: full realisation needs strength; weigh by exaltation state.
            if row.get("dignity") in STRONG_DIGNITIES:
                claim.qualifiers.append(
                    f"Saravali 23.86: realised in full - {graha} is "
                    f"{row['dignity']}, satisfying the strength condition the "
                    "text sets for the rāśi result."
                )
            elif row.get("dignity") in WEAK_DIGNITIES:
                claim.qualifiers.append(
                    f"Saravali 23.86: qualified - {graha} is debilitated, and "
                    "the text says the rāśi result is realised in full only "
                    "with strength; weigh accordingly."
                )
            # 24.23: the navamsa lord's strength checks the rasi result.
            if row.get("navamsha_dignity") in STRONG_DIGNITIES:
                claim.qualifiers.append(
                    f"Saravali 24.23: checked - {graha}'s navāṃśa dignity is "
                    f"{row['navamsha_dignity']}, and the text puts a strong "
                    "navāṃśa lord ABOVE the D1 verdict."
                )
            if row.get("vargottama"):
                claim.qualifiers.append(
                    "Saravali 24.22: vargottama - same sign in D1 and D9 "
                    "strengthens the testimony."
                )

        if "graha_in_bhava" in claim.rule_id or "planet_in_bhava" in claim.rule_id:
            house = row.get("house")
            if house in DUSTHANAS:
                claim.qualifiers.append(
                    f"Saravali 30.86-87: the {house}th is a duḥsthāna, where "
                    "the text INVERTS occupancy effects - malefics striking a "
                    "bhāva they occupy, benefics nourishing it, reverse here; "
                    "and the whole bhāva table is defeasible by yoga, drishti "
                    "and exaltation."
                )


# --- adjudication ------------------------------------------------------------

def synthesize(
    delineations: list[Delineation],
    facts: dict[str, Any] | None = None,
    tradition: str = "jyotisha",
) -> ReportSection:
    """Adjudicate fired claims into a per-topic synthesis section.

    Corroboration requires DISTINCT AUTHORS with the same polarity on the same
    topic. Contradiction is reported as contradiction, with whatever the
    sources themselves say about precedence attached - and where they say
    nothing, that is stated rather than papered over.
    """
    claims = claims_from(delineations)
    if facts is not None and tradition == "jyotisha":
        apply_saravali_gates(claims, facts)

    section = ReportSection("Synthesis by Life Topic", level=2)
    if not claims:
        section.notes.append("No fired delineation carries a taggable claim.")
        return section

    section.notes.append(
        "Adjudication uses only precedence the sources themselves state "
        "(Saravali 23.86, 24.23, 30.86-87 for this tradition). Agreement is "
        "counted between DISTINCT authors - one author quoted twice is one "
        "witness - and a contradiction no source resolves is reported as "
        "unresolved, not silently averaged away."
    )

    by_topic: dict[str, list[Claim]] = {}
    for claim in claims:
        by_topic.setdefault(claim.topic, []).append(claim)

    for topic in sorted(by_topic, key=lambda t: -len(by_topic[t])):
        topic_claims = by_topic[topic]
        authors_fav = {c.author for c in topic_claims if c.polarity == "favourable"}
        authors_unfav = {c.author for c in topic_claims if c.polarity == "unfavourable"}

        lines = [f"**{topic.capitalize()}** — {len(topic_claims)} clause(s) from "
                 f"{len({c.author for c in topic_claims})} author(s)."]

        if len(authors_fav) >= 2 and not authors_unfav:
            lines.append(
                "Corroborated favourable: "
                + "; ".join(sorted(authors_fav))
                + " agree independently."
            )
        elif len(authors_unfav) >= 2 and not authors_fav:
            lines.append(
                "Corroborated unfavourable: "
                + "; ".join(sorted(authors_unfav))
                + " agree independently."
            )
        elif authors_fav and authors_unfav:
            lines.append(
                "CONTRADICTION: favourable testimony from "
                + "; ".join(sorted(authors_fav))
                + " against unfavourable testimony from "
                + "; ".join(sorted(authors_unfav)) + "."
            )
            resolved = [c for c in topic_claims if c.qualifiers]
            if resolved:
                lines.append(
                    "The sources' own gates bear on it: "
                    + " ".join(q for c in resolved for q in c.qualifiers[:1])
                )
            else:
                lines.append(
                    "No precedence rule in the corpus resolves this. The "
                    "conflict stands, and choosing a side would be the "
                    "engine's invention, not the tradition's."
                )
        else:
            single = sorted({c.author for c in topic_claims})
            lines.append(
                ("Single-witness testimony from " + "; ".join(single) + " - "
                 "uncorroborated, not confirmed.")
            )

        for claim in topic_claims:
            marker = {"favourable": "+", "unfavourable": "−"}.get(claim.polarity, "·")
            lines.append(
                f"  {marker} {claim.text[:110]} — *{claim.author}*, "
                f"selected by {claim.trigger.split('·')[0].strip()}"
            )
            for q in claim.qualifiers:
                lines.append(f"      ↳ {q}")
        section.notes.append("\n".join(lines))

    return section
