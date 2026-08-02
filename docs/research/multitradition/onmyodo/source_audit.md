# Historical Japanese Onmyodo source audit

Status: research foundation, not production approval  
Updated: 2026-07-31

## Result of this pass

Onmyodo is not a Japanese cosmetic layer over BaZi, and it is not a single secret
book of Abe no Seimei. The inspected scholarship requires era-specific domains:

- ancient and Heian court bureau calendar, astronomy, timekeeping, and divination;
- court `shikiban` divination represented by *Senjiryakketsu*;
- medieval manuscript lineages and ritual adaptations;
- late-medieval/early-modern calendar divination represented by variable
  *Hoki Naiden Kinugyokutoshu* materials;
- early-modern popular almanacs such as `Ozassho`;
- Tsuchimikado institutional developments; and
- later folklore, religious groups, literature, manga, film, and revival practice.

These layers may be compared but not merged. Most are event, calendar, direction,
omen, or question techniques. The inspected evidence does not yet justify a
general birth-chart engine. If a technique requires the time of a question or
action, birth time is not a valid substitute.

## Institutional and historical frame

The National Diet Library's calendar history describes the `Onmyoryo` as the
government bureau responsible for calendrical work, astronomy, divination, and
timekeeping. It also describes the later Kamo association with calendars and Abe
association with astronomy. This supports separate calculation and practice
modules, not one undifferentiated supernatural system.

