#!/usr/bin/env python3
"""
Double-Blind Astrological Matching Test
======================================
Implements a 2-Alternative Forced-Choice (2-AFC) test. For each precise-time
celebrity, we present a blinded LLM judge with:
  1. The known biographical themes of the subject.
  2. Two anonymized astrological readings (Reading A and Reading B), where
     one is the actual reading and the other is a randomly selected decoy reading.
     Both readings have all references to the subject's and decoy's names replaced
     with "[The Native]" and headers stripped.

The LLM judge must decide which reading matches the biography better. We compute
the overall hit rate and the exact binomial p-value against the 50% null expectation.
"""

import json
import os
import sys
import re
import random
import math
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, List, Tuple, Any

PRECISE_CELEBS = [
    "Steve Jobs", "Richard Nixon", "Abraham Lincoln", "Elvis Presley",
    "Muhammad Ali", "Donald Trump", "Kurt Cobain", "Michael Jackson",
    "Bruce Lee", "Amy Winehouse", "Princess Diana", "Queen Elizabeth II",
    "Napoleon Bonaparte", "Mahatma Gandhi", "Jimi Hendrix", "Theodore Roosevelt",
    "Che Guevara", "Carl Jung", "Walt Disney", "Janis Joplin",
    "Leonardo DiCaprio", "Lady Gaga"
]

def anonymize_text(text: str, name: str, decoy_name: str) -> str:
    """Strips headers, truncates timing/remediation/special sections, strips blockquotes,
    and replaces all occurrences of subject and decoy names with [The Native]."""
    # 1. Strip the header lines (first 5 lines usually contain metadata)
    lines = text.splitlines()
    header_end = 0
    for idx, line in enumerate(lines[:10]):
        if "---" in line:
            header_end = idx + 1
            break
    if header_end > 0:
        lines = lines[header_end:]
    
    # 2. Filter and truncate at timing/remediation/special sections
    filtered_lines = []
    for line in lines:
        stripped = line.strip()
        # Truncate at timing, remediation, or special techniques to save tokens
        if (line.startswith("## VII.") or 
            line.startswith("## VI.") or 
            line.startswith("## VIII.") or 
            line.startswith("## IX.") or 
            "TIMING" in line.upper() or 
            "REMEDIATION" in line.upper() or 
            "SPECIAL" in line.upper()):
            break
        # Skip blockquotes
        if stripped.startswith(">"):
            continue
        filtered_lines.append(line)
        
    clean_text = "\n".join(filtered_lines)
    
    # 3. Gather name variations for both names
    names_to_anonymize = [name, decoy_name]
    variants = set()
    for n in names_to_anonymize:
        parts = n.split()
        variants.add(n)
        variants.add(n.lower())
        variants.add(n.upper())
        for part in parts:
            p = part.replace(".", "").replace(",", "").strip()
            if p and len(p) > 2:
                variants.add(p)
                variants.add(p.lower())
                variants.add(p.upper())
                variants.add(p.capitalize())
                
    # Sort by length descending to avoid partial replacements
    sorted_variants = sorted(list(variants), key=len, reverse=True)
    
    # Replace all with [The Native]
    for variant in sorted_variants:
        pattern = r'\b' + re.escape(variant) + r'\b'
        clean_text = re.sub(pattern, "[The Native]", clean_text)
        
    return clean_text

def call_openrouter_direct(messages: List[Dict[str, str]]) -> str:
    """Sends request to DeepSeek directly, using deepseek-chat."""
    api_key = (os.environ.get("DEEPSEEK_API_KEY") or "").strip()
    if not api_key:
        return "Error: DEEPSEEK_API_KEY environment variable not found."

    base_url = "https://api.deepseek.com/chat/completions"
    model = "deepseek-chat"
    timeout = 120.0

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 400
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(base_url, data=data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            result = json.loads(raw)
            
        choices = result.get("choices", [])
        if not choices:
            return f"Error: No choices in response. Full result: {result}"
            
        message = choices[0].get("message", {}) or {}
        content = message.get("content", "")
        return str(content).strip()
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8")
            detail = json.loads(body)
            msg = detail.get("error", {}).get("message", body)
        except Exception:
            msg = str(e)
        return f"DeepSeek Communication Error: {msg}"
    except Exception as e:
        return f"DeepSeek Communication Error: {str(e)}"

def parse_llm_json(response_text: str) -> dict:
    """Parse JSON response from LLM robustly, handling markdown blocks and fallback matching."""
    text = response_text.strip()
    if text.startswith("```"):
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline:]
        if text.endswith("```"):
            text = text[:-3]
    text = text.strip()
    try:
        return json.loads(text)
    except Exception as e:
        # Fallback regex parsing if JSON is slightly malformed
        decision_match = re.search(r'"decision"\s*:\s*"Reading\s+([AB])"', text, re.IGNORECASE)
        decision = f"Reading {decision_match.group(1).upper()}" if decision_match else None
        confidence_match = re.search(r'"confidence"\s*:\s*(\d+)', text)
        confidence = int(confidence_match.group(1)) if confidence_match else 5
        return {
            "analysis_reading_a": "Regex parse fallback",
            "analysis_reading_b": "Regex parse fallback",
            "decision": decision,
            "confidence": confidence,
            "raw_response": response_text
        }

def binomial_p_value(n: int, k: int) -> float:
    """Probability of getting >= k successes out of n trials with p=0.5 (one-sided)."""
    if k == 0:
        return 1.0
    p_val = 0.0
    for i in range(k, n + 1):
        p_val += math.comb(n, i) * (0.5 ** n)
    return p_val

