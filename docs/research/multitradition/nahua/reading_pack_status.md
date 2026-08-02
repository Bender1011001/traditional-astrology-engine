# Nahua reading pack — status and blockers

Status: **blocked before encoding**  
Updated: 2026-08-01  
Spec: [defensibility_spec.md](defensibility_spec.md)

## What was attempted

M4 of the autonomous build session: encode Florentine Codex Book 4 day-sign and
trecena auguries as passage-cited statements, and wire them into the panel as the
first non-Western reading section.

The defensibility spec identifies this as the highest-value interpretive work
available in any non-Western track, because the source is public, the auguries
are substantive, and the validated tonalpohualli pack already anchors to stable
Getty folio and text-record identifiers.

## Why it is blocked

**1. The text is not machine-retrievable from the Getty edition.**
`florentinecodex.getty.edu` is a client-rendered application. Fetching
`/book/4/folio/1r` returns navigation, citation metadata, and availability flags
for transcriptions and translations, but not the transcription or translation
text itself. The content that the validated pack cites by text-record ID
(`ecfe83af-...`, `3401d7c1-...`, and two others on folio 1r) was originally
inspected visually, not extracted programmatically.

Encoding auguries without retrieving the text would mean writing them from
recollection. For a pack whose entire purpose is passage-cited quotation, that is
self-defeating — it would produce exactly the unsourced day-sign table the
defensibility spec refuses.

**2. Translation rights are an open question, not a formality.**
The standard English translation of the Florentine Codex (Anderson and Dibble,
School of American Research / University of Utah Press, 1950-1982) is a 20th
century scholarly work and is not public domain. The Getty digital edition
carries its own translation with its own terms. The 16th century Nahuatl and
Spanish are old; the modern English rendering of them is not.

The corpus already treats rights review as a release gate. For this pack the
gate arrives earlier than usual: it governs whether the auguries can be *quoted*
at all, or only paraphrased with citation — and paraphrase materially weakens the
product, because the value is Sahagun's informants' own conditional language.

## What is not blocked

The structural finding stands and is already encoded in the defensibility spec:
this tradition's interpretation is better sourced than its date arithmetic. That
inverts the normal product shape and remains true regardless of access route.

The panel section correctly refuses to assign a day sign today, and states why.
That refusal is the defendable position and needs no further work to be honest.

## Required next actions, in order

1. **Resolve text access.** Either (a) locate the Getty API endpoint the client
   application calls for transcription and translation records, (b) obtain the
   Book 4 text through an institutional route, or (c) work from a public-domain
   edition of the Nahuatl and Spanish with an independent translation.
2. **Rights review on the chosen route**, specifically covering verbatim
   quotation of the English translation in a customer-facing artifact.
3. **Only then** encode auguries, one per day sign, each carrying folio,
   text-record ID, and the source's conditional language preserved intact.
4. Wire into the panel as a reading section that quotes the corpus and continues
   to refuse assigning the reader a day sign.

## Note on sequencing

This blocker does not invalidate the M4 design; it moves the first non-Western
reading section to whichever tradition clears its source gate first. On current
evidence that is **medieval Jewish**, whose defensibility spec found the Ibn Ezra
layer already computing inside the live report and needing attribution rather
than new sourcing.
