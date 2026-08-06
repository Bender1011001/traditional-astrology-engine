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
