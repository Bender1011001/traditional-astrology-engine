# Latin-European (Lilly, Christian Astrology 1647) source audit

Status: witness pinned, terms-of-art and point-table doctrine extracted; not production approval
Updated: 2026-08-03

## Result of this pass

The Latin-European track previously computed Lilly-style essential dignity scoring, Regiomontanus
cusps and accidental dignities in `src/engine/multitradition/hellenistic.py` (`build_latin_european`)
with **no rule manifest behind it**. This pass gives the tradition its first source-pinned
delineation layer, mined directly from the 1647 first edition of *Christian Astrology*.

## Witness selection

| Candidate | Verdict |
|---|---|
| EEBO-TCP diplomatic transcription | **Does not exist.** The `textcreationpartnership/Texts` catalog (TCP.csv, retrieved 2026-08-03) has no *Christian Astrology* row (Wing L2215) among its eleven-plus Lilly-related entries. The first repo guessed (A48431) is Lightfoot's *Works*, not Lilly. |
| archive.org `b30338724` (Wellcome, 1647) | **Pinned, primary.** Public Domain Mark 1.0; OCR text layer 2,005,702 bytes, sha256 `7c08b553…`. Long-s OCR'd as `f`; prose highly legible. |
| archive.org `bim_early-english-books-1641-1700_…_1647` (British Library microfilm) | **Pinned, second witness.** OCR 1,681,858 bytes, sha256 `f661a0a1…`. Preserves `ſ`; cleaner for the terms-of-art chapter (the void-of-course definition reads whole here). |
| 1659 second edition (`b30328524_0001`), 1852 Zadkiel abridgment, modern Regulus 1985 | Not used. First edition controls; the Zadkiel and Regulus texts are edited/copyright-encumbered respectively. |

Two page photographs were additionally pinned from the Wellcome item's IIIF endpoint, because both
OCR layers garble the numeric tables:

- `sources/ca1647_wellcome_leaf141_p107_orb_table.jpg` (sha256 `5d752cfc…`) — CA p. 107, the orb
  table. Every digit of both columns read from the photograph.
- `sources/ca1647_wellcome_leaf149_p115_point_table.jpg` (sha256 `083de395…`) — CA p. 115, the
  fortitude/debility point table. All 41 point values read from the photograph.

Full URLs, byte counts and hashes: `sources/access_manifest.json`.

## Legibility verdict (checked by reading, not assumed)

