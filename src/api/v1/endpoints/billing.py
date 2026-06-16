import hashlib
import json
import logging

import stripe
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.api.v1.auth import create_access_token, get_current_user
from src.api.v1.schemas import CheckoutRequest  # type: ignore
from src.core.config import settings
from src.database.core import get_db
from src.database.models import AsyncReportTask, GuestRequest, SubscriptionPlan, User
from src.services.fulfillment import FulfillmentService
from src.services.premium_generator import (
    generate_premium_report_task,
    llm_iterations_for_tier,
)
from src.services.subscription import SubscriptionService

logger = logging.getLogger(__name__)

router = APIRouter()


def _checkout_globally_enabled() -> bool:
    return str(getattr(settings, "SALES_MODE", "live")).strip().lower() == "live"


_REPORT_PRICE_CACHE: dict[str, str | None] = {}
_GUEST_ONE_TIME_TIERS = {"full_reading", "premium_audit", "forensic_nativity"}


def _stripe_field(obj, key, default=None):
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    try:
        return obj[key]
    except (KeyError, TypeError, AttributeError):
        return getattr(obj, key, default)


def _stripe_mapping(obj) -> dict:
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return obj

    to_dict_recursive = getattr(obj, "to_dict_recursive", None)
    if callable(to_dict_recursive):
        return to_dict_recursive()

    to_dict = getattr(obj, "to_dict", None)
    if callable(to_dict):
        return to_dict()

    return {}


def _checkout_purchase_metadata(session, plan_tier: str | None) -> dict:
    session_id = str(_stripe_field(session, "id", "") or "")
    amount_cents = int(_stripe_field(session, "amount_total", 0) or 0)
    currency = str(_stripe_field(session, "currency", "usd") or "usd").upper()
    tier = str(plan_tier or "unknown")
    value = round(amount_cents / 100.0, 2)
    item_name = "Horary Oracle Unlimited" if tier == "horary" else tier
    item_category = "subscription" if _stripe_field(session, "subscription") else "checkout"
    return {
        "transaction_id": session_id,
        "order_id": session_id,
        "currency": currency,
        "value": value,
        "amount_cents": amount_cents,
        "tier": tier,
        "items": [
            {
                "item_id": tier,
                "item_name": item_name,
                "item_category": item_category,
                "price": value,
                "quantity": 1,
            }
        ],
    }


def _lookup_onetime_price_id(
    *, product_name: str, unit_amount: int, currency: str = "usd"
) -> str | None:
    """
    Best-effort Stripe lookup for one-time report prices by Product name + amount.

    This is a safety net for misconfigured env vars; prefer explicit env vars in production.
    """
    cache_key = f"{product_name}|{unit_amount}|{currency}".lower()
    if cache_key in _REPORT_PRICE_CACHE:
        return _REPORT_PRICE_CACHE[cache_key]

    try:
        prices = stripe.Price.list(active=True, limit=100, expand=["data.product"])
        for p in prices.get("data") or []:
            try:
                if (p.get("type") or "").lower() != "one_time":
                    continue
                if (p.get("currency") or "").lower() != currency.lower():
                    continue
                if int(p.get("unit_amount") or 0) != int(unit_amount):
                    continue

                prod = p.get("product")
                prod_name = None
                if isinstance(prod, dict):
                    prod_name = prod.get("name")
                elif prod:
                    prod_name = str(prod)

                if (prod_name or "").strip() == product_name:
                    _REPORT_PRICE_CACHE[cache_key] = p.get("id")
                    return p.get("id")
            except Exception as e:
                logger.warning(
                    "Skipping price entry during lookup: %s", repr(e), exc_info=True
                )
                continue
    except Exception as e:
        logging.getLogger(__name__).error("Stripe price lookup failed: %s", e)

    _REPORT_PRICE_CACHE[cache_key] = None
    return None


def _chart_hash_from_chart_data(chart_data: dict | None) -> str | None:
    if not chart_data:
        return None

    date = str(chart_data.get("date") or "").strip()
    time = str(chart_data.get("time") or "").strip()
    city = str(chart_data.get("city") or "").strip().lower()
    state = str(chart_data.get("state") or "").strip().lower()
    if not date or not time or not city:
        return None

    raw = f"{date}_{time}_{city}_{state}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@router.get("/plans")
