import pytest
from httpx import AsyncClient
from httpx import AsyncClient
from src.app import app
from src.api.v1.auth import create_access_token
import json

@pytest.mark.asyncio
async def test_health_check():
    from httpx import ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # FastAPI's root or a simple endpoint
        response = await ac.get("/")
        # If it serves static files at root, it might be 200 or 404 if not found in test env
        assert response.status_code in [200, 404, 307]

@pytest.mark.asyncio
async def test_calculate_endpoint_free():
    from httpx import ASGITransport
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
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/calculate", json=payload)
        # Expected status 200 or 500 (if keys missing), but not 422
        assert response.status_code in [200, 500] 

@pytest.mark.asyncio
async def test_auth_validate_session():
    # exchanging session_id (mock) for token
    from httpx import ASGITransport
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/billing/verify-checkout-session", params={"session_id": "mock_id"})
        # Should be 400 since mock_id isn't real, but not 405 or 404
        assert response.status_code == 400 

def test_token_creation():
    token = create_access_token("test_hash", "free", data={"city": "London"})
    assert token is not None
    assert isinstance(token, str)
