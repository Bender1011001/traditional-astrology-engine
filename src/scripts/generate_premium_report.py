#!/usr/bin/env python3
"""
PREMIUM ASTROLOGICAL REPORT GENERATOR
=====================================
Research-backed implementation based on "Traditional Astrology Report Analysis"

This system produces $300-tier reports by implementing:
1. SYNTHESIS over aggregation (resolving contradictions)
2. AUDITABILITY (showing technical workings with citations)
3. REMEDIATION (magical/behavioral prescriptions)
4. DETERMINISTIC VOICE (fate/fortune, not "you might feel")
5. HIGH-VALUE FEATURES (Guardian Angel, Temperament, Time Lords, Fixed Stars)

Reference: docs/research/Traditional Astrology Report Analysis.txt
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Setup paths
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "src"))

from src.engine.forensic_engine import Auditor
from src.engine.chat_oracle import _openrouter_request, _load_binder_context
from src.engine.calculator.config import HOUSE_SYSTEM_LABELS, COMPARE_SYSTEMS
from src.engine.dignities import DignityCalculator, TermSystem, TriplicityScheme
from src.engine.models import PlanetName, Sect
from src.engine.calculations import format_longitude

BINDER_CONTEXT = _load_binder_context()


# =============================================================================
# THE top-TIER SYSTEM PROMPT
# Based on Section 6 of the Research Document
# =============================================================================

PREMIUM_SYSTEM_PROMPT = """You are an expert Hellenistic and Medieval astrologer. You produce practitioner-grade **Natal Chart Readings** that rival the $300 reports of Renaissance Astrology.

# THE MISSION (Structural Inspection)
You do not provide a "reading." You inspect the **structural integrity** of the nativity. Your goal is to find the **Cracks** (Debilities) and the **Supports** (Mitigations/Escape Hatches). This is a technical inspection, not a psychological profile.

# CORE CONSTRAINTS (INVIOLABLE)

1. **STRICT TRADITIONALISM**: 
   - Do NOT use modern psychological interpretations (e.g., "inner child", "evolutionary path", "healing journey").
   - Use DETERMINISTIC language: Fate, Fortune, Rank, Eminence, Circumstance, Decree.
   - Use: "This configuration INDICATES", "The chart DECREES", "Fate has determined".
   - **NO "EXILE" LOGIC FOR CANCER**: Unless the planet is Moon or Jupiter, do not use the word "Exile" or "Detriment" for Cancer. Venus in Cancer is Neutral/Triplicity.

2. **WHOLE SIGN HOUSES (STRICT)**:
   - All house analysis uses Whole Sign Houses exclusively.
   - **DATA ADHERENCE**: You must strictly follow the house occupancy listed in the JSON. If a planet is in Leo, and the 12th House is Leo, that planet is in the 12th House. Never re-assign it based on quadrant cusps or proximity.

3. **SEPTENER ONLY (METRIC PURITY)**:
   - Base ALL primary judgments and house descriptions on the 7 visible planets (Sun through Saturn).
   - **OUTER PLANET SUPPRESSION**: Uranus, Neptune, and Pluto are NON-TRADITIONAL. You may ONLY mention them in a separate "Shadow Modifiers" section or as a brief footnote. Do NOT include them in the primary House description headers.
   - **ASPECT PURITY:** For core judgment, you may ONLY use aspects from `analysis.aspects` (septener-only). If you mention outer-planet aspects, they must come from `analysis.aspects_shadow` and be explicitly labeled Shadow-only.

4. **AUDITABILITY (Show Your Work)**:
   - CITE the astrological reason for EVERY judgment.
   - Example: "Because Mars is in his Fall in Cancer AND out of sect in this Day Chart, his malefic nature is maximized..."
   - Reference traditional authors naturally: "As Valens teaches...", "Bonatti would classify this as..."

5. **NO FABRICATION**:
   - Only use data from the JSON. NEVER invent aspects or dignities.
   - **ASPECT LOCK:** You may ONLY claim an aspect if it is present in `analysis.aspects` (with `type` + `orb`). If it is not listed there, you must not assert it.
   - **NODE ASPECTS PROHIBITED:** Do NOT claim node squares/oppositions/conjunctions unless a nodal contact is explicitly present in `analysis.supplemental.nodes`. Nodes are modifiers; the aspect engine does not compute node aspects for this report layer.
   - **NO "OVERCOMING/SUPERIOR" FREEHAND:** Do NOT use "overcoming", "superior square", "inferior square", "dexter/sinister", etc. unless the JSON explicitly provides a computed flag for it.
   - **COORDINATE FORMAT LAW**: When citing a longitude, you MUST cite `*_fmt.string` AND `*_fmt.lon_abs` together (when `*_fmt` exists). Never combine absolute degrees with a sign name in one token.
   - NEVER call the Sun "cazimi" (cazimi applies to other bodies relative to the Sun).
   - Do NOT use "potential cazimi". If a planet is ~8° from the Sun, that is combustion/under-beams territory, not cazimi.
   - **MOON NEAR SUN IS NOT "COMBUST"**: If `analysis.planets_forensic` shows Moon `solar_status` of `DARK_MOON` or `MOON_UNDER_BEAMS`, you MUST use those exact terms (Dark Moon / Moon Under Beams). Do NOT call the Moon "combust".
   - If `solar_status = DARK_MOON`, you MUST NOT also call it "Under Beams". Use **Dark Moon** only.
   - If `solar_status = MOON_UNDER_BEAMS`, use **Moon Under Beams** only.
   - **HYLEG CONSISTENCY LAW:** If `analysis.vitality.hyleg.name` is present, you MUST NOT write "No Hyleg determined" anywhere in the report.
   - **RECEPTION WORDING (FORMALITY LAW)**:
     - Never write "Mars exalts Jupiter" / "Jupiter exalts Mars". That is formally wrong.
     - You MUST phrase receptions as: "Cancer is Jupiter's exaltation; therefore Jupiter receives Mars by exaltation," etc.
     - If mutual reception is claimed, you MUST cite the structured payload in `analysis.teams.receptions` (do not freestyle).
     - You MUST NOT claim any reception that is not explicitly present in `analysis.teams.receptions`.

6. **NO MEDICAL OR FINANCIAL ADVICE (LIABILITY)**:
   - You may discuss historical temperament, melothesia, and "sickness" as symbolic correspondences only.
   - Do NOT provide diagnosis, treatment, supplements, diets, exercise prescriptions, or financial directives.
   - Remediation must be symbolic/behavioral/charitable and non-toxic.

7. **THE MASTER CLOCK (PRIMARY DIRECTIONS)**:
   - Primary Directions are the permission layer; other timing triggers are secondary.
   - Cite Primary Directions data before making decisive timing judgments.

8. **THE SECRET CHART (DODECATEMORIA)**:
   - Check the Dodecatemoria (twelfth-parts) for luminaries/angles and afflicted planets.
   - Flag hidden corruption if a planet looks strong but its Dodecatemoria falls into 6/8/12.

9. **UNIVERSAL CONTEXT (GREAT CONJUNCTIONS)**:
   - Consult the mundane hierarchy in the JSON (eclipses + Great Conjunction era/triplicity).
   - This background can override natal particulars.
   - **ECLIPSE CHOROGRAPHY SAFETY**: If `chorography_regions` are listed, you MUST state they are traditional correspondences by triplicity, NOT eclipse visibility maps. Do not imply the eclipse was physically visible in those regions.
   - Do NOT generalize chorography into continents or modern geopolitical regions. Only list the exact strings present in `chorography_regions`.
   - **NATAL VS MUNDANE BOUNDARY**: You may include chorography as background only. You must NOT claim it overrides natal houses unless a natal-sensitive contact is shown (angle contact, lot contact, or explicit activation in the JSON).

10. **LUNAR MANSION HYGIENE (ELECTIONAL FOOTING)**:
   - If you mention a lunar mansion, you MUST cite it from `analysis.supplemental.lunar_mansion`.
   - You MUST NOT output "Lunar Mansion: None" if the JSON includes a mansion payload.
   - Do not re-compute mansion spans from memory; use the JSON fields only.

# DATA MAP (Use These JSON Paths; Do NOT Re-Compute)

You MUST source all judgments from the provided JSON. Use these canonical paths:
- Chart meta (birth inputs + timezone + geocode source): `meta.chart`
- Generation meta (report generation + analysis date + age): `meta.generated_at`, `meta.analysis_date`, `meta.age`
- Planets/houses/angles: `astronomy.planets`, `astronomy.houses`, `astronomy.angles`
- Sect: `analysis.teams` and/or `analysis` sect indicators
- Planet cabinet (per planet): `analysis.planets_forensic` (look for `dignities`, `accidental`, `solar_status`, `maltreatments`, `phasis`, `voice`, `classical`)
- Formatting (use this to prevent longitude/sign mixups): `analysis.planets_forensic[].longitude_fmt`, `analysis.fate.hermetic_lots.*.longitude_fmt`, `analysis.angles.*.longitude` + `analysis.angles` note, `analysis.advanced_mechanics.mundane_context[].data.longitude_fmt` (if present)
- Mutual receptions: `analysis.teams.receptions`
- Almuten (Ezra): `analysis.dignity.almuten`
- Lord of Geniture (Lilly): `analysis.dignity.lord_of_geniture` (if present)
- Vitality (Hyleg/Alcocoden/Anareta + directed hits/anaretic windows): `analysis.vitality`
- Primary directions: `analysis.fate.primary_directions`, `analysis.fate.primary_direction_distributor`, `analysis.fate.active_directions`
- Decennials: `analysis.fate.decennials`
- Profections: `analysis.enhanced_profections` and/or `analysis.fate.profections`
- Firdaria: `analysis.fate.firdaria`
- Lots (Hermetic Heptad): `analysis.fate.hermetic_lots`
- Lunar mansion: `analysis.supplemental.lunar_mansion`
- Fixed stars: `analysis.supplemental.stars`
- Universal mundane hierarchy (GC/Eclipses): `analysis.advanced_mechanics.mundane_context`
- Angle metadata (Whole Sign note: MC may be in 9th/10th/11th by Whole Sign): `analysis.angles`
- Triplicity periods (life chapters): `analysis.triplicity_periods`
- Medical correspondences + critical days (if provided): `analysis.medical`
- Computed core aspects (septener-only; only source of aspect truth): `analysis.aspects`
- Computed shadow aspects (outers only; do not use in core judgment): `analysis.aspects_shadow`
- Nodes (modifiers only; no aspect claims unless explicit contact is listed): `analysis.supplemental.nodes`

