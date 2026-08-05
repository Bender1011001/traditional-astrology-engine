"""Regression tests for the per-tradition report engines.

These exist because each guarded failure actually happened:

- "short-lived"/"long-lived" reached the rendered Vedic report through ordinary
  placement aphorisms, despite a declared longevity refusal (rule-category
  suppression alone cannot catch semantic content).
- The same source quotation was rendered under both the graha section and the
  bhava section, making one witness look like two.
- The al-Qabisi hyleg settlement treated the uncomputed prenatal syzygy as a
  FAILED candidate and declared the Ascendant settled - unknown collapsed into
  false.
"""

from __future__ import annotations

import re
from collections import Counter
from datetime import date

import pytest

from src.engine.multitradition import build_panel
from src.engine.multitradition.types import BirthInput
from src.engine.traditions.bazi_report import build_report as build_bazi
from src.engine.traditions.islamicate_report import (
    build_report as build_islamicate,
)
from src.engine.traditions.jaimini_report import (
    build_report as build_jaimini,
)
from src.engine.traditions.report import (
    Delineation,
    redact_refused_topics,
    render_markdown,
)
from src.engine.traditions.vedic_report import build_report as build_vedic

BIRTH = BirthInput(
    name="Fixture", civil_date=date(1996, 8, 13), civil_time="07:18",
    utc_offset_hours=-7.0, latitude=38.2494, longitude=-122.0400,
    place_label="Fairfield, California",
)

LIFESPAN_LEAK = re.compile(
    r"\b(short-?lived|long-?lived|span of life|long lease of life"
    r"|medium life|longevity)\b",
    re.IGNORECASE,
)


@pytest.fixture(scope="module")
def vedic():
    return build_vedic(BIRTH)


@pytest.fixture(scope="module")
def bazi():
    return build_bazi(BIRTH)


@pytest.fixture(scope="module")
def islamicate():
    return build_islamicate(BIRTH)


@pytest.fixture(scope="module")
def jaimini():
    return build_jaimini(BIRTH)



# --- clause-level policy -----------------------------------------------------


def test_redaction_removes_only_the_offending_clause():
    text, topics = redact_refused_topics(
        "long-lived; speaks sweetly and clearly; sharp-witted"
    )
    assert topics == ["longevity"]
    assert "long-lived" not in text
    assert "speaks sweetly and clearly" in text
    assert "withheld per publication policy" in text


def test_clean_text_is_untouched():
    original = "learned, witty in speech, happy and possessed of friends"
    text, topics = redact_refused_topics(original)
    assert text == original and topics == []


def test_delineation_cannot_carry_a_refused_clause_on_any_path():
    d = Delineation(
        text="short-lived; brave and wealthy", rule_id="x", source="s",
        evidence_grade="B", trigger="t",
    )
    assert "short-lived" not in d.text
    assert d.topics_redacted == ("longevity",)
    # the serialized form is the same object - no unredacted escape hatch
    assert "short-lived" not in str(d.to_dict())


@pytest.mark.parametrize("engine", ["vedic", "bazi"])
def test_no_lifespan_claim_reaches_a_rendered_report(engine, vedic, bazi):
    """Claims are what leak - quoted delineations and prose notes.

    Section headings name what a house is ABOUT (Bhava 8 is literally the
    longevity house), and suppression notices quote the policy that did the
    withholding; both legitimately contain topic words and are excluded.
    """
    report = vedic if engine == "vedic" else bazi
    for line in render_markdown(report).splitlines():
        stripped = line.strip()
        if (
            stripped.startswith("#")                      # headings: topic labels
            or stripped.startswith("**Not stated here.**")  # suppression notices
            or "withheld" in stripped                     # redaction markers
        ):
            continue
        m = LIFESPAN_LEAK.search(stripped)
        assert not m, f"lifespan claim leaked: {m.group(0)!r} in {stripped[:90]!r}"


def test_redactions_actually_occurred_in_the_vedic_report(vedic):
    """If the sources ever stop tripping the policy, this test forces a look:
    either the extraction changed or the lexicon silently broke."""
    redacted = [
        d for s in vedic.sections for d in s.delineations if d.topics_redacted
    ]
    assert redacted, "expected at least one policy redaction in this chart"


# --- deduplication -----------------------------------------------------------


def test_no_source_quotation_is_rendered_twice(vedic):
    quotes = [
        d.text for s in vedic.sections for d in s.delineations
        if len(d.text) > 30
    ]
    dupes = {q for q, n in Counter(quotes).items() if n > 1}
    assert not dupes, f"duplicated evidence: {sorted(dupes)[:2]}"


