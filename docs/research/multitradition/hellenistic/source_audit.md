# Hellenistic delineation pack - source audit

Status: covers the delineation layer only (sect and dignity meaning), built on top of
the already-live calculation engine at `src/engine/multitradition/hellenistic.py`
Updated: 2026-08-02

This audit covers the four fetched primary/aid sources and states, for each, what
was actually opened and read, what survives in the fetched copy, and its rights
status - verified rather than assumed, per this corpus's standing instruction.

## 1. Firmicus Maternus, *Mathesis* - Kroll/Skutsch (1897) and Kroll/Skutsch/Ziegler
   (1913), Teubner, 2 volumes

**What it is.** The only complete Latin astrological textbook to survive from
antiquity, written 334-337 CE. Firmicus is a contemporary source for the doctrine
the shipping engine already computes (sect, the five dignities, whole-sign
houses) and is one of the two authors DEFENSIBILITY.md names as carrying worked
example charts (that expectation did not pay off in this pass - see below).

**Provenance of the fetched copy.** Two `_djvu.txt` OCR text extracts:

- `firmicus_mathesis_kroll_skutsch_1897_vol1_djvu.txt` (656 KB, sha256
  `032d4df86ea409717cf4922b5718d404c27d5af4bda2f22136612c72dc555e5b`). Title page
  and preface read directly: "IULII FIRMICI MATERNI MATHESEOS LIBRI VIII
  EDIDERUNT W. KROLL ET P. SKUTSCH ... LIPSIAE IN AEDIBUS B. G. TEUBNERI
  MDCCCXCVII" = 1897. This fascicle contains Books I-IV plus the Book V preface.
- `firmicus_mathesis_kroll_skutsch_ziegler_1913_vol2_djvu.txt` (1.7 MB, sha256
  `b6733f346d25ac4da739c1156b5ad80130f525d1a523b44807ca0204275b2b30`). Title page
  and preface read directly: "EDIDERUNT W. KROLL ET F. SKUTSCH IN OPERIS
  SOCIETATEM ASSUMPTO K. ZIEGLER ... LIPSIAE IN AEDIBUS B.G.TEUBNERI MCMXIII" =
  1913. This fascicle contains Books V-VIII plus the full preface and indices.
  The preface itself explains why a third editor (Ziegler) had to be brought in
  for this fascicle - consistent with Skutsch (d. 1912) not living to see it
  finished.

**OCR quality.** Clean, ordinary Latin OCR noise (u/v confusion, occasional
dropped ligatures, some marginal-note garbling) - directly readable without any
systemic corruption. This was verified by a full-file scan for genuine Greek
Unicode characters (0 in both volumes, as expected for a Latin text) and by
extensive direct reading of Book II (signs, domiciles, exaltations, decans,
bounds, sect) and spot reading in Book III.

**What survives / what is lost.** Book II's own internal chapter index (quoted
in Kroll/Skutsch's own apparatus) records that chapters VIII-XIV are missing
entire from the oldest manuscript branch (sigla M, P, R, V): *De formis
stellarum*, *De ortu stellarum*, *De Luna quid cui astro se iungens significet*,
*De stellis quando sint matutinae*, *De scematibus stellarum*, *De moribus
stellarum et quo tempore quas vires habeant*, and a second *De stellis quando
sint matutinae quando vespertinae*. Some of this material survives, relocated
and out of place, in the later manuscripts (A, B, C, D, F) and Kroll/Skutsch
printed it back into its indicated position. This pack cites nothing from that
gap without first re-confirming an independent chapter heading or running page
header around it (see `hel.firmicus.book2_lost_chapters_disclosed` in
`delineation_rule_manifest.json`).

**Rights.** Published 1897 and 1913. Under United States copyright law, works
published before January 1, 1929 are in the public domain regardless of the
individual contributors' death dates - both fascicles clear this bar cleanly for
a US-market product. One nuance is worth recording for completeness even though
it does not change the US analysis: if the "K. Ziegler" who joined the second
fascicle is the classicist Konrat Ziegler (1884-1974), his own specific editorial
contributions would, in a life+70-year jurisdiction, not lapse until 2044. This
does not affect this product's rights position, which rests on the 1913
publication date, not on any contributor's lifespan.

**Worked-example search result.** DEFENSIBILITY.md's requirement 4 names Firmicus
as a worked-example source. A targeted search of both volumes for markers of a
real, dated nativity (`genitura` + a named person, `natus est`, consulship-year
phrasing, first-person testimonial language like `expertus sum`/`vidimus`) found
none. This is a keyword-search result over roughly 2.3M characters of text, not
an exhaustive cover-to-cover read of an eight-book work - it is recorded as the
single biggest concrete next step for this pack, not as proof no such chart
exists (Firmicus is known in the secondary literature to include illustrative
combinations; whether any of them is a real, dated chart rather than a
paradigmatic one was not conclusively settled in this pass).

