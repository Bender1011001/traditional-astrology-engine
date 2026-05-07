"""
Blind Celebrity Astrology Test
================================
Calculates natal charts for famous individuals using the Auditor engine,
then strips ALL identifying information (name, date, time, location, coordinates,
timezone, Julian day) and presents only raw planetary placements to an LLM
for interpretation.

The goal: Can the astrological data alone produce personality/life-theme
descriptions that match these people -- without the LLM knowing who they are?

Usage:
    python scripts/blind_celeb_test.py
"""

import io
import json
import sys
import os
import hashlib
import random
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engine.forensic_engine import Auditor
from src.engine.calculations import format_longitude


# =============================================================================
# CELEBRITY BIRTH DATA (well-sourced from Astro-Databank)
# =============================================================================
# These are ONLY used for chart calculation — NONE of this goes to the LLM.

CELEBRITIES = {
    "Steve Jobs": {
        "date_str": "1955-02-24",
        "time_str": "19:15",
        "city": "San Francisco",
        "state": "California",
        "known_themes": [
            "Visionary technologist / industry disruptor",
            "Perfectionist with obsessive attention to design",
            "Mercurial temperament, charismatic but harsh",
            "Adopted, complex relationship with father/origins",
            "Health crisis (pancreatic cancer), early death at 56",
            "Built one of the most valuable companies in history",
            "Zen Buddhist spiritual seeker",
        ],
    },
    "Marilyn Monroe": {
        "date_str": "1926-06-01",
        "time_str": "09:30",
        "city": "Los Angeles",
        "state": "California",
        "known_themes": [
            "Iconic sex symbol / actress",
            "Deeply insecure beneath the glamorous surface",
            "Turbulent love life, multiple marriages",
            "Orphaned / foster care upbringing, absent father",
            "Substance abuse and mental health struggles",
            "Mysterious death at 36 (probable overdose)",
            "Extraordinary magnetism and public fascination",
        ],
    },
    "Richard Nixon": {
        "date_str": "1913-01-09",
        "time_str": "21:35",
        "city": "Yorba Linda",
        "state": "California",
        "known_themes": [
            "37th President of the United States",
            "Watergate scandal — resigned in disgrace",
            "Brilliant strategist, opened relations with China",
            "Paranoid, secretive, enemies-list mentality",
            "Working-class Quaker upbringing",
            "Complex relationship with power and authority",
            "Political comeback after devastating 1962 loss",
        ],
    },
}


def calculate_chart(celeb_data: dict) -> dict:
    """Run the full Auditor pipeline for a celebrity."""
    result = Auditor.generate_full_nativity(
        date_str=celeb_data["date_str"],
        time_str=celeb_data["time_str"],
        city=celeb_data["city"],
        state=celeb_data["state"],
        name="Subject",  # Generic name
    )
    if "error" in result:
        raise RuntimeError(f"Chart calculation failed: {result['error']}")
    return result


