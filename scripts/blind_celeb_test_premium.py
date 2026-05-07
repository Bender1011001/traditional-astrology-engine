#!/usr/bin/env python3
import re
"""
Blind Celebrity Astrology Test — Premium Report Edition
==========================================================
Uses the production premium report generator (OpenRouter) to produce full
practitioner-grade readings for three anonymized celebrities.

The LLM receives the complete astrological data (planets, houses, aspects,
dignities, lots, vitality, time lords, mundane context) but NEVER sees:
  - The subject's name
  - Birth date, time, or location
  - Coordinates, timezone, Julian day, or UTC timestamp
  - Any age or analysis_date that could anchor the birth year

After all three reports are generated, the answer key is revealed so a human
can score each reading against documented biographical themes.

Usage:
    python scripts/blind_celeb_test_premium.py
"""
import io
import json
import os
import random
import sys
from datetime import datetime
from typing import Any, Dict

# Force UTF-8 on Windows console before any other output
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Reuse the premium report machinery directly
from src.scripts.generate_premium_report import (
    BINDER_CONTEXT,
    ITERATION_PROMPTS,
    PLANETARY_CHARITY_DISCLAIMER,
    PREMIUM_SYSTEM_PROMPT,
    apply_safety_filters,
    build_raw_data_appendix,
    generate_chart_data,
)
from src.engine.chat_oracle import _openrouter_request


# =============================================================================
# CELEBRITY BIRTH DATA — sourced from Astro-Databank
# These are ONLY used for chart calculation. Nothing goes to the LLM.
# =============================================================================

CELEBRITIES = {
    "Steve Jobs": {
        "date_str": "1955-02-24",
        "time_str": "19:15",
        "city": "San Francisco",
        "state": "California",
        "known_themes": [
            "Visionary technologist / industry disruptor",
            "Perfectionist with obsessive attention to design aesthetics",
            "Mercurial temperament — charismatic but harsh and exacting",
            "Adopted; complex, estranged relationship with biological father",
            "Pancreatic cancer diagnosis; died at 56",
            "Built one of the most valuable companies in human history",
            "Zen Buddhist, spiritual seeker, LSD experimentation in youth",
            "Reality distortion field — extraordinary persuasive power",
        ],
    },
    "Marilyn Monroe": {
        "date_str": "1926-06-01",
        "time_str": "09:30",
        "city": "Los Angeles",
        "state": "California",
        "known_themes": [
            "Iconic global sex symbol and actress",
            "Profound insecurity beneath a luminous, magnetic surface",
            "Turbulent love life, three marriages, many affairs",
            "Orphaned and raised in foster care; father unknown/absent",
            "Barbiturate and alcohol dependency; severe mental health struggles",
            "Mysterious death at age 36 — probable overdose",
            "Extraordinary public magnetism; became a cultural archetype",
            "Desired to be taken seriously as a dramatic actress",
        ],
    },
    "Richard Nixon": {
        "date_str": "1913-01-09",
        "time_str": "21:35",
        "city": "Yorba Linda",
        "state": "California",
        "known_themes": [
            "37th President of the United States",
            "Watergate scandal — first president to resign in disgrace",
            "Brilliant geopolitical strategist; opened diplomatic relations with China",
            "Paranoid, secretive personality; maintained an enemies list",
            "Humble working-class Quaker upbringing; driven by class resentment",
            "Complex, tormented relationship with power and authority",
            "Extraordinary political comeback after crushing 1962 defeat",
            "Survived multiple career-ending crises before the final fall",
        ],
    },
}


# =============================================================================
# SANITIZER — strips all identifying metadata from the chart JSON
# =============================================================================

FORBIDDEN_META_KEYS = {
    "subject_name", "generated_at", "analysis_date", "julian_day", "age",
    "birth_date", "birth_time", "city", "state", "lat", "lon", "timezone",
    "tz_abbrev", "utc_offset_hours", "dst_offset_hours", "utc_time",
    "geocode", "date", "time",
}

