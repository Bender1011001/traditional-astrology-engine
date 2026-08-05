# Jyotisha defensibility spec

Status: governing spec for the Vedic reading section  
Updated: 2026-08-02  
Standard: [../DEFENSIBILITY.md](../DEFENSIBILITY.md)

This spec governs the Parasari (BPHS-descended) track. It is deliberately
distinct from the sign-based Jaimini track at `../jaimini/`, which has its own
defensibility spec and is not merged with this one.

The adversary here is a working Jyotishi. That reader will check for divisional
charts and dasha before anything else, and will notice immediately if the section
reasons like a Western chart wearing sidereal longitudes.

## Core-technique checklist

| # | Technique | Source basis | Status |
|---|---|---|---|
| 1 | Sidereal longitudes under a named ayanamsa | India Calendar Reform Committee 1956 (registry: `jyotisha_india_calendar_reform_committee_1956`) fixes Lahiri as the civil standard | `implemented` (Lahiri, disclosed) |
| 2 | Lagna, its lord, and the lord's placement | Brhajjataka I; BPHS lagna chapters | `implemented` |
| 3 | Rasi (D1) placements with dignity | Brhajjataka II (encoded in `brhajjataka_planetary_rule_manifest.json`) | `implemented` |
| 4 | Nakshatra and pada for Moon, lagna, and each graha | Brhajjataka I.4-14 passages already passage-aligned | `implemented` |
| 5 | Whole-sign bhava assignment | classical default; Sripati is the live alternative | `implemented` (disclosed) |
| 6 | **Navamsha (D9)** | universally treated as mandatory; BPHS varga chapters | `implemented` (all grahas, nodes, lagna; vargottama flagged; D9 dignity separate) |
| 7 | Vimshottari mahadasha from janma nakshatra | BPHS dasha chapters; standard 120-year scheme | `implemented` |
| 8 | Vimshottari antardasha (bhukti) | same | `implemented` |
| 9 | Graha dignity: exaltation, debilitation, own sign, moolatrikona | Brhajjataka II | `implemented` (moolatrikona pending) |
| 10 | Friendship/enmity (naisargika and tatkalika) | BPHS relationship chapters | `implemented` (naisargika; tatkalika/panchadha not computed and disclosed) |
| 11 | Graha drishti (special aspects for Mars, Jupiter, Saturn) | BPHS aspect chapters | `implemented` |
| 12 | Yogas: Raja, Dhana, and yogakaraka identification | BPHS yoga chapters; Phaladeepika | `implemented` (with constituent facts, evaluated only after items 1-6) |
| 13 | Combustion (astangata) | BPHS | `implemented` |
| 14 | **Shadbala** — all six strengths with their sub-components and the pinda | BPHS Subodhini 1899 **uttara-khanda adhyaya 2**, slokas 1-46 (`strength_rule_manifest.json`) | `source_gated` — **fully encoded 2026-08-05 as computable procedure**: all six balas (drik, sthana, dig, kala, cheshta/ayana, naisargika), every sub-component (uccha, saptavargaja, ojayugma, kendradi, drekkana; natonnata, paksha, tribhaga, varsha/masa/dina/hora; ayana, gati, yuddha), the pinda assembly with its quarter-of-drsti correction, the required-minimum table, bhava-bala and bhava-dig-bala. Nine of the chapter's own worked figures recompute exactly. Still gated: independent Sanskrit review, and five limbs need inputs the engine lacks (see below) |
| 15 | **Ashtakavarga** — bhinna, sarva, the rekha/bindu tables, trikona and ekadhipatya sodhana, the pinda | BPHS Subodhini 1899 **uttara-khanda adhyaya 1** slokas 46-72 and **purva-khanda adhyayas 17, 18, 19, 20** (`strength_rule_manifest.json`) | `source_gated` — **fully encoded 2026-08-05**: all eight bhinnashtakavarga tables (each verified by row-sum against its canonical total, 337 in sum), the karana/bindu-versus-sthana/rekha notation trap, sarvashtakavarga with its strength grades, both reductions with all their cases, and pindotpatti with both gunaka tables and the chapter's own fully worked pinda (40 + 51 = 91). Still gated: independent Sanskrit review; three cells were settled by row-sum rather than by ink and are named |
| 16 | **Other vargas** (D10 career, D7 children, D12 parents, D3, D30, D2, D4, D60) and the shodasavarga scheme with vimsopaka bala | BPHS Subodhini 1899 **purva-khanda adhyaya 3**, slokas 52-129 (`varga_rule_manifest.json`) | `source_gated` — **computation rules encoded 2026-08-05 for D2, D3, D4, D7, D10, D12, D30, D60**, plus the sixteen-varga enumeration, the varga-to-question map (D10 career, D7 children, D12 parents, D30 misfortune), the tier names, and vimsopaka bala in all four schemes. Six vargas (D16, D20, D24, D27, D40, D45) are named by the text and remain **unmined, not blocked** |
| 17 | Planet-in-bhava classical delineation text (as opposed to structural condition alone) | Phaladeepika Adhyaya VIII (`delineation_rule_manifest.json`) | `source_gated` — sourced and paraphrased for 8 of 9 grahas across all 12 houses (Saturn 11/12, Sun 5/12); translation rights unresolved, independent Sanskrit review pending, no composer wiring written |
| 18 | Named-yoga delineation text (Pancha Mahapurusha, Kesari/Sakata, Mahabhagya, Adhama/Sama/Varishtha, Sunapha/Anapha/Durudhara/Kemadruma, Vesi/Vaasi/Kartari, 4 Rajayogas, Neechabhanga Rajayoga) | Phaladeepika Adhyayas V-VII (`delineation_rule_manifest.json`) | `source_gated` — same translation-rights/review hold as #17; several sub-yogas additionally need house-from-Moon or house-from-Sun computation the engine does not yet perform |
| 19 | Vimshottari mahadasha classical significations (general, per graha) | Phaladeepika Adhyaya XIX (`delineation_rule_manifest.json`) | `source_gated` — same translation-rights/review hold as #17; antardasha-level significations not yet sourced |
| 20 | **Bhavesha-in-bhava delineation from the root text itself** (lord of each bhava, in each bhava) | BPHS Subodhini 1899 purva-khanda adhyaya 15 (`bphs_rule_manifest.json`) | `source_gated` — 132 of 144 cells transcribed from the Sanskrit and rendered; independent Sanskrit review outstanding before promotion, and no composer wiring written |
| 21 | Functional benefic/malefic/yogakaraka/maraka by lagna | BPHS Subodhini 1899 adhyaya 13 (`bphs_rule_manifest.json`) | `source_gated` — all 12 lagnas transcribed (Aries partial, page-image gap); this recension's assignments diverge from the modern handbooks and the divergence is unresolved |
| 22 | Graded drishti (pada/dvipada/tripada/purna per graha per house-offset) | BPHS Subodhini 1899 adhyaya 4, slokas 23-29 (`bphs_rule_manifest.json`) | `source_gated` — the root text grades every aspect on a four-step scale rather than the flat special-aspect rule item 11 implements; the two are in open conflict and the conflict is recorded, not resolved |
| 23 | Rasi drishti (sign-to-sign aspect) taught inside the Parasari root text | BPHS Subodhini 1899 adhyaya 4, slokas 2-18 (`bphs_rule_manifest.json`) | `source_gated` — the recension teaches it in the main chapter sequence, which weakens the corpus's own Parasari/Jaimini partition; needs a doctrinal decision, not code |
| 24 | Vimshottari mahadasha delineation from the root text, conditioned on the dasha lord's dignity | BPHS Subodhini 1899 adhyaya 36 (`bphs_rule_manifest.json`) | `source_gated` — utkrsta/papa couplets for all 9 grahas plus placement-conditioned expansions for 8 (Ketu absent); column-interleave in the scan limits clause order |
| 25 | Antardasha quality from divisional placement (drekkana, dvadasamsa, trimsamsa) | BPHS Subodhini 1899 adhyaya 37, slokas 2-7 (`bphs_rule_manifest.json`) | `source_gated` — all six tests were encoded on 2026-08-02; five of them needed vargas that had no sourced computation rule. **As of 2026-08-05 they do**: D3, D12 and D30 are all defined in `varga_rule_manifest.json`, so this row's blocker is no longer a source blocker at all. What remains is engine work plus the independent Sanskrit review that gates the whole pack |
| 26 | **Graha in rasi delineation text** (which the engine has computed since day one and had no text for) | Saravali Adhyayas 22, 23, 25-29 read in Devanagari (`saravali_rule_manifest.json`); Brhajjataka XVIII via Aiyar (`brhajjataka_delineation_rule_manifest.json`) | `source_gated` — 82 rasi cells from Saravali (Mars Leo-Pisces lost to a missing leaf) and 72 from Brhajjataka; independent Sanskrit review outstanding, no composer wiring written |
| 27 | Graha-in-rasi modified by the graha aspecting it | Saravali 22, 25-29 (grouped by rasi owner) and 23 (sign by sign), 296 cells | `source_gated` — needs no new computation; the engine already emits drishti houses. Kalyanavarma attributes the method to "the elder Yavanas" (24.24) and that attribution is carried, not smoothed |
| 28 | **Graha in bhava from a second, undamaged witness** | Saravali Adhyaya 30, all seven grahas x twelve bhavas, 84 cells, no scan gap | `source_gated` — this closes the coverage hole item 17 left (Phaladeepika's Sun row is 5/12) *as coverage*, but Saravali is a different author and is rendered as a separate voice, never merged into item 17 |
| 29 | Moon in a navamsa, by the lord of that navamsa and the graha aspecting it | Saravali Adhyaya 24, 40 cells, plus the vargottama gate (24.22) and the navamsa-lord override (24.23) | `source_gated` — the engine already computes navamsa sign and vargottama; this is the first delineation text in the corpus keyed to item 6's own output |
| 30 | Vimshottari mahadasha delineation from Saravali, gated on the dasha lord's condition | Saravali Adhyaya 40 (`saravali_rule_manifest.json`) | `source_gated` — favourable and unfavourable halves for each graha, plus eight condition gates (dignity, bhava, enemy rasi, combustion, retrogression) and a within-period timing rule (sirsodaya/prsthodaya) that is computable today |

Items 14, 15 and 16 changed on 2026-08-05 and are the largest change this spec
has recorded. Until that date the track had thousands of delineation cells from
four authors and **no strength machinery at all** — it read well and weighed
nothing, which is the one thing a Jyotishi cannot work without. Adhyaya 15 sloka
100 (*balabalavivekena sarvesam phalam adiset*) and uttara 2 slokas 44-45 (the
strongest of the yoga-causing grahas is the one that gives the result) were
already recorded in this corpus as the text's own instruction to weigh, and there
was nothing to weigh with. There is now: 40 rules and 226 vectors of Shadbala and
Ashtakavarga arithmetic, and 13 rules and 75 vectors of divisional-chart
computation, all read out of the same 1899 scan that was declared unusable in the
engine's own source comments.

Three things about those numbers matter more than the count.

**They are arithmetic, so they are checkable, and they were checked.** The 1899
printing works its own examples. Nine of them were recomputed and reproduce the
printed result exactly — including the Sun's entire sadbala assembly (4|18|4 +
0|49|1 + 3|5|49 + 0|27|15 + 1|0|0 = 9|40|9 rupas, then corrected by a quarter of
the benefic drsti to 9|41|14) and the Sun's ashtakavarga pinda (graha-pinda 40 +
rasi-pinda 51 = yoga-pinda 91). Each of the eight bhinnashtakavarga tables was
additionally closed by row-sum against its canonical total. That is a far
stronger evidential position than any delineation cell in this pack: a failure
here is a failure against the source's own arithmetic, not against a translator's
judgment.

