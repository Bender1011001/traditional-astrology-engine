# HANDOFF — Full Project State

**Written:** 2026-08-02; **section 0 updated:** 2026-08-16
**Read this first.** It assumes no prior context. Companion documents: `docs/DEVELOPER_HANDOFF.md` (run / edit / ship) and `docs/SOURCE_ATTRIBUTED_READING_PLAN.md` (the forward plan).

---

# 0. STATE AS OF 2026-08-16

Claude's source session ended at `07a132e` (Firmicus II.26). This file was not updated that day; this block is the compact resume. How-to: `docs/DEVELOPER_HANDOFF.md`. The day's finding: `docs/sources/THE_CONDITION_RULE.md`. Notes: `ptolemy_greek_book1.md`, `firmicus_notes.md`, `picatrix_notes.md`, `ACQUISITIONS.md`.

**Shipped and live.** Valens V.1 causative place, V.2 syzygy climacteric, Lilly reception fortitudes. Mansions 12 and 24 were serving another mansion's electional advice; fixed in `src/engine/mansions.py`. The birthday-triggered test was rewritten. Suite was 1252 green at session end.

**Product.** The free edition is natal character + life-so-far, no future; the $20 report has time lords and the books.

**Acquisition.** All 37 `verified_rules` have an original-language source on disk. al-Biruni: Wright 1934 English plus the Persian *Tafhim* critical edition (not the Arabic facing MS the registry cites). Ibn Ezra: LJS 57 (Catalonia 1361) — *Reshit Hokhmah*, *Sefer ha-Mivharim*, *Sefer ha-Olam*, **not** *Sefer ha-Moladot* or *Sefer ha-Tequfah*. Claude cannot read the 14th-c. Sephardic semi-cursive; those two Ibn Ezra rules stay `parallel_text_and_translation_inspected`.

**Do not implement without Andrew.** Ptolemy III.11 benefic rescue (Jupiter 12° / Venus 8°). The doctrine is sourced; the payload lacks the anaretic degree's longitude; the window is directional on the killing degree, not a symmetric orb on the hyleg; *parapodiseis* (παραποδίσεις) means annotate the candidate as hindered, do not delete it. Same architecture at III.13, III.15, and Firmicus III.25 / IV.19 / IV.21. Implementing this changes published longevity figures and makes some readings harder, not softer.

**Retracted — do not re-open.** The claim that the engine "cites Ptolemy while running Paulus house topics." A live report's topical houses cite no authority. The Ptolemy mentions are doryphory, Algol, and the already-disclosed dignity-table forks.

**Settled — do not "fix."**
- Night Fortune: Ptolemy does not reverse; Dorotheus, Paulus, and Firmicus do. `lots.py` follows the majority.
- Egyptian terms: Ptolemy's totals, Valens, and Firmicus all match ours.
- Water triplicity: confirmed from Greek I.19.
- Ptolemaic Gemini terms: Lilly / MS D vs Boll–Boer. The author's own totals favor Boll–Boer. The constant is `_LILLY1647` — do not silently rename it.
- The Algol entry was already correct (constellation nature + IV.9 in `nemesis`).

**Open. Pick one; do not resume by transcribing unread volumes.**
1. The condition-rule gate (six attestations, zero code).
2. III.11 rescue plumbing (anaretic longitude first).
3. Book I derivations in the report — why Saturn rules Capricorn, etc. Already written in the notes. Commercially useful.
4. Chart lord: Firmicus prefers the lord of the Moon's next sign, not the Ibn Ezra almuten. Surface the method. Do not silently switch.
5. Decennials: Firmicus says the sect light opens (confirms our default) but orders from the sect light's sign, not the Ascendant. Valens VI.5 is still unread on that point. Do not change `decennials.py` yet.
6. Firmicus Book III planets-in-houses: unused, **equal houses** (not whole-sign), and `_PROTECTED_DIRECTIVE` will block his second-person counsel.
7. Picatrix intents; Dorotheus Virgo/Mercury share (no stated weight); Lilly Regulus +6 / Spica +5; a printed Hebrew Reshit Hokhmah.

