"""Flash vs Opus 4.8 comparison run on the same deterministic chart payload."""
import os
import sys
import traceback

sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "src"))

from src.scripts.generate_premium_report import (generate_chart_data,
                                                 run_premium_report)

ITERS = int(os.environ.get("COMPARE_ITERS", "4"))

print("Generating deterministic chart payload (shared input)...")
chart_data = generate_chart_data(
    "Test Native",
    "1996-08-13",
    "07:18",
    "Fairfield",
    "CA",
    latitude=38.2494,
    longitude=-122.0397,
)
if not chart_data:
    print("CHART GENERATION FAILED")
    sys.exit(1)

print(f"Chart payload size: {len(chart_data):,} chars (~{len(chart_data)//4:,} tokens)")

os.makedirs("premium_reports", exist_ok=True)
runs = [
    ("google/gemini-3.5-flash", "flash"),
    ("anthropic/claude-opus-4.8", "opus48"),
]

for model, tag in runs:
    os.environ["OPENROUTER_MODEL"] = model
    out = os.path.join("premium_reports", f"fairfield_{tag}.md")
    print(f"\n{'#'*70}\n# RUN {tag}  model={model}  iterations={ITERS}\n{'#'*70}")
    try:
        run_premium_report(chart_data, out, ITERS)
        print(f"RUN {tag} OK -> {out}")
    except Exception as e:
        print(f"RUN {tag} FAILED: {e!r}")
        traceback.print_exc()

print("\nCOMPARE DONE")