async def list_public_plans(db: Session = Depends(get_db)):
    """
    Public plan metadata for frontend gating (does NOT return Stripe secret data).

    Purpose:
    - Frontend can hide/disable tiers whose Stripe Price IDs are not configured.
    """
    tiers = ["horary", "scholar", "practitioner", "studio"]
    plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier.in_(tiers)).all()
    by_tier = {p.tier: p for p in plans}

    out = []
    checkout_global = _checkout_globally_enabled()
    for tier in tiers:
        p = by_tier.get(tier)  # type: ignore
        if not p:
            out.append(
                {
                    "tier": tier,
                    "price_monthly": None,
                    "price_annual": None,
                    "checkout_enabled_monthly": False,
                    "checkout_enabled_annual": False,
                }
            )
            continue

        out.append(
            {
                "tier": p.tier,
                "price_monthly": (  # type: ignore
                    float(p.price_monthly) if p.price_monthly is not None else None
                ),
                "price_annual": (  # type: ignore
                    float(p.price_annual) if p.price_annual is not None else None
                ),
                "checkout_enabled_monthly": bool(p.stripe_price_id_monthly)
                and checkout_global,
                "checkout_enabled_annual": bool(p.stripe_price_id_annual)
                and checkout_global,
            }
        )

    return {
        "plans": out,
        "sales_mode": str(getattr(settings, "SALES_MODE", "live")).strip().lower(),
        "checkout_globally_enabled": checkout_global,
    }


