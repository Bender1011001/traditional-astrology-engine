# Byzantine Greek defensibility spec

Status: governing spec for the Byzantine (Rhetorius) section
Updated: 2026-08-02
Standard: [../DEFENSIBILITY.md](../DEFENSIBILITY.md)

The adversary is a historian of Byzantine science or a specialist in the CCAG
corpus. That adversary's first move is not "is your delineation right" — it is
**"which recension are you quoting, and does that witness actually say it."**
This spec is built so that question always has an answer.

The section's whole claim to exist separately from a Hellenistic section rests
on one fact: Rhetorius chapter 54 supplies a **named, ordered, closed inspection
protocol** with the text's own completeness claim attached to it. Hellenistic
authors supply doctrine; this supplies procedure. Where the procedure is broken
by loss, the section shows the break rather than filling it.

## Core-technique checklist

| # | Technique | Source basis | Status |
|---|---|---|---|
| 1 | The seven-inspection order (*episkepsis pinakike*) as the judgment hierarchy | cap. 54, CCAG VIII.4 pp. 118-124, page-image collated | `implemented` in corpus — order encoded with both lost slots visible |
| 2 | Sect: leaders by day and night, Mercury shared | rec. L cap. 2, CCAG I p. 146, collated | `implemented` in corpus |
| 3 | Benefic/malefic as *reputed* rather than fixed classes | rec. L cap. 2, CCAG I p. 146, collated | `implemented` in corpus — the tradition's own qualifier, with Kroll's supplement disclosed |
| 4 | Triplicity lords: of the sect light, of the Ascendant, of the lower midheaven | cap. 54, pp. 118-119, collated | `implemented` in corpus |
| 5 | Lots of Fortune, Daimon, Basis, and the exaltation of the nativity | cap. 54 fifth inspection, pp. 121-122, collated | `implemented` in corpus |
| 6 | Lot construction from stated formulae (Lot of the anairetes; the *aitiatikos* lot) | cap. 54, pp. 123-124, collated | `implemented` in corpus — formulae computable, arithmetic checked in vectors |
| 7 | Ages of life split between lots and their lords | cap. 54, p. 122, collated | `implemented` in corpus |
| 8 | Prenatal syzygy and the planets rising before and after the lights | cap. 54 fourth inspection, p. 120, collated | `implemented` in corpus |
| 9 | The four angles judged by elemental blend | rec. L cap. 3, CCAG I pp. 146-147, collated | `implemented` in corpus — with the chapter's own worked example |
| 10 | Twelve places: Byzantine nomenclature and significations, expounded from the twelfth | cap. 57, twelve headings across pp. 126-170 | `implemented` in corpus — names and significations only |
| 11 | Void course (*kenodromia*) and bond (*syndesmos*) of the Moon | Byzantine epitome, CCAG VIII.3 p. 110, collated | `implemented` in corpus — the 30-degree bound is explicit |
| 12 | Provenance control: a Byzantine attribution is not authorship | epitome verdict on Antiochus + Boll's refutation, CCAG VIII.3 p. 111, collated | `implemented` in corpus as a governance rule |
| 13 | The Second Inspection of the protocol | it is gone from every described witness | `refused` — the original is lost, not gated |
| 14 | The final chapter on imperial nativities | the scribe of the only complete codex refused to copy it | `refused` — the surviving corpus cannot supply it |
| 15 | Planet-in-place delineation tables of cap. 57 | Cumont records that ninth-place material stands in the fourth and is repeated in the ninth, and that fourth-place Mercury/Moon material belongs to the eleventh | `source_gated` — the printed place assignments are known corrupt; needs an apparatus that resolves them |
| 16 | Annual distribution of the years from multiple origins | cap. 54 p. 122 names the origins (Ascendant, Sun, Moon, Lot of Fortune, lots of the parents) but never a step length | `source_gated` — the origins are encoded; the step length exists in no retrieved chapter |
| 17 | The *poleuon* and *diepon* of the Ascendant (cap. 56) | the chapter gives ordinal sets and delineations but never defines what the ordinals enumerate | `source_gated` — unblocked by cod. Venetus 7 f. 393, which Cumont could not inspect |
| 18 | Decans, *paranatellonta*, the *dodekaoros*, bright and shadowy degrees | cap. 54 instructs the reader to consult them; the tables are in CCAG VII and elsewhere | `source_gated` — tables not retrieved |
| 19 | Fixed stars on angular degrees, with the *anemos* condition | cap. 54 p. 124; Cumont traces it to the Anonymous of AD 379 | `source_gated` for the *anemos* predicate, which the chapter never defines |
| 20 | Portents, comets, earthquakes (John Lydus, *De ostentis*) | Wachsmuth 1897 retrieved; its OCR maps Latin into Greek glyphs and corrupts the Greek | `source_gated` — access-quality blocker, resolvable by page images |
| 21 | The Arabic and Persian absorption layer (Palchus, "Apomasar", Theophilus, Manuel Komnenos) | CCAG V.1 catalogue headings inspected; the texts are in appendices not retrieved | `source_gated` — and it must never be merged into the Rhetorius schools |
| 22 | A worked classical chart judged by Rhetorius himself | none found in the retrieved chapters | `source_gated` — see the worked-example inventory below |
| 23 | Longevity, death timing, violent-death judgment | cap. 54 supplies the machinery (anairetes lot, *biothanasia* signs) | `refused` — the lot may be computed and shown; the death reading is not produced |
| 24 | Obstetric, medical, ocular and skin claims | cap. 55; rec. L caps. 4 and 6 | `refused` — quoted as historical statements only |
| 25 | Claims about parents' ethnicity, birth status or social rank | cap. 54 pp. 120, 122 | `refused` — the passages are preserved verbatim and never rendered as claims |