Source: [National Diet Library calendar history](https://www.ndl.go.jp/koyomi/e/history/index.html)

Hayashi and Hayek's historiographic review goes further: `Onmyodo` needs
era-specific definitions such as court, medieval, and popular Onmyodo. It was
constructed in Japan from East Asian sources and institutions, but should not be
called a generic Japanese equivalent of Daoism. Its technical, religious, social,
and institutional meanings changed.

Source: [Japanese Journal of Religious Studies review](https://religion-in-japan.univie.ac.at/k/img_auth.php/d/d3/Hayashi_Hayek_2013b.pdf)

## Technical corpora

### Senjiryakketsu

Shinji Kosaka's 2004, 469-page study is the first controlling acquisition for
court `shikiban` divination. CiNii states that its base witnesses are held by
Kyoto University Library and the Maeda Ikutokukai Sonkeikaku Bunko and that it
includes a transcription on pages 183-264. The historiographic review calls it a
detailed study of the functioning of the divination-board technique.

This is evidence for a divination engine whose exact query, board setup, calendar
state, heavenly generals, judgments, and precedence must be reconstructed from
the text. It is not evidence for popular stories about physical `shikigami`, nor
is it automatically a natal method.

Sources: [NDL record](https://ndlsearch.ndl.go.jp/books/R100000002-I000007567550), [CiNii details](https://cir.nii.ac.jp/crid/1971993809699274140?lang=en)

### Hoki Naiden Kinugyokutoshu

The National Museum of Japanese History describes a 1584 manuscript as a
five-volume medieval compilation attributed to Abe no Seimei. The attribution is
part of the source's transmission claim and must not be restated as certain
authorship.

The museum's digitized variant is important precisely because comparison is
possible. Koike's 2024 manuscript study reports that five dated medieval
manuscripts vary substantially, that older witnesses are diverse, and that at
least three lines of knowledge may be present. The medieval `Hoki` was not a
fixed text.

Sources: [museum exhibition](https://www.rekihaku.ac.jp/event/2023_exhibitions_kikaku_on.html), [digitized variant record](https://khirin.rekihaku.ac.jp/en/pid/nmjh_collection/F-321-79.html), [manuscript-study abstract](https://www.rekihaku.ac.jp/assets/upload/book_kenkyu_202403_houkoku_247_pdf_en_247004.pdf)

Consequently every rule needs manuscript, copying date, lineage hypothesis,
section, and later-edition relationships. A rule in a common Edo print cannot be
retrojected into Heian court practice.

### Ozassho and early-modern calendar divination

The museum identifies its 1631 `Ozassho` as the earliest surviving example and
describes the genre as a plain-language compilation of calendar and divination
knowledge that repeatedly expanded into a practical encyclopedia.

Mariko Baba's study finds multiple competing logics of calendar divination in
late-medieval and early-modern military manuals and argues that `Hoki Naiden` was
only one. Its simplification of difficult correlative theory helped it spread.

Source: [Baba, “The Formation of Early Modern Calendar Divination”](https://www.jstage.jst.go.jp/article/rsjars/97/3/97_27/_article/-char/ja)

Therefore `Ozassho`, military calendar divination, and `Hoki` require distinct
packs even when later books borrow from one another.

## Calendar and astronomical kernel

Every historical calculation must name the calendar regime actually used for
the chosen period. A Gregorian timestamp cannot be directly fed into a table of
lunar months, sexagenary days, directions, and calendrical annotations.

```json
{
  "regime_id": "named Japanese calendar system and revision",
  "effective_interval": ["start", "end"],
  "authority": "primary calendar and technical study",
  "input_civil_date": "ISO date plus historical calendar policy",
  "locality": "historically relevant place",
  "lunisolar_date": {
    "era_name": "nengo",
    "era_year": 1,
    "month": 1,
    "leap_month": false,
    "day": 1
  },
  "sexagenary_designations": {},
  "solar_terms_or_mansions": [],
  "day_boundary": "source-specific",
  "uncertainty": [],
  "source_locators": []
}
```

Calendar production history, received Chinese algorithms, later Japanese
revisions, and printed calendrical annotations are separate data layers. Modern
Japanese almanac values cannot silently backfill a Heian calculation.

## Technique contracts

### Shikiban divination

Likely inputs include an event or question time and the contemporaneous calendar
state. The definitive input contract awaits full extraction from Kosaka's edition.

```json
{
  "technique": "senjiryakketsu_shikiban",
  "witness_id": "named manuscript",
  "query_context": "source-defined category",
  "divination_datetime": "not birth time unless the source says so",
  "calendar_state": {},
  "board_construction_steps": [],
  "derived_positions": [],
  "matched_judgments": [],
  "precedence_and_exceptions": [],
  "source_locators": []
}
```

No folklore description of Seimei's spirit servants may be converted into a
computational rule. The text's board entities, ritual representations, and later
legendary beings require separate labels.

### Directional and calendrical selection

Directional deities and taboos can change by year, lunar month, season, day, or
other source-defined state. Each result therefore requires:

- action or travel context;
- origin and intended direction;
- selected date/time;
- historical calendar regime;
- named source and period;
- active deity/taboo/qualification rules; and
- any authorized avoidance, waiting, or route-changing procedure.

Do not turn a historical travel taboo into safety advice or claim that violating
it causes harm.

### Birth input

For the user's one-form product, the Onmyodo module must initially return a
transparent coverage result:

```json
{
  "status": "source_limited",
  "birth_calendrics_available": true,
  "birth_judgment_available": false,
  "reason": "No inspected controlling corpus yet authorizes a general natal reading",
  "adjacent_techniques": ["historical calendar reconstruction", "event divination", "date/direction selection"]
}
```

If later research finds a birth-specific procedure, it becomes its own named,
dated source pack. It must not be synthesized from Japanese calendrical labels,
Chinese BaZi meanings, and modern popular Onmyodo.

## Rule provenance model

```json
{
  "period": "Heian court|medieval|early modern|modern",
  "institution_or_community": "named",
  "work": "title",
  "witness": "library or museum shelfmark",
  "copy_or_print_date": "known or estimated",
  "section_locator": "folio/page/line",
  "attributed_author": "source claim",
  "authorship_status": "accepted|attributed|pseudonymous|uncertain",
  "source_language_text": "licensed internal transcription",
  "rule_type": "calendar|astronomy|omen|shikiban|direction|rite",
  "inputs": [],
  "conditions": [],
  "derivations": [],
  "judgment": null,
  "variants": [],
  "modern_editor_notes": [],
  "status": "direct|restored|inferred|disputed"
}
```

## Acquisition and review workflow

1. Acquire Kosaka 2004 and Matsuoka's 2007 detailed commentary on
   *Senjiryakketsu*.
2. Obtain images of both base witnesses and collate them against the printed
   transcription.
3. Download the museum `Hoki` variant under its stated license and obtain the
   museum's 1584 witness plus the five manuscripts in Koike's study.
4. Obtain the 1631 `Ozassho` images and later dated editions.
5. Build a calendar-regime bibliography from Watanabe, Momo, and primary issued
   calendars identified in the NDL and museum sources.
6. Align kanbun/classical Japanese, modern Japanese explanation, and English
   translation without translating technical names into generic Western terms.
7. Obtain review from specialists in historical Japanese calendrics, kanbun,
   Onmyodo textual history, and the specific divination technique.

## Validation gates

- A known historical Japanese date must reconstruct identically from an
  independently implemented calendar reference for the selected regime.
- Leap months, era transitions, day boundaries, and sexagenary designations need
  adversarial boundary cases.
- Every board placement must be traceable to an explicit construction step.
- A second encoder must reproduce the pilot without seeing engine output.
- Manuscript variants must produce separate results or explicit conflicts.
- A `Hoki` print rule must not appear in a Heian `Senjiryakketsu` pack.
- Birth time must not satisfy a required question/event-time field.
- Changing date, hour, direction, manuscript, or period must change the trace
  where the source distinguishes it.
- A Japanese specialist must approve terminology and source attribution before
  public prose is written.

## Cultural and safety policy

- Use `Onmyodo`, `Onmyoryo`, and `onmyoji` with period-aware definitions.
- Do not present fiction, manga, film, shrine tourism, or modern occult manuals
  as evidence for Heian practice.
- Do not call all imported East Asian material "Daoism," and do not erase the
  Japanese institutions and historical transformations.
- Keep ritual, exorcistic, medical, death, warfare, and harmful prescriptions in
  historical context; do not issue them as instructions.
- Do not claim supernatural certainty or inevitable harm from a taboo direction.
- Living ritual groups and lineages require consent-based fieldwork and must not
  be reconstructed from old manuscripts alone.

## First bounded pilots

Run two pilots without pretending either is a natal chart:

1. **Historical calendar reconstruction:** reproduce one securely dated Heian
   document date under the correct calendar regime, including lunar date,
   sexagenary designations, and every uncertainty.
2. **One Senjiryakketsu board case:** after acquiring Kosaka's edition, encode one
   complete shikiban example from input through board construction and judgment,
   preserving both base-witness variants.

Only after both pass independent reproduction should the research expand to a
directional calendar pack or `Hoki`/`Ozassho`. The birth-data interface must show
`source_limited` until a birth-specific textual procedure passes the same gates.
