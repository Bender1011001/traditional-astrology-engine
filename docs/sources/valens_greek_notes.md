# Vettius Valens, *Anthologiae* — working notes from the Greek

**Source:** `tmp/acquire/pdfs/valens_anthologiae_kroll_1908_scan.pdf` (441 pages)
**Edition:** Wilhelm Kroll, *Vettii Valentis Anthologiarum Libri*, Berlin (Weidmann) 1908 — critical edition, Greek text with Latin apparatus criticus. Preface dated Guestfalorum, March 1908.
**Read from:** page images. **The OCR text of this scan is useless** — `valens_anthologiae_kroll_1908_djvu.txt` contains 1.1M characters and **zero Greek**; Google's OCR dropped the entire Greek body and kept only Kroll's Latin preface.
**Started:** 2026-08-08

---

## Why Valens

Valens (compiled c. 152–188 AD) is **the oldest surviving text that contains a complete, working method** — not merely doctrine, but doctrine plus the arithmetic plus roughly 130 worked example nativities. The older candidates all fail one test or another:

| Source | Date | Why not |
|---|---|---|
| Nechepso–Petosiris | c. 150–120 BC | **Lost.** Fragments only. Firmicus invokes them by name in his Book III proem. |
| Manilius | c. 10–20 AD | Survives complete, but has almost no planetary doctrine. You cannot read a chart from it. |
| Dorotheus | c. 75 AD | Older and near-complete, but the Greek is largely lost: Greek → Pahlavi → Arabic → English. Three removes. |
| Ptolemy | c. 150 AD | Survives complete in Greek, but he is a **deliberate reformer**: no Lots but Fortune, no Zodiacal Releasing, no exaltation degrees, reworked topical system. Complete transmission, incomplete system. |

Firmicus (*Mathesis*, c. 334, Latin) is the runner-up — later, but survives entire and in clean extracted text.

## Citation convention

Kroll cites by **printed page and line** (the index gives e.g. `56,16` = page 56, line 16). Use that form. **PDF page = printed page + 18** (printed p. 42 is PDF page 60).

## Reading method

`scripts/composite_pages.py` renders N book pages into one image at a fixed **per-page** pixel budget (~529×780). Cost is ~**550 tokens/page at any N** — packing more pages saves round-trips, not tokens, because cost scales with area. Use `--per-image 6` (2×3 grid) as the default sweep; it is the same cost as 4-up with a third fewer calls, and fully legible.

```bash
python scripts/composite_pages.py tmp/acquire/pdfs/valens_anthologiae_kroll_1908_scan.pdf OUTDIR --start 80 --count 6 --per-image 6
```

Reading images is about **1.8× cheaper than reading the same Greek as text** (Ancient Greek tokenizes at ~2 chars/token; a composite runs ~3.6).

**Known failure mode of the sweep:** the apparatus criticus sits at the legibility limit, and **spelled-out numerals are lost first** — I misread Aquarius's Venus bound because Valens writes **ἓξ** rather than ς′. Treat every degree count read at 6-up as provisional; re-render `--per-image 1` before asserting any number or relying on a variant.

## ⚠️ TRANSCRIPTION RULE — in force from 2026-08-09

**Transcribe the Greek verbatim as you read it, then translate. Do not extract-and-summarise.**

Everything read before 2026-08-09 was extracted, not transcribed: I kept the operative sentence and let the page go. That was a mistake — the translation work was being done anyway and thrown away, and roughly 250 pages now have my English without the Greek behind it.

**Output goes to `docs/sources/valens_translation.md`**, which is the durable artifact. This file (`valens_greek_notes.md`) stays as the working analysis — findings, engine implications, test cases. The translation file holds the text.

Every entry there is marked **[G]** Greek preserved · **[E]** my English only, Greek not kept · **[S]** substance only, not a rendering. **Never quote an [E] or [S] entry as though it were the Greek.** Re-read the page first; the page numbers are recorded for exactly that purpose.

**Do not reconstruct Greek from memory.** A fabricated line in a source file is worse than an admitted gap.

---

# ⭐ HOW TO DO A READING FROM THIS FILE

A fresh session with no context can work from here. Everything below is verified against the Greek and cross-checked against the engine on a real chart.

### Step 0 — the governing principle, before anything else
**Benefic and malefic are inputs, not verdicts.** Run the placement-and-sect test first (I.1 p.5; §"benefic and malefic are CONDITIONAL"). A malefic in its own place and in sect is *a giver of good things*. A benefic in the **2nd, 6th, 8th or 12th** is a **loss** — Valens says so in four separate chapters. Jupiter square the Sun is the cleanest proof: *"the good things of the star are pulled down and it falls into the opposite"* badly placed, *"glorious and acquisitive"* angular. Same planet, same aspect, opposite verdict.

### Step 1 — sect and the sect light
Sun above horizon = day. Sect: Sun/Jupiter/Saturn diurnal, Moon/Venus/Mars nocturnal, **Mercury by solar phase** — morning star diurnal, evening star nocturnal (Ptolemy I.7; Valens II.1 confirms Mercury common). Doubly attested; state it flatly.

### Step 2 — overall size of the life (II.22)
Six tests: luminaries in **busy signs** spear-borne by orientals with no malefic opposing → kingly; their lords angular; **prenatal syzygy or its lord** angular → fortunate; luminaries/most planets **under the earth** → notable and rich *but a bad end*; lords of **Fortune and Spirit** together with the ruler → brilliant; those lords **oriental, in own place, witnessed by the luminaries** → near kings or temples. "Busy degrees" are defined by arc, not whole sign (III.2).

### Step 3 — the life arc and its hinge (II.2)
Sect light → its triplicity → that triangle's **first ruler (early life)** and **second ruler (later life)**, hinge at the sign's ascensional time. Judge each for angular/succedent/cadent, oriental/occidental, own sign, and witnessing. **Angular or busy = brilliant; succedent = middling; cadent = low and unfortunate.** First badly / second well → early irregularity then effectiveness. First well / second badly → early success then being pulled down. Engine already returns these three rulers under `triplicity_periods`.

### Step 4 — the places
Use §II.5–II.15. Judge by **which planet is there, and where the lords of the Ascendant, Fortune and Spirit fall** — not by the house's topic label. Remember the four places where benefics are neutralised.

### Step 5 — the bounds
Every planet's Egyptian bound lord has a delineation (§I.3, all sixty). **Verified: our `EGYPTIAN_TERMS` matches Valens in all twelve signs.**

