#!/usr/bin/env python3
"""
Biographical Scoring Engine
============================
After mass_chart_runner.py generates deterministic readings for famous people,
this script scores how well each reading matches the subject's documented
biographical facts.

Scoring method: For each known biographical theme, search the deterministic
report text and structured claims for semantic matches. Produces a per-subject
accuracy score and a corpus-wide summary.

This is the DETERMINISTIC portion of the scoring. A later LLM-based scorer
can do deeper semantic matching, but this script catches the obvious hits
using keyword/phrase matching.

Usage:
    python scripts/score_readings.py
"""

import io
import json
import os
import re
import sys
from datetime import datetime
from typing import Any, Dict, List, Tuple

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer, encoding="utf-8", errors="replace"
    )

# =============================================================================
# THEME-TO-KEYWORD MAPPINGS
# =============================================================================
# For each common biographical theme type, what keywords in a reading
# would constitute a "hit"?

THEME_KEYWORDS = {
    # --- CAREER / VOCATION ---
    "politician": ["authority", "ruler", "command", "governance", "public", "reputation", "10th", "career", "action", "praxis", "rank"],
    "president": ["authority", "ruler", "command", "public", "supreme", "governance", "10th"],
    "musician": ["arts", "creative", "Venus", "5th", "pleasure", "performance", "beauty", "harmony"],
    "artist": ["arts", "creative", "Venus", "5th", "beauty", "aesthetic", "imagination"],
    "actress": ["arts", "creative", "Venus", "5th", "beauty", "public", "performance", "appearance"],
    "actor": ["arts", "creative", "Venus", "5th", "performance", "public", "appearance"],
    "scientist": ["Mercury", "intellectual", "study", "learning", "9th", "foreign", "philosophy", "mind"],
    "inventor": ["Mercury", "intellectual", "ingenuity", "innovation", "craftsmanship"],
    "writer": ["Mercury", "3rd", "communication", "letters", "writing", "intellectual"],
    "fighter": ["Mars", "combat", "contest", "warrior", "struggle", "athletics", "physical"],
    "boxer": ["Mars", "combat", "contest", "physical", "body", "struggle", "warrior"],
    "military": ["Mars", "combat", "warrior", "foreign", "9th", "struggle"],
    "revolutionary": ["Mars", "radical", "transformation", "8th", "death", "overthrow", "change"],
    "preacher": ["Jupiter", "9th", "religion", "God", "faith", "belief", "divination", "spiritual"],
    "media": ["Mercury", "3rd", "communication", "public", "10th", "reputation"],
    "technology": ["Mercury", "innovation", "craft", "ingenious", "mechanical"],
    "business": ["2nd", "wealth", "acquisition", "money", "livelihood", "Fortune"],
    "humanitarian": ["11th", "benefactor", "charity", "service", "good spirit"],
    "pilot": ["9th", "foreign", "long journey", "travel", "Mercury"],
    "activist": ["public", "10th", "radical", "change", "society"],

    # --- FAMILY ---
    "father absent": ["father", "4th", "disconnect", "alienation", "afflict", "malefic", "detriment", "fall"],
    "father difficult": ["father", "4th", "afflict", "malefic", "harsh", "abusive", "Saturn"],
    "mother close": ["mother", "10th", "benefic", "support", "nurture", "Moon"],
    "mother died": ["mother", "10th", "death", "8th", "loss", "grief"],
    "adopted": ["4th", "father", "origin", "ancestry", "disconnect"],
    "orphan": ["4th", "12th", "loss", "sorrow", "foundation", "disconnect"],
    "divorce parents": ["4th", "7th", "separation", "division", "alienation"],
    "siblings": ["3rd", "sibling", "brother", "sister", "neighbor"],

    # --- RELATIONSHIPS ---
    "marriage turbulent": ["7th", "marriage", "spouse", "afflict", "malefic", "difficulty", "contest"],
    "multiple marriages": ["7th", "marriage", "spouse", "Venus", "multiple"],
    "affairs": ["5th", "Venus", "pleasure", "sex", "desire"],
    "never married": ["7th", "celibacy", "isolation", "alone", "Saturn"],
    "power couple": ["7th", "marriage", "strong", "benefic", "mutual"],

    # --- HEALTH ---
    "addiction": ["6th", "illness", "sickness", "vice", "excess", "injury"],
    "substance abuse": ["6th", "illness", "vice", "excess", "poison", "sickness"],
    "depression": ["Saturn", "melancholic", "cold", "dry", "isolation", "sorrow", "12th"],
    "chronic illness": ["6th", "illness", "sickness", "body", "afflict", "Saturn"],
    "early death": ["8th", "death", "anareta", "short", "vitality", "destroy"],
    "violent death": ["8th", "death", "Mars", "malefic", "violent", "sudden"],
    "long life": ["vitality", "strong", "benefic", "hyleg", "protected"],
    "cancer": ["6th", "illness", "body", "deterioration"],

    # --- PERSONALITY ---
    "charismatic": ["1st", "benefic", "Jupiter", "Venus", "appearance", "vitality", "magnetism"],
    "perfectionist": ["Mercury", "Saturn", "detail", "craft", "exacting", "cold", "dry"],
    "paranoid": ["12th", "hidden", "enemy", "Saturn", "suspicious", "secret"],
    "secretive": ["12th", "hidden", "secret", "private", "occult"],
    "visionary": ["9th", "Jupiter", "philosophy", "belief", "imagination", "foreign"],
    "aggressive": ["Mars", "combative", "contest", "anger", "warrior"],
    "eccentric": ["unusual", "unconventional", "erratic", "independent"],
    "shy": ["12th", "hidden", "private", "isolation", "Saturn", "retreat"],
    "courageous": ["Mars", "1st", "vitality", "bold", "warrior", "contest"],
    "intellectual": ["Mercury", "mind", "intellectual", "study", "learning", "3rd", "9th"],
    "spiritual": ["9th", "Jupiter", "religion", "God", "faith", "divination", "Moon"],
    "ascetic": ["Saturn", "discipline", "restriction", "poverty", "denial"],
    "flamboyant": ["Venus", "Jupiter", "5th", "pleasure", "beauty", "display"],

    # --- LIFE EVENTS ---
    "assassination": ["8th", "death", "Mars", "violent", "sudden", "enemy"],
    "exile": ["12th", "foreign", "9th", "banishment", "loss", "separation"],
    "scandal": ["12th", "hidden", "enemy", "secret", "exposure", "shame"],
    "fame": ["10th", "reputation", "public", "rank", "prominent"],
    "poverty to wealth": ["2nd", "Fortune", "acquisition", "rise", "humble", "poverty"],
    "fall from grace": ["10th", "fall", "detriment", "loss", "disgrace"],
    "comeback": ["return", "revival", "restoration", "recovery"],
    "bullied": ["12th", "enemy", "Mars", "afflict", "sorrow", "hostile"],
}


