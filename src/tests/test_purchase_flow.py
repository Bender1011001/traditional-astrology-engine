import json
from types import SimpleNamespace

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.v1.endpoints import billing, guest_checkout, horary
from src.app import app
from src.database.core import Base, get_db
from src.database.models import AsyncReportTask, GuestRequest


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
async def test_guest_checkout_creates_full_reading_session(monkeypatch):
    created_kwargs = {}

    monkeypatch.setattr(
        guest_checkout.settings, "STRIPE_SECRET_KEY", " sk_test_unit\r\n"
    )
    monkeypatch.setattr(
        guest_checkout,
        "_get_or_create_stripe_price",
        lambda tier_key: "price_unit_full",
    )

    def fake_session_create(**kwargs):
        created_kwargs.update(kwargs)
        return SimpleNamespace(
            id="cs_test_full_reading",
            url="https://checkout.stripe.test/cs_test_full_reading",
        )

    monkeypatch.setattr(
        guest_checkout.stripe.checkout.Session, "create", fake_session_create
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="https://traditional-astrology.test"
    ) as ac:
        response = await ac.post(
            "/api/v1/guest/checkout",
            params={
                "tier": "full_reading",
                "date": "1990-01-01",
                "time": "12:00",
                "city": "London",
                "state": "United Kingdom",
                "name": "Launch Smoke",
            },
        )

    assert response.status_code == 200
    assert guest_checkout.stripe.api_key == "sk_test_unit"
    assert response.json()["url"] == "https://checkout.stripe.test/cs_test_full_reading"
    assert created_kwargs["mode"] == "payment"
    assert created_kwargs["line_items"] == [{"price": "price_unit_full", "quantity": 1}]
    assert created_kwargs["success_url"].startswith(
        "https://traditional-astrology.test/?paid=true&session_id="
    )
    assert (
        created_kwargs["cancel_url"]
        == "https://traditional-astrology.test/#get-reading"
    )
    assert created_kwargs["metadata"]["tier"] == "full_reading"

    chart_data = json.loads(created_kwargs["metadata"]["chart_data"])
    assert chart_data == {
        "date": "1990-01-01",
        "time": "12:00",
        "city": "London",
        "state": "United Kingdom",
        "name": "Launch Smoke",
    }


@pytest.mark.asyncio
async def test_guest_checkout_rejects_unknown_tier_without_stripe(monkeypatch):
    monkeypatch.setattr(guest_checkout.settings, "STRIPE_SECRET_KEY", "sk_test_unit")

    def fail_if_called(_tier_key):
        raise AssertionError("Stripe price lookup should not run for invalid tiers")

    monkeypatch.setattr(guest_checkout, "_get_or_create_stripe_price", fail_if_called)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="https://traditional-astrology.test"
    ) as ac:
        response = await ac.post(
            "/api/v1/guest/checkout",
            params={
                "tier": "not_a_product",
                "date": "1990-01-01",
                "time": "12:00",
                "city": "London",
            },
        )

    assert response.status_code == 400
    assert "Invalid tier" in response.json()["detail"]


@pytest.mark.asyncio
async def test_paid_horary_checkout_creates_five_dollar_session(monkeypatch):
    created_kwargs = {}

    monkeypatch.setattr(horary.settings, "STRIPE_SECRET_KEY", " sk_test_unit\r\n")
    monkeypatch.setattr(horary, "_get_or_create_horary_price", lambda: "price_horary")

    def fake_session_create(**kwargs):
        created_kwargs.update(kwargs)
        return SimpleNamespace(
            id="cs_test_horary",
            url="https://checkout.stripe.test/cs_test_horary",
        )

    monkeypatch.setattr(horary.stripe.checkout.Session, "create", fake_session_create)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="https://traditional-astrology.test"
    ) as ac:
        response = await ac.post(
            "/api/v1/horary/checkout",
            json={
                "question": "Will I receive a reply?",
                "city": "London",
                "state": "UK",
            },
        )

    assert response.status_code == 200
    assert horary.stripe.api_key == "sk_test_unit"
    assert response.json()["url"] == "https://checkout.stripe.test/cs_test_horary"
    assert created_kwargs["mode"] == "payment"
    assert created_kwargs["line_items"] == [{"price": "price_horary", "quantity": 1}]
    assert created_kwargs["success_url"].startswith(
        "https://traditional-astrology.test/horary.html?horary_paid=success"
    )
    assert created_kwargs["cancel_url"] == (
        "https://traditional-astrology.test/horary.html?horary_paid=cancelled"
    )
    assert created_kwargs["metadata"]["purchase_type"] == "horary_question"
    assert created_kwargs["metadata"]["tier"] == "horary_question"
    assert created_kwargs["metadata"]["question"] == "Will I receive a reply?"
    assert created_kwargs["metadata"]["city"] == "London"


