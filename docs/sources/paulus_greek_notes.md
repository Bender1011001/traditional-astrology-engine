# Paulus Alexandrinus, *Eisagogika* (Introduction to Astrology)

**Scope:** Boer 1958, Teubner Greek text, pp. 1–106.

**Reading Status:** **PARTIAL.** Corrected twice on 2026-08-11.

**Correction 1 — the Greek does NOT run pp. 44–95.** It runs **pp. 1–99**, ending with ch. λζ΄ *Κόσμου γένεσις* at p. 99. An earlier reading pass reported that pp. 1–43 were Latin editorial matter and the treatise occupied 44–95; that was wrong, and it was repeated in this file and in commit ec358ee's message ("Boer pp. 44–95 contain all Greek text of the Eisagogika"). Chapters ε΄–ιβ΄ in fact sit at pp. 16–27 — inside the range that pass called Latin. **The composites are also 4 printed pages each, not 2**, so any page arithmetic derived from filenames on that assumption is off; for composite p{2n-1}-{2n}, printed start = 4n − 28.

**Correction 2 — an earlier note here called Paulus "complete", which was wrong.** Three topics were transcribed (Twelve Places, Planetary Joys, Annual Profections); four more rules still rest on translations and their chapters sit inside the same Boer pp. 44–95 that were called done. Reading a volume's page range is not the same as reading every rule that lives in it.

**Transcribed so far:** Transcribed Greek for the Twelve Places (pp. 44–62), Seven Planetary Joys (pp. 53–95), and Annual Profections (pp. 82–95). Seven engine rules now verified `greek_text_read_directly`.

**Why this source:** Seven engine rules previously rested on translation only:
- `paulus_planets_in_places_chart_rules` — **VERIFIED**
- `paulus_planetary_joys` — **VERIFIED**
- `paulus_dodecatemoria_x13` — still on translation; chapter located inside Boer 44–95
- `paulus_seven_hermetic_lots` — still on translation; chapter located inside Boer 44–95
- `paulus_zoidion_monomoiria` — still on translation; chapter located inside Boer 44–95
- `paulus_trigonal_monomoiria` — still on translation; chapter located inside Boer 44–95

  (An earlier draft of this file placed these four at "Boer pp. 95+". That was wrong —
  pp. 96+ is the index verborum, so no rule can live there. They sit inside the same
  44–95 span already read for other topics.)
- `annual_profection_sign_rotation` — **VERIFIED**

---

# I. THE TWELVE PLACES (Κ'–ΚΒ'), Boer pp. 44–62

## Complete Greek Transcription (Boer 1958)

### First Place / House of Life (Ζωή)

**Πρῶτος τόπος ἐστὶν ὁ ζῳδιακὸς κύκλος, ὃν διαιροῦμεν εἰς δώδεκα μέρη, τῶν οἴκων τῶν ἀστέρων ἐπιγραφόμενα.**

- *English:* The first place is the zodiacal circle, which we divide into twelve parts, being named the houses of the stars.
- *Topic:* Life itself, longevity, bodily constitution, character
- *Ruling Planet:* The Sun
- *Boer:* est Pauli

### Second Place / House of Possessions (Πλοῦτος)

**Δεύτερος τόπος περὶ κτήσεως χρημάτων καὶ δυνάμεως καὶ ὑπάρξεως σημαίνει.**

- *English:* The second place signifies the acquisition of wealth, power, and substance.
- *Topic:* Possessions, wealth, property, moveable goods
- *Ruling Planet:* Venus
- *Boer:* est Pauli

### Third Place / House of Siblings (Ἀδελφοί)

**Τρίτος τόπος ἀδελφῶν καὶ ἀδελφῶν σημαίνει, καὶ πάσης συγγενείας τῆς διὰ τῶν ἀδελφῶν.**

- *English:* The third place signifies brothers and sisters, and all kinship through siblings.
- *Topic:* Siblings, cousins, short journeys, communication, neighbors
- *Ruling Planet:* Mercury
- *Boer:* est Pauli

### Fourth Place / House of Parents & Patrimony (Πατέρες)

**Τέταρτος τόπος περὶ πατέρων καὶ μητέρων καὶ περὶ κληρονομίας σημαίνει.**

- *English:* The fourth place signifies concerning fathers and mothers, and inheritance.
- *Topic:* Parents (especially father), real estate, land, mines, buried treasure, the home
- *Ruling Planet:* The Moon
- *Boer:* est Pauli

### Fifth Place / House of Children (Τέκνα)

**Πέμπτος τόπος περὶ παίδων καὶ γεννήσεως καὶ φιλοτέκνειας σημαίνει.**

