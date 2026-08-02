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
| 14 | Shadbala | BPHS bala chapters | `source_gated` — recension-dependent weights |
| 15 | Ashtakavarga | BPHS | `source_gated` |
| 16 | Other vargas (D10 career, D7 children, etc.) | BPHS varga chapters | `source_gated` — which vargas are mandatory varies by school |
| 17 | Planet-in-bhava classical delineation text (as opposed to structural condition alone) | Phaladeepika Adhyaya VIII (`delineation_rule_manifest.json`) | `source_gated` — sourced and paraphrased for 8 of 9 grahas across all 12 houses (Saturn 11/12, Sun 5/12); translation rights unresolved, independent Sanskrit review pending, no composer wiring written |
| 18 | Named-yoga delineation text (Pancha Mahapurusha, Kesari/Sakata, Mahabhagya, Adhama/Sama/Varishtha, Sunapha/Anapha/Durudhara/Kemadruma, Vesi/Vaasi/Kartari, 4 Rajayogas, Neechabhanga Rajayoga) | Phaladeepika Adhyayas V-VII (`delineation_rule_manifest.json`) | `source_gated` — same translation-rights/review hold as #17; several sub-yogas additionally need house-from-Moon or house-from-Sun computation the engine does not yet perform |
| 19 | Vimshottari mahadasha classical significations (general, per graha) | Phaladeepika Adhyaya XIX (`delineation_rule_manifest.json`) | `source_gated` — same translation-rights/review hold as #17; antardasha-level significations not yet sourced |

Items 17-19 are new as of 2026-08-02 and were added rather than folded into
items 7, 8 or 12, because those items are about calculation (mahadasha/
antardasha arithmetic) or structural detection (yoga conditions, with no
catalogue or phala attached, by design - see `vedic.py`'s own docstring), while
17-19 are about the classical delineation TEXT for those same facts. None of
items 1-16 changed status: this pass's sourcing did not touch Shadbala,
Ashtakavarga, or other-varga material, so 14-16 remain exactly as they were.
17-19 are marked `source_gated`, not `computable`, because a real hold remains
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

## Worked-example inventory

| Source | Location | Contains | Usable now |
|---|---|---|---|
| Brhajjataka, Aiyar 1905 translation | registry `jyotisha_varahamihira_brhajjataka_aiyar_1905_archive` | worked illustrations in the commentary | **inspected 2026-08-02**: keyword search of the full OCR found only abstract calculation walkthroughs ("suppose the Sun's longitude to be..."), no natal chart with real birth data and a stated verdict. Page-image (non-OCR) inspection still not attempted. |
| Saravali, Subrahmanya 1914 | registry `jyotisha_kalyanavarma_saravali_subrahmanya_1914_archive` | example applications | still needs page inspection; OCR remains too corrupted to read (mixed scripts, many misrecognitions) |
| Saravali, Nirnaya Sagar Press 1907 | registry `jyotisha_kalyanavarma_saravali_nirnayasagar_1907_archive` (new 2026-08-02) | full Sanskrit text, chapter structure, any worked example | **discovered 2026-08-02**: first Saravali witness with legible Devanagari OCR (291,940/366,411 characters proper Devanagari, 9 failure marks); text proper not yet read for content - this is now the priority Saravali lead, ahead of the 1914 witness |
| Phaladeepika, Subrahmanya 1950 | registry `jyotisha_mantreswara_phaladeepika_subrahmanya_1950_archive` | worked yoga examples | **inspected 2026-08-02**: Adhyayas V-VIII and XIX read directly; all are rule catalogs (now in `delineation_rule_manifest.json`), no worked chart found. Adhyayas IX-XVIII and XX-XXVIII not yet inspected. |
| BPHS Subodhini 1899 | registry `jyotisha_bphs_subodhini_1899_archive` | dasha and varga worked cases | **inspected 2026-08-02**: local mirror fetched and read directly; OCR confirmed almost total failure (near-all `?` characters), worse than previously suspected. Recension audit variance concern is moot until the text itself is recoverable; page-image (non-OCR) inspection is the only remaining path. |

Brhajjataka, Phaladeepika and BPHS have now each had at least one direct,
non-metadata inspection pass for worked-example content specifically; all three
came back negative in the chapters/portions inspected, which is recorded above
rather than left as an open placeholder. The Saravali branch is the one where
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
  with sourced weights.
- **No progeny, fertility, or childlessness claim** rendered about a living
  reader. Phaladeepika's planet-in-bhava and yoga material (Adhyayas V-VIII)
  routinely states progeny counts or "childless" outcomes as part of a house or
  yoga result; those clauses are retained in `delineation_rule_manifest.json`
  as historical testimony with an explicit suppression note, the same
  treatment this spec already gives varna/caste material, and are never
  rendered as a claim about the reader's own fertility.
- **No horoscope-of-women-chapter or issue-chapter material.** Phaladeepika
  Adhyayas XI-XII were located and deliberately not mined for rules; their
  subject matter is marriage/progeny outcome for the native and falls under
  the two refusals immediately above and below.

## Conventions requiring disclosure

| Convention | Chosen | Alternatives |
|---|---|---|
| Ayanamsa | Lahiri (Chitrapaksha) | Fagan-Bradley, Krishnamurti, Raman, True Citra, True Revati |
| Houses | Whole sign | Sripati, equal-from-degree |
| Nodes | Mean | True |
| Dasha year length | 365.2425 days | 360-day savana year; sidereal year |
| Moolatrikona boundaries | pending | vary slightly by text |
| Relative-house reckoning | house from the Lagna only | house from the Moon (chandra lagna) and house from the Sun are both classically used (Sunapha/Anapha/Durudhara/Kemadruma, Kesari/Sakata, Adhama/Sama/Varishtha, the Sun-relative Vesi/Vaasi cluster, and the kendra-from-Moon branch of Neechabhanga Rajayoga all require one or the other) but neither is computed by `vedic.py` today |

## Current implementation gap

The shipped panel section covers items 1-5, 7, and 9 (partially). To reach a
defendable reading it needs, in order: **navamsha (6)**, antardasha (8), drishti
(11), then yogas (12) gated on 10 and 13.

As of 2026-08-02, a delineation-content layer for items 17-19 exists in
`delineation_rule_manifest.json` (18 rules: planet-in-bhava for 8 of 9 grahas
across all 12 houses plus a partial Sun row, eight named-yoga clusters, and
Vimshottari mahadasha significations for all 9 grahas), sourced from
Phaladeepika. None of it is wired into `vedic.py` or the composer - this pass
was research-only by instruction, so the panel's rendered reading is
unchanged. The two concrete blockers to wiring it in are: (1) the Phaladeepika
1950 translation's copyright status is unresolved and independent Sanskrit
review is pending for every rule, matching the existing Brhajjataka posture;
and (2) several of the sourced yogas need house-from-the-Moon or
house-from-the-Sun relative reckoning that `vedic.py` does not yet compute (see
the relative-house-reckoning row above) - the Pancha Mahapurusha yogas and the
Lagna-kendra branch of Neechabhanga Rajayoga do not have this dependency and
are the nearest-term composer candidates once translation rights are resolved.