**Standing failure mode from this session.** A negative result from a partial check is not a fact about the world. Say "I have not found it yet." Four false unavailable claims; three were caught only because Andrew pushed.

---

# 0. STATE AS OF 2026-08-11

**Deployed and verified live.** `ef862ec` is on Cloud Run. Verification was done against a **baseline captured from prod before the deploy**, not against a green check: `Marriage_7th` / `Children_5th` / `Action_10th` went 0 → 2 in `/api/v1/charts/calculate-full`, healthz uptime reset, and a **real guest reading was generated through the customer flow** (18,703 words) and confirmed to contain the I.3 closing rule. Do it this way — a passing deploy job does not prove the revision took.

**Held back deliberately:** the email-verification feature (stashed, `git stash list`). Registration withholds the JWT and emails a link to `/verify-email.html`, **a page that does not exist in the repo**. Shipping it breaks all new signups. It needs that page written and SMTP confirmed. The `email_verified` / `verification_token` columns are already on main, so there is no migration hazard.

**A second deploy is pending** for the bound renderer and registry fix described below — the live revision emits the bound delineations but does not print them.

---

# 0b. STATE AS OF 2026-08-10

**A large source-fidelity pass landed.** Roughly 250 pages of Valens (Kroll 1908) and four chapters of Ptolemy (Boll–Boer) were read **directly from the Greek**, and **all 27 resulting engine changes are implemented** with 40 regression tests in `src/tests/test_valens_greek_corrections.py`.

**Read these three files before touching the engine:**

| File | Holds |
|---|---|
| `docs/sources/valens_translation.md` | The **text**: Greek and our own English, page,line cited. Entries marked **[G]** Greek preserved / **[E]** English only / **[S]** substance only. **Never quote an [E] or [S] entry as Greek.** |
| `docs/sources/valens_greek_notes.md` | The **analysis**: findings, the implemented change list, and TEST CASES where a reading met a life. |
| `docs/sources/ptolemy_greek_book1.md` | Ptolemy I.4–I.7, I.14, I.19–I.21 from the Greek. |

### The rule that changed everything

Valens I.1, p.5 — **placement and sect are tested BEFORE the benefic/malefic label**. A malefic in its own place and of the sect is *"a giver of good things, and indicative of greater rank and advancement"*; a benefic in the 2nd, 6th, 8th or 12th *"does not distribute its own goods."* The composer had this backwards and asserted verdicts from essential dignity alone.

### Standing rules now in force

- **Transcribe verbatim, then translate.** Never reconstruct Greek from memory — a fabricated line in a source file is worse than an admitted gap.
- **Releasing uses 360-day years**, confirmed by Valens's own conversion table (IV.10, 170). Calendar years put every boundary ~6 months late.
- **Valens's 60-invariant for ascensions is schematic, not astronomical** — it is false under exact computation by up to 4.4°. Never mix his tabulated ascensions with computed ones.
- **An escape clause governs only the sentence it appears in.** Carrying II.37's up to a stronger claim was a documented reader error.
- **Record failures.** The test-case section holds a chart where three of four testimonies matched and one failed, plus a timing technique that has fired three times with no result.
- **Emitting is not rendering.** There is already a rule that a rule pack which *loads* may *fire* nothing. There is now a second level of the same trap: evidence that fires may still never be **printed**. The bound emitter shipped without a renderer, so all eight delineations were generated, cited in the appendix, and their content never appeared in the report — the reader got the caveat *"the domicile lord decides whether what the degree carries comes out base or good"* attached to a claim that was never made. **Count the delineations in the composed prose, not in the evidence packet.** `test_bound_delineations_reach_the_customer_prose_not_only_the_packet` locks it.
- **Local green does not predict CI, and sometimes cannot.** `financial_astrology_analysis/` is gitignored ("never ship"), so tests importing it pass locally by construction and can only fail in CI. One imported it at module scope, which made the miss a *collection* error that aborted the whole suite and gated the deploy. To verify CI behaviour, move the directory aside and run: `mv financial_astrology_analysis .ci_sim_financial && pytest src/tests -q; mv .ci_sim_financial financial_astrology_analysis`. Local run = 1370 tests, CI-equivalent = 1240 + 2 skipped.

