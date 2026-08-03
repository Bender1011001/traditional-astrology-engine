# External review, 2026-08-03 — findings and work order

The owner supplied a full architectural review of the multi-tradition work.
Its verdict, quoted because it is the standard the rest of this file serves:

> "This is an unusually rigorous, source-aware framework for determining what
> can and cannot be computed or interpreted from multiple historical astral
> traditions. The system becomes genuinely exceptional once it stops equating
> rule retrieval with interpretation, separates research demonstrations from
> natal engines, enforces its own publication policies consistently, and builds
> a formal synthesis layer capable of explaining why one conclusion should
> survive when the sources conflict."

The review's twenty findings compress to: the sourcing discipline is strong;
the synthesis and presentation layers are weak; the worst defects are policy
leaks, false certainty, evidence duplication, and breadth inflation.

## Priority 0 — correctness failures: DONE

| Finding | Fix |
|---|---|
| Lifespan claims ("short-lived", "long-lived") reached the rendered Vedic report through ordinary placement aphorisms despite a declared longevity refusal | Clause-level semantic redaction in `Delineation.__post_init__` (`src/engine/traditions/report.py`): refused-topic lexicons (longevity, death) are applied to every sourced clause at construction time, so no engine, renderer or serializer path can leak one. The surviving verse keeps its non-refused clauses; the withholding is marked and topic-named in place. |
| Same quotation rendered under both graha and bhava sections; one witness looked like two, and doubled the leak surface | Claims render once. Bhava sections cross-reference the graha judgments; the opening cross-references instead of re-quoting the lagnesa; repeated yoga configurations reference the first quotation of a shared rule. |
| al-Qabisi hyleg: the uncomputed prenatal syzygy was treated as FAILED, and the Ascendant declared settled — unknown collapsed into false | `settle_hyleg` is tri-valued (pass / fail / unknown). An uncomputed earlier candidate forces `status: "conditional"` with `conditional_on` naming it. Unit-tested both ways. |
| Raw JSON printed in BaZi prose | Month-command rendered as prose. |
| "Full Reading" title on BaZi overclaims (no strength/pattern/useful-god adjudication) | Retitled "Structural Analysis with Classical Clauses (Ziping method)". |
| No regression coverage for any of the above | `src/tests/test_tradition_reports.py`: 12 tests — redaction unit + integration, no-quote-rendered-twice, bhava-sections-reference-only, tri-valued hyleg (unit + live), no-raw-JSON, title check, and a canary that fails if redactions stop occurring (so a silently broken lexicon is caught). |

## Priority 1 — honest maturity modeling: OPEN

Single status labels conceal a multidimensional reality. Replace with separate
axes per module: source readiness / computational readiness / validation
coverage / interpretation readiness / publication readiness. Stop counting
calendar demonstrations and construction experiments in the same headline as
natal engines. Honest coverage today: 2 developed natal reports (Vedic, BaZi
structural) + the Western premium engine; 4-5 partial judgment engines;
1 incomplete construction engine (Zi Wei); 5 calendar/cycle modules; 1
state-omen corpus demonstration (Babylonian — rename it as such); 1
solar-return module (Ibn Ezra).

Also under this heading:
- Split the single `[REFUSES]` label into specific statuses (not part of this
  tradition / source unavailable / source unread / translation pending /
  extraction incomplete / calculation unimplemented / missing user input /
  school fork unresolved / suppressed by policy).
- Replace the single evidence letter with a vector (edition / translation /
  extraction / validation / applicability).

## Priority 2 — synthesis architecture: OPEN, the deepest gap

The engines can prove why a quotation was selected but cannot adjudicate
conflicting quotations (Mercury: "ignorance and poverty" beside "sharp
intellect and learning"). Required per claim: scope (life topic), polarity,
strength, preconditions, modifiers/cancellation, precedence, independence
(shared lineage is not corroboration), temporal activation, confidence.
Precedence questions to answer per tradition before synthesis is credible:
house vs sign rank; dignity qualifying a house aphorism; D9 modifying D1;
two-author agreement vs one contrary; grade weighting; domain compatibility.

## Priority 3 — report redesign: OPEN

Three layers from one dataset: Reading (coherent, supported conclusions only),
Evidence (expandable citations), Audit (configuration, suppressions, hashes,
statuses). Currently interleaved; audit language leaks into the reading.

## Priority 4 — input forks: OPEN

Add optional tradition-specific inputs: sex/traditional classification (BaZi
luck direction, Zi Wei decade limits, Tibetan parkha), birth-time certainty,
record source, DST status, preferred local-time doctrine. Distinguish missing
data from doctrinal ambiguity. Produce branch-difference reports (the Chinese
solar-vs-clock fork changes the hour pillar 癸卯→甲辰 and the Zi Wei life/body
palaces: stable core + two branches + a difference list, not a footnote).
Generalize the Zi Wei invariance-testing pattern (assumption exists /
changes nothing here / changes a detail / changes sign-house / forks the
reading) to every configured method.

## Priority 5 — deepen before widening: OPEN

Vedic synthesis + policy; BaZi pattern/useful-god (predicates now exist in
`ziping_predicates.py`; adjudication thresholds remain source-gated); full
Hellenistic condition + time-lords; al-Qabisi prenatal syzygy computation and
worked-example validation; Latin reception/temperament/directions. Zi Wei and
the calendar modules stay research modules until their source gaps close.

## Standing principles adopted from the review

1. Unknown must never collapse into false — anywhere.
2. Policy is enforced on semantic content at output time, not on rule
   categories at extraction time.
3. A claim is stored once and referenced from every structural view.
4. Shared lineage is not independent confirmation.
5. Rule retrieval is not interpretation, and the product must not imply
   otherwise.