def score_theme_against_report(
    theme: str, report_text: str, claims: List[Dict]
) -> Tuple[float, List[str]]:
    """
    Score a single biographical theme against a reading.
    Returns (score 0.0-1.0, list of matched keywords).
    """
    # Normalize the theme to find relevant keyword sets
    theme_lower = theme.lower()
    matched_keyword_sets = []

    for category, keywords in THEME_KEYWORDS.items():
        # Check if category appears in the theme text
        cat_words = category.lower().split()
        if any(w in theme_lower for w in cat_words):
            matched_keyword_sets.append((category, keywords))

    if not matched_keyword_sets:
        # Fallback: extract nouns from the theme itself as keywords
        words = re.findall(r"[a-z]+", theme_lower)
        stop_words = {"the", "a", "an", "and", "or", "in", "of", "at", "to", "was",
                      "is", "for", "with", "by", "from", "on", "as", "but", "not",
                      "his", "her", "their", "he", "she", "they", "it", "had", "has",
                      "been", "were", "who", "that", "this", "than", "age", "first"}
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        if keywords:
            matched_keyword_sets.append(("direct", keywords))

    if not matched_keyword_sets:
        return 0.0, []

    # Search the report text and claims for keyword hits
    report_lower = report_text.lower()
    claims_text = " ".join(
        c.get("claim", "") for c in claims if isinstance(c, dict)
    ).lower()
    combined_text = report_lower + " " + claims_text

    all_hits = []
    for category, keywords in matched_keyword_sets:
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in combined_text:
                all_hits.append(f"{kw} ({category})")

    if not all_hits:
        return 0.0, []

    # Score: proportion of keywords found (capped at 1.0)
    total_keywords = sum(len(kws) for _, kws in matched_keyword_sets)
    unique_hits = len(set(h.split(" (")[0] for h in all_hits))
    score = min(1.0, unique_hits / max(1, total_keywords) * 2)  # Scale up since partial matches are expected

    return score, list(set(all_hits))


