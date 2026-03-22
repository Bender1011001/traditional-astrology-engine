import re
import sys

file_path = "E:/code.projects/astrology/scripts/generate_trace.py"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. We want to keep everything from `# ─── HTML Renderer` until the end of `render_html(trace: ComputationTrace) -> str:`
html_render_start = text.find("# ─── HTML Renderer")
if html_render_start == -1:
    print("Could not find HTML Renderer")
    sys.exit(1)

html_render_end_str = "</html>'''"
html_render_end = text.find(html_render_end_str, html_render_start)
if html_render_end == -1:
    print("Could not find HTML Renderer end")
    sys.exit(1)

html_render_end_idx = html_render_end + len(html_render_end_str)

html_renderer_code = text[html_render_start:html_render_end_idx]

top_code = """\"\"\"
Generate Computation Trace
==========================
Runs the full engine and captures every calculation step into a beautiful
standalone HTML document that practitioners can read and verify.

Usage:
    python scripts/generate_trace.py --date 1996-08-13 --time 07:18 --city Fairfield --state CA --name "Native"

Output:
    chart_outputs/<name>_trace.html   (self-contained, open in any browser)
    chart_outputs/<name>_trace.json   (machine-readable trace data)
\"\"\"

import sys
import os
import json
import argparse
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.engine.trace import ComputationTrace
from src.engine.trace_generator import build_trace_object

"""

bottom_code = """


def main():
    parser = argparse.ArgumentParser(description="Generate a Computation Trace for a nativity.")
    parser.add_argument("--date", default="1996-08-13", help="Birth date (YYYY-MM-DD)")
    parser.add_argument("--time", default="07:18", help="Birth time (HH:MM)")
    parser.add_argument("--city", default="Fairfield", help="Birth city")
    parser.add_argument("--state", default="CA", help="Birth state/country")
    parser.add_argument("--name", default="Native", help="Subject name")
    args = parser.parse_args()
    
    print(f"{'='*70}")
    print(f"GENERATING COMPUTATION TRACE")
    print(f"Subject: {args.name}")
    print(f"{'='*70}")
    
    print("\\n[1/3] Building trace object...")
    trace = build_trace_object(
        date_str=args.date,
        time_str=args.time,
        city=args.city,
        state=args.state,
        name=args.name,
    )

    if not trace.steps or trace.steps[0].category == "Error":
        print(f"ERROR generating trace: {trace.steps[0].calculation if trace.steps else 'Unknown error'}")
        return
        
    print("[2/3] Analyzing calculated trace...")
    print(f"Categories found: {len(trace.categories)}")
    print(f"Total steps: {len(trace.steps)}")

    print("[3/3] Rendering outputs...")
    
    # Output
    out_dir = os.path.join(os.path.dirname(__file__), '..', 'chart_outputs')
    os.makedirs(out_dir, exist_ok=True)
    
    safe_name = args.name.replace(" ", "_").lower()
    
    # HTML
    html = render_html(trace)
    html_path = os.path.join(out_dir, f'{safe_name}_computation_trace.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\\n[OK] HTML trace saved: {html_path}")
    
    # JSON
    json_path = os.path.join(out_dir, f'{safe_name}_computation_trace.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(trace.to_dict(), f, indent=2, default=str)
    print(f"[OK] JSON trace saved: {json_path}")
    
    print(f"\\n{'='*70}")
    print(f"TRACE COMPLETE: {len(trace.steps)} steps across {len(trace.categories)} categories")
    print(f"Elapsed: {trace.elapsed_ms:.0f}ms")
    print(f"\\nOpen {html_path} in any browser to view the trace.")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
"""

new_content = top_code + html_renderer_code + bottom_code

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"Successfully refactored {file_path}")