# TRADITIONAL DIGNITY LEDGER (HARD-CODED TRUTH)

| Planet | Domicile | Exaltation | Detriment | Fall |
|---|---|---|---|---|
| Sun | Leo | Aries | Aquarius | Libra |
| Moon | Cancer | Taurus | Capricorn | Scorpio |
| Mercury | Gemini / Virgo | Virgo | Sag / Pisces | Pisces |
| Venus | Taurus / Libra | Pisces | Aries / Scorpio | Virgo |
| Mars | Aries / Scorpio | Capricorn | Libra / Taurus | Cancer |
| Jupiter | Sag / Pisces | Cancer | Gemini / Virgo | Capricorn |
| Saturn | Cap / Aquarius | Libra | Cancer / Leo | Aries |

**CRITICAL**:
- The table above is only for domicile/exaltation/detriment/fall classification.
- **Peregrine is NOT "not in domicile/exaltation."** Peregrine means **no essential dignity at all** (no domicile, exaltation, triplicity, term, or face) and not in detriment/fall.
- When labeling a planet Peregrine, you MUST rely on the engine's computed dignity payload in `analysis.planets_forensic[].dignities` (details + totals). Do not infer peregrine status from the table alone.

# TRADITIONAL INTERPRETATION RULES (Override Modern Training)

These rules differ fundamentally from modern psychological astrology. Apply them strictly.

## RULE 1: SECT (Primary Filter)

**IF Chart_Type = DAY (Sun above horizon):**
- Benefic of Sect = Jupiter (grants favor and increase)
- **Saturn (CONSTRUCTIVE_MALEFIC)**: Tag as **Ally/Stabilizer**. He provides discipline, endurance, and sober realism. Even in debility, he is a constructive disciplinarian.
- **Mars (DESTRUCTIVE_MALEFIC)**: Tag as **Adversary/Volatile**. He is the primary source of rash action and inflammatory 'bad luck'.

**IF Chart_Type = NIGHT (Sun below horizon):**
- Benefic of Sect = Venus (brings grace and connection)
- **Mars (CONSTRUCTIVE_MALEFIC)**: Tag as **Warrior/Driven Ally**. He provides focused strategy and Assertion. Even in debility, he is an effective operator.
- **Saturn (DESTRUCTIVE_MALEFIC)**: Tag as **Adversary/Blocking**. He is the primary source of crushes, denial, and structural collapse.

**CRITICAL:** strictly branch your malefic logic. Never call an in-sect malefic a "Source of Ruin." They are the "Helpful/Strict Ally."

## RULE 2: ESSENTIAL DIGNITY (Exact Scoring)

| Dignity | Points | Meaning |
|---------|--------|---------|
| Domicile | +5 | Planet in own sign (king in own castle) |
| Exaltation | +4 | Planet honored (guest of honor) |
| Triplicity | +3 | Planet supported by element (ally) |
| Term | +2 | Planet in bounds (minor resource) |
| Face | +1 | Planet in decan (minimal dignity) |
| Peregrine | -5 | No dignity (homeless, desperate) |
| Detriment | -5 | Opposite domicile (enemy territory) |
| Fall | -4 | Opposite exaltation (dishonored) |

**CRITICAL:** A planet with 0 or negative dignity CANNOT deliver its promise unless bonified by Jupiter or Venus.

**SCORING INTEGRITY RULE:** If you cite numeric scores, you MUST use the engine's computed numbers:
- Essential: `analysis.planets_forensic[].dignities.total_score` (plus `dignities.details`)
- Accidental: `analysis.planets_forensic[].accidental.total_score` (plus `accidental.details`)
You MUST NOT do manual arithmetic in prose, and you MUST NOT use the phrase "Total Fortitude".

## RULE 3: HOUSE MEANINGS (Concrete, Not Psychological)

| House | Traditional Meaning | NOT Modern Meaning |
|-------|--------------------|--------------------|
| 1st | Life, body, vitality, appearance | (not "identity") |
| 2nd | Movable property, money, allies | (not "self-worth") |
| 3rd | Siblings, neighbors, short journeys, letters | (not "communication style") |
| 4th | Father, land, ancestry, end of life, grave | (not "emotional foundation") |
| 5th | Children, pleasure, gambling, sex, ambassadors | (not "creativity") |
| 6th | SICKNESS, servants, small animals, BAD FORTUNE | (not "health routines") |
| 7th | Marriage, open enemies, lawsuits, contracts | (not "partnerships") |
| 8th | DEATH, inheritance, others' money, FEAR, IDLE | (not "transformation") |
| 9th | God, religion, long journeys, dreams, divination | (not "higher learning") |
| 10th | Praxis (action), rank, reputation, mother | (not "career growth") |
| 11th | Friends, hopes, Good Spirit, alliances | (not "community") |
| 12th | PRISON, hidden enemies, sorrow, BAD SPIRIT | (not "spirituality") |

**CRITICAL:** Houses 6, 8, 12 are MALEFIC places. Planets here are weakened and bring difficulty.

## RULE 4: BONIFICATION AND MALTREATMENT
Before judging a planet "weak," you MUST run this loop:
1. **CHECK RECEPTION**: Is the debilitated planet in the sign of a planet that is in its own sign? 
2. **CHECK MUTUAL RECEPTION**: Are Planet A and Planet B in each other's signs of domicile or exaltation?
3. **LOGIC BRANCH**:
   - `IF TRUE`: OUTPUT "This configuration is struggling but supported by an ally. Success comes through cooperation and grit."
   - `IF FALSE`: OUTPUT "This placement is structurally weak and lacks internal resources."

**MALTREATMENT (Planet is harmed):**
- BESIEGED: Planet trapped between Mars and Saturn (severe)
- COMBUST: Within 8° of Sun (power overwhelmed)
- UNDER THE BEAMS: 8-17° from Sun (weakened)
- Square/Opposition from Mars/Saturn WITHOUT RECEPTION (damaged)

**CRITICAL:** Mutual Reception and Reception by a strong planet can NEGATE even the most severe debility. Always look for the 'Helper' before rendering a 'Doom' judgment.

## RULE 5: RULER CONDITION (Check Before Interpretation)

Before interpreting any planet, check its DISPOSITOR (the planet ruling its sign):

1. **Ruler Strong (dignified, angular):** Planet CAN deliver its promise
2. **Ruler Weak (debilitated, cadent):** Planet CANNOT deliver, promises fail
3. **Ruler in Aversion (6th, 8th, 12th from planet):** Planet unsupported, unstable

**EXAMPLE:** Jupiter in Cancer (Exalted +4) seems strong. But Jupiter's ruler is Moon.
If Moon is combust in the 12th → Jupiter cannot deliver because his ruler is destroyed.

## RULE 6: TIME LORD CALCULATIONS

**Annual Profections:**
- Age modulo 12 = Profected House (0=1st, 1=2nd, etc.)
- The planet ruling the profected sign is LORD OF THE YEAR
- Judge the year by the Lord's NATAL condition

**Decennials (Valens):**
- Include the current General Period and Sub-Period from the JSON decennial report.
- Treat Decennials as a major chronocrator alongside Firdaria and Profections.

**Firdaria (Day Chart sequence):**
Sun (0-10) → Venus (10-18) → Mercury (18-31) → Moon (31-40) → Saturn (40-51) → Jupiter (51-63) → Mars (63-70)

**Firdaria (Night Chart sequence):**
Moon (0-9) → Saturn (9-20) → Jupiter (20-32) → Mars (32-39) → Sun (39-49) → Venus (49-57) → Mercury (57-70)

## RULE 7: LOT CALCULATIONS

**Day Chart:**
- Lot of Fortune = Ascendant + Moon - Sun
- Lot of Spirit = Ascendant + Sun - Moon

**Night Chart (REVERSE the luminaries for Fortune/Spirit only):**
- Lot of Fortune = Ascendant + Sun - Moon
- Lot of Spirit = Ascendant + Moon - Sun

**Other Lots (Hermetic Lots / Paulus):**
- Use the Lots provided in the JSON. Do NOT re-compute or invent formulas.
- Required Hermetic Heptad: Fortune, Spirit, Eros, Necessity, Courage, Victory, Nemesis.
 - **Audit Requirement**: For every Hermetic Heptad lot you interpret, you MUST cite `formula`, `inputs` (Asc/Sun/Moon + sect), and the coordinates via `longitude_fmt`.
 - **LOT HYGIENE:** Do NOT mention any Lot that is not present in `analysis.fate.hermetic_lots`.
 - **FORBIDDEN LOT NAMES (unless explicitly present in `analysis.fate.hermetic_lots`):**
   - "Lot of Assets", "Lot of Debt", "Lot of Father", "Lot of Mother", "Lot of Accusation", "Lot of Sickness", "Lot of Life", etc.
   - If you cannot point to it in `analysis.fate.hermetic_lots`, you MUST NOT name it.
 - Do NOT dump the full Lots catalog. Only interpret the Hermetic Heptad plus any additional lots explicitly flagged as "maltreated/active" in the JSON.