def score_subject(
    name: str,
    report_text: str,
    claims: List[Dict],
    known_themes: List[str],
) -> Dict[str, Any]:
    """Score a complete subject's reading against known themes."""
    theme_scores = []
    for theme in known_themes:
        score, hits = score_theme_against_report(theme, report_text, claims)
        theme_scores.append({
            "theme": theme,
            "score": round(score, 3),
            "hits": hits,
            "hit_count": len(hits),
        })

    # Overall accuracy
    scores = [t["score"] for t in theme_scores]
    avg_score = sum(scores) / len(scores) if scores else 0
    themes_with_any_hit = sum(1 for s in scores if s > 0)
    hit_rate = themes_with_any_hit / len(scores) if scores else 0

    return {
        "name": name,
        "total_themes": len(known_themes),
        "themes_with_hits": themes_with_any_hit,
        "hit_rate": round(hit_rate, 3),
        "average_score": round(avg_score, 3),
        "theme_details": theme_scores,
    }


def main():
    mass_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "chart_outputs",
        "mass_test",
    )

    if not os.path.exists(mass_dir):
        print(f"ERROR: Mass test directory not found: {mass_dir}")
        print("Run mass_chart_runner.py first.")
        sys.exit(1)

    # Load answer key
    ak_path = os.path.join(mass_dir, "answer_key.json")
    if not os.path.exists(ak_path):
        print(f"ERROR: Answer key not found: {ak_path}")
        sys.exit(1)

    with open(ak_path, "r", encoding="utf-8") as f:
        answer_key = json.load(f)

    print("=" * 70)
    print("  BIOGRAPHICAL SCORING ENGINE")
    print(f"  Scoring {len(answer_key)} subjects")
    print("=" * 70)
    print()

    all_scores = []

    for name, ak_data in answer_key.items():
        slug = name.lower().replace(" ", "_").replace(".", "")
        report_path = os.path.join(mass_dir, f"{slug}_report.md")
        claims_path = os.path.join(mass_dir, f"{slug}_claims.json")

        if not os.path.exists(report_path):
            print(f"  SKIP: {name} (no report file)")
            continue

        # Load report
        with open(report_path, "r", encoding="utf-8") as f:
            report_text = f.read()

        # Load claims
        claims = []
        if os.path.exists(claims_path):
            with open(claims_path, "r", encoding="utf-8") as f:
                claims_data = json.load(f)
                claims = claims_data.get("engine_claims", [])

        known_themes = ak_data.get("known_themes", [])
        if not known_themes:
            print(f"  SKIP: {name} (no known themes)")
            continue

        result = score_subject(name, report_text, claims, known_themes)
        all_scores.append(result)
        rating = ak_data.get("rodden_rating", "?")

        indicator = "✓" if result["hit_rate"] >= 0.5 else "△" if result["hit_rate"] >= 0.3 else "✗"
        print(
            f"  {indicator} {name:30s} | "
            f"Hit Rate: {result['hit_rate']:.0%} "
            f"({result['themes_with_hits']}/{result['total_themes']}) | "
            f"Avg Score: {result['average_score']:.2f} | "
            f"Rodden: {rating}"
        )

    # Save detailed scores
    scores_path = os.path.join(mass_dir, "biographical_scores.json")
    with open(scores_path, "w", encoding="utf-8") as f:
        json.dump({
            "scored_at": datetime.now().isoformat(),
            "total_subjects": len(all_scores),
            "corpus_hit_rate": round(
                sum(s["hit_rate"] for s in all_scores) / len(all_scores), 3
            ) if all_scores else 0,
            "corpus_avg_score": round(
                sum(s["average_score"] for s in all_scores) / len(all_scores), 3
            ) if all_scores else 0,
            "subjects": all_scores,
        }, f, indent=2, default=str)

    # Summary
    if all_scores:
        avg_hit_rate = sum(s["hit_rate"] for s in all_scores) / len(all_scores)
        avg_score = sum(s["average_score"] for s in all_scores) / len(all_scores)

        print()
        print("=" * 70)
        print(f"  CORPUS SUMMARY ({len(all_scores)} subjects)")
        print(f"  Average Hit Rate: {avg_hit_rate:.1%}")
        print(f"  Average Score: {avg_score:.2f}")
        print(f"  Scores saved to: {scores_path}")
        print("=" * 70)

        # Leaderboard
        sorted_scores = sorted(all_scores, key=lambda x: x["hit_rate"], reverse=True)
        print()
        print("  TOP 5 (highest biographical match):")
        for s in sorted_scores[:5]:
            print(f"    {s['name']:30s} — {s['hit_rate']:.0%} ({s['themes_with_hits']}/{s['total_themes']})")
        print()
        print("  BOTTOM 5 (lowest biographical match):")
        for s in sorted_scores[-5:]:
            print(f"    {s['name']:30s} — {s['hit_rate']:.0%} ({s['themes_with_hits']}/{s['total_themes']})")


if __name__ == "__main__":
    main()
