import logging
import uuid
from datetime import datetime, timezone
from typing import Any

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.api.v1.auth import get_current_user
from src.api.v1.client_ip import get_client_ip
from src.api.v1.schemas import HoraryRequest  # type: ignore
from src.api.v1.utils import result_to_model
from src.core.config import settings
from src.database.core import get_db
from src.database.models import (
    AsyncReportTask,
    GuestRequest,
    SubscriptionPlan,
    UsageRecord,
    User,
)
from src.engine.calculator.main import calculate_chart_data
from src.engine.horary import build_horary_oracle

router = APIRouter()
logger = logging.getLogger(__name__)

HORARY_SUBSCRIPTION_TIER = "horary"
HORARY_SUBSCRIPTION_PRICE_CENTS = 500
HORARY_SUBSCRIPTION_PRODUCT_NAME = "Horary Oracle Unlimited"
_HORARY_SUBSCRIPTION_PRICE_CACHE: str | None = None


def _stripe_field(obj: Any, key: str, default: Any = None) -> Any:
    if hasattr(obj, "get"):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _metadata(obj: Any) -> dict[str, Any]:
    metadata = _stripe_field(obj, "metadata", {}) or {}
    if hasattr(metadata, "to_dict"):
        return dict(metadata.to_dict())
    return dict(metadata)


def _is_ready_horary_subscription_price(price_id: str) -> bool:
    try:
        price = stripe.Price.retrieve(price_id, expand=["product"])
        product = _stripe_field(price, "product")
        if isinstance(product, str):
            product = stripe.Product.retrieve(product)

        metadata = _metadata(price)
        recurring = _stripe_field(price, "recurring", {}) or {}
        return (
            bool(_stripe_field(price, "active", False))
            and bool(_stripe_field(product, "active", False))
            and int(_stripe_field(price, "unit_amount", 0) or 0)
            == HORARY_SUBSCRIPTION_PRICE_CENTS
            and str(_stripe_field(price, "currency", "") or "").lower() == "usd"
            and str(_stripe_field(recurring, "interval", "") or "") == "month"
            and metadata.get("tier") == HORARY_SUBSCRIPTION_TIER
        )
    except Exception as e:
        logger.warning(
            "Stripe horary subscription price validation failed for %s: %s",
            price_id,
            repr(e),
            exc_info=True,
        )
        return False


def _get_or_create_horary_subscription_price() -> str:
    global _HORARY_SUBSCRIPTION_PRICE_CACHE

    if _HORARY_SUBSCRIPTION_PRICE_CACHE and _is_ready_horary_subscription_price(
        _HORARY_SUBSCRIPTION_PRICE_CACHE
    ):
        return _HORARY_SUBSCRIPTION_PRICE_CACHE
    _HORARY_SUBSCRIPTION_PRICE_CACHE = None

    configured = (getattr(settings, "STRIPE_PRICE_HORARY_MONTHLY", "") or "").strip()
    if configured and _is_ready_horary_subscription_price(configured):
        _HORARY_SUBSCRIPTION_PRICE_CACHE = configured
        return configured

    try:
        prices = stripe.Price.search(
            query=f'active:"true" metadata["tier"]:"{HORARY_SUBSCRIPTION_TIER}"',
            limit=10,
        )
        for candidate in prices.data or []:
            price_id = _stripe_field(candidate, "id")
            if price_id and _is_ready_horary_subscription_price(str(price_id)):
                _HORARY_SUBSCRIPTION_PRICE_CACHE = str(price_id)
                return str(price_id)
    except Exception as e:
        logger.warning(
            "Stripe horary subscription price search failed: %s",
            repr(e),
            exc_info=True,
        )

    try:
        product = stripe.Product.create(
            name=HORARY_SUBSCRIPTION_PRODUCT_NAME,
            description=(
                "Unlimited focused traditional horary astrology questions for "
                "$5/month, judged by deterministic Regiomontanus rules."
            ),
            metadata={"tier": HORARY_SUBSCRIPTION_TIER},
        )
        price = stripe.Price.create(
            product=product.id,
            unit_amount=HORARY_SUBSCRIPTION_PRICE_CENTS,
            currency="usd",
            recurring={"interval": "month"},
            metadata={"tier": HORARY_SUBSCRIPTION_TIER},
        )
        _HORARY_SUBSCRIPTION_PRICE_CACHE = price.id
        logger.info("Created Stripe horary subscription price %s", price.id)
        return str(price.id)
    except Exception as e:
        logger.error(
            "Failed to create Stripe horary subscription price: %s",
            repr(e),
            exc_info=True,
        )
        raise


