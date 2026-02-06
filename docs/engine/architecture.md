# Engine Architecture

This page details the modular architecture of the Codex Caelestis engine.

## Directory Structure

*   `src/engine/`: Core logic.
    *   `forensic_engine.py`: The Auditor class (Hub).
    *   `dignities.py`: Essential dignity calculations (Ptolemy/Egyptian terms).
    *   `primary_directions.py`: Predictive mechanics.
*   `src/database/`: Persistence layer.
    *   `db_manager.py`: Database connection and backup utils.
    *   `models.py`: SQLAlchemy ORM definitions.

## Design Patterns

*   **Statelessness**: Engines are designed to be stateless where possible, accepting a `Chart` object and returning a Dict.
*   **Dependency Injection**: The `Auditor` injects derived data (like day/night sect) into sub-engines.
