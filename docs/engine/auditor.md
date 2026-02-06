# The Auditor (Forensic Engine)

The `Auditor` class (formerly `ForensicEngine`) is the orchestration hub of the Codex Caelestis. It serves as the "Single Source of Truth" for all astrological calculations.

## Architecture

The Auditor does not perform calculations itself; it delegates them to specialized sub-engines.

### Hierarchy
*   **Auditor** (Hub)
    *   `ChartCalculator` (Astronomy/Ephemeris)
    *   `DignityCalculator` (Essential Dignity)
    *   `ReceptionEngine` (Planetary Relationships)
    *   `MedicalAstrology` (Iatromathematics)
    *   `MundaneEngine` (Global Context/Overrides)
    *   `PrimaryDirectionsEngine` (Predictive)

## Methods

### `perform_audit`
The core logic method. It runs the entire suite of analyses and generates the **Rule Ledger**.

```python
def perform_audit(chart, jd, birth_dt, ans_date, age):
    # ... coordinates all sub-engines ...
    return full_analysis_dict
```

### `generate_full_nativity`
The public API entry point. It handles:
1.  **Chart Calculation**: Calling Swiss Ephemeris.
2.  **Audit Execution**: Running `perform_audit`.
3.  **Bifurcation**: Splitting output into `technical_data` (machine-readable) and `human_translation` (markdown reports).

## Rule Ledger
The Auditor's most important output is the *Rule Ledger*. This is a linear list of every logical "check" performed during analysis, tagged with a unique Rule ID and Source Citation.
