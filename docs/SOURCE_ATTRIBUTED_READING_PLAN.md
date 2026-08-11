# Plan: The Source-Attributed Reading

**Started:** 2026-08-02
**Owner decision that set the direction:** *"I want to show — according to your chart, this is what the original source text would have told you, if you had the master astrologer of that tradition. And I want to explain why we're telling them that: you are this or that, because this book says this."*

---

## 1. The goal, stated plainly

Every sentence a customer reads should be traceable to (a) a computed fact about their chart, and (b) a named rule from a named text with a chapter and page.

**We are not practitioners.** We do not counsel, we do not soften, and we do not decide what a reader is allowed to know. We transmit what the sources say, show the derivation, and let the reader judge whether the tradition is true.

**Interpretation, where it exists at all, is marked and separated** — never blended into the source material so the reader can't tell which is which.

### The format we're aiming for

Instead of:
> Money and belonging carry weight, delay and conditions.

We want:
> **Saturn in the 2nd house, out of sect**
> *Rule — Ptolemy, Tetrabiblos I.7 (Diurnal and Nocturnal):* in a night chart Saturn is contrary to sect, and its testimony is aggravated.
> *Rule — Paulus Alexandrinus, Introductory Matters ch. 24 (The Twelve Places):* the 2nd place signifies livelihood and movable resources.
> *Your chart:* Saturn at Sagittarius 18°28′, 2nd place, night birth.
> *Therefore, by these rules:* the out-of-sect malefic governs your livelihood.
> *[Commentary — ours, not the sources']:* in practice this reads as delay rather than denial.

---

## 1b. SOURCE POLICY (owner decision, 2026-08-02)

**"I only want to use the old texts. I don't want other people's opinions or interpretation."**

### The rule
Doctrine comes from the historical authority itself. Modern commentary, popularisations, and secondary interpretation are excluded as sources — they may be used privately as finding aids, never cited as doctrine.

A translation of Ptolemy is still Ptolemy. A modern astrologer explaining what Ptolemy meant is not.

### Tier 0 — the original languages (best available; started 2026-08-02)
**This is now the preferred tier. Work from it wherever the text exists.**

| Text | Location | Status |
|---|---|---|
| **Ptolemy, Greek** (Boll–Boer Teubner critical edition) | `docs/research/multitradition/hellenistic/sources/ptolemy_apotelesmatika_boll_boer_teubner_djvu.txt` | Book I ch. 7, 14, 19, 20 translated; ch. 21 opened. See `docs/sources/ptolemy_greek_book1.md` |
| **CCAG** vols 1, 5.1, 8.1, 8.3, 8.4 | `docs/research/multitradition/byzantine/sources/` | not started |
| **Lydus, *De Ostentis*** | same directory | not started |
| **Ibn Ezra, Hebrew** (facing pages in Sela) | `tmp/ibn_ezra_nativities_revolutions_sela.txt` | not started |

Three reasons this outranks Tier 1:
1. **No copyright at all.** The Greek is ancient; our English is our own work and is quotable without restriction.
2. **No translator between us and the author.** Our Ashmand edition is Ashmand's English of *Proclus' paraphrase* — Ptolemy at two removes. The registry has always said so in `edition_limit`; the Greek removes both layers.
3. **Ptolemy almost always says *why*.** English versions keep the rule and drop the argument. The argument is the more valuable half for a source-attributed reading.

### Tier 1 — quotable verbatim (old, public domain)
| Text | Status | Covers |
|---|---|---|
| **Lilly, *Christian Astrology* (1647)** | English **original**, PD | planets, twelve houses, dignities, reception, degree qualities, hyleg |
| **Ptolemy, *Tetrabiblos* (Ashmand 1822)** | PD translation | sect, aspects, triplicities, terms, prorogation |
| **al-Bīrūnī, *Book of Instruction* (Wright 1934)** | PD translation | Firdaria, hayz/halb, years tables |

### Tier 2 — technique usable, wording NOT quotable (in copyright)
Dorotheus (Pingree/Houlding — marked "personal study use only"), Ibn Ezra (Sela), Firmicus (Bram 1975), Paulus (Schmidt), Valens (Schmidt/Riley).

A **method** is arithmetic and free to implement. Only a translator's English is protected. So: compute the technique, describe it in our own words, cite chapter and page — never reproduce the translation.

### Tier 3 — excluded entirely
Modern commentary and popularisations. Specifically `docs/research/Binder1.txt`, which is AI-generated reports citing web pages, contains two corrupted planetary-years tables, and attributes web paraphrases to Ptolemy and Valens. **Leads only. Never a source.**

### Known consequences
- Paulus's twelve places (the classic Hellenistic house source) is unquotable AND its OCR is destroyed. **Lilly p.95 covers the same ground and is quotable** — use it.
- Zodiacal Releasing interpretation is thinner without quotable Valens. Mechanics are unaffected.
- [ ] Confirm al-Bīrūnī/Wright 1934 PD status per jurisdiction before commercial verbatim use.

---

## 2. Design principles

1. **No claim without a citation.** If we can't name the text, chapter and page, it doesn't go in the customer-facing layer.
2. **Where authorities disagree, show the disagreement.** Never silently pick one. (The engine already emits `doctrinal_disagreements` — use it.)
3. **Separate the layers visually.** Rule / Chart fact / Derivation / Commentary.
4. **A failing technique is removed, not softened.** Longevity is out because it failed testing, and that standard applies to everything.
5. **Alarming language must be sourced.** Most doom-language in astrology software comes from modern popularisations, not the texts. Lilly, Valens and al-Bīrūnī hedge constantly. If a scary line can't be traced to a primary text, it's cut.

---

## 3. What already exists and is verified

- [x] **Astronomy** — all positions cross-checked against GERMES to the arcminute, including UT conversion for a 1987 Kazakhstan birth
- [x] **Both bound tables** (Egyptian and Ptolemaic) — verified digit by digit, all 12 signs × 5 bounds
- [x] **All seven Hermetic lot formulas** including day/night sect reversal — verified against Paulus ch. 23
- [x] **Decennials** — 129-month invariant enforced in code, verified against Valens
- [x] **Zodiacal Releasing** — sign-years verified including the Capricorn 27 / Aquarius 30 asymmetry
- [x] **Annual profections** — verified against Paulus ch. 31
- [x] **Planetary joys, dodecatemoria, monomoiria** — verified against Paulus
- [x] **Doctrine registry** — 28 rules with edition, chapter and page in `src/database/data/doctrine_sources.json`
- [x] **Chart wheel** — rebuilt with glyphs, element bands, houses, aspects; mirror bug fixed
- [x] **Fixed in this session:** Hyleg altitude gate (was rejecting luminaries in 75% of charts), years-class inversion, modifier units error, `Unknown Gives 0 Years` placeholder

## 3b. Known broken / removed

- [x] **Longevity (Hyleg/Alcocoden/Anareta)** — REMOVED from customer output. Failed on 11 of 20 charts with known death dates. Do not reinstate without passing that test.
- [ ] **`sefstars.txt` not installed** — fixed-star positions fall back to linear precession from a 2025 epoch. Accurate to well under an arcminute, but install the real catalogue when convenient.
- [ ] **"Foreshadowing" ZR status** — a configured label currently published under a Valens citation. Either source it or relabel it.
- [ ] **ZR uses 360-day years** for L1/L2 boundaries; dates run ~5 days early per released year. Needs a source check.
- [ ] **Valens-variant Eros/Necessity** appear swapped in `lots.py` (dead code, no callers).
- [x] **Water triplicity fork — RESOLVED 2026-08-02 from Ptolemy's Greek (I.19).** Ptolemy says both received answers in one sentence: the triangle "was left to Mars," *and* the Moon co-rules by night and Venus by day *with him*. Water is his only three-ruler triangle. Our `(Venus, Moon)` sect-split is correct and Lilly's Mars is correctly held in its own table. **Remaining gap:** the two-slot structure cannot hold Mars as a water ruler in both sects, so that dignity goes unscored — needs a third optional slot, not a change to the existing two.
- [ ] **Mercury's sect was never resolved in readings** — fixed 2026-08-02 in `multitradition/hellenistic.py`. Ptolemy I.7 makes it determinate from the solar phase (morning → diurnal, evening → nocturnal); the engine computed the phase but printed "common" and stopped. Audited the other sect call sites: `horary.py:1260`, `trace_generator.py:330`, `hellenistic_report.py:224` and `free_reading_generator.py:188` all enumerate only the six fixed-sect planets and simply omit Mercury — a coverage gap, not a false claim. **One open case:** `byzantine_report.py:150` prints "Mercury is common to both" from a *Rhetorius* rule pack. Do NOT paste Ptolemy's resolution in there — that is tradition-blending, the same error as the old hybrid water triplicity. It needs Rhetorius' own text, or it stays as it is.

---

## 4. Phase 1 — The stress/activation timing engine

**The customer question that prompted this:** *"which periods will test the union, where the likelihood of a crisis is higher, and where an opportunity to strengthen the relationship arises."*

**What we will NOT build:** a probability-scored crisis calendar. No source produces one. Inventing a percentage and attributing it to Valens would violate principle 1.

**What we WILL build:** a mechanical activation table. Which significators are difficult *in this chart, by stated rule*, and which years activate them.

### The derivation (already prototyped and working)

- [x] **Step 1 — identify the difficult significators by rule**
  - Sect: out-of-sect malefic is aggravated → Ptolemy I.7
  - Essential dignity: peregrine / detriment / fall → Lilly, dignity tables pp. 104-117
  - Affliction by aspect: square, opposition, conjunction from malefics → Ptolemy I.16
- [x] **Step 2 — identify the difficult places** → Paulus ch. 24 (6th, 8th, 12th)
- [x] **Step 3 — compute when each is activated**
  - Annual profections → Paulus ch. 31
  - Firdaria major and sub-periods → al-Bīrūnī §395
  - Zodiacal Releasing L1 → Valens, Anthology IV.4-7
- [x] **Step 4 — count convergences** (how many difficult significators are active in the same year)

### Refinements still needed

- [ ] **Weight repetition, don't dedupe it.** Current prototype uses a `set()`, so a year where Venus is *both* Lord of the Year *and* Firdaria major scores the same as one where it appears once. That hides the most saturated years. **2041 is the clearest example** — Venus as Lord of the Year, Venus as Firdaria major, profected to the 7th house which Venus rules. That should rank at the top for a relationship question and currently doesn't.
- [ ] **Add ZR level 2** sub-periods, not just the 30-year L1 chapters
- [ ] **Add topical filtering** — "show me relationship years" should filter to the 7th house, its lord, and Venus; "work years" to the 6th/10th and their lords
- [ ] **Add the monthly profection** layer within a flagged year
- [ ] **Cite every row** — each activation line should carry the rule that produced it

### Prototype output (verified working, 2026-2060)

Years where three or more difficult significators activate:
- **2028** (age 41) — Firdaria Sun; sub-period Venus; profected to the 6th
- **2034** (age 47) — Lord of the Year Venus; Firdaria Sun; profected to the 12th
- **2040** (age 53) — Firdaria Venus; sub-period Saturn; profected to the 6th

Relationship-specific (7th house profections with Venus as Lord): **2029, 2041, 2053** — with 2041 doubled by the Venus Firdaria.

---

## 5. Phase 2 — Retrofit the reading into source-attributed format

- [ ] Define the four-part block structure (Rule / Chart fact / Derivation / Commentary) in the composer
- [ ] Map every existing composer section to its registry rule id
- [ ] Flag any section that has **no** citable rule — these are the ones we either source or cut
- [ ] Render the commentary layer visually distinct (sidebar, indent, or different type)
- [ ] Surface `doctrinal_disagreements` inline where the fork affects that specific chart

## 6. Phase 3 — Make it the product, not a one-off

- [ ] Everything above currently runs as hand-driven scripts for one customer. It needs to be in the composer so every reading gets it.
- [ ] Decide the free/paid boundary (owner decision, still open)
- [ ] Add `fonts-dejavu-core` to the Dockerfile so non-Latin PDFs render in production

### Location-based pricing (purchasing-power parity)

**Why:** $20 was priced as $20-in-California. The Kostanay customer paid $20 in Kazakhstan, where median monthly wage is roughly $300-400 — proportionally equivalent to a US customer paying $80-100. That is not what we intended to charge, and we found out only because the owner did the mental arithmetic after the fact.

- [ ] Detect buyer country at checkout (Stripe already returns it on the session; also available from request geo / Cloudflare headers)
- [ ] Define price tiers by purchasing power rather than by a flat USD figure. Options to evaluate:
  - World Bank PPP conversion factor
  - Big Mac index style simple banding (3-5 tiers)
  - Stripe Adaptive Pricing (may handle this natively — check first, cheapest path)
- [ ] Decide whether to show local currency at checkout as well
- [ ] **Never price *up*** for wealthy regions without a deliberate decision — the goal is not to extract more, it's to stop overcharging people in lower-income countries
- [ ] Confirm the tier is applied server-side in `guest_checkout.py` where `price_cents` lives (single source of truth, self-healing against Stripe)
- [ ] Consider grandfathering: anyone who already paid the flat rate from a lower-tier country is owed the difference or a refund

---

## 7. Open questions for the owner

- [ ] **Free or paid?** Still undecided. Note: the two most recent sales both delivered flawlessly (10s and 16s), and that customer bought twice and praised the methodology unprompted.
- [ ] **How much commentary, if any?** The spec says minimal and separated. Zero is also viable.
- [ ] **Translations** — the Russian attempt failed integrity checks (the cheap model summarised instead of translating). Needs a stronger model and smaller chunks if we revisit.

---

## 8. Standing notes

- **Customer pronouns:** do not infer gender from names. The Kostanay customer was assumed male from the payment name and is not. Reports are written in second person, which avoids the problem entirely — keep it that way.
- **Both Kovalev orders were refunded** by the owner on 2026-08-02, despite both having delivered successfully.
- **Tariq Taher (9 July)** — genuine fulfilment failure, make-good PDF generated at `artifacts/customer-makegood-20260715/`, refund status to confirm.
- **The Python on the deploy image is 3.10.** PEP 701 f-strings (nested same quotes, backslash in expression) crash the build. Gate locally with:
  `py -V:"Astral\CPython3.10.19" -m compileall -q src`
- **CI gates deploy** — a failed test run means `deploy_cloud_run` is skipped, so prod never receives a broken build.