### Still open

Bound delineations are **60 of 60** — the table is closed, and an unknown key still returns `None` rather than inventing. Every bound item now carries the I.3 closing rule (`BOUND_QUALIFIER`): the degree's contribution is stated in isolation, and the overlying domicile lord decides whether it comes out base or good. I.3 is registered in `verified_rules` as `greek_text_read_in_full`, so it no longer prints as "pending primary text verification".

**Ptolemy IV.3 is read** (`γ΄. Περὶ τύχης ἀξιωματικῆς`) — a graded ladder from kings, through leaders "lords of life and death", to crown-bearing/procuratorial/camp-commanding/priestly rank, to civic promotion, to the undistinguished, to the wholly lowly; then the *kind* of rank from the character of the attending stars. **Jupiter's line in that last list is lost to OCR corruption and is recorded as a gap, not reconstructed.** III.5 (parents) and IV.10 (divisions of times) are read but not yet written into `docs/sources/`. Three Ptolemy rules remain on Ashmand (flagged, not silently repointed) because those chapters are unread in Greek. Four Paulus chapters are graded `unattested_chapter`. Roughly 190 of Valens's 423 pages are unread, chiefly the worked example charts and Books VII–IX.

---

# 1. WHAT THIS BUSINESS IS

Traditional (pre-1700) astrology readings at **traditional-astrology.com**. Owner: Andrew, sole operator.

- **Free tier** — the complete ~17,000-word source-cited reading, rendered in the browser. Zero marginal cost (deterministic, no LLM call).
- **$20 tier** — the same reading as a typeset PDF, downloaded instantly after Stripe checkout.

**Live now:** Cloud Run service `astrology-engine`, project `astrology-engine-prod`, region `us-central1`.

---

# 2. IMMEDIATE / UNFINISHED

### 2a. A reply email is drafted but NOT SENT
To **verwina2@gmail.com**. Full text in §7 below. Owner asked for it, approved the content, has not sent it.

### 2b. Refund status to confirm
- **Tariq Taher**, 9 July, $20 — order genuinely failed (never delivered). Make-good PDF exists at `artifacts/customer-makegood-20260715/`. **Refund status unknown — check Stripe.**
- Kovalev x2 — refunded by owner 2026-08-02. Done.
- Janell Johnson, 20 May, $69 — failed, refunded previously. Done.

### 2c. Open technical items
See §5 (broken/removed) and the plan document.

---

# 3. THE CUSTOMER SITUATION (read before contacting)

**Email:** verwina2@gmail.com · **Payment name:** "Kovalev dmitrii"

**Bought two readings:**
| Date | Birth data | Delivered |
|---|---|---|
| 28 July 2026 | 1987-02-01, 02:00, Kostanay, Kazakhstan | Yes — PDF downloaded 10s after payment |
| 31 July 2026 | 1972-10-01, 13:25, Moscow | Yes — PDF downloaded 16s after payment |

Both refunded by the owner on 2 August.

### Critical facts
- **DO NOT infer gender from the name.** The payment name is masculine Russian, but the customer refers to *"my husband."* We assumed male early and it propagated through everything. **All reports are written in second person ("you"), which sidesteps this entirely — keep it that way.**
- **Her husband died by suicide in September 2023.** She disclosed this as context for a question about timing. Handle with care; do not analyse the death or use it as a validation datapoint. An earlier attempt to compute his death date against the timing model was correct to abandon — it is hindsight, not prediction, and implying the death was foreseeable is cruel and unsupportable.
- She has been in a new relationship since July 2023; they work together, separate households.
- She married April 2010.

