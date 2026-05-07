"""
Guest Checkout Endpoint — No authentication required.

Creates a Stripe Checkout Session for one-time readings.
After payment success, the frontend polls the premium generation status
to get the full reading.
"""

import json
import logging
import uuid

import stripe
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.api.v1.client_ip import get_client_ip
from src.api.v1.schemas import ChartRequest  # type: ignore
from src.core.config import settings
from src.database.core import get_db
from src.database.models import AsyncReportTask, GuestRequest
from src.services.admin_notifier import notify_chart_created
from src.services.premium_generator import generate_premium_report_task

logger = logging.getLogger(__name__)

router = APIRouter()

# Tier configuration — simple, no subscriptions
# config_key: maps to the settings attribute that holds the pre-configured Stripe Price ID
TIERS = {
    "full_reading": {
        "price_cents": 2500,
        "product_name": "Full Natal Chart Reading",
        "description": "Complete natal chart reading with timing, dignities, and personalized insights.",
        "config_key": "STRIPE_PRICE_FULL_READING",
    },
    "premium_audit": {
        "price_cents": 6900,
        "product_name": "Complete Astrological Analysis",
        "description": "20+ page deep-dive analysis with advanced timing, remediation, and 10-year forecast.",
        "config_key": "STRIPE_PRICE_PREMIUM_AUDIT",
    },
}

# Free teaser: no limit — always allow the quick preview
MAX_FREE_PREMIUM_PER_IP = 3


def _get_or_create_stripe_price(tier_key: str) -> str:
    """Get or create a Stripe Price ID for a tier. Caches in settings attributes."""
    tier = TIERS[tier_key]
    cache_attr = f"_stripe_price_cache_{tier_key}"

    # Check settings cache
    cached = getattr(settings, cache_attr, None)
    if cached:
        return cached

    # Check pre-configured price IDs (config_key → existing settings attribute)
    config_key = tier.get("config_key", "")
    if config_key:
        env_val = (getattr(settings, config_key, "") or "").strip()
        if env_val:
            setattr(settings, cache_attr, env_val)
            return env_val

    # Fallback: check generic env var STRIPE_PRICE_{TIER_KEY}
    generic_key = f"STRIPE_PRICE_{tier_key.upper()}"
    generic_val = (getattr(settings, generic_key, "") or "").strip()
    if generic_val:
        setattr(settings, cache_attr, generic_val)
        return generic_val

    # Search Stripe for existing price
    try:
        prices = stripe.Price.search(
            query=f'active:"true" metadata["tier"]:"{tier_key}"', limit=1
        )
        if prices and prices.data:
            price_id = prices.data[0].id
            setattr(settings, cache_attr, price_id)
            return price_id
    except Exception as e:
        logger.warning(
            "Stripe price search failed for %s: %s", tier_key, repr(e), exc_info=True
        )

    # Create product + price
    try:
        product = stripe.Product.create(
            name=tier["product_name"],  # type: ignore
            description=tier["description"],  # type: ignore
            metadata={"tier": tier_key},
        )
        price = stripe.Price.create(
            product=product.id,
            unit_amount=tier["price_cents"],  # type: ignore
            currency="usd",
            metadata={"tier": tier_key},
        )
        price_id = price.id
        setattr(settings, cache_attr, price_id)
        logger.info("Created Stripe price %s for tier %s", price_id, tier_key)
        return price_id
    except Exception as e:
        logger.error(
            "Failed to create Stripe price for %s: %s", tier_key, repr(e), exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="Payment system configuration error."
        )


@router.post("/checkout")
async def guest_checkout(
    request: Request,
    tier: str,
    date: str,
    time: str,
    city: str,
    state: str = "",
    name: str = "Guest",
):
    """
    Create a Stripe Checkout Session for a guest (no account required).
    After payment, the success page triggers premium generation.
    """
    tier_key = tier.strip().lower()
    if tier_key not in TIERS:
        raise HTTPException(
            status_code=400, detail=f"Invalid tier: {tier}. Use: {list(TIERS.keys())}"
        )

    # Validate basic inputs
    if not date or not city:
        raise HTTPException(status_code=400, detail="Date and city are required.")

    stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", "") or ""
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Payment system not configured.")

    price_id = _get_or_create_stripe_price(tier_key)

    # Generate a unique reference ID for this order
    order_id = uuid.uuid4().hex[:12]

    chart_data = {
        "date": str(date or "")[:20],
        "time": str(time or "")[:20],
        "city": str(city or "")[:100],
        "state": str(state or "")[:50],
        "name": str(name or "")[:100],
    }

    # Build Stripe Checkout Session
    origin = str(request.base_url).rstrip("/")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="payment",
            allow_promotion_codes=True,
            success_url=f"{origin}/?paid=true&session_id={{CHECKOUT_SESSION_ID}}&order={order_id}",
            cancel_url=f"{origin}/#get-reading",
            metadata={
                "order_id": order_id,
                "tier": tier_key,
                "chart_data": json.dumps(chart_data),
            },
        )
        return {"url": session.url, "session_id": session.id, "order_id": order_id}
    except Exception as e:
        logger.error("Stripe checkout creation failed: %s", repr(e), exc_info=True)
        raise HTTPException(
            status_code=500, detail="Could not create checkout session."
        )


