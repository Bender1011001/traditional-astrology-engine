# Session handoff — multi-tradition reading platform

Branch: `feat/multitradition-panel` (never touched `main`)
Updated: 2026-08-02
Mission: *one birth input → the best defendable reading each tradition supports*

## Bottom line

**12 tradition sections render from one birth input**, each with an evidence
grade, explicit disclosures, and refusals where the sources cannot speak. A
cross-tradition convergence layer collapses those 12 into **6 independent
voices** by calculation basis, so agreement is never manufactured from sections
that share a chart.

Run it:

```bash
python scripts/multitradition_panel.py --fixture fairfield --format markdown
```

Demo: `docs/research/multitradition/demo_fairfield_panel.md` (1223 lines).

| | Check | Result |
|---|---|---|
| Tests | `test_multitradition_panel.py` + `test_multitradition_convergence.py` | **137 passing** |
| Worked examples | 4 suites (Maya, Jyotisha, BaZi, Tibetan) | **33/33 claims**, mutation-tested |
| Research corpus | `validate_research_corpus.py` | pass — 194 rules, 244 vectors, 0 non-Western live |
| Coverage | `validate_engine_coverage.py` | pass — 20 tracks, 74 modules |
| Lint | session-owned files | clean |
| Live engine | premium pipeline, checkout | untouched |

## The 12 sections

| Tradition | Grade | What it does |
|---|---|---|
| Western | live engine | tropical positions, sect, whole-sign |
| Islamicate | validated pack | **computed** halb/hayyiz, firdaria ordering, 8 lineage variants |
| Medieval Jewish | validated pack | Ibn Ezra revolutions profile |
| Vedic | configured | navamsha, drishti, antardasha, combustion, **yogas with constituent facts** |
| BaZi | configured | pillars, hidden stems, **month command**, Ten Gods, luck pillars |
| Tibetan | configured | year character, rabjung |
| Maya | validated pack | Long Count/Tzolk'in/Haab/Lord of Night, both correlations |
| Nahua | validated pack | **quotes Book 4 auguries** from hash-pinned witnesses |
| Babylonian | configured | omen mode — state omens, genre boundary refused |
| Egyptian | validated pack | 365-day model; refuses to place the birth |
| Ziwei | transcription | Wenchang/Wenqu only; refuses the chart itself |
| Vietnamese | configured | full lunisolar date; all 5 pack vectors reproduce |

## Findings worth reading

- **Vedic**: independently reproduced the yoga analysis computed by hand earlier
  in the session (Mars yogakaraka, Jupiter–Venus Raja Yoga, Mercury Dhana Yoga),
  and yogakaraka detection reproduces the classical list with no lookup table.
  Saturn is neutral in D1 Pisces but **exalted in D9 Libra** — a D1-only verdict
  would have been wrong, which is exactly why navamsha is mandatory.
- **Islamicate**: Mercury holds **halb without hayyiz**, so the pack's one-way
  implication shows up in the chart itself. Mercury's classification **fails
  closed** in 3 of 4 fixtures because al-Biruni 385–386 states no conflict
  priority.
- **Babylonian**: **0 omens matched** for Fairfield out of 72 protases — every
  encoded protasis presupposes a lunar eclipse. Orb is zero on every axis and
  three widenings are named and refused. A synthetic eclipse sky yields 11
  matches, proving the zero is evidence, not a broken matcher.
- **Egyptian**: refuses to place the birth at all. `default_profile` is null and
  the year drifts a day per 4 years, so an unanchored conversion is wrong by an
  unbounded amount.
- **Ziwei**: refuses its own chart — life/body palaces need the lunar month and
  the pack registers no conversion, *including* an explicit refusal to borrow the
  Vietnamese kernel sitting in the same panel.
- **Convergence**: the refusal agreement lists 5 traditions but counts 4 voices,
  because Vietnamese and Ziwei share the sexagenary basis.

