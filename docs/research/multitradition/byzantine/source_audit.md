# Byzantine Greek astrological source audit

Status: first pass; two Rhetorius recensions retrieved and collated against page images; not production approval
Updated: 2026-08-02

## Result of this pass

Byzantine astrology can be built, and it must not be built as "late Hellenistic
with a different label." The retrieval settled that question with evidence rather
than argument.

Three things are now demonstrated from the text itself:

1. **The Byzantine layer reorganised what it inherited.** Rhetorius' chapter 54
   (*Ἐπίσκεψις πινακική*) is not a doctrine chapter — it is an **ordered
   seven-step inspection protocol** that tells the practitioner what to look at,
   in what order, and closes with an explicit warranty: *"when all these seven
   inspections have been examined in this way you will not err concerning the
   foundations of the nativity"* (CCAG VIII.4 p. 124, 17-18). Hellenistic authors
   supply the ingredients; this supplies the procedure. A judgment hierarchy
   stated by the source, not reconstructed by us, is exactly what the
   defensibility standard's requirement 2 asks for and almost never gets.
2. **The Byzantine layer criticised what it inherited.** The syntagma of cod.
   Parisinus gr. 2506 (CCAG VIII.3 pp. 93-125) is a *bibliography with verdicts*:
   the compiler summarises Critodemus, Callicrates, Balbillus, Antiochus and
   Rhetorius chapter by chapter, dates them, declares Ptolemy's *Tetrabiblos*
   "law and canon for all who came after him" (p. 93, 11), and says of the
   Hystaspes/Odapsos book that its author *"promises the same things as the
   others, but I have not yet tested it by experience"* (p. 92). That evaluative
   stance is a Byzantine artefact and it has doctrinal consequences — see the
   Antiochus dating error below.
3. **The Arabic absorption is real but it is a *later and separate* layer.** It
   is not in Rhetorius, who wrote under Anastasius in the early sixth century.
   It is in cod. Angelicus 29 (CCAG V.1), which Cumont and Boll describe as the
   only witness preserving the works of **Palchus and of "Apomasar"** — Abu
   Ma'shar in Greek — alongside a letter of the emperor **Manuel I Komnenos**,
   Theophilus of Edessa material, chapters on the *ἀλλαγὴ ἔτους* (annual
   revolution) and one headed *"That the dominion of the Arabs is waning."*
   Merging that material into a Rhetorius pack would be a six-hundred-year
   anachronism.

The production unit must therefore be **recension + edition + witness family**,
never "Byzantine astrology." This pack ships three separately scoped rule
schools and forbids inheritance between them.

## What survives, and in what shape

Rhetorius' *Compendium* does **not** survive as one intact work. Cumont's own
praefatio (CCAG VIII.4 pp. 115-117) states the position plainly:

- cod. **Parisinus gr. 2425** is the only described codex that gives Rhetorius'
  work as the Byzantine excerptor still read it — **except the final chapter**,
  which explained *"the nativities of emperors"* and **which the scribe was
  afraid to copy** (*librarius describere veritus est*). A politically motivated
  lacuna, not a physical one.
- even in 2425 the work is already *mancum et saucium* — maimed and wounded —
  and chapters missing there survive elsewhere (Paris. gr. 2506, Marcianus 335).
- the scribe of 2425 kept the orthography *pessime* and **suppressed the names
  of the authorities Rhetorius cited**, substituting "a certain one of the wise"
  for Anubion and deleting mentions of Valens.
- the ninth-century Byzantine epitomator (working shortly after AD 884)
  therefore sometimes preserves the text **more fully or more correctly** than
  the sole complete manuscript. Cumont edited from both.

That is the whole recension problem in four sentences, and it is why the rule
manifest carries a `school_id` per recension.

## Source map

| Author/work | Branch | Edition retrieved | Current evidentiary value | Main limitation |
|---|---|---|---|---|
| Rhetorius, *Compendium*, **recension P** | natal procedure, birth, places | CCAG VIII.4 pp. 115-174, ed. Cumont/Boudreaux 1921 | strongest: OCR retrieved and **five printed pages collated against rendered page images**; 17 rules encoded | sole manuscript is careless and suppresses source attributions; final chapter deliberately omitted; Second Inspection entirely lost |
| Rhetorius, *Compendium*, **recension L** | definitions, sect, signs | CCAG I pp. 140-164, ed. Boll 1898 | strong: two pages collated against images; 5 rules encoded | titled *from the treasuries of Antiochus*; one witness attributes the same chapter to Antiochus outright; overlaps Porphyry so far that Boll declined to decide whose words are whose |
| Byzantine syntagma of Paris. gr. 2506 | source criticism, definitions | CCAG VIII.3 pp. 93-125, ed. Boudreaux 1912 | strong: two pages collated; 5 rules encoded | it is a *summary*, so its wording is the epitomator's, not the author's |
| Palchus; "Apomasar"; Manuel Komnenos letter; Theophilus | questions, elections, revolutions, mundane | CCAG V.1 (Cumont/Boll 1904) OCR retrieved, catalogue headings inspected | identified and hash-pinned; **no rule extracted** | the volume prints catalogue *incipits* for most items; the texts themselves are in appendices and other volumes |
| John Lydus, *De ostentis* | portents, omens, comets, earthquakes | Wachsmuth 1897 Teubner, OCR retrieved and hash-pinned | **none** | the Archive.org OCR mapped the Latin praefatio into Greek glyphs; the Greek body is corrupt. Access-class blocker, not a rights or language blocker |
| Rhetorius, ed. Pingree/Heilen 2009 | all | not retrieved | none | in copyright; deliberately not used |