### What she said
Detailed, thoughtful, positive. Called the methodology *"coherent, consistent, and trustworthy… one of the few astrological texts where conclusions are logically derived from rules, rather than appearing as a collection of beautiful interpretations."* She is the only person who has given substantive feedback on this product.

### What she asked for
1. Crisis timing — periods of increased health risk, relationship tension, when afflicted significators activate
2. Detail *within* long periods (the Venus Firdaria 2036–2044 was one line)
3. Framing as a decision-making tool, not curiosity

**What we agreed to give:** #2 and the relationship part of #1, mechanically derived and cited.
**What we decline:** health-event timing. Not paternalism — the natal techniques don't produce it (that's decumbiture, a different chart), and the one natal method claiming to measure lifespan failed testing (§5).

---

# 4. TECHNICAL STATE — WHAT IS VERIFIED CORRECT

Cross-checked against **GERMES** (independent professional astrology software) on the Kostanay chart, agreeing to the arcminute:
- All seven classical planets, Ascendant, Midheaven, **Lot of Fortune** (sect-sensitive — a wrong sect would put it 78° off), and the UT conversion for 1987 Kazakhstan.

Verified in code audit:
- **Both bound tables** (Egyptian + Ptolemaic) — all 12 signs × 5 bounds, digit by digit
- **All seven Hermetic lot formulas** including day/night sect reversal on the correct lots
- **Decennials** — 129-month invariant enforced in code with a hard raise
- **Zodiacal Releasing** sign-years including the Capricorn 27 / Aquarius 30 asymmetry
- **Annual profections**, planetary joys, dodecatemoria, monomoiria, sect moderation

### Bugs found and FIXED this session
| Bug | Impact |
|---|---|
| **PDF chart wheel was MIRRORED** | Every PDF ever sent had houses running backwards, MC at the bottom. Cause: ReportLab Y-axis points up, SVG points down — identical formula, opposite render. The website's SVG wheel was always correct. |
| **Hyleg altitude gate** | `Planet.altitude` defaults to `0.0` and was never populated; `0.0 > 0` is False, so every luminary in houses 7/9/10/11 was rejected. Luminary-as-Hyleg went from 25% → 70% after fix. |
| Years-class inversion | Angular placements scored *worse* than succedent |
| Modifier units error | Months added as years, inflating modifiers ~12× |
| `Unknown Gives 0 Years` | Raw fallback printed as customer prose |
| Firdaria past age 75 | No evidence emitted → whole report failed |
| Decennials leap-day | Feb 29 / day-31 births broke the 129-month invariant |
| Contract regex | Bare "treat" matched as a medical claim |
| Python 3.10 f-strings | PEP 701 syntax crashed the deploy build |

---

# 5. KNOWN BROKEN / DELIBERATELY REMOVED

- **LONGEVITY (Hyleg / Alcocoden / Anareta) — REMOVED FROM OUTPUT.** Tested against 20 people with recorded birth times and known death dates: **failed on 11**. Do not reinstate without passing that test. Harness: `scripts/validate_longevity.py`. The acceptance criterion is doctrinally correct — the Alcocoden gives a *maximum*, so a promise below the age actually attained is definitionally broken.
- **`sefstars.txt` not installed** — fixed-star positions fall back to linear precession from a 2025 epoch (accurate to <1 arcminute, but install the real catalogue when convenient).
- **"Foreshadowing"** — a configured ZR status label published under a source-verified Valens citation. Source it or relabel.
- **ZR uses 360-day years** for L1/L2 boundaries; dates run ~5 days early per released year. Needs a source check.
- **Valens-variant Eros/Necessity swapped** in `lots.py` — dead code, no callers.
- **Water triplicity fork** — `PTOLEMAIC_TRIPLICITY` water row is `(Mars day, Moon night)`, which matches neither Ptolemy (Venus day / Moon night, per his Greek) nor Lilly (Mars both). An attempted "fix" broke two tests because the report *deliberately* surfaces this as a doctrinal disagreement. **Left as-is intentionally. Do not change without deciding the product question first.**