def sanitize_for_blind_test(result: dict) -> dict:
    """
    Extract ONLY the astrological content from a full Auditor result.
    Strips: name, date, time, location, coordinates, timezone, Julian day,
    generated_at timestamps, geocode metadata, UTC timestamps, age,
    analysis_date, and any other identifying information.
    """
    td = result["technical_data"]
    analysis = td.get("analysis", {})
    astronomy = td.get("astronomy", {})

    # --- PLANETARY PLACEMENTS (core data) ---
    planets_clean = {}
    raw_planets = astronomy.get("planets", {})
    for pname, pdata in raw_planets.items():
        # Skip outer planets and nodes for traditional focus, but include them
        # in a separate section so the LLM has full data
        lon = pdata.get("longitude", 0)
        planets_clean[pname] = {
            "sign": format_longitude(lon)["sign"],
            "degree": format_longitude(lon)["string"],
            "speed_deg_day": round(pdata.get("speed", 0), 4),
            "is_retrograde": pdata.get("is_retrograde", False),
        }
        # Add classical mechanics if available
        classical = pdata.get("classical", {})
        if classical.get("phasis"):
            planets_clean[pname]["phasis"] = classical["phasis"]
        if classical.get("kakosis"):
            planets_clean[pname]["kakosis"] = classical["kakosis"]

    # --- HOUSES ---
    houses_raw = astronomy.get("houses", {})
    houses_clean = {}
    for hnum, hlon in houses_raw.items():
        houses_clean[str(hnum)] = {
            "sign": format_longitude(hlon)["sign"],
            "degree": format_longitude(hlon)["string"],
        }

    # --- ANGLES ---
    angles_raw = astronomy.get("angles", {})
    angles_clean = {}
    for aname, alon in angles_raw.items():
        if alon is not None:
            angles_clean[aname] = {
                "sign": format_longitude(alon)["sign"],
                "degree": format_longitude(alon)["string"],
            }

    # --- SECT ---
    sect_data = analysis.get("sect", {})
    sect_clean = {
        "type": sect_data.get("type"),
        "note": sect_data.get("note"),
    }

    # --- DIGNITY SUMMARY ---
    dignity_raw = analysis.get("dignity", {})
    dignity_clean = {}
    if isinstance(dignity_raw, dict):
        # Extract planet-level dignity scores
        for key, val in dignity_raw.items():
            if key == "almuten":
                dignity_clean["almuten_figuris"] = val
            elif isinstance(val, dict):
                # Per-planet dignity breakdown
                dignity_clean[key] = val

    # --- TEMPERAMENT ---
    temperament = analysis.get("temperament", {})

    # --- ASPECTS (core septener only) ---
    aspects_core = analysis.get("aspects", [])

    # --- VITALITY (Hyleg/Alcochoden) ---
    vitality = analysis.get("vitality", {})

    # --- SYZYGY (prenatal) ---
    syzygy_raw = analysis.get("syzygy", {})
    syzygy_clean = {}
    if isinstance(syzygy_raw, dict):
        prenatal = syzygy_raw.get("prenatal_syzygy", {})
        if prenatal:
            syzygy_clean["prenatal_type"] = prenatal.get("type")
            syz_lon = prenatal.get("longitude")
            if syz_lon is not None:
                syzygy_clean["prenatal_degree"] = format_longitude(syz_lon)["string"]
            # Strip: jd_ut, datetime_utc (identifying)
        natal_phase = syzygy_raw.get("natal_phase", {})
        if natal_phase:
            syzygy_clean["natal_phase"] = {
                "moon_sun_elongation_deg": natal_phase.get("moon_sun_elongation_deg"),
                "is_waxing": natal_phase.get("is_waxing"),
            }

    # --- SUPPLEMENTAL ---
    supplemental = analysis.get("supplemental", {})
    supplemental_clean = {}
    if supplemental.get("lunar_mansion"):
        supplemental_clean["lunar_mansion"] = supplemental["lunar_mansion"]
    if supplemental.get("elements"):
        supplemental_clean["elemental_balance"] = supplemental["elements"]
    if supplemental.get("hemispheres"):
        supplemental_clean["hemispheres"] = supplemental["hemispheres"]
    # Stars (fixed star conjunctions)
    if supplemental.get("stars"):
        supplemental_clean["fixed_star_contacts"] = supplemental["stars"]

    # --- FORENSIC LOTS ---
    forensic_lots = analysis.get("forensic_lots", {})

    # --- TEAMS & RECEPTION ---
    teams = analysis.get("teams", {})

    # --- PLANETS FORENSIC (detailed per-planet analysis) ---
    planets_forensic = td.get("planets_forensic", [])
    # Strip any stray timestamps or location data from forensic entries
    pf_clean = []
    for pf in planets_forensic:
        if isinstance(pf, dict):
            cleaned = {k: v for k, v in pf.items()
                       if k not in ("jd", "julian_day", "datetime", "location")}
            pf_clean.append(cleaned)
        else:
            pf_clean.append(pf)

    # --- MEDICAL ---
    medical = analysis.get("medical", {})

    # --- ASSEMBLE BLIND PAYLOAD ---
    blind = {
        "planetary_placements": planets_clean,
        "houses": houses_clean,
        "angles": angles_clean,
        "sect": sect_clean,
        "dignity": dignity_clean,
        "temperament": temperament,
        "aspects": aspects_core,
        "vitality": vitality,
        "syzygy": syzygy_clean,
        "supplemental": supplemental_clean,
        "forensic_lots": forensic_lots,
        "teams_and_reception": teams,
        "planets_forensic": pf_clean,
        "medical": medical,
    }

    return blind