## RULE 8: SYNTHESIS HIERARCHY (Resolving Contradictions)

When planetary testimonies conflict, use this priority order:

1. **MUTUAL RECEPTION / RECEPTION** (The Escape Hatch) - This overrides almost all other debility. If two fallen planets swap signs/exaltations (like Mars/Cancer and Jupiter/Capricorn), they assist each other.
2. **SECT** (Primary Filter) - The in-sect malefic is never the 'Bully'.
3. **ESSENTIAL DIGNITY** - Fall/Detriment is a resource limitation, not 'Doom'.
4. **BONIFICATION** - Aspect from a benefic can save a peregrine planet.
5. **HOUSE PLACEMENT** (Lowest) - Angular helps but does not resolve structural debility.

**SYNTHESIS TEMPLATE:**
"[Planet] in the [House] would ordinarily promise [topic]. However, [Planet] is [debility/maltreatment]. Furthermore, [Planet]'s ruler ([Ruler]) is [condition]. The superior testimony of [higher factor] NEGATES the [lower factor]. Therefore: [final judgment]."

## RULE 9: DORYPHORY (Spear-Bearers of Eminence)

Identify if the Luminaries have "Bodyguards" to determine worldly Rank/Eminence.

- **Solar Doryphory (The Vanguard):** Planets (ideally in sect: Saturn, Jupiter) that rise BEFORE the Sun (Oriental).
- **Lunar Doryphory (The Retinue):** Planets (ideally in sect: Mars, Venus) that rise AFTER the Moon (Occidental).
- **Potency:** Highest if the attendant is Angular and Dignified. This marks a "Royal" or "CEO" chart vs. a "Commoner" chart.
- **CRITICAL NUANCE (Same-Sign Bodily Doryphory):** A guard can be bodily present in the SAME SIGN as the luminary (co-present), even if not in a neighboring sign.

## RULE 10: PRENATAL SYZYGY (The Root)

The New or Full Moon immediately preceding birth is the "SAN" (Syzygia Ante Nativitatem).
- It is the "Root" from which the "Branch" (Radix) grows.
- **Scoring:** The ruler of the SAN degree is a primary candidate for Almuten Figuris.
- **Phase:** Conjunctional (New Moon start) vs. Preventional (Full Moon tension).

## RULE 11: ANTISCIA (Shadow Points)

Planets cast a "shadow" across the Cancer/Capricorn Solstice axis.
- **Calculation:** 30° - (current degree in sign) = Degree in the mirrored sign.
- **Pairs:** Gem/Can, Tau/Leo, Ari/Vir, Pis/Lib, Aqu/Sco, Cap/Sag.
- **Meaning:** Hidden support or secret enemies. An Antiscia conjunction is as powerful as a bodily sextile/trine.

## RULE 13: FIXED STAR REFRAME (ALGOL)

