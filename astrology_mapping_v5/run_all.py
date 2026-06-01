#!/usr/bin/env python3
"""
run_all.py — Run all 20 domain pipelines and generate synthesis_report.md.

Historical Use Only — not financial, investment, medical, or legal advice.

Usage:
    python run_all.py [--domains dom1,dom2,...] [--force-refresh]

Generates results/<domain>_report.md for each domain, then
writes results/synthesis_report.md with cross-domain analysis.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from collections import defaultdict
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

_HERE = Path(__file__).parent.resolve()
_PROJECT_ROOT = _HERE.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

from astrology_mapping_v5.domains import DOMAINS
from astrology_mapping_v5.fetch_data import fetch_domain
from astrology_mapping_v5.features import generate_features_for_dates
from astrology_mapping_v5.pipeline import run_domain_pipeline
from astrology_mapping_v5.run_domain import build_target

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Directories
# ---------------------------------------------------------------------------

_DATA_DIR = _HERE / "data"
_RESULTS_DIR = _HERE / "results"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
_RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Run single domain (reuses run_domain logic)
# ---------------------------------------------------------------------------

def run_single_domain(domain_name: str, force_refresh: bool = False) -> dict:
    """
    Run the full pipeline for one domain. Returns result dict.
    Returns {'domain': domain_name, 'error': ..., 'verdict': 'ERROR'} on failure.
    """
    log.info("=" * 70)
    log.info("STARTING DOMAIN: %s", domain_name)
    log.info("=" * 70)

    domain_cfg = DOMAINS[domain_name]
    freq = domain_cfg["frequency"]
    target_col = domain_cfg["targets"][0]["col"]

    try:
        # 1. Fetch raw data
        raw_df = fetch_domain(domain_name, _DATA_DIR, force_refresh=force_refresh)
        if raw_df is None or len(raw_df) == 0:
            log.error("[%s] No data available — skipping.", domain_name)
            return {"domain": domain_name, "error": "no_data", "verdict": "SKIP"}

        # 2. Build target
        target_df = build_target(domain_name, raw_df, freq)
        if target_df is None or len(target_df) == 0:
            log.error("[%s] Target building failed — skipping.", domain_name)
            return {"domain": domain_name, "error": "target_failed", "verdict": "SKIP"}

        n_pos = int(target_df[target_col].sum())
        if n_pos < 20:
            log.warning("[%s] Too few positive events (%d) — skipping.", domain_name, n_pos)
            return {"domain": domain_name, "error": f"too_few_events_{n_pos}", "verdict": "SKIP"}

        # 3. Generate features
        date_range_dates = pd.DatetimeIndex(target_df["date"].unique())
        feature_cache = _DATA_DIR / f"{domain_name}_features.parquet"
        feature_df = generate_features_for_dates(
            date_range_dates, cache_path=feature_cache
        )

        # 4. Pipeline
        n_years = int((target_df["date"].max() - target_df["date"].min()).days / 365.25)
        min_train_years = max(5, min(20, n_years // 3))

        result = run_domain_pipeline(
            domain_name=domain_name,
            df=target_df,
            feature_df=feature_df,
            target_col=target_col,
            results_dir=_RESULTS_DIR,
            min_train_years=min_train_years,
            freq=freq,
        )
        result["n_pos"] = n_pos
        return result

    except Exception as exc:
        log.exception("[%s] Unhandled error: %s", domain_name, exc)
        return {"domain": domain_name, "error": str(exc), "verdict": "ERROR"}


# ---------------------------------------------------------------------------
# Cross-domain feature overlap analysis
# ---------------------------------------------------------------------------

def _analyze_feature_overlap(all_results: list[dict]) -> dict:
    """
    Identify features that appear in top 10 for multiple passing domains.
    (Simplified: counts domains where fast features were engaged.)
    """
    # For each domain that reached Step 3, tally which fast feature prefix groups
    # appeared (we don't have per-feature importance here, but we can identify
    # which fast feature groups were used across domains).
    fast_prefix_counts: dict[str, int] = defaultdict(int)
    passing_domains: list[str] = []

    for r in all_results:
        if r.get("verdict") == "SIGNAL_DETECTED":
            passing_domains.append(r.get("domain", ""))
        # Count feature groups that were engaged at Step 3
        if r.get("fast_gate_passes", False) or r.get("verdict") == "SIGNAL_DETECTED":
            # These domains engaged fast features
            fast_prefix_counts["fast_features_engaged"] += 1

    return {
        "passing_domains": passing_domains,
        "n_passing": len(passing_domains),
        "feature_group_counts": dict(fast_prefix_counts),
    }


# ---------------------------------------------------------------------------
# Synthesis report
# ---------------------------------------------------------------------------

def write_synthesis_report(all_results: list[dict], results_dir: Path) -> None:
    """Write the cross-domain synthesis_report.md."""
    report_path = results_dir / "synthesis_report.md"
    overlap = _analyze_feature_overlap(all_results)
    passing = overlap["passing_domains"]
    analysis_date = date.today().isoformat()

    def _f(val, d: int = 4) -> str:
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return "N/A"
        if isinstance(val, (int, float)):
            return f"{val:.{d}f}"
        return str(val)

    # ── Title / Disclaimer ──────────────────────────────────────────────────
    lines = [
        "# Astro-Mapping-v5 Synthesis Report",
        "",
        "> **Historical Use Only — not financial, investment, medical, or legal advice.**",
        ">",
        "> This study is a self-falsifying multi-domain astrological correlation analysis.",
        "> Any statistically significant result at this level of multiple testing should be",
        "> treated with extreme caution and is NOT suitable for investment, medical, legal,",
        "> or any other practical decision-making.",
        "",
        f"**Analysis Date**: {analysis_date}",
        f"**Domains Tested**: {len(all_results)}",
        f"**Domains Surviving All Gates**: {overlap['n_passing']}",
        "",
        "---",
        "",
    ]

    # ── Summary Table ────────────────────────────────────────────────────────
    lines += [
        "## Summary Table",
        "",
        "| Domain | N_obs | Calendar_AUC | Astro_AUC_Full | Fast_AUC | Gate_Step2 | Gate_Step3 | Verdict |",
        "|--------|-------|-------------|---------------|---------|-----------|-----------|---------|",
    ]
    for r in sorted(all_results, key=lambda x: x.get("domain", "")):
        dom = r.get("domain", "?")
        n_obs = r.get("n_obs", "N/A")
        cal_auc = _f(r.get("calendar_auc"))
        astro_full = _f(r.get("astro_auc_full"))
        fast_auc = _f(r.get("astro_auc_fast"))
        gate2 = "✅" if r.get("gate_passes") else "❌"
        gate3 = "✅" if r.get("fast_gate_passes") else ("—" if not r.get("gate_passes") else "❌")
        verdict = r.get("verdict", "?")
        lines.append(
            f"| {dom} | {n_obs} | {cal_auc} | {astro_full} | {fast_auc} | {gate2} | {gate3} | `{verdict}` |"
        )

    lines += ["", "---", ""]

    # ── Detailed results by verdict ──────────────────────────────────────────
    lines += [
        "## Results by Pipeline Stage",
        "",
        "### Domains Reaching SIGNAL_DETECTED",
        "",
    ]
    if passing:
        for dom in passing:
            lines.append(f"- `{dom}`")
    else:
        lines.append("- *None* — no domain survived all falsification tests.")
    lines += [""]

    lines += ["### Domains Failing Step 2 Gate (Astro vs Calendar)", ""]
    step2_fail = [r for r in all_results if r.get("verdict") == "FAIL_GATE_STEP2"]
    if step2_fail:
        for r in step2_fail:
            lines.append(
                f"- `{r['domain']}`: cal_AUC={_f(r.get('calendar_auc'))}, "
                f"astro_AUC={_f(r.get('astro_auc_full'))}"
            )
    else:
        lines.append("- None")
    lines += [""]

    lines += ["### Domains Failing Step 3 Gate (Fast Features)", ""]
    step3_fail = [r for r in all_results if r.get("verdict") == "FAIL_GATE_STEP3"]
    if step3_fail:
        for r in step3_fail:
            lines.append(
                f"- `{r['domain']}`: fast_AUC={_f(r.get('astro_auc_fast'))}"
            )
    else:
        lines.append("- None")
    lines += [""]

    lines += ["### Domains Failing Falsification (Step 4)", ""]
    falsif_fail = [r for r in all_results if r.get("verdict") == "FAIL_FALSIFICATION"]
    if falsif_fail:
        for r in falsif_fail:
            ls = r.get("label_shuffle", {})
            es = r.get("era_block_shuffle", {})
            rt = r.get("reverse_time", {})
            lines.append(
                f"- `{r['domain']}`: "
                f"label_p={_f(ls.get('p_value'), 3)}, "
                f"era_p={_f(es.get('p_value'), 3)}, "
                f"reverse_auc={_f(rt.get('reverse_auc'))}"
            )
    else:
        lines.append("- None")
    lines += [""]

    lines += ["### Skipped / Error Domains", ""]
    skip_err = [r for r in all_results if r.get("verdict") in ("SKIP", "ERROR")]
    if skip_err:
        for r in skip_err:
            lines.append(f"- `{r['domain']}`: {r.get('error', 'unknown error')}")
    else:
        lines.append("- None")
    lines += ["", "---", ""]

    # ── Overall Conclusion ───────────────────────────────────────────────────
    lines += [
        "## Overall Conclusion",
        "",
    ]
    if passing:
        lines += [
            f"**{len(passing)} domain(s)** survived all five falsification gates: "
            f"{', '.join(f'`{d}`' for d in passing)}.",
            "",
            "⚠️ **Caution**: Given the large number of domains tested simultaneously, "
            "some apparent signals are expected by chance alone under multiple comparison. "
            "These results do NOT constitute proof of astrological causation. "
            "Independent replication on held-out datasets is required before any "
            "further interpretation.",
        ]
    else:
        lines += [
            "**No domain survived all falsification gates.**",
            "",
            "This is the expected null result for a rigorous self-falsifying study: "
            "astrological features did not demonstrate predictive power beyond calendar "
            "seasonality and chance in any of the domains tested.",
        ]
    lines += [""]

    # ── Top 3 Next-Step Recommendations ─────────────────────────────────────
    lines += [
        "## Top 3 Recommendations for Future Work",
        "",
        "1. **Pre-register before testing**: To eliminate post-hoc selection bias, "
        "any future study should pre-register its hypotheses, domain selection, "
        "and statistical thresholds before data analysis begins.",
        "",
        "2. **Out-of-sample replication**: Any domain showing apparent signal should "
        "be replicated on a completely held-out dataset (e.g., non-US markets, "
        "different geophysical datasets) before drawing conclusions.",
        "",
        "3. **Frequentist correction for multiple comparisons**: With 20 domains tested, "
        "Bonferroni-corrected α = 0.05/20 = 0.0025. Future analyses should apply this "
        "correction explicitly to the p-values from Step 4.",
        "",
        "---",
        "",
        "> **Historical Use Only — not financial, investment, medical, or legal advice.**",
        ">",
        f"> Report generated: {analysis_date}",
    ]

    report_text = "\n".join(lines)
    report_path.write_text(report_text, encoding="utf-8")
    log.info("Synthesis report written: %s", report_path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run all astro-mapping-v5 domain pipelines"
    )
    parser.add_argument(
        "--domains",
        type=str,
        default="",
        help="Comma-separated list of domains to run (default: all)",
    )
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        default=False,
        help="Force re-download of all cached data",
    )
    args = parser.parse_args()

    if args.domains:
        domain_list = [d.strip() for d in args.domains.split(",") if d.strip()]
        unknown = [d for d in domain_list if d not in DOMAINS]
        if unknown:
            print(f"Unknown domains: {unknown}")
            print("Available:", list(DOMAINS.keys()))
            sys.exit(1)
    else:
        domain_list = list(DOMAINS.keys())

    log.info("Running %d domain(s): %s", len(domain_list), domain_list)
    t_global_start = time.time()

    all_results: list[dict] = []
    for domain_name in domain_list:
        t0 = time.time()
        result = run_single_domain(domain_name, force_refresh=args.force_refresh)
        result["wall_seconds"] = round(time.time() - t0, 1)
        all_results.append(result)
        log.info(
            "Domain %s completed in %.1f s → %s",
            domain_name, result["wall_seconds"], result.get("verdict", "?")
        )

    # Write synthesis report
    write_synthesis_report(all_results, _RESULTS_DIR)

    # Print final summary
    total_seconds = time.time() - t_global_start
    n_pass = sum(1 for r in all_results if r.get("verdict") == "SIGNAL_DETECTED")
    n_skip = sum(1 for r in all_results if r.get("verdict") in ("SKIP", "ERROR"))
    n_fail = len(all_results) - n_pass - n_skip

    print()
    print("=" * 70)
    print("ALL DOMAINS COMPLETE")
    print("=" * 70)
    print(f"  Total domains run:    {len(all_results)}")
    print(f"  SIGNAL_DETECTED:      {n_pass}")
    print(f"  FAILED:               {n_fail}")
    print(f"  SKIPPED/ERROR:        {n_skip}")
    print(f"  Total elapsed:        {total_seconds:.0f} s")
    print(f"  Synthesis report:     {_RESULTS_DIR / 'synthesis_report.md'}")
    print("=" * 70)
    print()
    print("Historical Use Only — not financial, investment, medical, or legal advice.")


if __name__ == "__main__":
    main()