## Recension problems that must never be merged

**1. The title itself disagrees about the author.**
Recension L's oldest witness, cod. Laur. XXVIII 34, is headed *ἐκ τῶν Ἀντιόχου
θησαυρῶν ἐπίλυσις καὶ διήγησις πάσης ἀστρονομικῆς τέχνης* — "from the treasuries
of **Antiochus**." Four other witnesses (Laur. XXVIII 7, Monac. 170, Monac. 105,
Vatic. 1444) head the same material *Ῥητορίου ἔκθεσις καὶ ἐπίλυσις …* — "the
exposition of **Rhetorius**." Boll prints both. A rule cited as "Rhetorius says"
without its witness family is unfalsifiable.

**2. One chapter is attributed to a third author in a sixth witness.**
Boll's note to CCAG I p. 146 records that the sect chapter also stands in cod.
Neapolitanus II C 33 f. 521v under the heading *περὶ αἱρέσεων τῶν ἄστρων
Ἀντιόχου*. The rule manifest records the divergence on the rule itself.

**3. A chapter title names its source in one recension and hides it in the other.**
Chapter 55 is headed *Περὶ τοκετοῦ* ("On childbirth") in Paris. gr. 2425 but
*Περὶ εὐτοκίας καὶ δυστοκίας καθὼς Δωρόθεος* ("… **according to Dorotheus**") in
Vaticanus 1056. Cumont concludes the genuine title named Dorotheus and the Paris
scribe cut him. This is the attribution-suppression habit of that scribe caught
in the act, and it is why "Rhetorius says X" is frequently "Dorotheus says X."

**4. The Byzantine epitomator got a date badly wrong, and said so in writing.**
CCAG VIII.3 p. 111, 2-3: *Οὗτος ὁ Ἀντίοχος μεταγενέστερός ἐστιν καὶ Παύλου τοῦ
Ἀλεξανδρέως καὶ Οὐάλεντος* — "this Antiochus is later than both Paul of
Alexandria and Valens." Boll's footnote refutes it: Antiochus is cited by
Porphyry and so is pre-third-century; the epitomator **never read Antiochus'
own Thesauri, only Rhetorius' sixth-century paraphrase of them**, in which
Valens and Paul had already been interpolated. The Byzantine tradition's own
attributions are therefore evidence about *Byzantine reading habits*, not about
authorship. The pack encodes that as a rule with a `provenance_warning`
conclusion rather than silently repeating the epitomator.

**5. Boll refused to separate Rhetorius from Porphyry, and so do we.**
CCAG I p. 142: *"Vix enim donec integrum habeas Porphyrium, enucleare possis,
quae sint verba Porphyrii, quae Rhetorii"* — until you have a complete Porphyry
you can hardly work out which words are Porphyry's and which Rhetorius'. Every
L-recension rule carries that boundary.

**6. A lacuna large enough to be a technique.**
Cumont's note on CCAG VIII.4 p. 119, 16: *Δευτέρα σκέψις tota periit* — **the
Second Inspection is entirely lost**, and the Third survives only as its tail.
Seven inspections are promised; five and two fragments are extant. Any product
that prints "Rhetorius' seven-step method" as if all seven were recoverable is
misrepresenting the corpus. This pack ships the order with the holes visible.

## Rights status

Everything used here is public domain. CCAG I (1898), V.1 (1904), VIII.1 (1929),
VIII.3 (1912) and VIII.4 (1921) are pre-1929 publications; their editors Boll
(d. 1924) and Cumont (d. 1947) are long past EU life+70. Two of the Archive.org
items carry an explicit CC Public Domain Mark 1.0. Wachsmuth's Lydus is 1897.

Consequently the correct action under the standard's translation table is
**translate directly and show the Greek**: original + rendering + citation, graded
`engine_translation_unreviewed`. No modern copyrighted translation was consulted
for any encoded passage, and the Pingree/Heilen critical edition was deliberately
not retrieved.

