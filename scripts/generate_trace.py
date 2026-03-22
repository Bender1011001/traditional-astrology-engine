"""
Generate Computation Trace
==========================
Runs the full engine and captures every calculation step into a beautiful
standalone HTML document that practitioners can read and verify.

Usage:
    python scripts/generate_trace.py --date 1996-08-13 --time 07:18 --city Fairfield --state CA --name "Native"

Output:
    chart_outputs/<name>_trace.html   (self-contained, open in any browser)
    chart_outputs/<name>_trace.json   (machine-readable trace data)
"""

import sys
import os
import json
import argparse
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.engine.trace import ComputationTrace
from src.engine.trace_generator import build_trace_object

# ─── HTML Renderer ────────────────────────────────────────────────────────────

def render_html(trace: ComputationTrace) -> str:
    """Render the trace as a beautiful standalone HTML document."""
    
    categories_html = []
    for cat in trace.categories:
        steps = trace.steps_by_category(cat)
        
        # Group by subsection within category
        subsections = {}
        for s in steps:
            key = s.subsection or "__main__"
            subsections.setdefault(key, []).append(s)
        
        steps_html_parts = []
        for sub_key, sub_steps in subsections.items():
            if sub_key != "__main__":
                steps_html_parts.append(f'<h4 class="subsection-header">{sub_key}</h4>')
            
            for s in sub_steps:
                inputs_rows = "".join(
                    f'<tr><td class="input-key">{k}</td><td class="input-val">{v}</td></tr>'
                    for k, v in s.inputs.items()
                )
                notes_html = f'<div class="step-notes"><strong>📝 Practitioner Note:</strong> {s.notes}</div>' if s.notes else ""
                
                steps_html_parts.append(f'''
                <div class="step-card">
                    <div class="step-header">
                        <span class="step-number">Step {s.step_number}</span>
                        <span class="step-technique">{s.technique}</span>
                    </div>
                    <div class="step-body">
                        <div class="step-section">
                            <div class="section-label">📥 Inputs</div>
                            <table class="inputs-table">{inputs_rows}</table>
                        </div>
                        <div class="step-section">
                            <div class="section-label">📜 Rule</div>
                            <div class="rule-text">{s.rule}</div>
                            <div class="source-tag">— {s.source}</div>
                        </div>
                        <div class="step-section">
                            <div class="section-label">🔢 Calculation</div>
                            <div class="calc-text">{s.calculation}</div>
                        </div>
                        <div class="step-section result-section">
                            <div class="section-label">✅ Result</div>
                            <div class="result-text">{s.result}</div>
                        </div>
                        {notes_html}
                    </div>
                </div>
                ''')
        
        steps_html = "\n".join(steps_html_parts)
        cat_id = cat.replace(" ", "-").replace("/", "-").lower()
        
        categories_html.append(f'''
        <div class="category-block" id="{cat_id}">
            <h3 class="category-title" onclick="toggleCategory(this)">
                <span class="collapse-icon">▼</span> {cat}
                <span class="step-count">{len(steps)} steps</span>
            </h3>
            <div class="category-body">
                {steps_html}
            </div>
        </div>
        ''')
    
    # Table of contents
    toc_items = "\n".join(
        f'<li><a href="#{cat.replace(" ", "-").replace("/", "-").lower()}">{cat}</a> <span class="toc-count">({len(trace.steps_by_category(cat))} steps)</span></li>'
        for cat in trace.categories
    )
    
    all_categories = "\n".join(categories_html)
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Computation Trace — {trace.subject_name}</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    :root {{
        --bg: #0a0a0f;
        --surface: #12121a;
        --surface-2: #1a1a2e;
        --surface-3: #252540;
        --border: #2a2a45;
        --text: #e8e8f0;
        --text-dim: #8888aa;
        --text-muted: #555570;
        --accent: #7c6aef;
        --accent-glow: #7c6aef40;
        --gold: #d4a853;
        --gold-glow: #d4a85330;
        --green: #4ade80;
        --cyan: #22d3ee;
        --red: #f87171;
        --orange: #fb923c;
    }}
    
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    
    body {{
        font-family: 'Inter', -apple-system, sans-serif;
        background: var(--bg);
        color: var(--text);
        line-height: 1.6;
        min-height: 100vh;
    }}
    
    .hero {{
        background: linear-gradient(135deg, #0f0c29 0%, #1a1040 40%, #24243e 100%);
        border-bottom: 1px solid var(--border);
        padding: 3rem 2rem;
        text-align: center;
    }}
    
    .hero h1 {{
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--gold), #f0d890, var(--gold));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }}
    
    .hero .subtitle {{
        color: var(--text-dim);
        font-size: 1.1rem;
        font-weight: 300;
    }}
    
    .hero .meta-line {{
        margin-top: 1rem;
        display: flex;
        gap: 2rem;
        justify-content: center;
        flex-wrap: wrap;
    }}
    
    .hero .meta-badge {{
        background: var(--surface-2);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-size: 0.85rem;
        color: var(--text-dim);
    }}
    
    .hero .meta-badge strong {{
        color: var(--gold);
    }}
    
    .container {{
        max-width: 1000px;
        margin: 0 auto;
        padding: 2rem;
    }}
    
    /* TOC */
    .toc {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
    }}
    
    .toc h2 {{
        font-size: 1.1rem;
        color: var(--gold);
        margin-bottom: 1rem;
        font-weight: 600;
    }}
    
    .toc ul {{
        list-style: none;
        columns: 2;
        column-gap: 2rem;
    }}
    
    .toc li {{
        padding: 0.3rem 0;
        break-inside: avoid;
    }}
    
    .toc a {{
        color: var(--accent);
        text-decoration: none;
        font-size: 0.9rem;
        transition: color 0.2s;
    }}
    
    .toc a:hover {{
        color: var(--gold);
    }}
    
    .toc-count {{
        color: var(--text-muted);
        font-size: 0.8rem;
    }}
    
    /* Category */
    .category-block {{
        margin-bottom: 1.5rem;
    }}
    
    .category-title {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1rem 1.5rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.8rem;
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--gold);
        transition: all 0.2s;
        user-select: none;
    }}
    
    .category-title:hover {{
        background: var(--surface-2);
        border-color: var(--gold);
        box-shadow: 0 0 20px var(--gold-glow);
    }}
    
    .collapse-icon {{
        transition: transform 0.3s;
        font-size: 0.8rem;
    }}
    
    .category-title.collapsed .collapse-icon {{
        transform: rotate(-90deg);
    }}
    
    .step-count {{
        margin-left: auto;
        font-size: 0.8rem;
        font-weight: 400;
        color: var(--text-muted);
        background: var(--surface-3);
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
    }}
    
    .category-body {{
        padding: 0.5rem 0 0 0;
        transition: max-height 0.4s ease;
        overflow: hidden;
    }}
    
    .category-body.hidden {{
        display: none;
    }}
    
    .subsection-header {{
        color: var(--cyan);
        font-size: 0.95rem;
        font-weight: 600;
        padding: 0.8rem 0 0.3rem 0.5rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 0.5rem;
    }}
    
    /* Step Card */
    .step-card {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        margin-bottom: 0.75rem;
        overflow: hidden;
        transition: border-color 0.2s;
    }}
    
    .step-card:hover {{
        border-color: var(--accent);
    }}
    
    .step-header {{
        background: var(--surface-2);
        padding: 0.6rem 1.2rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        border-bottom: 1px solid var(--border);
    }}
    
    .step-number {{
        background: var(--accent);
        color: white;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        white-space: nowrap;
    }}
    
    .step-technique {{
        font-weight: 600;
        font-size: 0.95rem;
    }}
    
    .step-body {{
        padding: 1rem 1.2rem;
    }}
    
    .step-section {{
        margin-bottom: 0.8rem;
    }}
    
    .section-label {{
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.3rem;
    }}
    
    .inputs-table {{
        width: 100%;
        font-size: 0.85rem;
        border-collapse: collapse;
    }}
    
    .inputs-table tr {{
        border-bottom: 1px solid var(--border);
    }}
    
    .inputs-table tr:last-child {{
        border-bottom: none;
    }}
    
    .input-key {{
        color: var(--text-dim);
        padding: 0.3rem 0.5rem 0.3rem 0;
        width: 120px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
    }}
    
    .input-val {{
        padding: 0.3rem 0;
        color: var(--text);
    }}
    
    .rule-text {{
        font-size: 0.9rem;
        color: var(--text);
        line-height: 1.7;
        padding: 0.5rem 0.8rem;
        background: var(--surface-2);
        border-radius: 6px;
        border-left: 3px solid var(--gold);
    }}
    
    .source-tag {{
        font-size: 0.8rem;
        color: var(--gold);
        font-style: italic;
        margin-top: 0.3rem;
        padding-left: 0.8rem;
    }}
    
    .calc-text {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        color: var(--cyan);
        background: var(--surface-2);
        padding: 0.6rem 0.8rem;
        border-radius: 6px;
        white-space: pre-wrap;
        word-break: break-word;
    }}
    
    .result-section {{
        background: linear-gradient(135deg, var(--surface-2), var(--surface-3));
        border-radius: 8px;
        padding: 0.8rem;
        border: 1px solid var(--border);
    }}
    
    .result-text {{
        font-size: 1rem;
        font-weight: 600;
        color: var(--green);
    }}
    
    .step-notes {{
        margin-top: 0.5rem;
        font-size: 0.82rem;
        color: var(--text-dim);
        background: var(--surface-2);
        padding: 0.5rem 0.8rem;
        border-radius: 6px;
        border-left: 3px solid var(--orange);
        white-space: pre-wrap;
    }}
    
    /* Footer */
    .footer {{
        text-align: center;
        padding: 2rem;
        color: var(--text-muted);
        font-size: 0.8rem;
        border-top: 1px solid var(--border);
        margin-top: 2rem;
    }}
    
    /* Responsive */
    @media (max-width: 768px) {{
        .hero h1 {{ font-size: 1.5rem; }}
        .toc ul {{ columns: 1; }}
        .container {{ padding: 1rem; }}
        .hero {{ padding: 2rem 1rem; }}
    }}

    /* Print */
    @media print {{
        body {{ background: white; color: #111; }}
        .step-card {{ break-inside: avoid; border: 1px solid #ccc; }}
        .hero {{ background: none; border: none; }}
        .hero h1 {{ color: #333; -webkit-text-fill-color: #333; }}
        .category-body.hidden {{ display: block !important; }}
    }}
    
    /* Controls */
    .controls-bar {{
        display: flex;
        gap: 1rem;
        align-items: center;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
    }}
    
    .search-input {{
        flex: 1;
        min-width: 200px;
        padding: 0.7rem 1rem;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        color: var(--text);
        font-family: 'Inter', sans-serif;
        font-size: 0.9rem;
        outline: none;
        transition: border-color 0.2s;
    }}
    
    .search-input:focus {{
        border-color: var(--accent);
        box-shadow: 0 0 12px var(--accent-glow);
    }}
    
    .search-input::placeholder {{
        color: var(--text-muted);
    }}
    
    .controls-buttons {{
        display: flex;
        gap: 0.5rem;
    }}
    
    .ctrl-btn {{
        padding: 0.6rem 1rem;
        background: var(--surface-2);
        border: 1px solid var(--border);
        border-radius: 8px;
        color: var(--text-dim);
        font-family: 'Inter', sans-serif;
        font-size: 0.8rem;
        cursor: pointer;
        transition: all 0.2s;
    }}
    
    .ctrl-btn:hover {{
        background: var(--surface-3);
        border-color: var(--accent);
        color: var(--text);
    }}
    
    .scroll-top {{
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: var(--accent);
        border: none;
        color: white;
        font-size: 1.2rem;
        cursor: pointer;
        opacity: 0;
        transition: opacity 0.3s;
        z-index: 100;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }}
    
    .scroll-top:hover {{
        background: var(--gold);
    }}
</style>
</head>
<body>
    <div class="hero">
        <h1>&#9881; Computation Trace</h1>
        <div class="subtitle">Every calculation step, verified and sourced</div>
        <div class="meta-line">
            <div class="meta-badge"><strong>{trace.subject_name}</strong></div>
            <div class="meta-badge">{trace.birth_data}</div>
            <div class="meta-badge"><strong>{len(trace.steps)}</strong> computation steps</div>
            <div class="meta-badge">Completed in <strong>{trace.elapsed_ms:.0f}ms</strong></div>
            <div class="meta-badge">Generated <strong>{trace.started_at.strftime("%Y-%m-%d %H:%M")}</strong></div>
        </div>
    </div>
    
    <div class="container">
        <div class="controls-bar">
            <input type="text" id="searchInput" class="search-input" placeholder="Search steps... (e.g. Sun, Domicile, Fortune)" oninput="filterSteps(this.value)">
            <div class="controls-buttons">
                <button class="ctrl-btn" onclick="expandAll()">Expand All</button>
                <button class="ctrl-btn" onclick="collapseAll()">Collapse All</button>
            </div>
        </div>
        
        <div class="toc">
            <h2>Table of Contents</h2>
            <ul>{toc_items}</ul>
        </div>
        
        {all_categories}
        
        <div class="footer">
            <p>Traditional Astrology Engine &mdash; Computation Trace</p>
            <p>All calculations use pre-1700 methods. Sources cited per step.</p>
            <p>Historical Use Only. Not medical, financial, or legal advice.</p>
        </div>
    </div>
    
    <button class="scroll-top" id="scrollTopBtn" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">&#8593;</button>
    
    <script>
        function toggleCategory(el) {{
            el.classList.toggle('collapsed');
            const body = el.nextElementSibling;
            body.classList.toggle('hidden');
        }}
        
        function expandAll() {{
            document.querySelectorAll('.category-title').forEach(el => {{
                el.classList.remove('collapsed');
                el.nextElementSibling.classList.remove('hidden');
            }});
        }}
        
        function collapseAll() {{
            document.querySelectorAll('.category-title').forEach(el => {{
                el.classList.add('collapsed');
                el.nextElementSibling.classList.add('hidden');
            }});
        }}
        
        function filterSteps(query) {{
            const q = query.toLowerCase().trim();
            document.querySelectorAll('.step-card').forEach(card => {{
                if (!q) {{
                    card.style.display = '';
                    return;
                }}
                const text = card.textContent.toLowerCase();
                card.style.display = text.includes(q) ? '' : 'none';
            }});
            // Auto-expand categories that have visible cards
            if (q) {{
                document.querySelectorAll('.category-block').forEach(block => {{
                    const visible = block.querySelectorAll('.step-card:not([style*="display: none"])');
                    const title = block.querySelector('.category-title');
                    const body = block.querySelector('.category-body');
                    if (visible.length > 0) {{
                        title.classList.remove('collapsed');
                        body.classList.remove('hidden');
                    }} else {{
                        title.classList.add('collapsed');
                        body.classList.add('hidden');
                    }}
                }});
            }}
        }}
        
        // Scroll-to-top button visibility
        window.addEventListener('scroll', () => {{
            const btn = document.getElementById('scrollTopBtn');
            btn.style.opacity = window.scrollY > 500 ? '1' : '0';
            btn.style.pointerEvents = window.scrollY > 500 ? 'auto' : 'none';
        }});
    </script>
</body>
</html>'''


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
    
    print("\n[1/3] Building trace object...")
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
    print(f"\n[OK] HTML trace saved: {html_path}")
    
    # JSON
    json_path = os.path.join(out_dir, f'{safe_name}_computation_trace.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(trace.to_dict(), f, indent=2, default=str)
    print(f"[OK] JSON trace saved: {json_path}")
    
    print(f"\n{'='*70}")
    print(f"TRACE COMPLETE: {len(trace.steps)} steps across {len(trace.categories)} categories")
    print(f"Elapsed: {trace.elapsed_ms:.0f}ms")
    print(f"\nOpen {html_path} in any browser to view the trace.")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