**They disagree with the modern handbooks in four places, and the disagreements
are published rather than normalised.** This recension's saptavargaja series is
45/30/20/15/10/4/2 (the handbooks give 45/30/22.5/15/7.5/3.75/1.875) and it
assigns 100 to a varga place that is the graha's own exaltation; its required
minimum strengths group the seven grahas into three classes at 6|32, 5|53 and
4|13 rupas (the handbooks give seven separate figures beginning Sun 5, Moon 6);
it does not double the Moon's paksha-bala; and it places ayana-bala with
cheshta-bala as the fourth bala rather than inside kala-bala. Any product that
says "BPHS says a graha is strong above N" without naming its recension is
guessing.

**One of them is a trap that would have corrupted every chart silently.** Uttara
1 sloka 72 defines *karana* = *bindu* as the ZERO and *sthana* = *rekha* as the
scored point, and the chapter enumerates the blanks first (slokas 19-45) and the
marks second (46-71). Popular modern writing routinely uses "bindu" for the
auspicious point, i.e. exactly backwards. An implementation that took this
chapter's first list for its scoring list would build every ashtakavarga
inverted and never fail a test.

Items 26-30 are new as of 2026-08-02 (second pass, same day). They come from
Kalyanavarma and Varahamihira, are held in their own manifests, and are not
merged with items 17-19 (Mantresvara) or 20-25 (BPHS). Item 26 is the one that
changes the shape of the gap: the engine has emitted every graha's rasi since it
was written and the corpus had no classical text for it at all. Item 28 is the
one that changes a recorded fact — the BPHS pass concluded that graha-in-bhava
coverage "still depends on a single damaged Phaladeepika scan," and Saravali 30
means it no longer does.

