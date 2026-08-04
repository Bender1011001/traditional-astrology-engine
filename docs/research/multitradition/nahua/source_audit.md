# Nahua / Central Mexican tonalpohualli source audit

Status: research foundation, not production approval  
Updated: 2026-08-01

## Result of this pass

The Nahua `tonalpohualli` has direct evidence for divination involving birth days, but it is not a twenty-sign personality zodiac. The surviving evidence is layered across pictorial manuscripts, Nahuatl testimony recorded in a colonial project, Spanish framing and annotations, later copies, and modern scholarship.

This pass now includes a machine-readable **cycle-arithmetic artifact only**. It validates all 260 coefficient/sign pairs, the twenty trecena heads, negative offsets, an explicitly synthetic date fixture, missing-epoch rejection, cross-tradition epoch rejection, and the absence of interpretation output. It deliberately has no default correlation and is neither live nor customer-eligible.

A defensible engine must combine—but never flatten—the following layers:

- coefficient 1–13;
- one of twenty day signs;
- position within a thirteen-day `trecena`;
- trecena patron(s);
- Lords of the Day and Night where attested by the selected manuscript;
- associated birds or other series where attested;
- year/month/day context and named ritual use;
- direct passage or image-specific augury;
- actions, observances, naming, and conduct that may qualify an outcome;
- source, region, date, and colonial mediation.

## Primary/near-primary witnesses inspected

### Florentine Codex, Book 4

The Getty digital edition provides synchronized manuscript images, Nahuatl text, Spanish text/framing, English translation and notes, and structured iconographic metadata. Its embedded folio record exposes stable folio, canvas, IIIF-manifest, text-record, language and citation identifiers. Book 4 explicitly concerns good and bad days and qualities associated with persons born under the signs, proceeding through the thirteen-day periods.

The first chapter is already enough to reject mechanical fatalism: it associates good fortune with the opening sign but says it may be ruined through negligence. A rule encoder must capture both the initial augury and conduct/condition clauses.

The source is colonial and collaborative. “Sahagun says” is insufficient attribution: the system must distinguish Nahua-language testimony and imagery from Sahagun's headings, theological labels, editorial divisions, and later English translation.