def _upsert_horary_subscription_plan(db: Session, price_id: str) -> SubscriptionPlan:
    plan = (
        db.query(SubscriptionPlan)
        .filter(SubscriptionPlan.tier == HORARY_SUBSCRIPTION_TIER)
        .first()
    )
    if not plan:
        plan = SubscriptionPlan(tier=HORARY_SUBSCRIPTION_TIER)
        db.add(plan)

    plan.chart_quota = None
    plan.api_quota = 0
    plan.price_monthly = 5.00
    plan.price_annual = 0.00
    plan.stripe_price_id_monthly = price_id
    plan.stripe_price_id_annual = None
    plan.features = {
        "api_access": False,
        "horary_unlimited": True,
        "deterministic_engine": True,
    }
    db.commit()
    db.refresh(plan)
    return plan


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _has_active_horary_access(user: User | None) -> bool:
    if not user or not user.subscription:
        return False

    sub = user.subscription
    plan_tier = ""
    if sub.plan and sub.plan.tier:
        plan_tier = str(sub.plan.tier).strip().lower()

    if plan_tier not in {"horary", "scholar", "practitioner", "studio"}:
        return False
    if str(sub.status or "").strip().lower() not in {"active", "trial"}:
        return False
    if sub.current_period_end and _as_utc(sub.current_period_end) < datetime.now(
        timezone.utc
    ):
        return False
    return True


def _horary_access_payload(user: User | None) -> dict[str, Any]:
    active = _has_active_horary_access(user)
    sub = user.subscription if user and user.subscription else None
    plan = sub.plan if sub and sub.plan else None
    return {
        "authenticated": bool(user),
        "active": active,
        "tier": str(plan.tier) if plan and plan.tier else "guest",
        "status": str(sub.status) if sub and sub.status else "none",
        "current_period_end": (
            sub.current_period_end.isoformat()
            if sub and sub.current_period_end
            else None
        ),
        "price_monthly": 5,
        "currency": "USD",
        "engine": "deterministic_horary_engine",
        "uses_llm": False,
    }


def _validated_question_payload(payload: HoraryRequest) -> HoraryRequest:
    question = (payload.question or "").strip()
    city = (payload.city or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is required for horary.")
    if not city:
        raise HTTPException(status_code=400, detail="City is required for horary.")
    return payload.model_copy(update={"question": question, "city": city})


def _build_horary_answer(payload: HoraryRequest) -> dict[str, Any]:
    payload = _validated_question_payload(payload)

    date_str = payload.date
    time_str = payload.time
    lat = getattr(payload, "latitude", None)
    lon = getattr(payload, "longitude", None)

    if not date_str or not time_str or lat is None or lon is None:
        from datetime import datetime

        import pytz  # type: ignore

        from src.engine.calculator.geo import get_coordinates, get_timezone

        try:
            if lat is None or lon is None:
                lat, lon = get_coordinates(payload.city, payload.state)
            if not date_str or not time_str:
                tz_str = get_timezone(lat, lon)
                local_dt = datetime.now(pytz.timezone(tz_str))
                date_str = date_str or local_dt.strftime("%Y-%m-%d")
                time_str = time_str or local_dt.strftime("%H:%M")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Location error: {str(e)}")

    res = calculate_chart_data(
        date_str,
        time_str,
        payload.city,
        payload.state,
        latitude=lat,
        longitude=lon,
        house_system="R",
    )
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])

    chart_model = result_to_model(res)
    oracle = build_horary_oracle(payload.question, chart_model)
    return {"meta": res.get("meta", {}), "oracle": oracle}