---

# 6. SOURCE POLICY (owner decision — governing)

> *"I only want to use the old texts. I don't want other people's opinions or interpretation."*

### Tier 1 — quotable verbatim (old, public domain)
- **Lilly, *Christian Astrology* (1647)** — English **original**. Planets, twelve houses, dignities, reception, degrees. `tmp/sources/lilly_1647_b30338724_djvu.txt`
- **Ptolemy, *Tetrabiblos* (Ashmand 1822)** — `tmp/ptolemy_1822.txt`
- **al-Bīrūnī (Wright 1934)** — `tmp/albiruni_1934.txt`

### Tier 2 — technique usable, wording NOT quotable (in copyright)
Dorotheus (Pingree/Houlding, marked *"personal study use only"*), Ibn Ezra (Sela), Firmicus (Bram 1975), Paulus (Schmidt), Valens (Schmidt/Riley).
**A method is arithmetic and free to implement. Only a translator's English is protected.** Compute the technique, describe it in our own words, cite chapter and page.

### Tier 3 — EXCLUDED ENTIRELY
`docs/research/Binder1.txt` — AI-generated reports citing web pages, containing **two corrupted planetary-years tables**, attributing web paraphrases to Ptolemy and Valens. Leads only, never a source.

### ⭐ MAJOR FINDING — WE HAVE ORIGINAL-LANGUAGE TEXTS
This changes the plan and was discovered at the very end of the session:

| Text | Location | Size |
|---|---|---|
| **Ptolemy, Greek (Boll–Boer Teubner critical edition)** | `docs/research/multitradition/hellenistic/sources/ptolemy_apotelesmatika_boll_boer_teubner_djvu.txt` | 287k Greek chars |
| **CCAG vols 1, 5.1, 8.1, 8.3, 8.4** (Catalogus Codicum Astrologorum Graecorum) | `docs/research/multitradition/byzantine/sources/` | ~180–230k Greek chars each |
| **Lydus, *De Ostentis*** (Wachsmuth 1897) | same directory | 273k Greek chars |
| **Ibn Ezra — original Hebrew** (facing pages in the Sela edition) | `tmp/ibn_ezra_nativities_revolutions_sela.txt` | 40k Hebrew chars |

**Why this matters:** translating from the original ourselves means (a) no copyright constraint at all, (b) no Victorian translator's interpretive layer, (c) we own the English.

**Proof it works** — Tetrabiblos I.7 on sect, read from the Greek and translated directly:
> *"They handed down the Moon and Venus as nocturnal, the Sun and Jupiter as diurnal, and Mercury as common to both — diurnal in the morning configuration, nocturnal in the evening… They assigned Saturn, being cooling, to the heat of the day; and Mars, being drying, to the moisture of the night. For thus each, obtaining proportion through the mixture, becomes proper to the sect that provides good temperament."*

That is the exact sect rule applied to her chart, **with Ptolemy's reasoning attached** — something Ashmand's English does not make visible.

**It also produced a finding we had missed:** Ptolemy says Mercury is *diurnal in the morning configuration, nocturnal in the evening.* Her Mercury is **Evening First** (occidental) → **nocturnal → in sect for her night chart.** A favourable condition on the planet the reading calls "able but obscured." Not in her report.

**Recommended next step:** make original-language-first the rule and start with the Greek Ptolemy. OCR has expected slips (`χαὶ` for καὶ, `μεῖξον` for μεῖζον) — readable but read critically.

---

# 7. THE PENDING EMAIL (approved, not sent)

**To:** verwina2@gmail.com

---
Hello,

