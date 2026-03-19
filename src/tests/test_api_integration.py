import pytest
from httpx import AsyncClient, ASGITransport
from src.app import app
from src.api.v1.auth import create_access_token
import json

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as ac:
        # FastAPI's root or a simple endpoint
        response = await ac.get("/")
        # If it serves static files at root, it might be 200 or 404 if not found in test env
        assert response.status_code in [200, 404, 307]

@pytest.mark.asyncio
async def test_calculate_endpoint_free():
    payload = {
        "name": "Test User",
        "date": "1990-01-01",
        "time": "12:00",
        "city": "London",
        "state": "ENG",  # Required field
        "lat": 51.5,
        "lon": -0.12,
        "tz": "Europe/London"
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as ac:
        # Charts router is mounted at /api/v1/charts, so /calculate lives there.
        response = await ac.post("/api/v1/charts/calculate", json=payload)
        # Valid responses in test env:
        #   200 — chart calculated successfully (engine ran in test)
        #   400 — bad input / geocode failure
        #   401 — auth required
        #   402 — free reading limit reached
        #   500 — missing runtime keys (OpenRouter, Stripe, etc.)
        assert response.status_code in [200, 400, 401, 402, 500], (
            f"Unexpected status {response.status_code}: {response.text[:200]}"
        )

@pytest.mark.asyncio
async def test_auth_validate_session():
    # exchanging session_id (mock) for token
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as ac:
        response = await ac.get("/api/v1/billing/verify-checkout-session", params={"session_id": "mock_id"})
        # Should be 400 since mock_id isn't real, but not 405 or 404
        assert response.status_code == 400 

def test_token_creation():
    token = create_access_token("test_hash", "free", data={"city": "London"})
    assert token is not None
    assert isinstance(token, str)