def main():
    mass_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "chart_outputs", "mass_test"
    )

    # Load answer key
    ak_path = os.path.join(mass_dir, "answer_key.json")
    if not os.path.exists(ak_path):
        print(f"ERROR: Answer key not found: {ak_path}")
        sys.exit(1)

    with open(ak_path, "r", encoding="utf-8") as f:
        answer_key = json.load(f)

    # Load all reports
    reports = {}
    for name in PRECISE_CELEBS:
        slug = name.lower().replace(" ", "_").replace(".", "")
        report_path = os.path.join(mass_dir, f"{slug}_report.md")
        if not os.path.exists(report_path):
            print(f"ERROR: Missing report for {name} ({report_path})")
            continue
        with open(report_path, "r", encoding="utf-8") as f:
            reports[name] = f.read()

    valid_names = list(reports.keys())
    n_trials = len(valid_names)

    # Ensure deterministic shuffling for reproducibility
    random.seed(42)

    print("=" * 72)
    print("  DOUBLE-BLIND ASTROLOGICAL MATCHING TEST")
    print(f"  Evaluating {n_trials} precise-time celebrities (2-AFC design)")
    print("=" * 72)
    print()

    results_log = []
    correct_count = 0

    for idx, name in enumerate(valid_names):
        print(f"[{idx+1}/{n_trials}] Testing {name}...", end="", flush=True)

        # Get biography themes
        themes = answer_key[name].get("known_themes", [])
        themes_text = "\n".join(f"- {t}" for t in themes)

        # Choose decoy
        decoy_name = random.choice([c for c in valid_names if c != name])

        # Anonymize readings
        true_anon = anonymize_text(reports[name], name, decoy_name)
        decoy_anon = anonymize_text(reports[decoy_name], decoy_name, name)

        # Assign A and B randomly
        assign_true_to_a = random.choice([True, False])
        if assign_true_to_a:
            reading_a = true_anon
            reading_b = decoy_anon
            true_label = "Reading A"
        else:
            reading_a = decoy_anon
            reading_b = true_anon
            true_label = "Reading B"

        # Construct LLM prompt
        prompt = f"""You are a blinded scientific auditor. You are participating in a double-blind validation test of traditional astrology.

Your task is to match a set of documented life themes (the biography of an anonymous individual) against two anonymized natal astrological reports: "Reading A" and "Reading B".
One of these readings is the actual natal report of the subject; the other is a decoy (a report of a completely different person).

# Subject Biography (Known Life Themes):
{themes_text}

# Reading A:
{reading_a}

# Reading B:
{reading_b}

# Instructions:
Analyze the alignments in both Reading A and Reading B against the Subject Biography.
You must choose which reading is the true natal report of the subject.

Your response must be in valid JSON format, with the keys ordered exactly as follows:
{{
  "decision": "Reading A" or "Reading B",
  "confidence": 1-10,
  "analysis_reading_a": "A 1-sentence analysis of why Reading A matches or does not match.",
  "analysis_reading_b": "A 1-sentence analysis of why Reading B matches or does not match."
}}
Ensure the JSON keys are generated in this exact order. Keep the analysis extremely brief (exactly 1 sentence per reading) to prevent truncation. Do not include markdown formatting or wrapper tags other than standard JSON.
"""

        messages = [
            {"role": "system", "content": "You are a precise, scientific, double-blind study evaluator. Output valid JSON only."},
            {"role": "user", "content": prompt}
        ]

        # Call OpenRouter directly
        raw_response = call_openrouter_direct(messages)

        # Parse decision
        parsed = parse_llm_json(raw_response)
        decision = parsed.get("decision")
        confidence = parsed.get("confidence", 5)
        analysis_a = parsed.get("analysis_reading_a", "")
        analysis_b = parsed.get("analysis_reading_b", "")

        is_correct = (decision == true_label)
        if is_correct:
            correct_count += 1
            status_str = "CORRECT"
        else:
            status_str = "INCORRECT"

        print(f" -> {status_str} (Choice: {decision}, True: {true_label}, Confidence: {confidence})")

        results_log.append({
            "subject": name,
            "decoy": decoy_name,
            "true_label": true_label,
            "decision": decision,
            "is_correct": is_correct,
            "confidence": confidence,
            "analysis_reading_a": analysis_a,
            "analysis_reading_b": analysis_b,
            "raw_response": raw_response if "raw_response" in parsed or raw_response.startswith("Oracle") or raw_response.startswith("Error") else None
        })

    # Summary Stats
    hit_rate = correct_count / n_trials
    p_val = binomial_p_value(n_trials, correct_count)
    is_significant = (p_val < 0.05)

    print("\n" + "=" * 72)
    print("  DOUBLE-BLIND TEST SUMMARY")
    print("=" * 72)
    print(f"  Total Trials:   {n_trials}")
    print(f"  Correct:        {correct_count}")
    print(f"  Incorrect:      {n_trials - correct_count}")
    print(f"  Hit Rate:       {hit_rate:.1%}")
    print(f"  Binomial p-val: {p_val:.4f}")
    print(f"  Significant:    {is_significant}")
    print("=" * 72)

    # Save to disk
    out_file = os.path.join(mass_dir, "double_blind_results.json")
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_trials": n_trials,
        "correct": correct_count,
        "hit_rate": hit_rate,
        "binomial_p_value": p_val,
        "is_significant": is_significant,
        "details": results_log
    }
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved raw test results to: {out_file}\n")

if __name__ == "__main__":
    main()