## 2. Claudius Ptolemy, *Apotelesmatika* (*Tetrabiblos*) - Boll/Boer, Teubner

**What it is.** The single most influential Hellenistic astrological text
transmitted directly in Greek. Unlike Valens and Firmicus, Ptolemy's Tetrabiblos
is a systematic, theory-first work and is not known to contain worked example
nativities - it explains doctrine, including (distinctively) *why* the malefics
are cross-assigned to the opposite sect's temperament, which neither Valens nor
Firmicus states as an explicit physical rationale in the material read for this
pack.

**Provenance of the fetched copy.** `ptolemy_apotelesmatika_boll_boer_teubner_djvu.txt`
(812 KB, sha256 `ffb057eb1c5ce3f8cb39e67e70f30430ab0f98d0c88136569b977d9049f9d0b4`).
The title page is badly mangled by OCR (a common failure mode where Latin
majuscule title-page typography gets read through a Greek-glyph model, producing
strings like "ΥΟΥΥΜῈΕΝ 111" for "VOLUMEN III"), but is reconstructible: "VOLUMEN
III APOTELESMATIKA EDIDERUNT F. BOLL ET AE. BOER, EDITIO STEREOTYPA CORRECTIOR
EDITIONIS PRIORIS" - i.e. **this file is a corrected stereotype (photomechanical)
reprint of an earlier edition, not the first edition itself.** The front-matter
bibliography contains internal citations dated 1940, consistent with the
well-documented first publication of Boll/Boer's Apotelesmatika in the Teubner
*Bibliotheca Scriptorum Graecorum et Romanorum* series in 1940 (Franz Boll died
in 1924; Aemilie Boer completed and published the edition).

**OCR quality.** The body Greek text is genuine, directly-encoded polytonic
Unicode throughout - a full-file scan found a consistent high density of real
Greek characters (roughly 1400-1500 per 2000-character sample across the entire
443,634-character file) and thousands of occurrences of common words like
καί/καὶ. This is ordinary OCR noise (occasional σ/ς and ρ/π confusion, some
line-final hyphenation artifacts), not the systemic font-mapping failure found in
the Valens file. Multiple passages (the sect chapter, the fire-triplicity
chapter, the parents chapter, the children chapter) were read directly and used
as source-of-record Greek for this pack's Ptolemy rules.

**Rights - flagged, not assumed.** This is the one source in this pack whose
rights status is genuinely open. Ptolemy's own 2nd-century Greek text is public
domain by age many times over; that is not in question. The specific *edition*
here, however, was first published in 1940 - after the US's flat pre-1929
public-domain cutoff that cleanly covers the Kroll-tradition Firmicus and Valens
volumes in this same pack. A foreign scholarly work first published in 1940 has
a US copyright status that depends on renewal history and, potentially, URAA
restoration (the Uruguay Round Agreements Act can restore US copyright to
foreign works that were still under copyright in their home country as of the
URAA date if they had fallen into the US public domain only through a lapsed
formality) - neither was checked in this pass. **This is recorded as an open
question and the corpus's own "verify, don't assume" instruction is followed: no
blanket public-domain claim is made for this specific edition.** The underlying
ancient Greek text remains fully quotable as a matter of intellectual history
regardless; what is unverified is the specific modern critical apparatus's
current US rights status.

## 3. Vettius Valens, *Anthologiae* - Kroll (1908), Weidmann - ACCESS FAILURE