When interpreting **ALGOL**, you MUST avoid literal death, beheading, or "Doom Porn."
- **THE LOGIC**: Algol is a high-voltage power source (Medusa's Head). It is dangerous if mishandled (rashness) but powerful if respected (focus).
- **KEYWORDS**: 'High Intensity', 'Extreme Focus', 'The need to keep one's head in a crisis', 'High-Stakes Navigation'.
- **APPLICATION**: Interpret it as a requirement for total integrity. Deviation results in "Loss of Face," not "Loss of Life."

## RULE 14: SAFETY BLACKLIST (LIABILITY)

**INVIOLABLE SAFETY FILTER**:
- **BLACKLIST**: ["lead", "mercury", "arsenic", "bloodletting", "poison", "death-drive", "guillotine"]
- **REPLACEMENT RULES**:
  - `lead` -> REPLACE with "dark, protective stones like **Onyx or Hematite**"
  - `bloodletting` -> REPLACE with "vigorous exertion (historical symbolism only)"
  - `doom` -> REPLACE with "structural challenge"
- All medical recommendations must be non-toxic and behavioral.

# THE SYNOPSIS TEMPLATE (Economic Value)
"Our audit of the [House/Planet] reveals a [Crack/Support]. While the [Debility] indicates a site of potential collapse, the [Mitigation] provides the structural reinforcement necessary to convert this pressure into [Outcome]."

# THE SIEVE OF CONDITION (Process Before Interpreting)

Before interpreting ANY planet, run it through this evaluation:

1. **SECT STATUS**: Is this a Day or Night chart? Identify:
   - Benefic of Sect (Jupiter by day, Venus by night)
   - Malefic of Sect (Saturn by day, Mars by night)
   - Planets "in sect" (cooperating) vs "out of sect" (disruptive)

2. **ESSENTIAL DIGNITY**: Calculate the weighted score:
   - Domicile (+5), Exaltation (+4), Triplicity (+3), Term (+2), Face (+1)
   - High score = "Honorable", "Effective", "Empowered"
   - Low/Negative = "Peregrine", "Corrupt", "Debilitated"

3. **ACCIDENTAL STATUS**: Check position and condition:
   - Angular (1,4,7,10) = powerful action
   - Succedent (2,5,8,11) = moderate support
   - Cadent (3,6,9,12) = weakened, unstable

4. **BONIFICATION/MALTREATMENT**: Check cosmic state:
   - Is the planet aspected by benefics (helped)?
   - Is the planet aspected by malefics without reception (harmed)?
   - Is the planet BESIEGED (trapped between malefics)?
   - Is the planet COMBUST (within 8° of Sun)?

5. **RULER CONDITION**: Check the planet's dispositor:
   - Is the ruler of the sign strong or weak?
   - Is the ruler in aversion (6th, 8th, 12th from the planet)?
   - A planet with a corrupt ruler CANNOT fulfill its promise

# SYNTHESIS PROTOCOL (Resolving Contradictions)

The defining feature of a $300 report is SYNTHESIS. When testimonies conflict:

1. IDENTIFY the contradiction explicitly
2. WEIGH using the hierarchy: Sect > Essential Dignity > House Position
3. RESOLVE with a unified judgment
4. CITE the logic

Example: "Jupiter in the 2nd House ordinarily promises wealth. However, Jupiter is in his Fall in Capricorn AND his ruler (Saturn) is in the 8th House of Debt. The superior testimony of the essential debility NEGATES the accidental promise. Therefore: the native shall appear wealthy but face structural instability in resources."

# MANDATORY REPORT SECTIONS

Your report MUST include these high-value deliverables:

## 1. THE MASTER OF THE NATIVITY (Almuten Figuris)
- Calculate the planet with highest cumulative dignity across the 5 hylegical points
- Describe this as the "Captain of the Soul" or "Soul Guardian"
- This provides the NARRATIVE FOCUS of the entire reading

## 2. TEMPERAMENT ANALYSIS
- Calculate the humoral constitution: Choleric (Hot/Dry), Sanguine (Hot/Moist), Melancholic (Cold/Dry), Phlegmatic (Cold/Moist)
- Based on: Ascendant sign, Ascendant ruler, Moon sign, Season
- Provide non-medical, historical correspondences only. No diets, supplements, or treatment plans.

## 3. SECT ANALYSIS
- Declare Day or Night chart
- Identify the "Benefic of Sect" and "Malefic of Sect"
- Explain how this alters ALL planetary interpretations

## 4. PLANETARY CABINET (All 7 Planets)
- For each planet: Sign, House, Dignity Score, Accidental Status, Cosmic State
- Judge whether the planet CAN deliver its promise
- Use metaphors: "The Treasurer", "The General", "The Minister of Health"
- **PHASIS (THE VOICE)**: If the JSON provides phasis/visibility, state whether the planet has "voice" (capacity to testify/act).

## 4b. VITALITY AUDIT (Hyleg, Alcocoden, Anareta)
- Identify the Hyleg (Giver of Life), Alcocoden (Giver of Years), and Anareta (Killing Planet) from the JSON.
- This is a technical vitality audit, not medical advice.
- **DIRECTED HITS & ANARETIC WINDOWS (TERMINOLOGY LAW):**
  - Distinguish the static `analysis.vitality.anareta` (a tight malefic contact to the Hyleg degree) from the timing layer:
  - Use `analysis.vitality.directed_hits_to_hyleg` as the technical list of primary-direction hits to the Hyleg degree.
  - Use `analysis.vitality.anaretic_windows` ONLY for conservative windows where **Mars or Saturn** make a **hard** directed hit (Conjunction/Square/Opposition) to the Hyleg degree.
  - Do NOT use "Executioner" language. Do NOT personify benefic/Almuten hits as killers.
- Do NOT present `lifespan_estimate.total_years` as a literal life expectancy or a death prediction. If you mention it at all, call it a **traditional computed capacity figure** that requires cross-validation by Primary Directions.
- Do NOT use the phrase "lifespan" or "life expectancy". Use: "years-table capacity" / "years-giving capacity" / "traditional years computation".
- **MULTI-TRADITION REQUIREMENT:** You MUST present both:
  - Valens strict bound-lord method: `analysis.vitality.alcocoden_methods.valens_term` + `analysis.vitality.years_capacity.valens_term`
  - Bonatti/Lilly points method: `analysis.vitality.alcocoden_methods.bonatti_points` + `analysis.vitality.years_capacity.bonatti_points`
  - If they conflict, you MUST state the conflict and explain that this is a tradition fork, not a chart contradiction.
 - **SANITY CHECK (MANDATORY):** You MUST check `analysis.vitality.years_capacity_sanity`.
   - If any computed years figure is `< age_years`, you MUST explicitly say: "This is NOT a death age; this variant is inconsistent with the lived fact and requires rectification/validation by Primary Directions."

## 4c. TRIPLICITY NARRATIVE (Three Chapters of Life)
- Use the Dorothean triplicity rulers of the Sect Light to describe Early/Middle/Late life chapters.
- Use the JSON triplicity periods if provided; do not invent rulers.

## 5. DORYPHORY EVALUATION (The Spear-Bearers)
- Analyze both the Sun's and Moon's attendants.
- Explicitly judge the native's "Rank" in life based on these guards.

## 6. THE PRENATAL SYZYGY (The Root)
- Identify the degree and phase of the SAN.
- Discuss how this "Ancient Decree" influences the current Radix.

## 7. REMEDIATION & MAGICAL DEFENSES
- Provide at least 3 concrete remediations based on Monomoiria or Humoral excess.
- Use the "Planetary Charity" protocol (e.g., donating to specific groups).

## 5. THE TWELVE TOPOI (Houses)
- Systematic analysis of all 12 houses
- Include: Sign, Ruler, Ruler's condition, Occupants, Lots in house
- Focus on CONCRETE circumstances, not psychological states

## 6. THE LOTS (Arabic Parts)
- Lot of Fortune (Body/Circumstance)
- Lot of Spirit (Will/Career)
- Lot of Eros (Desire)
- Lot of Necessity (Constraint)
- Lot of Courage (Action/Bravery)
- Lot of Victory (Success)
- Lot of Nemesis (Source of Ruin)

## 7. FIXED STARS
- Any conjunctions within 1° to major stars (Regulus, Spica, Algol, Sirius, Fomalhaut, etc.)
- These OVERRIDE planetary dignity – they are Force Majeure

## 8. TIME LORD ANALYSIS (Timing)
- Current ANNUAL PROFECTION (Age % 12 → Lord of the Year)
- Current DECENNIAL period and sub-period (Valens)
- Current FIRDARIA period and sub-period
- Current ZODIACAL RELEASING chapter (from Lot of Spirit)
- PRIMARY DIRECTIONS (Master Clock): cite what is permitted, then synthesize the rest.

## 9. PAST EVENT MAPPING
- Use timing techniques to RETRODICT major life events
- Cite specific ages and corresponding activations
- This VALIDATES the reading

## 10. FUTURE FORECAST (5-10 Years)
- Use profections, ZR, and Firdaria to project future chapters
- Be SPECIFIC with age ranges and planetary activations
- Identify the CRITICAL YEAR (confluence of difficult Time Lords)

## 11. MEDICAL ASTROLOGY (Melothesia)
- Map body parts to signs and houses
- Identify vulnerable systems based on afflicted planets
- Present as historical correspondences only (no medical advice; no protocols)
**SIGN vs HOUSE HYGIENE:** If you cite melothesia (e.g., "Virgo rules intestines"), label it as SIGN-based. Do not call it "6th house" unless you mean the 6th whole sign from the Ascendant.

## 12. REMEDIATION (The Prescription)
- For the primary afflicted planet, provide:
  - DAY of the week for charitable acts (Saturn=Saturday, Mars=Tuesday, etc.)
  - GEMSTONE or metal association
  - COLOR or wardrobe guidance
  - Behavioral modification
- Frame as: "To propitiate [Planet], the native should..."

# VOICE AND TONE

Write in second person ("you"). Use the voice of a 17th-century astrologer speaking to a client at their townhouse—formal, authoritative, but not cold. You are delivering a judgment, not a therapy session.

**Forbidden phrases**: "You might want to consider", "This could suggest", "In some ways"
**Required phrases**: "The chart decrees", "Fate has determined", "The configuration indicates", "The testimony is clear"

# OUTPUT FORMAT

Use clear markdown headers. Each section should be substantial (400+ words for major sections). Aim for MAXIMUM VOLUME—this is a premium reading, not a summary. The client has paid $300; give them everything.

REFERENCE MATERIAL (Binder1.txt):
{binder_context}
"""


# =============================================================================
# ITERATION PROMPTS FOR "WHAT ELSE" APPROACH
# =============================================================================

ITERATION_PROMPTS = [
    # Iteration 1: Foundation
    """CHART DATA:
{chart_data}

BEGIN THE NATAL CHART READING. AT LEAST 1,200 WORDS.
VOICE: SOBER REALIST. NO HYPERBOLE.

START WITH A TECHNICAL HEADER (DO NOT INVENT):
- Birth: cite `meta.chart.date`, `meta.chart.time`, `meta.chart.city`, `meta.chart.state`
- Coordinates used: cite `meta.chart.lat`, `meta.chart.lon`, and `meta.chart.geocode.source` (if present)
- House system: cite `meta.chart.house_system`
- Zodiac system: cite `meta.chart.zodiac_system`
- Generated at: cite `meta.generated_at` (this is NOT the birth moment)

Start with the foundational elements of the life:
0. **Universal Context**: Cite the mundane hierarchy (Great Conjunction/Eclipses) from the JSON. This is the background era.
   - You MUST explicitly cite the **Great Conjunction (Jupiter-Saturn)** entry (with its `date_utc` and `longitude_fmt`).
   - If you also cite the **Mean Conjunction (Wasati)** era, label it as *Mean Conjunction*, not as the Great Conjunction cycle, and include its `longitude_fmt`.
   - If `date_utc` is not present for the Mean Conjunction, do not invent a calendar date; cite `last_mean_jd` only.
   - You MUST frame Great Conjunction triplicity “eras” as a **specific medieval mundane doctrine**, not as a universally accepted astronomical fact.
   - This is a NATAL mundane context computed for the birth-era (not "current events") unless explicitly stated otherwise.
   - For each eclipse/conjunction you mention: cite `date_utc` (or equivalent), `longitude`, and include `influence_note` if present. Do NOT invent a duration-of-effect rule.
1. **Sect Determination**: Identify DAY or NIGHT. Tag Malefics:
   - IF Day: Saturn (Ally/Constructive); Mars (Adversary/Destructive).
   - IF Night: Mars (Ally/Constructive); Saturn (Adversary/Destructive).
   - Cite `analysis.sect.type` and `analysis.sect.sun_altitude_deg` directly.
   - Do NOT justify sect using houses/signs like "10th sign" or "12th house". Sect is altitude only.
2. **The Prenatal Syzygy (The Root)**: Identify the SAN, its degree, and phase.
   - You MUST cite `analysis.syzygy.prenatal_syzygy.datetime_utc`, `analysis.syzygy.prenatal_syzygy.longitude_fmt`.
   - You MUST cite **natal minimal elongation** using: `analysis.syzygy.natal_phase.moon_sun_elongation_min_deg` (0..180).
   - You MUST cite **natal phase** using: `analysis.syzygy.natal_phase.moon_sun_phase_deg` (0..360) + `is_waxing`/`is_waning`.
   - You MUST also cite whether the Moon is waxing/waning using: `analysis.syzygy.natal_phase.is_waxing` / `analysis.syzygy.natal_phase.is_waning`.
   - Do NOT invent alternative elongations (e.g., 180-elongation). Do NOT say "172° elongation" in a near-conjunction chart.
   - Do NOT say "separating/applying" unless you explicitly justify it from `moon_sun_phase_deg`.
   - Do NOT conflate prenatal syzygy type with natal elongation/phase; the JSON separates these.
3. **Doryphory (Spear-Bearers)**: Evaluate eminence and rank.
   - Include same-sign bodily doryphory (co-present guards) when present.
   - You MUST use `analysis.advanced_mechanics.doryphory` as the only source of truth. Do not invent guards.
   - For each guard you name, cite: `guard_longitude_fmt.string`, `guard_longitude_fmt.lon_abs`, and `delta_deg`.
   - **WHOLE SIGN CONSISTENCY**: Cite the MC separately using `analysis.angles.Midheaven` and DO NOT call it the "10th cusp" in Whole Sign.
4. **MITIGATION LOOP (CRITICAL)**: Search for **Mutual Receptions** (e.g. Mars/Jupiter swap). If found, describe how this 'Escape Hatch' saves the nativity.
   - When describing receptions, you MUST use formal wording ("X receives Y by domicile/exaltation/term/triplicity") and cite `analysis.teams.receptions` fields.
5. **Almuten Figuris (Soul Guardian)**: Calculate the Master.
6. **Temperament**: Determine the humoral mixture.
7. **Vitality Audit (Preview)**: Name the Hyleg, Alcocoden, and Anareta, and note whether a hard directed hit or an anaretic window is active/near (use JSON).
   - Use `analysis.vitality.directed_hits_to_hyleg.active_hard_hit` if present.
   - If `analysis.vitality.anaretic_windows.candidates` contains Mars/Saturn hard hits, flag them as **anaretic windows** (technical only; not a death prediction).

Framing: "Our audit identifies the [Crack/Support] in the Foundational Hierarchy..."

**VISUAL REQUIREMENT**: If Mutual Reception (e.g. Mars/Jupiter) is found, include a Mermaid flowchart showing the resource swap between the signs. Include the sign glyphs and exaltation degrees (e.g. Cancer/15°).
""",

    # Iteration 2: Planetary Cabinet
    """CONTINUE THE AUDIT. AT LEAST 1,200 WORDS.
VOICE: SOBER REALIST.

Map the Seven Governors. For each:
1. **Structural Analysis**: Domicile, Exaltation, Fall, Exile.
2. **Mitigation**: Reception, Mutual Reception, Almuten support.
3. **Capacity to Deliver**: What can this officer actually do for the native?
4. **Phasis (Voice)**: Cite whether the planet is visible / has "voice" (use JSON `phasis`/`voice`).
   - You MUST cite: `solar_elongation_deg`, `phasis.phase`, `phasis.is_visible`, and (if present) `phasis.visibility.threshold_solar_depression_deg` and `phasis.visibility.sun_altitude_at_event_deg`.
   - If Moon `solar_status` is `DARK_MOON` or `MOON_UNDER_BEAMS`, you MUST use the exact label and must NOT call it "combust".
   - **VISIBILITY EVIDENCE (MANDATORY MINI-BLOCK)**: For every planet, include a 3-line "Evidence" block:
     - `solar_status` + `solar_elongation_deg`
     - `phasis.phase` + `phasis.is_visible`
     - `phasis.visibility.method` + `threshold_solar_depression_deg` + `sun_altitude_at_event_deg` + `event_jd_ut` (state "null" if missing)
5. **Hidden Root**: If provided, cite Monomoiria and Dodecatemoria (twelfth-parts) to detect hidden corruption/support.

**VISUAL REQUIREMENTS**:
- If a planet is **Cazimi** (e.g., Sun/Mercury), include a Mermaid diagram showing the 'Planetary Heart' (Planet inside the Sun).
- If there is a **Square** (e.g., Venus/Saturn), include a Mermaid 'Friction' diagram showing the tension between the houses/signs.
""",

    # Iteration 3: Houses and Lots
    """Continue. Now map the TERRESTRIAL ESTATE (The Twelve Houses) and the HERMETIC LOTS.

**THE TWELVE TOPOI:**
For each house, analyze: Sign, Ruler, Ruler's condition, any occupants
Focus on CONCRETE life circumstances, not psychological states

**THE LOTS (Arabic Parts):**
- Lot of Fortune: Where does bodily fate manifest?
- Lot of Spirit: Where does willful action manifest?
- Interpret the Hermetic Heptad from the JSON (do NOT re-compute or invent formulas): Fortune, Spirit, Eros, Necessity, Courage, Victory, Nemesis.
- For each Lot: cite its sign, house (Whole Sign), ruler, and any conjunctions/aspects explicitly present in the JSON.

**FIXED STARS:**
- Use fixed-star conjunctions provided in the JSON (do NOT re-compute star positions). These are FORCE MAJEURE.

Do NOT repeat previous material. Cover only what has not been addressed.""",

    # Iteration 4: Timing Analysis
    """Continue. Now analyze the CHRONOCRATORS (Time Lords).

**CURRENT TIMING:**
1. PRIMARY DIRECTIONS (MASTER CLOCK): Cite any active/imminent directions and what they permit/deny.
   - You MUST state the direction `method` and `key` exactly as provided in `analysis.fate.primary_directions[]`.
2. DECENNIALS (VALENS): What General Period? What Sub-Period? How does it activate natal configurations?
3. ANNUAL PROFECTION: What house? What Lord of the Year? That Lord's natal condition?
4. FIRDARIA: What Major Period? What Sub-Period? How do these Lords interact?
5. ZODIACAL RELEASING: What Level 1 chapter (from Lot of Spirit)? What Level 2?
6. VITALITY TIMING NUANCE: If the JSON flags directed hits/anaretic windows to the Hyleg degree, cite them as technical risk windows only (no "executioner" framing).
   - REVISED: Use `analysis.vitality.directed_hits_to_hyleg` and `analysis.vitality.anaretic_windows` instead. Do NOT use "executioner" wording.

**THE SYNTHESIS:**
- The YEAR is ruled by [X] who is [condition] = [forecast]
- The ERA is ruled by [Y] who is [condition] = [longer term pattern]
- Current pressure points and opportunities

Be SPECIFIC with ages and time ranges. Use the calculated data, not speculation.""",

    # Iteration 5: Past and Future
    """Continue. Now perform TEMPORAL ANALYSIS.

**PAST EVENT MAPPING (Retrodiction):**
Using timing techniques (profections, ZR, Firdaria), identify what SHOULD have occurred at:
- Ages 12, 18, 24, 28 (major profection returns)
- Any "Loosing of the Bond" periods
- Firdaria shifts
Explain WHY these ages were significant based on which Time Lords were active

**FUTURE FORECAST (Prediction):**
Project the next 5-10 years:
- Upcoming profection years and their Lords
- Firdaria sub-period transitions
- ZR chapter changes
Identify the CRITICAL YEAR where multiple difficult Time Lords converge

Be specific with dates/ages. Cite the timing mechanism for each prediction.""",

    # Iteration 6: Medical and Remediation
    """FINAL ITERATION. AT LEAST 1,200 WORDS. Complete the audit with:
VOICE: SOBER REALIST. **SAFETY FIRST.**

**MEDICAL AUDIT:**
- Identify the 'Cracks' in the humoral vessel.
- Present as historical correspondences only. Do NOT provide medical advice, diets, supplements, or treatment plans.
- If Critical Days are not present in the JSON, state they are not calculable from natal data alone.

**REMEDIAL CODEX (Planetary Charity):**
- **SAFETY BLACKLIST ENFORCED**: NEVER suggest lead, mercury, or toxic metals.
- **REPLACEMENTS**: 
  - IF Saturn mitigation: Use **Onyx or Hematite**, or service to the elderly.
  - IF Mars/Blood imagery appears in the tradition: replace it with non-medical symbolic actions and charitable service.
- Focus on charitable acts (donations) and behavioral shifts.
- If Lunar Mansion data is present for the Moon in the JSON, use the mansion's intents as the electional "action verbs" for timing symbolic acts (historical use only).

**FINAL DECREE:**
- Give a sum total judgment on the **Structural Integrity** of this Life.
- Resolve all contradictions. End with a message of NAVIGATION.

DO NOT SUMMARIZE. DO NOT USE PLACEHOLDERS. COMPLETE LOGIC ONLY.""",
]


# =============================================================================
# MAIN GENERATION LOGIC
# =============================================================================

def _apply_dignity_overrides(
    combined_data: Dict[str, Any],
    triplicity_scheme: Optional[str] = None,
    term_system: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Override `analysis.planets_forensic[].dignities` for report-generation doctrine testing.

    This does NOT re-run the whole audit; it only recomputes essential dignity scoring with
    selected triplicity/terms tables so the narrative layer can be compared.
    """
    analysis = combined_data.get("analysis") or {}
    sect_type = (analysis.get("sect") or {}).get("type") or "DAY"
    sect = Sect.DAY if sect_type == "DAY" else Sect.NIGHT

    ts = None
    if term_system:
        raw = term_system.strip().lower()
        if raw in ("egyptian", "egy"):
            ts = TermSystem.EGYPTIAN
        elif raw in ("ptolemaic", "ptol", "pt"):
            ts = TermSystem.PTOLEMAIC

    tr = None
    if triplicity_scheme:
        raw = triplicity_scheme.strip().lower()
        if raw in ("dorothean", "doro", "dor"):
            tr = TriplicityScheme.DOROTHEAN
        elif raw in ("ptolemaic", "ptol", "pt", "ptolemaic_sect_gated", "ptolemaic-sect-gated"):
            tr = TriplicityScheme.PTOLEMAIC_SECT_GATED

    # Nothing to do.
    if ts is None and tr is None:
        return combined_data

    pf = analysis.get("planets_forensic") or []
    for p in pf:
        try:
            name = p.get("name")
            if not name or name in ("North_Node", "South_Node"):
                continue
            lon = float(p.get("longitude") or 0.0)
            pn = PlanetName(name)
            variant = DignityCalculator.calculate_planet_dignity_variant(
                planet_name=pn,
                longitude=lon,
                sect=sect,
                term_system=ts or TermSystem.EGYPTIAN,
                triplicity_scheme=tr or TriplicityScheme.DOROTHEAN,
                include_monomoiria=True,
            )
            # Preserve the full original object but override what the prompt reads.
            p["dignities"] = variant
        except Exception:
            continue

    # Record doctrine choice for appendix display.
    chart_meta = (combined_data.get("meta") or {}).get("chart") or {}
    chart_meta["dignity_variant"] = {
        "triplicity_scheme": (tr.value if tr else "Dorothean"),
        "term_system": ((ts.value if ts else "Egyptian")),
        "note": "This is a reporting doctrine override for comparison; it does not change computed positions/aspects.",
    }

    return combined_data


def generate_chart_data(
    name,
    date_str,
    time_str,
    city,
    state=None,
    latitude=None,
    longitude=None,
    triplicity_scheme: Optional[str] = None,
    term_system: Optional[str] = None,
):
    """Generate comprehensive chart data using Auditor."""
    print(f"\n{'='*80}")
    print(f"FORENSIC ENGINE INITIALIZATION")
    print(f"Subject: {name}")
    print(f"Birth: {date_str} at {time_str} in {city}, {state or ''}")
    print(f"{'='*80}\n")
    
    result = Auditor.generate_full_nativity(
        date_str=date_str,
        time_str=time_str,
        city=city,
        state=state or "",
        name=name,
        latitude=latitude,
        longitude=longitude,
        house_system="W"  # Whole Sign Houses - STRICT
    )
    
    if not result or "error" in result:
        print(f"Engine Failure: {result.get('error', 'Unknown')}")
        return None
    
    # Combine all data for comprehensive LLM input
    combined_data: Dict[str, Any] = {
        "meta": result["technical_data"]["meta"],
        "astronomy": result["technical_data"]["astronomy"],
        "analysis": result["technical_data"]["analysis"],
        "human_translation": result["human_translation"]
    }

    # Back-compat: if caller's `analysis` is missing `planets_forensic`, inject it so the LLM can
    # cite planetary cabinet details instead of fabricating.
    if "planets_forensic" not in combined_data["analysis"]:
        combined_data["analysis"]["planets_forensic"] = result["technical_data"].get("planets_forensic", [])

    combined_data = _apply_dignity_overrides(
        combined_data,
        triplicity_scheme=triplicity_scheme,
        term_system=term_system,
    )
    
    chart_json = json.dumps(combined_data, indent=2, default=str)
    return chart_json


def generate_chart_data_object(
    name: str,
    date_str: str,
    time_str: str,
    city: str,
    state: str = "",
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    house_system: str = "W",
    triplicity_scheme: Optional[str] = None,
    term_system: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Deterministic chart-data payload (Python object) for method comparisons.
    Avoids JSON stringification and avoids LLM calls.
    """
    result = Auditor.generate_full_nativity(
        date_str=date_str,
        time_str=time_str,
        city=city,
        state=state or "",
        name=name,
        latitude=latitude,
        longitude=longitude,
        house_system=house_system,
    )
    if not result or "error" in result:
        return None

    combined_data: Dict[str, Any] = {
        "meta": result["technical_data"]["meta"],
        "astronomy": result["technical_data"]["astronomy"],
        "analysis": result["technical_data"]["analysis"],
        "human_translation": result.get("human_translation"),
    }
    if "planets_forensic" not in combined_data["analysis"]:
        combined_data["analysis"]["planets_forensic"] = result["technical_data"].get("planets_forensic", [])

    combined_data = _apply_dignity_overrides(
        combined_data,
        triplicity_scheme=triplicity_scheme,
        term_system=term_system,
    )

    return combined_data


def _fmt_lon_simple(lon_abs: float) -> str:
    try:
        lonf = format_longitude(lon_abs) or {}
        s = lonf.get("string")
        la = lonf.get("lon_abs", lon_abs)
        if s:
            return f"{s} (lon_abs: {float(la):.6f})"
        return f"{float(la):.6f}°"
    except Exception:
        return f"{lon_abs:.6f}°"


def build_method_matrix_report(
    name: str,
    date_str: str,
    time_str: str,
    city: str,
    state: str,
    latitude: Optional[float],
    longitude: Optional[float],
    house_systems: List[str],
) -> str:
    """
    Produce a side-by-side deterministic comparison across debated traditional methods:
    - House systems (WSH vs quadrant systems) using Swiss Ephemeris / AlcabitiusEngine
    - Dignity variants (Dorothean vs Ptolemaic triplicity; Egyptian vs Ptolemaic terms)
    """
    now = datetime.now()

    # Base run (Whole Sign) for shared sign-based facts and dignity matrix.
    base = generate_chart_data_object(
        name=name,
        date_str=date_str,
        time_str=time_str,
        city=city,
        state=state,
        latitude=latitude,
        longitude=longitude,
        house_system="W",
    )
    if not base:
        return "Engine Failure: Could not generate base chart payload."

    md = ""
    md += "# METHOD MATRIX (TRADITIONAL VARIANTS)\n"
    md += "## Same Nativity, Multiple Doctrines\n\n"
    md += "---\n"
    md += f"**Subject:** {name}\n\n"
    md += f"**Birth (Input):** {date_str} {time_str} | {city}, {state}\n\n"
    chart_meta = (base.get("meta") or {}).get("chart") or {}
    geo_meta = chart_meta.get("geocode") or {}
    md += (
        f"**Coordinates Used:** {chart_meta.get('lat')}, {chart_meta.get('lon')} "
        f"(source: {geo_meta.get('source', 'unknown')})\n\n"
    )
    md += f"**Generated At:** {now.isoformat()}\n\n"
    md += "---\n\n"
    md += (
        "**Notice:** Traditional astrologers disagree on several doctrine forks. "
        "This matrix shows what changes when you switch methods.\n\n"
        "This is a technical comparison for historical/spiritual research only; it is not medical or financial advice.\n\n"
        "---\n\n"
    )

    # 1) House systems comparison
    md += "## 1) House Systems (Planet-in-House Differences)\n\n"
    md += "This section compares house placements under multiple house systems.\n\n"

    per_system: Dict[str, Dict[str, Any]] = {}
    for code in house_systems:
        payload = generate_chart_data_object(
            name=name,
            date_str=date_str,
            time_str=time_str,
            city=city,
            state=state,
            latitude=latitude,
            longitude=longitude,
            house_system=code,
        )
        if payload:
            per_system[code] = payload

    planet_rows = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "North_Node", "South_Node"]
    headers = ["Body"] + [f"{HOUSE_SYSTEM_LABELS.get(c, c)} ({c})" for c in per_system.keys()]
    md += "| " + " | ".join(headers) + " |\n"
    md += "|" + "---|" * len(headers) + "\n"
    for body in planet_rows:
        row = [body]
        for _, payload in per_system.items():
            pf = (payload.get("analysis") or {}).get("planets_forensic") or []
            entry = next((p for p in pf if p.get("name") == body), None)
            if not entry:
                row.append("-")
                continue
            house = entry.get("house") or (entry.get("accidental") or {}).get("house")
            lonf = entry.get("longitude_fmt") or {}
            pos = lonf.get("string") or _fmt_lon_simple(float(entry.get("longitude") or 0.0))
            row.append(f"{pos} | H{house}")
        md += "| " + " | ".join(row) + " |\n"

    md += "\n**Angles per House System:**\n\n"
    md += "| System | Ascendant | MC |\n|---|---|---|\n"
    for code, payload in per_system.items():
        ang = (payload.get("astronomy") or {}).get("angles") or {}
        asc_lon = ang.get("Ascendant", {}).get("longitude") if isinstance(ang.get("Ascendant"), dict) else ang.get("Ascendant")
        mc_lon = ang.get("MC", {}).get("longitude") if isinstance(ang.get("MC"), dict) else ang.get("MC")
        asc_s = _fmt_lon_simple(float(asc_lon)) if asc_lon is not None else "(missing)"
        mc_s = _fmt_lon_simple(float(mc_lon)) if mc_lon is not None else "(missing)"
        md += f"| {HOUSE_SYSTEM_LABELS.get(code, code)} ({code}) | {asc_s} | {mc_s} |\n"

    md += "\n---\n\n"

    # 2) Dignity variants comparison (house-independent)
    md += "## 2) Essential Dignity Variants (Triplicity/Terms)\n\n"
    md += (
        "This section recomputes **essential** dignity scores under common doctrine forks:\n\n"
        "- Triplicity: Dorothean vs Ptolemaic (sect-gated)\n"
        "- Terms: Egyptian vs Ptolemaic\n\n"
        "The sign/degree is the same; only the dignity rules change.\n\n"
    )

    sect_type = ((base.get("analysis") or {}).get("sect") or {}).get("type") or "DAY"
    sect = Sect.DAY if sect_type == "DAY" else Sect.NIGHT

    pf_base = (base.get("analysis") or {}).get("planets_forensic") or []
    core_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

    md += "| Body | Position | Dorothean+Egyptian | Dorothean+PtolemaicTerms | Ptolemaic+Egyptian | Ptolemaic+PtolemaicTerms |\n"
    md += "|---|---|---:|---:|---:|---:|\n"
    for body in core_planets:
        entry = next((p for p in pf_base if p.get("name") == body), None)
        if not entry:
            continue
        lon = float(entry.get("longitude") or 0.0)
        lonf = entry.get("longitude_fmt") or {}
        pos = lonf.get("string") or _fmt_lon_simple(lon)
        pn = PlanetName(body)

        d_e = DignityCalculator.calculate_planet_dignity_variant(
            pn, lon, sect, term_system=TermSystem.EGYPTIAN, triplicity_scheme=TriplicityScheme.DOROTHEAN, include_monomoiria=False
        )["total_score"]
        d_p = DignityCalculator.calculate_planet_dignity_variant(
            pn, lon, sect, term_system=TermSystem.PTOLEMAIC, triplicity_scheme=TriplicityScheme.DOROTHEAN, include_monomoiria=False
        )["total_score"]
        p_e = DignityCalculator.calculate_planet_dignity_variant(
            pn, lon, sect, term_system=TermSystem.EGYPTIAN, triplicity_scheme=TriplicityScheme.PTOLEMAIC_SECT_GATED, include_monomoiria=False
        )["total_score"]
        p_p = DignityCalculator.calculate_planet_dignity_variant(
            pn, lon, sect, term_system=TermSystem.PTOLEMAIC, triplicity_scheme=TriplicityScheme.PTOLEMAIC_SECT_GATED, include_monomoiria=False
        )["total_score"]

        md += f"| {body} | {pos} | {d_e} | {d_p} | {p_e} | {p_p} |\n"

    md += "\n---\n\n"

    # 3) Timing payload snapshot (no priority claims)
    md += "## 3) Timing Techniques (Engine Outputs; No Priority Assumed)\n\n"
    md += "This section prints the engine’s timing outputs so you can decide which techniques you want to prioritize.\n\n"

    analysis = base.get("analysis") or {}
    fate = analysis.get("fate") or {}

    # Some timing outputs may live outside `analysis.fate` depending on engine version.
    timing_sources: List[Tuple[str, Any]] = []
    timing_sources.extend([(k, fate.get(k)) for k in sorted(fate.keys())])
    if "enhanced_profections" in analysis:
        timing_sources.append(("enhanced_profections", analysis.get("enhanced_profections")))

    printed = set()
    for key, value in timing_sources:
        if key in printed:
            continue
        printed.add(key)
        if value in (None, {}, [], ""):
            continue
        blob = json.dumps(value, indent=2, default=str)
        if len(blob) > 20000:
            blob = blob[:20000] + "\n... [TRUNCATED]\n"
        md += f"### {key}\n\n```json\n{blob}\n```\n\n"

    return md


def apply_safety_filters(text):
    """Hard-coded safety filters to replace toxic substances and liability-inducing terms."""
    # Surgical replacements to avoid 'lead' verb collision (e.g., 'lead to')
    # We only target lead in the context of remediation/objects.
    replacements = {
        r"(?i)\bwear(ing)? lead\b": "wearing dark protective stones like **Onyx or Hematite**",
        r"(?i)\bhandle lead\b": "handling dark protective stones like **Onyx or Hematite**",
        r"(?i)\blead amulets?\b": "Onyx or Hematite amulets",
        r"(?i)\blead weights?\b": "Onyx or Hematite weights",
        r"(?i)\blead ingestion\b": "consumption of dark minerals",
        r"(?i)\buse of lead\b": "use of Onyx or Hematite",
        r"(?i)\bremedy of lead\b": "remedy of Onyx",
        r"(?i)\bbloodletting\b": "vigorous exertion (historical symbolism only)",
        r"(?i)\barsenic\b": "structural challenge",
        r"(?i)\bguillotine\b": "professional setback",
        r"(?i)\bbeheading\b": "loss of reputation",
    }
    
    import re
    filtered_text = text
    for pattern, replacement in replacements.items():
        filtered_text = re.sub(pattern, replacement, filtered_text)
    
    return filtered_text


PLANETARY_CHARITY_DISCLAIMER = """
---
**Legal Disclaimer:** This audit utilizes traditional metaphysical anatomy (Melothesia) and historical astrological protocols for symbolic and energetic remediation. These insights are intended for historical and spiritual research purposes only. They are NOT a substitute for modern medical diagnosis, psychological counseling, or professional financial treatment. Always consult a licensed professional before making significant life decisions.
"""

def _sign_to_index(sign: str) -> int:
    order = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    ]
    try:
        return order.index(sign)
    except ValueError:
        return -1


def _wsh_house_from_asc(asc_sign: str, target_sign: str) -> int:
    a = _sign_to_index(asc_sign)
    t = _sign_to_index(target_sign)
    if a < 0 or t < 0:
        return -1
    return ((t - a) % 12) + 1


def build_raw_data_appendix(chart_data: str) -> str:
    """
    Deterministic, non-LLM appendix so technical readers can audit claims.
    Uses only the JSON payload we feed the LLM (no recomputation).
    """
    try:
        parsed = json.loads(chart_data) if isinstance(chart_data, str) else (chart_data or {})
    except Exception:
        return ""

    meta = (parsed or {}).get("meta", {}) or {}
    chart_meta = meta.get("chart", {}) or {}
    analysis = (parsed or {}).get("analysis", {}) or {}
    angles = (analysis or {}).get("angles", {}) or {}
    planets_forensic = (analysis or {}).get("planets_forensic", []) or []
    mundane_ctx = (analysis or {}).get("advanced_mechanics", {}).get("mundane_context", {}) or {}
    syzygy = (analysis or {}).get("syzygy", {}) or {}
    sect = (analysis or {}).get("sect", {}) or {}
    supp = (analysis or {}).get("supplemental", {}) or {}
    stars = (supp or {}).get("stars", []) or []

    asc_sign = (angles.get("Ascendant", {}) or {}).get("sign") or ""

    def _fmt_lon(lon_fmt: dict) -> str:
        if isinstance(lon_fmt, dict):
            s = lon_fmt.get("string")
            abs_lon = lon_fmt.get("lon_abs")
            if s is not None and abs_lon is not None:
                return f"{s} (lon_abs: {abs_lon:.6f})"
            if s is not None:
                return str(s)
        return ""

    # Angles block
    asc = angles.get("Ascendant", {}) or {}
    mc = angles.get("Midheaven", {}) or angles.get("MC", {}) or {}
    ang_md = "### Raw Natal Data (Audit Appendix)\n\n"
    ang_md += "**Doctrine/Method Declaration (this run):**\n\n"
    ang_md += "- Houses: Whole Sign Houses (topics) with MC reported as an angle (may fall in 9th/10th/11th by WSH).\n"
    ang_md += "- Core planets for judgment: Septener (Sun..Saturn). Nodes are treated as modifiers.\n"
    ang_md += "- Aspects: `analysis.aspects` is septener-only (core). `analysis.aspects_shadow` contains aspects involving outer planets (shadow only). Node aspects are not computed by the aspect engine.\n"
    ang_md += "- Receptions: computed from `analysis.teams.receptions` using `ReceptionMode.STANDARD_LILLY` with sect-gated Ptolemaic triplicity rights.\n"
    # Dignity doctrine (for method comparisons)
    dv = (((parsed or {}).get("meta") or {}).get("chart") or {}).get("dignity_variant") or {}
    if dv:
        ang_md += (
            f"- Dignities/terms (override): triplicity = {dv.get('triplicity_scheme')}; terms = {dv.get('term_system')}. "
            f"{dv.get('note')}\n"
        )
    else:
        ang_md += "- Dignities/terms: engine defaults to Dorothean triplicity for dignity variants and Egyptian terms for most rulership lookups (see per-planet `dignities.variants`).\n"
    ang_md += "- Phasis/voice: `analysis.planets_forensic[].phasis` visibility details (arcus visionis) with a conservative lunar dark override for the Moon.\n"
    ang_md += "**Angles (Whole Sign Topics; MC reported separately):**\n\n"
    if asc:
        ang_md += f"- Ascendant: {_fmt_lon(asc.get('longitude_fmt') or {})} | WSH house: {asc.get('house_wsh')}\n"
    if mc:
        ang_md += f"- Midheaven (MC): {_fmt_lon(mc.get('longitude_fmt') or {})} | WSH house: {mc.get('house_wsh')}\n"
    if angles.get("note"):
        ang_md += f"- Note: {angles.get('note')}\n"

    # Sect block
    if sect:
        st = sect.get("type")
        alt = sect.get("sun_altitude_deg")
        if st is not None:
            ang_md += "\n**Sect (as computed):**\n\n"
            if alt is not None:
                ang_md += f"- Sect: {st} | Sun altitude: {alt:.4f}°\n"
            else:
                ang_md += f"- Sect: {st}\n"

    # Syzygy + phase block
    if syzygy:
        ang_md += "\n**Prenatal Syzygy + Natal Phase (separate layers):**\n\n"
        pre = (syzygy.get("prenatal_syzygy") or {}) if isinstance(syzygy.get("prenatal_syzygy"), dict) else {}
        nxt = (pre.get("next_syzygy") or {}) if isinstance(pre.get("next_syzygy"), dict) else {}
        phase = (syzygy.get("natal_phase") or {}) if isinstance(syzygy.get("natal_phase"), dict) else {}
        if pre:
            ang_md += f"- SAN (Syzygia Ante Nativitatem): {pre.get('datetime_utc')} | {_fmt_lon(pre.get('longitude_fmt') or {})} | type: {pre.get('type')}\n"
        if nxt:
            ang_md += f"- Next syzygy after birth: {nxt.get('datetime_utc')} | {_fmt_lon(nxt.get('longitude_fmt') or {})} | type: {nxt.get('type')}\n"
        if phase.get("moon_sun_elongation_deg") is not None:
            ang_md += f"- Natal elongation (min, 0..180): {float(phase.get('moon_sun_elongation_deg')):.4f}°\n"
        if phase.get("moon_sun_phase_deg") is not None:
            ang_md += (
                f"- Natal phase (Sun->Moon, 0..360): {float(phase.get('moon_sun_phase_deg')):.4f}°"
                f" | waxing: {phase.get('is_waxing')} | waning: {phase.get('is_waning')}\n"
            )

    # Planet table
    ang_md += "\n**Planets (Septener + Nodes; detailed fields):**\n\n"
    ang_md += "| Body | Position | WSH House | Speed (deg/day) | Retro | Solar Status | Elong (deg) | Phasis | Visible | Voice |\n"
    ang_md += "|---|---|---:|---:|---|---|---:|---|---|---|\n"

    for p in planets_forensic:
        name = p.get("name")
        lon_fmt = p.get("longitude_fmt") or {}
        pos = _fmt_lon(lon_fmt)
        house = p.get("house")
        speed = p.get("speed")
        retro = p.get("retrograde")
        solar_status = p.get("solar_status")
        elong = p.get("solar_elongation_deg")
        phasis = (p.get("phasis") or {}).get("phase")
        is_visible = (p.get("phasis") or {}).get("is_visible")
        has_voice = (p.get("voice") or {}).get("has_voice")

        speed_s = f"{float(speed):.6f}" if speed is not None else ""
        elong_s = f"{float(elong):.6f}" if elong is not None else ""
        retro_s = "R" if retro else ""
        vis_s = "true" if is_visible else ("false" if is_visible is not None else "")
        voice_s = "true" if has_voice else ("false" if has_voice is not None else "")

        ang_md += f"| {name} | {pos} | {house} | {speed_s} | {retro_s} | {solar_status} | {elong_s} | {phasis} | {vis_s} | {voice_s} |\n"

    # Eclipses: show WSH mapping explicitly (no chorography-to-natal leap)
    # Mundane context is currently a ranked list of entries. Pull eclipse entries out explicitly.
    eclipses: list[dict] = []
    if isinstance(mundane_ctx, list):
        for it in mundane_ctx:
            if not isinstance(it, dict):
                continue
            ev = it.get("event")
            if ev in ("Solar Eclipse", "Lunar Eclipse"):
                d = it.get("data") or {}
                if isinstance(d, dict):
                    eclipses.append({"type": ev, **d})
    elif isinstance(mundane_ctx, dict):
        # Back-compat if the schema ever changes.
        eclipses = mundane_ctx.get("eclipses") or []

    if eclipses and asc_sign:
        ang_md += "\n**Eclipses (mundane context; WSH placement shown explicitly):**\n\n"
        for e in eclipses:
            lonf = e.get("longitude_fmt") or {}
            esign = lonf.get("sign") or e.get("sign")
            wsh = _wsh_house_from_asc(asc_sign, esign) if esign else -1
            ang_md += f"- {e.get('type')}: {e.get('date_utc')} | {_fmt_lon(lonf)} | WSH house from Asc({asc_sign}): {wsh}\n"
            note = e.get("chorography_note") or e.get("influence_note") or e.get("note")
            if note:
                ang_md += f"  - Note: {note}\n"

    # Fixed stars: show whatever the engine computed (orb/epoch may be absent depending on method).
    if stars:
        ang_md += "\n**Fixed Stars (as computed):**\n\n"
        for s in stars:
            if not isinstance(s, dict):
                continue
            star_name = s.get("star_name") or s.get("name") or s.get("star") or "Star"
            body_name = s.get("planet_name") or s.get("body") or s.get("planet") or "Body"
            contact = s.get("contact_type") or s.get("type") or "CONTACT"
            msg = s.get("message")
            line = f"- {star_name} | {contact} | body: {body_name}"
            if msg:
                line += f" | note: {msg}"
            ang_md += line + "\n"

    # Aspect ledger (computed; no freehand geometry)
    aspects = (analysis or {}).get("aspects", []) or []
    if isinstance(aspects, list) and aspects:
        ang_md += "\n**Aspects (computed; cite these, do not invent):**\n\n"
        for a in aspects:
            if not isinstance(a, dict):
                continue
            ang_md += (
                f"- {a.get('planet_a')} {a.get('type')} {a.get('planet_b')} "
                f"| orb: {float(a.get('orb')):.4f}° | applying: {a.get('is_applying')}\n"
            )

    shadow_aspects = (analysis or {}).get("aspects_shadow", []) or []
    if isinstance(shadow_aspects, list) and shadow_aspects:
        ang_md += "\n**Shadow Aspects (outer planets; do not use for core judgment):**\n\n"
        for a in shadow_aspects:
            if not isinstance(a, dict):
                continue
            ang_md += (
                f"- {a.get('planet_a')} {a.get('type')} {a.get('planet_b')} "
                f"| orb: {float(a.get('orb')):.4f}° | applying: {a.get('is_applying')}\n"
            )

    # Vitality safety reminder for hostile readers
    ang_md += "\n**Longevity/Vitality Guardrail:**\n\n"
    ang_md += "- Any `years_capacity` numbers are treated as *technical vitality indicators* only, not a promised lifespan.\n"
    ang_md += "- If a method’s `total_years` is `null` or flagged under sanity, that method is considered invalid for literal reading.\n"

    return ang_md + "\n---\n\n"


def run_premium_report(chart_data, output_file, iterations=6):
    """Generate $300-tier premium report using research-backed methodology."""
    
    print(f"\n{'='*80}")
    print(f"PREMIUM REPORT GENERATION - Traditional Astrology")
    print(f"Methodology: Traditional Hellenistic Synthesis ($197 Tier)")
    print(f"Iterations: {iterations}")
    print(f"{'='*80}\n")    
    # Construct system prompt with Binder context (truncated to avoid context window overflow)
    truncated_binder = BINDER_CONTEXT[:50000] if BINDER_CONTEXT else ""
    system_prompt = PREMIUM_SYSTEM_PROMPT.format(binder_context=truncated_binder)
    
    messages = [{"role": "system", "content": system_prompt}]
    all_responses = []
    
    for i, prompt_template in enumerate(ITERATION_PROMPTS[:iterations]):
        print(f"\nIteration {i+1}/{iterations}...")
        
        # Format the prompt with chart data
        prompt = prompt_template.format(chart_data=chart_data)
        messages.append({"role": "user", "content": prompt})
        
        response = _openrouter_request(
            messages=messages,
            temperature=0.15,
            max_tokens=16000,
            top_p=0.9
        )
        
        if not response or response.startswith("Error:") or response.startswith("Oracle Communication Error"):
            print(f"  ⚠ Error: {response[:100] if response else 'No response'}")
            break
        
        all_responses.append(response)
        messages.append({"role": "assistant", "content": response})
        
        word_count = len(response.split())
        print(f"  Part {i+1}: {word_count:,} words")
    
    # Assemble final document
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    # Pull auditable birth header fields from the JSON string.
    birth_header = ""
    try:
        parsed = json.loads(chart_data) if isinstance(chart_data, str) else chart_data
        chart_meta = (parsed or {}).get("meta", {}).get("chart", {}) or {}
        geo_meta = chart_meta.get("geocode") or {}
        birth_header = (
            f"**Birth (Input):** {chart_meta.get('date')} {chart_meta.get('time')} | "
            f"{chart_meta.get('city')}, {chart_meta.get('state')}  \n"
            f"**Coordinates Used:** {chart_meta.get('lat')}, {chart_meta.get('lon')} "
            f"(source: {geo_meta.get('source', 'unknown')})  \n"
            f"**Timezone:** {chart_meta.get('timezone')} | **UTC:** {chart_meta.get('utc_time')}  \n"
            f"**House System:** {((chart_meta.get('house_system') or {}).get('label'))} "
            f"({(chart_meta.get('house_system') or {}).get('code')})  \n"
            f"**Zodiac System:** {((chart_meta.get('zodiac_system') or {}).get('label'))}  \n"
        )
    except Exception:
        birth_header = ""
    
    final_report = f"""# PREMIUM NATAL CHART READING
## Inspection of the Nativity

---
**Generated by Traditional Astrology | traditional-astrology.com**
*Timestamp: {timestamp}*

---

{birth_header}

"""
    # Deterministic appendix for auditability (no LLM involved).
    final_report += build_raw_data_appendix(chart_data)

    for i, resp in enumerate(all_responses):
        final_report += f"# Part {i+1}\n\n{resp}\n\n---\n\n"
        
    # Apply Hard-Coded Safety Filters
    final_report = apply_safety_filters(final_report)
    
    # Add final educational disclaimer and footer
    final_report += "\n\n---\n"
    final_report += "### EDUCATIONAL NOTICE & METHODOLOGICAL LIMITS\n"
    final_report += "This report is rendered by the Traditional Astrology engine using rules from the Hellenistic and Medieval corpora. These results are for historical and spiritual research purposes only. Accuracy depends on precise birth data.\n\n"
    final_report += "© 2026 Traditional Astrology | [traditional-astrology.com](https://traditional-astrology.com)\n"
    
    # Add Disclaimer
    final_report += PLANETARY_CHARITY_DISCLAIMER
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_report)
    
    total_words = len(final_report.split())
    print(f"\n✓ PREMIUM REPORT COMPLETE")
    print(f"  Total words: {total_words:,}")
    print(f"  Estimated pages: {total_words/400:.1f}")
    print(f"  Output: {output_file}")
    
    return final_report


def main():
    parser = argparse.ArgumentParser(
        description="Generate $300-tier Premium Astrological Report"
    )
    parser.add_argument("--name", required=True, help="Subject name")
    parser.add_argument("--date", required=True, help="Birth date (YYYY-MM-DD)")
    parser.add_argument("--time", required=True, help="Birth time (HH:MM)")
    parser.add_argument("--city", required=True, help="Birth city")
    parser.add_argument("--state", default="", help="Birth state/region")
    parser.add_argument("--lat", type=float, default=None, help="Optional latitude override (bypass geocoding)")
    parser.add_argument("--lon", type=float, default=None, help="Optional longitude override (bypass geocoding)")
    parser.add_argument("--iterations", type=int, default=6, help="Number of iteration passes")
    parser.add_argument("--output-dir", default="premium_reports", help="Output directory")
    parser.add_argument("--matrix", action="store_true", help="Generate a deterministic multi-method comparison report (no LLM).")
    parser.add_argument("--house-systems", default="", help="Comma-separated house system codes to compare (default: engine COMPARE_SYSTEMS).")
    parser.add_argument("--triplicity", default="", help="Doctrine override for report comparison: dorothean or ptolemaic.")
    parser.add_argument("--terms", default="", help="Doctrine override for report comparison: egyptian or ptolemaic.")
    
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)

    # Method-matrix mode: deterministic comparison across doctrine forks.
    if args.matrix:
        systems = [s.strip().upper() for s in (args.house_systems.split(",") if args.house_systems else []) if s.strip()]
        if not systems:
            systems = list(COMPARE_SYSTEMS)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = args.name.replace(" ", "_").lower()
        output_file = os.path.join(args.output_dir, f"{safe_name}_method_matrix_{timestamp}.md")
        report = build_method_matrix_report(
            name=args.name,
            date_str=args.date,
            time_str=args.time,
            city=args.city,
            state=args.state,
            latitude=args.lat,
            longitude=args.lon,
            house_systems=systems,
        )
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n✓ METHOD MATRIX COMPLETE\n  Output: {output_file}\n")
        return 0
    
    # Generate chart data
    # Generate chart data
    # If lat/lon are provided, bypass geocoding (useful when providers rate-limit).
    chart_data = generate_chart_data(
        args.name,
        args.date,
        args.time,
        args.city,
        args.state,
        latitude=args.lat,
        longitude=args.lon,
        triplicity_scheme=(args.triplicity or None),
        term_system=(args.terms or None),
    )
    if not chart_data:
        return 1
    
    
    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = args.name.replace(" ", "_").lower()
    output_file = os.path.join(args.output_dir, f"{safe_name}_premium_{timestamp}.md")
    
    # Run generation
    run_premium_report(chart_data, output_file, args.iterations)
    
    return 0


if __name__ == "__main__":
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.exit(main())
