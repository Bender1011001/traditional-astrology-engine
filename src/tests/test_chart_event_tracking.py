import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.v1.endpoints import premium
from src.database.core import Base, get_db
from src.database.models import ChartEvent, GuestRequest, ReadingFeedbackEvent
from src.app import app


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


@pytest.mark.asyncio
async def test_free_chart_request_persists_chart_event_and_feedback(
    db_session, monkeypatch
):
    def fake_generate_free_reading(**kwargs):
        return {
            "status": "completed",
            "reading_html": "<article>Durable reading</article>",
            "chart_data_summary": {
                "sun_sign": "Aries",
                "moon_sign": "Cancer",
                "rising_sign": "Libra",
                "sect": "DAY",
                "age": 36,
            },
            "error": None,
        }

    monkeypatch.setattr(premium, "generate_free_reading", fake_generate_free_reading)
    monkeypatch.setattr(premium, "notify_chart_created", lambda *args, **kwargs: None)

    payload = {
        "name": "Guest",
        "date": "1990-01-01",
        "time": "12:00",
        "city": "London",
        "state": "ENG",
        "time_unknown": True,
    }
    headers = {
        "X-Forwarded-For": "203.0.113.10",
        "User-Agent": "pytest-chart-browser",
        "Referer": "https://traditional-astrology.com/#get-reading",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True,
    ) as ac:
        response = await ac.post(
            "/api/v1/premium/guest/request", json=payload, headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["chart_event_id"]
        assert data["reading_hash"]

        chart_event = (
            db_session.query(ChartEvent)
            .filter(ChartEvent.id == data["chart_event_id"])
            .one()
        )
        assert chart_event.status == "completed"
        assert chart_event.client_ip == "203.0.113.10"
        assert chart_event.user_agent == "pytest-chart-browser"
        assert chart_event.referer == "https://traditional-astrology.com/#get-reading"
        assert chart_event.request_payload["date"] == "1990-01-01"
        assert chart_event.request_payload["time_unknown"] is True
        assert chart_event.chart_summary["sect"] == "DAY"
        assert chart_event.reading_html == "<article>Durable reading</article>"

        assert db_session.query(GuestRequest).count() == 1

        feedback_response = await ac.post(
            "/api/v1/reading_feedback",
            json={
                "chart_event_id": data["chart_event_id"],
                "reading_hash": data["reading_hash"],
                "vote": "good",
                "source": "b2c_free_chart",
                "birth": payload,
                "meta": {"chart_summary": data["chart_summary"]},
                "time_unknown": True,
            },
            headers=headers,
        )

    assert feedback_response.status_code == 200
    feedback_data = feedback_response.json()
    assert feedback_data["status"] == "feedback_saved"
    assert feedback_data["vote"] == "good"
    assert feedback_data["counts"] == {
        "total": 1,
        "good": 1,
        "bad": 0,
        "up": 1,
        "down": 0,
    }

    feedback = db_session.query(ReadingFeedbackEvent).one()
    assert feedback.chart_event_id == data["chart_event_id"]
    assert feedback.vote == "good"
    assert feedback.birth["city"] == "London"