**What it is.** The largest surviving body of Hellenistic astrological doctrine
in Greek, and (per standard scholarship on the text, confirmed here only through
Riley's modern translation used as a location aid, never as quoted authority) the
richest known source of real worked nativities cast by a practicing astrologer,
including Valens's own datable nativity in the later books. This was the single
highest-value target named in this task's instructions.

**Provenance of the fetched copy.**
`valens_anthologiae_kroll_1908_djvu.txt` (1.2 MB, sha256
`fdefb79a462b1e0b953b78713bed17aef24bdd25da65261112a105014003206c`). The Latin
front matter is legible and confirms: Kroll, Berlin (Weidmann), MDCCCCVIII =
1908 (dedication "In memoriam ... obiit December 23 1897" for Hermann Usener,
who originated the edition project).

**OCR quality - total failure of the Greek body text.** A full-file scan for
genuine Greek Unicode characters (`Ͱ`-`Ͽ`, `ἀ`-`῿`) across
all 1,100,625 characters of the file found **zero** matches, sampled at 100,000-
character intervals across the entire document and confirmed by an exhaustive
full-file regex count, not just spot sampling. By contrast, the same scan
applied to the Ptolemy file (443,634 characters, roughly 40% the size) found
2,277 occurrences of καί/καὶ alone. The Greek in the Valens file was evidently
OCR'd through a badly mismatched font-encoding model that mapped Greek glyph
shapes onto visually similar Latin letters (for example, the OCR renders what is
almost certainly νεκροφύλακες, "corpse-guards" - a real, attested Hellenistic
astrological term for planets ruling the eighth place - as the nonsense string
"vExQoqrv?.axEg"). **This is the identical failure class already documented and
named in this corpus's Byzantine pack for John Lydus's *De ostentis* (Wachsmuth
1897): an access/OCR-quality problem, not a language or rights problem** (see
DEFENSIBILITY.md's "translation is not a gate for quotation" table, row 3).

No attempt was made to reverse-engineer the font's character mapping from first
principles. A few strings look tantalizingly decodable by inspection (e.g. `xrjg`
plausibly maps to *τῆς*, `xal` plausibly to *καί*), but building a full
substitution table without an independent ground truth to validate it against
would risk exactly the kind of invented/misremembered quotation this corpus's
DEFENSIBILITY.md explicitly forbids ("that is not what the text says"). No rule
in this pack cites the Valens Greek text.

**Rights.** Published 1908 - would be safely public domain in the US under the
flat pre-1929 rule if the text were usable. The blocker is access quality, full
stop.

**What Riley's translation was used for (and only for).** Eight pages of Mark T.
Riley's 1990s English translation (`valens_anthologies_riley_translation.pdf`,
2.9 MB, sha256 `1abcb8f24a6b649c8e1c66ab0c398f99e8128c09000c7c8cca863a7c3a32ec6b`)
were read to confirm, independently of memory, that Book I opens with exactly
the planetary-significations-plus-sect chapter the standard scholarship expects,
and that its Egyptian bounds table ("The 50 Terms") is numerically consistent
with the Firmicus/engine bound table already cross-checked from a usable source
(Aries: Jupiter 6°, Venus 6°, Mercury 8°, Mars 5°, Saturn 5° in Riley's rendering
- 6/12/20/25/30 as cumulative ends, an exact match to
`reference_data.EGYPTIAN_TERMS[Sign.ARIES]`). This translation is a modern,
in-copyright work and is used strictly as a reading aid to orient this pass in
Valens's structure, per DEFENSIBILITY.md; it is never quoted as source authority
and no rule in `delineation_rule_manifest.json` is built on it.

**Next step, named plainly.** Render page images of the same (or a better) scan
of Kroll 1908 and read them directly, exactly as the Byzantine pack did for its
own Lydus-class failure. Only that unblocks Valens's sect chapter and his own
nativity as quotable Greek.

## Summary table

| Source | OCR usable? | Rights (US) | Used for |
|---|---|---|---|
| Firmicus vol.1 (Kroll/Skutsch 1897) | Yes, clean | Safely public domain (pre-1929) | 8 of 12 rules |
| Firmicus vol.2 (Kroll/Skutsch/Ziegler 1913) | Yes, clean | Safely public domain (pre-1929); Ziegler-apparatus nuance disclosed | 4 of 12 rules (cross-references only; see rule locations) |
| Ptolemy (Boll/Boer, this stereotype reprint of the 1940 edition) | Yes, ordinary noise | **Ancient text: PD. This 1940 edition: unverified, flagged** | 7 rules |
| Valens (Kroll 1908) | **No - total OCR failure** | Would be PD if usable | 0 rules; inventoried as a blocked lead only |
| Riley's Valens translation (1990s) | Yes (it is a normal English PDF) | In copyright, modern | Location/orientation aid only, never quoted as authority |

## 4. The Mathesis delineation-at-volume pack (added 2026-08-03)

A second extraction pass over the same two Firmicus volumes produced
`mathesis_delineation_rule_manifest.json` (23 rules, 196 quoted Latin cells,
~9,400 words of Latin with ~8,200 words of engine rendering) and
`mathesis_delineation_validation_vectors.json` (37 vectors). No new source
artifacts were fetched; the same SHA-256-pinned OCR files are the text of
record, and every cell carries its own char offset and line anchor into them.

**What was read and mined.**

- **Book II.17-19** (vol. 1): the idle places, the place-priority pairs, and
  the full twelve-place topical significations, including the Moon's 8th-place
  night-only joy.
- **Book III.2-7 and III.13** (vol. 1): the seven planet-in-place chapters -
  the single largest block (107 house cells), sect-split throughout exactly as
  Firmicus prints it (`per diem`/`per noctem` sub-cells).
- **Book IV.9-15** (vol. 1): the Moon-flow doctrine - the Moon separating from
  each planet and applying to another, split by lunar phase
  (crescens/minuta) and often by sect, plus the void-of-application series
  (`ad nullum feratur ... per vacuum`).
- **Book IV.17** (vol. 1): the Lot of Fortune - both computations (platic
  whole-sign and the by-degree method Firmicus tells the reader to follow),
  its significations, the double ruler procedure (domicile lord AND bound lord
  of the Lot's degree), and the verdict clause.
- **Book V.2-6** (vol. 2): the Ascendant in the Egyptian bounds of each of the
  five planets; Saturn in all twelve signs; Jupiter in the signs as far as the
  text survives; the Mercury-in-dignities fragment; and the Moon in the
  domicile/decan/bounds of each planet, phase-split.
- **Book VI.3-22** (vol. 2): six precisely-stateable two-planet aspect cells
  (Saturn-Jupiter in all four figures, Jupiter-Venus and Jupiter-Mercury
  trines).

**Textual findings worth recording.**

1. **The great Book V lacuna, confirmed in the fetched copy.** V.3 (Saturn in
   the signs) survives complete; V.4 (Jupiter) begins mid-chapter at Cancer
   and breaks off after Capricorn; the parallel chapters for Mars, the Sun and
   Venus in the signs are lost entirely; V.5 (Mercury) survives only as two
   cells (the Sun's domicile/decan, Venus' bounds/decan) plus a
   cross-reference to a lost earlier treatment of Mercury in the Moon's
   domicile; V.6 (the Moon) survives complete. The encoded rules report these
   as gaps that must not be filled from other authors.
2. **Apparatus interleaving is the dominant OCR hazard in vol. 2.** Kroll's
   critical apparatus is printed as page footnotes, and the OCR stream splices
   it into the running text at every page break; several lemmata are split
   mid-word across it ([Saturnus in Capricorno], [Saturnus in Piscibus],
   [Horoscopus in finibus Mercurii]). Every affected quotation stops at the
   last clean clause before the splice and says so in its cell notes.
3. **The Dorotheus lineage of Book VI.** Kroll/Skutsch/Ziegler print the Greek
   parallels from the Anonymous De planetis (CCAG II 159-180) beneath the
   aspect chapters and cite Heeg's demonstration that both Firmicus and the
   Anonymous descend from Dorotheus of Sidon - recorded in the aspect rule's
   exceptions.
4. **Editorial supplements followed as printed.** Angle-bracket supplements
   (`<a>`, `<se>`, `<neque de maternis>`, the whole opening clause of the
   Jupiter-bounds cell at V.2.5) are quoted as the edition prints them and
   flagged in cell notes; marked lacunae (rows of asterisks) stop the
   quotation.

**Refusal handling.** 55 of the 196 cells are encoded faithfully but marked
`output_policy: refused` (death timing/manner, lifespan numbers, servitude and
child-exposure verdicts, disease/disability as fate, sexual defamation,
criminal-conduct claims); where only one clause of an otherwise renderable
cell is affected, the clause is quarantined in `restricted_clauses` instead
and the rest of the cell stays renderable.

## Open question referred to the product owner (2026-08-02): the water triplicity

A research pass proposed changing the LIVE engine's `PTOLEMAIC_TRIPLICITY`
water-triangle day ruler from Mars to Venus. **The change was reverted, not
applied**, and is recorded here instead, because it alters shipping behaviour and
the decision is not a research call.

The substance is real and worth a decision:

- **Ptolemy's own text** (*Tetrabiblos* I.21) says of the watery triangle that
  Mars has familiarity with it through Scorpio, "but since the signs are
  feminine, the Moon by night and Venus by day, together with Mars, govern it."
  Read straight, that gives **Venus by day, Moon by night**, with Mars as a
  co-ruler of the triangle.
- **Lilly's printed table** gives **Mars by day and Mars by night** for water.
- **The engine currently holds** `("Mars", "Moon")` — Mars by day, Moon by night,
  which matches *neither* authority exactly.

The constant is named `PTOLEMAIC_TRIPLICITY` but its own comment reads
"(Lilly Mode)", so the mismatch may be deliberate: the code may intend Lilly's
scheme under a Ptolemaic label, in which case the day ruler should arguably be
Mars (Lilly) rather than Venus (Ptolemy) — and the *night* ruler is then the
part that diverges from Lilly instead.

Why this is not a research-side fix:

1. It feeds the Almuten Figuris scorer, so it can change the published Lord of
   the Geniture for any day chart with planets in water signs.
2. The three candidate tables disagree with each other, so "correcting" toward
   one silently picks a side in a live product.
3. The corpus convention elsewhere is to *show* such a fork rather than resolve
   it (compare the Firmicus Sagittarius-bounds divergence recorded in
   `delineation_rule_manifest.json`, where the engine keeps the consensus
   reading and the outlier is disclosed).

**Recommended resolution:** decide explicitly whether the constant means Ptolemy
or Lilly, rename it accordingly, and — if both are wanted — carry both tables and
disclose the fork the way the Hellenistic section already does for bounds and
triplicities. No code change should be made on research authority alone.
