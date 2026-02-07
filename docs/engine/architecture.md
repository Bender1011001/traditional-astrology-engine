# Engine Architecture

This page details the modular architecture of the Codex Caelestis engine.

## Directory Structure

* `src/engine/`: Core logic and AI synthesis.
  * `forensic_engine.py`: The Auditor class (Hub).
  * `dignities.py`: Essential dignity calculations.
  * `kakosis.py`: Maltreatment logic.
  * `synthesis.py`: Narrative construction.
  * `chat_oracle.py`: LLM integration for plain-language readings.
* `src/services/`: Integration and Bridge layers.
  * `engine_bridge.py`: Async wrapper for heavy engine calculations.
  * `subscription.py`: Stripe integration and plan management.
  * `fulfillment.py`: PDF generation and email delivery.
* `src/database/`: Persistence layer.
  * `core.py`: Database engine and session management.
  * `models.py`: SQLAlchemy ORM definitions for Users, Subscriptions, and Saved Charts.

## Calculation & Report Flow

1. Request Elevation: FastAPI receives the chart request and elevates it to the `engine_bridge`.
2. Ephemeris Layer: `ChartCalculator` pulls planetary positions using Swiss Ephemeris (`swisseph`).
3. Auditor Execution: The `Auditor` processes raw positions through the **Rule Ledger**.
4. Narrative Synthesis: `ReportSynthesizer` builds the markdown report from technical findings.
5. AI Enhancement: (Paid Tier Only) `ChatOracle` sends the report to the LLM for plain-language interpretation.
6. Caching: The final result is hashed and cached via `Redis`.

## Design Patterns

*   **Statelessness**: Engines are designed to be stateless, accepting a `Chart` object and returning a Dict.
*   **Bridge Pattern**: `engine_bridge.py` decouples the computationally heavy engine from the async web server.
*   **Dependency Injection**: The `Auditor` injects derived data (like day/night sect) into sub-engines.