## What blocks what

| Blocked item | Blocker class | What would unblock it |
|---|---|---|
| The Second Inspection of the pinax protocol | **the original is lost** — not access, not rights | nothing available; it is gone from every described witness |
| The final chapter on imperial nativities | scribal refusal in the only complete codex | a witness outside the described set; Pingree/Heilen would at least record whether one exists |
| Semantics of the ordinal sets in chapter 56 (*poleuon*) | the surviving chapter never defines them | the fuller text in Venetus 7 f. 393, which Cumont could not inspect "because of the war" |
| Chapter 55's Vaticanus 1056 collation | access | CCAG V.3 pp. 79-80, retrievable, not yet fetched |
| John Lydus, *De ostentis* portent branch | **access** (OCR unusable) | page images from the Wachsmuth scan |
| Palchus, Apomasar, Manuel Komnenos, Theophilus | access to the appendix texts, not the catalogue | CCAG V.1 appendices, CCAG VIII.1, and the Cumont/Boll editions of the Angelicus material |
| Any Rhetorius chapter numbering that matches modern scholarship | rights | the 2009 Pingree/Heilen edition |
| Promotion of any rule from research to reading | specialist review | an independent Byzantine-Greek reader and a second passage-to-predicate encoder |

## Distinctively Byzantine versus inherited

This is the justification for a separate track, so it is stated as a ledger.

**Inherited, and openly so.** The doctrine content is late Hellenistic: sect,
triplicity lords, terms, lots of Fortune and Daimon, dodekatemoria,
doryphories, prenatal syzygy, decans and paranatellonta. Rhetorius names his
sources — Ptolemy quoted at length, Valens by chapter, Paul of Alexandria,
Julian of Laodicea, Dorotheus, Anubion, Teucer, Critodemus, Hermes — and Cumont
traces the fixed-star clause on CCAG VIII.4 p. 124 to the **Anonymous of AD
379**. The pack labels each such rule with its stated upstream author.

**Distinctively Byzantine, and this is the whole case:**

- **A named, ordered, closed inspection protocol** (`ἐπίσκεψις πινακική`,
  seven `σκέψεις`) with a stated completeness claim. Hellenistic authors give
  topics; this gives sequence.
- **Compilation over a physical instrument.** The protocol is organised around
  the *πίναξ*, the astrologer's hinged board; a scholion in Paris. gr. 2419
  describes it as a *δίπτυχον δελτάριον* on which the zodiac was drawn and the
  positions laid out. The method is board-shaped, not book-shaped.
- **Multi-origin annual distribution.** CCAG VIII.4 p. 122: distribute the years
  "not only from the Ascendant, but also from the Sun and the Moon and the Lot
  of Fortune", and, if the parents are alive, from the lots of father and mother
  as well, "and so examine the parents' year." A single-Ascendant profection is
  explicitly rejected.
- **Evaluative bibliography** — the synkephalaiosis genre, with dating verdicts
  and an appeal to *πεῖρα*, experience, as the test of a book's promises.
- **Canonisation of Ptolemy** as *νόμος καὶ κανών*, with the frank admission that
  a recapitulation of him is being supplied only so as not to seem to omit the
  foundation.
- **A place-list that starts at the twelfth.** Chapter 57's exposition of the
  *δωδεκάτοπος* opens with *Τόπος δωδέκατος* and works backward, naming it
  *κακοδαιμόνημα*, *προαναφορὰ τοῦ ὡροσκόπου* and *μετακόσμιος* — "beyond the
  world."
- **Later still: the Arabic and Persian absorption** in the Angelicus/Palchus
  layer, carrying its own vocabulary (*ἀλλαγὴ ἔτους*) and its own politics.

**Consequence for the reading:** a Byzantine section is defensible when it runs
the seven-inspection order, shows where the order is broken by loss, labels each
doctrine with the upstream author Rhetorius himself names, and keeps the
sixth-century and twelfth-century layers apart. It is indefensible if it prints
Hellenistic delineations under a Byzantine banner.

## Validation gates for this track

1. Every encoded passage must be collated against a page image before its rule
   leaves `evidence_grade` C. Nine pages are collated today.
2. No rule may cross `school_id` boundaries. Recension P, recension L and the
   epitome are separate; a value found in one is never backfilled into another.
3. Where Rhetorius names an upstream author, the rule stores that name; where a
   modern editor supplies the attribution, the rule stores the editor instead.
4. Editorial supplements (Kroll's `κείμενοι`, Cumont's angle-bracket insertions)
   must be marked as such in the rule, because they are conjecture.
5. Nothing from this pack is customer-eligible until an independent
   Byzantine-Greek reader and a second passage-to-predicate encoder have signed
   off. `publication_status` is `research_only` and stays there.
