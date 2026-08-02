# Jaimini Source Audit

Status: Adhyāya 1 Pāda 1 encoded from two witnesses read in the original; not ready for implementation or publication
Date: 2026-08-02

## Outcome

The Jaimini Upadeśa Sūtra is **retrievable in Sanskrit, readable, and
sufficiently attested to found a serious pack** — which was not obvious before
this pass, since the tradition had nothing in this repo and its most-cited
modern treatments are all in copyright.

Two independent witnesses were read directly: a 1951 critical edition prepared
from fifteen manuscripts, and a printed Sanskrit edition with a full
commentary. They agree on the substance of every rule encoded here. They
disagree on sūtra numbering, on the number of variable significators, and on
three calculation methods — and those disagreements are the most valuable thing
this pass produced, because they are the ones a Jaimini practitioner will
already know about and will check for.

What this pass does **not** support is a reading section. Adhyāya 1 Pāda 1 is
one of sixteen pādas. The upapada, the yogas, the named daśās and the entire
āyurdāya apparatus are inventoried but unsourced.

This pass inspected five downloadable objects. Exact identifiers, SHA-256
hashes, and the retrieval failures are in
[`sources/access_manifest.json`](sources/access_manifest.json) and in
`../source_registry.json`.

## Why this is not a branch of the Jyotisha pack

The repo already carries a Parāśari pack built on Bṛhajjātaka and BPHS
witnesses. Jaimini is not a refinement of that method; it is a different one,
and the divergence is structural rather than stylistic:

- **Aspects are a property of signs, not planets.** A movable sign aspects the
  three fixed signs except the second from it; grahas merely inherit their
  sign's aspects (sūtras 1.1.2–1.1.3). Parāśari gives each graha a 7th-house
  aspect plus special aspects for Mars, Jupiter and Saturn. For any real chart
  the two schemes draw different lines.
- **Significators are variable and assigned by degree.** The Ātmakāraka is
  whichever graha has advanced furthest within its sign (1.1.10), and the
  remaining kārakas follow in descending order. In Parāśari the Moon is always
  the mother's significator; in Jaimini the Mātṛkāraka is whichever graha ranks
  fourth *in this chart*. Jaimini then runs a *fixed* significator layer as
  well (1.1.19–1.1.23), so both layers operate at once.
- **A second house frame.** Ārūḍha padas (1.1.29–1.1.31) generate a parallel
  twelve-house chart read alongside the rāśi chart, plus Horā, Bhāva, Ghaṭikā
  and Varṇada lagnas — none of which exist in the Parāśari core.
- **Daśās run on signs.** Chara daśā is a sign sequence whose direction depends
  on sign parity (1.1.24–1.1.27) and whose total is bounded at 144 years
  (1.1.33). Viṃśottarī is a nakṣatra-seeded *planetary* daśā of 120 years.
  Different mechanism, different periods, different lengths.
- **The text is written in numeric code.** Sūtra 1.1.31 declares that houses and
  signs throughout are to be read as kaṭapayādi consonant numerals; 1.1.32
  exempts planet names. Nothing comparable governs the Parāśari texts, and it
  is the root of most commentarial dispute.

Jaimini also *delegates* what Parāśari defines: sūtra 1.1.35 says the vargas are
to be taken as current among practitioners. A Jaimini engine must import its
divisional definitions from a named external text and may never attribute them
to Jaimini.

## Inspected witnesses

### K. V. Abhyankar, *The Upadeśa Sūtra of Jaimini* (Ahmedabad, 1951)

Archive identifier `jaimini-kva-a-4-size`. Gujarat Vidyāsabhā / Sheth B. J.
Institute, Research Series No. 36, 500 copies.

This is the controlling scholarly witness and there is nothing else like it in
the retrieved material. Its own foreword states the editorial situation
plainly: Adhyāyas 1–2 critically edited from **fifteen** manuscripts; Adhyāyas
3–4 edited for the first time from **three**; the editor's commentary supplied
only through Adhyāya 3 Pāda 3, "leaving the rest to some future scholar." It
also records the editor's judgement that the two available commentaries are
"comparatively modern", textually corrupt, and at places unsatisfactory — a
verdict this pass independently corroborated.

The OCR recovered the complete English apparatus (introduction §§1–130, the
full English translation of the sūtras, and the contents of four appendices)
and **zero Devanagari**. The Sanskrit pages came out as Latin gibberish. That
single failure is the largest blocker on this tradition, because behind it sit
the variant apparatus, the Jaimini-Sūtra-Kārikā (Appendix 1), the comparative
table against Bṛhad-Yavana-Jātaka, Bṛhajjātaka, Sārāvalī and Bṛhat Pārāśarī
(Appendix 4), and fourteen worked kāraka-kuṇḍalīs.