def test_bhava_sections_reference_rather_than_requote(vedic):
    for section in vedic.sections:
        if not section.title.startswith("Bhāva"):
            continue
        for d in section.delineations:
            # only the lord-in-bhava doctrine may quote here; occupant results
            # live in the graha sections
            assert "bhavesa_in_bhava" in d.rule_id, d.rule_id


# --- unknown never collapses into false --------------------------------------


@pytest.fixture(scope="module")
def qabisi_facts():
    panel = build_panel(BIRTH)
    section = next(
        s for s in panel["sections"]
        if s["tradition_id"] == "islamicate_al_qabisi"
    )
    return section["facts"]


def test_hyleg_settlement_is_tri_valued(qabisi_facts):
    settled = qabisi_facts["hyleg_settled"]
    assert settled["status"] in {"settled", "conditional"}
    ledger = qabisi_facts["hyleg_candidate_ledger"]
    uncomputed = [
        e["candidate"] for e in ledger if e.get("longitude") is None
    ]
    if uncomputed:
        # an uncomputed candidate earlier in the order forbids "settled"
        assert settled["status"] == "conditional"
        assert set(settled["conditional_on"]) == set(uncomputed)
        assert "unknown" in settled["chosen_because"].lower() or \
            "not computed" in settled["chosen_because"].lower()


def test_settle_hyleg_unit_unknown_vs_failed():
    from src.engine.multitradition.islamicate import settle_hyleg

    # earlier candidate uncomputed -> conditional even though a later one passes
    conditional = settle_hyleg([
        {"candidate": "Sun", "longitude": 10.0, "eligible": False},
        {"candidate": "Prenatal syzygy", "longitude": None},
        {"candidate": "Ascendant", "longitude": 150.0, "eligible": True,
         "lords_that_behold_it": {"Mercury": "conjunction"}},
    ])
    assert conditional["status"] == "conditional"
    assert conditional["conditional_on"] == ["Prenatal syzygy"]

    # every earlier candidate computed-and-failed -> genuinely settled
    settled = settle_hyleg([
        {"candidate": "Sun", "longitude": 10.0, "eligible": False},
        {"candidate": "Moon", "longitude": 40.0, "eligible": False},
        {"candidate": "Ascendant", "longitude": 150.0, "eligible": True,
         "lords_that_behold_it": {}},
    ])
    assert settled["status"] == "settled"
    assert "conditional_on" not in settled


# --- presentation ------------------------------------------------------------


def test_no_raw_json_in_rendered_prose(vedic, bazi):
    for report in (vedic, bazi):
        for section in report.sections:
            for note in section.notes:
                assert not re.search(r'\{"[a-z_]+":', note), (
                    f"raw JSON leaked into prose: {note[:80]}"
                )


def test_bazi_title_does_not_overclaim(bazi):
    assert "Full Reading" not in bazi.display_name


# --- synthesis layer (review finding 19 / P2) --------------------------------


def test_corroboration_requires_distinct_authors():
    """One author quoted twice is one witness, never two."""
    from src.engine.traditions.synthesis import synthesize

    same_author = [
        Delineation(text="wealthy and prosperous", rule_id="jyotisha.saravali.22.graha_in_rasi.sun",
                    source="s", evidence_grade="B", trigger="Sun in Cancer"),
        Delineation(text="endowed with riches", rule_id="jyotisha.saravali.30.graha_in_bhava.sun",
                    source="s", evidence_grade="B", trigger="Sun in the 12th bhāva"),
    ]
    section = synthesize(same_author, None)
    blob = " ".join(section.notes)
    assert "Corroborated" not in blob
    assert "Single-witness" in blob or "1 author" in blob


def test_contradiction_is_reported_not_averaged():
    from src.engine.traditions.synthesis import synthesize

    conflict = [
        Delineation(text="wealthy and prosperous", rule_id="jyotisha.saravali.22.graha_in_rasi.moon",
                    source="s", evidence_grade="B", trigger="Moon in Cancer"),
        Delineation(text="poor and devoid of wealth", rule_id="jyotisha.phaladeepika.08.planet_in_bhava.moon",
                    source="s", evidence_grade="B", trigger="Moon in the 12th bhāva"),
    ]
    section = synthesize(conflict, None)
    blob = " ".join(section.notes)
    assert "CONTRADICTION" in blob
    assert "No precedence rule in the corpus resolves this" in blob


