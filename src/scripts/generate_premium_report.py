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

PREMIUM_SYSTEM_PROMPT = """You are an expert Hellenistic and Medieval astrologer in the lineage of Vettius Valens, Guido Bonatti, and William Lilly. You produce practitioner-grade forensic dossiers that rival the $300 reports of Renaissance Astrology and Medieval Astrology Guide.

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

BEGIN THE FORENSIC AUDIT.

Start with the foundational elements that determine everything else:
1. **Sect Determination**: Day or Night? Who are the benefic and malefic of sect?
2. **Almuten Figuris (Soul Guardian)**: Calculate and identify the Master of the Nativity
3. **Temperament**: Determine the humoral constitution (Choleric/Sanguine/Melancholic/Phlegmatic)
4. **Core Character Architecture**: What is the fundamental nature of this soul?

Remember: SHOW YOUR WORK. Cite the calculations. Use deterministic language. This is a $300 forensic audit.""",

    # Iteration 2: Planetary Cabinet
    """Continue the audit. Now dissect the PLANETARY CABINET.

For EACH of the 7 visible planets (Sun through Saturn), provide:
- Sign and House placement
- Essential Dignity score (Domicile +5, Exaltation +4, Triplicity +3, Term +2, Face +1)
- Accidental status (Angular/Succedent/Cadent, Combust, Retrograde)
- Cosmic state (Bonified? Maltreated? Besieged?)
- The planet's capacity to deliver its promise

Use metaphors: "The General is lame", "The Treasurer is bankrupt", "The Minister speaks with authority"

Do NOT repeat anything from Part 1. Go DEEP on each planet.""",

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

    # Iteration 6: Medical, Psychological, Remediation
    """FINAL ITERATION. Complete the audit with:

**MEDICAL ASTROLOGY (Melothesia):**
- Map the body parts to afflicted signs/houses
- Identify the primary health vulnerabilities
- The pathological mechanism (e.g., "Saturn constricts the head via Aries placement")
- PRESCRIBE preventative protocols

**PSYCHOLOGICAL PATTERNS (The Shadow):**
- What is the native's primary psychological trap?
- What pattern will they repeat until conscious of it?
- What is the "Hidden King" or repressed archetype?

**RELATIONSHIP DYNAMICS:**
- The 7th House configuration and what partner archetype is sought
- The Lot of Nemesis and where betrayal originates

**CAREER AND PUBLIC LIFE:**
- The 10th House and its ruler
- The "Praxis" planets (Mars, Venus, Mercury) and professional archetype

**THE PRESCRIPTION (Remediation):**
For each significantly afflicted planet, prescribe:
- Day for charitable acts
- Gemstone/metal
- Color associations
- Behavioral modification

**FINAL SYNTHESIS:**
Weave everything into a single, coherent narrative of this soul's fate, purpose, and destiny. What is the ultimate message of this chart?

This is the premium conclusion. Make it worthy of a $300 consultation."""
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


def run_premium_report(chart_data, output_file, iterations=6):
    """Generate $300-tier premium report using research-backed methodology."""
    
    print(f"\n{'='*80}")
    print(f"PREMIUM REPORT GENERATION")
    print(f"Methodology: Research-backed $300-tier synthesis")
    print(f"Iterations: {iterations}")
    print(f"{'='*80}\n")
    
    # Construct system prompt with Binder context
    system_prompt = PREMIUM_SYSTEM_PROMPT.format(binder_context=BINDER_CONTEXT)
    
    messages = [{"role": "system", "content": system_prompt}]
    all_responses = []
    
    for i, prompt_template in enumerate(ITERATION_PROMPTS[:iterations]):
        print(f"\nIteration {i+1}/{iterations}...")
        
        # Format the prompt with chart data
        prompt = prompt_template.format(chart_data=chart_data)
        messages.append({"role": "user", "content": prompt})
        
        response = _openrouter_request(
            messages=messages,
            temperature=0.15,  # Lower temp for more deterministic output
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
    
    final_report = f"""# PREMIUM ASTROLOGICAL DOSSIER
## Forensic Analysis of the Nativity

**Generated:** {timestamp}  
**Methodology:** Traditional Hellenistic-Medieval Synthesis  
**House System:** Whole Sign Houses (Strict)  
**Planetary Corpus:** Septener (Sun through Saturn)

---

"""
    
    for i, resp in enumerate(all_responses):
        final_report += f"# Part {i+1}\n\n{resp}\n\n---\n\n"
    
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
