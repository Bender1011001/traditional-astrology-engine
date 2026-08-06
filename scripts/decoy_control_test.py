#!/usr/bin/env python3
"""
Decoy Permutation Control Test
==============================
Scores every precise-time celebrity's known biographical themes against:
  1. Their OWN astrological report (the diagonal)
  2. Every OTHER celebrity's report in the corpus (the off-diagonals)

This directly tests whether the 74.3% accuracy is a real astrological signal
(own-chart score > decoy-chart score) or pure interpretive elasticity / 
confirmation bias (own-chart score ≈ decoy-chart score).
"""

import json
import os
import sys
import random
from datetime import datetime
from typing import Dict, List, Tuple

# Re-use scoring logic from score_readings.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.score_readings import score_theme_against_report, score_subject

PRECISE_CELEBS = [
    "Steve Jobs", "Richard Nixon", "Abraham Lincoln", "Elvis Presley",
    "Muhammad Ali", "Donald Trump", "Kurt Cobain", "Michael Jackson",
    "Bruce Lee", "Amy Winehouse", "Princess Diana", "Queen Elizabeth II",
    "Napoleon Bonaparte", "Mahatma Gandhi", "Jimi Hendrix", "Theodore Roosevelt",
    "Che Guevara", "Carl Jung", "Walt Disney", "Janis Joplin",
    "Leonardo DiCaprio", "Lady Gaga"
]

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

    # Load all reports and claims
    loaded_data = {}
    for name in PRECISE_CELEBS:
        slug = name.lower().replace(" ", "_").replace(".", "")
        report_path = os.path.join(mass_dir, f"{slug}_report.md")
        claims_path = os.path.join(mass_dir, f"{slug}_claims.json")

        if not os.path.exists(report_path):
            print(f"ERROR: Missing report for {name} ({report_path})")
            continue

        with open(report_path, "r", encoding="utf-8") as f:
            report_text = f.read()

        claims = []
        if os.path.exists(claims_path):
            with open(claims_path, "r", encoding="utf-8") as f:
                claims_data = json.load(f)
                claims = claims_data.get("engine_claims", [])

        loaded_data[name] = {
            "report_text": report_text,
            "claims": claims,
            "known_themes": answer_key[name].get("known_themes", [])
        }

    valid_celebs = list(loaded_data.keys())
    n = len(valid_celebs)

    print("=" * 72)
    print("  DECOY PERMUTATION CONTROL TEST")
    print(f"  Cross-scoring {n} precise-time celebrities")
    print("=" * 72)
    print()

    # 22x22 Cross-Scoring Matrix
    # rows = biography (themes), cols = chart (report)
    matrix_hit_rate = []
    matrix_avg_score = []

    for i, row_name in enumerate(valid_celebs):
        row_rates = []
        row_scores = []
        themes = loaded_data[row_name]["known_themes"]

        for j, col_name in enumerate(valid_celebs):
            report_text = loaded_data[col_name]["report_text"]
            claims = loaded_data[col_name]["claims"]

            res = score_subject(row_name, report_text, claims, themes)
            row_rates.append(res["hit_rate"])
            row_scores.append(res["average_score"])

        matrix_hit_rate.append(row_rates)
        matrix_avg_score.append(row_scores)

    # Extract Diagonal (Own-Chart) and Off-Diagonal (Decoy) values
    own_rates = []
    decoy_rates = []
    own_scores = []
    decoy_scores = []

    print("  Subject-level details:")
    print(f"    {'Subject':25s} | Own Hit Rate | Decoy Hit Rate (Avg)")
    print("    " + "-" * 60)

    for i, name in enumerate(valid_celebs):
        o_rate = matrix_hit_rate[i][i]
        o_score = matrix_avg_score[i][i]
        own_rates.append(o_rate)
        own_scores.append(o_score)

        d_rate_vals = [matrix_hit_rate[i][j] for j in range(n) if j != i]
        d_score_vals = [matrix_avg_score[i][j] for j in range(n) if j != i]
        
        avg_d_rate = sum(d_rate_vals) / len(d_rate_vals)
        avg_d_score = sum(d_score_vals) / len(d_score_vals)
        
        decoy_rates.extend(d_rate_vals)
        decoy_scores.extend(d_score_vals)

        print(f"    {name:25s} | {o_rate:12.0%} | {avg_d_rate:19.1%}")

    mean_own_rate = sum(own_rates) / n
    mean_decoy_rate = sum(decoy_rates) / len(decoy_rates)
    mean_own_score = sum(own_scores) / n
    mean_decoy_score = sum(decoy_scores) / len(decoy_scores)

    # Permutation Test
    # Shuffle report columns across subjects N=10000 times, calculate shuffled own-chart rate
    random.seed(42)
    n_perms = 10000
    null_rates = []
    null_scores = []

    for _ in range(n_perms):
        col_indices = list(range(n))
        random.shuffle(col_indices)
        
        perm_rates = [matrix_hit_rate[i][col_indices[i]] for i in range(n)]
        perm_scores = [matrix_avg_score[i][col_indices[i]] for i in range(n)]
        
        null_rates.append(sum(perm_rates) / n)
        null_scores.append(sum(perm_scores) / n)

    # p-values
    p_value_rate = sum(1 for nr in null_rates if nr >= mean_own_rate) / n_perms
    p_value_score = sum(1 for ns in null_scores if ns >= mean_own_score) / n_perms

    print("\n" + "=" * 72)
    print("  SUMMARY RESULTS")
    print("=" * 72)
    print(f"  Metric             | Own-Chart  | Decoy-Chart | Diff    | p-value")
    print("  " + "-" * 68)
    print(f"  Average Hit Rate   | {mean_own_rate:10.1%} | {mean_decoy_rate:11.1%} | {mean_own_rate - mean_decoy_rate:+7.1%} | {p_value_rate:.4f}")
    print(f"  Average Match Score| {mean_own_score:10.3f} | {mean_decoy_score:11.3f} | {mean_own_score - mean_decoy_score:+7.3f} | {p_value_score:.4f}")
    
    verdict = "SIGNIFICANT (p < 0.05)" if p_value_rate < 0.05 else "NOT SIGNIFICANT (p >= 0.05)"
    print(f"\n  Verdict: {verdict}")
    print("=" * 72)

    # Save results
    results = {
        "run_timestamp": datetime.now().isoformat(),
        "total_subjects": n,
        "valid_subjects": valid_celebs,
        "own_chart": {
            "avg_hit_rate": mean_own_rate,
            "avg_match_score": mean_own_score,
            "subject_hit_rates": dict(zip(valid_celebs, own_rates)),
            "subject_match_scores": dict(zip(valid_celebs, own_scores))
        },
        "decoy_chart": {
            "avg_hit_rate": mean_decoy_rate,
            "avg_match_score": mean_decoy_score
        },
        "permutation_test": {
            "n_permutations": n_perms,
            "p_value_hit_rate": p_value_rate,
            "p_value_match_score": p_value_score
        },
        "matrix_hit_rate": matrix_hit_rate,
        "matrix_avg_score": matrix_avg_score
    }

    out_file = os.path.join(mass_dir, "decoy_control_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Detailed results saved to: {out_file}\n")

if __name__ == "__main__":
    main()