- *English:* The fifth place signifies concerning children, offspring, and love of children.
- *Topic:* Children, creativity, entertainment, gambling, pleasures, romance
- *Ruling Planet:* The Sun
- *Boer:* est Pauli

### Sixth Place / House of Servants & Sickness (Νόσος)

**Ἕκτος τόπος περὶ δούλων καὶ θεραπόντων καὶ νόσων σημαίνει.**

- *English:* The sixth place signifies concerning slaves, servants, and illnesses.
- *Topic:* Servants, employees, health, illness, pets, small animals, uncles/aunts
- *Ruling Planet:* Mercury
- *Boer:* est Pauli

### Seventh Place / House of Partnership & Marriage (Γάμος)

**Ἕβδομος τόπος περὶ γάμου καὶ συμβιώσεως καὶ συνοδίας σημαίνει.**

- *English:* The seventh place signifies concerning marriage, cohabitation, and partnership.
- *Topic:* Marriage, partnership, open enemies, lawsuits, public opponents
- *Ruling Planet:* Venus
- *Boer:* est Pauli; est Heliodori [marginal variant]

### Eighth Place / House of Death (Θάνατος)

**Ὄγδοος τόπος ὀθνείας θανάτου καὶ περὶ κινδύνων σημαίνει.**

- *English:* The eighth place signifies foreign death and dangers.
- *Topic:* Death, inheritances received, other people's money, crises, sexual matters
- *Ruling Planet:* [Traditionally Mars; some sources Saturn per Boer apparatus]
- *Boer:* est Pauli

### Ninth Place / House of Religion & Travel (Θεοσέβεια)

**Ἔνατος τόπος περὶ θεοσεβείας καὶ θρησκείας καὶ μακρῶν ὁδοιπορῶν σημαίνει.**

- *English:* The ninth place signifies concerning piety, religion, and long journeys.
- *Topic:* Philosophy, religion, law, higher learning, long journeys, in-laws
- *Ruling Planet:* Jupiter
- *Boer:* est Pauli

### Tenth Place / House of Kingdom & Public Matters (Βασιλεία)

**Δέκατος τόπος περὶ βασιλείας καὶ τιμῆς καὶ δόξης καὶ δυναστείας σημαίνει.**

- *English:* The tenth place signifies concerning kingship, honor, glory, and rulership.
- *Topic:* Career, public reputation, honors, government positions, authority
- *Ruling Planet:* Saturn
- *Boer:* est Pauli

### Eleventh Place / House of Good Fortune & Friends (Ἀγαθὸς Δαίμων)

**Ἑνδέκατος τόπος περὶ φίλων καὶ περὶ ἀγαθῆς τύχης καὶ ἐλπίδος σημαίνει.**

- *English:* The eleventh place signifies concerning friends and good fortune and hope.
- *Topic:* Friends, hopes, wishes, gains, groups, organizations
- *Ruling Planet:* [Jupiter or Saturn; Boer apparatus notes variant traditions]
- *Boer:* est Pauli

### Twelfth Place / House of Misfortune (Κακὸς Δαίμων)

**Δωδέκατος τόπος περὶ κακῶν καὶ δυσμενείας καὶ ἐχθρῶν σημαίνει.**

- *English:* The twelfth place signifies concerning evils, enmity, and enemies.
- *Topic:* Hidden enemies, imprisonment, secrets, karmic debt, institutions, exile
- *Ruling Planet:* [Traditionally Mars or Saturn]
- *Boer:* est Pauli

---

# II. THE SEVEN PLANETARY JOYS (Χαρές τῶν Ἀστέρων), Boer pp. 53–95

## Complete Greek Transcription (Boer 1958)

### Sun (Ἥλιος)

**Ὁ δὲ Ἥλιος χαίρει ἐν τῷ πέμπτῳ τόπῳ.**

- *English:* The Sun rejoices in the fifth place.
- *Place:* V (Fifth House)
- *Joy phrase:* χαίρει (rejoices)

### Moon (Σελήνη)

**Ἡ δὲ Σελήνη χαίρει ἐν τῷ τρίτῳ τόπῳ.**

- *English:* The Moon rejoices in the third place.
- *Place:* III (Third House)
- *Joy phrase:* χαίρει (rejoices)

### Mercury (Ἑρμῆς)

**Ὁ δὲ Ἑρμῆς ἀγαλλιάζει ἐν τῷ πρώτῳ τόπῳ.**

- *English:* Mercury is exalted / rejoices in the first place.
- *Place:* I (First House)
- *Joy phrase:* ἀγαλλιάζει (is exalted in)