FORBIDDEN_CHART_KEYS = {
    "date", "time", "city", "state", "lat", "lon", "timezone",
    "tz_abbrev", "utc_offset_hours", "dst_offset_hours", "utc_time",
    "geocode", "julian_day",
}

# Fields inside planets_forensic / analysis that might expose year via JD
FORENSIC_STRIP_KEYS = {"jd", "julian_day", "datetime", "location", "utc_time"}


def _deep_strip_jd(obj: Any) -> Any:
    """Recursively remove any dict key that looks like it encodes a timestamp."""
    if isinstance(obj, dict):
        return {
            k: _deep_strip_jd(v)
            for k, v in obj.items()
            if k not in FORENSIC_STRIP_KEYS
        }
    if isinstance(obj, list):
        return [_deep_strip_jd(item) for item in obj]
    return obj


def _strip_syzygy_dates(syzygy: Any) -> Any:
    """Remove datetime_utc fields from syzygy (they contain the birth year)."""
    if not isinstance(syzygy, dict):
        return syzygy
    out = {}
    for k, v in syzygy.items():
        if k == "datetime_utc":
            continue  # drops birth-anchored UTC timestamps
        if k == "jd_ut":
            continue  # Julian day uniquely identifies the birth moment
        if isinstance(v, dict):
            out[k] = _strip_syzygy_dates(v)
        else:
            out[k] = v
    return out


# Matches ISO-8601 dates like 1926-06-01 or 1926-06-01T09:30:00
_ISO_DATE_RE = re.compile(r'\d{4}-\d{2}-\d{2}(?:T[\d:+Z.]+)?')


def sanitize_chart_json(chart_json_str: str, label: str, birth_year: str) -> str:
    """
    Parse the full chart JSON, strip all identifying information, inject
    the anonymized label, and return a clean JSON string for the LLM.
    """
    data = json.loads(chart_json_str)

    # --- Strip meta entirely, replace with anonymous label ---
    data["meta"] = {
        "subject_label": label,
        "note": (
            "Birth data has been redacted for blind interpretation. "
            "The astrologer must not attempt to identify this individual."
        ),
        # Preserve house system and zodiac system (astrologically relevant, not identifying)
        "house_system": (data.get("meta", {}).get("chart", {}) or {}).get("house_system"),
        "zodiac_system": (data.get("meta", {}).get("chart", {}) or {}).get("zodiac_system"),
    }

    # --- Strip syzygy dates from analysis ---
    analysis = data.get("analysis", {})
    if "syzygy" in analysis:
        analysis["syzygy"] = _strip_syzygy_dates(analysis["syzygy"])

    # --- Strip JD / timestamps from planets_forensic ---
    if "planets_forensic" in analysis:
        analysis["planets_forensic"] = _deep_strip_jd(analysis["planets_forensic"])

    # --- Strip JD / timestamps from advanced_mechanics ---
    if "advanced_mechanics" in analysis:
        analysis["advanced_mechanics"] = _deep_strip_jd(analysis["advanced_mechanics"])

    # --- Strip age and analysis_date (they anchor the birth year) ---
    for strip_key in ("age", "analysis_date"):
        analysis.pop(strip_key, None)

    # --- Strip enhanced_profections age references ---
    ep = analysis.get("enhanced_profections", {})
    if isinstance(ep, dict):
        ep.pop("age", None)
        ep.pop("current_year", None)
        ep.pop("birth_year", None)

    data["analysis"] = analysis

    # --- Strip human_translation (often references name/date in prose) ---
    data.pop("human_translation", None)

    raw = json.dumps(data, indent=2, default=str)

    # Belt-and-suspenders: replace any ISO date that starts with the birth year
    def _redact_date(m: re.Match) -> str:
        if m.group(0).startswith(birth_year):
            return '[REDACTED-DATE]'
        return m.group(0)

    sanitized = _ISO_DATE_RE.sub(_redact_date, raw)
    return sanitized


