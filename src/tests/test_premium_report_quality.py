import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.v1.endpoints import premium
from src.app import app
from src.database.core import Base, get_db
from src.database.models import AsyncReportTask, GuestRequest
from src.services.premium_generator import (
    RAW_APPENDIX_MARKER,
    build_customer_facing_report_markdown,
    ensure_customer_report_quality,
    llm_iterations_for_tier,
)


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False,
    )
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield session
    finally:
        app.dependency_overrides.clear()
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_customer_report_removes_legacy_front_loaded_appendix():
    raw_report = f"""# PREMIUM NATAL CHART READING

{RAW_APPENDIX_MARKER}

| Body | Position |
|---|---|
| Sun | Leo |

# Part 1

This is a substantial interpretive section about the nativity. It describes the
chart in ordinary customer-facing language and does not force the reader to
parse raw audit tables before receiving the paid interpretation.
"""

    customer_report = build_customer_facing_report_markdown(raw_report)

    assert RAW_APPENDIX_MARKER not in customer_report
    assert "| Body | Position |" not in customer_report
    assert "# Part 1" in customer_report
    assert "substantial interpretive section" in customer_report


def test_customer_report_removes_trailing_technical_appendix():
    raw_report = f"""# PREMIUM NATAL CHART READING

# Part 1

This is the actual reading body.

---

## Technical Appendix

{RAW_APPENDIX_MARKER}

Internal calculation table.
"""

    customer_report = build_customer_facing_report_markdown(raw_report)

    assert RAW_APPENDIX_MARKER not in customer_report
    assert "## Technical Appendix" not in customer_report
    assert "Internal calculation table" not in customer_report
    assert "This is the actual reading body." in customer_report


def test_appendix_only_report_is_rejected():
    raw_report = f"""# PREMIUM NATAL CHART READING

{RAW_APPENDIX_MARKER}

Internal calculation table.
"""

    with pytest.raises(RuntimeError, match="interpretive customer content"):
        ensure_customer_report_quality(raw_report)


@pytest.mark.parametrize(
    ("tier", "expected_iterations"),
    [
        ("full_reading", 1),
        ("single_reading", 1),
        ("free_premium", 1),
        ("free_premium_trial", 1),
        ("premium_audit", 3),
        ("complete_analysis", 3),
        ("forensic_nativity", 6),
        ("top", 6),
    ],
)
def test_llm_iterations_are_tiered(tier, expected_iterations):
    assert llm_iterations_for_tier(tier) == expected_iterations


@pytest.mark.asyncio
async def test_free_premium_trial_allows_one_report_per_ip(db_session, monkeypatch):
    payload = {
        "name": "Test User",
        "date": "1996-08-13",
        "time": "07:18",
        "city": "Fairfield",
        "state": "CA",
    }

    async def fake_generate_task(task_id, request_meta):
        return None

    monkeypatch.setattr(premium, "generate_premium_report_task", fake_generate_task)
    monkeypatch.setattr(premium, "notify_chart_created", lambda *_args, **_kwargs: None)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=False
    ) as ac:
        response = await ac.post(
            "/api/v1/premium/free-trial/request",
            json=payload,
            headers={"x-forwarded-for": "203.0.113.10"},
        )
        second_response = await ac.post(
            "/api/v1/premium/free-trial/request",
            json=payload,
            headers={"x-forwarded-for": "203.0.113.10"},
        )

    assert response.status_code == 200
    assert response.json()["status"] == "started"
    assert response.json()["tier"] == "premium_audit"
    assert response.json()["free_entitlement"] == "one_free_best_reading_per_ip"
    assert response.json()["report_iterations"] == 3
    assert response.json()["free_premium_remaining"] == 0

    task = db_session.query(AsyncReportTask).one()
    assert task.status == "pending"
    assert task.request_meta["tier"] == "premium_audit"
    assert task.request_meta["free_entitlement"] == "one_free_best_reading_per_ip"
    assert task.request_meta["report_iterations"] == 3

    usage = db_session.query(GuestRequest).one()
    assert usage.ip_address == "203.0.113.10"
    assert usage.request_type == premium.FREE_PREMIUM_REQUEST_TYPE

    assert second_response.status_code == 200
    assert second_response.json()["status"] == "limit_reached"
    assert db_session.query(GuestRequest).count() == 1