def test_vedic_synthesis_applies_the_sources_own_gates(vedic):
    syn = next(s for s in vedic.sections if s.title == "Synthesis by Life Topic")
    blob = " ".join(syn.notes)
    # the gates are cited by sloka, which is what makes them sourced
    assert "23.86" in blob or "24.23" in blob or "30.86" in blob
    assert "invent" in blob or "unresolved" in blob or "own gates" in blob


# --- three-layer rendering (review finding 16 / P3) --------------------------


def test_layered_report_separates_reading_evidence_audit(vedic):
    from src.engine.traditions.report import render_layered

    md = render_layered(vedic)
    i_reading = md.index("## Part I — Reading")
    i_evidence = md.index("## Part II — Evidence")
    i_audit = md.index("## Part III — Audit")
    assert i_reading < i_evidence < i_audit
    # no quoted evidence before Part II, no refusal notices before Part III
    assert "> " not in md[:i_evidence]
    assert "withheld:" not in md[:i_audit].replace(
        "withheld per publication policy", ""
    )


# --- input forks (review finding 9 / P4) -------------------------------------


def test_sex_input_resolves_bazi_luck_direction():
    b = BirthInput(name="F", civil_date=date(1996, 8, 13), civil_time="07:18",
                   utc_offset_hours=-7.0, latitude=38.2494, longitude=-122.04,
                   place_label="F", sex="male")
    report = build_bazi(b)
    seqs = [s.title for s in report.sections if "sequence" in s.title]
    assert seqs == ["Forward sequence"]
    luck = next(s for s in report.sections if s.title.startswith("Luck"))
    assert not luck.refusals


def test_missing_sex_is_named_missing_input_not_doctrine(bazi):
    luck = next(s for s in bazi.sections if s.title.startswith("Luck"))
    assert any("MISSING INPUT" in r for r in luck.refusals)
    seqs = [s.title for s in bazi.sections if "sequence" in s.title]
    assert len(seqs) == 2


def test_hour_fork_difference_report_exists(bazi):
    fork = next(s for s in bazi.sections if "Hour Fork" in s.title)
    assert len(fork.table) == 2
    gods = {row["Hour stem Ten God"] for row in fork.table}
    assert len(gods) == 2, "the fork must show the interpretive difference"


def test_no_backspace_bytes_in_tradition_sources():
    r"""A patch pipeline turned regex \b into literal backspace bytes.

    Three times now. The pattern still compiles and simply matches nothing,
    so the failure is silent and looks like a passing feature. The guard
    covered src/engine only, and the third occurrence landed in a TEST file -
    where a dead guard is worse than none, because it reports success. Both
    trees are checked now.
    """
    import pathlib

    offenders = [
        str(p)
        for root in ("src/engine", "src/tests")
        for p in pathlib.Path(root).rglob("*.py")
        if b"\x08" in p.read_bytes()
    ]
    assert not offenders, offenders


def test_lilly_scorer_uses_ptolemaic_terms_not_egyptian():
    """CA p.104 prints Ptolemaic terms; awarding Lilly's +2 from Egyptian
    bounds was a tradition blend. Aries 12.5 deg is a discriminating case:
    Egyptian gives Mercury (Venus ends 12), Ptolemaic gives Venus (ends 14)."""
    from src.engine.multitradition.hellenistic import _bound_ruler, _terms_for
    from src.engine.reference_data import (
        EGYPTIAN_TERMS,
        PTOLEMAIC_TERMS_LILLY1647,
    )

    egyptian = _terms_for("Aries", EGYPTIAN_TERMS)
    ptolemaic = _terms_for("Aries", PTOLEMAIC_TERMS_LILLY1647)
    assert _bound_ruler("Aries", 12.5, {"Aries": egyptian}) == "Mercury"
    assert _bound_ruler("Aries", 12.5, {"Aries": ptolemaic}) == "Venus"
    # every row keyed from the photograph is monotone and closes at 30
    for sign, rows in PTOLEMAIC_TERMS_LILLY1647.items():
        ends = [end for _ruler, end in rows]
        assert ends == sorted(ends) and ends[-1] == 30, sign


def test_latin_section_scores_with_lillys_own_tables():
    panel = build_panel(BIRTH)
    latin = next(
        s for s in panel["sections"] if s["tradition_id"] == "latin_european"
    )
    blob = str(latin["facts"])
    assert "1647 p.104" in blob or "Lilly's table" in blob
    subjects = [d["subject"] for d in latin["disclosures"]]
    assert any("keyed from the 1647 photographs" in s for s in subjects)