Nothing on this checklist is `computable`. Items 15-22 are blocked on a named
document or a named access problem; items 13, 14, 23, 24 and 25 are facts about
the corpus or standing product refusals.

## Judgment hierarchy

The source states its own order, so this section does not have to invent one.
The composer executes exactly this, and prints the gaps:

1. **First inspection.** Before anything else, the ease or difficulty of the
   birth. Then the *doryphoriai* of the lights — attended by their own sect or
   by the contrary sect. Then the lights' gender placement, by sign and by
   quadrant of the board. Then whether the lights are bound or unbound to each
   other and to the Ascendant. Then the triplicity lords of the sect light and
   of the Ascendant, their house rulers, the bound rulers of Sun and Moon, the
   *dodekatemoria*, and the Lots of Fortune and Daimon with their lord. It
   closes on the triplicity lords of the lower midheaven, the first for the
   quality of the death, the second for the injury.
2. **Second inspection.** *Lost entirely.* The section prints this slot as a
   hole, because it is one.
3. **Third inspection.** On the angles; survives only as the end of its argument.
4. **Fourth inspection.** The conjunctions and full moons: where they fell and
   what they apply to; which planets rise before and after the lights.
5. **Fifth inspection.** The Lots of Fortune, Daimon, Basis and the exaltation of
   the nativity, with their phases and positions; then the lots' topical
   division, the ages, and the multi-origin distribution of the years.
6. **Sixth inspection.** The Nodes, by place and decan and by who beholds them.
   The sentence breaks off mid-clause.
7. **Seventh inspection.** The *dodekatemoria*, above all of Sun, Moon and
   Ascendant.

Then, and only then, the chapter's warranty may be quoted:
*"when all these seven inspections are examined in this way you will not go
wrong about the foundations of the nativity."* It is quoted with the two missing
slots named in the same breath. Quoting it without them would be the single most
misleading thing this section could do.

Two ordering rules sit above the seven:

- **Recension before doctrine.** No statement is made without its witness family.
- **Named upstream author before Byzantine attribution.** Where Rhetorius names
  Ptolemy, Valens, Dorotheus, Paul, Julian of Laodicea or the Anonymous of 379,
  that name is printed. Where a Byzantine compiler supplies an attribution, it is
  labelled as a Byzantine reading habit, not as authorship (checklist item 12).

## Worked-example inventory

| Source | Contains | Usable now |
|---|---|---|
| Rhetorius cap. 54-57, CCAG VIII.4 pp. 118-174 | procedure and delineation; **no worked chart** in the seven collated pages | no |
| Rhetorius' final chapter, "the nativities of emperors" | by its title, the one place worked imperial charts would have stood | **no — the scribe of Paris. gr. 2425 refused to copy it** |
| Byzantine syntagma, CCAG VIII.3 p. 111 | the Antiochus epitome ends by noting the author worked a grammarian's nativity as a specimen and then a second, royal nativity | not printed there; only the summary of it survives |
| Palchus corpus, cod. Angelicus 29 (CCAG V.1) | Palchus is known for dated horoscopes | **not retrieved**; the strongest available lead for a datable Byzantine worked chart |
| Pingree/Heilen 2009 | would state whether any witness preserves a worked chart | in copyright, not retrieved |

**Result: zero worked examples are reproducible today.** This is the honest
weakest point of the track and it is stated first, not buried. The nearest thing
to a proof the section currently offers is different in kind and worth naming:
nine printed pages were rendered from the scans and read as images, and the
encoding corrected the OCR in places where the OCR was wrong — including one
substantive verb (*megalynousi*, "magnify", where the OCR gave a non-word) on
which a whole rule turns. That is reproducible by anyone with the same hashes.

The route to a real worked example runs through Palchus, not through Rhetorius.

## Refusal list

