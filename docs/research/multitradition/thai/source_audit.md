# Thai, Lanna, and Lue astrology source audit

Status: research foundation, not production approval  
Updated: 2026-07-31

## Result of this pass

There is enough evidence to define a serious Thai research program, but not a
single generic "Thai astrology" engine. At minimum the product must separate:

- Central Thai `Suriyayatra` astronomical/calendar calculation;
- Lanna `Suriyayatra` and calendar conventions;
- Lue `Suriyayatra` and calendar conventions;
- Central Thai natal judgment texts, including *Chakratipani*;
- 27-mansion, mundane/state, and dream material in *Tamradao*;
- named Thai techniques in current professional practice; and
- later universal, Uranian, Western, Indian, Chinese, or commercial systems
  currently taught or practiced in Thailand.

Common Sanskrit-derived terms and a shared textual ancestor do not make regional
formulas or judgments interchangeable.

## Calculation corpus

### Suriyayatra comparative thesis

Yuttaporn Naksuk's 2005 Thai-epigraphy thesis compares Central Thai, Lanna, and
Lue manuscript versions. The repository supplies a 344-page image PDF, which was
downloaded and hashed in this pass:

`bb6ce48627638d37b1c9018e06d07c58344349a2e5e6f78a5551de8baa5d1514`

The abstract inventories 97 formulas: 28 Central Thai, 42 Lanna, and 27 Lue. It
states that the major formulas share an ancient Indian, especially
Surya-Siddhanta-related, basis, while some formulas were devised locally for ease
of computation and compatibility with regional calendars.

