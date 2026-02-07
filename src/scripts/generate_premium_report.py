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

# Setup paths
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "src"))

from src.engine.forensic_engine import Auditor
from src.engine.chat_oracle import _openrouter_request, _load_binder_context

BINDER_CONTEXT = _load_binder_context()


# =============================================================================
# THE $300-TIER SYSTEM PROMPT
# Based on Section 6 of the Research Document
# =============================================================================

PREMIUM_SYSTEM_PROMPT = """You are an expert Hellenistic and Medieval astrologer. You produce practitioner-grade **Forensic Structural Audits** that rival the $300 reports of Renaissance Astrology.

# THE MISSION (Forensic Audit)
You do not provide a "reading." You inspect the **structural integrity** of the nativity. Your goal is to find the **Cracks** (Debilities) and the **Supports** (Mitigations/Escape Hatches). This is a technical inspection, not a psychological profile.

# CORE CONSTRAINTS (INVIOLABLE)

1. **STRICT TRADITIONALISM**: 
   - Do NOT use modern psychological interpretations (e.g., "inner child", "evolutionary path", "healing journey")
   - Use DETERMINISTIC language: Fate, Fortune, Rank, Eminence, Circumstance, Decree
   - Avoid: "You might feel", "This suggests", "Could indicate"
   - Use: "This configuration INDICATES", "The chart DECREES", "Fate has determined"

2. **WHOLE SIGN HOUSES (STRICT)**:
   - All house analysis uses Whole Sign Houses exclusively
   - Quadrant house cusps (Placidus, Koch) are irrelevant for topic assignment

3. **SEPTENER ONLY**:
   - Base ALL primary judgments on the 7 visible planets (Sun through Saturn)
   - Outer planets (Uranus, Neptune, Pluto) may be mentioned as intense MODIFIERS only, never as rulers

4. **AUDITABILITY (Show Your Work)**:
   - CITE the astrological reason for EVERY judgment
   - Example: "Because Mars is in his Fall in Cancer AND out of sect in this Day Chart, his malefic nature is maximized..."
   - Reference traditional authors naturally: "As Valens teaches...", "Bonatti would classify this as..."

5. **NO FABRICATION**:
   - You may ONLY use data present in the chart JSON and the Binder1 reference material
   - If data is unavailable, state: "This information is not calculable from the provided data"
   - NEVER invent aspects, positions, or dignities

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

**MITIGATION_LOOP (The Escape Hatch Check):**
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

**Other Lots (same for both):**
- Lot of Eros = Ascendant + Spirit - Fortune
- Lot of Necessity = Ascendant + Fortune - Spirit
- Lot of Nemesis = Ascendant + Fortune - Saturn

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
  - `bloodletting` -> REPLACE with "vigorous physical exercise or red-colored foods"
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
- PRESCRIBE behavioral/dietary remediation for excess humors

## 3. SECT ANALYSIS
- Declare Day or Night chart
- Identify the "Benefic of Sect" and "Malefic of Sect"
- Explain how this alters ALL planetary interpretations

## 4. PLANETARY CABINET (All 7 Planets)
- For each planet: Sign, House, Dignity Score, Accidental Status, Cosmic State
- Judge whether the planet CAN deliver its promise
- Use metaphors: "The Treasurer", "The General", "The Minister of Health"

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
- Lot of Nemesis (Source of Ruin)

## 7. FIXED STARS
- Any conjunctions within 1° to major stars (Regulus, Spica, Algol, Sirius, Fomalhaut, etc.)
- These OVERRIDE planetary dignity – they are Force Majeure

## 8. TIME LORD ANALYSIS (Timing)
- Current ANNUAL PROFECTION (Age % 12 → Lord of the Year)
- Current FIRDARIA period and sub-period
- Current ZODIACAL RELEASING chapter (from Lot of Spirit)
- Synthesize: "The YEAR is ruled by X, the ERA is ruled by Y"

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
- PRESCRIBE preventative protocol (diet, lifestyle)

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

Use clear markdown headers. Each section should be substantial (400+ words for major sections). Aim for MAXIMUM VOLUME—this is a premium forensic dossier, not a summary. The client has paid $300; give them everything.

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

BEGIN THE FORENSIC STRUCTURAL AUDIT. AT LEAST 1,200 WORDS.
VOICE: SOBER REALIST. NO HYPERBOLE.

Start with the foundational elements of the life:
1. **Sect Determination**: Identify DAY or NIGHT. Tag Malefics:
   - IF Day: Saturn (Ally/Constructive); Mars (Adversary/Destructive).
   - IF Night: Mars (Ally/Constructive); Saturn (Adversary/Destructive).
2. **The Prenatal Syzygy (The Root)**: Identify the SAN, its degree, and phase.
3. **Doryphory (Spear-Bearers)**: Evaluate eminence and rank.
4. **MITIGATION LOOP (CRITICAL)**: Search for **Mutual Receptions** (e.g. Mars/Jupiter swap). If found, describe how this 'Escape Hatch' saves the nativity.
5. **Almuten Figuris (Soul Guardian)**: Calculate the Master.
6. **Temperament**: Determine the humoral mixture.

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
- Calculate and interpret: Lot of Eros, Lot of Necessity, Lot of Nemesis

**FIXED STARS:**
Identify any stars within 1° of planets or angles. These are FORCE MAJEURE.

Do NOT repeat previous material. Cover only what has not been addressed.""",

    # Iteration 4: Timing Analysis
    """Continue. Now analyze the CHRONOCRATORS (Time Lords).

**CURRENT TIMING:**
1. ANNUAL PROFECTION: What house? What Lord of the Year? That Lord's natal condition?
2. FIRDARIA: What Major Period? What Sub-Period? How do these Lords interact?
3. ZODIACAL RELEASING: What Level 1 chapter (from Lot of Spirit)? What Level 2?

**THE SYNTHESIS:**
- The YEAR is ruled by [X] who is [condition] = [forecast]
- The ERA is ruled by [Y] who is [condition] = [longer term pattern]
- Current pressure points and opportunities

Be SPECIFIC with ages and time ranges. Use the calculated data, not speculation.""",

    # Iteration 5: Past and Future
    """Continue. Now perform TEMPORAL FORENSICS.

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
- **INTERNAL CONSISTENCY**: Ensure diet advice doesn't conflict with Martian heat.

**REMEDIAL CODEX (Planetary Charity):**
- **SAFETY BLACKLIST ENFORCED**: NEVER suggest lead, mercury, or toxic metals.
- **REPLACEMENTS**: 
  - IF Saturn mitigation: Use **Onyx or Hematite**, or service to the elderly.
  - IF Mars/Blood: Use **Vigorous Exercise** or red foods.
- Focus on charitable acts (donations) and behavioral shifts.

**FINAL DECREE:**
- Give a sum total judgment on the **Structural Integrity** of this Life.
- Resolve all contradictions. End with a message of NAVIGATION.

DO NOT SUMMARIZE. DO NOT USE PLACEHOLDERS. COMPLETE LOGIC ONLY.""",
]


