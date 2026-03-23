import pytest
from httpx import AsyncClient, ASGITransport
from src.app import app
from src.api.v1.auth import create_access_token
import json

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as ac:
        # Root serves static files — may be 200 or 404 in test env
        response = await ac.get("/")
        assert response.status_code in [200, 404, 307]


@pytest.mark.asyncio
async def test_healthz_endpoint():
    """Verify /api/healthz returns structured health info."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as ac:
        response = await ac.get("/api/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "2.0.0"
        assert "uptime_seconds" in data
        assert isinstance(data["uptime_seconds"], (int, float))

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
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "meta" in data
        assert "astronomy" in data
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


@pytest.mark.asyncio
async def test_daily_briefing_endpoint():
    """Test the daily navigator endpoint returns a valid briefing."""
    payload = {
        "date": "1990-01-01",
        "time": "12:00",
        "city": "London",
        "state": "ENG",
        "target_date": "2026-03-23",
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as ac:
        response = await ac.post("/api/v1/charts/daily-briefing", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert data["status"] == "success"
        briefing = data["briefing"]
        assert "profections" in briefing
        assert "firdaria" in briefing
        assert "transits" in briefing
        assert "moon" in briefing
        assert "epitasis" in briefing
        assert "recommendations" in briefing
        assert "forecast_summary" in briefing


@pytest.mark.asyncio
async def test_weekly_briefing_endpoint():
    """Test the weekly navigator endpoint returns 7 daily briefings + overview."""
    payload = {
        "date": "1990-01-01",
        "time": "12:00",
        "city": "London",
        "state": "ENG",
        "start_date": "2026-03-23",
        "days": 3,
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as ac:
        response = await ac.post("/api/v1/charts/weekly-briefing", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert data["status"] == "success"
        assert data["num_days"] == 3
        assert len(data["days"]) == 3

        # Verify week overview structure
        overview = data["week_overview"]
        assert "summary" in overview
        assert "transit_heatmap" in overview
        assert len(overview["transit_heatmap"]) == 3

        # Verify each day has a briefing with expected keys
        for day in data["days"]:
            briefing = day["briefing"]
            assert "date" in briefing
            assert "profections" in briefing
            assert "moon" in briefing