- **No completed protocol.** The Second Inspection is lost and the Third is a
  fragment. The section will not reconstruct them from Valens, Firmicus or Paul,
  and will not present five-and-a-half inspections as seven.
- **No death, longevity or violent-death judgment.** The Lot of the *anairetes*
  and the *aitiatikos* lot may be computed and displayed with their formulae;
  the *biothanasia* readings attached to them are not produced.
- **No medical, obstetric or ocular claim.** Chapter 55 on easy and difficult
  birth, recension L's chapters on skin afflictions and on the signs held to
  injure the eyes, and the *epileptic and god-possessed* clause of chapter 56 are
  quoted as historical statements with their citations and never applied to a
  person.
- **No claim about a person's parentage, ethnicity, birth status or rank.**
  "Say the parents are of another stock or another nation, or base-born, or
  lowly" is preserved verbatim in the pack because deleting it would falsify the
  corpus, and is never rendered.
- **No non-human-birth judgment.** The configuration that makes the native "not a
  human being but a portent or a quadruped" is retained only as evidence that
  this protocol judges a figure, and as the anchor of a recension divergence.
- **No merging of recensions.** A value in Paris. gr. 2425 is never backfilled
  into Laur. XXVIII 34 or into the epitome, and vice versa. Where the witnesses
  disagree — the title of chapter 55, the reading of the portent clause, the
  attribution of the sect chapter — both are printed.
- **No re-attribution to Antiochus, Porphyry or Hermes** on the strength of a
  Byzantine heading. The epitomator demonstrably misdated Antiochus because he
  was reading Rhetorius' paraphrase; that is recorded as a rule.
- **No Arabic-era material inside a sixth-century pack.** Palchus, "Apomasar",
  Theophilus and the Komnenian material belong to a separate school and a
  separate date, and will be labelled as such when they are encoded.
- **No use of the Pingree/Heilen edition.** It is in copyright and was
  deliberately not retrieved; every rule rests on public-domain CCAG text.

## Conventions requiring disclosure

| Convention | Chosen | Note |
|---|---|---|
| Controlling editions | CCAG I (1898), VIII.3 (1912), VIII.4 (1921) | public domain; chapter identifiers are CCAG's, not the modern edition's, and the two numberings must be concorded rather than conflated |
| Translation | engine's own, from the Greek | graded `engine_translation_unreviewed`; Greek is shown beside every rendering so a specialist can check it |
| Text of record | the rendered page image, not the OCR | the OCR misreads at least one rule-bearing verb and all the Greek numerals in chapter 56; nine pages are collated and the rest of the pack is graded B accordingly |
| Editorial supplements | disclosed per rule | Kroll's `keimenoi` in the sect chapter and Cumont's angle-bracket insertions are conjecture and are marked as such |
| Places | counted from the Ascendant, in whole signs, as the chapters themselves count ("the ninth place from the Ascendant", "the twelfth from the Lot of Fortune") | derived places from a lot are used exactly as chapter 54 uses them |
| Zodiac frame | not stated by the source | Rhetorius' own star longitudes are what date him to the early sixth century; any modern recomputation is a reconstruction and must be labelled one |
| Sect reversal of the lots | as chapter 54 states it, crediting Ptolemy by name inside the text | the reversal is inherited doctrine that the source itself attributes |
| Chapter 56's ordinal sets | left uninterpreted | reading them as hours or as places would be a guess; the pack returns nothing |

## Current implementation gap

There is no Byzantine reading section and no Byzantine code. This pass built the
source foundation: 31 rules and 44 vectors across three separately scoped
recension schools, resting on six hash-pinned public-domain artifacts and nine
page images that were read rather than OCR-trusted.

What that buys, concretely: the judgment hierarchy is not a reconstruction, it is
a quotation; the sect and benefic/malefic rules come with the tradition's own
qualifier that those categories are only *reputed*; two lots have complete
formulae whose arithmetic is checked in vectors; the void-course definition has
an explicit numeric bound; and the twelve places carry their Byzantine names.

What it does not buy: any worked chart, any Byzantine chart computation, and any
delineation table — the last deliberately, because the printed place assignments
are known to be corrupt.

The next three moves, in order of value:

1. **Palchus.** He is the only realistic route to a datable Byzantine worked
   chart, and his corpus also carries the Arabic-absorption layer. Retrieving the
   CCAG V.1 appendices is one download away.
2. **Page images for CCAG VIII.4 pp. 126-174 and CCAG VIII.3 pp. 92-109.** This
   converts the grade-B rules to grade A and makes the chapter-57 concordance
   against the Byzantine chapter list usable.
3. **Independent Byzantine-Greek review** of the 31 encoded passages, plus a
   second passage-to-predicate encoder. Until both exist, `publication_status`
   stays `research_only` and nothing here reaches a customer.