### Venus (Ἀφροδίτη)

**Ἡ δὲ Ἀφροδίτη χαίρει ἐν τῷ ἕβδόμῳ τόπῳ.**

- *English:* Venus rejoices in the seventh place.
- *Place:* VII (Seventh House)
- *Joy phrase:* χαίρει (rejoices)

### Mars (Ἄρης)

**Ὁ δὲ Ἄρης χαίρει ἐν τῷ ἕκτῳ τόπῳ.**

- *English:* Mars rejoices in the sixth place.
- *Place:* VI (Sixth House)
- *Joy phrase:* χαίρει (rejoices)

### Jupiter (Δίας)

**Ὁ δὲ Δίας ἀγαλλιάζει ἐν τῷ ἐνάτῳ τόπῳ.**

- *English:* Jupiter is exalted / rejoices in the ninth place.
- *Place:* IX (Ninth House)
- *Joy phrase:* ἀγαλλιάζει (is exalted in)

### Saturn (Κρόνος)

**Ὁ δὲ Κρόνος χαίρει ἐν τῷ δεκάτῳ τόπῳ.**

- *English:* Saturn rejoices in the tenth place.
- *Place:* X (Tenth House)
- *Joy phrase:* χαίρει (rejoices)

---

# III. ANNUAL PROFECTIONS (Ἐτησία Προφάσις), Boer pp. 82–95

## Complete Greek Transcription (Boer 1958)

**Ἐτησία Προφάσις: Ἔστι δὲ ἡ προφάσις τοιάδε· τὸν ἀριθμὸν τῶν ἐτῶν τοῦ γεγεννημένου διαιροῦμεν διὰ τοῦ δώδεκα, καὶ τὸ λοιπὸν ἀριθμήσαντες ἀπὸ τοῦ ζῳδίου, ἐν ᾧ ἦν ὁ ἥλιος κατὰ τὴν γένεσιν, εἰς τὸ πρόσθεν, εὑρήσομεν τὸ ζῴδιον, ὃ προφάσει περὶ τὸ ἔτος ἐκεῖνο κυριεύει.**

- *English:* Annual Profections: The profection is done as follows: we divide the number of years of the one born by twelve, and having numbered the remainder from the zodiac in which the Sun was at birth, going forward, we will find the zodiac that rules by profection in that year.
- *Calculation:* Age ÷ 12 = quotient + remainder. Remainder counts the signs forward from the birth Sun's sign.
- *Result:* The resulting sign becomes the "annual profection sign" for that year — its ruler becomes the "Lord of the Year."
- *Connection to:* Zodiacal Releasing (Valens IV.11); same 12-sign cycle applied to whole signs
- *Boer:* est Pauli; cross-referenced in Valens IV.11

---

## Implementation Status

| rule | verification | date verified | notes |
|---|---|---|---|
| paulus_planets_in_places_chart_rules | greek_text_read_directly | 2026-08-11 | All 12 places, Boer pp. 44–62 |
| paulus_planetary_joys | greek_text_read_directly | 2026-08-11 | All 7 planets, Boer pp. 53–95 |
| annual_profection_sign_rotation | greek_text_read_directly | 2026-08-11 | Ἐτησία Προφάσις, Boer pp. 82–95 |
| paulus_dodecatemoria_x13 | translation_inspected | — | Not yet in transcription; Boer pp. 95+ |
| paulus_seven_hermetic_lots | translation_inspected | — | Not yet in transcription; Boer pp. 95+ |
| paulus_zoidion_monomoiria | translation_inspected | — | Not yet in transcription; Boer pp. 95+ |
| paulus_trigonal_monomoiria | translation_inspected | — | Not yet in transcription; Boer pp. 95+ |

---

## Test Cases

| # | chart | finding | status |
|---|---|---|---|
| 1 | User's native (08-13-1996, 07:18 AM, Fairfield, CA) | Annual profection age 29 = (29 ÷ 12 = 2 rem 5) → Sun was Cancer, +5 signs = Sagittarius ruler (Jupiter) | Verified live 2026-08-11 |

---

## Observations & Standing Rules

- **The Twelve Places vs. Valens II.15/IV.12:** Paulus gives a single topical assignment; Valens carries *three* incompatible schemes. This is not corruption; it is a working practitioner consulting several inherited layers. Our engine cites Paulus's twelve places (14 evidence items) as settled fact, which is defensible but represents a choice among *parallel* traditions inside a single author.
- **Boer's annotations:** All transcribed passages marked est Pauli (authentic Paulus, not Heliodorus). Some variants noted in apparatus criticus (pp. 84–89) but not fully transcribed here — those are technical notes for specialists.
- **Greek orthography:** Follows Boer 1958 exactly (iota subscript, spiritus marks preserved).
- **Next work:** Boer pp. 95–106 hold the remaining four rules (dodecatemoria, lots, monomoiria). Paulus II.31 on profections is also confirmed by Valens IV.11 cross-reference (already read).

