# Modular astrology report template

This folder contains a print-first HTML/CSS report template for the premium astrology PDF path:

- `astrology_report_template.html`
- `astrology_report_template.css`

The HTML is renderer-neutral but uses Jinja-style bindings because the backend is Python. Pipe your engine payload into the `report` object, render the HTML, then hand the output to the PDF renderer you choose. The template is intentionally separate from the current ReportLab generator so it can be wired in without changing the existing purchase or email path.

Required contract highlights:

- `report.client.display_name`
- `report.birth.date`, `report.birth.time`, `report.birth.location`, `report.birth.audit_rows`
- `report.summary.sect`, `report.summary.ascendant`, `report.summary.almuten`
- `report.chart.wheel_svg` or `report.chart.house_cusps` plus `report.chart.planets`
- `report.planets`, `report.houses`, `report.dignities`, `report.accidental_conditions`
- `report.luminaries.sun`, `report.luminaries.moon`, `report.personal_planets`, `report.social_planets`
- `report.aspects`, `report.receptions`, `report.lots`, `report.almuten`
- `report.timing.profection`, `report.timing.firdaria.periods`, `report.timing.solar_return`, `report.timing.primary_directions`, `report.timing.next_year.months`
- `report.synthesis.themes`, `report.reflection_prompts`, `report.method.steps`, `report.next_steps.actions`

Design notes:

- The CSS is Letter-size and print-first, with `@page` configured for browser/PDF rendering.
- The template has 30 ordered content modules, but it does not force 30 PDF pages. Normal modules flow naturally; only the cover and final call-to-action sheet force page breaks.
- Every report module is an explicit `.report-section` with `data-section-index` and a semantic `data-section` name so the backend can omit, repeat, or expand modules before rendering.
- The final page includes conversion slots for follow-up offers while preserving the Historical Use Only safety boundary.
- Chart rendering is delegated to `report.chart.wheel_svg` when available; the built-in SVG shell is only a structured fallback for engine-bound cusp and planet data.
