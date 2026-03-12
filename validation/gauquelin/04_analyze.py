"""
04_analyze.py - Statistical analysis of Gauquelin validation results.

Merges results_raw.json with subjects_occupation.json by id, then runs
full statistical analysis on all variables across occupational groups.

REQUIRES hypotheses_locked.json (from 03_lock_hypotheses.py) to exist.

Output: full_results.json

Analysis performed:
  - ANOVA (F-stat, p-value) for all continuous variables across groups
  - Chi-square for all categorical variables across groups
  - Cohen d for each H1-H5 pairwise comparison
  - Cramer V for categorical hypotheses
  - Underpowered group flags (n < 30)
  - Hypothesis verdict: SUPPORTED / NOT SUPPORTED / INCONCLUSIVE

Usage: python 04_analyze.py --out-dir ./output
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore", category=RuntimeWarning)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data loading and flattening
# ---------------------------------------------------------------------------

def load_and_merge(out_dir: Path) -> pd.DataFrame:
    """
    Load results_raw.json and subjects_occupation.json, merge by id.

    This is the ONLY place where occupation data is joined to results.
    It must be called only after hypotheses_locked.json exists.
    """
    results_path = out_dir / "results_raw.json"
    occ_path     = out_dir / "subjects_occupation.json"
    lock_path    = out_dir / "hypotheses_locked.json"

    if not lock_path.exists():
        raise FileNotFoundError(
            f"hypotheses_locked.json not found in {out_dir}. "
            "Run 03_lock_hypotheses.py first."
        )
    if not results_path.exists():
        raise FileNotFoundError(f"results_raw.json not found in {out_dir}.")
    if not occ_path.exists():
        raise FileNotFoundError(f"subjects_occupation.json not found in {out_dir}.")

    with open(results_path, encoding="utf-8") as fh:
        results = json.load(fh)
    with open(occ_path, encoding="utf-8") as fh:
        occ_list = json.load(fh)
    with open(lock_path, encoding="utf-8") as fh:
        lock_data = json.load(fh)

    logger.info("Loaded %d results, %d occupation records.",
        len(results), len(occ_list))
    logger.info("Hypothesis lock: %s (hash %s)",
        lock_data.get("run_timestamp"), lock_data.get("lock_hash", "")[:16] + "...")

    # Flatten results into rows
    rows = [_flatten_result(r) for r in results]
    df_results = pd.DataFrame(rows)

    # Occupation lookup
    occ_map = {o["id"]: o for o in occ_list}
    df_results["occupation_group"]  = df_results["id"].map(
        lambda i: occ_map.get(i, {}).get("occupation_group", "Unknown"))
    df_results["occupation_detail"] = df_results["id"].map(
        lambda i: occ_map.get(i, {}).get("occupation_detail", "Unknown"))

    n_unmatched = (df_results["occupation_group"] == "Unknown").sum()
    if n_unmatched:
        logger.warning("%d results have no matching occupation record.", n_unmatched)

    logger.info("Merged dataframe: %d rows x %d columns.",
        *df_results.shape)
    return df_results

def _flatten_result(r: Dict) -> Dict:
    """Flatten a results_raw.json record into a single-level dict for pandas."""
    row: Dict[str, Any] = {"id": r.get("id", "")}

    # Temperament
    temp = r.get("temperament", {})
    row["temperament.primary"]     = temp.get("primary", "Unknown")
    scores = temp.get("scores", {})
    for k in ("Hot", "Cold", "Moist", "Dry"):
        row[f"temperament.scores.{k}"] = float(scores.get(k, 0))

    # Almuten
    alm = r.get("almuten", {})
    row["almuten.winner"] = alm.get("winner", "Unknown")

    # Lord of Geniture
    log = r.get("lord_of_geniture", {})
    row["lord_of_geniture.winner"] = log.get("winner", "Unknown")

    # Sect
    sect = r.get("sect", {})
    row["sect.type"] = sect.get("type", "Unknown") if isinstance(sect, dict) else str(sect)

    # Planets
    planets = r.get("planets", {})
    for p in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
        pd_data = planets.get(p, {})
        row[f"planets.{p}.house"]                  = int(pd_data.get("house", 0))
        row[f"planets.{p}.essential_dignity_total"] = float(pd_data.get("essential_dignity_total", 0))
        row[f"planets.{p}.accidental_total"]        = float(pd_data.get("accidental_total", 0))
        row[f"planets.{p}.solar_status"]            = pd_data.get("solar_status", "Free")
        row[f"planets.{p}.is_retrograde"]           = bool(pd_data.get("is_retrograde", False))

    # Elements
    el = r.get("elements", {})
    for e in ("FIRE", "EARTH", "AIR", "WATER"):
        row[f"elements.{e}"] = float(el.get(e, 0))

    # Hemispheres
    hemi = r.get("hemispheres", {})
    for h in ("East", "West", "North", "South"):
        row[f"hemispheres.{h}"] = float(hemi.get(h, 0))

    # Maltreatments
    row["maltreatment_count"]        = int(r.get("maltreatment_count", 0))
    row["maltreatment_severity_sum"] = int(r.get("maltreatment_severity_sum", 0))

    return row


# ---------------------------------------------------------------------------
# Statistical test helpers
# ---------------------------------------------------------------------------

def cohen_d(a: np.ndarray, b: np.ndarray) -> float:
    """Compute Cohen d effect size (positive = a > b)."""
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    pooled_std = np.sqrt((np.std(a, ddof=1)**2 + np.std(b, ddof=1)**2) / 2)
    if pooled_std == 0:
        return 0.0
    return float((np.mean(a) - np.mean(b)) / pooled_std)


def cramers_v(contingency: pd.DataFrame) -> float:
    """Compute Cramer V from a contingency table."""
    chi2, _, _, _ = stats.chi2_contingency(contingency, correction=False)
    n = contingency.values.sum()
    k = min(contingency.shape) - 1
    if n == 0 or k == 0:
        return float("nan")
    return float(np.sqrt(chi2 / (n * k)))


def run_anova(df: pd.DataFrame, variable: str,
             group_col: str = "occupation_group") -> Dict:
    """
    One-way ANOVA for a continuous variable across all groups.
    Returns F-statistic, p-value, and group means.
    """
    groups = [
        g[variable].dropna().values
        for _, g in df.groupby(group_col)
        if variable in df.columns
    ]
    groups = [g for g in groups if len(g) >= 2]
    if len(groups) < 2:
        return {"F": None, "p": None, "group_means": {}, "n_groups": len(groups)}
    try:
        F, p = stats.f_oneway(*groups)
    except Exception:
        F, p = None, None
    group_means = {}
    for grp, sub in df.groupby(group_col):
        vals = sub[variable].dropna()
        if len(vals) > 0:
            group_means[str(grp)] = {
                "mean": float(vals.mean()),
                "std":  float(vals.std()),
                "n":    int(len(vals)),
            }
    return {
        "F": float(F) if F is not None and not np.isnan(F) else None,
        "p": float(p) if p is not None and not np.isnan(p) else None,
        "group_means": group_means,
        "n_groups": len(groups),
    }

def run_chi_square(df: pd.DataFrame, variable: str,
                   group_col: str = "occupation_group") -> Dict:
    """
    Chi-square test for a categorical variable across all groups.
    Returns chi2, p-value, and Cramer V.
    """
    if variable not in df.columns:
        return {"chi2": None, "p": None, "cramers_v": None}
    ct = pd.crosstab(df[group_col], df[variable])
    if ct.shape[0] < 2 or ct.shape[1] < 2:
        return {"chi2": None, "p": None, "cramers_v": None}
    try:
        chi2, p, _, _ = stats.chi2_contingency(ct, correction=False)
        v = cramers_v(ct)
    except Exception:
        chi2, p, v = None, None, None
    return {
        "chi2":     float(chi2) if chi2 is not None else None,
        "p":        float(p)    if p is not None else None,
        "cramers_v": float(v)   if v is not None and not (v != v) else None,
    }


def test_hypothesis_continuous(
    df: pd.DataFrame,
    variable: str,
    group_a_names: List[str],
    group_b_names: List[str],
    direction: str,
    threshold: float,
    group_col: str = "occupation_group",
) -> Dict:
    """
    Test a continuous hypothesis with Mann-Whitney U and Cohen d.

    direction: "A > B" or "A < B" (for one-sided test interpretation).
    """
    vals_a = df.loc[df[group_col].isin(group_a_names), variable].dropna().values
    vals_b = df.loc[df[group_col].isin(group_b_names), variable].dropna().values

    result: Dict[str, Any] = {
        "variable": variable,
        "group_a": group_a_names,
        "group_b": group_b_names,
        "n_a": int(len(vals_a)),
        "n_b": int(len(vals_b)),
        "mean_a": float(np.mean(vals_a)) if len(vals_a) > 0 else None,
        "mean_b": float(np.mean(vals_b)) if len(vals_b) > 0 else None,
        "underpowered": len(vals_a) < 30 or len(vals_b) < 30,
        "u_stat": None,
        "p_value": None,
        "cohen_d": None,
        "verdict": "INCONCLUSIVE",
    }

    if len(vals_a) < 2 or len(vals_b) < 2:
        result["verdict"] = "INCONCLUSIVE"
        return result

    try:
        u, p = stats.mannwhitneyu(vals_a, vals_b, alternative="two-sided")
        result["u_stat"] = float(u)
        result["p_value"] = float(p)
    except Exception as exc:
        result["error"] = str(exc)
        return result

    d = cohen_d(vals_a, vals_b)
    result["cohen_d"] = float(d) if not np.isnan(d) else None

    if result["underpowered"]:
        result["verdict"] = "INCONCLUSIVE"
    elif p < threshold:
        a_gt_b = np.mean(vals_a) > np.mean(vals_b)
        expected_a_gt_b = "A > B" in direction or "> B" in direction
        if a_gt_b == expected_a_gt_b:
            result["verdict"] = "SUPPORTED"
        else:
            result["verdict"] = "NOT SUPPORTED"
    else:
        result["verdict"] = "NOT SUPPORTED"

    return result


def test_hypothesis_categorical(
    df: pd.DataFrame,
    variable: str,
    target_value: str,
    group_a_names: List[str],
    group_b_names: List[str],
    threshold: float,
    group_col: str = "occupation_group",
) -> Dict:
    """
    Test a categorical hypothesis (proportion of target_value in group A vs B).
    Uses chi-square + Cramer V.
    """
    sub = df.loc[df[group_col].isin(group_a_names + group_b_names)].copy()
    sub["is_target"] = sub[variable] == target_value
    sub["in_a"]      = sub[group_col].isin(group_a_names)

    ct = pd.crosstab(sub["in_a"], sub["is_target"])

    result: Dict[str, Any] = {
        "variable":    variable,
        "target_value": target_value,
        "group_a":     group_a_names,
        "group_b":     group_b_names,
        "n_a":         int(sub["in_a"].sum()),
        "n_b":         int((~sub["in_a"]).sum()),
        "prop_a":      float(sub.loc[sub["in_a"], "is_target"].mean()) if sub["in_a"].any() else None,
        "prop_b":      float(sub.loc[~sub["in_a"], "is_target"].mean()) if (~sub["in_a"]).any() else None,
        "chi2":        None,
        "p_value":     None,
        "cramers_v":   None,
        "underpowered": sub["in_a"].sum() < 30 or (~sub["in_a"]).sum() < 30,
        "verdict":     "INCONCLUSIVE",
    }

    if ct.shape[0] < 2 or ct.shape[1] < 2:
        return result
    try:
        chi2, p, _, _ = stats.chi2_contingency(ct, correction=False)
        v = cramers_v(ct)
        result["chi2"]      = float(chi2)
        result["p_value"]   = float(p)
        result["cramers_v"] = float(v) if not np.isnan(v) else None
    except Exception as exc:
        result["error"] = str(exc)
        return result

    if result["underpowered"]:
        result["verdict"] = "INCONCLUSIVE"
    elif p < threshold:
        prop_a = result["prop_a"] or 0
        prop_b = result["prop_b"] or 0
        if prop_a > prop_b:
            result["verdict"] = "SUPPORTED"
        else:
            result["verdict"] = "NOT SUPPORTED"
    else:
        result["verdict"] = "NOT SUPPORTED"
    return result

CONTINUOUS_VARIABLES = [
    "temperament.scores.Hot", "temperament.scores.Cold",
    "temperament.scores.Moist", "temperament.scores.Dry",
    "planets.Sun.house", "planets.Sun.essential_dignity_total", "planets.Sun.accidental_total",
    "planets.Moon.house", "planets.Moon.essential_dignity_total", "planets.Moon.accidental_total",
    "planets.Mercury.house", "planets.Mercury.essential_dignity_total", "planets.Mercury.accidental_total",
    "planets.Venus.house", "planets.Venus.essential_dignity_total", "planets.Venus.accidental_total",
    "planets.Mars.house", "planets.Mars.essential_dignity_total", "planets.Mars.accidental_total",
    "planets.Jupiter.house", "planets.Jupiter.essential_dignity_total", "planets.Jupiter.accidental_total",
    "planets.Saturn.house", "planets.Saturn.essential_dignity_total", "planets.Saturn.accidental_total",
    "elements.FIRE", "elements.EARTH", "elements.AIR", "elements.WATER",
    "hemispheres.East", "hemispheres.West", "hemispheres.North", "hemispheres.South",
    "maltreatment_count", "maltreatment_severity_sum",
]

CATEGORICAL_VARIABLES = [
    "temperament.primary", "almuten.winner", "lord_of_geniture.winner", "sect.type",
    "planets.Sun.solar_status", "planets.Moon.solar_status",
    "planets.Mercury.solar_status", "planets.Venus.solar_status",
    "planets.Mars.solar_status", "planets.Jupiter.solar_status",
    "planets.Saturn.solar_status",
]


def _hyp_verdict(sub_tests: List[Dict]) -> str:
    verdicts = [x.get("verdict", "INCONCLUSIVE") for x in sub_tests]
    if any(v == "SUPPORTED" for v in verdicts):
        return "SUPPORTED"
    if all(v == "INCONCLUSIVE" for v in verdicts):
        return "INCONCLUSIVE"
    return "NOT SUPPORTED"


def run_analysis(df: pd.DataFrame, lock_data: Dict, threshold: float = 0.01) -> Dict:
    """Run full statistical analysis; return results dict."""
    group_col = "occupation_group"
    group_counts = df[group_col].value_counts().to_dict()
    underpowered_groups = [g for g, n in group_counts.items() if n < 30]

    anova_results: Dict[str, Dict] = {}
    for var in CONTINUOUS_VARIABLES:
        if var in df.columns:
            anova_results[var] = run_anova(df, var, group_col)

    chi2_results: Dict[str, Dict] = {}
    for var in CATEGORICAL_VARIABLES:
        if var in df.columns:
            chi2_results[var] = run_chi_square(df, var, group_col)

    hyp_results: List[Dict] = []
    non_athletes   = [g for g in group_counts if g != "Athletes"]
    non_scientists = [g for g in group_counts if g != "Scientists"]

    # H1: Mars accidental dignity - Athletes vs rest
    h1 = test_hypothesis_continuous(
        df, "planets.Mars.accidental_total",
        ["Athletes"], non_athletes, "A > B", threshold)
    h1["hypothesis_id"] = "H1"
    hyp_results.append(h1)

    # H2: Mercury dignity - Scientists vs rest (two vars)
    h2a = test_hypothesis_continuous(df, "planets.Mercury.essential_dignity_total",
        ["Scientists"], non_scientists, "A > B", threshold)
    h2a["hypothesis_id"] = "H2a"
    h2b = test_hypothesis_continuous(df, "planets.Mercury.accidental_total",
        ["Scientists"], non_scientists, "A > B", threshold)
    h2b["hypothesis_id"] = "H2b"
    hyp_results.append({"hypothesis_id": "H2",
        "verdict": _hyp_verdict([h2a, h2b]),
        "sub_tests": [h2a, h2b]})

    # H3: Mars ess. / maltreatment - Military vs Artists (two vars)
    h3a = test_hypothesis_continuous(df, "planets.Mars.essential_dignity_total",
        ["Military"], ["Artists"], "A > B", threshold)
    h3a["hypothesis_id"] = "H3a"
    h3b = test_hypothesis_continuous(df, "maltreatment_severity_sum",
        ["Military"], ["Artists"], "A < B", threshold)
    h3b["hypothesis_id"] = "H3b"
    hyp_results.append({"hypothesis_id": "H3",
        "verdict": _hyp_verdict([h3a, h3b]),
        "sub_tests": [h3a, h3b]})

    # H4: Melancholic temperament - Scientists+Writers vs Athletes
    h4 = test_hypothesis_categorical(df, "temperament.primary", "Melancholic (Cold/Dry)",
        ["Scientists", "Writers"], ["Athletes"], threshold)
    h4["hypothesis_id"] = "H4"
    hyp_results.append(h4)

    # H5: Choleric temperament - Athletes+Military vs Scientists
    h5 = test_hypothesis_categorical(df, "temperament.primary", "Choleric (Hot/Dry)",
        ["Athletes", "Military"], ["Scientists"], threshold)
    h5["hypothesis_id"] = "H5"
    hyp_results.append(h5)

    # Rank variables by F-stat or chi2
    anova_ranked = sorted(
        [(k, v["F"]) for k, v in anova_results.items() if v.get("F") is not None],
        key=lambda x: -x[1])
    chi2_ranked = sorted(
        [(k, v["chi2"]) for k, v in chi2_results.items() if v.get("chi2") is not None],
        key=lambda x: -x[1])

    return {
        "metadata": {
            "hypothesis_lock_timestamp": lock_data.get("run_timestamp"),
            "hypothesis_lock_hash":      lock_data.get("lock_hash"),
            "significance_threshold":    threshold,
            "minimum_group_size":        30,
        },
        "group_summary": {
            "counts":             {str(k): int(v) for k, v in group_counts.items()},
            "underpowered_groups": underpowered_groups,
        },
        "anova": anova_results,
        "chi_square": chi2_results,
        "hypothesis_tests": hyp_results,
        "top_5_strongest_variables": {
            "continuous": [(k, round(f, 4)) for k, f in anova_ranked[:5]],
            "categorical": [(k, round(c, 4)) for k, c in chi2_ranked[:5]],
        },
        "bottom_5_weakest_variables": {
            "continuous": [(k, round(f, 4)) for k, f in anova_ranked[-5:]],
            "categorical": [(k, round(c, 4)) for k, c in chi2_ranked[-5:]],
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Analyze Gauquelin results (merges occupation data).",
    )
    ap.add_argument("--out-dir", type=Path, default=Path("."))
    ap.add_argument("--threshold", type=float, default=0.01)
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load and merge
    try:
        df = load_and_merge(args.out_dir)
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        return 1

    # Load lock data
    with open(args.out_dir / "hypotheses_locked.json", encoding="utf-8") as fh:
        lock_data = json.load(fh)

    # Run analysis
    results = run_analysis(df, lock_data, threshold=args.threshold)

    # Save
    out_path = args.out_dir / "full_results.json"
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False, default=str)
    logger.info("Full results saved to %s", out_path)

    # Summary print
    print("
--- Hypothesis Verdicts ---")
    for h in results["hypothesis_tests"]:
        hid = h.get("hypothesis_id", "?")
        verdict = h.get("verdict", "?")
        print(f"  {hid}: {verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())