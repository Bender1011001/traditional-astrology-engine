# Khmer astronomy, astrology, and divination source audit

Status: research foundation, not production approval  
Updated: 2026-07-31

## Result of this pass

Khmer research divides into three non-interchangeable layers:

1. the astronomical ephemeris recipes recorded by Faraut in 1910;
2. surviving archival manuscripts and translations on astrology/divination; and
3. contemporary Cambodian practices, including Thai-derived and individual
   hybrid methods after severe manuscript and teacher loss.

The first layer is mathematically implementable after direct source collation.
It supplies planetary positions, not a complete natal judgment system. The
second is the necessary path to historical interpretations. The third requires
living-practice partnership and must not be backdated as ancient Khmer doctrine.

## Ephemeris corpus

### Faraut 1910

*Astronomie cambodgienne* is a 283-page work recording the calculation practices
of Khmer `hora`, or astronomer-astrologers. Gallica holds a digitization, but a
direct PDF request returned HTTP 429 during this pass; only bibliographic and
reuse metadata were inspected.

Source: [Gallica record](https://gallica.bnf.fr/ark:/12148/bpt6k6549556d)

Gallica's commercial-reuse terms matter because the intended product generates
revenue. The public-domain underlying text does not automatically make Gallica's
images free for commercial reuse.

### Vernotte and Kichenassamy

The full 30-page study reconstructs Faraut's integer recipes for the Sun, Moon,
lunar ascending node, Mercury, Venus, Mars, Jupiter, and Saturn. Important
implementation findings include:

- a 638-era reference and an astronomical day the authors conclude is midnight;
- conflicting wording in Faraut that elsewhere says positions are for sunrise;
- exact integer divisions, quotients, remainders, and corrections;
- source errors and especially unreliable true-longitude data;
- a sidereal reference distinct from modern tropical ephemerides;
- strong relation to a Surya-Siddhanta canon; and
- longitude corrections more consistent with a Burmese location than Cambodia.

Source: [full paper](https://arxiv.org/pdf/1709.09620)

The conclusion is a transmission hypothesis backed by mathematical comparison.
The engine must label it as modern scholarship rather than claiming that Khmer
practitioners described their own system as "Burmese."

## Archival rule corpus

EFEO file `FR EFEO P.CAMB/Paris/160` contains 120 partially numbered folios of
Cambodian astronomy, additional astronomy/astrology papers, Sun/Moon notes, and
thirteen folios identified as a French translation of palm-leaf manuscript EF
106, a divination collection.

Source: [EFEO archive record](https://archives.efeo.fr/index.php/p-camb-paris-160)

This is the most concrete next lead for historical judgment rules. The French
translation cannot stand alone: it must be aligned to the original manuscript,
dated, and reviewed for colonial translation choices.

The Khmer Manuscript Heritage Project is a broader discovery repository. Its
catalog must be searched by Khmer/Pali technical vocabulary once specialist
terms are established.

Source: [Khmer Manuscript Heritage Project](https://khmer-manuscripts.bdrc.io/)

## Contemporary practice

Jiaviriyaboonya's full ethnographic paper documents multiple contemporary Phnom
Penh practices: birth-date numerology, old-scripture divination, royal astrology,
market divination, cards, and mediumship. It reports restricted transmission and
major losses during the Khmer Rouge period, extensive current use of named Thai
books, and no single standardized contemporary Cambodian technique.

Source: [full article](https://www.cambridge.org/core/services/aop-cambridge-core/content/view/BE787C048BF52C17B31B3F096D16598A/S0392192123000093a.pdf/influences_of_thai_divination_on_cambodian_fortunetelling_practice.pdf)

Therefore:

- a Thai-derived method used in Cambodia is a real contemporary Cambodian
  practice when documented as such;
- it is not automatically an indigenous pre-1975 Khmer method;
- a royal, rural, urban, temple, and market technique may have different
  authority structures; and
- individual hybrid practice needs practitioner-specific attribution.

## Ephemeris calculation contract

```json
{
  "pack": "faraut_1910_khmer_ephemeris",
  "source_locator": "page and recipe",
  "epoch_policy": {},
  "reference_day_time": "midnight|sunrise|variant",
  "reference_longitude": {},
  "sidereal_reference": {},
  "luminary": "sun|moon|rahu|mercury|venus|mars|jupiter|saturn",
  "integer_operations": [],
  "printed_constants": [],
  "editorial_corrections": [],
  "mean_position": {},
  "true_position": null,
  "source_error_status": "none|suspected|demonstrated",
  "modern_comparison_only": {}
}
```

All printed errors and proposed corrections remain in the trace. The engine may
offer `diplomatic_source` and `critical_reconstruction` modes; it may not silently
repair the table.

## Interpretation rule contract

```json
{
  "period": "historical|post_1979|contemporary",
  "source_or_practitioner": "named",
  "work_and_witness": "shelfmark or publication",
  "technique": "source term",
  "lineage": "khmer_inherited|thai_derived|other|hybrid|unknown",
  "inputs": [],
  "calculation_steps": [],
  "judgment": {},
  "ritual_context": [],
  "translation_layers": [],
  "consent_and_publication_scope": {},
  "status": "direct|inferred|disputed"
}
```

For the shared birth-data interface, current honest coverage is:

```json
{
  "historical_ephemeris": "research_verified",
  "historical_natal_judgment": "source_limited",
  "contemporary_birth_numerology": "requires_practitioner_specific_research",
  "generic_khmer_birth_reading": "not_implemented"
}
```

## Required acquisition

1. Acquire and hash Faraut 1910 through Gallica or a partner library.
2. Reproduce every mean-position recipe with exact integer arithmetic.
3. Request EFEO `P.CAMB/Paris/160` and original manuscript EF 106.
4. Search the Khmer Manuscript Heritage Project using terms supplied by a Khmer
   manuscript specialist.
5. Identify pre-1975 printed astrology/divination books in the National Library
   of Cambodia and private/temple collections.
6. Partner with Khmer scholars and living practitioners; record whether a method
   is inherited, Thai-derived, reconstructed, or individual.
7. Obtain commercial image/text permissions and honor interview consent.

## Validation gates

- Every Faraut integer recipe must reproduce the modern paper's mean-position
  tables before use.
- Midnight and sunrise readings must be separate convention candidates until the
  primary text and specialist review resolve them.
- Printed errors and corrections must produce distinct trace states.
- Modern Swiss Ephemeris positions are comparison data, not Khmer outputs.
- Every judgment must cite a manuscript/practitioner source beyond Faraut's
  astronomy.
- Thai-derived rules must retain Thai source identity and Cambodian adoption
  context.
- A Khmer specialist must validate terminology and the first source pack.
- A living-practice module requires documented consent and must not expose
  restricted teachings.
- Medical, political, harmful, ritual, or coercive predictions must be excluded
  from advice even when historically documented.

## First bounded pilots

1. **Faraut mean-longitude validator:** implement Sun, Moon, Rahu, Mars, Jupiter,
   and Saturn for one published example date, preserving every quotient,
   remainder, correction, and the midnight/sunrise fork.
2. **EF 106 archival concordance:** align one complete divination unit across
   the palm-leaf original, French translation, modern Khmer transcription, and
   English translation before encoding any judgment.

The calculation pilot can proceed first. The natal product remains
`source_limited` until the archival pilot proves an applicable birth technique.