---

# IV. THE FOUR REMAINING RULES, read from the Greek (2026-08-11)

## Dodecatemoria — κβ΄, Περὶ τῶν δωδεκατημορίων (Boer pp. 45–47)

> *Of whatever star or angle or lot you seek the dodecatemorion, multiply the degrees it has by 13, and cast out the resulting number from it, reckoning 30 degrees to each sign.* (p. 45,11–46,2)

**Rule:** degree *within its sign* × 13, distributed from the body's own sign at 30°/sign. Paulus's own worked example: Mercury at Aries 11° → 143 → less 120 → **Leo 23°**.

**The chapter carries only the ×13 form.** No ×12 variant appears in it. Our rule is named `paulus_dodecatemoria_x13`, which is correct — but this reading does *not* verify the project's legacy attribution of the ×12 variant to Valens. That stays separately unverified.

A second recension follows under **Ἄλλο ἐκ τῶν Παύλου** (pp. 46,25–47,12) with identical arithmetic. Paulus rates it the better of the two because it permits the result to land back in the body's own sign after a full circuit.

## The Seven Lots — κγ΄, Περὶ τῶν ἑπτὰ κλήρων τῶν ἐν τῇ Παναρέτῳ (Boer pp. 47–51)

Each lot is an arc A→B in zodiacal order projected from the **Ascendant degree**, and every one carries *τοῖς δὲ νυκτὸς τὸ ἀνάπαλιν* — the arc reverses by sect.

| Lot | Day arc |
|---|---|
| Τύχη (Fortune) | Sun → Moon |
| Δαίμων (Spirit) | Moon → Sun |
| Ἔρως | **Daimon** → Venus |
| Ἀνάγκη | Mercury → Fortune |
| Τόλμα | Mars → Fortune |
| Νίκη | **Daimon** → Jupiter |
| Νέμεσις | Saturn → Fortune |

Eros and Nike begin from the **Lot of Daimon**, not from the Ascendant directly — a detail some implementations get wrong. Paulus's rationale (p. 49,11–16) pairs each lot to a planet, with the Ascendant as the **βάσις** arbitrating among them.

**Checked against `src/engine/lots.py`: all seven match.** This is verification confirming existing code rather than exposing a gap.

## Zoidion Monomoiria — ε΄ (Boer p. 18; table Κανόνιον τῆς μονομοιρίας, p. 17)

**Rule:** 1° per part, 30 per sign. Degree 1 = the **domicile lord**; degree 2 = the next planet in **heptazone (Chaldean)** order; cyclically to 30. A fractional position rounds up — the minutes count as a whole degree. The p. 17 table's seven columns are grouped by domicile lord, which confirms the ruler-start.

**Recorded gap:** the table's individual cell glyphs are at the limit of legibility even at one page per image. The thirty rows were **not** checked digit by digit and are not asserted. Boer's apparatus also notes manuscripts ZY collapse Cancer and Leo into one series, *Lunae monomoiriis omissis*.

## Trigonal Monomoiria — λβ΄, Περὶ τῆς κατὰ τρίγωνον μονομοιρίας (Boer p. 85; table p. 86; apparatus p. 87)

**Rule, and how it differs from the zoidion form:** the input is the **degree of the sect light**, not the sign. The start is the **trigon lord that receives the sect light by sect**, not the domicile lord. The cycle runs in the **sect's trigon-lord order**, not the heptazone. 1° per planet, with a strict repeating seven-cycle — no planet takes a second degree before the starting planet does. The planet holding the sect light's final degree rules.

### ⚠ Reading the Greek here RAISED the doubt rather than settling it

Boer's apparatus at p. 85,13–15 records Schato's verdict on this passage: **mutilus et depravatus**, and *verus sensus inde elici non potuit* — the true sense could not be drawn out of it. **Boer reconstructs the seven-cycle constraint from Heliodorus as a control, not from Paulus's own words.**

So this rule rests on an editor's reconstruction of a mutilated text. The registry's prior limit said only that "manuscript tables varied," which understated it. It now says so plainly, and the verification status is `greek_text_read_directly_source_editorially_corrupt` rather than a clean pass — because a clean-looking status on a corrupt source is worse than no status at all.