Source: [Digital Florentine Codex, Book 4 folio 1r](https://florentinecodex.getty.edu/es/book/4/folio/1r)

### INAH-hosted complete cycle table

The INAH scan of Manuel Orozco y Berra's historical *El Tonalamatl* supplies a complete twenty-row day-sign order, the coefficient permutation across the twenty trecenas, the trecena-head order, and the return after 260 positions. It is used as a grade-B arithmetic witness, not as a modern controlling interpretation or orthographic authority. Historical spellings remain visible in the machine-readable spec while stable machine identifiers are kept separate.

Source: [INAH scan, El Tonalamatl](https://mna.inah.gob.mx/docs/anales_/109.pdf)

### Tonalamatl de Aubin

INAH identifies this seventeenth-century Tlaxcalan amate screenfold as a book of the day-and-destiny count. The described panels include trecena patrons, numbered days, nine Lords of the Night, thirteen Lords of the Day, and thirteen birds. This proves that a day-sign-only implementation omits essential pictorial layers.

Source: [INAH Tonalamatl de Aubin](https://www.codices.inah.gob.mx/pc/contenido.php?id=2)

Access warning recorded 2026-08-01: the live INAH page's download area contained unrelated gambling links. The institutional descriptive block remains useful evidence, but no linked form or off-domain download is trusted. Plate acquisition must use a clean institutional or BnF endpoint.

### Codex Borbonicus

The French National Assembly, which holds the manuscript, describes an amate screenfold with later Spanish annotations used as a Mexican religious/divinatory calendar and festival ritual source. Original imagery and later annotation must be encoded separately. Its colonial acquisition and current Mexican cultural-property concerns are material provenance, not a footnote to omit.

Source: [Assembly facsimile](https://www.assemblee-nationale.fr/histoire/7gf-borbonicus.asp)

### Narrow INAH iconographic project

The inspected 2023 INAH project entry concerns shell ornaments in the ninth and tenth trecenas of the Codex Borbonicus. It may support that bounded iconographic workstream, but it is not a general calculation or interpretation authority. Its named outputs still require collection.

Source: [INAH Tonalpohualli project](https://www.etnohistoria.inah.gob.mx/public/proyecto_interior.php?id=Mw%3D%3D)

## Corpus still required

The controlling comparative corpus must include at least:

- Codex Borgia and related Borgia Group manuscripts;
- Codex Vaticanus B;
- Codex Fejervary-Mayer;
- Codex Cospi where relevant;
- Codex Telleriano-Remensis;
- Codex Vaticanus A / Rios;
- Codex Borbonicus;
- Tonalamatl de Aubin;
- Florentine Codex Book 4;
- other Nahuatl/Spanish colonial descriptions and current Nahua scholarship.

Each witness gets its own sequence and interpretation layer. Similar imagery is a comparison link, not proof of identical meaning.

## Calendar kernel

The 260-day count combines thirteen coefficients and twenty day signs. The arithmetic kernel must store:

```json
{
  "epoch_id": "named colonial/modern correlation",
  "epoch_civil_date": "date with calendar policy",
  "epoch_tonalpohualli": {"number": 1, "sign": "Cipactli"},
  "region": "named polity/community/source",
  "authority": "publication and passage",
  "uncertainty": "declared",
  "day_start": "source-specific",
  "enabled_series": ["trecena", "lords_night", "lords_day", "birds"]
}
```

A modern birth date cannot be mapped responsibly until the civil-date correlation, region, and day boundary are selected. The Maya correlation must never be reused merely because both traditions use 260-day cycles.

## Pictorial/passsage rule model

```json
{
  "witness": "tonalamatl_aubin",
  "plate_or_folio": "stable locator",
  "region_period": "source identity",
  "calendar_position": {
    "trecena": "1 Cipactli",
    "day_number": 1,
    "day_sign": "Cipactli",
    "night_lord": null,
    "day_lord": null,
    "bird": null
  },
  "pictorial_elements": [],
  "nahuatl_terms": [],
  "colonial_annotations": [],
  "direct_augury": null,
  "qualifying_conduct_or_ritual": [],
  "modern_interpretation": [],
  "status": "direct|inferred|disputed",
  "reviewers": []
}
```

Do not derive a meaning by adding independent keyword lists for number, sign, patron, and bird unless a source supplies that compositional procedure.

## Product boundaries

### Historical calendar converter

Produces the coefficient/day sign and, where a source permits, the other cyclic series under a named epoch. It must show uncertainty and source scope.

### Tonalamatl explorer

Lets a user inspect a trecena/day across selected codices and Book 4, seeing agreements, differences, original images, Nahuatl passages, colonial annotation, and modern scholarship.

### Birth-day reconstruction

Can show what selected witnesses say about a birth-day configuration. It must present conditions, alternatives, and mediation, not declare an immutable personality or fate.

### Living Nahua practice

Requires separate community-based research and consent. Colonial and pre-Columbian sources do not authorize the system to speak for living Nahua communities.

## Translation and provenance workflow

1. Capture institutional images and catalog records for every manuscript.
2. Record provenance, production estimate, material, region, known annotations, restoration, and colonial custody.
3. Align pictorial pages across witnesses without assuming equivalence.
4. For alphabetic texts, align Classical Nahuatl, Spanish, and English by sentence/folio.
5. Mark whether each heading or claim is Nahua testimony, colonial editor framing, later annotation, or modern interpretation.
6. Obtain Classical Nahuatl, codicology, and contemporary Nahua review.
7. Resolve image and translation rights before publication.

## Validation gates

- Modular cycle arithmetic must round-trip across at least 260 consecutive days.
- Epoch/correlation alternatives must produce visibly distinct results and separate cache keys.
- Every pictorial series must match the full selected manuscript sequence.
- A Book 4 claim must link to Nahuatl text and folio, not only an English heading.
- Mutation tests must show that changing number, day sign, trecena, or enabled lord series selects different source evidence where the manuscript actually distinguishes them.
- Cross-codex comparison must preserve disagreements.
- A qualified specialist must reproduce the first trecena from the source pack without seeing engine output.

## Cultural and safety policy

- Never call the product an “Aztec zodiac.”
- Use `Nahua`, `Mexica`, or a more specific identity according to the source; do not treat the labels as automatically interchangeable.
- Do not make deterministic death, illness, criminality, fertility, warfare, sacrifice, or moral-character predictions.
- Preserve colonial violence, Christian polemic, and manuscript custody as context rather than repeating colonial judgments as neutral facts.
- Do not appropriate living ceremonial practice.
- Do not merge Nahua and Maya day meanings.

## First bounded pilot

Build a **One Cipactli trecena source concordance**. The preliminary cycle-only kernel is complete, but the concordance itself is not:

1. acquire and justify one explicitly chosen colonial correlation and day boundary; the current 260-day arithmetic uses no historical default epoch;
2. manifest the corresponding plates in Tonalamatl de Aubin and Codex Borbonicus;
3. align the thirteen Book 4 day passages in Nahuatl, Spanish, and English;
4. record patrons, day/night lords, birds, imagery, auguries, and conditional clauses only where the witness supplies them;
5. document disagreements and colonial layers;
6. obtain Classical Nahuatl and codex-specialist review;
7. expand only after the entire trecena passes blind reproduction.

Current artifacts:

- `tonalpohualli_cycle_spec.json`: inspected sign order, source anchors, epoch contract, output contract, and product boundary;
- `calendar_rule_manifest.json`: eight atomic calendar/boundary rules;
- `calendar_validation_vectors.json`: twelve positive, wraparound, negative, conversion, rejection, and output-boundary fixtures;
- `validate_tonalpohualli_cycle.py`: executable 260-pair uniqueness, recurrence, trecena-head, vector-coverage, and product-boundary gate.


## 2026-08-04: the correlation candidates were never hunted

This track held 72 Florentine Book 4 auguries and refused to place a birth "because
no approved epoch exists". Nobody had gone looking for the candidates. They are
published and named.

**Found.** Susan Milbrath, "Seasonal Cycles, Veintena Rituals, and Yearbearer
Ceremonies in Central Mexico", *Trace* 81 (2022): 247-280, DOI
`10.22134/trace.81.2022.142`, open full text at
<https://www.redalyc.org/journal/4238/423872655010/html/>. It states Caso's two
anchors and credits them to Caso 1967, *Los calendarios prehispanicos*, and Caso
1971, "Calendrical Systems of Central Mexico", HMAI 10-11: 333-48.

- **13 August 1521 Julian = 1 Coatl, year 3 Calli** (the fall of Tenochtitlan).
- **8 November 1519 Julian = 8 Ehecatl, ninth day of Quecholli, year 1 Acatl.**

### The fork, recomputed here from first principles

The two anchors disagree. This repository converted both dates to Julian Day
Numbers and both day-signs to positions in the 260-day cycle:

- JDN 13 Aug 1521 = 2,276,828; JDN 8 Nov 1519 = 2,276,184; elapsed **644 days**.
- 644 mod 260 = **124**.
- 1 Coatl sits at cycle position 104; projecting back 124 gives position **240**,
  which is **7 Cipactli** - not the 8 Ehecatl (position 241) that Caso records.

The offset is exactly one day, which reproduces the discrepancy the article
attributes to Caso, and Caso's own reported resolution is that the Mexica day began
at **noon**, so one European day can map to two adjacent tonalpohualli days
depending on the time of the event. For births this is not academic: a birth before
local noon and one after fall on different day signs under that resolution.

### What was encoded

`correlation_candidates_manifest.json` - six candidates with anchors, evidence
grades and blocking reasons: the two Caso anchors (grade B), Tena's 26 February
year start, the Nuttall-Ochoa equinox-locked scheme, Meza's fixed Cipactli year
start, and Francisco Rodriguez Cortes' living Chiapas count (all grade D, primary
publications not retrieved). Plus `correlation_rule_manifest.json` (12 rules) and
`correlation_validation_vectors.json` (12 vectors).

`default_candidate` is `null` and stays null. The pack fails closed when no
candidate is selected, and when one is selected it must be named alongside the
alternatives it displaced and alongside the Caso fork.

Two candidates are recorded as structurally unusable rather than merely ungated:
the Nuttall-Ochoa scheme is an *observational* rule tied to the sighted equinox and
so cannot be reduced to a fixed day offset, and a fixed Cipactli year start cannot
hold across a 365-day year because 365 is not a multiple of 20.

### The gate that now matters more

`nahua.correlation.augury_application_gate`. A correlation makes it technically
possible to render Book 4 as a birth-day trait table, and that would misstate the
source. Book 4's first chapter heading says the day-fortune is *merited*
(`qujmaceoaia`) and can be forfeited through one's own negligence
(`tlatziviliz` / `floxura`), and folios 21r, 35v, 52v and 55v show the operative
sign being assigned by ritual choice and household means rather than by the date of
birth.

### Still to obtain

Caso 1967 and Caso 1971 themselves; Tena, *El calendario mexica y la cronografia*;
Nuttall's papers; H. B. Nicholson's restatement (the pairing is cited in the field
as the Caso-Nicholson correlation, and Nicholson's own statement was not retrieved
in this pass); Hanns J. Prem's correlation papers. Searches run:
`Caso 1939 correlation tonalpohualli Christian calendar "1 Cipactli" anchor date
Sahagun 1521 Tenochtitlan fall day sign`; the calmecacanahuac correlation survey;
the azteccalendar.com correlation settings page; and the Milbrath article read in
full.
