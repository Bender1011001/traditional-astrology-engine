# Jaimini defensibility spec

Status: governing spec for the Jaimini reading section — **no such section exists yet**
Updated: 2026-08-02
Standard: [../DEFENSIBILITY.md](../DEFENSIBILITY.md)

The adversary here is a Jaimini practitioner, and that reader is not the same
person as the Jyotishi who audits our Parāśari section. A Jaimini reader opens
with the chara kārakas and the rāśi dṛṣṭis, and will know within one paragraph
whether the section is Jaimini or a Parāśari reading with Jaimini vocabulary
sprinkled on it. That is the failure mode this spec exists to prevent.

**Why this is a separate tradition and not a Jyotisha sub-section.** Jaimini
disagrees with mainstream Parāśari on the four things that determine what a
chart says:

| Question | Parāśari answer | Jaimini answer |
|---|---|---|
| What aspects what | grahas aspect the 7th, plus special aspects for Mars, Jupiter, Saturn | **signs** aspect signs by modality; grahas inherit their sign's aspects |
| Who signifies the mother | the Moon, always | whichever graha ranks 4th by degree **in this chart** |
| Which houses are read | the twelve bhāvas from lagna | the bhāvas **and** a parallel ārūḍha-pada frame, **and** Horā / Ghaṭikā / Bhāva / Varṇada lagnas |
| How time is measured | Viṃśottarī, a nakṣatra-seeded **graha** daśā | Chara, Sthira, Nārāyaṇa — **sign** daśās with per-sign lengths |

Give the same chart to both methods and they nominate different significators,
draw different aspect lines, and open different periods. Merging them produces a
reading neither tradition would sign.

## Core-technique checklist

Every row is `source_gated` or `refused`. Nothing is `implemented`, because no
Jaimini engine exists; nothing is `computable`, because every row is blocked on
a **named document** we do not yet hold, or on the corpus's own standing rule
that a single unreviewed Sanskrit reading may not be promoted into a pack that
drives automated judgment. Read the gates literally: each one names what would
clear it.

