# Testing Strategy

Codex Caelestis uses `pytest` for its testing suite, covering both unit tests for the calculation engine and integration tests for the API.

## Test Structure

Tests are located in `src/tests/` and adhere to standard pytest discovery rules (`test_*.py`).

*   **Unit Tests**: Verify the accuracy of astrological calculations.
    *   `test_primary_directions.py`: Predictive mechanics.
    *   `test_vitality.py`: Hyleg/Alcocoden logic.
*   **Integration Tests**: Verify API endpoints and database interactions.
    *   `test_api_integration.py`: End-to-end endpoint testing using `httpx`.
    *   `test_db_auth.py`: User registration and authentication flows.

## Running Tests

### 1. Install Dependencies
Ensure you have the test dependencies installed (included in `requirements.txt`).
*   `pytest`
*   `pytest-asyncio`
*   `httpx`

### 2. Execute Suite
Run all tests from the project root:

```bash
pytest src/tests
```

### 3. Run Specific Test
```bash
pytest src/tests/test_api_integration.py
```

## Continuous Integration

Tests should be run before any deployment to production to ensure no regressions in calculation accuracy or API stability.
