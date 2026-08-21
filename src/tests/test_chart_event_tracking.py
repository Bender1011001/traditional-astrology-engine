import json
import sys
import types

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.v1.endpoints import premium
from src.database.core import Base, get_db
from src.api.v1.schemas import ChartRequest
from src.database.models import (
    AsyncReportTask,
    ChartEvent,
    GuestRequest,
    ReadingEmailOptIn,
    ReadingFeedbackEvent,
)
from src.app import app
from src.services import premium_generator


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
async def test_free_chart_request_starts_complete_llm_task_and_persists_chart_event(
    db_session, monkeypatch
):
    async def fake_generate_premium_report_task(task_id, request_meta):
        return None

    monkeypatch.setattr(
        premium, "generate_premium_report_task", fake_generate_premium_report_task
    )
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
        assert data["status"] == "started"
        assert data["task_id"]
        assert data["chart_event_id"]
        assert data["tier"] == "free_llm_chart"
        assert data["report_iterations"] == 1
        assert data["instant"] is False
        assert data["free_readings_remaining"] is None

        chart_event = (
            db_session.query(ChartEvent)
            .filter(ChartEvent.id == data["chart_event_id"])
            .one()
        )
        assert chart_event.status == "pending"
        assert chart_event.event_type == "free_complete_analysis"
        assert chart_event.client_ip == "203.0.113.10"
        assert chart_event.user_agent == "pytest-chart-browser"
        assert chart_event.referer == "https://traditional-astrology.com/#get-reading"
        assert chart_event.request_payload["date"] == "1990-01-01"
        assert chart_event.request_payload["time_unknown"] is True
        assert chart_event.chart_summary == {}
        assert chart_event.reading_html is None
        assert "email" not in chart_event.request_payload

        assert db_session.query(GuestRequest).count() == 0
        assert db_session.query(ReadingEmailOptIn).count() == 0

        task = (
            db_session.query(AsyncReportTask)
            .filter(AsyncReportTask.id == data["task_id"])
            .one()
        )
        assert task.status == "pending"
        assert task.request_meta["tier"] == "free_llm_chart"
        assert task.request_meta["free_entitlement"] == "free_single_pass_reading"
        assert task.request_meta["report_iterations"] == 1
        assert task.request_meta["chart_event_id"] == data["chart_event_id"]
        assert task.request_meta["time_unknown"] is True
        assert task.request_meta["free_readings_remaining"] is None
        assert "customer_email" not in task.request_meta