| # | Technique | Source basis | Status |
|---|---|---|---|
| 1 | Rāśi dṛṣṭi — movable, fixed, dual sign aspects | Upadeśa Sūtra 1.1.2 with the vṛddha kārikā *caraṃ dhanaṃ vinā sthāṇuḥ*; two witnesses agree exactly | `source_gated` — text settled, but promotion needs independent Sanskrit review per DEFENSIBILITY.md; the OCR restoration of 1.1.2 must be checked against page images |
| 2 | Graha dṛṣṭi derived from sign dṛṣṭi | Sūtra 1.1.3 *tanniṣṭhāś ca tadvat* | `source_gated` — same review gate as row 1 |
| 3 | Chara kārakas — Ātma through Dāra, ranked by degree-within-sign | Sūtras 1.1.10–1.1.18; arithmetic fully stated | `source_gated` — the **arithmetic** is settled but the **candidate set** is not: Abhyankar's critical text carries a Pitṛkāraka sūtra the Sūtrārthaprakāśikā's text lacks. Only Abhyankar's variant apparatus, printed in Devanagari his OCR did not recover, can settle it |
| 4 | Rāhu convention — included or not, forward or reverse counted | vṛddha verse *meṣādy-asavya-mārgeṇa rāhuketū na kārakau* quoted in the Sūtrārthaprakāśikā | `source_gated` — the verse reaches us only through a quotation; its home is Abhyankar's Appendix 1 (Jaimini-Sūtra-Kārikā), unread |
| 5 | Sthira kārakas — fixed significators coexisting with the chara layer | Sūtras 1.1.19–1.1.23 | `source_gated` — witnesses disagree on 1.1.21/1.1.22 (all three topics from Jupiter, or split across Jupiter, Venus, Saturn) |
| 6 | Kaṭapayādi decoding of the sūtras | Sūtras 1.1.31–1.1.32 *sarvatra savarṇā bhāvā rāśayaś ca* / *na grahāḥ* | `source_gated` — method confirmed by two independent worked examples (*dāra* = 4, *viveka* = 144); every remaining word needs decoding under review |
| 7 | Ārūḍha padas and the pada-kuṇḍalī | Sūtras 1.1.29–1.1.31 | `source_gated` — the Sanskrit for these sūtras was not recovered; encoded from Abhyankar's English alone, and the inclusive-counting convention is assumed, not stated |
| 8 | Upapada and its delineation | named in the Sītārāma Jhā preface and in Abhyankar's contents paragraph 113 | `source_gated` — the governing sūtras lie in Adhyāya 1 Pādas 2–4, not yet read |
| 9 | Argalā and its obstruction | Sūtras 1.1.4–1.1.9 | `source_gated` — the argalā/virodhī **pairing** and the **target** of the argalā are both disputed in the commentary; needs the critical apparatus |
| 10 | Special lagnas — Horā, Bhāva, Ghaṭikā | vṛddha verses quoted at Sūtrārthaprakāśikā 1.1.31 | `source_gated` — rates are stated; the **starting point** is a live three-way dispute in which Nīlakaṇṭha's own position survives only as a hostile paraphrase |
| 11 | Varṇada lagna | vṛddha verse quoted at Sūtrārthaprakāśikā 1.1.31 | `source_gated` — the commentator who transmits the rule twice says he does not understand why it is stated as it is |
| 12 | Chara daśā — counting direction | Sūtras 1.1.24–1.1.27; both witnesses agree the exception is Taurus, Leo, Scorpio, Aquarius | `source_gated` — settled between witnesses; blocked only on review |
| 13 | Chara daśā — period lengths | Sūtra 1.1.28 | `source_gated` — the sūtra fixes the counting but not the subtract-one convention, the lord-in-own-sign case, or the dual lordship of Scorpio and Aquarius. Those sit in Adhyāya 2, unread |
| 14 | Sthira, Nārāyaṇa and the other named daśās | Abhyankar contents paragraphs 67–68 "Kinds of Daśās" | `source_gated` — inventory known, governing sūtras unread |
| 15 | 144-year daśā cycle bound | Sūtra 1.1.33 *yāvad vivekam āvṛttir bhānām* | `source_gated` — decoding confirmed twice; review gate only |
| 16 | Natural strength order of the grahas | Sūtra 1.1.23 *mando 'jyāyān graheṣu* | `source_gated` — the sūtra gives only Saturn; the full order is the commentary's import from Bṛhajjātaka and must be labelled as such |
| 17 | Rājayoga and the other yogas | Abhyankar contents paragraph 66 | `source_gated` — Adhyāya 1 Pāda 2 onward, unread |
| 18 | Divisional charts — Horā, Dreṣkāṇa, Navāṃśa | Sūtra 1.1.35 *horādayaḥ siddhāḥ* | `refused` as a *Jaimini* doctrine — the sūtra explicitly delegates these to current practice. Any varga the engine uses must be attributed to the text it came from, never to Jaimini |
| 19 | Āyurdāya — length of life by the three methods | Abhyankar contents paragraphs 73–74; the Jammu Nīlakaṇṭha manuscript folios treat it at length | `refused` — see the refusal list |
| 20 | Time, kind and cause of death | Abhyankar contents paragraphs 75–76 | `refused` — see the refusal list |
| 21 | Worked-example reproduction | Abhyankar contents paragraphs 105–129, fourteen worked kāraka-kuṇḍalīs | `source_gated` — this is the single highest-value outstanding acquisition; it sits behind a 238 MB page-image PDF whose text layer lost the charts |

## Judgment hierarchy

Jaimini's own order, taken from the sequence of the sūtras themselves rather
than from Parāśari habit. The composer must execute in this order; later steps
may qualify earlier ones but may not silently replace them.

1. **Decode the text before applying it.** Kaṭapayādi first (1.1.31–1.1.32).
   Every downstream number depends on it, and most commentator disputes are
   decoding disputes wearing doctrinal clothes.
2. **Rāśi dṛṣṭi.** Establish which signs aspect which (1.1.2), then which
   grahas inherit those aspects (1.1.3). This is the geometry everything else
   is read on, and it is the first sūtra of substance in the text.
3. **Argalā.** Which grahas intervene on that geometry, and which obstruct
   (1.1.4–1.1.9) — with the target of the intervention disclosed as disputed.