def build_llm_prompt(subjects: dict) -> str:
    """
    Build the prompt that goes to the LLM.
    Contains ONLY anonymized planetary data — no names, dates, or locations.
    """
    prompt_parts = [
        "# Blind Astrology Interpretation Test",
        "",
        "You are a master traditional astrologer trained in pre-1700s Hellenistic and",
        "Medieval techniques (Ptolemy, Valens, Bonatti, Lilly). You are given the complete",
        "natal chart data for three anonymous individuals, labeled Subject A, B, and C.",
        "",
        "## IMPORTANT CONSTRAINTS",
        "- You are given ONLY planetary placements, houses, aspects, dignities, and classical mechanics.",
        "- You do NOT know the birth date, time, location, or name of any subject.",
        "- You must NOT attempt to guess who these people are.",
        "- Provide your interpretation based SOLELY on the astrological data.",
        "",
        "## YOUR TASK",
        "For each subject, provide a detailed character analysis covering:",
        "1. **Core Temperament & Personality** — What kind of person is this?",
        "2. **Career/Vocation** — What fields or activities does the chart suggest?",
        "3. **Relationships & Family** — What patterns emerge?",
        "4. **Health & Vitality** — What does the vitality picture look like?",
        "5. **Major Life Themes** — What are the dominant narratives of this life?",
        "6. **Challenges & Shadow** — What are the chief difficulties?",
        "7. **Overall Arc** — If you had to summarize this life in 2-3 sentences, what would you say?",
        "",
        "Use traditional astrological reasoning. Cite specific placements and aspects.",
        "Be specific and bold — hedge less, interpret more.",
        "",
        "---",
        "",
    ]

    for label, data in subjects.items():
        prompt_parts.append(f"## {label}")
        prompt_parts.append("")
        prompt_parts.append("```json")
        prompt_parts.append(json.dumps(data, indent=2, default=str))
        prompt_parts.append("```")
        prompt_parts.append("")
        prompt_parts.append("---")
        prompt_parts.append("")

    return "\n".join(prompt_parts)


def main():
    # Force UTF-8 on Windows console
    import sys as _sys
    if _sys.stdout.encoding and _sys.stdout.encoding.lower() != 'utf-8':
        _sys.stdout = io.TextIOWrapper(_sys.stdout.buffer, encoding='utf-8', errors='replace')
        _sys.stderr = io.TextIOWrapper(_sys.stderr.buffer, encoding='utf-8', errors='replace')

    print("=" * 70)
    print("  BLIND CELEBRITY ASTROLOGY TEST")
    print("  Calculating charts with full Auditor pipeline...")
    print("=" * 70)
    print()

    # Randomize the order so the LLM can't guess based on position
    celeb_names = list(CELEBRITIES.keys())
    random.seed(42)  # Deterministic shuffle for reproducibility
    random.shuffle(celeb_names)

    labels = ["Subject A", "Subject B", "Subject C"]
    key_map = {}  # label -> real name (kept secret from the LLM)
    subjects = {}

    for i, name in enumerate(celeb_names):
        label = labels[i]
        key_map[label] = name
        celeb = CELEBRITIES[name]

        print(f"  [{label}] Calculating chart... ", end="", flush=True)
        result = calculate_chart(celeb)
        blind_data = sanitize_for_blind_test(result)
        subjects[label] = blind_data
        print("DONE")

        # Quick sanity check: ensure no identifying info leaked
        blind_json = json.dumps(blind_data, default=str)
        leaked_fields = []
        for forbidden in [celeb["date_str"], celeb["time_str"], celeb["city"],
                          name, str(celeb.get("latitude", "")),
                          str(celeb.get("longitude", ""))]:
            if forbidden and forbidden in blind_json:
                leaked_fields.append(forbidden)
        if leaked_fields:
            print(f"    ⚠️  WARNING: Possible data leak detected: {leaked_fields}")
        else:
            print(f"    ✓ No identifying data in blind payload")

    # Build the LLM prompt
    prompt = build_llm_prompt(subjects)

    # Save outputs
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              "chart_outputs", "blind_test")
    os.makedirs(output_dir, exist_ok=True)

    # 1. The prompt (what goes to the LLM)
    prompt_path = os.path.join(output_dir, "llm_prompt.md")
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(prompt)
    print(f"\n  ✓ LLM prompt saved to: {prompt_path}")

    # 2. The answer key (kept secret)
    answer_key_path = os.path.join(output_dir, "answer_key.json")
    answer_key = {
        "mapping": key_map,
        "known_themes": {label: CELEBRITIES[name]["known_themes"]
                         for label, name in key_map.items()},
        "note": "DO NOT share this file with the LLM. This is for human scoring only.",
    }
    with open(answer_key_path, "w", encoding="utf-8") as f:
        json.dump(answer_key, f, indent=2, default=str)
    print(f"  ✓ Answer key saved to: {answer_key_path}")

    # 3. Raw blind data (for debugging)
    raw_path = os.path.join(output_dir, "blind_data.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(subjects, f, indent=2, default=str)
    print(f"  ✓ Raw blind data saved to: {raw_path}")

    # Print the key map for the operator
    print()
    print("=" * 70)
    print("  ANSWER KEY (DO NOT SHARE WITH LLM)")
    print("=" * 70)
    for label, name in key_map.items():
        print(f"    {label} = {name}")
    print()
    print("  Next step: Feed llm_prompt.md to an LLM and compare its")
    print("  interpretation against the known_themes in answer_key.json")
    print("=" * 70)


if __name__ == "__main__":
    main()
