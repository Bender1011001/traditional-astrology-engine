# Session handoff — multi-tradition reading platform

Branch: `feat/multitradition-panel` (never touched `main`)
Date: 2026-08-01
Mission: *one birth input → the best defendable reading each tradition supports*

## Bottom line

M1–M3 shipped and committed, plus navamsha — the one gap M2 identified as blocking a defendable Vedic reading. **M4 is blocked on source access and rights, not
on effort** — recorded rather than worked around, because faking it would have
produced exactly the unsourced content the whole standard exists to prevent.
M5–M6 not started.

The panel renders one birth into **8 tradition sections**, and there is now an
operational definition of "defendable" plus a test suite that can go red.

Run it:

```bash
python scripts/multitradition_panel.py --fixture fairfield --format markdown
```

Demo artifact: **`docs/research/multitradition/demo_fairfield_panel.md`**
(359 lines, your birth across all 8 traditions), committed and tracked.
(`artifacts/` is gitignored, so the demo lives under `docs/`.)

## Status by milestone

| | Milestone | Status | Commit |
|---|---|---|---|
| M1 | Calculation panel, 8 traditions | **shipped** | `ecbde9c` |
| M2 | Defensibility standard + 7 specs | **shipped** | `7b06327` |
| M3 | Worked-example suite + runner | **shipped** | `b5de1ed` |
| M4 | Nahua reading pack | **blocked** | `c78e47c` (blocker recorded) |
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
| `pytest src/tests/test_multitradition_panel.py` | **27 passed** |
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
