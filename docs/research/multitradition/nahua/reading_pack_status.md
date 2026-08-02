# Nahua reading pack — status and blockers

Status: **blocked on retrieval only**
Updated: 2026-08-01 (revised — see correction below)
Spec: [defensibility_spec.md](defensibility_spec.md)

## Correction to the previous version of this document

The first version of this file gave two blockers: text retrieval, and rights on
the Anderson & Dibble English translation. **The rights blocker was wrong** and
is withdrawn.

The reasoning error: the Anderson & Dibble English is only needed if the English
is what we quote. It is not. The Florentine Codex's 16th-century Nahuatl and
Sahagun's parallel 16th-century Spanish are public domain. Rendering those
directly removes the copyright question entirely, and produces a *better*
artifact than depending on a modern translation — because the reader can be shown
the original, the rendering, and the folio citation together, and a specialist
can check all three against each other.

See the "Translation is not a gate for quotation" section added to
[../DEFENSIBILITY.md](../DEFENSIBILITY.md), which now governs this class of
decision corpus-wide.

## The actual blocker, correctly scoped

**Retrieval.** No route tried from this environment returns the source text:

| Route | Result |
|---|---|
| `florentinecodex.getty.edu/book/4/folio/1r` | client-rendered application; HTML returns navigation, citation metadata, and availability flags, but no transcription or translation text |
| `loc.gov/item/2021667837` (World Digital Library) | HTTP 403 to the fetch tool |

This is an **access problem**, not a language problem and not a rights problem.
The Library of Congress states it is unaware of copyright restrictions on the WDL
Florentine Codex materials.

## What unblocks it

Any one of these is sufficient, and the first is trivial:

1. **Drop page images into the repo.** Download the Book 4 folios covering the
   twenty day signs from the WDL or Getty viewer and commit them under
   `docs/research/multitradition/nahua/folios/`. Images can be read directly; the
   Nahuatl and Spanish can be transcribed and rendered from them.
2. **Find the Getty client's data endpoint.** The application fetches
   transcription and translation records by ID — the validated tonalpohualli pack
   already cites four such IDs on folio 1r (`ecfe83af-...`, `3401d7c1-...`,
   `31115076-...`, `e91d245b-...`). If that endpoint is reachable, the text is
   directly retrievable.
3. **Institutional or offline copy** of the Nahuatl/Spanish transcription.

## Encoding plan once text is in hand

1. Per day sign: transcribe the Nahuatl, transcribe the Spanish, render an
   English translation, record the folio and Getty text-record ID.
2. Grade the rendering `engine_translation_unreviewed` — honest about being
   unreviewed, and checkable because the original travels with it.
3. **Preserve the conditional language.** Book 4's auguries are frequently
   conditioned on conduct ("if he did penance...", "if he was negligent..."). That
   conditionality is the doctrine. Flattening it into a trait list is precisely
   the failure the defensibility spec forbids.
4. Wire into the panel as a reading section that quotes the corpus per sign and
   **continues to refuse assigning the reader a day sign**, because the
   correlation problem is independent of the text problem and remains unsolved.

## What is not blocked

The structural finding stands: this tradition's interpretation is better sourced
than its date arithmetic, which inverts the normal product shape.

The panel's refusal to assign a day sign is correct today and is unaffected by
any of the above. The correlation gap and the retrieval gap are separate; solving
retrieval enables quotation of the corpus, not personalization of it.