@router.post("/generate-paid")
async def generate_paid_reading(
    request: Request,
    background_tasks: BackgroundTasks,
    session_id: str,
    db: Session = Depends(get_db),
):
    """
    After successful payment, verify the Stripe session and start premium generation.
    Returns a task_id to poll for status.
    """
    stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", "") or ""
    if not stripe.api_key:
        raise HTTPException(status_code=500, detail="Payment system not configured.")

    # Verify payment
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except Exception as e:
        logger.error(
            "Stripe session retrieval failed for %s: %s",
            session_id,
            repr(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=400, detail="Invalid or expired checkout session."
        )

    if session.payment_status != "paid":
        raise HTTPException(status_code=402, detail="Payment not completed.")

    # Check for Idempotency (prevent duplicate report tasks for the same session)
    existing_task = (
        db.query(AsyncReportTask).filter(AsyncReportTask.id == session_id).first()
    )
    if existing_task:
        # If it already exists, someone double-clicked or reloaded the page. We silently accept it.
        return {
            "task_id": existing_task.id,
            "tier": session.metadata.get("tier", "unknown"),  # type: ignore
            "message": "Report generation already in progress.",
        }

    # Extract chart data from metadata
    chart_data_str = session.metadata.get("chart_data", "{}")  # type: ignore
    chart_data = json.loads(chart_data_str)

    if not chart_data.get("date") or not chart_data.get("city"):
        raise HTTPException(status_code=400, detail="Chart data missing from session.")

    # Create async task
    chart_request = ChartRequest(
        date=chart_data["date"],
        time=chart_data.get("time", "12:00"),
        city=chart_data["city"],
        state=chart_data.get("state", ""),
        name=chart_data.get("name", "Guest"),
    )

    # Capture customer email from Stripe session so we can email the PDF on completion
    customer_email = None
    try:
        cd = getattr(session, "customer_details", None)
        if cd:
            customer_email = getattr(cd, "email", None)
        if not customer_email:
            customer_email = getattr(session, "customer_email", None)
    except Exception:
        pass

    request_meta = chart_request.model_dump()
    if customer_email:
        request_meta["customer_email"] = customer_email

    task = AsyncReportTask(
        id=session_id,  # Use Stripe session_id as the primary key for guaranteed 1:1 idempotency
        status="pending",
        request_meta=request_meta,
    )
    db.add(task)

    # Record guest usage (for analytics)
    client_ip = get_client_ip(request)
    usage = GuestRequest(
        ip_address=client_ip,
        request_type=f"paid_{session.metadata.get('tier', 'unknown')}",  # type: ignore
    )
    db.add(usage)
    db.commit()
    db.refresh(task)

    # Start background generation (pass request_meta so email delivery works)
    background_tasks.add_task(
        generate_premium_report_task, task.id, request_meta  # type: ignore
    )
    background_tasks.add_task(
        notify_chart_created,
        chart_request.model_dump(),
        f"Paid: {session.metadata.get('tier', 'unknown')}",  # type: ignore
    )

    return {
        "task_id": task.id,
        "tier": session.metadata.get("tier", "unknown"),  # type: ignore
        "message": "Report generation started.",
    }


@router.get("/task-status/{task_id}")
async def check_task_status(
    task_id: str,
    db: Session = Depends(get_db),
):
    """Poll the status of a reading generation task."""
    task = db.query(AsyncReportTask).filter(AsyncReportTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    return {
        "task_id": task.id,
        "status": task.status,
        "result": task.result_json if task.status in ("completed", "failed") else None,
    }