@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CheckoutRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a Stripe Checkout Session.

    Supported Tiers:
    - One-time purchases:
      - 'single_reading': $25 (single chart unlock)
      - 'calibration': $27 (PDF)
      - 'full': $197 (Forensic Packet)

    - Subscriptions (B2B):
    - 'horary': $5/mo (unlimited deterministic horary questions)
    - 'practitioner': $147/mo (unlimited calculations, 100 API calls/day, 100 saved charts)
    - 'studio': $497/mo (unlimited calculations, unlimited API, unlimited saved charts)
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    if not _checkout_globally_enabled():
        raise HTTPException(
            status_code=409,
            detail="Checkout is currently paused.",
        )

    tier = (request.tier or "").strip().lower()

    # ----------------------------
    # One-time tiers
    # ----------------------------
    if tier in {"single_reading", "calibration", "full"}:
        if not request.chart_request:
            raise HTTPException(
                status_code=400,
                detail="chart_request is required for one-time purchases",
            )

        # Map tier -> Stripe Price ID (prefer env; fallback to product lookup).
        if tier == "single_reading":
            price_id = (
                getattr(settings, "STRIPE_PRICE_SINGLE_READING_ONETIME", "") or ""
            ).strip()
            if not price_id:
                price_id = _lookup_onetime_price_id(
                    product_name="Single Reading",
                    unit_amount=int(getattr(settings, "SINGLE_READING_PRICE_USD", 25))
                    * 100,
                )
            plan_tier = "SINGLE_READING"
        elif tier == "calibration":
            price_id = (
                getattr(settings, "STRIPE_PRICE_CALIBRATION_ONETIME", "") or ""
            ).strip()
            if not price_id:
                price_id = _lookup_onetime_price_id(
                    product_name="Calibration Audit", unit_amount=2700
                )
            plan_tier = "CALIBRATION"
        else:
            price_id = (
                getattr(settings, "STRIPE_PRICE_FULL_ONETIME", "") or ""
            ).strip()
            if not price_id:
                price_id = _lookup_onetime_price_id(
                    product_name="Full Forensic Audit + Agent Data", unit_amount=19700
                )
            plan_tier = "FULL"

        if not price_id:
            raise HTTPException(
                status_code=500, detail="Stripe one-time price is not configured"
            )

        # Stripe expects a literal "{CHECKOUT_SESSION_ID}" placeholder in the final URL.
        final_success_url = request.success_url or ""
        if "{CHECKOUT_SESSION_ID}" not in final_success_url:
            sep = "&" if "?" in final_success_url else "?"
            final_success_url = (
                f"{final_success_url}{sep}session_id={{CHECKOUT_SESSION_ID}}"
            )

        # Minimal chart payload stored in metadata (keep Stripe metadata small).
        cr = request.chart_request.model_dump() if request.chart_request else {}
        chart_min = {
            "date": str(cr.get("date") or "")[:20],
            "time": str(cr.get("time") or "")[:20],
            "city": str(cr.get("city") or "")[:100],
            "state": str(cr.get("state") or "")[:50],
            "name": str(cr.get("name") or "")[:100],
        }

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{"price": price_id, "quantity": 1}],
                mode="payment",
                allow_promotion_codes=True,
                success_url=final_success_url,
                cancel_url=request.cancel_url,
                customer_email=user.email,  # type: ignore
                client_reference_id=user.id,  # type: ignore
                metadata={
                    "user_id": user.id,  # type: ignore
                    "plan_tier": plan_tier,
                    "chart_data": json.dumps(chart_min),
                },
                invoice_creation={
                    "enabled": True,
                    "invoice_data": {
                        "metadata": {"user_id": user.id, "plan_tier": plan_tier}  # type: ignore
                    },
                },
            )
            return {"sessionId": session.id, "url": session.url}
        except Exception as e:
            logger.error(
                "Stripe one-time checkout creation failed: %s", repr(e), exc_info=True
            )
            raise HTTPException(
                status_code=500, detail="Failed to create checkout session"
            )

    # ----------------------------
    # Subscription tiers
    # ----------------------------
    if tier not in {"horary", "scholar", "practitioner", "studio"}:
        raise HTTPException(status_code=400, detail="Invalid tier")

    try:
        service = SubscriptionService(db)
        session = service.create_checkout_session(
            user=user,
            plan_tier=tier,
            annual=request.annual,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            chart_data=(
                request.chart_request.model_dump() if request.chart_request else None  # type: ignore
            ),
        )
        return {"sessionId": session.id, "url": session.url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "Stripe subscription checkout creation failed: %s", repr(e), exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to create checkout session")


@router.get("/verify-checkout-session")
async def verify_checkout_session(
    session_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except Exception as e:
        logger.warning(
            "Invalid Stripe session retrieval for session_id=%s: %s",
            session_id,
            repr(e),
            exc_info=True,
        )
        raise HTTPException(status_code=400, detail="Invalid Session ID")

    # Subscription checkouts with trials can complete without an immediate payment.
    payment_status = _stripe_field(session, "payment_status")
    if payment_status not in {"paid", "no_payment_required"}:
        raise HTTPException(status_code=400, detail="Payment not completed")

    metadata = _stripe_mapping(_stripe_field(session, "metadata", {}))
    user_id = _stripe_field(metadata, "user_id")
    plan_tier = _stripe_field(metadata, "plan_tier")

    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid session metadata")

    # Sync DB status immediately (subscriptions only).
    is_subscription = bool(_stripe_field(session, "subscription")) or (
        str(_stripe_field(session, "mode") or "").lower() == "subscription"
    )
    if is_subscription:
        service = SubscriptionService(db)
        service._process_subscription_success(session)  # Reuse webhook logic to be safe

    # Recover Chart Data
    chart_data = None
    chart_hash = f"user_{user_id}"
    if _stripe_field(metadata, "chart_data"):
        try:
            chart_data_raw = _stripe_field(metadata, "chart_data")
            if chart_data_raw is not None:
                chart_data = json.loads(str(chart_data_raw))
        except (TypeError, ValueError) as e:
            logger.warning(
                "Failed to parse chart_data from session metadata: %s",
                repr(e),
                exc_info=True,
            )
    chart_hash = _chart_hash_from_chart_data(chart_data) or chart_hash

    # TRIGGER FULFILLMENT (Background Task) for report products only.
    if plan_tier in {"CALIBRATION", "FULL"} and chart_data and user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.email:
            background_tasks.add_task(
                FulfillmentService.fulfill_order,
                user_email=str(user.email),
                user_name=str(user.name) if user.name else "User",
                chart_request=chart_data,
                tier=str(plan_tier) if plan_tier else "practitioner",
            )

    # Create Token
    # We include user_id in data so get_current_user works
    access_token = create_access_token(
        chart_hash=chart_hash,
        tier=str(plan_tier) if plan_tier else "",
        expires_days=30,
        data={"user_id": user_id, "chart_input": chart_data},
    )

    return {
        "verified": True,
        "access_token": access_token,
        "chart_hash": chart_hash,
        "chart_data": chart_data,  # Return so frontend can repopulate if needed
        "tier": plan_tier,
        "purchase": _checkout_purchase_metadata(session, plan_tier),
    }


@router.post("/cancel-subscription")
async def cancel_subscription(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Cancel the user's active subscription (auto-renew off).
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        service = SubscriptionService(db)
        sub = service.cancel_subscription(user, immediate=False)
        period_end_str = (
            sub.current_period_end.strftime("%Y-%m-%d")
            if sub.current_period_end
            else "end of billing period"
        )
        return {
            "success": True,
            "message": "Auto-renewal turned off. Access continues until "
            + period_end_str,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "Subscription cancellation failed for user %s: %s",
            user.id if user else "unknown",
            repr(e),
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")


@router.post("/start-trial")
async def start_trial(
    tier: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Start a no-card trial for an existing account.

    Allowed tiers: horary, scholar, practitioner, studio.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    tier_norm = (tier or "").strip().lower()
    if tier_norm not in {"horary", "scholar", "practitioner", "studio"}:
        raise HTTPException(status_code=400, detail="Invalid tier")

    # Don't allow overwriting a Stripe-managed subscription.
    sub = user.subscription
    if sub and sub.stripe_subscription_id and sub.status in {"active", "trial"}:
        raise HTTPException(
            status_code=400,
            detail="Subscription already managed by Stripe. Use checkout instead.",
        )

    service = SubscriptionService(db)
    try:
        updated = service.start_trial(user, tier_norm)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "success": True,
        "status": updated.status,
        "plan_tier": updated.plan.tier if updated.plan else tier_norm,
        "trial_end_date": (
            updated.trial_end_date.isoformat() if updated.trial_end_date else None
        ),
    }


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET.strip()
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event["type"]

    # --- Guest one-time purchase fulfillment ---
    # Guest checkout sessions have no user_id/client_reference_id; they carry
    # metadata.tier from the no-account checkout flow. Handle them here before
    # SubscriptionService, which would otherwise silently drop them.
    if event_type == "checkout.session.completed":
        session_obj = event["data"]["object"]
        metadata = _stripe_mapping(_stripe_field(session_obj, "metadata", {}))

        tier = str(_stripe_field(metadata, "tier", "") or "").strip().lower()
        user_id = _stripe_field(metadata, "user_id") or _stripe_field(
            session_obj, "client_reference_id"
        )

        if tier in _GUEST_ONE_TIME_TIERS and not user_id:
            session_id = str(_stripe_field(session_obj, "id", "") or "")
            payment_status = str(
                _stripe_field(session_obj, "payment_status", "") or ""
            )

            if payment_status == "paid" and session_id:
                # Idempotency — skip if task already exists
                existing = (
                    db.query(AsyncReportTask)
                    .filter(AsyncReportTask.id == session_id)
                    .first()
                )
                if not existing:
                    import json as _json

                    chart_data_str = _stripe_field(metadata, "chart_data", "{}")
                    try:
                        chart_data = _json.loads(chart_data_str)
                    except (TypeError, ValueError) as e:
                        logger.warning(
                            "Webhook: failed to parse guest chart data for session %s: %s",
                            session_id,
                            repr(e),
                            exc_info=True,
                        )
                        chart_data = {}

                    # Capture customer email
                    customer_email = None
                    try:
                        cd = _stripe_field(session_obj, "customer_details", {}) or {}
                        customer_email = _stripe_field(
                            cd, "email"
                        ) or _stripe_field(
                            session_obj,
                            "customer_email"
                        )
                    except Exception as e:
                        logger.warning(
                            "Webhook: failed to read customer email for session %s: %s",
                            session_id,
                            repr(e),
                            exc_info=True,
                        )

                    request_meta = {
                        "date": chart_data.get("date", ""),
                        "time": chart_data.get("time", "12:00"),
                        "city": chart_data.get("city", ""),
                        "state": chart_data.get("state", ""),
                        "name": chart_data.get("name", "Guest"),
                        "tier": tier,
                        "report_iterations": llm_iterations_for_tier(tier),
                        # Mark as a paid order so the generator's safety net
                        # (failure alerts, missing-email alert, iteration floor)
                        # covers webhook-fulfilled purchases too — not just the
                        # browser-triggered generate-paid path.
                        "paid": True,
                    }
                    if customer_email:
                        request_meta["customer_email"] = customer_email

                    task = AsyncReportTask(
                        id=session_id,
                        status="pending",
                        request_meta=request_meta,
                    )
                    db.add(task)

                    # Record guest usage
                    usage = GuestRequest(
                        ip_address="webhook",
                        request_type=f"paid_{tier}",
                    )
                    db.add(usage)
                    db.commit()
                    db.refresh(task)

                    background_tasks.add_task(
                        generate_premium_report_task, task.id, request_meta
                    )
                    logger.info(
                        "Webhook: started guest fulfillment for session %s", session_id
                    )

            return {"status": "success"}

    # --- Subscription / authenticated-user events ---
    service = SubscriptionService(db)
    service.handle_webhook(event)

    return {"status": "success"}