def verify_no_leak(blind_json: str, celeb: Dict) -> list:
    """Check that no identifying strings appear in the blind JSON."""
    forbidden_strings = [
        celeb["date_str"],
        celeb["time_str"],
        celeb["city"],
        celeb["state"][:4],  # partial match
        celeb["date_str"][:4],  # birth year alone
    ]
    found = [s for s in forbidden_strings if s in blind_json]
    return found


# =============================================================================
# BLIND REPORT RUNNER — wraps run_premium_report with sanitized data
# =============================================================================

BLIND_SYSTEM_PROMPT_PREFIX = """
# BLIND INTERPRETATION PROTOCOL

This is a BLIND astrological assessment. The birth data (date, time, location, name) has been
redacted. You are given only the astrological structure.

CRITICAL RULES:
- You MUST NOT attempt to identify, guess, or speculate about who this person is.
- Do NOT use phrases like "this chart resembles..." or name any historical figure.
- Treat the subject as "this native" or use the label provided in `meta.subject_label`.
- Provide a full, authoritative reading based solely on the astrological data.
- All other rules in your system prompt apply unchanged.

---
"""


def run_blind_premium_report(
    blind_chart_json: str,
    label: str,
    output_file: str,
    iterations: int = 6,
) -> str:
    """
    Drive the premium report generator with anonymized data.
    Identical to run_premium_report() but:
    - Prepends the blind protocol notice to the system prompt
    - Omits the birth_header from the final document
    - Uses the anonymized label as the document title
    """
    truncated_binder = BINDER_CONTEXT[:50000] if BINDER_CONTEXT else ""
    system_prompt = (
        BLIND_SYSTEM_PROMPT_PREFIX
        + PREMIUM_SYSTEM_PROMPT.format(binder_context=truncated_binder)
    )

    # Override iteration 1's birth-header instruction with a blind-safe version
    blind_iteration_1 = ITERATION_PROMPTS[0].replace(
        "Start with the foundational elements of the life:",
        "Start with the foundational elements of the nativity (do not reference or invent birth details):",
    ).replace(
        "- Birth: cite `meta.chart.date`, `meta.chart.time`, `meta.chart.city`, `meta.chart.state`",
        "- Subject Label: cite `meta.subject_label` only. Do NOT reference any date, time, or location.",
    ).replace(
        "- Coordinates used: cite `meta.chart.lat`, `meta.chart.lon`, and `meta.chart.geocode.source` (if present)",
        "  (Coordinates have been redacted — omit this line.)",
    )

    blind_prompts = [blind_iteration_1] + list(ITERATION_PROMPTS[1:])

    messages = [{"role": "system", "content": system_prompt}]
    all_responses = []

    for i, prompt_template in enumerate(blind_prompts[:iterations]):
        print(f"    Iteration {i+1}/{iterations}...", end=" ", flush=True)

        try:
            prompt = prompt_template.format(chart_data=blind_chart_json)
        except KeyError:
            # Some iteration prompts don't have {chart_data}
            prompt = prompt_template

        messages.append({"role": "user", "content": prompt})

        response = _openrouter_request(
            messages=messages, temperature=0.15, max_tokens=16000, top_p=0.9
        )

        if (
            not response
            or response.startswith("Error:")
            or response.startswith("Oracle Communication Error")
        ):
            print(f"ERROR: {(response or 'No response')[:120]}")
            break

        all_responses.append(response)
        messages.append({"role": "assistant", "content": response})
        word_count = len(response.split())
        print(f"{word_count:,} words")

    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    final_report = f"""# BLIND NATAL CHART READING — {label}
## Forensic Inspection of an Anonymous Nativity

---
**Generated by Traditional Astrology Engine**
*Timestamp: {timestamp}*
*Protocol: BLIND — birth data redacted*

---

"""
    final_report += build_raw_data_appendix(blind_chart_json)

    for i, resp in enumerate(all_responses):
        final_report += f"# Part {i+1}\n\n{resp}\n\n---\n\n"

    final_report = apply_safety_filters(final_report)

    final_report += "\n\n---\n"
    final_report += "### BLIND TEST NOTICE\n"
    final_report += (
        "This reading was generated without knowledge of birth date, time, location, or identity. "
        "It is part of a blind validation study of traditional astrological technique. "
        "For historical and spiritual research purposes only.\n\n"
    )
    final_report += PLANETARY_CHARITY_DISCLAIMER

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_report)

    total_words = len(final_report.split())
    print(f"    Report saved: {output_file} ({total_words:,} words)")
    return final_report


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 70)
    print("  BLIND CELEBRITY ASTROLOGY TEST — PREMIUM REPORT EDITION")
    print("=" * 70)
    print()

    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "chart_outputs", "blind_test"
    )
    os.makedirs(output_dir, exist_ok=True)

    # Randomize order — LLM can't guess by position
    celeb_names = list(CELEBRITIES.keys())
    random.seed(42)
    random.shuffle(celeb_names)

    labels = ["Subject A", "Subject B", "Subject C"]
    key_map = {}
    all_reports = {}

    for i, name in enumerate(celeb_names):
        label = labels[i]
        key_map[label] = name
        celeb = CELEBRITIES[name]

        print(f"\n[{label}] = {name} (identity hidden from LLM)")
        print(f"  Step 1: Calculating chart via Auditor...")

        # Step 1: Full chart via premium generator
        raw_chart_json = generate_chart_data(
            name="Subject",  # Generic — will be stripped anyway
            date_str=celeb["date_str"],
            time_str=celeb["time_str"],
            city=celeb["city"],
            state=celeb["state"],
        )

        if not raw_chart_json:
            print(f"  ERROR: Chart calculation failed for {name}")
            continue

        print(f"  Step 2: Sanitizing — stripping all identifying data...")

        # Step 2: Sanitize
        birth_year = celeb["date_str"][:4]
        blind_json = sanitize_chart_json(raw_chart_json, label, birth_year)

        # Leak verification
        leaks = verify_no_leak(blind_json, celeb)
        if leaks:
            print(f"  WARNING — leaked fields detected: {leaks}")
        else:
            print(f"  Verification passed — no identifying data in payload")

        # Save the blind payload for auditing
        blind_data_path = os.path.join(output_dir, f"{label.lower().replace(' ', '_')}_blind_payload.json")
        with open(blind_data_path, "w", encoding="utf-8") as f:
            f.write(blind_json)

        print(f"  Step 3: Running premium LLM interpretation (6 iterations)...")

        # Step 3: Run premium report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_label = label.lower().replace(" ", "_")
        output_file = os.path.join(output_dir, f"{safe_label}_premium_reading_{timestamp}.md")

        report = run_blind_premium_report(
            blind_chart_json=blind_json,
            label=label,
            output_file=output_file,
            iterations=6,
        )
        all_reports[label] = {
            "output_file": output_file,
            "word_count": len(report.split()),
        }

    # Save answer key
    answer_key = {
        "mapping": key_map,
        "known_themes": {
            label: CELEBRITIES[name]["known_themes"]
            for label, name in key_map.items()
        },
        "report_files": all_reports,
        "note": "DO NOT share this file with the LLM. For human scoring only.",
        "generated_at": datetime.now().isoformat(),
    }
    answer_key_path = os.path.join(output_dir, "answer_key.json")
    with open(answer_key_path, "w", encoding="utf-8") as f:
        json.dump(answer_key, f, indent=2, default=str)

    print()
    print("=" * 70)
    print("  COMPLETE")
    print("=" * 70)
    print()
    print("  ANSWER KEY (the blind):")
    for label, name in key_map.items():
        rpt = all_reports.get(label, {})
        print(f"    {label} = {name}  [{rpt.get('word_count', '?'):,} words]")
    print()
    print(f"  Answer key: {answer_key_path}")
    print(f"  Reports:    {output_dir}")
    print()
    print("  Next step: read each *_premium_reading_*.md without looking at")
    print("  the answer key and score the LLM's themes against known_themes.")
    print("=" * 70)


if __name__ == "__main__":
    main()