Source: [Silpakorn University record and PDF](https://sure.su.ac.th/xmlui/handle/123456789/2009?locale-attribute=en)

This directly forbids a shared-constants implementation. Each manuscript and
regional version needs a complete formula manifest before comparison.

### Independent intercalation study

Gislen supplies equations and worked examples for Thai solar-day, tithi,
intercalary-month, and intercalary-day calculations. He also demonstrates that
Thai and Burmese calendars, though superficially similar, use fundamentally
different synchronization logic.

Source: [full article](https://www.researchgate.net/publication/326293290_ON_LUNISOLAR_CALENDARS_AND_INTERCALATION_SCHEMES_IN_SOUTHEAST_ASIA)

The article is a validator and secondary reconstruction. Naksuk's manuscript
witnesses and issued historical calendars must control the production formulas.

### Historical inscription fixtures

The Thai Ministry of Culture page identifies inscriptions containing historical
chart and `Suriyayatra` quantities, including era, month, avoman, elapsed days,
stellar mansion, and related values. It reports a Julian reconstruction for the
Chiang Mai foundation inscription.

Source: [Ministry of Culture](https://www.culture.go.th/culture_th/ewt_news.php?filename=i&nid=4352)

Every named inscription must be traced to image and critical edition before use,
but these are ideal blind validation fixtures because they preserve computed
historical states rather than modern calculator output.

## Judgment corpora

### Chakratipani

Chanin Phongsawad's full article describes *Chakratipani* as a birth-day and
birth-sign work whose Pali text is attributed to Udom Ramathera and whose Thai
translation/verse redaction is associated with Prince-Patriarch
Paramanuchitchinorot in the early Rattanakosin period. The article uses a 2013
edition.

The work includes:

- eight planetary deities: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, and
  Rahu;
- twelve signs;
- seven weekdays;
- planet/ascendant and other placement conditions;
- rising-sign narratives; and
- age-specific narrative sequences tied to literature, Jataka, and Buddhist
  biography.

Source: [full article](https://so06.tci-thaijo.org/index.php/JoMbuHu/article/download/265309/180448/1077631)

The article is not a complete rule edition. It quotes examples that include
medical, disability, fertility, death, enslavement, and deterministic claims.
Those may be retained in restricted source evidence but must not become health
advice or demeaning customer judgments.

### Tamradao

Nipatporn Pengkaew's 1995 Thai-epigraphy thesis transcribes and analyzes an
early-Rattanakosin text written across Thai, Khmer, and Chrieng scripts. Its
abstract describes 27 stellar groups, ruler/state prognostication, political and
economic imagery, and dream divination.

Source: [Silpakorn University record](https://sure.su.ac.th/xmlui/handle/123456789/1787)

This belongs in mansion, mundane, and dream modules unless individual passages
prove a natal use. It must not be absorbed into *Chakratipani*.

### Living professional taxonomy

The current Horathai foundation curricula distinguish astronomical foundations,
zodiac and ascendant construction, natal and transit charts, `Thaksa`, `Tri-Wai`,
planetary age-period techniques, `Suriyayatra`, `Manat`, and military/electional
charting. This is a useful practice inventory and reviewer lead, not an authority
for ancient wording.

Source: [Horathai foundation](https://www.horathai.com/)

## Calculation contract

```json
{
  "calculation_pack": "suriyayatra",
  "region": "central_thai|lanna|lue",
  "manuscript_id": "shelfmark",
  "edition_id": "transcription/edition",
  "era_and_epoch": {},
  "historical_calendar_regime": {},
  "day_boundary": "source-defined",
  "integer_units": {},
  "formula_sequence": [
    {
      "step": 1,
      "operation": "exact integer operation",
      "constants": [],
      "remainder_policy": "explicit",
      "source_locator": "folio/line"
    }
  ],
  "regional_only_steps": [],
  "outputs": {},
  "uncertainties": []
}
```

Traditional integer recipes must be implemented as written before a modern
floating-point simplification is considered. Remainder, truncation, indexing,
epoch, longitude, and day-start rules are semantic, not implementation details.

The Swiss Ephemeris may supply an independent astronomical comparison. It may
not replace a `Suriyayatra` result while retaining the traditional label.

## Judgment rule contract

```json
{
  "work": "chakratipani",
  "textual_layer": "pali|thai_translation|thai_verse|modern_editor",
  "source_locator": "page/verse/line",
  "calculation_pack_required": "named",
  "conditions": [],
  "judgment": {},
  "life_phase_or_age": null,
  "mythic_or_literary_analogy": [],
  "exceptions": [],
  "translation_notes": [],
  "safety_class": "ordinary|medical|disability|fertility|death|demeaning",
  "publication_action": "publish|historical_context_only|suppress"
}
```

Mythic and literary analogies are part of the rule's rhetoric and cultural logic;
they are not replaceable by generic sign keywords. Conversely, an analogy cannot
authorize invented events not stated by the source.

## Required acquisition

1. OCR and manually transcribe Naksuk's full image PDF.
2. Identify and obtain every Central Thai, Lanna, and Lue base manuscript.
3. Acquire the 2013 *Chakratipani* edition and trace its Pali witnesses.
4. Acquire Pengkaew's complete *Tamradao* thesis and source witness.
5. Retry the National Library of Thailand `Horawitthaya` scans; current direct
   opens time out and search metadata is not sufficient.
6. Trace the historical inscriptions named by the Ministry page to critical
   editions and high-resolution images.
7. Engage Thai, Lanna, and Lue language specialists and practitioners separately.

## Validation gates

- Every one of Naksuk's 97 formulas must be inventoried by region and witness.
- Shared and unique formulas must have separate test IDs.
- Exact-integer outputs must reproduce at least three examples per regional pack.
- Historical inscriptions and issued almanacs must be blind fixtures.
- Leap-day/month and year-boundary mutations must change the correct quantities.
- A regional pack may not fall back to another region's constant.
- Every natal judgment must cite the exact *Chakratipani* layer and condition.
- A complete 12-rising-sign concordance must preserve text variants and analogies.
- Medical, disability, fertility, death, and demeaning claims must fail the public
  publication contract even when source-authentic.
- Qualified Thai and regional reviewers must reproduce the first pilot without
  seeing engine output.

## First bounded pilots

1. **Three-version Suriyayatra concordance:** choose one solar and one lunar
   calculation present in Central Thai, Lanna, and Lue witnesses; implement each
   exact recipe and expose every differing constant and remainder step.
2. **Chakratipani rising-sign concordance:** align the twelve rising-sign passages
   across Pali, Thai prose, Thai verse, and the 2013 edition; calculate only after
   the required Thai ascendant convention is sourced.

Neither pilot should be published as a complete Thai reading. They are the gates
for calculation integrity and textual integrity respectively.
