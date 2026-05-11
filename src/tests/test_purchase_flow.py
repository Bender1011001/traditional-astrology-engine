import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.v1.endpoints import billing, guest_checkout, horary
from src.api.v1.auth import create_access_token
from src.app import app
from src.database.core import Base, get_db
from src.database.models import (
    AsyncReportTask,
    GuestRequest,
    SubscriptionPlan,
    UsageRecord,
    User,
    UserSubscription,
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
async def test_generate_paid_reading_returns_ga4_purchase_metadata(
    db_session, monkeypatch
):
    background_calls = []
    chart_data = {
        "date": "1990-01-01",
        "time": "12:00",
        "city": "London",
        "state": "United Kingdom",
        "name": "Paid Guest",
    }
    paid_session = SimpleNamespace(
        id="cs_test_paid_full",
        payment_status="paid",
        amount_total=2500,
        currency="usd",
        metadata={
            "order_id": "ord_full",
            "tier": "full_reading",
            "chart_data": json.dumps(chart_data),
        },
        customer_details=SimpleNamespace(email="paid@example.com"),
        customer_email=None,
    )

    monkeypatch.setattr(guest_checkout.settings, "STRIPE_SECRET_KEY", " sk_test_unit ")
    monkeypatch.setattr(
        guest_checkout.stripe.checkout.Session,
        "retrieve",
        lambda session_id: paid_session,
    )

    async def fake_generate_premium_report_task(task_id, request_meta):
        background_calls.append((task_id, request_meta))

    monkeypatch.setattr(
        guest_checkout,
        "generate_premium_report_task",
        fake_generate_premium_report_task,
    )
    monkeypatch.setattr(guest_checkout, "notify_chart_created", lambda *_args: None)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="https://traditional-astrology.test"
    ) as ac:
        response = await ac.post(
            "/api/v1/guest/generate-paid",
            params={"session_id": "cs_test_paid_full"},
            headers={"X-Forwarded-For": "203.0.113.55"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "cs_test_paid_full"
    assert data["tier"] == "full_reading"
    assert data["purchase"] == {
        "transaction_id": "cs_test_paid_full",
        "order_id": "ord_full",
        "currency": "USD",
        "value": 25.0,
        "amount_cents": 2500,
        "tier": "full_reading",
        "items": [
            {
                "item_id": "full_reading",
                "item_name": "Full Natal Chart Reading",
                "item_category": "paid_reading",
                "price": 25.0,
                "quantity": 1,
            }
        ],
    }

    task = (
        db_session.query(AsyncReportTask)
        .filter(AsyncReportTask.id == "cs_test_paid_full")
        .one()
    )
    assert task.request_meta["tier"] == "full_reading"
    assert task.request_meta["customer_email"] == "paid@example.com"

    usage = (
        db_session.query(GuestRequest).filter_by(request_type="paid_full_reading").one()
    )
    assert usage.ip_address == "203.0.113.55"
    assert background_calls[0][0] == "cs_test_paid_full"


def _create_user(db_session, user_id="user_horary", email="horary@example.com"):
    user = User(
        id=user_id,
        email=email,
        name="Horary User",
        password_hash="not-used",
        salt="",
    )
    db_session.add(user)
    db_session.commit()
    return user


def _auth_header(user_id="user_horary"):
    token = create_access_token("", "free", data={"user_id": user_id})
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_horary_subscription_checkout_creates_monthly_session(
    db_session, monkeypatch
):
    created_kwargs = {}
    _create_user(db_session)

    monkeypatch.setattr(horary.settings, "STRIPE_SECRET_KEY", " sk_test_unit\r\n")
    monkeypatch.setattr(
        horary, "_get_or_create_horary_subscription_price", lambda: "price_horary_monthly"
    )

    def fake_session_create(**kwargs):
        created_kwargs.update(kwargs)
        return SimpleNamespace(
            id="cs_test_horary_sub",
            url="https://checkout.stripe.test/cs_test_horary_sub",
        )

    monkeypatch.setattr(horary.stripe.checkout.Session, "create", fake_session_create)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="https://traditional-astrology.test"
    ) as ac:
        response = await ac.post(
            "/api/v1/horary/subscription/checkout",
            headers=_auth_header(),
        )

    assert response.status_code == 200
    assert horary.stripe.api_key == "sk_test_unit"
    assert response.json()["url"] == "https://checkout.stripe.test/cs_test_horary_sub"
    assert created_kwargs["mode"] == "subscription"
    assert created_kwargs["line_items"] == [
        {"price": "price_horary_monthly", "quantity": 1}
    ]
    assert created_kwargs["success_url"].startswith(
        "https://traditional-astrology.test/horary.html?horary_subscribed=success"
    )
    assert created_kwargs["cancel_url"] == (
        "https://traditional-astrology.test/horary.html?horary_subscribed=cancelled"
    )
    assert created_kwargs["customer_email"] == "horary@example.com"
    assert created_kwargs["client_reference_id"] == "user_horary"
    assert created_kwargs["metadata"]["purchase_type"] == "horary_subscription"
    assert created_kwargs["metadata"]["tier"] == "horary"
    assert created_kwargs["metadata"]["plan_tier"] == "horary"

    plan = db_session.query(SubscriptionPlan).filter_by(tier="horary").one()
    assert float(plan.price_monthly) == 5.0
    assert plan.stripe_price_id_monthly == "price_horary_monthly"


@pytest.mark.asyncio
async def test_subscriber_horary_answer_requires_active_subscription_and_persists(
    db_session, monkeypatch
):
    user = _create_user(db_session)
    plan = SubscriptionPlan(
        id="plan_horary",
        tier="horary",
        chart_quota=None,
        api_quota=0,
        price_monthly=5.00,
        price_annual=0.00,
        stripe_price_id_monthly="price_horary_monthly",
        features={"horary_unlimited": True},
    )
    db_session.add(plan)
    db_session.add(
        UserSubscription(
            user_id=user.id,
            plan_id=plan.id,
            status="active",
            stripe_customer_id="cus_horary",
            stripe_subscription_id="sub_horary",
            current_period_start=datetime.now(timezone.utc),
            current_period_end=datetime.now(timezone.utc) + timedelta(days=30),
        )
    )
    db_session.commit()

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

    monkeypatch.setattr(horary, "_build_horary_answer", fake_build_answer)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="https://traditional-astrology.test"
    ) as ac:
        response = await ac.post(
            "/api/v1/horary/subscriber-answer",
            json={
                "question": "Will the package arrive?",
                "city": "London",
                "state": "UK",
            },
            headers={**_auth_header(), "X-Forwarded-For": "203.0.113.42"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["paid"] is True
    assert data["subscription_active"] is True
    assert data["question"] == "Will the package arrive?"
    assert data["oracle"]["verdict"] == "YES"
    assert data["access"]["active"] is True
    assert data["access"]["uses_llm"] is False

    task = (
        db_session.query(AsyncReportTask)
        .filter(AsyncReportTask.id == data["task_id"])
        .one()
    )
    assert task.status == "completed"
    assert task.request_meta["tier"] == "horary_subscription"
    assert task.request_meta["user_id"] == "user_horary"
    assert task.result_json["oracle"]["verdict"] == "YES"

    usage = (
        db_session.query(GuestRequest)
        .filter_by(request_type="subscription_horary_question")
        .one()
    )
    assert usage.ip_address == "203.0.113.42"
    usage_record = db_session.query(UsageRecord).filter_by(
        resource_type="horary_question"
    ).one()
    assert usage_record.user_id == "user_horary"
    assert usage_record.cost_credits == 1


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

    monkeypatch.setattr(billing.settings, "STRIPE_WEBHOOK_SECRET", " unit_webhook_secret\r\n")

    def fake_construct_event(payload, sig_header, secret):
        assert payload == b"{}"
        assert sig_header == "sig_unit"
        assert secret == "unit_webhook_secret"
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


@pytest.mark.asyncio
async def test_guest_checkout_webhook_accepts_stripe_object_without_get(
    db_session, monkeypatch
):
    class StripeLike:
        def __init__(self, **fields):
            self._fields = fields

        def __getitem__(self, key):
            if key in self._fields:
                return self._fields[key]
            raise KeyError(key)

        def __getattr__(self, key):
            try:
                return self[key]
            except KeyError as exc:
                raise AttributeError(key) from exc

        def to_dict_recursive(self):
            converted = {}
            for key, value in self._fields.items():
                if hasattr(value, "to_dict_recursive"):
                    converted[key] = value.to_dict_recursive()
                else:
                    converted[key] = value
            return converted

    background_calls = []
    chart_data = {
        "date": "1982-03-09",
        "time": "19:00",
        "city": "Tecpan",
        "state": "Mexico",
        "name": "Paid Guest",
    }
    session_obj = StripeLike(
        id="cs_test_guest_webhook_stripe_object",
        payment_status="paid",
        metadata=StripeLike(
            tier="premium_audit",
            chart_data=json.dumps(chart_data),
        ),
        customer_details=StripeLike(email="object-paid@example.com"),
    )
    event = {
        "type": "checkout.session.completed",
        "data": {"object": session_obj},
    }

    monkeypatch.setattr(billing.settings, "STRIPE_WEBHOOK_SECRET", "unit_webhook_secret")
    monkeypatch.setattr(
        billing.stripe.Webhook,
        "construct_event",
        lambda _payload, _sig_header, _secret: event,
    )

    async def fake_generate_premium_report_task(task_id, request_meta):
        background_calls.append((task_id, request_meta))

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
        .filter(AsyncReportTask.id == "cs_test_guest_webhook_stripe_object")
        .one()
    )
    assert task.status == "pending"
    assert task.request_meta == {
        **chart_data,
        "tier": "premium_audit",
        "report_iterations": 3,
        "customer_email": "object-paid@example.com",
    }
    assert background_calls == [
        (
            "cs_test_guest_webhook_stripe_object",
            {
                **chart_data,
                "tier": "premium_audit",
                "report_iterations": 3,
                "customer_email": "object-paid@example.com",
            },
        )
    ]