@pytest.mark.asyncio
async def test_paid_horary_answer_verifies_payment_and_persists(
    db_session, monkeypatch
):
    monkeypatch.setattr(horary.settings, "STRIPE_SECRET_KEY", " sk_test_unit\r\n")

    paid_session = SimpleNamespace(
        id="cs_test_paid_horary",
        payment_status="paid",
        metadata={
            "purchase_type": "horary_question",
            "tier": "horary_question",
            "order_id": "ord_horary",
            "question": "Will the package arrive?",
            "city": "London",
            "state": "UK",
            "date": "",
            "time": "",
            "latitude": "",
            "longitude": "",
        },
    )

    def fake_retrieve(session_id):
        assert session_id == "cs_test_paid_horary"
        return paid_session

    def fake_build_answer(payload):
        return {
            "meta": {"city": payload.city},
            "oracle": {
                "verdict": "YES",
                "total_score": 3,
                "verdict_weight": "strong",
                "strictures": [],
                "conditions": [],
                "querent_sign": "Aries",
                "querent_ruler": "Mars",
                "quesited_label": "Package",
                "quesited_house": 3,
                "quesited_sign": "Gemini",
                "quesited_ruler": "Mercury",
                "moon_sign": "Cancer",
            },
        }

    monkeypatch.setattr(horary.stripe.checkout.Session, "retrieve", fake_retrieve)
    monkeypatch.setattr(horary, "_build_horary_answer", fake_build_answer)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="https://traditional-astrology.test"
    ) as ac:
        response = await ac.post(
            "/api/v1/horary/paid-answer",
            params={"session_id": "cs_test_paid_horary"},
            headers={"X-Forwarded-For": "203.0.113.42"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["paid"] is True
    assert data["question"] == "Will the package arrive?"
    assert data["session_id"] == "cs_test_paid_horary"
    assert data["oracle"]["verdict"] == "YES"

    task = (
        db_session.query(AsyncReportTask)
        .filter(AsyncReportTask.id == "cs_test_paid_horary")
        .one()
    )
    assert task.status == "completed"
    assert task.request_meta["tier"] == "horary_question"
    assert task.request_meta["order_id"] == "ord_horary"
    assert task.result_json["oracle"]["verdict"] == "YES"

    usage = (
        db_session.query(GuestRequest)
        .filter_by(request_type="paid_horary_question")
        .one()
    )
    assert usage.ip_address == "203.0.113.42"


def test_get_or_create_price_skips_inactive_configured_product(monkeypatch):
    created_price_kwargs = {}

    monkeypatch.setattr(
        guest_checkout.settings, "STRIPE_PRICE_FULL_READING", "price_stale"
    )
    monkeypatch.setattr(
        guest_checkout.settings, "_stripe_price_cache_full_reading", None, raising=False
    )

    def fake_price_retrieve(price_id, expand=None):
        assert price_id == "price_stale"
        assert expand == ["product"]
        return SimpleNamespace(
            id=price_id,
            active=True,
            unit_amount=2500,
            currency="usd",
            product=SimpleNamespace(id="prod_inactive", active=False),
        )

    def fake_price_create(**kwargs):
        created_price_kwargs.update(kwargs)
        return SimpleNamespace(id="price_new_full")

    monkeypatch.setattr(guest_checkout.stripe.Price, "retrieve", fake_price_retrieve)
    monkeypatch.setattr(
        guest_checkout.stripe.Price,
        "search",
        lambda **_kwargs: SimpleNamespace(data=[]),
    )
    monkeypatch.setattr(
        guest_checkout.stripe.Product,
        "create",
        lambda **_kwargs: SimpleNamespace(id="prod_new_full"),
    )
    monkeypatch.setattr(guest_checkout.stripe.Price, "create", fake_price_create)

    price_id = guest_checkout._get_or_create_stripe_price("full_reading")

    assert price_id == "price_new_full"
    assert created_price_kwargs["product"] == "prod_new_full"
    assert created_price_kwargs["unit_amount"] == 2500
    assert created_price_kwargs["currency"] == "usd"
    assert created_price_kwargs["metadata"] == {"tier": "full_reading"}


@pytest.mark.asyncio
async def test_guest_checkout_webhook_fulfills_current_guest_tier(
    db_session, monkeypatch
):
    background_calls = []
    chart_data = {
        "date": "1990-01-01",
        "time": "12:00",
        "city": "London",
        "state": "ENG",
        "name": "Paid Guest",
    }
    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_guest_webhook",
                "payment_status": "paid",
                "metadata": {
                    "tier": "full_reading",
                    "chart_data": json.dumps(chart_data),
                },
                "customer_details": {"email": "paid@example.com"},
            }
        },
    }

    monkeypatch.setattr(billing.settings, "STRIPE_WEBHOOK_SECRET", " whsec_unit\r\n")

    def fake_construct_event(payload, sig_header, secret):
        assert payload == b"{}"
        assert sig_header == "sig_unit"
        assert secret == "whsec_unit"
        return event

    async def fake_generate_premium_report_task(task_id, request_meta):
        background_calls.append((task_id, request_meta))

    monkeypatch.setattr(billing.stripe.Webhook, "construct_event", fake_construct_event)
    monkeypatch.setattr(
        billing, "generate_premium_report_task", fake_generate_premium_report_task
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="https://traditional-astrology.test"
    ) as ac:
        response = await ac.post(
            "/api/v1/billing/webhook",
            content=b"{}",
            headers={"stripe-signature": "sig_unit"},
        )

    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    task = (
        db_session.query(AsyncReportTask)
        .filter(AsyncReportTask.id == "cs_test_guest_webhook")
        .one()
    )
    assert task.status == "pending"
    assert task.request_meta == {
        **chart_data,
        "tier": "full_reading",
        "report_iterations": 1,
        "customer_email": "paid@example.com",
    }

    usage = db_session.query(GuestRequest).one()
    assert usage.ip_address == "webhook"
    assert usage.request_type == "paid_full_reading"
    assert background_calls == [
        (
            "cs_test_guest_webhook",
            {
                **chart_data,
                "tier": "full_reading",
                "report_iterations": 1,
                "customer_email": "paid@example.com",
            },
        )
    ]