**Connected prose: good.** Examples actually read whole in the pinned text layers: the void-of-course
definition ("A Planet is voyd of courſe, when he is ſeperated from a Pla-net, nor doth forthwith,
during his being in that Signe, apply to any other" — BIM lines ~8200-8206); the full separation
passage with the Sun/Moon 13°30′ moiety arithmetic (Wellcome, p. 110); both manners paragraphs of
every planet chapter; the considerations and perfection chapters entire.

**Numeric tables: degraded in both OCR layers.** The Wellcome layer collapses the p. 115 debility
digits into `00 4^ v-A 4^ <ui 4*`; the BIM layer drops several fortitude digits. This was resolved
by reading the pinned page photographs, not by filling from memory or later editions. Where a digit
remained doubtful even at the photograph (none did for the two tables) or in prose (Venus's maximum
elongation, cazimi's first numeral, some example placements), the doubt is recorded **inside the
affected rule** instead of being silently resolved.

## What was extracted

`lilly_ca_rule_manifest.json`: 34 rules. `lilly_ca_validation_vectors.json`: 52 vectors; every rule
referenced by at least one vector.

1. **Aspect doctrine** — aspect inventory and qualities; partill/platick with moiety arithmetic; the
   complete p. 107 orb table (both columns, plus the Jupiter-chapter 9° internal variant recorded);
   application three ways; superior/inferior application and dexter/sinister; separation beginning at
   6′ and completing at summed moieties; prohibition (bodily and aspectal); refranation; translation
   (both of Lilly's forms — the Book 1 form without reception and the perfection-chapter form
   requiring it); collection with double reception; frustration.
2. **Reception** — definition, ranked types (domicile "strongest and best", then exaltation,
   triplicity, term, face), and the effect: mutual reception perfects a matter that aspects deny.
3. **The p. 115 point table, complete** — 8 essential rows (+5/+4/+3/+2/+1; −5/−4/−5 with mutual
   reception by house scoring as domicile and by exaltation as exaltation), 18 accidental fortitude
   rows, 15 accidental debility rows. Note the 1647 reading "In the eighth and sixth **2**" (not 4).
4. **Solar and other conditions** — combustion 8°30′ (with Lilly's own dissenting moiety opinion
   recorded), under-beams 17°, cazimi 17′, oriental/occidental, hayz, besieging, peregrine, void of
   course with the four exception signs.
5. **Planet natures** — all seven, with hot/cold/moist/dry qualities, humour, sect, benefic/malefic
   class, and the well-dignified/ill-dignified manners fork quoted verbatim.
6. **Planetary hours** (weekday ruler, 1st and 8th hour from sunrise) and, as domain-`other` horary
   doctrine with scope notes: the considerations before judgment and the seven modes of perfection.

## Worked example reproduced

Lilly's own scoring of the Book 2 riches figure (CA pp. 179-181) is encoded as vectors: Jupiter 20
("He hath no Debilities, either Accidentall or Essentiall": 4+5+4+2+5), Venus 23−5=18, Mercury
18−5=13, Moon 12−7=5, and his collected table (Saturn 8, Jupiter 20, Mars 9, Sun 8, Venus 18,
Mercury 13, Moon 5; Part of Fortune weak by two testimonies). His arithmetic reproduces exactly from
the p. 115 table as encoded — the strongest available check that the table was keyed correctly.

## Cross-references against the al-Qabisi pack

Recorded per-rule in `conflicts_with`, notably:

| Concept | Lilly (1647) | al-Qabisi (10th c.) | Verdict |
|---|---|---|---|
| Void of course | any planet; separated, applying to none for the rest of its sign; Moon emphasized; performs somewhat in ♉♋♐♓ | any planet; same remainder-of-sign definition; adds the distinct "feral" | **Concordant definitions** — recorded as concordance, not conflict |
| Application/orb | per-planet orbs, summed moieties | flat 6° rule | Conflict recorded |
| Reception | mutual, in each other's dignities; perfecting effect | one-directional *qabul* + "return" to weakened planets | Divergence recorded |
| Translation | perfection form requires the translator be received | *naql* has no reception condition | Divergence recorded |
| Collection | both must receive the collector | *radd al-nur*, no reception; second form via transfer | Divergence recorded |
| Terms/bounds | Ptolemaic, by Lilly's explicit attribution | Egyptian bounds (as does the engine's reference table) | **Conflict recorded** — a Lilly-mode scorer must not use Egyptian bounds |
| Dignity points | 5/4/3/2/1 | identical ladder, seven centuries earlier | Concordance (already noted in the al-Qabisi pass) |

## Boundaries

- `publication_status: research_only`; `customer_prediction: false` on every rule.
- Death-timing, lifespan (Hyleg/Alcocoden) and moralizing fate-claims were **not extracted**; the
  refusal list in `defensibility_spec.md` governs.
- Horary-specific doctrine is carried as domain `other` with explicit scope notes, not passed off as
  natal.

## Known gaps / next actions

1. The p. 104 essential-dignity table's degree columns (Ptolemaic terms digits) are OCR-degraded and
   were not re-keyed; only the attribution claim is encoded. Key them from page photographs.
2. CA Book 3 (nativities): the temperament-collection apparatus and the worked nativity remain
   unmined; Book 2's remaining worked figures likewise.
3. Independent specialist review (early-modern English / history of astrology) before any rule
   leaves `research_only`.

## 2026-08-03: the p.104 Ptolemaic terms are keyed - the named follow-up is closed

The digits of "A Table of the Essentiall Dignities of the Planets according to
Ptolomy" (CA p.104, leaf 138) were read from IIIF page photographs (full page
plus three high-resolution crops, all hash-pinned in `sources/`), because both
OCR text layers garble the table. All twelve term rows are monotone, close at
30, and agree with the received Ptolemaic set. The same photograph confirms
Lilly's triplicity column for the watery signs as Mars day AND night (the
Cancer row prints Mars/Mars), corroborating the LILLY_TRIPLICITY table from
the printed doctrine.

Consequence in the engine: `build_latin_european`'s scorer no longer blends
traditions. Its +2 now comes from `PTOLEMAIC_TERMS_LILLY1647` and its +3 from
`LILLY_TRIPLICITY`; Egyptian bounds and Dorothean triplicities remain the
Hellenistic section's. A discriminating regression test pins Aries 12.5° -
Mercury by the Egyptian table, Venus by the Ptolemaic - so the blend cannot
quietly return.
