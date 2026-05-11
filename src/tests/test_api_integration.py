from datetime import datetime, timezone
from pathlib import Path
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from src.api.v1.auth import create_access_token
from src.app import app
from src.database.core import DEFAULT_DATABASE_URL, SessionLocal, _resolve_database_url
from src.database.models import AsyncReportTask, User
from src.engine.user_auth import _as_utc


def test_cloud_run_database_url_is_required():
    with pytest.raises(RuntimeError, match="DATABASE_URL must be set"):
        _resolve_database_url(DEFAULT_DATABASE_URL, is_cloud_run=True)


def test_naive_reset_token_expiry_is_treated_as_utc():
    expires_at = _as_utc(datetime(2026, 5, 8, 1, 0, 0))

    assert expires_at.tzinfo == timezone.utc
    assert expires_at.isoformat() == "2026-05-08T01:00:00+00:00"


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True
    ) as ac:
        # Root serves static files — may be 200 or 404 in test env
        response = await ac.get("/")
        assert response.status_code in [200, 404, 307]


@pytest.mark.asyncio
async def test_healthz_endpoint():
    """Verify /api/healthz returns structured health info."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True
    ) as ac:
        response = await ac.get("/api/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "2.0.0"
        assert "uptime_seconds" in data
        assert isinstance(data["uptime_seconds"], (int, float))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("path", "expected_location"),
    [
        ("/login.html", "/account.html?auth=login"),
        ("/register.html", "/account.html?auth=register"),
        ("/signup.html", "/account.html?auth=register"),
        ("/forgot-password.html", "/account.html?auth=forgot"),
    ],
)
async def test_auth_pages_redirect_to_auth_modal(path, expected_location):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=False
    ) as ac:
        response = await ac.get(path)

    assert response.status_code == 302
    assert response.headers["location"] == expected_location


@pytest.mark.asyncio
async def test_owner_page_is_retired_without_analytics_redirect():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=False
    ) as ac:
        response = await ac.get("/owner.html")

    assert response.status_code == 410
    assert "location" not in response.headers
    assert response.headers["x-robots-tag"] == "noindex, nofollow"
    assert "no-store" in response.headers["cache-control"]


@pytest.mark.asyncio
async def test_reset_password_redirect_preserves_token():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=False
    ) as ac:
        response = await ac.get("/reset-password.html?token=abc+123")

    assert response.status_code == 302
    assert response.headers["location"] == "/account.html?auth=reset&token=abc%20123"


def test_public_nav_exposes_account_entry_link():
    index_html = Path(__file__).resolve().parents[1] / "static" / "index.html"
    text = index_html.read_text(encoding="utf-8")

    assert '<a id="navLoginBtn" href="#" class="nav-link hidden"' in text
    assert '<a id="navAccountBtn" href="/account.html" class="nav-link"' in text
    assert "/js/auth.js?v=astro-v" in text


def test_owner_bootstrap_key_is_not_committed():
    script = Path(__file__).resolve().parents[2] / "check_via_api.py"
    text = script.read_text(encoding="utf-8")

    assert 'OWNER_KEY = "' not in text
    assert "OWNER_BOOTSTRAP_KEY" in text


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/docs", "/redoc", "/openapi.json"])
async def test_api_docs_are_not_public_by_default(path):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=False
    ) as ac:
        response = await ac.get(path)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_account_html_serves_public_account_entry():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=False
    ) as ac:
        response = await ac.get("/account.html")

    assert response.status_code == 200
    assert "location" not in response.headers
    assert "no-store" in response.headers["cache-control"]
    assert "no-cache" in response.headers["cache-control"]
    assert response.headers["pragma"] == "no-cache"
    assert response.headers["expires"] == "0"
    assert response.headers["x-robots-tag"] == "noindex, nofollow"
    assert "My Account" in response.text
    assert "accountLoginAction" in response.text
    assert "accountRegisterAction" in response.text
    assert "/dashboard.html" in response.text
    assert "/js/auth.js?v=astro-v" in response.text


@pytest.mark.asyncio
async def test_dashboard_html_serves_account_surface():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=False
    ) as ac:
        response = await ac.get("/dashboard.html")

    assert response.status_code == 200
    assert "location" not in response.headers
    assert "no-store" in response.headers["cache-control"]
    assert "no-cache" in response.headers["cache-control"]
    assert response.headers["pragma"] == "no-cache"
    assert response.headers["expires"] == "0"
    assert response.headers["x-robots-tag"] == "noindex, nofollow"
    assert "Your Account" in response.text
    assert "Saved Charts" in response.text
    assert "Daily Horoscope Profile" in response.text


@pytest.mark.asyncio
async def test_daily_html_serves_public_horoscope_surface():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=False
    ) as ac:
        response = await ac.get("/daily.html")

    assert response.status_code == 200
    assert "Daily Horoscopes" in response.text
    assert "publicHoroscopeCard" in response.text
    assert "/api/v1/charts/daily-horoscopes" in response.text
    assert "personal-briefing" in response.text


@pytest.mark.asyncio
async def test_compatibility_html_serves_synastry_surface():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=False
    ) as ac:
        response = await ac.get("/compatibility.html")

    assert response.status_code == 200
    assert "Compatibility Through Traditional Synastry" in response.text
    assert "/api/v1/synastry" in response.text
    assert "Compare Two Charts" in response.text


@pytest.mark.asyncio
async def test_synastry_endpoint_uses_chart_options_as_keywords():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True
    ) as ac:
        response = await ac.post(
            "/api/v1/synastry",
            json={
                "person_a": {
                    "name": "Person A",
                    "date": "1996-08-13",
                    "time": "07:18",
                    "city": "Fairfield",
                    "state": "CA",
                    "latitude": 38.2493581,
                    "longitude": -122.039966,
                    "house_system": "W",
                    "zodiac_system": "tropical",
                },
                "person_b": {
                    "name": "Person B",
                    "date": "1990-01-01",
                    "time": "12:00",
                    "city": "London",
                    "state": "UK",
                    "latitude": 51.5072,
                    "longitude": -0.1276,
                    "house_system": "W",
                    "zodiac_system": "tropical",
                },
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert "person_a" in data
    assert "person_b" in data
    assert "synastry" in data
    assert "overall_assessment" in data["synastry"]


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/dashboard", "/dashboard/"])
async def test_dashboard_short_paths_redirect_temporarily(path):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=False
    ) as ac:
        response = await ac.get(path)

    assert response.status_code == 302
    assert response.headers["location"] == "/dashboard.html"


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/account", "/account/"])
async def test_account_short_paths_redirect_temporarily(path):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=False
    ) as ac:
        response = await ac.get(path)

    assert response.status_code == 302
    assert response.headers["location"] == "/account.html"


@pytest.mark.asyncio
async def test_account_workspace_endpoints_for_saved_charts_and_reports():
    db = SessionLocal()
    user_id = f"test-user-{uuid.uuid4().hex}"
    email = f"account-{uuid.uuid4().hex}@example.com"
    task_id = f"task-{uuid.uuid4().hex}"
    try:
        user = User(
            id=user_id,
            email=email,
            name="Account Tester",
            password_hash="not-used",
            salt="",
            charts_saved=[
                {
                    "hash": "seed-chart",
                    "name": "Seed Chart",
                    "date": "1990-01-01",
                    "time": "12:00",
                    "city": "London",
                    "state": "ENG",
                    "house_system": "W",
                    "zodiac_system": "tropical",
                    "saved_at": "2026-05-08T00:00:00+00:00",
                }
            ],
        )
        task = AsyncReportTask(
            id=task_id,
            status="completed",
            request_meta={
                "user_id": user_id,
                "account_email": email,
                "name": "Seed Chart",
                "date": "1990-01-01",
                "time": "12:00",
                "city": "London",
                "state": "ENG",
                "tier": "free_premium",
                "report_iterations": 1,
            },
            result_json={
                "report_markdown": "# Seed Report\n\nThis report is archived.",
                "tier": "free_premium",
                "report_iterations": 1,
            },
        )
        db.add(user)
        db.add(task)
        db.commit()
    finally:
        db.close()

    token = create_access_token("", "free", data={"user_id": user_id})
    headers = {"Authorization": f"Bearer {token}"}

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            follow_redirects=True,
        ) as ac:
            overview = await ac.get("/api/v1/account/overview", headers=headers)
            assert overview.status_code == 200
            overview_data = overview.json()
            assert len(overview_data["charts"]) == 1
            assert len(overview_data["reports"]) == 1

            created = await ac.post(
                "/api/v1/account/charts",
                headers=headers,
                json={
                    "name": "Second Chart",
                    "date": "1996-08-13",
                    "time": "07:18",
                    "city": "Fairfield",
                    "state": "CA",
                    "label": "self",
                },
            )
            assert created.status_code == 200
            assert created.json()["success"] is True

            report = await ac.get(f"/api/v1/account/reports/{task_id}", headers=headers)
            assert report.status_code == 200
            assert "archived" in report.json()["report"]["report_markdown"]

            transits = await ac.get(
                "/api/v1/account/charts/0/transits?days=1&start_date=2026-05-08",
                headers=headers,
            )
            assert transits.status_code == 200
            assert transits.json()["num_days"] == 1
    finally:
        db = SessionLocal()
        try:
            db.query(AsyncReportTask).filter(AsyncReportTask.id == task_id).delete()
            db.query(User).filter(User.id == user_id).delete()
            db.commit()
        finally:
            db.close()


@pytest.mark.asyncio
async def test_custom_404_page():
    """Verify non-existent paths return custom 404 page."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True
    ) as ac:
        response = await ac.get("/this-page-does-not-exist.html")
        assert response.status_code == 404
        assert "Lost Among the Stars" in response.text


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
        "tz": "Europe/London",
    }
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True
    ) as ac:
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
async def test_auth_validate_session(monkeypatch):
    # exchanging session_id (mock) for token
    def fake_retrieve(_session_id):
        raise ValueError("mock Stripe session does not exist")

    monkeypatch.setattr(
        "src.api.v1.endpoints.billing.stripe.checkout.Session.retrieve",
        fake_retrieve,
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True
    ) as ac:
        response = await ac.get(
            "/api/v1/billing/verify-checkout-session", params={"session_id": "mock_id"}
        )
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
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True
    ) as ac:
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
async def test_daily_horoscopes_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True
    ) as ac:
        response = await ac.get(
            "/api/v1/charts/daily-horoscopes",
            params={"target_date": "2026-05-08"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["date"] == "2026-05-08"
    assert data["sky"]["sun"]["sign"]
    assert len(data["horoscopes"]) == 12
    assert {item["sign"] for item in data["horoscopes"]} >= {"Aries", "Pisces"}
    assert data["disclaimer"].startswith("Historical Use Only")


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
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True
    ) as ac:
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