## Corrections made this session

1. **"Translation is a gate" was wrong** and is withdrawn corpus-wide. The
   originals are public domain and readable directly; only *rule promotion* into
   a validated pack still wants specialist review. This was blocking three
   Islamicate modules whose Arabic TEI was already hash-pinned in the repo.
2. **Getty "client-rendered" was not a real blocker** — the app's `__NEXT_DATA__`
   names a backend serving folio JSON to plain HTTP. 150 folios now pinned.
3. **Tibetan element anchor bug**: returned Wood Mouse for 1996 instead of Fire
   Mouse. Fixed by deriving from the sexagenary cycle; now a worked example.

## In flight

A subagent is reading Classical Nahuatl across the 150 pinned folios to encode
the remaining 19 trecena chapters. 4 statements encoded so far (Ce Cipactli).

## Next

1. Finish the Nahua 20-trecena encoding.
2. BaZi branch relations (combinations, clashes, harms, punishments) — the last
   `computable` item on that spec.
3. Jyotisha worked examples from the four archive translations (page inspection).
4. Korean/Mongolian/Burmese/Thai/Khmer profiles over the shared cores.

---

## Earlier milestone detail (M1–M4)

## Status by milestone

| | Milestone | Status | Commit |
|---|---|---|---|
| M1 | Calculation panel, 8 traditions | **shipped** | `ecbde9c` |
| M2 | Defensibility standard + 7 specs | **shipped** | `7b06327` |
| M3 | Worked-example suite + runner | **shipped** | `b5de1ed` |
| M4 | Nahua reading pack | **shipped** (was blocked; user challenge broke it open) | see final commits |
| M5 | Babylonian omen mode | not started | — |
| M6 | BaZi Ten Gods, Tibetan obstacle years | not started | — |
| — | BaZi research kernel (carried over) | shipped | `2fbd991` |
| + | Navamsha (D9), closing M2's Jyotisha blocker | **shipped** | see last commit |

## Validation — all green

| Check | Result |
|---|---|
| `validate_research_corpus.py` | **pass** — 160 sources, 19 manifests, 194/194 rules vector-covered, 244 vectors, 7 defensibility specs, 2 worked-example suites, **0 non-Western live engines** |
| `validate_engine_coverage.py` | **pass** — 20 tracks, 74 modules |
| `validate_worked_examples.py` | **pass** — 13/13 claims across 4 comparable examples |
| `pytest src/tests/test_multitradition_panel.py` | **29 passed** |
| `ruff` | clean across all new code |
| Live engine / premium / checkout | **untouched** (the two modified `auth.py` files predate this session) |

## What shipped

### M1 — the panel

`src/engine/multitradition/` turns one `BirthInput` into per-tradition sections,
each carrying an **evidence grade** and explicit **disclosures**.

| Section | Grade | Content |
|---|---|---|
| Western traditional | live engine | tropical positions, sect, whole-sign houses |
| Islamicate / Persian | validated pack | profile over the same core; al-Biruni layers named, firdaria durations refused |
| Medieval Jewish | validated pack | profile; Ibn Ezra revolutions layer named |
| Vedic | configured | sidereal Lahiri, nakshatra+pada, whole-sign, dignity, full Vimshottari |
| Chinese BaZi | configured | four pillars, **hour fork emitted 3 ways**, element tally, luck pillars both directions |
| Tibetan | configured | year character (element/animal/polarity), rabjung position |
| Maya | validated pack | Long Count / Tzolk'in / Haab / Lord of Night under **both** correlations |
| Nahua | validated pack | cycle arithmetic; correlation **refused** |

Design rules enforced by tests: every section discloses something; a failing
section is recorded and the panel still renders; nothing is customer-eligible.

**Cross-checks that passed:** BaZi pillars and Vedic positions reproduce the
independent hand calculations from earlier in the session, to the arcminute and
to the day on dasha boundaries. Maya long count verified against the 13.0.0.0.0
era base.

