# Defensibility standard

Status: governing standard for every reading section  
Updated: 2026-08-01

## The test

A reading is defendable when a serious practitioner **of that tradition** reads
their section and cannot truthfully say any of:

1. "You missed our core method." — a technique the tradition's own authorities
   treat as mandatory is absent.
2. "That is not what the text says." — a delineation misstates its source.
3. "Our tradition does not claim that." — a claim is imported from another
   system, or invented where the sources are silent.

The adversary is the expert of that system, not a general reader. A section that
would satisfy a curious layperson and fail a practitioner has failed.

## The five requirements

Every tradition pack must satisfy all five before its reading section ships.

### 1. Complete the non-negotiable core

Each tradition has techniques its own authorities treat as required. A Jyotisha
reading without navamsha and dasha treatment is indefensible regardless of prose
quality; a BaZi reading without month-command assessment is indefensible; a
Hellenistic reading without sect is indefensible.

Each `defensibility_spec.md` therefore opens with a **core-technique checklist**
derived from the sources, not from implementation convenience. Anything on that
checklist that is not implemented must appear in the reading as a stated
limitation, not silently omitted.

### 2. Judge in the tradition's own order

Systems have a judgment hierarchy: sect before dignity; day-master and month
command before ten gods; lagna and its lord before divisional refinement.
Flattening a hierarchy into parallel bullet points is the reliable tell of a
synthetic reading. Each spec records the tradition's hierarchy and the composer
must execute it in that order.

### 3. Every interpretive sentence traces to a passage

No delineation without a citation. Method forks are preserved rather than
averaged. Anything the product chose rather than inherited is labeled
`configured_method` with its alternatives named. This is already the house style
of the live Western report and it is the minimum bar elsewhere.

### 4. Reproduce the tradition's own worked examples

This is the strongest available proof short of hiring a specialist per tradition.
The classical corpora contain **worked charts**: Lilly judges example figures in
*Christian Astrology*, Valens works charts through the *Anthology*, Jyotisha
commentaries carry worked examples, and BaZi texts carry case charts (命例). If
the engine, given the same chart, reproduces the classical author's own stated
judgment, that result is difficult for a critic to wave away.

Each spec inventories which worked examples exist and where. Each pack ships a
machine-readable worked-example suite whose results are published pass or fail.

### 5. Refuse what the tradition cannot say

A Babylonian section stating "this corpus judges states and kings, not
personalities — here are the positions and the omens that would have applied" is
defendable. An invented Babylonian personality reading is indefensible by
construction. The same holds for pharaonic Egyptian natal claims, for Nahua day
signs without an approved correlation, and for any lifespan number presented
without its branch and its doubts.

The honest ceiling, stated plainly, is part of "best possible." Sometimes it is
most of it.

## Translation is not a gate for quotation

A correction to an error this standard originally encouraged.

Requiring "an independent specialist translation" before a tradition can say
anything conflates two different activities:

**Rule promotion into a validated pack** — where a rule will drive automated
judgment — legitimately wants independent review. Not because reading the
language is hard, but because technical terms (`yongshen`, `hayyiz`,
`moolatrikona`, `de ling`) carry doctrinal weight that a single unreviewed
reading can silently distort, and because the pack is a single point of failure
for every reading built on it.

**Quotation and reading** does not. Where the source is public domain, rendering
it directly is *more* defensible than depending on a modern copyrighted
translation, because the reader can be given all three of: the original text, the
rendering, and the passage citation. A specialist can then check the rendering
against the original — which is impossible when the product paraphrases someone
else's copyrighted English to avoid quoting it.

The practical consequences:

| Situation | Correct action |
|---|---|
| Public-domain original, no modern translation rights | **Translate directly.** Show original + rendering + citation. Grade as `engine_translation_unreviewed`. |
| Public-domain original, modern translation exists but is copyrighted | Same. The modern translation is a convenience, not a prerequisite. |
| Original not retrievable | **This is the real blocker** — an access problem, not a language or rights problem. Name it as such. |
| Rule promotion into a validated pack | Independent specialist review still required. |

Applies across the corpus: Classical Nahuatl and 16th-century Spanish
(Florentine Codex), Classical Chinese (`Yuanhai Ziping`, `Sanming Tonghui`),
Sanskrit (Brhajjataka, BPHS), Arabic (al-Biruni, Abu Ma'shar), Hebrew (Ibn Ezra),
Greek (Valens, Ptolemy), Latin (Lilly's sources, the Hermann/John/Adelard
lineages), and Akkadian.

Where a blocker is recorded, it must state which of the four rows above applies.
A blocker that says "awaiting translation" when the original is public domain and
retrievable is not a blocker — it is unfinished work.

## The defense brief

Each tradition additionally publishes a defense brief covering: sources and
editions used; techniques covered and techniques omitted; conventions chosen and
why; worked examples attempted and their results; and what the section refuses to
output. That document is what a hostile expert engages with, and it is what makes
"best reading available" a checkable claim rather than a marketing sentence.

## Spec template

Every `<tradition>/defensibility_spec.md` carries these sections:

```
## Core-technique checklist      # mandatory techniques + citation + status
## Judgment hierarchy            # ordered; the composer executes this order
## Worked-example inventory      # which classical charts exist, where, usable?
## Refusal list                  # what this tradition will not be made to say
## Conventions requiring disclosure
## Current implementation gap
```

Status vocabulary for checklist items:

| Status | Meaning |
|---|---|
| `implemented` | computed and rendered today |
| `computable` | inputs exist; composer work remains |
| `source_gated` | blocked on an edition, translation, or specialist review |
| `refused` | the tradition or its surviving sources cannot support it |