I'm very sorry for the loss of your husband.

Thank you for writing, and for going into that much detail. You're the first person who's given me real feedback on any of this, and honestly it's worth more to me than the money was.

I've refunded both of your purchases — I'm not happy with the reports yet.

Let me try to answer what you asked.

You're right that "2036–2044, Venus" tells you nothing useful. That period actually divides into seven, each with its own ruler. Yours run:

Venus/Venus — Jan 2036 to Mar 2037
Venus/Mercury — Mar 2037 to May 2038
Venus/Moon — May 2038 to Jul 2039
Venus/Saturn — Jul 2039 to Aug 2040
Venus/Jupiter — Aug 2040 to Oct 2041
Venus/Mars — Oct 2041 to Dec 2042
Venus/Sun — Dec 2042 to Jan 2044

The one I'd mark is July 2039 to August 2040, when Venus reaches its Saturn sub-period. You'll remember from the report that Venus and Saturn already sit together in your chart, and that Venus falls in Saturn's own bound with no dignity of its own. So that stretch hands the planet governing your partnerships over to the planet that's already pressing on it. If any part of the Venus years asks something of a relationship, that's where the rules point.

For relationships specifically, your seventh house is Taurus, ruled by Venus. The annual profection reaches it, making Venus Lord of the Year, three times in the range you're asking about:

Jan 2029 to Jan 2030
Jan 2041 to Jan 2042
Jan 2053 to Jan 2054

2041 is the strongest of the three, because Venus is Lord of the Year and is also ruling the larger Firdaria period at the same time. The same planet arriving twice, from two cycles that run independently of each other.

I'd add one thing about that year though. For most of it the sub-ruler is Jupiter, which is the strongest and most helpful planet you have. It only turns to Mars in October 2041. So by the rules that year reads as partnership matters being strongly activated, not as a bad year. The technique does separate those two things, even if summaries usually don't.

If you want the years where the most difficult parts of your chart line up at once, they're 2028, 2034 and 2040.

On health I have to tell you that I don't have it, and I'd rather explain why than be vague about it. Two reasons. This tradition doesn't read health events from the birth chart at all — that's a separate branch, worked from a chart cast for the moment a person falls ill, not from the nativity. And the one birth-chart method that does claim to measure length of life, I tested against twenty people with recorded birth times and known death dates. It got more than half of them wrong. So I took it out of the reports rather than hand anyone a number I don't believe in.

What I'm building now is the timing in proper detail, year by year, with each line showing which rule and which book it came from, so you can check the reasoning rather than take my word for it. When it's ready I'll send you the new version, no charge. If there's something particular you want covered in it, tell me and I'll build it in.

Thank you again. This was genuinely the most useful message I've had about any of this.

Andrew
traditional-astrology.com
---

**Note:** the multi-tradition side project was deliberately left out — owner is still working out its shape and didn't want to raise it prematurely.

---

# 8. HER CHART (reference — verified against GERMES)

**1987-02-01, 02:00 Kostanay (53°13′N 63°37′E, UTC+5) = 1987-01-31 21:00 UT**
Ascendant **Scorpio 10°35′** · MC **Leo 26°57′** · **NIGHT** chart (Sun 52° below horizon)

| | Position | House | Condition |
|---|---|---|---|
| Sun | Aquarius 11°27′ | 4 | **detriment** (−5), rules 10th |
| Moon | Pisces 13°01′ | 5 | triplicity, Evening First, **overcome by Saturn square** |
| Mercury | Aquarius 24°37′ | 4 | triplicity (+3), **under the beams** |
| Venus | Sagittarius 25°18′ | 2 | **peregrine** (−5), conj Saturn, in Saturn's bound, rules 7th + 12th |
| Mars | Aries 16°18′ | 6 | **domicile (+5), in its joy**, rules 1st + 6th |
| Jupiter | Pisces 23°15′ | 5 | **domicile (+5)**, rules 2nd + 5th |
| Saturn | Sagittarius 18°28′ | 2 | triplicity, **out of sect**, rules 3rd + 4th |