4. **Chara kārakas.** Rank the grahas by degree-within-sign and assign
   Ātmakāraka downward (1.1.10–1.1.18). The Ātmakāraka outranks the lagna lord
   for personal signification — this is the inversion that most distinguishes
   Jaimini from Parāśari, and doing it late is the tell of a Parāśari reading
   in costume.
5. **Sthira kārakas.** Apply the fixed significators (1.1.19–1.1.23) *alongside*
   the chara layer, not instead of it. Jaimini runs both.
6. **Ārūḍha padas.** Build the pada-kuṇḍalī (1.1.29–1.1.31) as a second frame
   read in parallel with the rāśi chart, never merged into it.
7. **Special lagnas.** Horā, Bhāva, Ghaṭikā, Varṇada — each with its starting-
   point convention disclosed.
8. **Daśā.** Direction first (1.1.24–1.1.27), then lengths, then the 144-year
   bound (1.1.33). Read against the qualified natal structure, never as
   free-floating themes.

Strength (1.1.23) is a tie-breaker applied within steps, not a step of its own.

## Worked-example inventory

| Source | Location | Contains | Usable now |
|---|---|---|---|
| Abhyankar 1951, introduction §§105–129 | registry `jaimini_abhyankar_1951_upadesa_sutra_critical_edition` | **fourteen** worked kāraka-kuṇḍalīs of named, dated people — Ramakrishna Paramahamsa, M. G. Ranade, Tilak, Madan Mohan Malaviya, Sayajirao Gaekwar, Vasudeo Shastri Abhyankar, Gandhi, N. C. Kelkar, Nehru, Vallabhbhai Patel, G. V. Mavlankar, J. S. Karandikar, Justice N. S. Lokur, plus a mundane chart for Ahmedabad city | **No** — the OCR recovered the contents list but not the chart pages. Needs the page images |
| Abhyankar 1951, §§110–115 | same | illustrations of pada-kuṇḍalī, upapada-kuṇḍalī, and planetary alliances with life-periods | No — same gate |
| Sūtrārthaprakāśikā at 1.1.31 | registry `jaimini_sutrarthaprakasika_dli_2015_242319` | two numeric Varṇada worked examples with full sign-degree-minute-second longitudes | **Partially** — the numbers are legible in OCR but the arithmetic uses finer values than the verse as stated, so they cannot yet be turned into a passing test |
| Abhyankar Appendix 4 | same | comparative contents table across Jaimini, Bṛhad-Yavana-Jātaka, Bṛhajjātaka, Sārāvalī and Bṛhat Pārāśarī | No — not in the OCR |

This is an unusually strong worked-example position on paper and an unusually
weak one in practice: fourteen named charts with the author's own stated
judgments exist and are the obvious validation suite, and we cannot read them
yet. That single acquisition would move this tradition further than any other
piece of work available to it.

## Refusal list

- **No lifespan claim, and no āyurdāya arithmetic presented as a result.**
  Jaimini's longevity material is extensive — Abhyankar devotes four
  introduction paragraphs to it and the Jammu Nīlakaṇṭha folios turn on the
  dīrgha / madhya / alpa āyus triad — and it is exactly the kind of
  branch-dependent arithmetic the live Western report already demonstrates
  behaves badly when the branches disagree. Retain in the trace; never assert.
- **No time, kind, or cause of death.** The text supplies all three. We publish
  none of them, in any hedged form.
- **No Jaimini attribution for any divisional chart.** Sūtra 1.1.35 delegates
  Horā, Dreṣkāṇa and the rest to current practice. Presenting a navāṃśa as
  "Jaimini's navāṃśa" would misattribute a definition the text pointedly
  declines to give.
- **No silent choice between the seven-kāraka and eight-kāraka schemes**, and no
  silent Rāhu convention. These change who the Ātmakāraka is — the single most
  load-bearing assignment in the system. A reading that picks one without
  saying so is not a Jaimini reading, it is our reading.
- **No merging of Jaimini and Parāśari aspect lines, significators, or daśās**
  into one verdict. Where both are shown, they are shown as two readings with
  their disagreements visible.
- **No delineation of the Ātmakāraka's bandha/mokṣa signification as a
  prediction.** The commentary's "bondage" includes literal imprisonment. It is
  historical testimony, not a forecast.
- **No claim resting on Adhyāyas 1.2 through 4.** Nothing outside Adhyāya 1
  Pāda 1 has been read in the original. The upapada, the yogas, the named
  daśās and the ārūḍha delineations are all inventoried and none is sourced.