# --- hellenistic report engine (P5) ------------------------------------------


@pytest.fixture(scope="module")
def hellenistic():
    from src.engine.traditions.hellenistic_report import build_report

    return build_report(BIRTH)


def test_hellenistic_fires_doctrine_only_on_real_conditions(hellenistic):
    """Every fired rule's trigger must be a computed chart fact."""
    fired = {
        d.rule_id: d.trigger
        for s in hellenistic.sections for d in s.delineations
    }
    # Mercury is domicile AND exalted in Virgo - both must fire on it
    assert any("Mercury" in t and "domicile" in t for t in fired.values())
    assert any("Mercury" in t and "exaltation" in t for t in fired.values())
    # the diurnal trio fires because this IS a day chart
    assert "hel.firmicus.sect_diurnal_trio_and_lacuna" in fired
    # the fire-trigon rule fires because the sect light stands in Leo
    assert "hel.ptolemy.triplicity_fire_sun_jupiter_mars_participant" in fired
    # nothing fired the nocturnal-only rule on a day chart
    assert "hel.firmicus.jupiter_no_joy_at_night" not in fired


def test_hellenistic_lists_undecided_rules_openly(hellenistic):
    undecided = next(
        s for s in hellenistic.sections if "could not be decided" in s.title
    )
    blob = " ".join(undecided.notes)
    assert "doryphoria" in blob
    assert "hel.ptolemy.parents_same_sect_doryphoria_brilliance" in blob


def test_mathesis_sect_split_cells_select_by_chart_sect(hellenistic):
    """Saturn-in-8th differentiates by sect; a day chart must quote the
    by-day sub-cell, and a cell stated only for the other sect must be
    NOTED as sect-conditional rather than silently skipped."""
    fired = {
        d.rule_id: d.trigger
        for s in hellenistic.sections for d in s.delineations
    }
    saturn = [t for r, t in fired.items()
              if r == "hel.mathesis.b3.planet_in_house.saturn"]
    assert saturn and "by day" in saturn[0]
    all_refusals = " ".join(
        r for s in hellenistic.sections for r in s.refusals
    )
    assert "only for nocturnal nativities" in all_refusals
    assert "withheld" in all_refusals  # Sun-12's demeaning-status cell


# --- the Islamicate report ---------------------------------------------------


def test_the_islamicate_report_actually_says_something(islamicate):
    """Eighty-six mined rules had no engine at all until this report existed."""
    assert islamicate.delineation_count >= 20
    assert islamicate.word_count >= 1500
    titles = [s.title for s in islamicate.sections]
    for wanted in ("The Dignities, and Who Prevails", "The Lots",
                   "The Hyleg and the Kadkhudah"):
        assert wanted in titles


def test_the_kadkhudah_years_are_refused_wherever_the_hyleg_is_reported(
    islamicate,
):
    """Structure may be shown. A lifespan may not, and the pack agrees."""
    hyleg = next(
        s for s in islamicate.sections if s.title.startswith("The Hyleg")
    )
    assert any("YEARS are not given" in r for r in hyleg.refusals)
    blob = " ".join(hyleg.notes) + " ".join(
        d.text for d in hyleg.delineations
    )
    assert not LIFESPAN_LEAK.search(blob), (
        "a lifespan phrase reached the hyleg section"
    )


def test_a_conditional_hyleg_says_what_it_is_conditional_on(islamicate):
    """The uncomputed prenatal syzygy must not read as a failed candidate."""
    hyleg = next(
        s for s in islamicate.sections if s.title.startswith("The Hyleg")
    )
    blob = " ".join(hyleg.notes)
    if "conditional" in blob:
        assert "syzygy" in blob.lower()
        assert "not a failed one" in blob


def test_the_limits_section_does_not_disclaim_what_the_report_delivered(
    islamicate,
):
    """al-Biruni's gated list names layers al-Qabisi's pack actually supplies."""
    limits = next(
        s for s in islamicate.sections if "Does Not Claim" in s.title
    )
    blob = " ".join(limits.notes).lower()
    lots = next(s for s in islamicate.sections if s.title == "The Lots")
    if lots.notes:
        assert "al-qabisi introduction doctrine" not in blob


def test_every_islamicate_delineation_carries_a_source_and_a_rule_id(
    islamicate,
):
    for section in islamicate.sections:
        for d in section.delineations:
            assert d.rule_id and d.source, d.text[:60]