@pytest.mark.asyncio
async def test_free_chart_request_is_uncapped_for_repeat_visitors(
    db_session, monkeypatch
):
    async def fake_generate_premium_report_task(task_id, request_meta):
        return None

    monkeypatch.setattr(
        premium, "generate_premium_report_task", fake_generate_premium_report_task
    )
    monkeypatch.setattr(premium, "notify_chart_created", lambda *args, **kwargs: None)

    payload = {
        "name": "Guest",
        "date": "1990-01-01",
        "time": "12:00",
        "city": "London",
        "state": "ENG",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        responses = [
            await ac.post(
                "/api/v1/premium/guest/request",
                json=payload,
                headers={"X-Forwarded-For": "203.0.113.20"},
            )
            for _ in range(6)
        ]

    assert [response.status_code for response in responses] == [200] * 6
    assert db_session.query(AsyncReportTask).count() == 6
    assert db_session.query(ChartEvent).count() == 6
    assert db_session.query(GuestRequest).count() == 0
    assert db_session.query(ReadingEmailOptIn).count() == 0
    assert all(
        response.json()["free_readings_remaining"] is None for response in responses
    )


@pytest.mark.asyncio
async def test_first_llm_task_completes_chart_event(db_session, monkeypatch):
    chart_event = ChartEvent(
        id="chart-event-1",
        event_type="free_complete_analysis",
        status="pending",
        client_ip="203.0.113.10",
        request_payload={
            "name": "Guest",
            "date": "1990-01-01",
            "time": "12:00",
            "city": "London",
            "state": "ENG",
        },
    )
    task = AsyncReportTask(
        id="task-1",
        status="pending",
        request_meta={
            "name": "Guest",
            "date": "1990-01-01",
            "time": "12:00",
            "city": "London",
            "state": "ENG",
            "tier": "premium_audit",
            "free_entitlement": "complete_analysis_free_for_launch",
            "report_iterations": 6,
            "chart_event_id": "chart-event-1",
            "free_readings_remaining": 2,
            "time_unknown": True,
        },
    )
    db_session.add(chart_event)
    db_session.add(task)
    db_session.commit()

    chart_data = {
        "meta": {
            "age": 36,
            "chart": {
                "date": "1990-01-01",
                "time": "12:00",
                "city": "London",
                "state": "ENG",
                "house_system": {"label": "Whole Sign"},
            },
        },
        "astronomy": {"angles": {"Ascendant": 180.0}},
        "analysis": {
            "sect": {"type": "DAY"},
            "planets_forensic": [
                {
                    "name": "Sun",
                    "longitude": 15.0,
                    "longitude_fmt": {"sign": "Aries"},
                },
                {
                    "name": "Moon",
                    "longitude": 95.0,
                    "longitude_fmt": {"sign": "Cancer"},
                },
            ],
        },
        "human_translation": {},
    }
    report_markdown = (
        "# Part 1\n\nHistorical Use Only — not medical, financial, legal, "
        "psychological, emergency, or safety advice.\n\nThis is the complete "
        "LLM report response for the free chart."
    )

    monkeypatch.setattr(
        premium_generator, "SessionLocal", lambda: db_session
    )
    monkeypatch.setattr(
        premium_generator,
        "generate_chart_data",
        lambda **_kwargs: json.dumps(chart_data),
    )
    monkeypatch.setattr(
        premium_generator.PremiumGenerator,
        "generate_premium_report_markdown",
        staticmethod(lambda *_args, **_kwargs: report_markdown),
    )
    monkeypatch.setitem(
        sys.modules,
        "src.engine.trace_generator",
        types.SimpleNamespace(generate_trace=lambda **_kwargs: {"steps": []}),
    )

    await premium_generator.generate_premium_report_task("task-1", task.request_meta)

    refreshed_task = (
        db_session.query(AsyncReportTask).filter(AsyncReportTask.id == "task-1").one()
    )
    refreshed_event = (
        db_session.query(ChartEvent).filter(ChartEvent.id == "chart-event-1").one()
    )

    assert refreshed_task.status == "completed"
    assert refreshed_task.result_json["tier"] == "premium_audit"
    assert refreshed_task.result_json["report_iterations"] == 6
    assert refreshed_task.result_json["chart_event_id"] == "chart-event-1"
    assert refreshed_task.result_json["reading_hash"]

    assert refreshed_event.status == "completed"
    assert refreshed_event.reading_html == report_markdown
    assert refreshed_event.reading_hash == refreshed_task.result_json["reading_hash"]
    assert refreshed_event.chart_summary["sun_sign"] == "Aries"
    assert refreshed_event.chart_summary["moon_sign"] == "Cancer"
    assert refreshed_event.chart_summary["rising_sign"] == "Libra"
    assert refreshed_event.chart_summary["sect"] == "DAY"


def _guest_payload(**overrides):
    payload = {
        "name": "Guest",
        "date": "1990-01-01",
        "time": "12:00",
        "city": "London",
        "state": "ENG",
    }
    payload.update(overrides)
    return payload


def test_chart_request_accepts_valid_optional_email():
    request = ChartRequest(
        date="1990-01-01",
        time="12:00",
        city="London",
        email="  User@Example.COM ",
    )
    assert request.email == "user@example.com"


@pytest.mark.parametrize(
    "email",
    [None, "", "   ", "not-an-email", "missing-domain@", "@nouser.com", "a" * 300, 123],
)
def test_chart_request_drops_invalid_or_blank_email(email):
    kwargs = {"date": "1990-01-01", "time": "12:00", "city": "London"}
    if email is not None:
        kwargs["email"] = email
    request = ChartRequest(**kwargs)
    assert request.email is None


@pytest.mark.asyncio
async def test_free_chart_request_stores_email_opt_in_when_valid(
    db_session, monkeypatch
):
    async def fake_generate_premium_report_task(task_id, request_meta):
        return None

    monkeypatch.setattr(
        premium, "generate_premium_report_task", fake_generate_premium_report_task
    )
    monkeypatch.setattr(premium, "notify_chart_created", lambda *args, **kwargs: None)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True,
    ) as ac:
        response = await ac.post(
            "/api/v1/premium/guest/request",
            json=_guest_payload(email="  Visitor@Example.COM "),
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "started"
    assert data["chart_event_id"]
    assert data["instant"] is False

    opt_in = db_session.query(ReadingEmailOptIn).one()
    assert opt_in.email == "visitor@example.com"
    assert opt_in.chart_event_id == data["chart_event_id"]
    assert opt_in.consented_at is not None

    chart_event = (
        db_session.query(ChartEvent)
        .filter(ChartEvent.id == data["chart_event_id"])
        .one()
    )
    assert "email" not in chart_event.request_payload

    task = (
        db_session.query(AsyncReportTask)
        .filter(AsyncReportTask.id == data["task_id"])
        .one()
    )
    assert task.request_meta["customer_email"] == "visitor@example.com"
    assert task.request_meta["tier"] == "free_llm_chart"


@pytest.mark.parametrize(
    "email",
    ["not-an-email", "", "   ", "missing-domain@", None],
)
@pytest.mark.asyncio
async def test_free_chart_request_ignores_invalid_or_blank_email(
    db_session, monkeypatch, email
):
    async def fake_generate_premium_report_task(task_id, request_meta):
        return None

    monkeypatch.setattr(
        premium, "generate_premium_report_task", fake_generate_premium_report_task
    )
    monkeypatch.setattr(premium, "notify_chart_created", lambda *args, **kwargs: None)

    payload = _guest_payload()
    if email is not None:
        payload["email"] = email

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/api/v1/premium/guest/request", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "started"
    assert data["task_id"]
    assert data["chart_event_id"]
    assert db_session.query(ReadingEmailOptIn).count() == 0

    task = (
        db_session.query(AsyncReportTask)
        .filter(AsyncReportTask.id == data["task_id"])
        .one()
    )
    assert "customer_email" not in task.request_meta


def _completed_task_fixtures(db_session, *, customer_email=None, tier="free_llm_chart"):
    request_meta = {
        "name": "Guest",
        "date": "1990-01-01",
        "time": "12:00",
        "city": "London",
        "state": "ENG",
        "tier": tier,
        "free_entitlement": "free_single_pass_reading",
        "report_iterations": 1,
        "chart_event_id": "chart-event-email-1",
        "free_readings_remaining": None,
    }
    if customer_email:
        request_meta["customer_email"] = customer_email

    chart_event = ChartEvent(
        id="chart-event-email-1",
        event_type="free_complete_analysis",
        status="pending",
        client_ip="203.0.113.10",
        request_payload={
            "name": "Guest",
            "date": "1990-01-01",
            "time": "12:00",
            "city": "London",
            "state": "ENG",
        },
    )
    task = AsyncReportTask(
        id="task-email-1",
        status="pending",
        request_meta=request_meta,
    )
    db_session.add(chart_event)
    db_session.add(task)
    db_session.commit()
    return request_meta


def _patch_successful_generation(monkeypatch, db_session):
    chart_data = {
        "date": "1990-01-01",
        "city": "London",
        "meta": {
            "age": 36,
            "chart": {
                "date": "1990-01-01",
                "time": "12:00",
                "city": "London",
                "state": "ENG",
                "house_system": {"label": "Whole Sign"},
            },
        },
        "astronomy": {"angles": {"Ascendant": 180.0}},
        "analysis": {
            "sect": {"type": "DAY"},
            "planets_forensic": [
                {
                    "name": "Sun",
                    "longitude": 15.0,
                    "longitude_fmt": {"sign": "Aries"},
                },
                {
                    "name": "Moon",
                    "longitude": 95.0,
                    "longitude_fmt": {"sign": "Cancer"},
                },
            ],
        },
        "human_translation": {},
    }
    report_markdown = (
        "# Part 1\n\nHistorical Use Only — not medical, financial, legal, "
        "psychological, emergency, or safety advice.\n\nThis is the complete "
        "LLM report response for the free chart."
    )
    monkeypatch.setattr(premium_generator, "SessionLocal", lambda: db_session)
    monkeypatch.setattr(
        premium_generator,
        "generate_chart_data",
        lambda **_kwargs: json.dumps(chart_data),
    )
    monkeypatch.setattr(
        premium_generator.PremiumGenerator,
        "generate_premium_report_markdown",
        staticmethod(lambda *_args, **_kwargs: report_markdown),
    )
    monkeypatch.setitem(
        sys.modules,
        "src.engine.trace_generator",
        types.SimpleNamespace(generate_trace=lambda **_kwargs: {"steps": []}),
    )
    return report_markdown


class _FakePdfBuffer:
    def getvalue(self):
        return b"%PDF-fake"


class _FakePdfGenerator:
    def __init__(self, *args, **kwargs):
        pass

    def generate(self, custom_content=None):
        return _FakePdfBuffer()


@pytest.mark.asyncio
async def test_completed_free_reading_emails_pdf_copy(db_session, monkeypatch):
    request_meta = _completed_task_fixtures(
        db_session, customer_email="visitor@example.com"
    )
    _patch_successful_generation(monkeypatch, db_session)
    sent = []

    def fake_send_report_email(*args, **kwargs):
        sent.append((args, kwargs))

    monkeypatch.setitem(
        sys.modules,
        "src.engine.pdf_generator",
        types.SimpleNamespace(PDFReportGenerator=_FakePdfGenerator),
    )
    monkeypatch.setattr(
        premium_generator, "_send_report_email", fake_send_report_email
    )

    await premium_generator.generate_premium_report_task("task-email-1", request_meta)

    refreshed_task = (
        db_session.query(AsyncReportTask)
        .filter(AsyncReportTask.id == "task-email-1")
        .one()
    )
    refreshed_event = (
        db_session.query(ChartEvent)
        .filter(ChartEvent.id == "chart-event-email-1")
        .one()
    )

    assert refreshed_task.status == "completed"
    assert refreshed_event.status == "completed"
    assert sent
    args, kwargs = sent[0]
    assert args[0] == "visitor@example.com"
    assert args[2] == b"%PDF-fake"
    assert kwargs["tier"] == "free_llm_chart"


@pytest.mark.asyncio
async def test_free_reading_email_failure_does_not_fail_task(
    db_session, monkeypatch
):
    request_meta = _completed_task_fixtures(
        db_session, customer_email="visitor@example.com"
    )
    report_markdown = _patch_successful_generation(monkeypatch, db_session)

    def fail_send_report_email(*args, **kwargs):
        raise RuntimeError("send_email returned False for visitor@example.com")

    monkeypatch.setitem(
        sys.modules,
        "src.engine.pdf_generator",
        types.SimpleNamespace(PDFReportGenerator=_FakePdfGenerator),
    )
    monkeypatch.setattr(
        premium_generator, "_send_report_email", fail_send_report_email
    )

    await premium_generator.generate_premium_report_task("task-email-1", request_meta)

    refreshed_task = (
        db_session.query(AsyncReportTask)
        .filter(AsyncReportTask.id == "task-email-1")
        .one()
    )
    refreshed_event = (
        db_session.query(ChartEvent)
        .filter(ChartEvent.id == "chart-event-email-1")
        .one()
    )

    assert refreshed_task.status == "completed"
    assert refreshed_event.status == "completed"
    assert refreshed_event.reading_html == report_markdown


def test_free_tier_report_email_subject_and_pdf_attachment(monkeypatch):
    sent = {}

    def fake_send_email(**kwargs):
        sent.update(kwargs)
        return True

    monkeypatch.setattr(premium_generator, "send_email", fake_send_email)
    premium_generator._send_report_email(
        "visitor@example.com",
        "Guest",
        b"%PDF-fake",
        {"date": "1990-01-01", "city": "London"},
        tier="free_llm_chart",
    )

    assert sent["to_email"] == "visitor@example.com"
    assert sent["subject"] == "Your Natal Chart Reading — Traditional Astrology"
    assert sent["attachment_bytes"] == b"%PDF-fake"
    assert "source-cited edition" not in sent["html_content"]
    assert "Your Natal Chart Reading is ready." in sent["html_content"]


def test_paid_tier_report_email_keeps_source_cited_line(monkeypatch):
    sent = {}

    def fake_send_email(**kwargs):
        sent.update(kwargs)
        return True

    monkeypatch.setattr(premium_generator, "send_email", fake_send_email)
    premium_generator._send_report_email(
        "paid@example.com",
        "Guest",
        b"%PDF-fake",
        {"date": "1990-01-01", "city": "London"},
        tier="forensic_nativity",
    )

    assert "This source-cited edition covers" in sent["html_content"]
    assert sent["subject"] == "Your Forensic Nativity Report — Traditional Astrology"


@pytest.mark.asyncio
async def test_reading_feedback_saves_comment_and_notifies_owner(
    db_session, monkeypatch
):
    notifications = []

    monkeypatch.setattr(
        "src.api.v1.endpoints.telemetry.AdminNotificationService.notify_reading_feedback",
        lambda **kwargs: notifications.append(kwargs),
    )

    chart_event = ChartEvent(
        id="feedback-chart-1",
        event_type="free_complete_analysis",
        status="completed",
        client_ip="203.0.113.11",
        request_payload={
            "name": "Guest",
            "date": "1990-01-01",
            "time": "12:00",
            "city": "London",
            "state": "ENG",
        },
        chart_summary={"sect": "DAY"},
        reading_hash="hash-feedback-1",
        reading_html="# Reading",
    )
    db_session.add(chart_event)
    db_session.commit()

    payload = {
        "chart_event_id": "feedback-chart-1",
        "reading_hash": "hash-feedback-1",
        "vote": "bad",
        "source": "b2c_free_chart",
        "birth": {
            "date": "1990-01-01",
            "time": "12:00",
            "city": "London",
            "state": "ENG",
        },
        "meta": {"chart_summary": {"sect": "DAY"}},
        "time_unknown": False,
        "comment": "Career timing felt specific, but the family section felt off.",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="https://traditional-astrology.test",
        follow_redirects=True,
    ) as ac:
        response = await ac.post(
            "/api/v1/reading_feedback",
            json=payload,
            headers={
                "X-Forwarded-For": "203.0.113.12",
                "User-Agent": "pytest-feedback-browser",
                "Referer": "https://traditional-astrology.test/#reading",
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "feedback_saved"
    assert data["vote"] == "bad"
    assert data["counts"] == {
        "total": 1,
        "good": 0,
        "bad": 1,
        "up": 0,
        "down": 1,
    }

    feedback = db_session.query(ReadingFeedbackEvent).one()
    assert feedback.chart_event_id == "feedback-chart-1"
    assert feedback.reading_hash == "hash-feedback-1"
    assert feedback.vote == "bad"
    assert feedback.comment == payload["comment"]
    assert feedback.birth["city"] == "London"
    assert feedback.user_agent == "pytest-feedback-browser"

    assert notifications == [
        {
            "vote": "bad",
            "source": "b2c_free_chart",
            "comment": payload["comment"],
            "chart_event_id": "feedback-chart-1",
            "reading_hash": "hash-feedback-1",
            "birth": payload["birth"],
            "url": "https://traditional-astrology.test/#reading",
            "ua": "pytest-feedback-browser",
        }
    ]