Items 17-19 are new as of 2026-08-02 and were added rather than folded into
items 7, 8 or 12, because those items are about calculation (mahadasha/
antardasha arithmetic) or structural detection (yoga conditions, with no
catalogue or phala attached, by design - see `vedic.py`'s own docstring), while
17-19 are about the classical delineation TEXT for those same facts. None of
items 1-16 changed status: this pass's sourcing did not touch Shadbala,
Ashtakavarga, or other-varga material, so 14-16 remain exactly as they were.
Items 20-25 are new as of 2026-08-02 and come from the root text itself rather
than from Mantresvara. They are kept as separate rows, and in a separate
manifest (`bphs_rule_manifest.json`), because BPHS and Phaladeepika are
different authors of different dates: item 20's bhavesha grid and item 17's
graha-in-bhava grid answer different questions and are never merged into one
delineation. Items 22 and 23 are the uncomfortable ones - the root text
contradicts what this engine currently implements (item 11) and what this
corpus's own tradition partition assumes - and they are recorded as conflicts
rather than quietly dropped.

17-25 are marked `source_gated`, not `computable`, because a real hold remains
on each (translation rights, independent review) and because this pass wrote
no composer or engine code to consume them; `computable` is reserved for gaps
that are ours alone and immediately actionable, which per
`ceiling_report.py` this corpus's own tooling refuses to let stand unresolved.

**Item 6 is done** (2026-08-01), verified by four structural properties the
classical rule guarantees and now covered by a runnable worked example. It
immediately earned its place: in the Fairfield chart Saturn is neutral in D1
Pisces but **exalted in D9 Libra** — a D1-only verdict on Saturn would have been
wrong.

## Judgment hierarchy

The composer must execute in this order. Later steps may qualify earlier ones;
they may not silently replace them.

1. Lagna and lagna lord: sign, degree, nakshatra, placement, condition.
2. Moon: janma rasi and janma nakshatra — in Jyotisha the Moon outranks the Sun
   for personal significations.
3. Graha dignity and placement in D1, with retrogradation and combustion.
4. Bhava rulership: which graha owns which house, and where that owner sits.
5. Drishti: who aspects what, including the special aspects.
6. Navamsha cross-check: does D9 confirm or undercut the D1 verdict on each graha.
7. Yogas, evaluated only after 1-6 and only where their constituent conditions
   have actually been verified.
8. Dasha: current mahadasha and antardasha, read against the qualified natal
   structure — never as free-floating themes.

**Amended 2026-08-05.** The hierarchy above was written when the corpus had no
strength machinery, and it therefore had to leave "strength" as an unexplained
word in steps 3 and 7. It no longer is, and the amendment is not cosmetic: the
root text supplies the arbiter and now the corpus holds it.

- Step 3 (dignity and placement) is completed by **sthana-bala**, whose five
  limbs are exactly the facts the engine already computes — dignity, varga
  dignity, rasi and navamsa parity, house from the lagna, degree within the rasi.
  This limb is computable today with no new inputs at all.
- Step 5 (drishti) is completed by **drik-bala**, and the completion is
  uncomfortable: uttara 2 slokas 2-7 turn every aspect into a continuous function
  of the arc between the two points, with six graded cases. That is the
  arithmetic under adhyaya 4's quarter-grading, and it is incompatible with the
  flat Mars 4/7/8, Jupiter 5/7/9, Saturn 3/7/10 rule the engine implements. The
  fork recorded at item 22 is now recorded twice, from two chapters, in two
  forms.
- Step 7 (yogas) has an explicit ordering rule the composer must execute:
  uttara 2 slokas 44-45 — *tesam baliyah krtasam sa evasya phalapradah*, "the
  strongest of the yoga-causing grahas is the very one that gives the result …
  where many yogas are obtained, this is declared the rule." **A composer that
  prints every detected yoga as a parallel bullet has not executed the source.**
  Sadbala is the ranking function the text itself provides, which is why its
  absence was never a decorative gap.
- A new step sits between 6 and 7 for any question about career, children,
  parents or misfortune: purva 3 slokas 103-108 name **D10, D7, D12 and D30** as
  the instruments for exactly those questions. A reading that answers a career
  question out of D1 and D9 has been given the wrong chart by its own tradition's
  reckoning.
- Ashtakavarga enters as a **separate** judgment, not as a modifier of the above.
  It has its own mandatory pipeline order — build the eight tables, sum the seven
  for the sarva total, then trikona sodhana, then ekadhipatya sodhana, then the
  pindas — and the order is load-bearing: the sarva total is taken from the
  UNREDUCED tables and the pindas from the twice-reduced ones. An implementation
  that reduces before summing reports a sarva total that is not 337 and is simply
  wrong.

The root text's own statement of this order, now that it is readable, agrees
with step 4 and adds a qualifier the composer must carry: BPHS Subodhini 1899
adhyaya 15 sloka 100 - *balabalavivekena sarvesam phalam adiset*, "the result of
every one of them is to be declared by discrimination of strength and weakness"
- and adhyaya 36 sloka 92 restates it for dasha. Neither bhavesha grid may be
rendered unconditionally. This is the text making proportionality part of the
rule, not a commentator softening it, and a reading that quotes a bhavesha cell
flat has already departed from the source.

Saravali states the same order in three places of its own, and all three are now
encoded rather than paraphrased:

- **23.86** — *rasipatau balayukte rasau ca balanvite tatha candre / rasiphalam
  syat sakalam nicoccavidhina ca sancintyam*: the rasi result is realised **in
  full** only when the rasi lord, the rasi and the graha are strong, and must
  then be weighed again by exaltation and debilitation. Step 3 gates step 6's
  input, not the other way round.
- **24.23** — *tasya nirodho drsto yady amsapatir bali bhavati*: the rasi result
  is **checked** if the navamsa lord is strong. This puts step 6 (navamsha)
  above step 3 (D1 verdict) explicitly, in the author's own words, and it is the
  strongest textual support this spec has for why item 6 is non-negotiable.
- **30.86-87** — malefics strike down the bhava they occupy and benefics nourish
  it, **inverted in the 6th, 8th and 12th**; and the whole bhava table is then
  defeasible by yoga, by benefic or friendly drishti, and by exaltation. A
  composer that prints a bhava line without running steps 3, 5 and 7 against it
  has not executed Kalyanavarma's order.

The practical consequence for the composer is that none of the 563 Saravali
cells may be emitted as a flat sentence. Each is a candidate that the strength,
navamsa and drishti steps either confirm, reduce or invert.

## Worked-example inventory

| Source | Location | Contains | Usable now |
|---|---|---|---|
| Brhajjataka, Aiyar 1905 translation | registry `jyotisha_varahamihira_brhajjataka_aiyar_1905_archive` | worked illustrations in the commentary | **inspected 2026-08-02**: keyword search of the full OCR found only abstract calculation walkthroughs ("suppose the Sun's longitude to be..."), no natal chart with real birth data and a stated verdict. Page-image (non-OCR) inspection still not attempted. **Second pass 2026-08-02**: Adhyaya XVIII read and encoded; still no nativity. The nearest thing found anywhere this pass is XXII.2, which walks a *constructed* configuration (Cancer rising with the Moon in it; Mars, Saturn, the Sun and Jupiter in exaltation) purely to illustrate the definition of karaka planets. That is an illustrative diagram with no native and no claimed outcome, and it is **not** a validation vector under requirement 4. Recorded so the next pass does not re-find it and mistake it for one. |
| Saravali, Subrahmanya 1914 | registry `jyotisha_kalyanavarma_saravali_subrahmanya_1914_archive` | example applications | still needs page inspection; OCR remains too corrupted to read (mixed scripts, many misrecognitions) |
| Saravali, Nirnaya Sagar Press 1907 | registry `jyotisha_kalyanavarma_saravali_nirnayasagar_1907_archive` | full Sanskrit text, chapter structure, any worked example | **READ 2026-08-02 (second pass)**: Adhyayas 22-30 and 40 read line by line in Devanagari and encoded (87 rules, 563 cells). Result for this inventory is **negative**: those chapters are rule statements throughout and work no nativity. Adhyayas 31-39 and 41-53 (including 40-41 dasha continuation, 44 stri-jataka, 51 nasta-jataka, 52 astakavarga) are **not yet read** and are where a worked figure would most plausibly sit — nasta-jataka in particular is a chapter about reconstructing an unknown birth, which is the genre most likely to carry one. |
| Phaladeepika, Subrahmanya 1950 | registry `jyotisha_mantreswara_phaladeepika_subrahmanya_1950_archive` | worked yoga examples | **inspected 2026-08-02**: Adhyayas V-VIII and XIX read directly; all are rule catalogs (now in `delineation_rule_manifest.json`), no worked chart found. Adhyayas IX-XVIII and XX-XXVIII not yet inspected. |
| BPHS Subodhini 1899 | registry `jyotisha_parasara_bphs_subodhini_1899_egangotri` (new 2026-08-02) | dasha and varga worked cases | **CORRECTED 2026-08-02**: the earlier "almost total `?` failure" verdict was wrong — the file has 100 question marks in 1,106,274 characters and 807,038 Devanagari codepoints, and reads. Worked material actually found: (a) adhyaya 37 sloka 1 gives the antardasha formula AND works it (Sun mahadasha 6 years, Sun antardasha within it 3 months 18 days) - directly checkable against the engine today, and the one BPHS claim in the pack needing no translation judgment; (b) adhyaya 36 slokas 8-10 work a Vimshottari balance from a stated Moon longitude; (c) adhyaya 28 slokas 44-48 name *natives* for the varga-dignity raja-yogas - Harishchandra, Bali, Yudhishthira, Shalivahana, Nagarjuna, "the Manus" - legendary and dynastic figures with no recoverable birth data, so inventory rather than test charts. |

| BPHS Subodhini 1899, **uttara-khanda adhyayas 1-2 and purva-khanda adhyayas 17-20** | registry `jyotisha_parasara_bphs_subodhini_1899_egangotri` (read 2026-08-04) | the strength and ashtakavarga arithmetic, worked | **THE RICHEST WORKED-EXAMPLE SEAM IN THIS TRADITION, and it is arithmetic rather than delineation.** Uttara 2 does not merely state the sadbala formulas, it *computes them for a specific chart* and prints the intermediate figures. Recomputed and reproducing exactly: the six drsti-value cases; the Sun's uccha-bala (114°14′ ÷ 3 = 38|04); the Sun's dig-bala (147°05′ ÷ 3 = 0|49|01); natonnata (unnata 24|22 doubled = 48|44, and 60 − 48|44 = 11|16); paksha (elongation 38°45′ ÷ 3 = 12|55, and 60 − 12|55 = 47|05); the kala-bala sum (0\|48\|44 + 0\|47\|5 + 1\|0\|0 + 0\|30\|0 = 3\|5\|49); ayana (40°52′30″ ÷ 3 = 13|37|30, doubled for the Sun = 27|15); **the complete sadbala assembly for the Sun, 9\|40\|9 rupas, corrected by a quarter of the benefic drsti to 9\|41\|14**; the first house's bhava-bala (5\|59\|16 + 0\|6\|52 + 0\|50\|41 = 6\|56\|49) and its dig-bala (85°15′ ÷ 3 = 28|25); the three required-minimum class totals (392, 353, 253 virupas = 6\|32, 5\|53, 4\|13 rupas); the four trikona-sodhana cases; and **the Sun's ashtakavarga pinda, graha-pinda 40 + rasi-pinda 51 = 91**. Every one of these is now a validation vector in `strength_validation_vectors.json`. This is the first material in the Jyotisha pack where a test failure would be a failure against the *source's own numbers* rather than against an encoder's reading, and it needs no translation judgment whatever. |

Brhajjataka, Phaladeepika and BPHS have now each had at least one direct,
non-metadata inspection pass for worked-example content specifically. Brhajjataka
and Phaladeepika came back negative in the chapters inspected. BPHS came back
POSITIVE on the second pass, after the first pass's legibility verdict was found
to be false - which is the more useful lesson of the two: a "the scan is
unreadable" finding is a claim about the scan, and it has to be produced by
reading the scan, not by a character-frequency impression of it. The Saravali branch is the one where
this pass changed the picture from "corrupted" to "legible but unread" - that
reading pass is the next highest-value M3 task for this tradition.

## Refusal list

- **No lifespan claim.** Ayurdaya methods exist and are recension-dependent; the
  live Western report already demonstrates how badly length-of-life arithmetic
  behaves when branches disagree. Jyotisha ayurdaya is not asserted.
- **No muhurta or remedial prescription.** Gemstone, mantra, and ritual remedies
  are prescriptive advice, not historical delineation.
- **No caste, varna, or social-rank delineation** rendered as a claim about the
  reader, even where the sources state it. Retain in the audit trace with the
  suppression reason.
- **No marriage-compatibility verdict** (kuta/guna milan) in a natal reading; it
  requires a second chart and its own source treatment.
- **No claim depending on Shadbala or Ashtakavarga** until those are implemented
  with sourced weights. **Restated 2026-08-05:** the weights are now sourced —
  every one of them, from the root text, with the recension named and the
  divergences from the handbooks published. What remains unsatisfied is
  *implemented*: no engine code computes any of it, five limbs need chart inputs
  the engine does not produce, and the independent Sanskrit review that gates the
  whole pack is outstanding. So the refusal stands, but its reason has changed
  from "we do not have the doctrine" to "we have not run it", and the reading
  must say which of those it means.
- **No varga-dignity tier predicate about a person.** Purva 3 slokas 92-100 grade
  a chart into kimshuka / vyanjana / chamara / chhatra / kundala / mukuta and
  parijata / uttama / gopura / simhasana / paravata / devaloka / brahmaloka /
  shakravahana / shridhama. The tier NAME is a defensible thing to report once
  the vargas are computed; the kingship and world-conquest predicate attached to
  the upper tiers is not, and is refused — the same treatment already given to
  adhyaya 28's raja-yoga ladder.
- **No progeny, fertility, or childlessness claim** rendered about a living
  reader. Phaladeepika's planet-in-bhava and yoga material (Adhyayas V-VIII)
  routinely states progeny counts or "childless" outcomes as part of a house or
  yoga result; those clauses are retained in `delineation_rule_manifest.json`
  as historical testimony with an explicit suppression note, the same
  treatment this spec already gives varna/caste material, and are never
  rendered as a claim about the reader's own fertility.
- **No maraka, killing-agency, or timing-of-death claim.** BPHS Subodhini 1899
  adhyaya 13 assigns a killing graha to every lagna and adhyaya 23 is an entire
  chapter of maraka distinctions. All of it is transcribed in
  `bphs_rule_manifest.json` with `output_policy: "refused"`; none of it is
  rendered, in any form, including as a softened "difficult period". The text's
  own sloka 40 is a *restriction* - a graha does not kill in its own dasha and
  bhukti - and it is encoded alongside the killing clauses, because a pack that
  records only the accusations and drops the exemptions misrepresents the
  doctrine it claims to be preserving.
- **No destitution or imprisonment verdict.** BPHS adhyaya 31's daridra-yogas
  and bandhana-yogas are encoded and refused for the same reason as the death
  material. They are kept in the manifest rather than skipped so that adhyaya
  30's dhana-yogas are not published as if the text only ever promised wealth.
- **No third-party defamation.** The bhavesha grid of adhyaya 15 repeatedly
  states that the native's wife is a courtesan or unchaste, that his mother is
  an adulteress, that his father is a great thief, or that his wife or child
  will not live. Every such clause is transcribed in full under
  `restricted_by_house` with its reason and is never rendered. The publishable
  remainder of the same verse is rendered; the verse is not discarded whole.
- **No `mleccha`, `jati`, impotence (`kliba`) or bodily-incapacity clause**
  rendered about a reader - extending the caste refusal above to the specific
  vocabulary this recension actually uses.
- **No "you will be a king" predicate.** The varga-dignity raja-yoga ladder of
  adhyaya 28 grades a chart into Parijata / Uttama / Gopura / Simhasana /
  Airavata / Paravata; the tier NAME would be a defensible thing to report if
  the vargas were ever computed, and the emperor predicate attached to it is
  not.
- **No horoscope-of-women-chapter or issue-chapter material.** Phaladeepika
  Adhyayas XI-XII were located and deliberately not mined for rules; their
  subject matter is marriage/progeny outcome for the native and falls under
  the two refusals immediately above and below.
- **No mode-of-death delineation.** The twelve-lagna block Aiyar appends to
  Brhajjataka XVIII — which he attributes to *Satyacharya*, not to Varahamihira —
  ends every one of its twelve cells with how the native dies (by weapon, by
  poison, by snake-bite, by drugs administered by women, by a fall, by fire).
  The rule is encoded in full and refused in full:
  `jyotisha.brhajjataka.18.lagna_rasi_satyacharya` carries
  `output_policy: "refused"` on every cell. It is kept because a corpus that
  drops the whole block cannot honestly claim to have read the chapter.
- **No sexual-violence or homicide predicate, in any framing.** Saravali 40.11
  states that in the Moon's mula-dasha with the Moon in a rasi of Mars the
  native violates a maiden or kills a young woman. It is transcribed verbatim
  and refused outright; it is not softened, not generalised into "conflict
  around relationships", and not rendered in any customer-facing context.
- **No disability, impotence or bodily-deformity delineation.** Saravali's rasi
  and bhava tables use `sanda`, `kliba`, `napumsaka`, `vikala`, `kubja`,
  `kana` (one-eyed), `badhira` (deaf), `muka` (mute), `kustha` (leprosy) and
  `bhagandara` (fistula) as ordinary delineation vocabulary. Every such cell is
  encoded verbatim with `output_policy: "refused"`. This extends, and uses the
  same mechanism as, the `kliba` refusal already recorded for BPHS.
- **No occupational-caste assignment.** Saravali 26.43 makes the native a
  washerman, garland-maker or jeweller; 40.13 and 28.6 assign him a wife or a
  likeness "of the slaughterer people" (`vadhaki`); Brhajjataka XVIII.11
  assigns "the handicraft of men of low castes, such as shoe-making"; XVIII.14
  makes Venus in Aries a `sudra`. All refused, all retained.

## Conventions requiring disclosure

| Convention | Chosen | Alternatives |
|---|---|---|
| Ayanamsa | Lahiri (Chitrapaksha) | Fagan-Bradley, Krishnamurti, Raman, True Citra, True Revati |
| Houses | Whole sign | Sripati, equal-from-degree |
| Nodes | Mean | True |
| Dasha year length | 365.2425 days | 360-day savana year; sidereal year |
| Moolatrikona boundaries | **settled 2026-08-05 from the root text**: Sun Leo 0-20°, Moon Taurus 3-30° (0-3° being exaltation), Mars Aries 0-12°, Mercury Virgo 15-20° (0-15° exaltation), Jupiter Sagittarius 0-10°, Venus Libra 0-15°, Saturn Aquarius 0-20°; the remainder of each sign is own-sign | vary slightly by text. The arcs above are stated explicitly in the Subodhini commentary to uttara 2 sloka 8, graha by graha, as part of the saptavargaja-bala rule, and are encoded in `strength_rule_manifest.json` |
| Saptavargaja dignity weights | this recension: exaltation 100, moolatrikona 45, own 30, great friend 20, friend 15, neutral 10, enemy 4, great enemy 2 | the modern handbooks give 45/30/22.5/15/7.5/3.75/1.875 and no separate exaltation value. Recorded as printed, not normalised |
| Sadbala required minima | this recension: Sun/Mercury/Jupiter 6\|32 rupas, Moon/Venus 5\|53, Mars/Saturn 4\|13 — three classes, with per-component minima for sthana, dig, cheshta, kala and ayana | the handbooks give seven separate figures (Sun 5, Moon 6, Mars 5, Mercury 7, Jupiter 6.5, Venus 5.5, Saturn 5). Drik-bala has no minimum in either scheme, and this recension states the reason: it varies with place and is the signed term |
| Placement of ayana-bala | this recension groups it with **cheshta-bala** as the fourth bala (uttara 2 slokas 20-24) | the handbooks fold it into kala-bala. Consequence: this recension's kala-bala has four limbs, not six or seven |
| Paksha-bala for the Moon | not doubled | several handbooks double it |
| Ashtakavarga notation | *karana* = *bindu* = the **zero/blank**; *sthana* = *rekha* = the **scored point** (uttara 1 sloka 72) | much popular modern writing uses "bindu" for the scored point, i.e. inverted. This recension enumerates the blanks first and the marks second, so a careless reading builds every chart backwards |
| Shodasavarga vimsopaka weights | published as printed, and they do not close: the four explicit values plus half for each remaining varga sum to **18.5**, not 20 | either the scan has lost sloka 124's first pada or this printing is defective. Not patched |
| BPHS recension | 1899 Subodhini (Mumbai), purva-khanda, self-titled *Brhatparasarahorasaramsa* | Sharma and Santhanam recensions differ substantially in chapter count, order and content; the 1899 preface itself claims 100 adhyayas in two khandas and claims first printing. Any BPHS quotation must name which recension it came from |
| Graha drishti weighting | flat special aspects (Mars 4/7/8, Jupiter 5/7/9, Saturn 3/7/10) | BPHS adhyaya 4 grades every graha's glance on all seven of the 3rd, 4th, 5th, 7th, 8th, 9th and 10th, in quarters. The engine implements the flat rule; the root text does not teach it |
| Node dignities | engine's current scheme | BPHS adhyaya 36 slokas 35-36 give Rahu exalted in Taurus, moolatrikona Cancer, owning Gemini, Sagittarius, Virgo and Pisces (Ketu exalted in Scorpio). Recorded, not adopted |
| Saravali drishti-cell granularity | for Adhyayas 22 and 25-29 the encoded cell is keyed to the **owner** of the rasi, so both of a two-sign owner's rasis receive the same delineation | This is Kalyanavarma's own grouping, not an encoder's shortcut; Adhyaya 23 (the Moon) is keyed sign by sign instead. The two schemes sit in one book and the manifest flags which applies on every rule |
| Saravali Moon-dasha rasi expansion | where 40.11-13 name an owner ("a house of Mars", "a rasi of Venus") the encoder expanded to both of that owner's rasis | The expansion is the encoder's and is named as such in the rule's exceptions. Scorpio has no statement of its own and inherits the Mars cell |
| Brhajjataka rendering channel | Aiyar's 1905 English, graded B | The printed Devanagari of the 1905 edition is not in this OCR. The IAST mula quoted beside each cell comes from `sources/brhajj_u.txt` and is **not** collated against the print, which is why the grade is B and not A even though a Sanskrit text is shown |
| Relative-house reckoning | house from the Lagna only | house from the Moon (chandra lagna) and house from the Sun are both classically used (Sunapha/Anapha/Durudhara/Kemadruma, Kesari/Sakata, Adhama/Sama/Varishtha, the Sun-relative Vesi/Vaasi cluster, and the kendra-from-Moon branch of Neechabhanga Rajayoga all require one or the other) but neither is computed by `vedic.py` today |

## Current implementation gap

The shipped panel section covers items 1-5, 7, and 9 (partially). To reach a
defendable reading it needs, in order: **navamsha (6)**, antardasha (8), drishti
(11), then yogas (12) gated on 10 and 13.

As of 2026-08-02, a delineation-content layer for items 17-19 exists in
`delineation_rule_manifest.json` (18 rules, sourced from Phaladeepika), and a
second, larger layer for items 20-25 exists in `bphs_rule_manifest.json` (107
rules, 342 validation vectors, sourced from BPHS itself). A third and fourth
layer were added later the same day: `saravali_rule_manifest.json` (87 rules,
563 validation vectors, 563 delineation cells, read directly from the 1907
Devanagari) and `brhajjataka_delineation_rule_manifest.json` (8 rules, 85
vectors, English-mediated, grade B). **None of the four is wired into
`vedic.py` or the composer.**

That last sentence is now the binding constraint rather than a footnote. The
engine renders almost nothing not because the corpus is empty — it holds 645
rules across the whole multitradition set and 202 of them are Jyotisha
delineation — but because `vedic_report.py` reads exactly one file,
`delineation_rule_manifest.json`, and looks up exactly one shape,
`jyotisha.phaladeepika.08.planet_in_bhava.<graha>`. The Saravali manifest was
authored to that shape deliberately: `results_by_house` keyed by house number as
a string, `results_by_graha` keyed by the engine's own graha names. Wiring it is
a loader change, not a re-encoding. Two shapes are new and need a small reader
extension: `results_by_rasi` (keyed by English sign name) and the nested
condition maps used by the dasha gates.

The single largest change this pass makes is not a rule count. It is that
`src/engine/traditions/vedic_report.py` currently tells the reader, in its own
method notes, that *"Brhat Parasara Hora Sastra - the root text this system is
named for - is NOT the source of any delineation here. Its available scan is
unusable."* **The second half of that sentence is now false.** The scan is
usable; 107 rules were read out of it. The sentence must be rewritten before the
next reading ships, because as it stands it tells a Jyotishi something untrue
about why the root text is absent. The honest replacement is narrower: BPHS is
readable and encoded, but nothing from it is rendered yet, pending independent
Sanskrit review of the renderings and a composer wiring pass.

The remaining blockers, in order of how much they cost:

1. **Independent Sanskrit review.** Every one of the 107 renderings is graded
   `engine_translation_unreviewed`. Under `../DEFENSIBILITY.md` that is enough
   to *quote* from - original, rendering and citation are all published
   together - and not enough to *promote into a validated pack*. This is the
   gate, and it is a real one rather than a placeholder.
2. **Recension collation.** This recension is missing 12 of adhyaya 15's 144
   cells, and its adhyaya 13 lagna assignments disagree with the modern
   handbooks. Until it is collated verse-by-verse against the Sharma and
   Santhanam recensions, no reading may claim "BPHS says" without naming the
   recension - and this pack refuses to fill its own gaps from the others.
3. **Divisional charts (item 16).** Adhyaya 37's antardasha quality test and
   adhyaya 28's raja-yoga ladder both run on vargas beyond D9. Five of six
   bhukti tests and the entire raja-yoga ladder are unevaluable today.
4. **The drishti conflict (item 22).** The engine's flat special-aspect rule and
   the root text's graded scale cannot both be presented as Parasari. One of
   them has to be labelled a `configured_method` with the other named as its
   alternative.

5. **The second Saravali witness is not usable for collation.** Ten distinctive
   strings from passages encoded this pass were searched in
   `delineation_saravali_2015313760_djvu.txt`; nine returned nothing and the
   tenth returned a mangled context. No cross-witness disagreement could be
   established **in either direction**, so none is recorded — and the absence of
   recorded conflicts in `saravali_rule_manifest.json` must not be read as
   evidence that the witnesses agree. The 1907 edition's own printed pathabheda
   apparatus is carried where it bears on an encoded cell, but a within-edition
   apparatus is not a collation.
6. **Brhajjataka XIX is unmined and is the corpus's best collation target.**
   Varahamihira XIX and Kalyanavarma 23 state the *same* technique — the Moon in
   each rasi, modified by the graha aspecting it. Saravali 23 is encoded (84
   cells); Brhajjataka XIX is not. Mining it would give this tradition its first
   genuine two-author collation of a single delineation table, which is worth
   more to a hostile reader than another hundred uncollated cells.

Nothing in this pass changed the rendered panel. `customer_prediction` is false
on all 107 BPHS conclusions, on all 87 Saravali conclusions and on all 8
Brhajjataka conclusions, and no engine code reads any of the new manifests.

## Current implementation gap, restated 2026-08-05

The 2026-08-02 statement above is still true of the delineation layers and is
left standing. What changed on 2026-08-05 is that the gap is no longer *shaped*
the way that statement assumes. Until this pass the honest summary of this
tradition was: **thousands of delineation cells from four authors, and nothing to
weigh them with.** Two manifests now close that.

| New manifest | Rules | Vectors | Contents |
|---|---|---|---|
| `strength_rule_manifest.json` | 40 | 226 | Sadbala (uttara 2) and Ashtakavarga (uttara 1, purva 17-20), as computable procedures |
| `varga_rule_manifest.json` | 13 | 75 | D2, D3, D4, D7, D10, D12, D30, D60; the sixteen-varga scheme; varga-to-question map; tier names; vimsopaka bala |

Both were authored as **arithmetic**, not prose: every rule carries an explicit
formula, a unit table, the Devanagari it renders, and the source's own worked
figures as vectors. The unit is stated because it is a trap of its own — the
1899 printing writes every strength as a sexagesimal triple whose leading place
is the **rupa** (60 virupas), and an implementation that reads the leading place
as virupas is wrong by a factor of sixty throughout. That unit is not defined by
any sloka; it was established by recomputing the chapter's own tallies, and the
rule that records it is graded `C` and says so.

### What is computable today, with no new engine inputs

The engine already produces sidereal longitudes, rasi, degree-within-rasi,
houses, lordships, navamsa and dignities. On those alone the following run:

- **sthana-bala in full** — uccha, saptavargaja (for the vargas that exist),
  ojayugma, kendradi, drekkana
- **dig-bala in full**
- **naisargika-bala** (a constant table; needs no chart at all)
- **paksha-bala** (needs only the Sun-Moon elongation)
- **the gati-bala table** of cheshta-bala
- **all eight bhinnashtakavarga tables, the sarvashtakavarga, both sodhanas and
  all three pindas** — ashtakavarga is entirely whole-sign counting and needs
  nothing the engine lacks
- **D2, D3, D4, D7, D10, D12, D30 and D60**, and therefore the shadvarga and
  saptavarga **vimsopaka** schemes

### What is not computable, and exactly why

Stated per limb so the gap is visible rather than aggregated:

| Limb | Missing input |
|---|---|
| natonnata-bala | local sunrise/sunset; ishta-kala in ghatis; day and night length |
| tribhaga-bala | day and night length, to locate the birth in one of six parts |
| varsha/masa/dina/hora-bala | lords of the year, month, weekday and planetary hora |
| ayana-bala | the **sayana** (tropical) longitude and its bhuja. The ayanamsa is already known, so this is one addition away |
| cheshta-bala proper | **madhyama** (mean) longitude and **sighrocca**. The engine has true longitude and a retrogradation flag only |

Four of those five are clock-and-calendar facts, not astronomy the engine cannot
do. None is a source gap.

### The blockers that remain, in order of cost

1. **Independent Sanskrit review.** Unchanged, and it now gates 53 more rules.
   Under `../DEFENSIBILITY.md` an `engine_translation_unreviewed` rendering is
   enough to *quote* and not enough to *promote*. The arithmetic rules are the
   least exposed to this — a formula that reproduces the source's own printed
   answer is verified by the arithmetic itself — but the surrounding prose and
   the technical vocabulary still need a specialist.
2. **Recension collation.** Now sharper, because the divergences are numeric and
   therefore unmistakable: the saptavargaja series, the required minima, the
   Moon's paksha-bala, and the placement of ayana-bala all disagree with the
   modern handbooks. Until this recension is collated against Sharma and
   Santhanam, no reading may say "BPHS says a graha is strong above N."
3. **Composer and engine wiring.** Still zero. `vedic_report.py` reads exactly
   one manifest and one rule shape. The two new manifests were deliberately
   authored to be *loadable* — tables keyed by house number as a string, graha
   names matching the engine's own — but nothing loads them.
4. **The drishti conflict**, now doubled. Adhyaya 4 grades every glance in
   quarters; uttara 2 slokas 2-7 give the arithmetic behind that grading as a
   continuous six-case function of the arc. The engine's flat special-aspect rule
   is a third thing, and it is the only one of the three that this recension does
   not teach anywhere. One of them has to be labelled `configured_method`.
5. **Six vargas unmined, not blocked.** D16, D20, D24, D27, D40 and D45 are named
   at purva 3 slokas 52-54 and their computation rules sit in the unread stretches
   of the same chapter (slokas 66-76 and 79-87) in the same legible scan. Reading
   them completes the dasavarga and shodasavarga vimsopaka schemes. Calling this a
   blocker would be exactly the error this corpus has recorded six times before.
6. **Three ashtakavarga cells were settled by arithmetic rather than by ink** —
   Jupiter's ninth house and Venus's fourth and eighth. Each is named in
   `jyotisha.bphs.u01.bhinnashtakavarga.scan_damage_disclosure` with the reading
   that was taken and the reading that was rejected. A second witness would settle
   them; the row-sums make the risk small but not zero.

Nothing in this pass changed the rendered panel either. `customer_prediction` is
false on all 53 new conclusions, the kingship predicate of the varga tiers is
refused, and no engine code reads either new manifest.