**Key structure:** six of seven dispositor chains terminate at **Jupiter** (5th house); **Mars** answers to nothing. Moon's antiscion opposes Mars within **41 arcminutes** — tightest configuration in the chart. Lot of Fortune Libra 9°02′ (12th); Spirit Sagittarius 12°15′ (2nd). Prenatal New Moon exact at Aquarius 9°06′, 29 Jan 1987 (4th house).

**Deliverables produced:** `artifacts/kovalev-2060/Kovalev - Traditional Astrological Judgment.pdf` (14 pages, second person, corrected wheel).

---

# 9. GOTCHAS THAT WILL WASTE YOUR TIME

1. **Deploy image is `python:3.10-slim`.** PEP 701 f-strings (nested same quotes, backslash in expression) pass locally on 3.13 and **crash the build**. Gate with:
   `py -V:"Astral\CPython3.10.19" -m compileall -q src`
2. **CI gates deploy.** Failed tests → `deploy_cloud_run` is skipped → prod never receives a broken build. A red CI run is safe, not an outage.
3. **Windows console is cp1252** — printing Cyrillic or Greek raises `UnicodeEncodeError`. Write to a file with `encoding="utf-8"` instead.
4. **SMTP: authenticate as `andrew@traditional-astrology.com`, NOT the gmail address.** This was the cause of months of "expired app password" confusion — the password belonged to a different Google account than the one configured. Fixed in prod env.
5. **Translation via the cheap model FAILED integrity checks** — 455 citations became 91, headings vanished, year tokens dropped. The `scripts/translate_report.py` integrity checker caught it. Needs a stronger model and smaller chunks.
6. **The PDF renderer does not handle markdown tables** — they print as raw pipes. Use bulleted lists.
7. **Fixed-star output carries alarming boilerplate** ("danger from fire/explosions" on Markab). Do not pass to customers unreviewed — it is modern popularisation, not source doctrine.
8. **`Base.metadata.create_all()` does not add columns to existing tables.** Any new model field needs a real migration or prod will crash.

---

# 10. WHERE THINGS LIVE

- **Plan / next steps:** `docs/SOURCE_ATTRIBUTED_READING_PLAN.md`
- **Doctrine registry** (28 rules, edition + chapter + page): `src/database/data/doctrine_sources.json`
- **Reading composer:** `src/services/reading_composer.py` · **Evidence layer:** `src/services/reading_evidence.py`
- **Longevity engine:** `src/engine/hyleg.py` · **Validation harness:** `scripts/validate_longevity.py`
- **Chart wheel:** `TraditionalChartWheel` in `src/engine/pdf_generator.py`
- **Unicode/glyph fonts:** `src/engine/fonts.py`
- **Render a reading to PDF:** `scripts/render_report_pdf.py`
- **Primary texts:** `tmp/` and `tmp/sources/` · **Original-language:** `docs/research/multitradition/*/sources/`
- **Customer artifacts:** `artifacts/kovalev-2060/`, `artifacts/customer-makegood-20260715/`

---

# 11. OPEN DECISIONS FOR THE OWNER

- [ ] **Free or paid?** Undecided. Data point: the two most recent sales delivered flawlessly and the customer bought twice, unprompted, then praised the methodology.
- [ ] **Location-based pricing.** $20 was priced as $20-in-California. In Kazakhstan (median wage ~$300–400/mo) that's proportionally $80–100. Detail in the plan doc.
- [x] **Water triplicity** — confirmed from Ptolemy I.19 Greek on 2026-08-16. Old (MARS, MOON) row was wrong.
- [ ] **Multi-tradition project** — owner exploring ~20 traditions, same source-first method, with an idea of keeping only those that converge across charts. Early stage.
- [ ] **How much commentary in readings**, if any. Spec says minimal and clearly separated.