Research implication: Abhyankar's English is usable now for passage alignment
and was used exactly that way. His introduction is his own scholarship and must
be tagged as editorial, not attributed to Jaimini — his date argument, his
Greece comparison, and his navāṃśa/nakṣatra-caraṇa hypothesis are all his.

Rights: 1951 Indian publication, status unresolved. The uploader applied
CC BY-NC-ND, which an uploader cannot grant over another party's work. Used for
internal alignment and paraphrase only. This is not a practical constraint,
because the Sanskrit itself is quoted from the public-domain witness instead.

### *Jaiminīyasūtram* with the *Sūtrārthaprakāśikā* commentary

Archive identifier `in.ernet.dli.2015.242319`. Benares; DLI citation date 1951.

The primary **Sanskrit** witness for this pack, and by a wide margin the best
Devanagari OCR of the five objects (104,988 Devanagari characters, largely
legible). Adhyāya 1 Pāda 1 sūtras 1–33 were read in the original with the
commentary.

The commentary is a genuine critical instrument rather than a paraphrase. It
names and argues with Nīlakaṇṭha twice, with the author of the *Subodhinī*
three times, and with Premanidhi Paṇḍita once. It quotes vṛddha kārikās for
rāśi dṛṣṭi, the kāraka degree ranking, the Rāhu reverse-count convention, the
Horā and Bhāva Lagna rates and the Varṇada construction. It quotes a
Bṛhat-Pārāśara-Horā-Sārāṃśa passage on the seven kārakas — Parāśara cited as a
witness *inside* a Jaimini commentary. And at 1.1.31 it twice admits it cannot
explain the rule it is transmitting.

Its running sūtra text has **seven** chara kārakas and no Pitṛkāraka sūtra, and
it explicitly reports and rejects the manuscripts that carry one — the same
manuscripts Abhyankar's critical text follows.

Research implication: this is the witness that makes the pack possible, and its
authorship and date are the least secure thing about it. The Archive record
associates the *Sūtrārtha Prakāśikā* with Rāma Ratna Ojhā; the title page has
not been read. That must be settled before any rule is promoted.

### Nīlakaṇṭha, *Jaimini Sūtra Vyākhyā* (Jammu MS 882 Gha)

Archive identifier `JaiminiSutraWithVyakhyaNeelkanth882GhaAlm5Shlf1Devanagari
Jyotisha`, from the Dharmārtha Trust manuscripts at the Raghunath Temple,
Jammu; digitized by eGangotri under CC0.

The only **direct** witness to Nīlakaṇṭha retrieved. Manuscript OCR quality is
poor (28,648 Devanagari characters, much of it garbled, with running heads and
marginalia interleaved). Content is identifiable — the visible folios treat
lagneśa and daśameśa in movable/fixed/dual pairings yielding dīrgha, madhya and
alpa āyus, which is the Jaimini three-fold longevity determination, with Horā
Lagna in view.

**No rule in this pack is extracted from this manuscript.** Every Nīlakaṇṭha
position in the manifest rests on the Sūtrārthaprakāśikā's quotation of him,
and is labelled as such on the rule. That is an uncomfortable position: at
1.1.31 we know only what Nīlakaṇṭha *denied*, reported by the man denying him
back. Transcription of these folios is the second item on the missing-work
list.

### Sītārāma Jhā, *Jaimini Sūtram* with the *Tattvadarśa* Hindi ṭīkā

Archive identifier `xyly-jaimini-sutram-sanskrit-hindi-tika-sahitam-tattvad`.
Benares, Master Khelari Lal and Sons; undated; CC0 as applied by the digitizer.

Third witness, used for corroboration rather than extraction. Its editor's
Hindi preface is independently valuable on two points. It states what
distinguishes this text from other jātaka works: sign and planetary dṛṣṭi,
results via the *ātmādi* kārakas, results from *pada* and *upapada*,
chara/sthira daśā results, and āyurdāya reckoned by several methods — an
inventory that matches this audit's divergence claim from an unrelated
direction. And it names **Nīlakaṇṭha and Keśava** among the older ācāryas who
wrote ṭīkās and kārikās on the text, independently corroborating the Nīlakaṇṭha
attribution and adding a commentator this pass has not otherwise located.

This edition appears to cover two adhyāyas.

### B. Suryanārāin Rao, *Jaimini Sutras* (DLI, cited 1949)

Archive identifier `in.ernet.dli.2015.486584`.

Retrieved, inspected, and **unusable**. A Devanagari OCR profile was applied to
an English-language book: 76,936 Devanagari characters and zero Latin
characters across a text that is in English. No sentence is recoverable.

What survives is the table-of-contents structure, which independently confirms
this pack's inventory of distinctively Jaimini machinery — aspects of planets
and zodiacal signs, kārakas or significators, and a list of special lagnas
including Ārūḍha/Pada, Varṇada, Ghaṭikā, Horā and Bhāva Lagna. No rule is drawn
from it.

Research implication: worth re-acquiring, because Rao is a third independent
translation and would be the natural tie-breaker on the 1.1.15 numbering
question.