### Step 6 — topics
Marriage §II.37 (7th sign **plus Venus's condition, dispositor, witnesses**; note the Mars/Jupiter/Mercury escape clause). Children §II.39 (Mercury, Jupiter, Lot of Children — **never a bound**). Siblings §II.40. Aspect pairs §II.16.

### Rules for writing it
- Cite **page,line** (Kroll's system; **PDF page = printed page + 18**).
- Where two sources disagree, **show the fork** — never pick silently.
- Quote the **conditions**, not just the verdict. Valens attaches them everywhere; dropping them is not faithful transmission, it is quoting half a sentence.
- Second person throughout. **Never infer gender from a name.**
- **Do not use:** longevity/length-of-life (removed for failing 11 of 20 tested charts), and violent-death material (§II.41).

---

---

# Index capitum — the operational map

Transcribed from Kroll's own index (PDF pp. 12–15). This is the evidence that Valens covers a complete reading; every line is a chapter we can go read.

## Book I — foundations
| ch | Greek | English | page,line |
|---|---|---|---|
| 1 | Περὶ τῆς τῶν ἀστέρων φύσεως | The nature of the stars | 1,3 |
| 2 | Περὶ τῆς τῶν ιβ′ ζῳδίων φύσεως | The nature of the twelve signs | 5,22 |
| 3 | Περὶ ὁρίων | **The bounds** | 14,12 |
| 4 | Περὶ ὡροσκόπου | The Ascendant | 19,7 |
| 5 | Ὡροσκοπικῶν γνωμῶν | Ascensional rules | 20,30 |
| 6 | Περὶ μεσουρανήματος | The Midheaven | 22,28 |
| 7 | Περὶ ἀναρροπῆς τῶν ζῳδίων | Inclination of the signs | 23,16 |
| 8 | Περὶ ἀκουόντων καὶ βλεπόντων ζῳδίων | Hearing and seeing signs | 24,22 |
| 9 | Σύνοδος καὶ πανσέληνοι ἀπὸ χειρός | Conjunction and full moon, by hand | 25,11 |
| 10 | Περὶ ἑπταζώνου ἤτοι σαββατικῆς ἡμέρας | The seven-zone / weekday | 26,10 |
| 11 | Περὶ οἰκοδεσπότου ἔτους | **Lord of the year** | 27,1 |
| 12 | Περὶ ἀρρενικῶν καὶ θηλυκῶν μοιρῶν | Masculine and feminine degrees | 27,31 |
| 13 | Περὶ φωτισμῶν Σελήνης | Illuminations of the Moon | 28,6 |
| 14–20 | *(lunar and planetary computation by hand)* | | 28,20–37,10 |
| 21 | Περὶ συμπαρουσίας καὶ συγκράσεως | **Co-presence and mixture** | 37,11 |
| 22 | Περὶ σχηματισμῶν κατὰ πλείους | **Configurations of several planets** | 41,7 |
| 23 | Περὶ σπορᾶς | Conception | 50,5 |
| 24 | Περὶ ἑπταμήνων | Seven-month births | 53,5 |

## Book II — the places, the lots, and the topics of life
| ch | Greek | English | page,line |
|---|---|---|---|
| 1 | Περὶ τριγώνων | The triplicities | 54,4 |
| 2 | Τριγώνων διαιρέσεις καὶ οἰκοδεσποτεῖαι καὶ συνεργῶν καὶ αἱρέσεων… ἡμέρας καὶ νυκτός | **Triplicity rulers, co-workers, and sects by day and night** | 56,16 |
| 3 | Περὶ κλήρου τύχης καὶ οἰκοδεσπότου | **Lot of Fortune and its lord** | 59,19 |
| 4 | Περὶ τοῦ λαχόντος τὴν ὥραν ἢ τὸν κλῆρον ἀστέρος | The star allotted the hour or the lot | 60,5 |
| 5 | Κακοδαίμονος τόπος | **12th — Bad Daimon** | 62,8 |
| 6 | Ἀγαθοῦ δαίμονος τόπος | **11th — Good Daimon** | 62,18 |
| 7 | Θεοῦ Ἡλίου τόπος | **9th — place of the God/Sun** | 63,15 |
| 8 | Ὀγδόης τόπος, θανάτου | **8th — death** | 64,1 |
| 9 | Ὁ Δεικὸς τόπος | 7th | 64,24 |
| 10 | Ἕκτος τόπος, Ἄρεως | **6th — of Mars** | 65,18 |
| 11 | Πέμπτος τόπος | 5th | 66,8 |
| 12 | Τέταρτος, ὑπόγειον | 4th — subterranean | 67,1 |
| 13 | Τρίτος τόπος θεᾶς Σελήνης | **3rd — of the goddess Moon** | 67,12 |
| 14 | Δεύτερος τόπος καλεῖται Ἅιδου πύλη | **2nd — called the Gate of Hades** | 68,9 |
| 15 | Τόπων ὀνομασίαι ἐννέα | The nine names of the places | 69,11 |
| 16 | Τριγωνικὰ καὶ ἑξαγωνικὰ καὶ διαμετρικὰ σχήματα | **Trine, sextile and opposition figures** | 69,17 |
| 17 | Περὶ ὡροσκόπου τοῦ τῆς τύχης κλήρου | Ascendant of the Lot of Fortune | 79,7 |
| 18–20 | *(Fortune, Spirit, exaltations and eudaimonia)* | | 80,9–82,5 |
| 21 | Περὶ προειρημένων κεφαλαίων ὑποδείγματα | **Worked examples of the foregoing** | 83,9 |
| 22 | Περὶ ἐνδόξων καὶ ἐπισήμων γενέσεων… καὶ περὶ ἀδόξων | **Eminent vs obscure nativities** | 87,5 |
| 23–25 | Περὶ κλήρου δάνους / κλῆρος κλοπῆς / κλῆρος ἐνέδρας | Lots of loan, theft, ambush | 90,18–91,16 |
| 26 | Περὶ προκειμένων τόπων ὑποδείγματα | Worked examples | 91,17 |
| 27 | Περὶ χρόνων ἐπιμερισμοῦ καὶ ἀπράκτων καὶ ζωῆς | **Time-distribution, inactive periods, and life** | 94,16 |
| 28–29 | Περὶ ἀποδημίας (ἐκ τῶν Ἑρμίππου) | Travel abroad (from Hermippus) | 96,1 |
| 30 | Περὶ προτελευτῆς γονέων μεθ' ὑποδείγματος | **Which parent dies first, with example** | 101,1 |
| 31 | Περὶ γονέων ἐκ τῶν Τιμαίου | Parents, from Timaeus | 102,19 |
| 32 | Περὶ ὀρφανίας πατέρων | Orphanhood | 103,30 |
| 33 | Περὶ χωρισμοῦ γονέων | **Separation of parents** | 104,27 |
| 34 | Περὶ ἐλευθέρων καὶ δουλικῶν γενέσεων | Free and slave nativities | 105,32 |
| 35 | Σχήματα Σελήνης ια′ πρὸς ἀποτελεσμάτων δυνάμεις | **Eleven configurations of the Moon** | 106,26 |
| 36 | Περὶ οἴνους καὶ πάθους μεθ' ὑποδειγμάτων καθ' ἓν ἕκαστον ζῳδίων | Injury and affliction, sign by sign | 109,8 |
| 37 | Περὶ γάμου καὶ συναρμογῆς καὶ εὐπαθείας | **Marriage and union** | 114,19 |
| 38 | Ἄλλως περὶ γάμου μετὰ ὑποδείγματος | Marriage, otherwise, with example | 119,9 |
| 39 | Περὶ τεκνώσεως ἢ ἀτεκνίας | **Children or childlessness** | 122,9 |
| 40 | Περὶ ἀδελφῶν | **Siblings** | 123,6 |
| 41 | Περὶ βιαιοθανάτων μεθ' ὑποδείγματος | Violent death, with example | 128,25 |

## Book III — length of life and the timing apparatus
| ch | Greek | English | page,line |
|---|---|---|---|
| 1 | Περὶ ἐπικρατήσεως | **Epikratesis (prorogation / rulership of life)** | 132,3 |
| 2 | Περὶ μοιρῶν ἐπισήμων τῶν κέντρων | Notable degrees of the angles | 134,22 |
| 3 | Περὶ ἀφέσεως | **Aphesis (releasing)** | 136,1 |
| 4 | Περὶ ἀνέμων τῶν ἀστέρων καὶ τῶν ὑψωμάτων καὶ βαθμῶν | Winds, exaltations, degrees | 140,4 |
| 5 | Περὶ αἱρέσεως τῶν ἀστέρων | **Sect of the stars** | 141,16 |
| 6 | Περὶ προκειμένων κεφαλαίων ὑποδείγματα | Worked examples | 141,27 |
| 7 | Ἄλλως περὶ ἐχθρῶν τόπων καὶ αἱρέσεων ἐκ τῶν Κριτοδήμου | Hostile places and sects, from **Critodemus** | 142,21 |
| 8 | Περὶ ἐχθρῶν ἀστέρων καὶ κλιμακτηρικῶν τόπων… Κριτοδήμου | Hostile stars and climacteric places, Critodemus | 143,5 |
| 9 | Περὶ ἀνέμων καὶ τροπῶν | Winds and turnings | 144,13 |
| 10 | Ἐκ τῶν Βάλεντος περὶ ἐμβόλου κλήρου καὶ χρόνων ζωῆς | **Lot of the ἔμβολος and the times of life** | 145,28 |
| 11 | Περὶ κλιμακτῆρος ἑβδομαδικῆς καὶ ἐννεαδικῆς ἀγωγῆς | **Climacterics: sevenfold and ninefold cycles** | 147,31 |

*(Index continues past Book III; remaining books to be transcribed when reached. Zodiacal Releasing sits in Books IV–VII.)*

---

## What this index already establishes

1. **Valens covers a complete reading.** Natures of planets and signs → bounds → angles → lots → the twelve places individually → aspects → then the life topics one by one (parents, siblings, marriage, children, travel, death, eminence) → then the whole timing apparatus (lord of the year, time-distribution, prorogation, releasing, climacterics). Nothing essential is missing.

2. **The places have names, not numbers.** 12th = Κακοδαίμων (Bad Daimon), 11th = Ἀγαθὸς Δαίμων (Good Daimon), 9th = θεοῦ/Ἡλίου τόπος (place of the God, of the Sun), 6th = Ἄρεως τόπος (place of Mars), 3rd = θεᾶς Σελήνης (of the goddess Moon), 2nd = **Ἅιδου πύλη, the Gate of Hades**. Our reading calls the 2nd "livelihood and movable resources" after Paulus. Valens names it the Gate of Hades. Worth showing the reader that the tradition holds both.

3. **Named earlier authorities inside Valens:** Critodemus (III.7, III.8), Hermippus (II.28), Timaeus (II.31). Valens is quoting sources older than himself, which is part of why he matters.

4. **Chapter II.2 is the source of the Dorothean triplicity table** — "divisions of the triangles and rulerships and **co-workers** and sects, day and night." The three-ruler (day / night / participating) scheme our `DOROTHEAN_TRIPLICITY` implements. This is the chapter to check it against.

---

# Findings by chapter

## I.1 — Περὶ τῆς τῶν ἀστέρων φύσεως (The nature of the stars), pp. 1–5

**Kroll heads the book "Desunt plura" — "much is missing."** The *Anthologiae* as transmitted begins mid-work; there is no surviving introduction. Any claim that Valens "begins by saying X" is false.

Each planet is given in a fixed six-part schema: **significations → parts of the body ruled → substances and crops ruled → diseases/injuries produced → sect → colour and taste.** The last is systematic and complete across all seven, and we have none of it.

### The seven, from Valens's own Greek

**☉ Sun** — ὁ παντεπόπτης, *the all-seeing*; fiery, "an intellectual light, an organ of psychic perception."
- *Signifies:* kingship, leadership, mind, practical wisdom, form, motion, height of fortune, the transaction of the gods, judgment, publicity, action, leadership of crowds, **father**, master, friendship, honoured persons, honours of images and statues and crowns, high-priesthoods of the fatherland.
- *Body:* head, sense-organs, **right eye**, sides, heart, the pneumatic (sensitive) motion, sinews.
- *Substance:* gold. *Crops:* wheat and barley.
- **Sect: diurnal. Colour: yellowish-brown. Taste: sharp.**

**☽ Moon** — "having come to be from the reflection of the solar light and possessing a **bastard light** (νόθον φῶς)."
- *Signifies:* life, body, **mother**, conception, form, face, sight, cohabitation or **lawful marriage**, nourishment, elder brother, housekeeping, queen, mistress, money, fortune, city, gathering of crowds, receipts, expenditures, household, ships, sojourning abroad, **wanderings — "for she does not provide straight paths, on account of Cancer."**
- *Body:* **left eye**, stomach, breasts, genitals, spleen, meninges, marrow — "whence she produces dropsical conditions."
- *Substance:* silver and glass.
- **Sect: nocturnal. Colour: green. Taste: salty.**

**♄ Saturn** — **ὁ Νεμέσεως ἀστήρ, the star of Nemesis.**
- *Makes people:* petty, malicious, full of cares, self-abasing, solitary, sullen, concealing their guile, austere, downcast, **having a hypocritical gaze**, squalid, **black-clothed**, importunate, gloomy-faced, ill-suffering.
- *Produces:* humiliations, sluggishness, inactivity, obstructions of what is undertaken, **long-lasting lawsuits**, overturnings of affairs, concealments, confinements, bonds, griefs, accusations, tears, **orphanhoods**, captivities, exposures of infants. Farmers — "on account of his ruling the earth" — renters of property, tax-collectors.
- *Body:* legs, knees, sinews, lymph, phlegm, bladder, kidneys, "the inward hidden parts."
- *Diseases:* those arising **from cold and moisture** — dropsy, pains of the sinews, gout, cough, dysentery, ruptures, spasms.
- *Also:* unmarried men, widowhoods, orphanhoods, **childlessness**. Deaths violent — **in water, by hanging, by bonds, or by dysentery**; and falls on the face.
- *Substance:* lead, wood, stones.
- **Sect: diurnal. Colour: castor-like. Taste: astringent.**

**♃ Jupiter**
- *Signifies:* childbearing, offspring, desire, loves, associations, acquaintanceships, **friendships of great men**, prosperity, salaries, great gifts, abundance of crops, justice, offices, citizenships, reputations, presidencies of temples, arbitration of judgments, trusts, **inheritances**, brotherhood, partnership, **adoption**, confirmation of good things, deliverance from evils, **release from bonds**, freedom, deposits, money, stewardships.
- *Body:* inner thighs, feet — "whence he furnishes running in athletic contests" — and inwardly the seed, the womb, the liver, the **right-hand parts**.
- *Substance:* tin.
- **Sect: diurnal. Colour: grey, rather white. Taste: sweet.**

**♂ Mars**
- *Signifies:* violences, wars, plunderings, outcries, insults, **adulteries**, removals of possessions, expulsions, exiles, estrangements of parents, captivities, corruptions of women, embryotomies, intimacies, marriages, removals of goods, falsehoods, empty hopes, violent thefts, robberies, severings of friends, anger, fighting, abuse, enmities, lawsuits. Brings **violent murders, cuttings and bloodlettings**, attacks of fevers, ulcerations, eruptions, burnings, bonds, tortures, perjury, wandering.
- *Also makes:* military commands and polemarchs, hoplites, leaderships, huntings and chases, **falls from a height or from four-footed beasts**.
- *Body:* head, seat, private parts; inwardly the blood, seminal passages, bile, excretion, hinder parts. "He has also the hard and the abrupt."
- *Substance:* **iron**; and adornment of garments **on account of Aries**; wine and pulses.
- **Sect: nocturnal. Colour: red. Taste: bitter.**

**♀ Venus** — "is desire and love."
- *Signifies:* **mother** and nourishment; priesthoods, gymnasiarchies, wearing of gold, wearing of crowns, gladnesses, friendships, companionships, purchases of ornament, transactions toward the good, **marriages**, clean arts, fine voices, music-making, sweet melodies, comeliness, painting, **mixtures and varieties of colours**, purple-dyeing and perfumery — and the masters of these; work in emerald, stone and ivory; gold-buying, gold-adorning, barbers, lovers of cleanliness. Market-inspectorships, measures, weights, trade, workshops, givings, takings, laughter, cheerfulness, ornament, hunting from wet places. Benefits and exceptional reputations **from royal or household women**.
- *Body:* neck, face, lips, smell, and the **front parts from foot to head**; the organs of intercourse; inwardly the lung.
- *Substance:* precious stones and varied ornament. *Crops:* the olive.
- **Sect: nocturnal. Colour: white. Taste: most oily.**

**☿ Mercury**
- *Signifies:* education, letters, examination, reason, **brotherhood**, interpretation, heraldry, numbers, reckoning, geometry, commerce, youth, games, **theft**, community, message, service, gain, discovery, following, athletics, wrestling, voice-training, sealing, sending letters, weighing, **testing money**, hearing, "being various."
- "He is **giver both of understanding and of practical wisdom**, lord of **brothers and of younger children**, and maker of every market and banking art."
- *Professions:* temple-builders, modellers, statue-makers, **doctors**, grammarians, lawyers, orators, philosophers, architects, musicians, diviners, sacrificers, bird-watchers, **dream-interpreters**, plaiters, weavers.
- *Body:* hands, shoulders, fingers, joints, belly, hearing, artery, intestines, tongue.

### Findings against our engine

1. **Sect assignments match Ptolemy exactly** — Sun/Jupiter/Saturn diurnal, Moon/Venus/Mars nocturnal. Two independent 2nd-century sources agree. This is now doubly attested and can be stated flatly.
2. **Colour and taste are a complete, systematic attribute set we do not carry at all.** Seven planets, both attributes, no gaps. Whether it belongs in a customer reading is a judgment call, but it is unambiguously part of the doctrine.
3. **The mother has two significators.** The Moon signifies μητέρα, *and* Venus "signifies mother and nourishment." Our engine treats maternal significators more narrowly. Valens doubles them in the oldest source we have.
4. **Siblings have three.** Moon (elder brother), Jupiter (brotherhood), Mercury (lord of brothers) — and Mercury also of *younger* children. Sibling questions should weigh all three, not one.
5. **Right/left is assigned.** Sun rules the **right** eye, Moon the **left**; Jupiter rules the **right-hand parts**. Specific and checkable, and absent from our output.
6. **Saturn's diseases are derived, not listed arbitrarily** — "such injuries as arise from cold and moisture," which follows directly from his nature in Ptolemy I.4. The two texts interlock.
7. **Valens explains his own reasoning in passing** — the Moon gives wanderings "on account of Cancer"; Mars rules garment-ornament "on account of Aries"; Saturn makes farmers "on account of his ruling the earth." These are derivations, not assertions, and they are exactly the material the source-attributed format needs.

---

## ⭐ I.1 end, p. 5 — benefic and malefic are CONDITIONAL, not fixed

This is the single most consequential sentence read so far, and it belongs at the front of any reading we produce.

> Οἱ μὲν οὖν **ἀγαθοποιοὶ** ἐπιτόπως καὶ καλῶς κείμενοι τὰ ἴδια ἀποτελοῦσι κατά τε τὴν ἰδίαν καὶ τὴν τοῦ ζῳδίου φύσιν… **παραπεπτωκότες δὲ ἐναντιωμάτων εἰσὶ δηλωτικοί**· ὁμοίως δὲ καὶ οἱ **κακοποιοὶ** χρηματίζοντες ἐπιτόπως καὶ τῆς αἱρέσεως **ἀγαθῶν δοτῆρες καὶ μειζόνων τάξεων καὶ προκοπῶν δηλωτικοί**, ἀχρημάτιστοι δὲ ἐκπτώσεις καὶ καταιτιασμοὺς ἀποτελοῦσι.

> *The **benefics**, well placed and in their proper places, accomplish their own effects according to their own nature and the nature of the sign, the testimony or co-presence of each star being mixed in. **But when fallen, they are indicative of oppositions.** Likewise also **the malefics**: when transacting in their proper places and of the sect, they are **givers of good things, and indicative of greater rank and of advancement**; but when not transacting, they accomplish falls and accusations.*

**A malefic in its proper place and in sect is a giver of good things.** A benefic badly placed indicates adversity. The labels name a planet's raw quality, not its verdict in a chart — placement and sect decide the verdict.

This is stated flatly in our oldest complete working source, c. 165 AD. It is not a modern softening, and it is not the later Rhetorius "nominal categories" idea — it precedes that by four centuries.

**Consequence for the product:** our reading treats Saturn and Mars as difficulty by default and sect as a modifier applied afterward. Valens has it the other way round: the placement-and-sect test decides, and the malefic label is only the starting material. Every paragraph that reads "Saturn afflicts X" needs to be checkable against "is Saturn in his proper place and in sect here?" — and where he is, the tradition's own answer is advancement, not damage.

---

## I.1 p. 5 — the technical aspect vocabulary, and each planet's abstract domain

> Each star is lord of its own substance in relation to the cosmos, with respect to **sympathy and antipathy and mutual affection**, and to their blendings with one another — by **application (συναφή)** and **separation (ἀπόρροια)**, and **overcoming (καθυπερτέρησις)**, or also **enclosure (ἐμπερίσχεσις)** and **spear-bearing (δορυφορία)** and **hurling of rays (ἀκτινοβολία)**, and the addressing of the lords.
>
> The **Moon** is lord of forethought; the **Sun** of radiance; **Saturn** of ignorance and necessity; **Jupiter** of reputation and crowns and eagerness; **Mars** of action and toil; **Venus** of love and desire and beauty; **Mercury** of law and custom and trust.

Two things worth having:

- **The named configuration operations — checked, and we have all six.** `src/engine/kakosis.py` implements Overcoming (labelled *Kathuperteresis* in its own comments), Besiegement, Enclosure, Striking with a Ray (*Aktinobolia*), Adherence and Opposition; application/separation and doryphory are elsewhere in the engine. Valens's list at 5,~13 is fully covered. **No gap here** — recorded because an earlier draft of this note wrongly flagged one.
- **A one-word essence for each planet** that is not a list of professions. "Saturn is lord of ignorance and necessity" and "Mars of action and toil" are far better opening lines for a planet's paragraph than any modern keyword set, and they are Valens's own.

---

## I.2 — Περὶ τῆς τῶν ιβ′ ζῳδίων φύσεως (The nature of the twelve signs), pp. 5–14

Each sign carries a large fixed attribute set, then a character delineation ("those born in it will be…"), then **chorography** (the regions of the earth it governs, part by part), then the **paranatellonta** (stars co-rising and co-setting north and south).

Attributes used, from Aries and Gemini as samples: house of ―, gender, **tropical / solid / two-bodied**, terrestrial or watery or airy or fiery, commanding, free / servile / "slave-free", **upward- or downward-tending**, **half-voiced / well-voiced / voiceless**, fertile or barren or "few-offspring", changeable, public, political, administrative, **disjunct (ἀσύνδετον)**, **eclipsic**.

- **Aries** — house of Mars; masculine, tropical, terrestrial, commanding, fiery, free, upward-tending, half-voiced, good, changeable, administrative, public, political, few-offspring, "orderly midheaven and cause of reputation." Natives: brilliant, notable, commanding, just, hating wickedness, free, bold in judgment, boastful, great-souled, **unstable, irregular**, high-necked, threatening. Chorography: Media at the head, Babylonia at the breast, Scythia on the right, Cyprus at the Pleiades, Arabia on the left, Persia and the Caucasus under the shoulders.
- **Gemini** — house of Mercury; masculine, two-bodied, well-voiced, upward-tending, airy, **feminized**, slave-free, barren, public. Natives: lovers of learning, practising letters and education, poetic, music-loving, voice-trainers, quick-witted, undertaking trusts; also mixed, commercial, meddlesome, **initiates of hidden things**.
- **Cancer** — house of the Moon; feminine, tropical, **ὡροσκόπος κόσμου, "Ascendant of the cosmos"**, servile, downward-tending, voiceless, watery, good. (The Thema Mundi reference — it matches Firmicus's *Thema Mundi* in *Mathesis* III.1, where the Moon is placed in Cancer 15°.)

**Findings:** the voice attribute (half-voiced / well-voiced / voiceless) and the upward/downward-tending axis are systematic across all twelve and we carry neither. The chorography is complete and is the ancient basis of astrological geography. **Cancer as Ascendant of the cosmos** is a doctrinal anchor shared with Firmicus — two independent sources, one Greek and one Latin, agreeing on the world-horoscope.

### ⭐ The four angles of the Thema Mundi are embedded in the sign descriptions

Read across the chapter, Valens names all four world-horoscope angles as attributes of individual signs. He never states the Thema Mundi as such — it is distributed through the sign list, which is why it is easy to miss:

| Sign | Valens's phrase | Angle |
|---|---|---|
| **Cancer** | ὡροσκόπος κόσμου | Ascendant of the cosmos |
| **Libra** | ὑπόγειον κόσμου | IC of the cosmos |
| **Capricorn** | δύσις κόσμου | Descendant of the cosmos |
| **Aries** | κόσμιον μεσουράνημα καὶ δόξης αἴτιον | Midheaven of the cosmos, and cause of reputation |

Internally consistent — whole-sign from Cancer puts Libra 4th, Capricorn 7th, Aries 10th. And it matches **Firmicus's *Thema Mundi*** (*Mathesis* III.1, Latin, read earlier today), which places the Moon in Cancer 15° and the Sun in Leo 15°. Two independent sources, one Greek and one Latin, on the same world-horoscope.

### The signs, pp. 8–12

- **Cancer** — changeable, public, crowd-related, political, many-offspring, amphibious. Natives reputation-loving, theatrical, pleasure-loving, fond of company; **"unstable in judgment, saying one thing and thinking another,"** not staying in one occupation or at most two, given to wanderings and sojourns abroad.
- **Leo** — house of the Sun; masculine, free, fiery, intellectual, **kingly**, seated, upward-tending, solid, commanding, prone to anger. Natives notable, just, hating wickedness, insubordinate, **hating flattery**, beneficent. **"And if the ruler happens to be angular, or with benefics, they become brilliant, renowned, tyrannical, kingly."**
- **Virgo** — house of Mercury; feminine, winged, human-formed, delicate, **"in figure the form of Justice (Δίκη)"**, two-bodied, barren, downward-tending, earthy, half-voiced and voiceless, workshop-related. Natives good, simple, mystical, full of cares, managers of others' property, trustworthy, good stewards, **secretaries advanced from words or reckonings**, initiates of hidden things; **spending in their first years, more prosperous in their middle years**.
- **Libra** — house of Venus; masculine, tropical, human-formed, feminized, voiced, **diminishing of possessions**, presiding over crops, wine, oil, crowns, perfumes. Natives good and just **but envious**, desirers of others' goods; **losing what they first acquired and coming to later gains**; presiding over measures, weights, or plenty.
- **Scorpio** — house of Mars; feminine, solid, watery, many-seeded, corrupting, voiceless, servile, unchanging, **taking away possessions**. Natives guileful, wicked, rapacious, murderous, traitors, secret plotters, thieves.
- **Sagittarius** — house of Jupiter; masculine, fiery, voiced, **"moist because of Argo"**, winged, two-bodied, **enigmatic**, commanding, kingly. Natives good, just, great-souled, generous, brother-loving; **diminishing what they first acquired, then acquiring again**, overcoming enemies; **"weaving matters enigmatically."**
- **Capricorn** — house of Saturn; feminine, tropical, earthy, sterile, chilled, voiceless, servile, **cause of evils**, hump-shaped, **lame**, indicative of toils and labours, stone-cutting, agricultural. Natives bad, **"good and simple by hypocrisy,"** laborious, sleepless, plotters of great works, liars, blameworthy.
- **Aquarius** — masculine, solid, human-shaped, silver-loving, sterile, very cold, free, feminized, unchanging, **bad**, cause of toils through injustice or of burdens and hard labour, industrious, public. Natives envious, hating their own, single-minded, sullen, guileful, misanthropic, godless, accusers, traitors.

### Three findings from the sign chapter

1. **The delineations are brutally blunt.** Scorpio natives are "murderous, traitors, thieves"; Capricorn "bad, liars, shameful"; Aquarius "misanthropic, godless, traitors." This is the same problem as Firmicus's "destroyer of wife and children." **It cannot be transmitted flat**, and the reason is doctrinal, not squeamish — see the next point.

2. **Valens attaches conditionals that decide the outcome.** Leo's natives are kingly *"if the ruler happens to be angular, or with benefics."* The sign gives a substrate; the **ruler's condition** decides what it becomes. Quoting the substrate without the condition is not faithful transmission — it is quoting half a sentence. This is the same structure as the conditional benefic/malefic rule at 5,~5, and our engine already computes both halves.

3. **Valens repeatedly gives a temporal arc, not a static trait.** Virgo: poor early, prosperous in middle life. Libra: loses what it first acquired, gains later. Sagittarius: diminishes, then acquires again. These are **timing statements embedded in the sign delineation** — closer to what the customer actually asked for than anything in our current output, and available from the natal sign alone.

---

## ⭐ I.3 — Περὶ ὁρίων (On the bounds), pp. 14–19

**This chapter is not a table. It is a delineation of what each of the sixty bounds *means*.** We ship the degree boundaries and have never had a word of the meaning. This is the single largest block of usable, unencumbered delineation found so far.

**Status: complete. All 60 are translated** (the last 19 were read on 2026-08-10 from printed pp. 15–19). The chapter's closing sentence, p. 19,4–7, governs every one of them: the degrees were set out *alone, for teaching*, and **the domicile lord lying over them decides whether what the degree carries comes out base or good**. Shipped as `BOUND_QUALIFIER` and asserted on every emitted bound item.

### The boundaries are the Egyptian set — verified

Checked digit by digit against `EGYPTIAN_TERMS`:

| Sign | Valens | Matches our table |
|---|---|---|
| Aries | Jup 6, Ven 6, Merc 8, Mars 5, Sat 5 | ✅ |
| Taurus | Ven 8, Merc 6, Jup 8, Sat 5, Mars 3 | ✅ |
| Gemini | Merc 6, Jup 6, Ven 5, Mars 7, Sat 6 | ✅ |
| Cancer | Mars 7, Ven 6, Merc 6, Jup 7, Sat 4 | ✅ |
| Leo | Jup 6, Ven 5, Sat 7, Merc 6, Mars 6 | ✅ |
| Scorpio | Mars 7, Ven 4, … | ✅ |
| Sagittarius | Jup 12, Ven 5, Merc 4, Sat 5, Mars 4 | ✅ |
| Capricorn | Merc 7, Jup 7, Ven 8, Sat 4, Mars 4 | ✅ |
| Pisces | Ven 12, Jup 4, Merc 3, Mars 9, Sat 2 | ✅ |

**Libra — resolved by the apparatus.** Kroll's text reads Sat 6, Merc 5, Jup 8, Ven 7, Mars 4, which contradicts our table. The apparatus at 16,18 settles it: *"ceteri Mercurio VIII, Iovi VII, Veneri VII, Marti II partes dant"* — **the other witnesses give Merc 8, Jup 7, Ven 7, Mars 2**, which is our table exactly. This manuscript is the outlier and Kroll flags it. **No defect in our data.**

**Aquarius — verified at 1-up: Merc 7, Ven 6, Jup 7, Mars 5, Sat 5. ✅ matches our table.** My 4-up reading was wrong: Valens writes the Venus figure as the **word ἓξ** ("six") rather than the numeral ς′, and at reduced resolution I misread it as ιβ′. Worth recording as a known failure mode of the 4-up sweep — **spelled-out numerals are the thing it loses first**, and any bound or degree count read at 4-up should be treated as provisional until confirmed.

So **all twelve signs are now verified against `EGYPTIAN_TERMS`, with no discrepancy.** The one apparent conflict (Libra) is a manuscript outlier that Kroll himself flags.

Aquarius delineations — Merc 7: *of the rich and treasure-loving, gladly hoarding; intelligent, legal, making everything exact, commanding, small-souled, full of cares, loving education and every skill, administrative, economical, philanthropic.* Ven 6: *well-loved, god-fearing, **prospering without toil**, suddenly-fortunate, well-off, seafaring; many-seeded degrees — and it happens that one born under them consorts with old women, or with the injured, or with eunuchs.* Jup 7: *fortunate, petty, secretive, unambitious, unmanifest, good-childed, unbrotherly.* Mars 5: *injurious especially about the inward parts, busied with lawsuits; of wicked, feeble and dissolute men — but quick to attempt evils.* Sat 5: *sterile, moist, ill-born, injurious — especially about the meninges, the inward parts, dropsies and spasms; scarce, few-brothered, few-childed, envious, **at the end not fortunate**.*

### The delineations

Each bound carries a character. Sampling the ones read in full:

**Aries** — Jup 6: *gracious, robust, much-crowned, benefic.* Ven 6: *cheerful, skilled in art, distinguished, complete, clean, of good complexion.* Merc 8: *changeable and well-natured, windy, hail-bringing, thundering, lightning-hurling.* Mars 5: *corrupting, fiery, unstable, manly; of malefactors and the rash.* Sat 5: *very cold, sterile, envious.*

**Taurus** — Ven 8: *many-seeded, many-offspring, healthy, industrious, rather drunken.* Merc 6: *intelligent, prudent — but malefactors, few-seeded, evil-natured, death-producing.* Jup 8: *great-minded, manly, ruling, beneficent, great-souled, gracious.* Sat 5: *barren, sterile, eunuch-like, vagabond, blameworthy, toilsome.* Mars 3: *masculine, tyrannical, fiery, harsh, murderous, temple-robbing, utterly wicked — **yet not undistinguished**, but corrupting and not long-lived.*

**Gemini** — Merc 6: *gracious, well-set, intelligent, of many arts, scientific, practical, celebrated.* Jup 6: *contentious, gracious, calm, much-crowned, well-nourished, beneficent.* Ven 5: *flowery, musical, poetic, crowd-related, joyful.* Mars 7: *much-toiling, **brotherless**, few-childed, corrupting, raw, meddlesome.* Sat 6: *gracious, administrative, acquisitive, intellectual, much-known, notable, distinguished in understanding, most renowned.*

**Leo** — Jup 6: *experienced, masculine, imperial, wholly commanding, practical, eminent, **having nothing lowly***. Ven 5: *most well-tempered, relaxed, much-wise, enjoying.* Sat 7: *much-experienced, thoughtful, natural, well-natured, narrow, **mystical**, of many arts, seekers of hidden things — but sterile and barren.* Merc 6: *learned, crowd-related, heads of schools, incomparable, legal, intelligent.*

**Virgo** — Merc 7: *loftiest, administrative, much-wise, fair, **setting people over great affairs**, most intelligent, eminent — **but not fortunate in love-matters**; generally the whole of Virgo, but especially these degrees and those of Venus.*

**Sagittarius** — Jup 12: *of practical men; altogether various in every art and action, much-crowned, many-childed, many-brothered.* Ven 5: *well-tempered, renowned, victorious, crown-bearing, god-fearing, honoured by superiors in crowds and among leaders; good in children and siblings; **and to have several wives**.* Merc 4: *of lovers of learning, prolific writers, practical men, **begetting eternal things**, philosophers, eminent in knowledge and prudence — **when Mercury inclines**; but **when Mars**, lovers of arms and tacticians.* Sat 5: *sterilizing, injuring, very cold, harmful; of base men unfortunate in everything.* Mars 4: *very hot, danger-fleeing, insolent, shameless, corrupting — but having much movement in everything.* Closing line: ***"All the degrees in Sagittarius are various concerning all matters."***

**Capricorn** — Merc 7: *lively, satirical, mimicking, lying, whorish, procuring; desirers of others' goods and inglorious — yet quick in everything, gracious and well-off, **but not lofty**.* Jup 7: *"in the loftiest depression" — producing **both reputation and disrepute, wealth and poverty**, benefactions and theatrical displays; sterile, bearing females or monsters, small-seeming, private.* Ven 8: *of the profligate, lustful, downward-tending, undiscerning, blameworthy; changeable about their ends, not dying well, nor stable about marriages.* Sat 4: *austere, joyless, strange, ill-childed, ill-brothered, raw, corrupting, very cold, envious, hesitating, guileful.* Mars 4: *lofty, authoritative, tyrannical, investing everything with command; scarce in their own kin, destructive of people, travelling, quarrel-loving, contentious to the end.*

**Pisces** — Ven 12: *cheerful, much-crowned, downward-tending, enjoying, sweet-living, glad, charming, beloved; **advancing spontaneously**; workers for the gods.* Jup 4: *of lovers of learning and men of science, distinguished in crowds and prevailing in all discourse; many-brothered, many-childed.* Merc 3: *much-crowned, ruling, transacting for honoured men, merciful, god-loving, well-tempered.* Mars 9: *practical, **sea-fighters**.*

### Why this matters

1. **It is the missing half of a table we already ship.** Every chart we produce reports a bound lord. We say "Venus in Saturn's bound" and then say nothing about what that means. Valens says.
2. **The bound delineations are conditional too.** Sagittarius/Mercury is philosophers *"when Mercury inclines"* and soldiers *"when Mars"* — the same structure as the sign rulers and the benefic/malefic rule. Three times now, in three different chapters, Valens makes the outcome depend on a further condition the engine already computes.
3. **They are not uniformly grim.** Taurus/Mars is "murderous, temple-robbing, utterly wicked — **yet not undistinguished**." Capricorn/Jupiter produces "**both** reputation and disrepute, wealth **and** poverty." Valens repeatedly refuses a single verdict inside a single bound.
4. **Some are startlingly specific and checkable** — Sagittarius/Venus "to have several wives"; Virgo/Mercury "not fortunate in love-matters"; Gemini/Mars "brotherless"; Pisces/Mars "sea-fighters." These are the falsifiable-prediction material, and they come with a citation.

---

## I.5–I.10 — the computational chapters, pp. 20–26

Mostly hand-calculation superseded by the ephemeris, but four rules are doctrinally load-bearing.

**I.6 — the Midheaven is computed, not looked up.** *Taking from the setting degree, according to the **ascensions of the clima**, up to the opposite point, release the half of these from the western degree; wherever it falls, that is the Midheaven.*

### ⚠️ FINDING (2026-08-10): the 60-invariant does NOT hold astronomically

Implementing engine change #18 disproved the rule it was meant to assert.

Under exact spherical computation a sign and its opposite sum to between **55.8° and 64.4°**, never 60 except near the equinoxes — while all twelve still sum to exactly 360.

The reason is structural. Oblique ascension is `OA = RA − AD`, and `AD(λ+180) = −AD(λ)`, so in an opposite pair the ascensional-difference terms **cancel** and the sum reduces to `2 × (RA span of the sign)`. That equals 60 only where the RA span is exactly 30 — i.e. at the equinoctial points.

**Valens's 60 is a property of the ancient arithmetical rising-time schemes, which are linear by construction — not of the sky.** Measured at 38°N:

| Sign pair | Sum |
|---|---|
| Aries / Libra | 55.82 |
| Taurus / Scorpio | 59.82 |
| Gemini / Sagittarius | 64.36 |

### ✅ Confirmed from Valens's own table (2026-08-10)

**VIII.6, p.304** gives the numbers directly: *"let **Aries**, in the second clima, **ascend in 20** … since **Taurus ascends in 24**."* That is an arithmetic step of **4**. Extended and mirrored:

`20 · 24 · 28 · 32 · 36 · 40 | 40 · 36 · 32 · 28 · 24 · 20` — summing to **360**, with every opposite pair on **60 by construction**.

The invariant is an artifact of the progression. The disproof was derived from the spherical mathematics; **his own table confirms it independently.**

**Consequences, both real:**
1. **Never "fix" the engine's exact astronomy to match a schematic table.** Locked by `test_valens_sixty_invariant_is_schematic_not_astronomical`.
2. **Never mix Valens's tabulated ascensions with our computed ones in one calculation.** They are different models and disagree by up to ~4.4°. This bears on ZR period lengths, the aphesis conversion, and the II.2 life-arc hinge, all of which cite "the ascension of the sign."

**I.7 — ⭐ ascensional-time symmetry (as Valens states it).** *Since **Aries ascends in 20**, **Libra ascends in 40**, to the completion of **60**. For however much each sign ascends in, **the diametrically opposite sign takes up the remainder to 60**.*

A sign and its opposite always sum to **60 equinoctial times**. This is the invariant underneath ZR period lengths, the aphesis conversion, and the II.2 life-arc hinge ("the ascension of the sign"). **Worth adding as a test assertion** — any ascensional-time table should satisfy `asc(sign) + asc(opposite) == 60` for its clima.

**I.8 — ⭐ "hearing" and "seeing" signs are defined by ascensional times, not convention.** *Likewise concerning **hearing and seeing** signs, it is to be known **from the ascensions**. Pisces sees Taurus; for from Pisces the ascension in the 2nd clima is 160, and from Taurus 200 … and the ascension of the two together approaches 360.* Signs of **equal ascension** hear and see one another. Not decorative — II.6 uses the category ("in a hearing or seeing sign they furnish greater goods").

**I.9** — prenatal syzygy by hand: count from the solar degree to the lunar, find the twelfth-parts, run back to the solar degrees.

**I.10 — the planetary week.** *The **order of the stars according to the day** is: **Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn**.* Reckoned by subtracting sevens from the years **since Augustus** plus the days from **Thoth** to the birthday.

**Calendar note for anyone checking his worked examples:** Valens dates in the **Augustan era** with **Egyptian months** — Thoth, Mechir, Mesore recur throughout. His example charts cannot be verified without converting from that calendar first.

## ⚠️ I.11 — Περὶ οἰκοδεσπότου ἔτους: this "Lord of the Year" is NOT the profection lord, p. 27

> *If you wish to know the **lord of the year** in the same way: the complete years of **Augustus** 148, intercalary 36, and of **Thoth** 1, make 185; from these I **subtract 26 sevens**; 3 remain. These [count] **from the Sun** — **the year terminates at Mars**. When you have recognized the lord of the year, you will find the **lord of the month** likewise, and the **lord of the day**.*

**This is a calendrical/weekday reckoning**, continuous from the Augustan epoch — the same sevens-arithmetic as the weekday in I.10. It is **not** the annual profection. Valens gives profection separately at **IV.11** (age ÷ 12, remainder counts the sign), which is what our engine implements and cites to Paulus ch. 31.

**Do not conflate them.** Two distinct techniques share the phrase "lord of the year."

And Valens immediately objects to the universal form of it:

> *But **that those born in the same year should have obtained one and the same rulership does not seem to have reason**. Generally the ancients grasped the lord of the year from the new moon of **Thoth** (for from there they made the beginning of the year), but **more naturally from the rising of the Dog Star**.*

He is rejecting a year-lord shared by everyone born that year, and preferring a **Sirius-rising** epoch to the civil one. A doctrinal fork he flags himself.

## I.12 — masculine and feminine degrees, pp. 27–28

> *Of the **masculine** signs the **first 2½ degrees are masculine**, the next 2½ **feminine**; of the **feminine** signs the first 2½ **feminine**, the next masculine, the next feminine.*

Twelve alternating 2½° blocks per sign, phase set by the sign's own gender.

### ⚠️ DOCTRINAL FORK — this is not the table we ship

`src/engine/degrees.py:_MF` carries masculine/feminine degrees cited to **Lilly, *Christian Astrology* p.117 (1647)**, and Lilly's boundaries are **irregular**:

| | Valens I.12 (c. 165) | Lilly 1647 |
|---|---|---|
| Aries (masc.) | M 0–2½, F 2½–5, M 5–7½, F 7½–10 … regular alternation | M 0–8, F 8–9, M 9–15, F 15–22, M 22–30 |
| Taurus (fem.) | F 0–2½, M 2½–5, F 5–7½ … | F 0–5, M 5–11, F 11–17, M 17–21, F 21–24, M 24–30 |

**Two different systems, not a transcription error.** Valens states a *generative rule*; Lilly prints an *irregular table* with no evident pattern. Neither is a corruption of the other.

Our citation is honest (we attribute to Lilly, and it is Lilly's), but per the standing policy — *where authorities disagree, show the fork* — this belongs in `doctrinal_disagreements` rather than being shipped as though it were the tradition's single answer. **Engine change #17.**

## I.13–I.19 — lunar computation, pp. 28–32

Hours of lunar illumination by day of the month (I.13); the Moon's invisibility near conjunction (I.14); the **third-day, seventh-day and fortieth-day Moon** as critical points (I.15); finding the **ascending node** by hand (I.16–17).

**I.18 — the Moon's latitude by quadrant:** *From **Leo to Libra** the Moon descends northerly; from **Scorpio to Capricorn** descends southerly; from **Aquarius to Aries** ascends southerly; from **Taurus to Cancer** ascends northerly.*

**I.19 is titled Ἱππάρχειον — "the Hipparchan [method]"** for the Moon's position. Another named authority inside Valens, alongside Nechepso, Critodemus, Hermippus, Timaeus and Abraham.

## ⚠️ I.20 — the era tables, and evidence of later editing, pp. 33–36

Planetary position tables reckoned in regnal years from Augustus. The emperor list runs **Titus, Domitian, Trajan, Hadrian, Antoninus, Marcus Aurelius and Verus, Commodus, Severus, Alexander, Maximinus — and then Gordian and Philip**.

**Valens died c. 175. Philip the Arab reigned 244–249.** The list was therefore **extended by later hands**, and Kroll's apparatus flags the seam (*"auctor an librarius concinnitatem neglexerit incertum"* — whether the author or a copyist neglected the consistency is uncertain).

Direct evidence that the *Anthologiae* remained a **working book that later practitioners kept current** — which is why its transmission is uneven, and a reason to treat any calendrical apparatus in it as potentially post-Valens.

## ⭐ I.21 — Περὶ συμπαρουσίας καὶ συγκράσεως (Co-presence and mixture), pp. 37–41

**Every two-planet combination, delineated.** Distinct from II.16, which does the same by *specific aspect*; this chapter is co-presence and general blending.

- **Saturn + Jupiter** — *sympathetic to each other*: benefits **from the dead**, adoptions, lords of properties, guardians, **managers of others' affairs**, economical, lovers of learning.
- **Saturn + Mars** — ***enemies***, producers of oppositions and demolitions: factions among relatives, ill-will, enmities, deceits, plots, malefactions, judgments — ***except if, falling in their own or in busy signs and witnessed by benefics, they construct notable and brilliant nativities***; though uncertain as to happiness, with inglorious dangers or betrayals.
- **Saturn + Mercury** — *concordant and practical*; slanders on account of mystical matters, judgments, disturbances over writings and money — yet **much-experienced and much-learned**, prognosticators, lovers of learning, meddlesome, **initiates of hidden things**, pious toward the divine, **troubled in conscience**.
- **Saturn + Moon** — beneficial, acquisitive of properties, foundations, shipowning; **beneficent from deaths** — *especially when the Moon is making her course from the east and is witnessed by benefics*; but uncertain in possession, and sorrowful about the place of the wife through separations, hatreds and griefs.
- **Saturn + Sun** — concordant; *they give possessions and reputations **along with envy**, and take them away*; **secret enemies among greater persons**, threats, plots.
- **Jupiter + Sun** — brilliant, glorious, ruling, tyrannical, practical, **honoured and benefited by crowds**, well-off and rich.
- **Jupiter + Moon** — good and acquisitive, masters of ornament and of bodies, **notable offices**, benefited **by women and notable persons**, gifts and honours, treasurers or **lenders**, or **finders of treasure**.

**The Saturn + Mars entry is the strongest statement of rule #1 in the whole work.** The most hostile pair in the system produces *notable and brilliant nativities* when well placed and witnessed. If that pair can be redeemed by placement, nothing in the chart can be read from the planets' labels alone.

---

## ⭐ II.1 — Περὶ τριγώνων (The triplicities), pp. 54–56

Book II opens with the author's own name: **Οὐεττίου Οὐάλεντος Ἀντιοχέως** — *Vettius Valens of Antioch*.

### The complete three-ruler scheme — and it matches our Dorothean table exactly

> We have found the zodiacal circle arranged, according to difference and affinity, into **two sects, of the Sun and of the Moon, diurnal and nocturnal.**

| Triangle | Signs | Day | Night | Participating |
|---|---|---|---|---|
| Fire | Aries, Leo, Sagittarius | **Sun** | **Jupiter** | **Saturn** |
| Earth | Taurus, Virgo, Capricorn | **Venus** | **Moon** | **Mars** |
| Air | Gemini, Libra, Aquarius | **Saturn** | **Mercury** | **Jupiter** |
| Water | Cancer, Scorpio, Pisces | **Venus** | **Mars** | **Moon** |

**✅ Verified against `DOROTHEAN_TRIPLICITY` — all four rows, all three positions, exact match.** Our three-ruler table is correct and now has a primary-source Greek witness, not just an attribution to Dorotheus through the Arabic.

Valens gives reasons rather than a bare table: the Sun "fitted **Jupiter and Saturn** to his own sect as **co-workers and guardians** — Jupiter as an imitation of himself and successor of the kingship, a chooser of good things and **giver of reputation and of life**; and Saturn as a servant of evil and of oppositions and a **taker-away of times**." The Moon "had as co-sectarians Venus and Mars — Venus for benefiting and for **distributing reputations and times**, and Mars for injuring the nativities."

> Ἑρμῆς κοινὸς ὑπάρχων ἐξαιρέτως ταῖς δυσὶν αἱρέσεσιν ἐξυπηρετεῖ
> *Mercury, being **common**, serves both sects especially — toward the good or the base, according to the affinity and configuration of each star.*

### ⭐ A third witness on the water triplicity

This settles the fork harder than this morning's Ptolemy finding did. **Valens and Ptolemy independently agree that Venus rules the water triangle by day.**

| Source | Water, day | Water, night |
|---|---|---|
| **Ptolemy** (Greek, I.19) | **Venus** | Moon *(with Mars co-ruling both)* |
| **Valens** (Greek, II.1) | **Venus** | Mars *(Moon participating)* |
| Lilly (1647) | Mars | Mars |

Two independent 2nd-century Greek sources give **Venus by day**. Lilly is the outlier. Our `PTOLEMAIC_TRIPLICITY["Water"] = (VENUS, MOON)` and `DOROTHEAN_TRIPLICITY` water row are both correct, and Lilly is correctly quarantined in his own table.

---

## ⭐ II.2 — the procedure for judging a nativity's overall fortune, pp. 56–57

This is a complete, mechanical, citable algorithm, and the engine already computes every input.

> **For those born by DAY one must look at the SUN — in which triangle he is — and the ruler of it by preeminence, and that one's co-worker:** whether it is **angular, succedent or cadent**; **oriental or occidental**; or **in its own signs**; and **by whom it is witnessed, benefics or malefics** — and so make the pronouncements.
>
> For if it is on the Ascendant or the Midheaven, or in one of the other **busy (χρηματιστικά) signs**, they foreshow **fortunate and brilliant** nativities; if in the succedents, **middling**; in the cadents, **low and unfortunate**. And one must also look at the Sun himself, how he has fared and by whom he is witnessed.
>
> **For those born by NIGHT, look similarly at the MOON**, and the ruler by preeminence of her triangle and its co-ruler, as before.

**Procedure:** sect light → its triplicity → that triplicity's sect-appropriate ruler and co-worker → test each for angularity, solar phase, own sign, and witnessing → angular/busy = brilliant, succedent = middling, cadent = low.

### ⭐ And the two rulers divide the life in time

> **If the ruler by preeminence falls badly, but the one by succession is angular and well configured**, the native will in the **first years** have irregularities — until the ascension of the sign or its cyclical restoration — and **afterwards will be effective**, though he will pass life unstably and fearfully.
>
> **But if the leading ruler falls well and the following one badly**, having been brought out well in the **first years** he will **afterwards be pulled down**, from the time of the ascension of the sign in which the following ruler fell badly.

**First triplicity ruler governs early life; second governs later life; the hinge is the ascensional time of the sign.** This is the "two triplicity lords divide the life" doctrine, stated with its mechanism, in our oldest complete source.

**This is the closest thing yet to what the customer actually asked for** — a life arc with a turning point, derived mechanically, citable to page and line, and computable from data the engine already holds. It also explains the recurring "loses what he first acquired, gains later" motif in the sign delineations (Libra, Sagittarius, Virgo): those are the same doctrine expressed sign by sign.

---

---

## ⭐ II.5–II.10 — the places, pp. 62–65

**Valens's house doctrine is structurally unlike Paulus's, and the difference matters for us.** Paulus gives each place a *topic* ("the 2nd signifies livelihood and movable resources") — that is what our engine cites, 14 times. Valens gives **conditional outcomes**: what results when benefics land there, when malefics land there, and above all when **the lord of the Ascendant, the lord of the Lot of Fortune, or the lord of the Daimon** falls there.

His unit of judgment is not the house's topic. It is *which planet, in what condition, ruling what*.

**[12th] Κακοδαίμονος τόπος — place of the Bad Daimon**
> If the **malefics** happen to be here they produce **great injuries and falls**, especially if in their own faces. And if the **Lot of Fortune** is here and someone rules it, **there will never be any benefit, not even in the transits — for they became enemies from the beginning, from the birth.** Likewise the **benefics in this place do not distribute their own goods.** And when the three stars — **the lord of the Ascendant, of the Lot, and of the Daimon** — fall in this sign, they make people unfortunate and unseemly and lacking daily nourishment; and many will hold out their hands.

**[11th] Ἀγαθοῦ δαίμονος τόπος — place of the Good Daimon**
> If the **benefics** are here, well placed or in their own faces, they make people **conspicuous and rich from youth** — and more so if they behold the **Lot of Fortune** in trine and the Ascendant in sextile; in a hearing or seeing sign they furnish very many and greater goods.

**[9th] Θεοῦ Ἡλίου τόπος — place of the God, of the Sun; the pre-Midheaven**
> If the **benefics** are here and are allotted the Ascendant or Fortune, the native will be **blessed, pious, a prophet of a great god, and will be heard as a god.** … With only **Mercury** witnessing, they become **royal secretaries from middle age**. The **lord of this place well placed makes them effective**; badly placed, ineffective. A malefic present or opposed makes them ill-doing, or sterile, or childless.

**[8th] Ὄγδοος τόπος θανάτου — the eighth, of death**
> The **benefics present in this place are ineffective and weak, and do not distribute their own goods**; and if they also rule the Ascendant and the Lot, they turn out much more ineffective and irregular. If the **malefics** are present having ruled the Lot, the natives are **wanderers and lose whatever they acquire**.

**[6th] Ἕκτος τόπος Ἄρεως — the sixth, of Mars**
> If the **benefics** happen to be present here, the native **will lose whatever he acquires** and his substance will not remain with him; he will be diminished by penalties as he advances toward old age. The **Sun** present here and ruling the Lot of Fortune or the Ascendant makes the native **condemned by a great authority**.

### The finding: the bad places neutralise benefics

Stated three separate times, in three separate chapters:

| Place | Valens on benefics there |
|---|---|
| 6th | "the native will lose whatever he acquires" |
| 8th | "ineffective and weak, and do not distribute their own goods" |
| 12th | "do not distribute their own goods" |

This is the exact complement of the conditional rule at 5,~5 — *"the benefics, when fallen, are indicative of oppositions."* Valens states the principle once in Book I and then applies it place by place in Book II. **A benefic in the 6th, 8th or 12th is not a mitigation in this system; it is a loss.** Our reading treats benefics as favourable and their house placement as flavour. Valens inverts that.

### And the Lot of Fortune is a primary judging tool, not a decoration

In every one of these chapters the operative question is where the **lord of the Ascendant, the lord of the Lot of Fortune, and the lord of the Daimon** fall. Our reading computes Fortune and Spirit and reports their positions. Valens uses their **lords' placements** as the main instrument for judging the whole life. That is a different and much heavier use than we make of them.

---

## ⭐ II.3 — Περὶ κλήρου τύχης καὶ οἰκοδεσπότου (Lot of Fortune and its lord), pp. 59–60

> *Wishing more precisely to confirm the place concerning good fortune, [I go] further to the **Lot of Fortune, a most necessary and powerful place** — as **the king** also, beginning **in the 13th book**, showed mystically, saying: … For those born **by day** one must clearly count **from the Sun to the Moon, and again the same amount from the Ascendant**, and observe the resulting place — **which star's it is, and which or how many are upon it**, and the squares and trines. **For from this knowledge of the places you will judge the affairs of those born as manifest.***

**✅ Day formula confirmed: ASC + (Moon − Sun)** — matches our implementation. "The king" is **Nechepso**, the pseudonymous royal author, cited by book number — another lost source quoted inside Valens.

Note the emphasis: Fortune is not a point to report, it is a **place to judge** — which planet owns it, what sits on it, what aspects it.

## ⭐ II.4 — the planet that rules the Ascendant or the Lot, pp. 60–62

A delineation set keyed to **(planet, ruling ASC or Fortune, witnesses)** — directly usable, since the engine computes all three inputs.

- **Saturn** allotted the hour or ruling the Lot, **Mars not opposing** → *prospers in the action Saturn distributes*; **witnessed by Jupiter → doubly**; **by Venus → through a woman, or through training**; **but Mars with him or opposing → disturbances and oppositions**; **Mercury co-ruling → impeded in hearing**.
- **Jupiter** rising with the hour or the Lot → ***very fortunate from youth***; with Mars present or trine → *advances in brilliant military service*; Saturn added → *comes into positions of eminence*.
- **Sun** allotted the hour or Fortune and rising, in sympathy with Jupiter → fortunate.
- **Moon** allotted the hour or the Lot of Fortune → ***makes them great***, especially in her own triangle.
- **Venus** conjunct or square Fortune → *deemed worthy of great honour*.
- **Saturn** square or opposing the **Moon** in equal degrees → *the native will have interference with his nourishment and **will be cast out by his parents***.

Same structure throughout: a base verdict, then witnesses that double it, redirect it, or reverse it.

## II.11–II.14 — the remaining places, pp. 66–68

**[5th]** *If **benefics** are allotted the Lot or the Ascendant, the native **will be great, will lead crowds, and will lay down laws**.* Venus ruling the Ascendant or Lot, in her own face or place → well-propertied and honoured. But **Mars** so placed → *they rule all kinds of places; they become **either generals or tyrants**, and will be **lords of life and death** — not only of the least but of notable people.*

**[4th, ὑπόγειον]** *If **benefics** rule the Ascendant or Fortune, or are present, they will have their livelihood **in sacred things**; and ruling the archetypal Lot while under the earth, **they will receive oracles from daimones and apparitions of images**.* Mars there instead → life through evils, crisis, violent death. And: ***"this place produces benefactions after death, and legacies to one's own."***

**[3rd, of the goddess Moon]** *If the **Moon** is here having been allotted the Ascendant or the Lot, in her own face, the native will be great, will rule a city, command many, be listened to, and be lord of treasures. And if the **Sun** is co-present and she has made her rising — **a priest of a greatest goddess, or a priestess**, with an unhindered livelihood.*

**[2nd, Ἅιδου πύλη — the Gate of Hades]** ***In this sign the benefics will help nothing***, and the malefics produce sluggish, injured people ***unable to swim through life to the end***. With the Lot here and malefics ruling it or the Ascendant → *they become **guardians of the dead, passing their life outside the gate**.*

### Running total: benefics are neutralised in FOUR places
2nd (*"will help nothing"*), 6th (*"will lose whatever he acquires"*), 8th (*"ineffective and weak"*), 12th (*"do not distribute their own goods"*). Four separate chapters, same principle, all flowing from I.1 p.5.

---

## ⭐ II.15 — Τόπων ὀνομασίαι ἐννέα (The nine names of the places), p. 69

A complete topical assignment — **and it is not the same as Paulus's twelve places, which our engine cites 14 times.**

> *The **god** signifies concerning the **father**; the **goddess** concerning the **mother**; the **Good Daimon** concerning **children**; **Good Fortune** concerning **marriage**; the **Bad Daimon** concerning **sufferings**; **Bad Fortune** concerning **injuries**; the **Lot of Fortune and the Ascendant** concerning **life and livelihood**; the **Daimon** concerning **practical wisdom**; the **Midheaven** concerning **action**; **Eros** concerning **desire**; **Necessity** concerning **enemies**.*

Mapped to places: father → **9th**, mother → **3rd**, children → **11th**, marriage → **5th**, sufferings → **12th**, injuries → **6th**, life → **1st + Fortune**, action → **MC**.

**Handle carefully — this is a parallel scheme, not a replacement.** Valens himself says at II.37 that *"the place concerning marriage is naturally taken from the 7th sign."* So he holds both: the **7th sign** for marriage *and* **Good Fortune** for marriage. Some of these names are **lots** (Fortune, Daimon, Eros, Necessity) rather than houses. The honest reading is that Valens runs a lot-based topical layer alongside the sign-based one, and consults both. **Do not silently substitute this for Paulus — surface it as a fork.**

---

## II.16 — Τριγωνικαὶ καὶ ἑξαγωνικαὶ καὶ διαμετρικὰ σχήματα (aspect figures), pp. 69–79

Ten pages of **planet-pair aspect delineations**, conditioned on angularity and on which planet is on the Ascendant. Sample:

> ***Jupiter trine the Sun signifies great and glorious things.*** If the Sun is on the Ascendant, [it signifies] both for the **father** and for the nativity; if merely angular, for the father — renowned, but **less than the former**; toward the nativity nothing notable, **unless some other cause corrects it**. If **Saturn** is in left trine to the Sun on the Ascendant, much greater things of reputation — they become much-propertied, much-farming and rich.

Note again the structure: the same aspect gives a **different verdict depending on angularity**, and Valens writes in the escape clause explicitly — *"unless some other cause corrects it."*

Further pairs read (pp. 70–75):

- **Mars opposing the Sun**, with Jupiter and Saturn in right trine to the Sun → *the native comes to be in greatnesses and reputations of crowds.* (A malefic opposition producing eminence — rule #1 again.)
- **Venus sextile the Sun, oriental** → *a beneficial and notable father and native; and if the figure falls on the Good Daimon or Good Fortune, he will be deemed worthy of **purple and gold-wearing by a woman**.*
- **Saturn square the Sun from the left** → harms the common livelihood while the father still lives, especially in feminine signs. ***If opposition, much worse*** — betrayed by his own.
- **Mars square the Sun** → bad for father and native; injuries and sufferings.
- ***Jupiter square the Sun*** in inglorious degrees or signs *is unpleasant; for **the good things of the star are pulled down and it falls into the opposite**.* But in glorious signs, **especially angular**, glorious and acquisitive. **Jupiter opposing the Sun is worse still** — the goods are extinguished and they meet opposition from those in authority.
- **Moon trine Mercury**, diurnal, Mercury oriental → inventive, well-natured; in a more glorious nativity, **royal secretaries, rulers of cities, orators, geometers**. Occidental and nocturnal instead → **various philosophers and partakers of mysteries**.
- ***Venus square Saturn*** → *unlaughing, having stern brows, **harder toward love-matters, not much-sharing (οὐ πολυκοίνους)*** — but mingling with older women; some suffer through brothers or guardians.

**Jupiter square the Sun is the clearest single proof of rule #1 in the whole work**: Valens says outright that a benefic's goods are *"pulled down and fall into the opposite"* when badly placed, and are glorious when angular. Same planet, same aspect, opposite verdict, decided by placement.

**pp. 76–79 of this chapter not yet extracted.**

---

## ⭐⭐ II.17 — the Lot of Fortune is a SECOND ASCENDANT, p. 79

> *Before all one must precisely establish the **Lot of Fortune** and look at **what part of the cosmos it fell into** — angles, succedents, or cadents. Likewise seek **its lord**: if it is rising, diurnal, or in some other **busy** sign, witnessed by Sun and Moon and the benefics, it will make the native **brilliant, notable, fortunate**.*
>
> ***For the Lot itself takes up the power of the ASCENDANT and of LIFE; the tenth from it, of MIDHEAVEN and REPUTATION; the seventh, of the setting; the fourth, of the subterranean. And the remaining places will take up the power of the twelve topical positions.***
>
> *For some mystically posit **the general Ascendant and its squares as the COSMIC angles**, and **the Lot and its squares as the GENETHLIACAL angles**.*

**A complete second twelve-place system, counted from Fortune**, with its own angles. Not a footnote — Valens says "before all," and the derived Midheaven is used operationally in II.21 ("Saturn and Mars culminating, or succedent to **the Midheaven of the Lot**… are indicative of downfall").

### ⚠️ Engine: we compute this and never use it

`src/engine/topical.py:443` already emits **`places_from_fortune`**, and `forensic_engine.py:1347` already documents the ZR split as *"Lot of Spirit (action, career, eminence) and the Lot of Fortune (body, circumstance)"* — someone had this right.

**But neither `places_from_fortune` nor the Fortune/Spirit distinction appears anywhere in `reading_composer.py` or `reading_evidence.py`.** The layer is computed, carried in the analysis payload, and **never reaches the reader**. This is the "loading is not firing" pattern: the rule pack loads and fires nothing.

That makes engine change #13 larger than first stated — not "add a sentence of explanation," but **surface an entire computed layer that Valens says to consult "before all."***

## ⭐ II.18 — the Lot of Exaltation, p. 80

> *We ourselves also found a certain **mystical place from experience**: to take, **by day, from the natal Sun to ARIES** (which is his exaltation), and **by night from the Moon to TAURUS**, and the same **from the Ascendant**; and wherever it terminates, **look at the place and its lord**.*

Day: Sun → Aries, projected from the Ascendant. Night: Moon → Taurus.

**✅ We carry it.** `src/engine/lots.py:141` — *"Exaltation: Distance from exaltation degree (19 Ari / 3 Tau)"*, with the day/night branch. Matches Valens II.18 exactly. Previously an unattributed extra beyond the seven Hermetic lots; **now sourced to Valens II.18, 80,9**.

## ⭐ II.19 — what Fortune and Spirit each govern, p. 81

> *Concerning the undertakings of actions and their changes, both the **Lot of Fortune** and the **Daimon** take up much power. For **[Fortune] shows the things concerning the BODY and the crafts done BY HAND**; the **DAIMON** shows those concerning **soul and MIND, and the actions done through WORDS** and through **givings and takings**.*

Refines the IV.4 distinction with a practical edge: **Fortune → body and manual work; Spirit → mind, speech, and transactions.** Together with IV.4 (Fortune = the Moon's lot, body; Spirit = the Sun's lot, mind) this is now stated twice, in two books.

## ⭐ II.20 — περιποίησις resolves: the 11th from Fortune, p. 82

> *We also found the **eleventh place from Fortune** to be **acquisitive, a giver of possessions and goods**, especially with benefics present or witnessing. For **Sun, Jupiter and Venus** there furnish gold, silver, ornament and the greatest substance, and **gifts from greater men and kings**…*

**This defines the term used in II.22.** When Valens says *"if Fortune falls well but the **Acquisition** is afflicted, they diminish their possessions as age advances"* — the **Acquisition (περιποίησις) is the 11th place from the Lot of Fortune**. That rule was uninterpretable without this chapter; it is now computable.

## ⭐ II.22 — Περὶ ἐνδόξων καὶ ἐπισήμων γενέσεων (Glorious and notable nativities — and inglorious ones), pp. 87–90

The "how large is this life" procedure. Six named tests:

1. *If the **Sun and Moon**, being in **busy (χρηματιστικά) signs**, are **spear-borne (δορυφορηθῶσιν) by most of the oriental stars**, with **no malefic opposing** — they make nativities **fortunate and glorious, leading and kingly**.*
2. *Likewise if the **lords of these** are on the Ascendant or angular.*
3. *If the **conjunctional or full-moon sign** [prenatal syzygy], **or its lord**, is on the Ascendant or Midheaven, the natives will be fortunate.*
4. *But if the **Sun or Moon or most of the stars are under the earth**, they become **notable and rich, but they will end their life badly**, or are turned about by envies, accusations and notoriety.*
5. *If the **lords of both the Daimon [Spirit] and Fortune** are found in the place of the **Basis**, with the ruler co-present — **brilliant and glorious**.*
6. *Those who have **the lord of both Fortune and the Daimon oriental, in their own places, and witnessed by Sun and Moon**, are born glorious and notable, and **move near kings or temples**, deemed worthy of gifts and reputation.*

And another life-arc rule: *If **Fortune falls well but the Acquisition is afflicted**, they diminish their possessions **as age advances**. If **Fortune falls badly and the Acquisition well**, they become **better from a young age**.*

**Engine note:** every input here is already computed — syzygy, doryphory, orientality, Fortune, Spirit, house placement, witnessing. This is assembly, not new calculation.

---

## II.23–II.25 — Lots of debt, theft, ambush, pp. 90–92

- **Theft** — *by day from **Mercury to Mars**, and the same from **Saturn**; by night from **Mars to Mercury**, and the same from Saturn.*
- **Ambush** — *by day from the **Sun to Mars**, and the same from the **Ascendant**; by night the reverse.*

Our `forensic_lots` already emits Theft and Accusation; **check the formulas against these**.

---

## ⭐ II.30–II.33 — parents, orphanhood, separation, pp. 101–105

### Which parent dies first (II.30)
> *Others have explained variously; **we ourselves, having tested, found thus**. Since the **Sun signifies the father, and in second place Saturn** — more precisely, for both night and day births, **the one made akin to the Moon** (beheld by her, co-present, or in her house or trine) **takes up the paternal place; and likewise Venus the maternal place, and the Moon**.*
>
> *One must look in each nativity **which is more beheld by the malefics or has fallen away** — Sun, Moon, Venus or Saturn. If the **Sun**, holding the paternal place, is overlooked by **Mars or Saturn with the benefics absent**, the earlier death is about the **father**; if the **Moon or Venus**, about the **mother**. If both lights are overlooked, **the one that has fallen away or is out of sect** signifies it.*

**Confirms the double maternal significator** first seen at I.1: mother = **Venus *and* the Moon**. Father = **Sun**, secondarily **Saturn**.

### Lot of the Father (II.30, p.103)
> *In a **day** nativity, **from the Sun to Saturn**, and the same from the Ascendant; **some, from the Sun to Jupiter**. By **night**, from **Venus to the Moon**, and the same from the Ascendant.*

Valens records a **variant within the day formula** (Saturn vs Jupiter) — surface it as a fork if implemented. *(The night formula as printed reads Venus→Moon, which is unexpected for a paternal lot; flag for a 1-up re-read before use.)*

> *If the **lord of the paternal lot** is on the opposite point, or the lord of the opposite is on the lot, **it indicates an adoptive father** — likewise for the mother.*

### II.31 — parents "from Timaeus"
Day: the Sun, his sign, the lord of Jupiter's sign, and the sign receiving Jupiter. Mother: the Moon's sign and her ruler; by day, from Venus and Venus's sign. Another named earlier source.

### II.32 — orphanhood
> *Mars with the Sun square Saturn make orphanhood. Saturn and Mars configured with Mercury, **Jupiter not beholding**, become orphaned. Saturn with Jupiter setting makes orphans. The Moon in a two-bodied sign witnessed by Jupiter makes **fatherless**.*

### II.33 — separation of parents
> ***Mars and Saturn interposing between the lights**, or falling between them, or by their rays, **separate [the native] from the parents**. … Saturn lying with the Sun while the Moon is alienated **separates the parents**.*

Note the distinction Valens draws — separation *from* the parents versus separation *of* the parents from each other.

## ⭐ II.35 — Σχήματα Σελήνης ια′: the eleven lunar configurations, p. 106

> *The configurations of the Moon are, **by natural reckoning, eleven**: first the **conjunction**, second the **rising**; then at **46°** from the Sun she makes the **crescent**; then to **90°** the **half-moon**; then to **135°** the **gibbous**; then to **180°** the **full moon**; then the **second gibbous**; then to **280°** the **second half-moon**; then to **360°** to the **setting**.*

An **eleven-stage phase doctrine with named degree boundaries.** Our engine emits a single `lunar_cycle` evidence item; this is far more granular and is the basis for judging the Moon's condition by phase rather than by aspect alone.

### ⭐ And pp. 107–108 assign each phase a TOPIC and a RULING PLANET

*"Τί σημαίνει ἑκάστη φάσις"* — what each phase signifies:

| Phase | Signifies | Lord / until |
|---|---|---|
| **Conjunction** | reputation, power, kingly and tyrannical dispositions, **public affairs of cities**, parents, marriages, mysteries, all universal matters | its own lord, latitude and course |
| **Rising** ("the light") | **life, action, future foundation**; confirms the conjunction's actions | Mercury co-introduces, to day 4 |
| **Crescent** | **upbringing, things hoped for in life, women and the mother** | Mercury prevails, to 8 |
| **Half-moon** | **injury, affliction, violent happenings**; also **children and rank** | Venus configures, to 12 |
| **Gibbous** | **happiness, coming advancement, travel abroad, sympathy of kin** | Sun, to 19 |
| **Full moon** | **reputation and disrepute**, travel, violent events, **falls from eminence and rises from the least**, parents | — |
| *(descending)* | | Mars, to 21 |
| **Second gibbous** | **sojourning abroad, greater action, happiness** — "equal in power to the god" | **Jupiter**, to 25 |
| **Second half-moon** | ***old matters, long-lasting afflictions***, children | **Saturn**, to 30 |

A systematic phase→topic→ruler table. Note the symmetry Valens builds in: the waxing half-moon gives *injury and violent happenings*, the waning half-moon gives *old matters and long-lasting afflictions* — acute versus chronic, and Saturn rules the chronic one.

## II.36 — Περὶ σίνους καὶ πάθους (Injury and affliction, sign by sign), pp. 109–114 — READ, POLICY-EXCLUDED

> *Since **the ancients wrote the place concerning injury obscurely**, we shall explain it more manifestly. Some … make **the beginning of the LIMBS from the LOT OF FORTUNE**: the Lot itself [the head]; the 2nd, the sides; the 3rd, the belly; the 4th, the hips; the 5th, the thigh; the 7th, the knees; the 8th, the shins; the 9th, the feet; the 10th, the head; the 11th, face and neck; the 12th, forearms and shoulders.*
>
> ***And the AFFLICTIONS from the DAIMON.** For the Daimon itself is the **heart**; the 2nd, the inner belly; the 3rd, through which the seed is carried, and the place of the kidneys; the 4th, the colon; the 5th, the liver; the 7th, the bladder; the 8th, the intestines; the 9th, the meninges and teeth and hearing; the 11th, the tongue; the 12th, the stomach.*
>
> *These follow **Leo and Cancer**, since the **Moon is the place of the cosmos and the Sun is light and daimon**.*

**Structurally this is a third use of the Fortune/Spirit derived-house layer** (II.17) — outward/bodily parts counted from **Fortune**, inward organs from **Spirit** — and it is consistent with II.19's body/mind split. Worth noting as confirmation of that layer even though the content is excluded.

The rest of the chapter (pp. 109–114) is sign-by-sign bodily affliction. **Read; not for customer output**, on the same policy footing as II.41 — we make no medical claims. The material is authentic and the exclusion is our product decision, not a gap in the source.

## ⭐ II.37 — Περὶ γάμου καὶ συναρμογῆς (Marriage and union), pp. 114–121

Valens opens with his own epistemic standard:

> *Whatever methods have seemed to me **through experience** to be true, these I have set forth with their solutions. Now I shall clarify the place concerning marriage — being various, but easily grasped by those who have sense.*

### The method
> **The place concerning marriage is naturally taken from the 7th sign from the Ascendant; but one must look at VENUS — how she lies, with whom, and by whom or by what she is witnessed or ruled.**

Not the 7th house alone. **Venus's condition, co-presence, witnesses and dispositor** carry the judgment.

### The operative rules in this chapter
- *Venus in **tropical** signs, or transacting in **two-bodied** ones — **especially by night** — makes people **much-married (πολυγάμους)** and much-sharing; especially if Mercury is with her, and much more if Mars also witnesses her.*
- *And if **her lord is setting, or in the bad-daimon place (κακοδαιμονῶν)**, or a corrupter afflicts her, or she is badly placed — it makes people **unfortunate about marriages and transactions**.*
- *A corrupter annulling Venus by witnessing, or especially her ruler, produces **deaths of wives, or injuries, or crises**. Well placed toward the nativity, **inheritances** from them; badly placed, sufferings and griefs.*
- ***Saturn overlooking (ἐπιβλέπων) Venus makes people for the most part unmarried (ἀγάμους) and hard to deal with.***
- *Venus in **Saturn's sign or bounds**, or opposed by him, **and neither Mars nor Jupiter witnessing her, nor Mercury co-present** → **"altogether widows and virgins."*** — note the three-fold escape clause.
- *Saturn **always opposing** Venus gives an injured or barren spouse — **"and likewise for a woman, a husband."*** (Valens does state the reciprocal.)
- ***The Moon set under the beams (combust) is not good for marriage.***

### Findings
1. **The escape clause is doctrinally important.** The worst outcome requires the *absence* of Mars, Jupiter and Mercury testimony. Valens builds the mitigation into the rule itself — a fourth instance of the conditional structure seen at I.1 p.5, in the sign rulers, and in the bounds.
2. **Venus's dispositor being in the 12th is a named marriage affliction**, not an inference. That is a computable test we do not currently run.
3. **Combustion of the Moon is a named marriage affliction.** Also computable, also not currently applied to this topic.
4. Valens explicitly extends the doctrine to female natives. Our second-person reports sidestep the issue anyway, which remains the right call.

## ⭐ II.38 — the Lot of Marriage, pp. 119–121

> *For **men, from the Sun to Venus**; for **women, from the Moon to Mars** — and the same **from the Ascendant**. For **Venus and Mars are the corrupters of both the lights**: because the Sun, exalted in Aries, **is corrupted in Libra** and makes diminution of the day; and the Moon, exalted in Taurus, **is brought low in Scorpio** and makes removal of her light.*

A derivation, not an assertion: Venus rules **Libra**, the Sun's fall; Mars rules **Scorpio**, the Moon's fall. The marriage significator for each sex is the planet that undoes that sex's light.

> ***Venus then will be the marriage-arranger (γαμοστόλος) of men, and Mars of women, universally.** Whence for **men** one must compare the marriage place with the **DAIMON**, and for **women** with the **LOT OF FORTUNE**.*

A fourth use of the Fortune/Spirit layer.

### Delineations
> *If **many stars are present at or witness the marriage-arranging place, there will be many marriages**. If the stars are with the Moon and **Jupiter** witnesses, they come together **lawfully**; if **Saturn**, they are **separated by death**; if **Mercury without Jupiter**, they are blamed over slave-women. If **Jupiter witnesses Saturn**, a lawful marriage is shown … If **Saturn, Mercury and Mars witness**, they come together in common and **childlessly**. If [Mars] is added to **Venus or the Moon**, the courtesan-like and lustful follows, and **jealousies and factions** arise, and the cohabitation is full of pretence.*

### ⚠️ Methodological tension with our own policy

**Valens's marriage lot is sex-differentiated at the formula level** — men Sun→Venus, women Moon→Mars — and the comparison lot differs too (Spirit vs Fortune). Our reports are deliberately second-person precisely so we never infer or assert a native's sex, after getting that wrong on a real customer.

These cannot both hold. The honest options, in preference order:

1. **Compute both and present both**, labelled — "the men's formula gives X, the women's gives Y." Faithful, no inference, lets the reader take the one that applies.
2. **Ask** at intake, as an optional field, and omit the technique when unanswered.
3. **Omit the lot** and rely on II.37 (7th sign + Venus's condition), which is *not* sex-differentiated.

**Option 1 is the recommendation** — it matches the standing rule that where the tradition forks we show the fork rather than pick, and here the "fork" is simply which formula applies to the reader. **Never guess from a name.**

---

## ⭐ II.27 — Περὶ χρόνων ἐμπράκτων καὶ ἀπράκτων (Effective and ineffective times), pp. 94–95

A **fourth timing system**, distinct from profections, Firdaria and Zodiacal Releasing.

> *The times of **good fortune or misfortune, of irregularity and disturbance**, will be grasped **from the ascension of each sign, or from the cyclic period of the star**.*

### Different significators for different questions
> *For those seeking the times **OF LIFE**, attend to the **Ascendant and the Moon**, or the sign on which their lords are present. For **ACTION and REPUTATION**, attend to the **Lot of Fortune and the Daimon and the Sun**, or the **conjunction/full moon [syzygy]**, and **the exaltation and its lord**.*

We currently run one undifferentiated timeline. Valens splits it: **life** is read from Ascendant + Moon; **career and standing** from Fortune + Spirit + Sun + syzygy.

### The handover order
> *Those present **in the first place to the Ascendant** will begin to rule the **first time-period**; then those in the **Midheaven**, or in the **setting place**, or in the **subterranean**. And if these places are **empty of stars**, those in the **succedents**; and these being empty too, those in the **cadents** — and even if they are not so strong, still **they will manage affairs**.*

**Chronological handover by house rank**: angles first (ASC → MC → DESC → IC), then succedents, then cadents. Period lengths from the sign's **ascensional time** or the planet's **cyclic period**. Empty places are skipped, not left blank.

**Engine note:** this is fully computable — we already have ascensional times (used in ZR) and planetary periods (used in Firdaria and decennials). It is assembly, not new astronomy. It also supplies exactly what the Kostanay customer asked for and we could not give: *"which periods, and why."*

## II.28–II.29 — Περὶ ἀποδημίας (Travel abroad), pp. 96–101

> *The **lot concerning foreign travel** is counted **from Saturn to Mars, and the same from the Ascendant**.*

II.28 is attributed to **Hermippus**; II.29 cites **Abraham** ("τὰ ὑπὸ Ἀβραάμου λεγόμενα") — another named earlier authority inside Valens.

---

## ⭐ II.39 — Περὶ τεκνώσεως ἢ ἀτεκνίας (Children or childlessness), pp. 122–123

**This is where the fertility question is judged — not in a bound delineation.**

> *The place concerning children is taken from **Mercury**… Afflicted by **Saturn and Mars** they are causes of **childlessness or of the destruction of children**; helped by **Jupiter**, causes of good offspring.*
>
> *One must consider also the **lot-ruler of children**, found thus: **from Jupiter to Mercury** [for males], and for females **from Jupiter to Venus**, and the same **from the Ascendant**.*
>
> *The **lord of this place** witnessed by a corrupter **destroys children**; by the givers, it indicates good offspring. When **Jupiter, Venus and Mercury are unafflicted**, they indicate good offspring; the reverse produces … deaths concerning children.*
>
> ***Those witnessing the child-givers from two-bodied signs, or themselves in two-bodied signs — the number is doubled.** The **feminine** stars witnessing the child-giver give **females**; the **masculine** give **males**.*

Specific configurations: in a **male** nativity, Jupiter with or ruled by Mars while Saturn witnesses or is with Venus → childlessness and children lost. In a **female** nativity, Moon in Mercury's places with Venus in a masculine sign witnessed or ruled by Saturn → *childless, or the children born are destroyed.*

**Methodological point.** The bound delineations at I.3 repeatedly say στειρώδης / ἄγονος ("sterile", "barren") — but those words track **Saturn's bounds and Saturn-ruled signs** almost perfectly, and follow directly from Ptolemy I.4–I.5 (cold and dry are the non-generative qualities). They are a colouring of the *degrees*. **The question of children is judged here, by Mercury, Jupiter, the Lot of Children and their lords.** Reading a fertility verdict out of a bound is the "quote half a sentence" error.

## II.40 — Περὶ ἀδελφῶν (Siblings), p. 123

> *The **Sun on the Ascendant** makes few- or scarce-siblinged. **Saturn angular** makes scarce- or few-siblinged. **Jupiter, Mercury and Venus angular are GIVERS of siblings.** **Saturn opposing destroys the expectation.** **Saturn with Mars** destroys siblings or makes them weak.*
>
> *In the **third place from the Ascendant, which is concerning siblings**, **Venus and the Moon** being akin give **sisters** — especially if the sign is feminine; but **Sun, Jupiter, Mercury** in a masculine sign give **brothers**.*

Confirms the three sibling significators from I.1 and adds the sex-determination rule.

## II.41 — Περὶ βιαιοθανάτων (Violent deaths), pp. 123–128 — READ, NOT FOR USE

Opens with another conditional: *"The **opposition of Sun and Moon is not always harsh**; but when a malefic coming upon the phase looks at it, or they are ray-cast while having a relation — **then** it becomes harsh. Whence even the wholly-fortunate nativities did not obtain the fortunate to the end."*

The remainder is five pages of specific violent-death configurations. **Recorded as read; not to be used in customer output.** This is a policy decision, not a doctrinal one — the material exists and is authentic. It stays out for the same reason the longevity module did.

---

## ⭐ III.1 — Περὶ ἐπικρατήσεως (Epikratesis — which light prevails), pp. 132–134

> *Concerning the foundation of the **vital times**, different men have handed down different things; but since the topic seems various and multipartite, **we too, having tested them**, shall explain further. Let our first account be that concerning **epikratesis, ray-casting, and rulership**. And before all, let the epikratesis be sought concerning the **Sun and the Moon**.*

### Valens breaks with received doctrine, in the first person
> *Some gave it to the Sun by day and the Moon by night; **but I say (ἐγὼ δέ φημι)** that **the Sun prevails also by night, and the Moon by day**, if they happen to be **seasonably configured**. And if both do, the epikratesis is assigned to whichever is **more properly configured** and has obtained sect or triangle.*

A documented fork **inside Valens**, flagged by him. Worth surfacing as such.

### The ruler of life comes from the BOUND
> *And from the **bounds of the prevailing luminary** the **ruler (οἰκοδεσπότης)** is found. But if **both fall away**, the **bound of the ascending degree or of the Midheaven** will produce the rulership — mostly that one whose lord holds a proper configuration to the Ascendant.*
>
> *And if **both luminaries have the bound of one star**, that one is judged **more destructive (ἀναιρετικώτερος) and ruler**.*

He then gives a numbered decision table of positional cases ("First epikratesis… Second… Third…") covering Sun on the Ascendant with Moon in the Bad Daimon, Sun in the Good Daimon with Moon at Midheaven, and so on.

## III.2 — Περὶ μοιρῶν ἐπισήμων τῶν κέντρων (Notable degrees of the angles), pp. 134–135

Method for deciding which degrees are **χρηματιστικαί (busy / transacting)**: take the arc from the ascending degree to the IC, and reckon **a third part** of the collected sum as angular-transacting; planets in those degrees are **powerful**, and those in the remainder toward the IC are **ἀχρημάτιστοι — untransacting, ineffective**.

This matters because "busy signs" is a load-bearing term in II.2 and II.22, and here Valens defines it **by degree arc, not by whole sign**.

## ⭐ III.3 — Περὶ ἀφέσεως (Aphesis — releasing), pp. 136–137

> *Since some, carried by **envy or inexperience**, treat the aphesis one-sidedly and obscurely — for all use the number of degrees from the releasing degree to the **square side**, and the ascensions — it is necessary for us to explain the difference. For we find nativities that **have passed the square side**, and greater ones in signs of few ascensions, **although the ancient says precisely that it is impossible**.*
>
> *When a nativity is set out, it will be necessary to look **whether the nativity is ruled or unruled**, and whether the **Sun, the Moon, or the Ascendant is the releaser (ἀφέτης)**.*
>
> *If the Sun or Moon takes the releasing place, reckon **from the releasing degree to the square side**, how much time is collected **according to the clima** in which he was born, and having collected it, declare that he will live so many years.*

**Worked example (p.137):** rising at **Gemini 13° in the 2nd clima**, culminating **Aquarius 22°**. Releasing from the ascending degree, *"the termination of the years is **not necessarily at the square side, Virgo 13°, but as far as the IC, Leo 22°**"* — if no destroyer casts a ray.

### Engine note — do NOT reinstate longevity on this
Our `hyleg.py` longevity module was **removed from customer output for failing 11 of 20 charts with known death dates**, and that decision stands. Note that Valens's method here is **a different algorithm entirely** — bound-based, clima-dependent, with the release running to the IC rather than the square. It is not the Lilly/al-Bīrūnī procedure we tested. If longevity is ever revisited, this would need its own validation run against `scripts/validate_longevity.py`, and the same acceptance criterion applies: **promised years ≥ age attained, or it does not ship.**

---

## ⭐ V.3 — Περὶ καταρχῶν (Inceptions): the nodal prohibition, p. 212

> *Concerning the days brought down, one must guard, **when the Moon passes the ASCENDING NODE of the moment and its squares and oppositions — especially at the same degrees** — not to undertake anything: **not to sail, not to marry, not to meet, not to found, not to plant, not to form associations, nor in general to do anything.** For it will be judged neither firm nor easily concluded, but **changeable, incomplete, damaging or grievous, and not enduring**.*
>
> *…for **not even the BENEFICS present in these places will furnish anything full of goods**. Whence **even WITHOUT A NATIVITY**, if one guards the Moon's passages toward the ascending node, **he will not go wrong**.*

Two things:
- **A clean electional rule**: the Moon on the nodal axis (conjunct, square or opposite the node, degree-exact) voids an undertaking.
- ***"Even without a nativity"*** — Valens states outright that this works as **pure electional astrology**, no birth chart required. Rare explicit acknowledgement that a technique stands alone.
- And **rule #1 again**: benefics there furnish nothing.

## ⭐ V.4 — the five climacteric signs, p. 213

> *These signs are **climacteric**: **ARIES, TAURUS, CANCER, SCORPIO, AQUARIUS**. The years falling in these turn out **precarious**; and when the Sun comes to be in them in these handings-over, **the month too will be evident**.*

A concrete, checkable five-sign list — and a method for narrowing a flagged year to a **month** (when the transiting Sun enters the climacteric sign). Not implemented.

## ⭐ V.5 — the SOLAR RETURN (ἀντιγένεσις), p. 213

> *We shall necessarily make the **anti-nativity**; for it contributes much toward the seasonal changes of the times — **sometimes confirming** the powers of the outcomes, **sometimes hindering** them. … The Sun being in the natal sign, we look at **when and at what hour the Sun takes the restorative degree which it had from birth**, and that we shall say is rising.*

The solar return defined by the Sun's return to its **exact natal degree**, with the Ascendant for that moment. Valens is explicit that it **modulates** the natal promise — confirming or hindering — rather than generating events of its own. Consistent with IV.16's ὑπόστασις rule.

## ⭐⭐ V.9, p. 226 — why he carries eight timing systems

> *One must examine the degree-motions from the treatise of the tables toward the phenomena, for the universal observations and chronographies are held together out of these releases.*
>
> ***Whence the MAJORITY, not understanding that matters are accomplished THROUGH MANY METHODS, suppose the science to be non-existent, or inconclusive, or hard to grasp — having occupied themselves throughout with the power of A SINGLE METHOD.** But those who, with all precision, have brought in **many methods** or powers, and **used mind and judgment and reason according to the method appropriate to the nativity**, have acquired the operation of the outcomes as easy to grasp.*

This is Valens's own answer to the question his book raises: he gives eight timing systems and ranks none because **he holds that the method must be fitted to the chart**, and that people who pick one technique and stick to it conclude the whole subject is empty.

### It reads like an escape hatch — until VI.8

"You used the wrong method for this nativity" could excuse any failure after the fact, and V.9 gives no rule for **choosing** the method in advance. That is exactly what Test Case 1 exposes: four testimonies, three matched, one failed, and nothing telling you beforehand which to weight.

**But VI.8 answers it, and the answer is not a hedge — see below.**

## ⭐⭐⭐ VI.8, p. 257 — Valens says why the methods were never resolved

> *Since I had acquired the **discovery** of the things sought easily, through continual exercise and the whole variety of methods — **but the DISCRIMINATION and the clear TESTING required TIME, and this remained short for me** (for the life of men is momentary, even if it should seem to go on very long) — **like a father at the end of life, weighed down by disease, leaving brief instructions to his children before decay overtakes him**, so with a father's earnestness I noted down the chapters of the theorems as they came to me, **giving to the lovers of the beautiful a beginning of the road**.*
>
> ***If the mind were long-lived or immortal, the division would have been indisputable and single; but the gods know all things.***

**He is not defending plurality. He is admitting he ran out of life to resolve it.**

*"If the mind were long-lived or immortal, the division would have been indisputable and single"* — Valens believed there **was** a single right answer, that finding it required testing he could not complete, and that he was handing forward an unfinished job. The eight timing systems are not a doctrine of methodological pluralism. **They are a list of candidates he never got to eliminate.**

### What this means for this project

It removes the escape hatch and replaces it with an assignment. Valens's own standard was **discrimination by testing** (διάκρισις καὶ σαφὴς ἔλεγχος); he simply lacked the time. We have ephemeris code, a validation harness, and the ability to run a technique against many charts in seconds.

**The test-case section of this file is the work Valens said he could not finish.** That is the honest framing for the whole project — not "we transmit the ancient wisdom," but "we do the elimination he asked for." And it makes recording failures like Test Case 1 not an embarrassment but the actual deliverable.

## VI.6–VI.7, p. 256 — and again he rejects chart-independent time-lords

> *Most, however, make the times on every nativity **by the seven-zone**, beginning from Saturn, then Jupiter, Mars, Sun, Venus, Mercury, Moon … **But this does not please me, since the same time-lords will be found on most nativities.***

Third instance of the same principle (cf. I.11, and the II.2 procedure): **a time-lord scheme that gives everyone the same answer is worthless.** Consistent objection, stated three times in three books.

## VI.8, p. 259 — Valens labels his own sources three ways

> *I said before that **some things I have unravelled from the ancients' obscure arrangements**; **some I have adopted** as they seemed good; and **some I myself, having discovered them privately, arranged**.*

A provenance statement about his own book: inherited-and-clarified / adopted / original. Useful when citing him — not everything in the *Anthologiae* claims the same authority, and he says so.

## V.6–V.8 — finer timing and lunar inclinations, pp. 214–217

**V.6** the transacting month and day, from the **transiting Sun to the natal Moon**, projected from the Ascendant. **V.7** headed *"this is the **TRUE** division of the days"* — Valens distinguishing his preferred day-method from the alternatives he has already given. **V.8** a table of the Moon's **inclinations (προσνεύσεις)** at each new moon, sign by sign.

---

# ⭐ TEST CASES — where the reading met a life

The only way this gets real. Record every chart where a Valens reading can be checked against known facts, **especially the misses**.

## Case 1 — 1996-08-13, 07:18 PDT, Fairfield CA (owner's chart). Male. Day chart.

**Known fact supplied by the native: no relationship of any kind, to age 30.**

Chart points bearing on it: Ascendant Virgo 1°30′ (Mercury bound); **Venus Cancer 5°32′, out of sect, in Mars's bound, 11th house**; **Saturn Aries 6°51′ square Venus at 1°18′, Saturn in the 10th sign from Venus (overcoming)**; Jupiter Capricorn 8°30′ (fall, retrograde) opposing Venus 2°58′; **Lot of Marriage (men, Sun→Venus) Cancer 15°56′, 11th house** — Mars conjunct 3°25′, Mercury sextile 1°14′, Jupiter opposition 7°26′, Venus co-present.

| Testimony | Prediction | Outcome |
|---|---|---|
| **II.37** — *Saturn overlooking Venus makes people **for the most part unmarried (ἀγάμους)** and hard to deal with* | unmarried | ✅ **matches** |
| **I.3** — Ascendant in Virgo/Mercury bound: *not fortunate in love-matters; especially these degrees* | unfortunate | ✅ **matches** |
| **II.16** — Venus square Saturn: *harder toward love-matters, **not much-sharing (οὐ πολυκοίνους)*** | few or none | ✅ **matches** |
| **II.38** — *many stars present at or witnessing the marriage place → **many marriages*** | many | ❌ **fails** |

### Findings

1. **Weighting signal.** The **aspect-based** and **bound-based** testimonies matched; the **lot-occupancy count** failed. Where Valens's methods conflict on a topic, this case says prefer the condition of the significator over the population of the lot. One case is not a rule — but it is the first datum, and it points the same way as Valens's own methodological statement at I.22 (placement decides).

2. **Reader error to avoid — importing a condition from the wrong sentence.** In the first pass I quoted the ἀγάμους line and then softened it using II.37's escape clause (*"and neither Mars nor Jupiter witnessing her, nor Mercury co-present"*). **That clause attaches only to the extreme outcome** — "altogether widows and virgins." The base statement *Saturn overlooking Venus makes people for the most part unmarried* has **no escape clause**. Softening it was unsupported, and the unsoftened reading is the one that matched.

   Generalise: **an escape clause governs the sentence it is in.** Do not carry it upward to a stronger claim earlier in the chapter.

3. **Timing has now failed THREE times on this chart, across two techniques.**
   - **7th-house profection** years fall at ages **6, 18, 30, 42, 54** (Lord of the Year Jupiter, ruler of the 7th, in fall and **retrograde** — which by IV.14 reads as *postponement*). **Ages 6 and 18 passed with no result.** Age 30 began 13 Aug 2026.
   - **Topical release from the 7th** (IV.16, computed 2026-08-09, 360-day years): L1 **Taurus, lord Venus, Mar 2023 – Feb 2031**. That is Venus's own domicile — **the most relationship-activated L1 chapter this technique can produce** — and it has run **three and a half years with no result**. The current L2 is **Cancer/Moon** (Jul 2025 – Aug 2027), the Moon being peregrine and combust in the 12th, which is a candidate explanation but was not stated in advance.

   **Do not present any of these windows as a forecast.** Report them as "what the tradition marks as most activated," always with the failure record attached. Two techniques, three activations, no result.

4. **The natal picture and the current releases point opposite ways.** Natally **Spirit is angular in the 1st, Fortune buried in the 12th**. But the releases invert it: **Fortune** runs a 20-year **Mercury** chapter (the chart's best planet, in the Ascendant's sign) from 2015–2035, while **Spirit** runs **Mars-in-fall at L1 with Saturn-in-fall at L2** to 2031. Valens gives no rule for reconciling nativity against release when they disagree. **Flag it; do not resolve it.**

---

# ✅ ENGINE CHANGES — ALL 27 IMPLEMENTED, 2026-08-09/10

Every item below is shipped, with regression tests in
`src/tests/test_valens_greek_corrections.py` (40 tests). Each test names the
passage it enforces, because almost every one of these was a rule the engine
**already computed the inputs for and then failed to apply** — so a silent
revert would look like working software.

Evidence items on a reference chart went from **87 to 111**.

**Two changes disproved the note that specified them, and that is recorded rather than hidden:**

- **#18** was meant to assert Valens's rule that a sign and its opposite ascend in 60. **Under exact spherical computation it is false** — pairs run 55.8° to 64.4°, because `AD(λ+180) = −AD(λ)` makes the pair-sum reduce to twice the sign's RA span. Valens's 60 belongs to the ancient *arithmetical* schemes. The test now pins the discrepancy so nobody "fixes" the astronomy to match a schematic table.
- **#20**'s lunar bands were wrong in my first draft: Valens gives *"to 280 the second half-moon, then to 360 to the setting"*, and I had merged those two, shifting everything after the full moon by one band.

**One change exposed a latent bug in the publication contract.**

Adding the Valens timing rules broke **13 previously-passing tests**. The cause was not the new doctrine — it was `reading_contract.py`, whose `fatalistic_claim` rule matched the bare word **"guaranteed"**. The new prose says *"…it describes the manner and severity of a difficulty, **not a guaranteed event**."* A disclaimer.

**The contract was flagging its own disclaimers**, which pushes authors toward vaguer hedging — precisely the opposite of what the rule exists to enforce, and the same class of over-match as the earlier "treat" → medical-claim false positive.

Fixed in two parts: the fatalism pattern now requires an **assertive construction** (`is guaranteed`, `guarantees that`, `guaranteed outcome/success/to`), and `_pattern_violation` gained a **general negation guard** that skips a match preceded by a negator within the same sentence. The guard applies to every pattern, not just this one, and it deliberately does not look past a sentence boundary — so a denial in an earlier clause cannot launder a promise that follows. Locked by 14 tests.

**Two were narrowed on inspection:**

- **#10** — I was about to mark seven Paulus chapters "attested". Boer only annotates four in the index I read, so the grades are now `attested_by_boer` (2), `corroborated_elsewhere` (2), `unattested_chapter` (4). Absence of an annotation is not attestation.
- **#9** — three Ptolemy rules remain on Ashmand. I have not read those chapters in Greek, so they are **flagged** with an `edition_limit_note` rather than silently repointed.

**One correction to my own hand analysis:** the II.2 life-arc (#3) judges the triplicity rulers by **place**, not essential dignity. On the Kostanay chart both rulers fall in injurious places, so the arc correctly stays silent — where my manual reading had asserted an arc from Mars's domicile. The engine is now more faithful than I was.

---

## Original specification

# ENGINE CHANGES REQUIRED

Concrete, from verified findings. Nothing here is speculative.

| # | Change | Source | Notes |
|---|---|---|---|
| 1 | **Invert the benefic/malefic logic.** Run the placement-and-sect test first; the label is the input, not the verdict. A malefic in its own place and in sect is a *giver of good things*; a benefic in the 6th/8th/12th is a *loss*. | Valens I.1 p.5; II.5, II.8, II.10 | Biggest change. Affects every planet paragraph. |
| 2 | **Add the 60 bound delineations** keyed `(sign, bound_lord)`. | Valens I.3, pp. 14–19 | We ship bound lords with no meanings. Our own translation, unencumbered. |
| 3 | **Add the II.2 life-arc procedure** — sect light → triplicity → 1st ruler (early life) / 2nd ruler (later life), hinge at the sign's ascensional time. | Valens II.2, pp. 56–57 | Engine already returns `triplicity_periods` with exactly these three rulers. Wire the temporal reading. |
| 4 | **Add Valens's marriage tests**: Venus's dispositor in the 12th; Moon combust; Saturn overcoming Venus; and the Mars/Jupiter/Mercury escape clause. | Valens II.37 | All computable now. |
| 5 | **Mercury's sect from solar phase** in the main composer, not just the multitradition panel. | Ptolemy I.7 | Already fixed in `multitradition/hellenistic.py`; main path still silent. |
| 6 | **Third slot for Mars in the Ptolemaic water triplicity.** | Ptolemy I.19 | Two-slot structure can't hold it; dignity currently unscored. |
| 7 | **Planet colour and taste** — complete set, all seven. | Valens I.1 | Judgment call whether it reaches the customer. |
| 8 | **Second significators**: mother = Moon *and* Venus; siblings = Moon, Jupiter *and* Mercury. | Valens I.1 | We treat both too narrowly. |
| 9 | **Repoint remaining Ashmand citations** to the Greek where the chapter has been read. | — | Three Ptolemy rules still on Proclus's paraphrase. |
| 10 | **Grade every Paulus rule** against Boer's `est Pauli, non Heliodori` annotations. | Boer 1958 praefatio | Paulus is 14 of 87 evidence items and the text is documented as interpolated. |
| 11 | **Repoint the exaltation-degree citation** from Firmicus (c. 334) to **Valens III.4, 140,4** (c. 165). | Valens III.4 | All seven degrees verified identical. ~170 years earlier witness. |
| 12 | **Repoint the hayz/halb citation** from al-Bīrūnī §496 (c. 1029) to **Valens III.5, 141,16**. | Valens III.5 | ~860 years earlier. Adds Mercury-by-bound-rulership and "Venus rejoices rising more than culminating." |
| 13 | **⚠️ Surface the whole Fortune-derived layer — it is computed and never reaches the reader.** `topical.py:443` emits `places_from_fortune`; `forensic_engine.py:1347` documents Fortune=body / Spirit=action. **Neither appears in `reading_composer.py` or `reading_evidence.py`.** Valens says consult it "before all": the Lot is a **second Ascendant** (its 10th = reputation, 7th = setting, 4th = subterranean), and the **11th from Fortune is the Acquisition place** that II.22's wealth-over-time rule depends on. | Valens II.17, II.19, II.20, IV.4 | Classic "loading is not firing." Biggest single unused asset found. |
| 21 | **Cite the Lot of Exaltation.** `lots.py:141` computes it correctly (day Sun→Aries, night Moon→Taurus) but it sits outside the seven Hermetic lots with no attribution. | Valens II.18, 80,9 | Verified exact. Citation only. |
| 14 | **Add the II.4 lord-of-Ascendant / lord-of-Fortune delineations** keyed `(planet, witnesses)`. | Valens II.4 | All inputs already computed. |
| 15 | **Add Valens's time-distribution** (angles → succedents → cadents handover), with **separate significators**: life from ASC+Moon, career from Fortune+Spirit+Sun+syzygy. | Valens II.27 | Uses ascensional times and planetary periods we already have. |
| 16 | **Add climacterics from the aspect a malefic throws at Fortune** — opposition→7s, right trine→9th, left trine→5th, right square→10th, left square→4th. | Valens III.15 | Not implemented at all. |
| 17 | **Surface the masculine/feminine-degree fork.** We ship Lilly's irregular table; Valens I.12 gives a regular 2½° alternation. Two systems, not one. | Valens I.12 vs Lilly p.117 | Move to `doctrinal_disagreements`. |
| 18 | **Add an ascensional-time invariant test**: `asc(sign) + asc(opposite) == 60` for the clima. | Valens I.7 | Underpins ZR, aphesis and the II.2 hinge. Cheap assertion, catches table corruption. |
| 19 | **Don't conflate the two "Lord of the Year" techniques.** I.11 is a weekday/calendrical reckoning from the Augustan epoch; IV.11 is the profection (age ÷ 12). We implement the latter. | Valens I.11 vs IV.11 | Naming hazard only, but it will bite someone. |
| 20 | **Add the eleven lunar configurations** with their degree boundaries (46°, 90°, 135°, 180°, …), each with its topic and ruling planet. | Valens II.35 | We emit one undifferentiated `lunar_cycle` item. |
| 22 | **Surface Valens's own bound system** as a named fourth option — dignity-count, sect-dependent, **includes the lights**. | Valens III.9 | `doctrinal_disagreements`, not a new `TermSystem`. |
| 23 | **⭐ Topical releasing.** ZR is hard-wired to Fortune and Spirit; Valens says release **from the place you are asking about** — MC for action, **7th for marriage**, 5th for children. Add a `release_from` parameter. | Valens IV.16 | Machinery exists. This is the technique customers keep asking for and we have never given. |
| 24 | **Retrograde time-lord ⇒ POSTPONEMENT, not denial** (ὑπέρθεσις). A distinct verdict from affliction. | Valens IV.14 | Cheap; affects every Lord-of-the-Year paragraph. |
| 25 | **Cap timing verdicts by the natal ὑπόστασις.** Strong foundation under bad times ⇒ disorder and fear, *not* catastrophe. Never read a period identically across charts. | Valens IV.16 | Doctrinal guard against the commonest predictive error. |
| 26 | **Rank places by potency** — busy (ASC, MC, 11th, 5th, Fortune, Spirit, Eros, Necessity) / middling (9th, 3rd, 7th, 4th) / injurious (2nd, 6th, 8th, 12th; **6th better than 12th**). Judge handing-over by **direction** (cadent→angular good) and by **dignity relation** (exaltation→exaltation good, fall→fall moderate). | Valens IV.11, IV.13 | Resolves χρηματιστικός, which II.2 and II.22 both depend on. |
| 27 | **Surface topical assignment as a fork.** Valens carries **three** incompatible schemes (II.5–14; II.15 nine names; IV.12). We ship Paulus's as settled fact. | Valens IV.12 | Marriage sits in the 7th, the 5th, *and* the 2nd/10th depending on chapter. |

---

---

## ⭐ III.12 — Valens attacks the popularisers of his own day, p. 150

Worth having in full, because it is the ancient statement of exactly the standard this project is trying to meet.

> *Since in each chapter I keep recalling **my own labour by way of testing**, lest I should seem to do these things for form's sake — I ran back to the books of the **ancient epitomizers** and learned that their discourse is **prettified and affectedly bad, able to astound the souls of readers and of the soft, but stripped of truth and hostile to the sober-minded**. For having wasted the time of many people and beguiled them, **it curtailed the life of some and utterly punished others**.*

And on Critodemus's mystical self-presentation, which Valens elsewhere cites as a source:

> *From there someone [wrote] the so-called "Vision" of Critodemus … **the rest full of monstrous tales aimed at the ignorant**: "Having sailed the deep," he says, "and travelled much desert, I was deemed worthy by the gods to attain a harbour without danger and a most secure abode."*

Valens, c. 165 AD, complaining that astrological writing is ornamental, impressive to the naive, empty of substance, and that it **harms people**. He cites Critodemus for technique in III.7–8 and mocks his packaging here — the same separation of method from presentation we have been making all day.

## ⭐ III.13–III.14 — conception, and the planetary periods, pp. 152–155

III.13 gives the method for finding the Sun, Moon and Ascendant **at conception**. III.14 opens with the same empirical note:

> *I found this sect too concerning the times of life **variously entangled by the ancients**; but I myself **sought it out through experience** and distinguished it.*

### ✅ The planetary periods — verified against our table

> *Each of the stars is master of its own period: **Saturn 30 years, Jupiter 12, Mars 15, Sun 19, Venus 8, Mercury 20, Moon 25.***

| | Valens III.14 | `hyleg.py` PLANETARY_YEARS "minor" |
|---|---|---|
| Saturn | 30 | 30 ✅ |
| Jupiter | 12 | 12 ✅ |
| Mars | 15 | 15 ✅ |
| Sun | 19 | 19 ✅ |
| Venus | 8 | 8 ✅ |
| Mercury | 20 | 20 ✅ |
| Moon | 25 | 25 ✅ |

**All seven exact.** And Valens names the same three-tier structure we implement: *"use the three limits — **least, mean, greatest** (ἐλάχιστον, μέσον, τέλειον)."* He also notes the numbers may be reckoned *"as days or months or years"* depending on the transacting signs — which is the same scaling principle decennials and ZR use.

## ⭐✅ III.16 — Μέσα ἔτη τῶν ἀστέρων: the mean years, and the formula, p. 157

> *Adding each star's **greatest period** and its **least**, you will find the **mean years**. For instance, **Saturn's complete years 57 and least 30 make 87, of which the half is 43½**. Jupiter's complete **79** and least **12** make 91, of which the half is **45½**…*

**mean = (greatest + least) ÷ 2** — stated outright, with worked arithmetic.

| | least | greatest | mean (derived) | ours |
|---|---|---|---|---|
| Saturn | 30 | 57 | 43.5 | 43.5 ✅ |
| Jupiter | 12 | 79 | 45.5 | 45.5 ✅ |
| Mars | 15 | 66 | 40.5 | 40.5 ✅ |
| Sun | 19 | 120 | 69.5 | 69.5 ✅ |
| Venus | 8 | 82 | 45 | 45 ✅ |
| Mercury | 20 | 76 | 48 | 48 ✅ |
| Moon | 25 | 108 | 66.5 | 66.5 ✅ |

**All 21 values in `hyleg.py PLANETARY_YEARS` are now verified against Valens's Greek** — least, greatest and mean, plus the rule that generates the middle column. These had been inherited from the al-Bīrūnī tradition and were previously unchecked. They are correct, and the mean column is not an independent datum but a derivation.

## ⭐✅ III.4 — the EXALTATION DEGREES, p. 140 — and this upgrades a citation

> *The **Sun** is exalted about the **19th degree of Aries**; the **Moon** about the **3rd of Taurus**; **Jupiter** about the **15th of Cancer**; **Mars** about the **28th of Capricorn**; **Saturn** about the **21st of Libra**; **Mercury** about the **15th of Virgo**; **Venus** about the **27th of Pisces**.*

All seven **exact** against `hellenistic.py EXALTATION` (Aries 19, Taurus 3, Virgo 15, Pisces 27, Capricorn 28, Cancer 15, Libra 21).

This matters for provenance. Today's Ptolemy reading established that **Ptolemy gives no exaltation degrees at all** — I.20 is sign-only — so our engine correctly cites them to `hel.firmicus.exaltation_degrees_table`. **Valens III.4 is ~170 years earlier than Firmicus.** Citation should be upgraded (engine change #11).

## ⭐ III.5 — Περὶ αἱρέσεως τῶν ἀστέρων (Sect of the stars — the hayz doctrine), p. 141

> *The **Sun, Jupiter and Saturn** rejoice being **above the earth by day**, and below by night; the **Moon, Mars and Venus** rejoice being **above the earth by night**, and below by day. **Mercury goes according to the sects and the rulership of the bounds.***
>
> *Whence for those born by day, if someone has Jupiter, Sun and Saturn **above the earth and well configured, he will be better off** than one having them below.*
>
> ***Venus rejoices more rising than culminating; and the rest of the stars rejoice being on the Ascendant rather than setting.***

This is **hayz / halb**. Our engine emits `hayz_halb` cited to **al-Bīrūnī §496 (c. 1029)**; **Valens III.5 is ~860 years earlier.** Another citation to upgrade. Note the third clause: Mercury's sect by **sect *and* bound rulership** — a refinement on Ptolemy I.7's phase rule, not a contradiction.

## III.3 cont. — the destroyers and their orb, pp. 138–139

> *The **destroyers (ἀναιρέται)** are **Saturn, Mars, the Sun, and the Moon carried to a phase**. There are also destructive **places** — the releasing bounds and those of the malefics. And destructive **degrees** are judged as **three on either side** of the release … **so that they are six in all**.*

A **±3° orb**, stated explicitly. Recorded for completeness; longevity stays out of customer output.

## III.7–III.8 — Critodemus material, pp. 142–144

Hostile places and releasings **from the books of Critodemus**, plus a table of hostile degrees derived through **bound correspondences** between signs. Valens uses Critodemus for technique here and mocks his mystical packaging at III.12 — that separation is his.

## ⭐⭐ III.9 — Valens rejects the received bounds and proposes his own, pp. 144–145

> *But **it did not seem right to me**, as some do, to impose the bounds according to the **seven-zone** … but **according to the HOUSES and the EXALTATIONS and the TRIANGLES**. Thus the **Sun's** house is Leo, exaltation Aries, triangle Sagittarius — that makes **3**; so in each sign the Sun has **3** bounds. The **Moon's** house is Cancer, exaltation Taurus, triangles Virgo and Capricorn — **4**…*

Counting each planet's dignities gives its degree-allotment in **every** sign:

| | dignities | degrees |
|---|---|---|
| Sun | ♌ house, ♈ exalt, ♐ tri | **3** |
| Moon | ♋ house, ♉ exalt, ♍♑ tri | **4** |
| Saturn | ♑♒, ♎ exalt, ♊ tri | **4** |
| Jupiter | ♐♓, ♋ exalt, ♈♌ tri | **5** |
| Mars | ♈♏, ♑ exalt, ♓♋ tri | **5** |
| Venus | ♉♎, ♓ exalt, ♍♑ tri | **5** |
| Mercury | ♊♍, ♍ exalt, ♒♎ tri | **4** |
| | | **= 30** ✓ |

**Two things make this remarkable:**

1. **It includes the LIGHTS.** Egyptian, Chaldean and Ptolemaic bounds all exclude the Sun and Moon. Valens's does not.
2. **It is SECT-DEPENDENT** — no other bound system is:
> *In **Aries, Leo, Sagittarius**, **by DAY** the Sun takes first 3, then Jupiter 5, then Venus 5 and the Moon 4, likewise Saturn 4, Mercury 4, and next Mars 5 — together 30. **By NIGHT the reverse**: Jupiter 5, Sun 3, Moon 4, Venus 5, Mercury 4, Saturn 4, Mars 5 — together 30.*

**A fourth bound system, and Valens's own** — flagged in the first person, derived from a stated principle, arithmetically closed at 30. Ptolemy attacks the Egyptian bounds for having no rationale (I.21); Valens replaces them with one that does. Neither adopted the other's answer.

**Not implemented, and probably should not be** — our `TermSystem` enum carries the three transmitted systems, which is the right default. But it belongs in `doctrinal_disagreements` as a named fourth option with an author and a derivation. **Engine change #22.**

## III.10 — the ἔμβολος lot and times of life, pp. 145–147 — READ, POLICY-EXCLUDED

Length-of-life material headed *"from the [books] of Valens."* Same footing as III.1–3 and II.41: recorded, not used.

## ⭐ III.11 — sevenfold and ninefold climacterics, pp. 147–150

> *We shall show, **as the KING also indicated** [Nechepso], concerning the climacteric: to take **from the rising of Seth [Sirius] to the birthday**, and from the collected number of days to subtract…*
>
> *For **nocturnal** nativities to seek the **sevenfold**, and for **diurnal** the **ninefold**, **it seems to some**; but in both they are alike. And the **sevenfold will be toward MARS, the ninefold toward SATURN**.*

Two cycles with planetary owners: **7-year → Mars, 9-year → Saturn**. The sect split (nocturnal→7, diurnal→9) Valens reports as *others'* view and declines to endorse — *"but in both they are alike."* Cite the cycle-to-planet mapping as his; the sect split as a reported opinion.

Note the epoch: **the heliacal rising of Sirius** — the same one he preferred over the civil year at I.11.

## III.15 — Περὶ κλιμακτήρων (Climacterics), p. 156

> *There are also the **lot-climacterics**, especially when **malefics are with, or witness, Fortune**. In the **opposition**, through **sevens** of years; in the **right trine**, through the **9th**; in the **left trine**, through the **5th**; in the **right square**, through the **10th**; in the **left**, through the **4th**.*

Climacteric periodicity is derived from **which aspect the malefic casts to the Lot of Fortune** — a computable rule we do not implement.

## ⭐⭐ IV.2, IV.4 — why Zodiacal Releasing uses two lots, pp. 158–161

**IV.2** — *The beginning of the release will be, for **conjunctional** nativities, the **first star after the conjunction**; for **full-moon** nativities, the first after the full moon.*

**IV.4** gives the doctrinal reason for releasing from both lots, and it is the passage that explains what each one governs:

> *Making the beginning of the release from the **Lot of Fortune** and the **Daimon**, which distinguish the **Sun** and the **Moon**. For the **Moon**, being cosmically **Fortune**, and being **body and breath**, near the earth and sending her effluence to us, accomplishes the like — **being lady of our body**. But the **Sun**, being cosmically **MIND** and cause, touching the **souls** of men through his own activity, arouses them…*
>
> *Since, then, the **bodily** lot is sought — such as **climacterics, weaknesses, bleedings, falls or sufferings**, and whatever pertains to the body — one must release **zodiacally from the Lot of Fortune**; and wherever the time terminates, we reckon the sign and the stars present or witnessing, how they are configured toward the ruler of the releasing times, and **whether the time-lords of the lots are angular or off-centre**.*

**Fortune = the Moon's lot = the BODY and circumstance. Spirit/Daimon = the Sun's lot = MIND, soul, action.** That is why the technique runs two releases, and it tells you which one answers which question. Our engine releases from both and reports both; **it does not tell the reader what the difference means.** This paragraph is the missing explanation, and it is Valens's own.

*(Note for policy: Valens directs bodily and health timing to the Fortune release. We do not publish health timing — that stands as a product decision, not a claim that the source lacks a method. State it that way if asked.)*

---

## ⭐⭐ IV.10 — ZODIACAL RELEASING, pp. 170–171

The core definition, in Valens's own words:

> *When we find a nativity … we shall make the **release of the years (ἄφεσις) from the Lot of Fortune or the Daimon, ZODIACALLY (ζῳδιακῶς)**, giving to each [sign] **the period of years as far as it can respond**; then we shall give **months**, then **days and hours**. And if the nativity of an **infant** is found, from the release we shall first apportion **hours**, then days, then months.*

That establishes, from the source:
- Release from **Fortune or Spirit** — both, not one
- **Sign by sign** (ζῳδιακῶς), not by degree
- Each sign receives **its ruler's period in years**
- Then the **same procedure recursively** at months, days, hours — i.e. the L1/L2/L3/L4 levels our engine computes
- For infants, start at the **hour** level

### ✅ Capricorn 27 confirmed
The period list at p.170 includes **Αἰγόκερως ἔτη κζ′ — "Capricorn, 27 years"** alongside the planetary figures (Sun 19, Saturn 30, Jupiter 12, Mars 15, Venus 8, Mercury 20). This directly attests the **Capricorn 27 / Aquarius 30 asymmetry** our ZR implementation already carries. Previously verified only by inheritance; now sourced.

The chapter also gives each period **converted down to months, days and hours** (Jupiter 12y 12m 30d 2d 12h; Mars 15y 15m 36d 3d 3h; Venus 8y 8m 20d 1d 16h; Mercury 20y 20m 50d 4d 4h) — the scaling table that makes the recursive levels work.

**Worked example** (p.170): Sun and Mercury in Capricorn, Saturn and Jupiter in Leo, Mars and Venus in Aquarius, Moon in Gemini, Ascendant Leo, **Fortune in Pisces, Spirit in Capricorn** — *"whence let the release of Fortune be from Pisces."* Full arithmetic follows.

## ⭐⭐ IV.6 — where the Capricorn 27 / Aquarius 30 asymmetry comes from, p. 164

Every ZR implementation carries these two numbers as magic constants. Valens derives them:

> ***Aquarius distributes 30 years, Capricorn 27***; since **the Sun is master of complete years 120, of which the half is 60** — from this, apportion the half to the diametrically opposite **Aquarius**, which is **30 years**. And **the Moon is master of complete years 108, of which the half is 54** — of this it apportions the half to the diametrically opposite **Capricorn**, which is **27 years**. ***Of the two signs then 57 years are collected, which is the complete [period] of Capricorn [Saturn].***

- Aquarius is opposite **Leo**, the Sun's domicile → Sun's **greatest** 120 ÷ 2 = 60 ÷ 2 = **30**
- Capricorn is opposite **Cancer**, the Moon's domicile → Moon's **greatest** 108 ÷ 2 = 54 ÷ 2 = **27**
- And **30 + 27 = 57 = Saturn's greatest years** — the two Saturn signs sum to Saturn's own maximum.

The internal consistency is the proof: three independently verified figures (Sun 120, Moon 108, Saturn 57) generate both constants and close the loop.

### ✅ Our `ZR_YEARS` verified — and for the right reason
`src/engine/prediction.py:10` gives Aries 15, Taurus 8, Gemini 20, Cancer 25, Leo 19, Virgo 20, Libra 8, Scorpio 15, Sagittarius 12, **Capricorn 27, Aquarius 30**, Pisces 12. Every sign takes its **domicile lord's least years**; Capricorn and Aquarius take the derived values above. All twelve correct. Note that Aquarius 30 *coincides* with Saturn's least years but is **not** derived from them — it comes from the Sun's greatest, halved twice.

## ⭐ IV.5 — Λύσις τοῦ συνδέσμου, the Loosing of the Bond, p. 163

> *The **loosings of the bond** will occur variously according to the natures of the stars. The **Sun and Moon handing over to Saturn** are indicative of oppositions … enmities of greater men, threats on account of mystical and old matters, overturnings, judgments and counter-suits, suspect livelihoods, **demotions of rank**, bodily troubles and dangers or shipwrecks, sudden circumstances and many accusations — **unless benefics present or witnessing dim the outcomes**.*
>
> *…**Saturn loosing the bond from Capricorn and Aquarius into Leo and Cancer**…*

**Confirms the mechanism directly: the bond is loosed across the Capricorn/Aquarius ↔ Cancer/Leo axis** — the same axis the sign-year derivation above turns on. And the escape clause appears again: *"unless benefics present or witnessing dim the outcomes."*

This chapter is what our registry already cites for ZR (`valens_zodiacal_releasing`, "Book IV, Chapters 4–7 … Loosing of the Bond, and sign period years, pp. 3–14"). **The citation is sound** — chapters IV.4–IV.7 do contain exactly the division from Fortune and Spirit, the loosing of the bond, and the sign period years.

## IV.7 — handing over and receiving, p. 165

> *One must look, in the division, at **both the one HANDING OVER and the one RECEIVING** — whether they are **angular or cadent**, in the **same sign**, or **lying upon one another**…*

The παράδοσις / παραλαβή doctrine: a period transition is judged by the condition of **both** time-lords, not just the incoming one. **IV.8 is a worked example chart — skipped per instruction.**

## ⭐ IV.11 — Περὶ ἐνιαυτοῦ χρηματιστικοῦ (The transacting year — annual profection), pp. 171–175

> *Having examined the years brought down of the nativity, we shall bring out **as many TWELVES as we can**, and giving the **remaining number** to the one able to receive it, we shall know **to whom the year is handed over**.*

Annual profection stated as arithmetic: age ÷ 12, the remainder counts the sign. Confirms our implementation.

He opens the chapter with another attack on his predecessors:

> *The many, setting out the division of times **variously and blameworthily**, handed down **no sect of truth**, but … **left the greatest error and an everlasting search to their readers**.*

### ⭐⭐ pp. 176–178 — the definitive ranking of places, and the rules of handing-over

> *First one must look **whether the handing-over occurs from ANGULAR places to ANGULAR**, or **from the Good Daimon to the Lot or to a busy place** — so that the signification may be practical or glorious; and then likewise **from the CADENTS TO THE ANGLES**, or **from the Bad Daimon to the Good Daimon**.*

**Direction of transfer is itself a judgment.** Rising in rank (cadent→angular, 12th→11th) is good; the reverse is not.

> *The **BUSY and ACTIVE (χρηματιστικοὶ καὶ ἐνεργητικοί)** places are: **the Ascendant, the Midheaven, the Good Daimon [11th], Good Fortune [5th], the Lot of Fortune, the Daimon, Eros, Necessity**. **MIDDLING (μέσα)**: the **God [9th], the Goddess [3rd]**, and the **remaining two angles [7th, 4th]**. **MODERATE and INJURIOUS**: the rest.*
>
> *…**Bad Fortune [6th] seems better than the Bad Daimon [12th]**, inasmuch as it holds a **trine figure to the Midheaven**.*

**This resolves χρηματιστικός, the term II.2 and II.22 both hang on** — and note the list mixes **houses and lots** freely, consistent with II.15's nine names. A three-tier potency ranking:

| Tier | Places |
|---|---|
| **Busy / active** | ASC, MC, 11th, 5th, **Lot of Fortune, Spirit, Eros, Necessity** |
| **Middling** | 9th, 3rd, 7th, 4th |
| **Moderate / injurious** | 2nd, 6th, 8th, 12th — with **6th better than 12th** (it trines the MC) |

Compare III.2, which defines busy *degrees* by arc from the Ascendant to the IC. **Both definitions exist and are not the same thing** — one ranks places, one measures degrees. Do not substitute one for the other.

## ⚠️⭐ IV.12 — a THIRD twelve-place topical table, p. 179

Valens now gives a **full twelve-place list that matches neither II.5–II.14 nor the nine names of II.15**:

> **1st** — **life**, as it were body and breath.
> **2nd** — livelihood, **the Gate of Hades**, giving and taking, partnership, **involvement with a woman**, transaction, **benefit from the dead**, **place of the will**.
> **3rd** — brothers, sojourning abroad, **kingship, authority**, friends, kinsmen, funeral rites, slaves.
> **4th** — children, one's own offspring and **elder persons**, city, house, properties, transfers, **dangers, death, confinement, mystical matters**.
> **5th** — children, friendship, partnership, bodies, **freedmen, adoption**.
> **6th** — slaves, injury, enmity, affliction, weakness.
> **8th** — death, benefit from the dead, ***an IDLE place (ἀργὸς τόπος)***, judgment, weakness.
> **9th** — friendship, travel, benefit from foreigners, **of god, king, ruler**, ***astrology itself (ἀστροσκόπος)***, **appearances of the gods, divination, mystical or hidden matters**.
> **10th** — action, reputation, advancement, children, **wife**, change, renewal of matters.
> **11th** — friends, **hopes**, gift, children, benefit, freedmen.
> **12th** — foreign land, enmity, slaves, injury, **dangers, tribunals**, affliction, death, weakness.

**Valens carries at least three topical schemes and reconciles none of them.** Marriage sits in the 7th (II.37), in Good Fortune/5th (II.15), and "involvement with a woman" in the 2nd with "wife" in the 10th (here). Children sit in the 5th, the 11th (II.15), the 4th and the 10th.

**This is not corruption — it is a working practitioner consulting several inherited layers.** Our engine cites Paulus's twelve places (14 evidence items). That is one defensible scheme among several *inside a single author*. It strengthens the case for surfacing topical assignment as a fork rather than a fact.

## ⭐ IV.14 — retrograde time-lords POSTPONE; they do not deny, p. 182

> *Universally one must observe concerning all the stars: when they are found **ORIENTAL**, handing over or receiving, and **ruling the year** or the universal times, and by **ingress come into the BUSY places** and make their rising — **they accomplish actions manifestly**, for their power is then aroused…*
>
> *But if they are **at their first station and found RETROGRADE**, they put the expected things, the matters, the benefits and the undertakings **INTO POSTPONEMENT (ὑπέρθεσις)**. Likewise at their evening rising they will be **weaker and obstructive, showing only appearances and hopes**.*

**A retrograde time-lord defers rather than denies.** A distinct verdict from affliction, and one we do not currently make. Directly applicable wherever a Lord of the Year is retrograde.

## ⭐⭐ IV.16 — TOPICAL RELEASING: release from the place you are asking about, p. 185

> *And this reasoning naturally holds, that **from EACH PLACE the significations or the releases of the years should be made**: for instance **from the MIDHEAVEN when we inquire about ACTION**, and **from the place concerning MARRIAGE when about a WIFE**, and from the place concerning slaves when about bodies, and likewise **from the place concerning CHILDREN**.*

**Releasing is not restricted to Fortune and Spirit.** For a topical question you release **from that topic's own place**. This is the technique that answers "when, for *this* subject" rather than "when, in general" — and it is exactly what our customers keep asking for and what we have never given them.

Combined with IV.4 and II.19 (Fortune → body, Spirit → mind and action), the full picture is:

| Question | Release from |
|---|---|
| Body, health, circumstance | **Lot of Fortune** |
| Mind, career, eminence, action | **Lot of Spirit / Daimon** |
| Action and standing specifically | **Midheaven** |
| Marriage | **the 7th place** |
| Children | **the 5th place** |
| Any topic | **that topic's own place** |

**Engine change #23** — the ZR machinery already exists; it needs a `release_from` parameter rather than being hard-wired to the two lots.

## ⭐ IV.16 — the ὑπόστασις limits what any period can do, p. 184

> *First it is necessary to recognise the **FOUNDATION (ὑπόστασις) and the RANK of every nativity** … so that we do not speak of the outcome as though for the greater and the glorious alike, **but distinguish**.*
>
> *When we find a **notable and brilliant foundation preserved by the testimony of the benefics**, with **malefics holding the times** in the chronological handings-over, or coming by ingress upon the angles or busy places — **we say the nativity will suffer nothing out of place**; but the affairs will be **managed disorderly**, and it will incur notoriety or blame, and come into gloom and fears.*

**The natal baseline caps the timing.** A strong foundation under bad times produces disorder and anxiety, **not catastrophe**; and by the same logic a weak foundation under good times does not produce greatness. Timing modulates within the range the nativity already set.

This is the doctrinal answer to the commonest failure in predictive astrology — reading a hard transit as though it meant the same thing in every chart. Valens forbids it explicitly: *"not as though for the greater and the glorious alike, but distinguish."*

## ⭐⭐ IV.17–IV.20+ — the handing-over delineations, pp. 189 ff.

The operational payload of the whole timing system: **every planet handing the time to every other**, plus the Ascendant as a giver. Roughly 56 combinations, each with witness conditions.

**IV.17 — the Sun as giver:**
- **Sun → Saturn**: *makes the year **toilsome***; ineffectiveness, oppositions, enmities, disputes, **harms from superiors or elders**, uprisings of subordinates, **diseases of the eyes**, irregularities of livelihood, envied movements, and **the death of the father or of one like a father**. Falling badly: accusations and confinements.
- **Sun → Jupiter**: *a **brilliant** year* — reputation of the father, associations with superiors, prosperity, gifts, **notable actions or offices**, zeal for children, **marriages**.

**IV.18 — the Moon as giver:**
- **Moon → herself**: *unpleasant* — enmities and lawsuits from greater persons, counter-actions of relatives **or of a wife**; with a malefic beholding, bodily weaknesses and dangers.

**IV.19 — the Ascendant as giver:**
> ***The Ascendant handing over to a MALEFIC makes the worst time — especially to SATURN BY NIGHT and to MARS BY DAY*** — bodily dangers, irregularities of livelihood, fears, troublesome accusations, falls or injuries.

**⭐ Note what that specifies: Saturn *by night*, Mars *by day* — in each case the OUT-OF-SECT malefic.** Not "malefics are bad," but "the malefic contrary to sect is worst." Sect governs the timing verdict exactly as it governs the natal one. Rule #1 again, now in the predictive layer.

- **Asc → Jupiter**: brilliant and acquisitive; reputations, notable ranks, benefit from superiors; *some, delivered from dangers or accusations, become well-consoled; some experience **freedom***.
- **Asc → Venus**: good and beneficial; associations and **involvements with women**, purchases, gladness, **deliverance from evils**.
- **Asc → Moon**: practical; **benefits from women**, associations, renewals, **successful travels** — *especially if benefics witness; if malefics, the contrary, and disturbances besides*.
- **Asc → Mercury**: practical and successful; *but if harmed by malefics, subject to **lawsuits and loss***.

**IV.20 — Saturn as giver:**
- **Saturn → himself**: harassments and ineffectiveness; enmities and dishonours from **greater or elder persons**; obstructive to undertakings, and whatever is arranged will be unstable. *With Mercury and Mars beholding*: trouble over **writings**, overturnings of old or death-related matters, deceits.
- **Saturn → Sun**: danger or death of the father; otherwise weakness of livelihood.

**Structure worth noting for implementation:** every entry has the same shape — a base verdict for the pair, then modifiers for **who witnesses**, then a fallback for **"falling badly."** Same three-part shape as the natal delineations. The engine already computes giver, receiver, and witnesses for each profection and Firdaria transition; this is the missing text layer, and it is large but mechanical.

## ⭐ IV.25 — the four lots as time-lords, p. 201

Not just Fortune and Spirit — **Fortune, Daimon, Eros and Necessity** each hand over and receive.

- **Fortune** in busy places with benefics → good fortune, advancement of action, reputation, affairs.
- **Daimon** in busy places with benefics → successes, resolutions, judgment, **well-directed reasonings**, profitable counsel of friends, associations with superiors, gifts, reputation. **Fallen or witnessed by malefics** → *elevations of mind and **psychic torments**, insensibility and contrary counsels — **thinking their own errors to be successes and laying the causes on others**, while failing at most things.*
- **Eros** in busy places with benefics → **well-chosen desires and lovers of the beautiful**; some turn to education, bodily training or music; others, *charmed by love-affairs and intimacies*, count female and male companions as goods.
- **Necessity** in busy places with benefics → familiarities, greater associations, **the overthrow or death of enemies**; with malefics → lawsuits, judgments, expenditures, *"whence, having acted against their own choice, they pass life in distress."*

**The afflicted-Daimon delineation is the most psychologically specific thing in the work** — mistaking one's own errors for successes and blaming others. Worth having, and it is the Spirit lot, which our engine already computes.

## IV.26–IV.30 — four more timing subdivisions, pp. 202–205

- **IV.26 — a 28-year cycle "according to Critodemus":** *Moon 1st, **1 year**; Mercury 2nd, **2**; Venus 3rd, **3**; Sun 4th, **4**; Mars 5th, **5**; Jupiter 6th, **6**; Saturn 7th, **7** — **making 28 years**.* Entry point set by the **monomoiria**: the lord of the sign the Moon occupies takes first, then the rest in Chaldean order.
- **IV.27 — the release may begin from any of four points:** *the **Sun**, the **Moon**, the **Ascendant**, or the **Lot of Fortune**.* Attributed to Seuthes/Hermeias. Another confirmation that the starting point is a choice, not a fixed rule (cf. IV.16's topical releasing).
- **IV.28 — the month:** *from the handing-over Sun to the natal Sun, and the same from the sign allotted the year.* Monthly profection.
- **IV.29 — the transacting day:** years brought down × 5 or 4, plus days from the birthday.
- **IV.30 — quarter-divisions of the periods:** *Saturn 30, the quarter **7½**; Jupiter 12, the quarter **3**…* — subdividing each planetary period into fourths for finer timing.

**Together with ZR, profection, Firdaria, II.27's angle-handover and III.11's climacterics, Valens carries at least eight distinct timing systems.** He does not rank them. That is itself worth telling a reader: the tradition's answer to "when" was never one method.

## ⭐ IV.13 — handing-over judged by dignity relationship, p. 181

> *A handing-over **from EXALTATION to EXALTATION**, with benefics present or witnessing, is **glorifying and beneficial** — especially if the lords are in their own place. Likewise **from their own houses to their own exaltations**, or from exaltations to their own houses. But handing over **from FALL to FALL**, they become **moderate and irregular**.*

The transfer between time-lords is graded by the **dignity relation between the giving and receiving signs** — a third dimension on top of angularity (IV.11) and the condition of both lords (IV.7).

### Valens's oath, p. 173
The famous passage binding the reader:

> *I adjure you, my most honoured brother, and those **initiated into this treatise**, by the circle of the stars of heaven … and the **Sun and Moon and the five wandering stars, through which the whole of life is driven**, and by **Providence herself and holy Necessity** …*

Context worth keeping: this sits immediately after a long first-person digression on his own hardships and the cost of the work. It is the clearest evidence that the *Anthologiae* is a working teacher's book addressed to a named student, not a treatise for publication — which bears on why its transmission is so uneven.

---

# COVERAGE MAP

**Read and extracted** (printed pages; PDF = printed + 18):

| Chapter | pp. | Content |
|---|---|---|
| Praefatio | I–XX | Kroll's manuscript history; "Desunt plura" |
| I.1 | 1–5 | **Planetary natures, sect, colour, taste; ⭐ the conditional benefic/malefic rule; the six configuration operations** |
| I.2 | 5–14 | **The twelve signs; ⭐ the four Thema Mundi angles** |
| I.3 | 14–19 | **⭐ All sixty bound delineations; Egyptian boundaries verified for all 12 signs** |
| I.4–I.5 | 19–21 | Finding the Ascendant (computational) — skimmed |
| II.1 | 54–56 | **⭐ Triplicity rulers verified against `DOROTHEAN_TRIPLICITY`; water fork triple-attested** |
| II.2 | 56–57 | **⭐ Fortune-judging procedure and the two-ruler life arc** |
| II.3–II.4 | 59–62 | **⭐ ✅ Lot of Fortune day formula; lord-of-ASC / lord-of-Fortune delineations** |
| II.5–II.14 | 62–68 | **The places; benefics neutralised in 2nd/6th/8th/12th** |
| II.15 | 69 | **⭐ The nine named places — a topical fork against Paulus** |
| II.16 | 69–75 | Aspect-pair delineations (**pp. 76–79 not yet extracted**) |
| II.22 | 87–90 | **⭐ Eminence procedure — six tests** |
| II.23–25 | 90–92 | Lots of debt, theft, ambush |
| II.27 | 94–95 | **⭐ Time-distribution; separate significators for life vs action** |
| II.28–29 | 96–101 | Travel; Lot of Travel formula (Hermippus, Abraham) |
| II.37 | 114–117 | **⭐ Marriage (pp. 118–121 not yet extracted)** |
| II.39–II.41 | 122–128 | **Children, siblings; violent death (read, not for use)** |
| III.1–III.3 | 132–139 | **⭐ Epikratesis, busy degrees, aphesis, the destroyers and ±3° orb** |
| III.4–III.5 | 140–141 | **⭐ ✅ Exaltation degrees verified; hayz/sect-rejoicing** |
| III.7–III.8 | 142–144 | Critodemus: hostile places and degrees |
| III.12–III.16 | 150–157 | **⭐ Valens attacks the popularisers; conception; ✅ all 21 planetary-year values verified + the mean formula; climacterics** |
| IV.1–IV.7 | 158–167 | **⭐⭐ ✅ ZR sign-years DERIVED (Cap 27 / Aqu 30); Loosing of the Bond; Fortune=body / Spirit=mind; handing-over doctrine** |
| IV.10–IV.11 | 170–175 | **⭐⭐ Zodiacal Releasing defined; annual profection; Valens's oath** |

| I.5–I.24 | 20–54 | Computation; **⚠️ two different "Lord of the Year"**; **masc/fem degree fork**; **⭐ I.21 planetary pairs**; **⭐ I.22 triads + rule #1 as method**; gestation limits |
| II.3–II.4 | 59–62 | **⭐ ✅ Fortune day formula; lord-of-ASC/Fortune delineations** |
| II.17–II.20 | 79–82 | **⭐⭐ Fortune as a SECOND ASCENDANT; ✅ Lot of Exaltation; Fortune=body/Spirit=mind; περιποίησις = 11th from Fortune** |
| II.30–II.36 | 101–114 | Parents, orphanhood, separation; **⭐ eleven lunar phases → topic → ruler**; injury (excluded) |
| II.38 | 119–121 | **⭐ Lot of Marriage, sex-differentiated** |
| III.9–III.11 | 144–150 | **⭐⭐ Valens's OWN bound system (sect-dependent, includes the lights)**; climacterics 7→Mars, 9→Saturn |
| IV.11–IV.13 | 176–181 | **⭐⭐ definitive ranking of places; rules of handing-over; a THIRD topical table; παράδοσις by dignity** |

**NOT yet read** — roughly 240 of 423 printed pages:

- **I.6–I.24** (21–54) — chart computation by hand, conception, seven-month births. Mostly computational; low priority except **I.11 Lord of the Year (27,1)** and **I.21–22 planetary mixtures and triads (37,11–50,4)**, the latter partly read at pp. 42–45.
- **II.3–II.4** (59–62) — **Lot of Fortune and its lord**. High priority; Fortune is load-bearing throughout.
- **II.17–II.21** (79–87) — Ascendant of Fortune, exaltations and eudaimonia, worked examples.
- **II.30–II.36** (101–114) — parents, orphanhood, **separation of parents**, free/slave births, the **eleven Moon configurations**.
- **III.4–III.11** (138–150) — sect of the stars, Critodemus material, **climacterics: sevenfold and ninefold cycles**.
- **IV.1–IV.9** (156–170) — the rest of Book IV's timing apparatus, immediately before the ZR chapter.
- **IV.12 onward and Books V–IX** (175–423) — distribution, transmission of times, and the bulk of the ~130 worked example charts.

**Highest-value unread, in order:** IV.1–IV.9 (the ZR apparatus around the chapter already read) → II.3 Lot of Fortune → III.11 climacterics → II.30–33 parents → I.21–22 planetary mixtures. Bounds verified all twelve signs; Dorothean triplicities verified in full; water-triplicity fork now triple-attested.
**Next:** II.11–15 remaining places (66,8–69,16), II.16 aspects (69,17), II.3 Lot of Fortune (59,19). Then Book II.22 eminent vs obscure (87,5), II.27 time-distribution (94,16), II.37 marriage (114,19). Then Book III.1 epikratesis and III.3 aphesis.

## I.22 — Περὶ σχηματισμῶν κατὰ πλείους (Configurations of several planets), pp. 41–45

Valens delineates planets **in threes**. Sect and configuration qualifications are attached. This is a delineation layer our engine does not compute at all.

Read so far (pp. 42–45):

- **Κρόνος Ζεὺς Ἄρης** (Saturn Jupiter Mars) — produce mixtures of good things: some renowned, high-priestly, leading, procuratorial, presiding over crowds and districts or over military affairs, commanding and being obeyed; adorned not so much by the outward show of life, but led about by oppositions, accusations and violent affairs; some adorned in substance of life and masters of possessions and foundations, and benefiting from the dead, but lesser in reputation. Judgment is made according to the positions and the energies of the signs.
- **Κρόνος Ζεὺς Ἀφροδίτη** — good and beneficial in actions, acquisitive; producing associations of men and women, and friendships and advancements, and benefactions from the dead; but blameworthy and envied in their habits, and irregular about unions, enduring chills in season, and enmities or judgments. Yet friendly and sociable, delighting in new and many friendships; but as to the account of children and bodies, not throughout stable, nor enduring without grief.
- **Κρόνος Ζεὺς Ἑρμῆς** — practical, economical, trustworthy, presiding over crowds, commanding and obeyed, managers of money and directors of accounts or votes. Such men possess a liberal **and hypocritical** character: sometimes they appear knavish and villainous, sometimes good and noble; they will become desirers of what belongs to others and [exhorted or] grasping, for whose sake they endure disturbances or judgments, and debts and public notoriety.
- **Κρόνος Ἄρης καὶ Ἥλιος** — *indicative of violent, alien and dangerous affairs*; for they produce men rash and reckless in their actions, malefactors, godless, traitors, insubordinate, hating their own, separated from their own people and consorting with foreigners; coming to be amid abuse and dangers, enduring falls from a height or from four-footed beasts, or fears of burnings; toilsome in their undertakings, not guarding what surrounds them, alien in their desires; from evils they provide — unless the figure be military or athletic — and so laborious, though not ineffectual.
- **Κρόνος Ἄρης Σελήνη** — reckless in their undertakings and noble, but hard to succeed in their actions and beset by oppositions and violent affairs; for they become violent, quarrelsome, malefactors, rapacious, having a robber's manner, falling into judgments amid defences, and taking trial of accusation and imprisonment — unless somehow the nativity be contentious or war-loving, so that by the holding of this figure the fulfilment may be borne. Some then become notorious or passionate, and accomplish a violent end.
- **Κρόνος Ἄρης Ἀφροδίτη** — as to actions and friendships they deal from the first as though beneficial, forming reputations and associations; but afterwards they are set up as assailants and plotters through certain rivalries and betrayals, on whose account they make accusations and enmities toward both male and **female persons**; they endure blame and reproach, or are turned about in adulteries, and take on notoriety and terrors. Some, then, by unlawful minglings and indifferent, turn back unabashed — becoming partners of evildoing or of poisonings, they endure the fear of what may come.
- **Κρόνος Ἄρης Ἑρμῆς** — produce villainies and treacheries, judgments and disturbances, on account of written or secret matters; guarantors who endure contests for others, and demotions; otherwise sharp and shrewd in their actions, passing life variously and…
- **Κρόνος Ἀφροδίτη Ἥλιος** — indicative of great associations and honours and actions, causes of reputation and prominence and crowd-leadership; but unenduring both as to acquisition and as to the rest, and they dissolve their friendships through irregularities, and work out diminutions of life and terrors or losses on account of female persons, and betrayals of secret matters; and as to minglings and intercourse, unstable and indifferent.
- **Κρόνος Ἀφροδίτη Σελήνη** — bring on irregularities and instabilities of life, especially as to the place concerning wife and mother and children; for they bring on ingratitudes and gracelessnesses, and there are enmities and factions, separations, blame, terrors, unlawful minglings; but as to actions not resourceless, easily inventive and coming to be in circumstances, benefited by the dead, yet not preserved by many, or themselves conscious of malefaction or poisonings, and transgressors against women.
- **Κρόνος Ἀφροδίτη Ἑρμῆς** — intelligent, thoughtful, and concerning actions unerring and prosperous, well-lettered, accomplishing their first actions and desirers of others, much-learned, meddlesome, various, medical, pleasing; new in innovation and in change and in foreignness. If in these matters the figure be badly disposed, or Mars overlook, on account of poisonings or female persons or occasions of death, disturbances and judgments befall them, and they take on unjust diminutions of life and captivities.
- **Ζεὺς Ἥλιος Σελήνη** — renowned, brilliant, widely-known…
- **Ζεὺς Σελήνη** — successful in attainment, bold, public men, having many friends, coming to advancement and raised from small fortune, deemed worthy of trust; military, athletic, renowned, leading, presiding over crowds and districts, receiving honours and salaries or priesthood; suffering opposition and falling into accusations and betrayed by their own or by female persons, and enduring diminutions from those who surround them, and afterwards surrounded by secret or unexpected affairs.
- **Ζεὺς Ἄρης Ἑρμῆς** — practical, hot, agitated; in public places or in military ranks obtaining high offices, doing kingly and political things; irregular as to life and consumers of their surroundings, well-disposed and trustworthy stewards, easily setting right their faults; but they bring on themselves other causes of blame, being reckoned malefactors and falling into oppositions. Some then athletic, crown-bearing, or ascetics of the body, much-learned, lovers of ornament, or in a foreign land making provision, and to their own men foremost.
- **Ζεὺς Ἄρης Ἀφροδίτη** — having many friends and living together amiably, producing associations of the greater sort and deemed worthy of benefits, coming to be in advancements, promoted by women; some then of high-priestly rank…

Further triads read (pp. 46–49): Jupiter–Mercury–Sun, Jupiter–Mercury–Moon, Jupiter–Mercury–Venus, Jupiter–Venus–Sun, Jupiter–Venus–Moon, Venus–Sun–Moon, Venus–Mars–Moon, Mercury–Sun–Moon, Mercury–Venus–Moon, Moon–Mercury–Venus, Mercury–Mars–Venus, Mars–Sun–Moon, Mars–Sun–Venus, Mars–Sun–Mercury, Mars–Moon–Mercury. Representative:

- **Jupiter–Mercury–Moon** — *good, acquisitive, well-aimed in action; collectors of gifts, receiving trusts; **mystical, intelligent, rational**; guardians of deposited property, **advanced from words and reckonings**; lenders, hirers, much-befriended, much-known, guardians, managers of affairs, generous.*
- **Mars–Sun–Moon** — *bold, manly, daring, practical; **athletic and military**, ruling, leading; providing from violent and toilsome matters and from hard crafts — but **caught up in dangerous affairs** and coming into greater enmities and accusations, **except if benefics somehow configured preserve the foundation**.*
- **Mars–Moon–Mercury** — *energetic, mechanical … **initiates of hidden things and privy to unspoken matters**; but violent, insubordinate, desirers of others' goods, falling into accusations and dangerous affairs, enduring disturbances over **writings and money**.*

### ⭐ And then Valens states rule #1 as method, p. 49

> *And these things we have added **as single-form and universal distinctions**. But when other mixtures are also considered — whether by **co-presence or by co-witnessing**, according to the star's nature and the **topical determination** — **the power of the matters will be altered**.*
>
> *…It is set out in this treatise **how one ought to compare the star's placement**: how it is configured — whether **angular, oriental, setting, rising, lord of the triangle** — and likewise **the signs in which they happen to be, whether their own or of their own sect**.*

This is the methodological statement underneath everything: **the delineation lists are the raw material; placement transforms them.** He says outright that he kept the combination lists short because the ancients had already covered them, and that what *this* treatise contributes is the comparison procedure. Any use of Valens that quotes his delineations without running his placement tests is using the half of the book he considered least original.

## I.23–I.24 — conception and seven-month births, pp. 50–54

> *Three limits existing — **least, mean and greatest** — the excess of each is 15 degrees … the **least is 258 days**, shown after the setting degree, that is with **the Moon in the descension**; the **mean 273**, with **the Moon on the Ascendant**; the **greatest 288**, with **the Moon in the setting**.*

Three gestation intervals tied to the Moon's position at conception — the **Trutine of Hermes** family. I.24 treats seven-month births as a separate case.

**Status:** I.22 complete (pp. 41–50); I.23–I.24 read.

---

## Books V–IX — structure map (2026-08-11)

Read for scope, not full transcription. Filenames in the composite batch run 18 pages ahead of the true Kroll page (`printed = filename − 18`) — confirmed by reading the printed folio number off the scan itself, not assumed. Anyone resuming this batch should recompute from the scan, not the filename.

**Book V (Kroll pp. 209–238)** — corrects the earlier estimate of "209–229"; it runs longer. Aitionology (the causative place), climacteric years, ecliptic places. This is the chapter that grounds the climacteric technique already in the engine (Valens III.15) — worth cross-checking III.15 against V's fuller statement next pass.

**Book VI (Kroll pp. 239–262).** 9 chapters. VI.9 (pp. 260–262) is a second statement of the Trutine-of-Hermes gestation technique already read at I.23–I.24 — not a new technique, a restatement. VI.5–7 give a decennial + 9-month chronocrator subdivision distinct from the IV.16 releasing already implemented. **Not currently in the engine** — flagged as a gap, not built.

**Book VII (Kroll pp. 263–294).** At least 5 chapters (II–IV titles fall in an unscanned gap, pp. 265–280 — a real gap, not filled). VII.5 gives klima-conditioned (latitude-band) decennial tables. Contains a full worked nativity, "the defeated woman" (τῆς ἡττηθείσης γυναικός, p. 285) — one of Valens's own example charts. Colophon styles the book "πρὸς Δάφνην," distinct from the "to Marcus" address used elsewhere.

**Book VIII (Kroll pp. ~295–328).** Start page and several chapters unconfirmed (gaps at pp. 295–296, 303–320, 323+ — unscanned). Contains κανόνιον/πλινθίον degree-mapping boards tied to Nechepso/Petosiris "organa." No discursive nativity found in the sampled pages, but the gaps mean this isn't conclusive.

**Book IX (Kroll pp. 329–362).** 19 chapters. Prooimion (329–330) is autobiographical: Valens names predecessors (Nechepso's 13th book, Critodemus, Timaeus, Asclation) and describes his own travels ("πελαγοδρομήσας... κλιμάτων τε καὶ ἐθνῶν κατόπτης γενόμενος"). IX.7 (pp. 341–342) treats **sex-determination and teratology of nativities** — a topic not seen in Books I–VIII and **not currently implemented** in the engine. IX.11 (pp. 353–354) is a doxography of rival solar-year theories (Euctemon, Philippus, Aristarchus, the Chaldaeans, Nechepso, plus apparatus citations of Sudines, Kidenas, Hipparchus) — historically valuable, not doctrine to implement.

**End of the Anthologiae proper: Kroll p. 362** (IX.19). What follows (pp. 363–372, "Additamenta vetusta") is a **later scribal appendix, not Valens's text** — proven by internal evidence: it contains a dated nativity for Valentinian (b. 25 June 419), three centuries after Valens wrote. It has its own colophon and its own internal two-book numbering. Do not cite it as Valens. An Index Verborum follows from ~p. 383 to the end of the scanned volume.

**Open gaps, recorded rather than guessed:** VI cap. I's exact heading; VII cap. II–IV titles; VIII's start page and cap. I–II/IV/VI+ titles; IX cap. V, VI, X, XII, XVI, XVII titles. All fall in unscanned page ranges within the current composite batch, not places the reader looked and found nothing.

**Not yet reflected in `verified_rules`:** nothing in V–IX has been transcribed to delineation-level detail yet, so no registry entries change from this pass. This is a scope map for the next reading session, not a verification.

---

## V.2 read in full — a second, distinct climacteric technique (2026-08-11)

Offset re-verified directly against the scan's own printed folio (reads "209"/"210" in the running head) — confirmed, not assumed.

**Gap, recorded not guessed:** V.1's opening/defining passage (Περὶ αἰτιαστικοῦ τόπου) falls on printed pp. 207–208, outside the pulled scan range. Only the tail of V.1 (p. 209, judging a "dynastic place" by malefic/benefic testimony) was read. Needs pp. 207–208 (PDF ~225–226) before any claim about V.1 is treated as settled.

**Title correction:** V.2's heading reads Περὶ ἐνιαυτοῦ κλιμακτηρικοῦ καὶ ἐκλειπτικῶν τόπων καὶ **καταρχῶν** ("...and catarchic beginnings") — not "κατοχῶν" as an earlier structure-mapping pass had it. Valens distinguishes this from the dedicated chapter III, Περὶ καταρχῶν, immediately following.

**V.2's method, read from Kroll p. 210** — this is a **different climacteric technique from III.15**, not a restatement:

> *A climacteric year is found from the malefics' reception or transmission toward the luminaries and the ascendant, and toward one another; but generally, thus: one must always release the years from the ascending sign. If the year so brought down terminates in the sign of the [preceding] conjunction or full moon, or in their squares or oppositions, the year is climacteric and disturbed — especially if, these conditions holding, transiting Saturn is also found in one of the four cadent places from the nativity.*

Mechanism: (1) annual profection from the **ascendant** — a sign per year of age; (2) the profected sign is checked against the **pre-natal syzygy** (last New or Full Moon before birth) and its square/opposition signs; (3) the year is climacteric if they coincide, and worse if **transiting Saturn** sits in one of the four cadent places that year.

**III.15 (already implemented, `src/services/reading_evidence.py:908`)** derives climacteric *periodicity* from a malefic's aspect to the **Lot of Fortune** — a static natal figure, no profection, no transit, no syzygy. The two share only the label "climacteric." Implementing V.2 does not touch III.15's code path; it is additive.

**Not yet built:** V.2 requires three pieces the engine doesn't currently compute for this purpose — the profected-ascendant sign for a given age, the pre-natal syzygy sign, and a transiting-Saturn-in-cadent-house check for the queried year. None of the three is present under `valens_lot_climacterics`.

---

## V.1 read in full — the causative place, a Lot not currently in the engine (2026-08-11)

Folio-verified: p0225-0226.png right page carries the "Liber V" opening header and "cap. I," continuing directly into p0227-0228.png (209/210, already read). The chapter opens by referring back to earlier books' treatment of sect, then introduces this place as tested "from experience" (ἐκ πείρας).

**Construction, from Kroll ~p. 207–208** — a Lot, built the same way Fortune and Spirit are:

- By day: the Saturn→Mars arc, projected forward from the Ascendant.
- By night: the Mars→Saturn arc, projected forward from the Ascendant.
- A variant Valens attributes to "others" (ἄλλοι): the same arc projected from Mercury instead of the Ascendant.

Valens states its function directly: "responsible for fears and dangers and bonds/imprisonments" (φόβων καὶ κινδύνων καὶ δεσμῶν παραίτιος). Once located, the astrologer checks whether it falls in a malefic's own sign, or whether Saturn/Mars apply to or aspect it — that testimony is what turns the place from background risk into an active threat of confinement.

**Not currently in the engine.** This is a distinct Lot construction, unrelated to Fortune/Spirit/Daemon and unrelated to III.15's Lot-of-Fortune climacteric check. Building it would need: sect-conditional arc (Saturn→Mars day, Mars→Saturn night), projected from the Ascendant, plus the Mercury-based variant Valens flags as an alternate school. Then a malefic-testimony check identical in shape to the one already used for III.15's climacteric figure — reusable code, new Lot.

V.1's tail (p. 209, already read) covers severity grading — how compromised the place is, from mere anxiety through to actual imprisonment, depending on the strength of malefic testimony against it.

---

## VI.5–7 read — a third chronocrator technique, distinct from IV.16 releasing (2026-08-11)

Folio-verified against the scan's own running heads: VI.5 at pp. 251–253, VI.6 at pp. 253–254, VI.7 at pp. 254–256.

**VI.5** introduces the method as one Valens says he personally recovered — "cast aside... because its points of entry are riddling" — not an established technique he's merely repeating. It partitions life into consecutive blocks of **10 years, 9 months**, each block ruled by a planet in sequence from the sect light (Sun by day, Moon by night), cycling through the seven until the queried span is reached.

**VI.6** subdivides each major block proportionally among all seven planets, down to months/days/hours — a nested sub-period inside each major period, structurally analogous to how zodiacal releasing has L1/L2/L3 but built on fixed calendar durations rather than sign-traversal. Worked example given: Saturn's ~2y6m block splits into seven sub-slices (Saturn 6mo29d, Jupiter 2mo27d, Mars 3mo14d, Sun 4mo12d, Venus 1mo25d, Mercury 4mo19d, Moon 5mo24d — summing back to 2y6m).

**VI.7** gives an arithmetical shortcut to find which planet governs a given calendar date without walking the whole period table sequentially: convert elapsed days using a 365¼-day year, reduce by cycles of 129 days, and the remainder locates the position in the planetary sequence.

**Distinct from IV.16 (zodiacal releasing, already implemented):** this technique is pure calendar/day-count division assigned to planets in a fixed rotation — no signs, no Lots, no "loosing of the bond." It is a separate time-lord system Valens presents as a real find of his own, not a restatement of releasing under different arithmetic.

**Not currently in the engine.** Building it needs: the 10y9m major-period cascade from the sect light, the proportional VI.6 subdivision formula, and the VI.7 modulus shortcut for date lookup. None of the three pieces overlaps with the existing `valens_zodiacal_releasing` code path.

Chapter VIII (length-of-life from the full-moon/horoscopic gnomon) begins at p. 257, visible in the same scan set but not yet read.

---

## VI.8 read — length of life from the full-moon/horoscopic gnomon (2026-08-11)

Kroll pp. 257–259, folio-verified. Valens frames this as harder than finding the target facts themselves: judging death-timing precisely. Method combines two reference points as "gnomons" — the pre-natal full moon's degree and the Ascendant degree — and examines which releasing/destructive places (ἀφετικοὶ καὶ ἀναιρετικοὶ τόποι) fall near them by star, sign, or bound. He explicitly criticizes rival methods using "complicated numeric combinations" as false precision. A square/opposition distance rule between Ascendant and Moon degrees judges "deadly" testimonies (p. 258). Not a single output — a diagnostic framework, closer in spirit to how the engine already treats testimony-counting than to a mechanical formula. Chapter IX (Trutine of Hermes restatement, already logged) follows at p. 260; Book VI closes at p. 262.

Not yet assessed for engine gap status — needs comparison against existing longevity/prorogation code before building.

---

## Built: V.1, V.2, VI.5-6 (2026-08-11)

All three techniques found in this reading pass are now in the engine.

**V.1 causative place** — `src/engine/lots.py`, `LotName.CAUSATIVE_PLACE`. Sect-conditional Saturn/Mars arc from the Ascendant. Emitter reports the sign and whether a malefic owns it; where neither does, it says Valens's own activation test is silent rather than asserting the place is active.

**V.2 syzygy climacteric** — `src/engine/valens_periods.py::climacteric_year`. Profected ascendant against the pre-natal syzygy sign and its hard figures, with transiting Saturn in a cadent place as the aggravating witness Valens names.

A property of this rule worth stating plainly, because it looks alarming otherwise: it marks four signs out of twelve, so the climacteric years fall on a **fixed three-year lattice for every chart** — only the offset varies. A native will always have roughly thirty marked years in a ninety-year span. The count is arithmetic, not a measure of how hard a life is, and the interpretive limit says so.

A test locks the asymmetry Valens's own wording implies: transiting Saturn is a witness to a climacteric year, not a cause of one. A cadent Saturn in an unmarked year must not manufacture a climacteric, or the technique would fire on about a third of all years by itself.

**VI.5-6 decennial cascade** — `src/engine/valens_periods.py::decennial_cascade`. 129-month major periods subdivided by `minor_years / 129`.

**Why this could be implemented confidently from a single reading:** the arithmetic self-verifies. The seven minor years sum to 129, and 129 months *is* the 10-years-9-months period VI.5 names — the same fact stated twice. Subdividing by that ratio reproduces six of the seven figures in Valens's own worked Saturn example to the day. Jupiter is the exception (computed 2m23.7d against a transcribed 2m27d) and is recorded as a probable OCR slip on the numeral rather than smoothed away; six independent agreements outweigh one disagreement, but the disagreement stays visible in the code comment and the test docstring.

**What is NOT verified, and is flagged everywhere it surfaces:** which planet opens the L1 sequence. VI.5's opening lines were not read closely enough to settle it. The engine configures it from the sect light, and `starting_planet_verified: False` rides in the payload, the interpretive limit, and an assertion — so a configured default cannot harden into a sourced claim. The period *lengths* are exact; the *ruler order* is provisional.

**VI.7's shortcut is not built.** Its arithmetic (reduce elapsed days by cycles of 129) was read but not pinned down well enough to implement. `decennial_ruler_at_age` walks the cascade instead, which reaches the same answer without guessing at the modulus.

---

## VII.2-4 read — the Book VII gap closed (2026-08-11)

Folio-verified against the scan's own running heads (p0291-0292.png reads "273"/"274", not the assumed 265-266 — the earlier structure map's page estimates were off by several pages within Book VII, corrected here). Chapter I in fact runs through p. 266, not ending at p. 264 as first mapped.

**VII.2** (Kroll pp. 267–271), Ἀγωγὴ δευτέρα περὶ χρόνων διαιρέσεως πρὸς τὰς τῶν ζωδίων ἀναφορὰς καὶ τὰς τῶν ἀστέρων περιόδους — a second chronocrator method, opened as "a more detailed division, discovered through experience and toil" (ἐκ πείρας καὶ πόνου). Combines the rising-times (anaphorai) of the zodiacal signs with planetary period-numbers. Several worked nativities. Closes with a quoted Cleanthes fragment on fate.

**VII.3** (Kroll pp. 272–273), Ἀγωγὴ περὶ χρόνων ζωῆς πρὸς τὸν κλῆρον τῆς τύχης καὶ τὸν τούτου κύριον — **a fourth technique built from the Lot of Fortune**, distinct from every other Fortune-based method already read this session: II.22's acquisition-place split, III.15's climacteric periodicity, and IV.4-7's releasing. This one computes life-periods from Fortune's own degree and its ruling planet's period-years directly — no releasing arithmetic, no aspect-to-malefic test. Opens with a striking preface asking whether the ancients concealed prognostic method "out of envy" (φθόνῳ) or simply never grasped it. One full worked example given (Aphrodite/Aquarius ascendant, klima ε′).

**VII.4** (Kroll pp. 274–276), Ἀγωγὴ λεπτομερεστέρα καὶ περὶ χρόνων ἐμπράκτων καὶ ἀπράκτων πρὸς τὰς ἀναφορὰς καὶ τὰς περιόδους τῶν ἀστέρων — VII.2's method refined to monthly resolution, distinguishing active (ἔμπρακτοι) from inactive (ἄπρακτοι) periods. Notes that neighboring co-rulers ("synmerizontes") modify outcomes, and that period boundaries need precise determination.

**Running tally of Fortune-based timing techniques found in Valens: four.** None of VII.2-4 is implemented. Not assessed for build priority — recorded for the next pass.

---

## Book VIII read — the two instruments, and twin rectification (2026-08-11)

Folio-verified: filename offset confirmed at exactly 18 here (p0313-0314.png reads printed 295/296, checked again on the next two composites). Note this held for Book VIII but did NOT hold cleanly inside Book VII — verify per batch, do not carry an offset across books.

**Book VIII begins at printed p. 295**, Οὐεττίου Οὐάλεντος Ἀντιοχέως ἀνθολογιῶν βιβλίον η΄.

**VIII.1** (pp. 295–296), Πῆξις τοῦ α΄ ὀργάνου — construction of the "first instrument," a degree-by-degree numerical table across the zodiac. Base numbers per degree, increments (παραυξήσεις), and additions of 14 units. Assigns every degree of every sign a number, with signs sharing sets (Libra/Leo/Pisces one set, Aries/Virgo another, Scorpio another). Chronocratic scaffolding, not a house technique.

**VIII.2** (pp. 296–297), Πῆξις τοῦ δευτέρου ὀργάνου φυσική — the astronomical rationale behind those numbers plus a second instrument. Valens identifies the 14 additions with the Moon's lights and the 2 increments with the Sun's digits, resolves a chain of divisions to 360 (one year), then extends year by year at 2°20′ each. Explicitly derivational: he says he thought it necessary to append "the derivation of its construction" after setting out its management.

**VIII.3** (pp. 297–299) — fixing the horoscopic degree against the two instruments. **VIII.5** opens at p. 300.

**VIII.4** (pp. 299–300), Πῶς χρὴ τῶν διδυμογόνων τὴν γεννητικὴν ὥραν ἱστάνειν — **rectification for twins**, and a real gap. Valens tabulates which reported hour-pairs are astronomically possible and which are not: first twin reported at hour 1 and second at hour 3 reads as hour 3½; hour 1 and hour 7 as hour 6½; hour 1 and hour 9 as hour 9. Some pairs he flags outright as **οὐ δυνατόν, not possible** — no such interval can have occurred — and supplies the corrected substitute. Closes by noting twins can be born within the same quarter-hour, and that the hour's steep slope (ὀξυρροπία) shifts the degree.

**Not implemented, and neither is the other one.** The engine mentions "rectification" only as a caveat — text telling the reader a longevity figure is unusable and *needs* rectification — while implementing no rectification technique at all. Valens supplies two: the Trutine of Hermes gestation rule (I.23–24, restated VI.9) and this twin table. Both absent.

---

## Book IX gaps closed — and a pattern worth acting on (2026-08-11)

Folio-verified (offset 18 here, confirmed on three separate composites).

**IX.5** (pp. 339–340), Περὶ κατακλίσεως καὶ καταρχῶν — decumbiture and inceptions. Count days from the pre-natal syzygy to the birth day, cast out tetraeterides (four-year units), repeat from the current year's syzygy to the birth date and again to the day the person took to bed, then compare residues: coincidence is judged fatal, divergence indicates danger from disease. Valens then generalises the same reasoning to the inception of **any** undertaking — building dedications, leading armies, generalships, city-commands. Closes with a polemic against charlatans (γόητες) who claim to answer everything from one inception and deceive people about lifespan, preferring brief truthful judgment from the temperamental and angular constitution.

**IX.6** (pp. 340–341), Περὶ εὑρέσεως ὡροσκοποῦντος ζῳδίου καὶ μοίρας ὡροσκοπούσης — rectification: recovering an unknown ascendant sign and degree. Several alternatives, each marked Ἄλλως, including one "toward forced rectification" (πρὸς ἀναγκαστικὴν ἀγωγήν) using the Sun's position in the syzygy sign against the Moon's prosneusis.

**IX.10** (pp. 351–352), Ἀγωγὴ περὶ ὡροσκόπου μοίρας — a second, independent ascendant-degree method, which Valens says he is disclosing against his predecessors' practice: he names **Petosiris**, who "set things out mystically to the king," and credits **Thrasyllos**. Uses the Sun-to-Moon arc converted to oblique ascensions against a solar gnomon and the climate's rising-times table; agreement confirms the reported hour, excess or deficit says how far the ascendant must move.

### The pattern

**Valens supplies at least four rectification techniques and the engine implements none of them:**

| technique | location | status |
|---|---|---|
| Trutine of Hermes (gestation) | I.23–24, restated VI.9 | not built |
| Twin hour-pair table | VIII.4 | not built |
| Ascendant recovery | IX.6 | not built |
| Ascendant degree via gnomon | IX.10 | not built |

Meanwhile the engine's own longevity output tells the reader a failed figure "requires rectification and primary-direction validation" — advice it cannot act on, because "rectification" appears in the codebase only as that caveat string. A reader who follows the instruction has nowhere to go.

**IX.5's katarchai layer is a separate matter**, and larger: it is inceptional/electional judgment, which this project deliberately keeps off the nativity (cf. the Lilly horary split). Recorded, not proposed.