**Bug caught and fixed:** the first Tibetan implementation returned *Wood* Mouse
for 1996 — it should be *Fire* Mouse. Cause was a private element anchor that
didn't track stem parity. Fixed by deriving from the same sexagenary cycle the
validated BaZi kernel encodes, then verified at four anchors (1027, 1984, 1996,
2026). This is exactly the class of error the worked-example discipline exists to
catch.

### M2 — defensibility standard

`docs/research/multitradition/DEFENSIBILITY.md` defines the operational test: a
section is defendable when a practitioner **of that tradition** cannot say *"you
missed our core method"*, *"that is not what the text says"*, or *"our tradition
does not claim that."*

Seven specs written, each with a core-technique checklist, judgment hierarchy,
worked-example inventory, refusal list, disclosure table, and current gap. The
corpus validator now **requires** all seven to exist, carry the six mandatory
sections, and list ≥3 refusals each.

Findings worth your attention:

- **Jyotisha's single blocking gap is navamsha** — and it's arithmetic we can
  already do. Highest-leverage next task in the whole program.
- **BaZi's blockers are hidden stems + month command.** Also note: its worked
  examples are *untrustworthy* until edition control resolves the documented
  `Sanming Tonghui` interpolation problem (later printings inserted charts).
- **Babylonian defensibility is mostly refusal** — the corpus has no personality
  genre. But its SAA8 reports are the best worked-example material in the repo:
  named ancient astrologers applying named omens to dated skies, with the
  astronomy already Horizons-cross-checked.
- **Nahua is inverted** — interpretation better sourced than arithmetic.
- **Medieval Jewish is nearly done and mislabeled** — the Ibn Ezra pack already
  drives the live report's solar-return layer without being credited.
- **Maya day meanings are refused on appropriation grounds**, not only source
  grounds: they belong to a living tradition with contemporary practitioners.

### M3 — worked examples