## Retrieval routes that failed, and one trap

**GRETIL holds no astrological Jaimini.** The full index was downloaded and
searched. GRETIL carries Jaimini-Gṛhyasūtra, Jaimini Mīmāṃsāsūtra (plain and
with commentary 1–7), Jaiminīya-Brāhmaṇa, Jaiminīya-Upaniṣad-Brāhmaṇa and
Jaiminīyanyāyamālāvistara — and not the Upadeśa Sūtra. Recorded as a negative so
the route is not retried blindly.

**sanskritdocuments.org** did not yield it either.

**The trap.** Most archive.org items titled "Jaimini Sutra" are the **Pūrva
Mīmāṃsā Sūtra** of Jaimini, a work of Vedic ritual hermeneutics with no
astrological content whatever. Specifically excluded during this pass: the
Allahabad 1911 *Sacred Books of the Hindus* volume (Gaṅgānātha Jhā), the
Śāstradīpikā of Pārthasārathi Miśra, the Mīmāṃsākaustubha series, Mohan Lal
Sandal's translation, and the Jaimini Gṛhyasūtra (Caland 1922). A future pass
that ingests by title alone will pick up the wrong Jaimini; this is recorded in
the access manifest so it does not happen twice.

**Modern treatments were excluded by policy, not by failure.** Sanjay Rath's
course on the Upadeśa Sūtra, B. V. Raman's *Studies in Jaimini Astrology*,
Iranganti Rangacharya and the Sureś Chandra Miśra Hindi edition were all
identified and not used. Under this corpus's translation policy, reading the
public-domain Sanskrit directly and publishing original, rendering and citation
together is more defensible than paraphrasing someone else's copyrighted
English.

## What was encoded

`jaimini_rule_manifest.json` records **41** atomic, research-only rules covering
Adhyāya 1 Pāda 1: sign and planetary dṛṣṭi, the full argalā complex, chara
kāraka assignment with both scheme variants and both Rāhu conventions, sthira
kārakas, kaṭapayādi decoding, ārūḍha padas, daśā counting direction and the
144-year bound, the four special lagnas, natural strength, and the varga
delegation.

`jaimini_validation_vectors.json` supplies **43** vectors, covering every rule.
Several are deliberately *negative*: they assert that the engine must abstain.
Vectors `jaimini.v.karaka.rank.seven` and
`jaimini.v.karaka.rank.eight-with-rahu-reversed` run the same planetary
longitudes through both conventions and produce different Ātmakārakas, which is
the clearest available demonstration of why the convention must be disclosed.

Twelve commentator disagreements were found and are tabulated in
`extraction_notes.md` §8. Ten are encoded as separate attributed rules with
`conflicts_with` links. Two are recorded but not promoted, with reasons.

The pack deliberately does **not** encode: an ayanāṃśa (the sūtras fix none), a
resolution of the seven-versus-eight kāraka question, a Rāhu convention, a
chara daśā period length (the sūtra fixes the counting but not the conventions),
or any delineation from outside Adhyāya 1 Pāda 1.

## Safety and publication limits

The inspected contents include āyurdāya, time of death, kind and cause of
death, and gendered and status-bearing family material. They may be researched
and represented historically. Customer output must not:

- state a lifespan, a death age, or a survival deadline;
- state a time, kind or cause of death;
- present the Ātmakāraka's *bandha/mokṣa* signification as a prediction — the
  commentary's "bondage" includes literal imprisonment;
- assert a kāraka assignment without disclosing the scheme and Rāhu convention
  it depends on;
- merge Jaimini and Parāśari verdicts into one judgement;
- attribute any divisional chart definition to Jaimini.

The full refusal list is in [`defensibility_spec.md`](defensibility_spec.md).

## Next source work

1. Acquire the page images for `jaimini-kva-a-4-size`. One acquisition clears
   the Pitṛkāraka question, the Jaimini-Sūtra-Kārikā, the Parāśari comparison
   table, and fourteen worked charts.
2. Commission Devanagari transcription of the Jammu Nīlakaṇṭha folios covering
   Adhyāya 1 Pāda 1.
3. Obtain independent Sanskrit review of the restorations in
   `extraction_notes.md` before any rule is promoted.
4. Read Adhyāya 1 Pādas 2–4 and Adhyāyas 2–4 in the original.
5. Confirm the Sūtrārthaprakāśikā's authorship and date from the title page.
6. Build a sūtra-numbering concordance across Abhyankar, the
   Sūtrārthaprakāśikā, Sītārāma Jhā and Rao. Until it exists, an external
   citation of "Jaimini 1.1.15" is ambiguous.
7. Extract Abhyankar's fourteen kāraka-kuṇḍalīs into a `worked_examples.json`
   suite. These are named, dated modern figures with the editor's own stated
   judgements — the strongest validation available to this tradition, and
   currently the largest single piece of unrealised value in it.