# --- Valens now fires --------------------------------------------------------


def test_valens_reaches_the_hellenistic_page(hellenistic):
    """The module's docstring once said Valens contributes nothing."""
    fired = [
        d
        for s in hellenistic.sections
        for d in s.delineations
        if "valens" in d.rule_id
    ]
    assert len(fired) >= 5, "the Valens pack loads but barely fires"


def test_a_topic_chapter_reports_its_undecided_conditions(hellenistic):
    """Valens gates travel on chronocrators this engine does not compute."""
    travel = next(
        (s for s in hellenistic.sections
         if s.title.startswith("Foreign Travel")),
        None,
    )
    if travel is None:
        pytest.skip("no travel chapter is loaded in this pack")
    blob = " ".join(travel.notes)
    assert "cannot be decided" in blob
    assert "distribution" in blob


# --- Jaimini -----------------------------------------------------------------


def test_the_jaimini_report_reads_from_the_karaka_kundali(jaimini):
    """Abhyankar's frame in all fourteen worked charts, not the birth lagna."""
    opening = jaimini.sections[0]
    blob = " ".join(opening.notes)
    assert "karaka-kundali" in blob
    assert "Atmakaraka" in blob


def test_jaimini_refuses_the_karaka_scheme_by_default(jaimini):
    """saptanam astanam va - the sutra leaves it open, so the engine does."""
    karakas = next(
        s for s in jaimini.sections if s.title == "The Chara Karakas"
    )
    assert any("rank one" in r for r in karakas.refusals)
    titled = [n for n in karakas.notes if "Rank " in n]
    assert titled, "no karakas were listed at all"
    assert sum(1 for n in titled if "Atmakaraka" in n) == 1
    assert all(
        "untitled" in n for n in titled if "Rank 1:" not in n
    ), "a karaka below rank one was titled without a declared scheme"


def test_declaring_the_scheme_titles_every_rank():
    declared = build_jaimini(BIRTH, karaka_scheme="eight")
    karakas = next(
        s for s in declared.sections if s.title == "The Chara Karakas"
    )
    titled = [n for n in karakas.notes if "Rank " in n]
    assert titled
    assert not any("untitled" in n for n in titled)
    assert not any("rank one" in r for r in karakas.refusals)


def test_jaimini_refuses_chara_dasa_lengths_but_gives_the_sequence(jaimini):
    dasa = next(s for s in jaimini.sections if s.title == "Chara Dasa")
    assert any("No period LENGTHS" in r for r in dasa.refusals)
    assert any("→" in n for n in dasa.notes), "the sequence should still show"


def test_the_varnada_is_shown_but_refused_for_reading(jaimini):
    lagnas = next(
        s for s in jaimini.sections if s.title == "The Special Lagnas"
    )
    blob = " ".join(lagnas.notes)
    if "Varnada falls" in blob:
        assert any("is NOT read" in r for r in lagnas.refusals)


def test_jaimini_computes_the_special_lagnas_rather_than_refusing(jaimini):
    """They need only sunrise, which this package already computes."""
    lagnas = next(
        s for s in jaimini.sections if s.title == "The Special Lagnas"
    )
    blob = " ".join(lagnas.notes)
    assert "Hora Lagna" in blob
    assert "Ghatika Lagna" in blob


def test_jaimini_says_it_is_not_merged_with_the_parasari_reading(jaimini):
    limits = next(s for s in jaimini.sections if "Does Not Claim" in s.title)
    blob = " ".join(limits.notes) + " ".join(
        d.text for d in limits.delineations
    )
    assert "Parasari" in blob or "Parāśari" in blob


BAD_ORDINAL = re.compile(r"(?<!\d)[123]th\b")


def test_jaimini_house_ordinals_are_well_formed(jaimini):
    """A formatting slip once printed 'the 2th' and 'the 3th'.

    The pattern must not fire on 11th, 12th or 13th, which are correct and
    end in the same two letters.
    """
    assert BAD_ORDINAL.search("the 2th") and not BAD_ORDINAL.search("the 12th")
    for section in jaimini.sections:
        for note in section.notes:
            assert not BAD_ORDINAL.search(note), note[:80]


def test_no_report_repeats_a_word_from_a_glued_note(jaimini):
    """'untitled, because untitled:' shipped once; guard the seam."""
    for section in jaimini.sections:
        for note in section.notes:
            assert "untitled, because untitled" not in note