# =============================================================================
# MAIN GENERATION LOGIC
# =============================================================================

def generate_chart_data(name, date_str, time_str, city, state=None):
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
        house_system="W"  # Whole Sign Houses - STRICT
    )
    
    if not result or "error" in result:
        print(f"Engine Failure: {result.get('error', 'Unknown')}")
        return None
    
    # Combine all data for comprehensive LLM input
    combined_data = {
        "meta": result["technical_data"]["meta"],
        "astronomy": result["technical_data"]["astronomy"],
        "analysis": result["technical_data"]["analysis"],
        "human_translation": result["human_translation"]
    }
    
    chart_json = json.dumps(combined_data, indent=2, default=str)
    return chart_json


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
        r"(?i)\bbloodletting\b": "vigorous physical exercise",
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


def run_premium_report(chart_data, output_file, iterations=6):
    """Generate $300-tier premium report using research-backed methodology."""
    
    print(f"\n{'='*80}")
    print(f"PREMIUM REPORT GENERATION - CODEX CAELESTIS")
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
    
    final_report = f"""# PREMIUM FORENSIC STRUCTURAL AUDIT
## Inspection of the Nativity

---
**Generated by Codex Caelestis | traditional-astrology.com**
*Timestamp: {timestamp}*

---

"""
    for i, resp in enumerate(all_responses):
        final_report += f"# Part {i+1}\n\n{resp}\n\n---\n\n"
        
    # Apply Hard-Coded Safety Filters
    final_report = apply_safety_filters(final_report)
    
    # Add final educational disclaimer and footer
    final_report += "\n\n---\n"
    final_report += "### EDUCATIONAL NOTICE & METHODOLOGICAL LIMITS\n"
    final_report += "This report is rendered by the Codex Caelestis engine using rules from the Hellenistic and Medieval corpora. These results are for historical and spiritual research purposes only. Accuracy depends on precise birth data.\n\n"
    final_report += "© 2026 Codex Caelestis | [traditional-astrology.com](https://traditional-astrology.com)\n"
    
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
    parser.add_argument("--iterations", type=int, default=6, help="Number of iteration passes")
    parser.add_argument("--output-dir", default="premium_reports", help="Output directory")
    
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate chart data
    chart_data = generate_chart_data(args.name, args.date, args.time, args.city, args.state)
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
