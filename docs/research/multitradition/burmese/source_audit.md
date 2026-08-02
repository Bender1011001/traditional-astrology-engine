# Burmese and related Myanmar astrology source audit

Status: research foundation, not production approval  
Updated: 2026-07-31

## Result of this pass

The research now has a viable Burmese/Arakanese calendar workstream and a direct
digitized astrological manuscript lead. It still does not have a production-grade
`Mahabote` corpus. English commercial manuals and modern calculators may help
discover terminology or test cases, but they cannot define traditional rules.

Required separation includes:

- original Burmese `Makaranta` calendar methods;
- later `Thandeikta` changes and historical official decisions;
- Arakanese calendar variants;
- current Myanmar calendar practice;
- birth-day/constellation manuscript astrology;
- `Mahabote`, if its indigenous textual and teaching lineage can be established;
- Burmese, Pali, Pa'O, Mon, and other linguistic/community layers; and
- apotropaic, magical, ritual, medical, and natal material within mixed manuals.

## Calendar corpus

### Irwin 1909

Irwin's *The Burmese and Arakanese Calendars* is a full technical monograph with
conversion tables, historical rules, corrections, and discussion of official
calendar practice. The preface names U Wizaya of Mandalay and Saya Maung Maung
of Kemmendine as important informants.

The book is also a colonial-period work with its own reform proposals. Its layers
must be marked separately:

- description of observed Burmese practice;
- description of Arakanese practice;
- quotation or explanation of `Thandeikta`;
- official tables and historical promulgations;
- errors corrected in the printed corrigenda; and
- Irwin's proposed future reforms.

Source: [public-domain scan](https://upload.wikimedia.org/wikipedia/commons/6/68/The_Burmese_%26_Arakanese_calendars_%28IA_burmesearakanese00irwiiala%29.pdf)

### Modern comparative calculation

Gislen distinguishes the original Burmese calculation from later `Thandeikta`
changes and supplies the original fixed intercalary-month pattern,
intercalary-day logic, exact quantities, and examples. His main conclusion is
that Burmese and Thai intercalation cannot share an implementation despite their
similar surface vocabulary and common era.

Source: [full article](https://www.researchgate.net/publication/326293290_ON_LUNISOLAR_CALENDARS_AND_INTERCALATION_SCHEMES_IN_SOUTHEAST_ASIA)

This article is an independent mathematical reconstruction. Indigenous calendar
texts, official almanacs, and dated inscriptions must decide production behavior,
especially after historical changes and discretionary corrections.

## Astrological corpus

### MAP 19777

The Asia and Pacific Museum catalogs a public-domain paper `parabaik` dated or
signed in 1925. It uses Burmese, Pali, and Pa'O and contains formulas,
astrological diagrams, numbered constellations and years, and repeated statements
about persons born under them. It also contains Jataka material and instructions
for charms, healing, protection, and karmic consequences.

Source: [museum manuscript record](https://manuskrypty.muzeumazji.pl/en-manuscript-19777/)

This is direct evidence for birth-related rules, but not proof that the system is
`Mahabote`. Every folio must be transcribed and the calculation diagrams decoded
before naming the technique.

### SOAS illustrated manuscript study

Elizabeth Moore's 2007 article studies a late-nineteenth/early-twentieth-century
illustrated SOAS manuscript and its Burmese Buddhist, court, cosmological, and
astrological context. Only the repository abstract was accessible in this pass.

Source: [SOAS record](https://soas-repository.worktribe.com/output/387524)

The full article and manuscript shelfmark/images are required for rule work.

### Mahabote status

Current web discovery is dominated by a 1981 American manual, later commercial
summaries, and calculators. None has yet supplied an inspected Burmese source,
lineage, edition, complete precedence rules, or independently checkable worked
charts. Consequently:

```json
{
  "technique": "mahabote",
  "status": "source_limited",
  "customer_output": false,
  "reason": "No controlling Burmese-language corpus or validated lineage",
  "allowed_use_of_modern_manuals": "discovery and comparison only"
}
```

## Calendar contract

```json
{
  "calendar_pack": "burmese_makaranta|burmese_thandeikta|arakanese|named_modern",
  "effective_interval": [],
  "epoch": {},
  "source_text": "named",
  "official_adjustments": [],
  "intercalary_month_rule": {},
  "intercalary_day_rule": {},
  "year_type": "common|intercalary_month|intercalary_month_and_day",
  "month_sequence": [],
  "day_boundary": "source-defined",
  "conversion_trace": [],
  "uncertainties": []
}
```

The engine must allow a historical rule/table result to differ from a purely
formulaic projection. Discretionary or officially promulgated calendar changes
are data, not errors to smooth away.

## Manuscript rule contract

```json
{
  "work_id": "map_19777",
  "folio_side": "stable image locator",
  "language": "burmese|pali|pao",
  "script": "named",
  "technique_name_in_source": null,
  "birth_inputs": [],
  "calculation_steps": [],
  "diagram_elements": [],
  "judgment": {},
  "ritual_or_remedy": [],
  "translation_alternatives": [],
  "safety_class": "ordinary|medical|ritual|harmful",
  "status": "direct|restored|uncertain"
}
```

Do not assume a numbered constellation corresponds to a Western sign, Indian
nakshatra, or another Burmese manual until the source identification is proved.

## Required acquisition

1. Download and sequence every MAP 19777 image.
2. Obtain Burmese, Pali, and Pa'O diplomatic transcriptions.
3. Acquire Moore 2007 and the complete SOAS manuscript.
4. Locate indigenous `Makaranta`, `Thandeikta`, and calendar manuals and their
   modern critical studies.
5. Collect historical official calendars and current authoritative almanacs.
6. Identify Burmese-language `Mahabote` manuals, teachers, school variants, and
   worked charts; treat the 1981 English manual as a comparison witness only.
7. Run a separate Mon source search rather than assigning Mon material to Burma.

## Validation gates

- Calendar conversion must reproduce Irwin's historical tables, with corrigenda.
- Irwin's reform tables must never appear as observed Burmese history.
- Makaranta, Thandeikta, Arakanese, and modern packs need separate cache keys.
- All intercalary boundary years require before/at/after fixtures.
- Independent official almanacs or dated inscriptions must confirm each era.
- Every manuscript judgment must link to a folio and source-language text.
- A Burmese/Pali/Pa'O reviewer must identify the first rule set without seeing
  the proposed `Mahabote` label.
- Medical, healing, karmic-remedy, and protection material must not become
  customer instructions.
- No public `Mahabote` result until at least two independent Burmese sources and
  a qualified practitioner reproduce the same full chart procedure.

## First bounded pilots

1. **Calendar fork validator:** reproduce a period where Makaranta,
   Thandeikta, and Arakanese rules or tables differ, showing every intercalation
   decision and historical authority.
2. **MAP 19777 folio unit:** encode one complete birth-related diagram and its
   text across all languages, without naming the technique until expert review.

The first pilot validates calendar identity; the second establishes whether the
surviving manuscript can support a natal engine at all.