@router.get("/horary/access")
async def horary_subscription_access(user: User | None = Depends(get_current_user)):
    """
    Report whether the current account has unlimited horary access.
    """
    return _horary_access_payload(user)


@router.post("/horary/subscription/checkout")
async def create_horary_subscription_checkout(
    request: Request,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a Stripe Checkout Session for the $5/month unlimited horary pass.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Account sign-in is required.")

    if _has_active_horary_access(user):
        return {"already_active": True, "access": _horary_access_payload(user)}

    if str(getattr(settings, "SALES_MODE", "live")).strip().lower() != "live":
        raise HTTPException(status_code=409, detail="Checkout is currently paused.")

    stripe.api_key = (getattr(settings, "STRIPE_SECRET_KEY", "") or "").strip()
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Payment system not configured.")

    try:
        price_id = _get_or_create_horary_subscription_price()
        _upsert_horary_subscription_plan(db, price_id)
        origin = str(request.base_url).rstrip("/")
        metadata = {
            "purchase_type": "horary_subscription",
            "tier": HORARY_SUBSCRIPTION_TIER,
            "plan_tier": HORARY_SUBSCRIPTION_TIER,
            "user_id": str(user.id),
        }
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            allow_promotion_codes=True,
            success_url=(
                f"{origin}/horary.html?horary_subscribed=success"
                "&session_id={CHECKOUT_SESSION_ID}"
            ),
            cancel_url=f"{origin}/horary.html?horary_subscribed=cancelled",
            customer_email=str(user.email),
            client_reference_id=str(user.id),
            metadata=metadata,
            subscription_data={"metadata": metadata},
        )
        return {"url": session.url, "session_id": session.id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Stripe horary subscription checkout creation failed: %s",
            repr(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail="Could not create subscription checkout session."
        )


@router.post("/horary/subscriber-answer")
async def subscriber_horary_answer(
    payload: HoraryRequest,
    request: Request,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cast a horary answer for an active unlimited horary subscriber.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Account sign-in is required.")
    if not _has_active_horary_access(user):
        raise HTTPException(
            status_code=402,
            detail="An active $5/month Horary Oracle subscription is required.",
        )

    result = _build_horary_answer(payload)
    task_id = f"horary_sub_{uuid.uuid4().hex}"
    request_meta = payload.model_dump()
    request_meta.update(
        {
            "tier": "horary_subscription",
            "user_id": str(user.id),
            "account_email": str(user.email),
        }
    )
    result["question"] = payload.question
    result["paid"] = True
    result["subscription_active"] = True
    result["task_id"] = task_id
    result["access"] = _horary_access_payload(user)

    try:
        task = AsyncReportTask(
            id=task_id,
            status="completed",
            request_meta=request_meta,
            result_json=result,
        )
        db.add(task)
        db.add(
            GuestRequest(
                ip_address=get_client_ip(request),
                request_type="subscription_horary_question",
            )
        )
        if user.subscription:
            db.add(
                UsageRecord(
                    subscription_id=user.subscription.id,
                    user_id=str(user.id),
                    resource_type="horary_question",
                    resource_id=task_id,
                    cost_credits=1,
                    metadata_json={
                        "city": payload.city,
                        "state": payload.state or "",
                        "tier": "horary_subscription",
                    },
                )
            )
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(
            "Failed to persist subscriber horary answer for user %s: %s",
            user.id,
            repr(e),
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Could not save horary answer.")

    return result


@router.post("/horary")
async def horary_oracle(
    payload: HoraryRequest,
    request: Request,
    user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Subscription-gated horary API. Kept at the original path so older static
    callers do not expose a free bypass around Horary Oracle Unlimited.
    """
    return await subscriber_horary_answer(payload, request, user, db)