Schema + runner. Maya: **3 examples, 8/8 claims pass**, including a claim that
exists specifically to catch the most common error in popular Maya software
(reusing the era base's `8 Kumk'u` for 13.0.0.0.0 instead of advancing the Haab
280 days to `3 K'ank'in`). **Mutation-tested** — injecting that exact error turns
the suite red, reverting restores green.

Jyotisha: 3 examples. The navamsha structural check is now **runnable and
passing** (5 claims); the two classical-chart examples remain `inventory_only`
pending page inspection, honestly labeled with blockers.

## Configured-method choices made (every one disclosed in output)

| Tradition | Choice | Alternatives shown |
|---|---|---|
| Vedic | Lahiri ayanamsa | Fagan-Bradley, Krishnamurti, Raman, True Citra, True Revati |
| Vedic | whole-sign houses | Sripati, equal-from-degree |
| Vedic | mean nodes | true nodes |
| Vedic | 365.2425-day dasha year | 360-day savana; sidereal |
| BaZi | Li Chun year boundary | lunar new year, civil Jan 1 |
| BaZi | jie month boundaries via Swiss Ephemeris | printed almanac, mean motion |
| BaZi | day anchor JDN 2433191 = Jia-Zi | any registered concordance |
| BaZi | civil-midnight day rollover | late-Zi at 23:00 |
| BaZi | true solar time primary for hour | clock time, local mean time |
| Tibetan | BaZi Li Chun year as Losar proxy | Phugpa Losar, civil year |
| Maya | Lords of Night `(total_day+1) mod 9` | not in validated pack |
| Nahua | JDN 2451545 fixture anchor | explicitly non-historical |

## Blockers

**1. M4 / Nahua — RESOLVED.** The backend API serves folio JSON to plain HTTP
(`dfc-be.ch.digtest.co.uk/codex/codex_folio/book/4/folio/{f}/`); found by
loading the page in the in-app browser and reading `__NEXT_DATA__`. Ten folios
(1r-5v) fetched and hash-pinned, all four pack-cited text-record UUIDs verified
present. M4 encoding can proceed. Original note kept below for the record:

**(historical) M4 / Nahua — RETRIEVAL ONLY.** Corrected after review: the rights blocker
I originally recorded was wrong and is withdrawn. The 16th-century Nahuatl and
Sahagun's Spanish are public domain and can be rendered directly, so the modern
copyrighted English translation was never needed. The real and only blocker is
that no route tried returns the text: Getty is client-rendered, and LoC/WDL
returns 403 to the fetch tool.

**Trivially unblockable by you:** download the Book 4 folios covering the twenty
day signs and commit them under
`docs/research/multitradition/nahua/folios/`. Images can be read directly.
Full detail in `docs/research/multitradition/nahua/reading_pack_status.md`.

**1b. The same error was found propagating into the Islamicate gates**, where it
was blocking real work. Three modules listed obtaining a modern English
translation (Brill 2019, Aragno 2004, 1994) as a gate — while seven Arabic and
Latin TEI witnesses sit hash-verified in the repo with 30 catalogued passages.
Gates rewritten to ask for the critical *apparatus* (stemma, variant collation),
which is genuine scholarly value, rather than the translation. Consequence: the
8 preserved variants are publishable content **now**.

A new standard section, "Translation is not a gate for quotation", now governs
this decision corpus-wide and separates rule promotion (independent review still
required) from quotation (render the public-domain original directly).

**2. Sex is not in the birth input contract.** Affects BaZi luck-pillar direction
(currently both emitted) and Tibetan parkha (currently refused). Needs a product
decision, not research.

**3. Tibetan mewa/parkha have no sourced anchor.** Refused rather than guessed.

## Next 3 actions

1. **BaZi hidden stems + month command.** Hidden stems are a fixed lookup table;
   month command is the tradition's first substantive judgment. Together they
   move BaZi from pillar calculator to reading.
2. **M5 Babylonian omen mode** — the design is already written in
   `babylonian/defensibility_spec.md`, the astronomy is Horizons-verified, and
   ~70 omen rules are encoded. Highest ratio of existing assets to remaining work.
3. **Jyotisha drishti + antardasha** — the next two items on that spec's
   checklist now that navamsha is done; both are pure arithmetic.

Deferred deliberately: M4 until source access resolves; Maya two-converter
cross-check (valuable, needs network); medieval Jewish attribution (needs a
decision about touching the live report, which this session's ground rules
excluded).

## Demo — your chart

Full artifact at `docs/research/multitradition/demo_fairfield_panel.md`. Header:

```
Birth: 1996-08-13 07:18 (UTC-7) — Fairfield, California, United States
UTC: 1996-08-13T14:18:00 · JDN: 2450309
Local mean time: 06:09:50 · True solar time: 06:05:05 (equation of time -4.7 min)
```

| Tradition | Result |
|---|---|
| Western | Asc Virgo 1°30, MC Taurus 27°03, **day** chart, Sun Leo 12th |
| Vedic | Lagna Leo 7°41 (Magha pada 3), Janma Ashlesha pada 1, Mercury mahadasha to Feb 2010 |
| BaZi | 丙子 / 丙申 / 壬午 / 癸卯 — Yang Water day master, **Earth absent**, luck pillar 己亥 from Nov 2024 |
| Tibetan | Male Fire Mouse, rabjung 17 year 10 |
| Maya | GMT 584283: **12.19.3.7.6, 10 Kimi, 9 Yaxk'in, G4** · GMT 584285: 12.19.3.7.4, 8 K'an, 7 Yaxk'in, G2 |
| Nahua | correlation refused — no day sign assigned |

Note the BaZi hour fork is live for your birth: true solar time 06:05 falls in 卯
Mao, clock time 07:18 falls in 辰 Chen. The panel emits both and says why.
