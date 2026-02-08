# 05. Technical Debt & Risk Assessment

## 1. Risk Heatmap (Complex/Fragile Files)

| File | Lines | Risk Factor | Reason |
|------|-------|-------------|--------|
| `src/engine/chart_calculator.py` | ~934 | **HIGH** | God-class. Handles Geocoding, Ephemeris, and 10+ sub-engines. High Cyclomatic Complexity. Extensive use of broad `except Exception` clauses masks potential errors. |
| `src/api/v1/endpoints/charts.py` | ~372 | **MEDIUM** | Mixes HTTP concerns with business logic (LLM fallback, caching rules, auto-save). |
| `src/engine/logic.py` | ~90 | **LOW** | Explicitly marked "DEPRECATED". Exists only for backward compatibility. |
| `src/static/basic.js` | (Unknown) | **MEDIUM** | Front-end logic mentioned in CONTEXT.md. If this handles paywalls client-side without strict backend validation, it's a security risk. |

## 2. Identified Code Smells

### A. The "God Function" in `calculate_chart_data`
The function `calculate_chart_data` in `src/engine/chart_calculator.py` is a massive procedural block (lines 281-934+).
- **Violation**: Single Responsibility Principle.
- **Effect**: Hard to test, hard to maintain. A change to "Phasis" logic could break "Geocoding" if variables leak.
- **Refactoring Strategy**: Extract sub-routines (e.g., `_calculate_geodata`, `_calculate_planetary_positions`, `_apply_classical_rules`).

### B. Legacy Wrappers
`src/engine/logic.py` contains `perform_forensic_audit` which is a wrapper around `Auditor.perform_audit`.
- **Status**: Marked DEPRECATED.
- **Risk**: New features might be added to `Auditor` but missed in the legacy wrapper, causing API divergence between endpoints using different entry points.

### C. Broad Exception Handling
Multiple instances of:
```python
except Exception as e:
    results["error"] = str(e)
```
- **Location**: `chart_calculator.py`.
- **Risk**: Swallows `KeyboardInterrupt` or System exits. Hides specific `ImportErrors` or `SyntaxErrors` during development.
- **Fix**: Catch specific exceptions (`swe.Error`, `GeocoderServiceError`) and let unexpected ones bubble up or be logged with stack traces.

## 3. Security Risks

- **Geocoding User Agent**: Local variable `_ua_base` defaults to "astrology_app/1.0". If many concurrent requests hit Nominatim, this could get IP banned.
- **Client-Side/Backend Duplication**: CAUTION implies `src/static/basic.js` handles some Paywall logic. Ensure `verify_quota` middleware is strictly enforced on ALL premium routes.

## 4. Refactoring Candidates

1.  **Refactor `chart_calculator.py`**: Break into `GeospatialService` and `EphemerisService`.
2.  **Unify Chart Generation**: Ensure B2B and V1 endpoints use the Exact Same Service Method to prevent logic drift.
3.  **Remove `src/engine/logic.py`**: Update all consumers to use `Auditor` directly and delete the wrapper.