## Conventions requiring disclosure

| Convention | Status here | Alternatives that must be named |
|---|---|---|
| Kāraka scheme | **undecided** | seven kārakas (Sūtrārthaprakāśikā running text, Mātṛkāraka doubles as Putrakāraka) vs eight (Abhyankar's critical text, with a distinct Pitṛkāraka) |
| Rāhu in the kāraka set | **undecided** | excluded entirely; or included and reverse-counted at 30° − λ; or included forward |
| Rāhu/Ketu as one kāraka or two | Abhyankar: one | he reasons they hold identical degrees-within-sign, giving eight not nine |
| Kāraka tie-break | **undecided** | finer units per *kalādibhiḥ*; or the stronger graha (the Sūtrārthaprakāśikā's own view, and *kecit*); or by sthira-kāraka (Subodhinī, rejected) |
| Argalā target | **undecided** | the bhāva under consideration (Sūtrārthaprakāśikā) vs the aspecting graha (Subodhinī) |
| Scope of *viparītaṃ ketoḥ* | **undecided** | universal across 1.1.4–1.1.8 vs confined to the trikoṇa sūtra it follows |
| Horā / Bhāva Lagna starting point | **undecided** | from the Sun's sign always (Sūtrārthaprakāśikā); from the Sun if the lagna is odd and from the lagna if even (*prācīnāḥ* and the vṛddha); Nīlakaṇṭha's own position, which we cannot yet read |
| Sthira kāraka for grandfather, husband, son | **undecided** | all three from Jupiter (Abhyankar) vs Jupiter, Venus, Saturn respectively (Sūtrārthaprakāśikā) |
| Sūtra numbering | both recorded | Abhyankar and the Sūtrārthaprakāśikā diverge by one from 1.1.15 onward. Every citation in this pack carries both |
| Ayanāṃśa, nodes, house model | inherited, not Jaimini's | the Upadeśa Sūtra fixes none of these; they must be disclosed as imported from the shared Jyotisha profile |
| Ārūḍha inclusive counting | **assumed** | the sūtra does not state whether counting is inclusive; standard Sanskrit usage is assumed and flagged |

Eleven undecided conventions is not a defect of this pack. It is the finding.
The Jaimini corpus is genuinely forked, and a product that hides that is
misrepresenting the tradition more seriously than one that omits it.

## Current implementation gap

There is no Jaimini code, no Jaimini panel section, and no Jaimini reading. This
pack is a **source foundation**: 41 rules and 43 vectors covering Adhyāya 1
Pāda 1, read in Sanskrit from two independent witnesses, with every commentator
disagreement encoded as a separate attributed rule rather than averaged away.

Being precise about the gate, because "source_gated" can be used to hide work:

- **Rows 1, 2, 12, 15, 16 are gated on review alone.** Their texts are settled
  and their two witnesses agree. Independent Sanskrit review is the only thing
  between them and implementation. That review is a real corpus policy, not an
  excuse — but it is the *fastest-clearing* gate on this list, and nobody should
  pretend otherwise.
- **Row 3 is the prize.** The chara kāraka ranking is pure arithmetic — sort the
  grahas by longitude mod 30, descending — and is directly implementable and
  testable today. What blocks it is not the arithmetic but the candidate set:
  seven bodies or eight, and Rāhu forward or reversed. Those change the
  Ātmakāraka in real charts, and the document that would settle them is
  Abhyankar's variant apparatus, which his scan's OCR did not recover.
- **Rows 7, 8, 13, 14, 17 are gated on unread text**, plainly. Adhyāya 1 Pāda 2
  onward has not been read in the original.
- **Row 21 is gated on one PDF.** Fourteen worked charts with the editor's own
  judgments sit in a 238 MB image file. Acquiring it is the highest-leverage
  next action for this tradition by a wide margin.

Ordered next work: (1) page images for Abhyankar, unlocking rows 3, 4 and 21 at
once; (2) Sanskrit review of the settled rows; (3) direct transcription of the
Jammu Nīlakaṇṭha manuscript, so the tradition's most-cited commentator stops
reaching us through the words of someone arguing with him; (4) Adhyāya 1
Pādas 2–4.
