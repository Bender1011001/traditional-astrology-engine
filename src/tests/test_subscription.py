"""Unit tests for the Stripe Subscription Service."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from src.database.models import (SubscriptionPlan, User, UserSubscription)
from src.services.subscription import SubscriptionService


class StripeLikeObject:
    """Minimal StripeObject facsimile: item/attribute access, no .get()."""

    def __init__(self, **values):
        self._values = values

    def __getitem__(self, key):
        return self._values[key]

    def __getattr__(self, key):
        try:
            return self._values[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def to_dict_recursive(self):
        return dict(self._values)


@pytest.fixture
def mock_db_session():
    return MagicMock()


@pytest.fixture
def service(mock_db_session):
    return SubscriptionService(db=mock_db_session)


@pytest.fixture
def test_user():
    user = User(id=1, email="test@example.com")
    return user


@pytest.fixture
def free_plan():
    return SubscriptionPlan(
        id=1, tier="free", stripe_price_id_monthly=None, chart_quota=1, api_quota=0
    )


@pytest.fixture
def pro_plan():
    return SubscriptionPlan(
        id=2,
        tier="scholar",
        stripe_price_id_monthly="price_123",
        chart_quota=10,
        api_quota=100,
    )


def test_start_trial_free_plan(service, mock_db_session, test_user, free_plan):
    """Testing starting a free tier (which should setup active sub, not a trial)."""
    service.get_plan_by_tier = MagicMock(return_value=free_plan)

    sub = service.start_trial(test_user, plan_tier="free")

    assert sub.status == "active"
    assert sub.plan_id == 1
    assert sub.trial_start_date is None
    assert sub.trial_end_date is None
    assert sub.current_period_end is None  # Free plan doesn't end period implicitly
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()


def test_start_trial_pro_plan(service, mock_db_session, test_user, pro_plan):
    """Testing starting a standard trial on a pro plan."""
    service.get_plan_by_tier = MagicMock(return_value=pro_plan)

    sub = service.start_trial(test_user, plan_tier="scholar", trial_days=14)

    assert sub.status == "trial"
    assert sub.plan_id == 2
    assert sub.trial_start_date is not None
    assert sub.trial_end_date is not None
    assert (sub.trial_end_date - sub.trial_start_date).days == 14
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()


@patch("stripe.Price.retrieve")
@patch("stripe.checkout.Session.create")
def test_create_checkout_session_recurring(
    mock_stripe_checkout, mock_stripe_price, service, test_user, pro_plan
):
    """Test creating a standard recurring subscription checkout session."""
    service.get_plan_by_tier = MagicMock(return_value=pro_plan)

    # Mock price retrieve to indicate recurring
    mock_price = MagicMock()
    mock_price.recurring = {"interval": "month"}
    mock_stripe_price.return_value = mock_price

    mock_session = MagicMock()
    mock_session.id = "cs_test_123"
    mock_stripe_checkout.return_value = mock_session

    session = service.create_checkout_session(
        user=test_user,
        plan_tier="scholar",
        success_url="http://example.com/success",
        cancel_url="http://example.com/cancel",
    )

    assert session.id == "cs_test_123"

    # Check that mode is subscription and it passed correct arguments
    mock_stripe_checkout.assert_called_once()
    kwargs = mock_stripe_checkout.call_args[1]
    assert kwargs["mode"] == "subscription"
    assert kwargs["customer_email"] == "test@example.com"
    assert kwargs["client_reference_id"] == 1
    assert kwargs["line_items"][0]["price"] == "price_123"
    assert kwargs["subscription_data"]["metadata"]["plan_tier"] == "scholar"
    assert "{CHECKOUT_SESSION_ID}" in kwargs["success_url"]


@patch("stripe.Price.retrieve")
@patch("stripe.checkout.Session.create")
def test_create_checkout_session_onetime(
    mock_stripe_checkout, mock_stripe_price, service, test_user
):
    """Test creating a one-time purchase checkout session."""
    onetime_plan = SubscriptionPlan(
        id=3, tier="onetime", stripe_price_id_monthly="price_one_time"
    )
    service.get_plan_by_tier = MagicMock(return_value=onetime_plan)

    # Mock price retrieve to indicate one-time (no recurring component)
    mock_price = MagicMock()
    mock_price.recurring = None
    mock_stripe_price.return_value = mock_price

    mock_session = MagicMock()
    mock_session.id = "cs_test_456"
    mock_stripe_checkout.return_value = mock_session

    session = service.create_checkout_session(user=test_user, plan_tier="onetime")

    kwargs = mock_stripe_checkout.call_args[1]
    assert kwargs["mode"] == "payment"
    assert "invoice_creation" in kwargs
    assert kwargs["invoice_creation"]["enabled"] is True


def test_process_subscription_success_new_sub(service, mock_db_session, pro_plan):
    """Test webhook logic when a checkout.session.completed hits."""
    # Simulate DB user lookup
    user = User(id=1, email="webhook@example.com")
    mock_db_session.query().filter().first.return_value = user
    service.get_plan_by_tier = MagicMock(return_value=pro_plan)

    # session dict from Stripe
    session_data = {
        "client_reference_id": 1,
        "metadata": {"plan_tier": "scholar"},
        "subscription": "sub_123",
        "customer": "cus_123",
        "mode": "subscription",
    }

    # We must patch stripe.Subscription.retrieve because process_subscription_success calls it
    with patch("stripe.Subscription.retrieve") as mock_stripe_sub:
        mock_stripe_sub.return_value = MagicMock(
            current_period_start=1600000000,
            current_period_end=1602592000,
            get=MagicMock(return_value="active"),  # not trialing
        )
        with patch(
            "src.services.notifications.AdminNotificationService.notify_purchase_completed"
        ) as mock_notify:
            service._process_subscription_success(session_data)

            # Sub should be created and activated
            assert hasattr(user, "subscription") or mock_db_session.add.called
            mock_notify.assert_called_once()


def test_process_subscription_success_accepts_stripe_object(service, mock_db_session, pro_plan):
    """Stripe SDK webhook objects do not expose dict.get()."""
    user = User(id=1, email="webhook@example.com")
    mock_db_session.query().filter().first.return_value = user
    service.get_plan_by_tier = MagicMock(return_value=pro_plan)

    session_data = StripeLikeObject(
        client_reference_id=1,
        metadata=StripeLikeObject(plan_tier="scholar"),
        subscription="sub_123",
        customer="cus_123",
        mode="subscription",
        amount_total=500,
    )

    stripe_sub = StripeLikeObject(
        current_period_start=1600000000,
        current_period_end=1602592000,
        status="active",
    )

    with patch("stripe.Subscription.retrieve", return_value=stripe_sub):
        with patch(
            "src.services.notifications.AdminNotificationService.notify_purchase_completed"
        ) as mock_notify:
            service._process_subscription_success(session_data)

    created_sub = mock_db_session.add.call_args.args[0]
    assert created_sub.plan_id == 2
    assert created_sub.stripe_customer_id == "cus_123"
    assert created_sub.stripe_subscription_id == "sub_123"
    assert created_sub.status == "active"
    mock_notify.assert_called_once()


def test_process_subscription_success_ignores_unowned_stripe_object(
    service, mock_db_session
):
    """Retired one-time checkout retries should return cleanly when no user is present."""
    session_data = StripeLikeObject(
        client_reference_id=None,
        metadata=StripeLikeObject(tier="horary_question"),
        subscription=None,
        customer=None,
        mode="payment",
        amount_total=500,
    )

    service._process_subscription_success(session_data)

    mock_db_session.query.assert_not_called()


def test_get_usage_stats(service, mock_db_session, pro_plan, test_user):
    # Setup user with an active sub
    sub = UserSubscription(
        id=99,
        plan=pro_plan,
        status="active",
        current_period_start=datetime.now(timezone.utc),
    )
    test_user.subscription = sub

    # Mock scalar() returned from func.sum
    mock_db_session.query().filter().scalar.side_effect = [5, 50]  # charts, api

    stats = service.get_usage_stats(test_user)

    assert stats["charts"] == 5
    assert stats["api"] == 50
    assert stats["chart_limit"] == 10
    assert stats["api_limit"] == 100
