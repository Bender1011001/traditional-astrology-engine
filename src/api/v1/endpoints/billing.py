from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from src.database.core import get_db
from src.api.v1.auth import get_current_user, create_access_token
from src.database.models import SubscriptionPlan, User
from src.api.v1.schemas import CheckoutRequest
from src.services.subscription import SubscriptionService
from src.services.fulfillment import FulfillmentService
from src.core.config import settings
import stripe
import json
import logging
import hashlib


router = APIRouter()


def _checkout_globally_enabled() -> bool:
    return str(getattr(settings, "SALES_MODE", "live")).strip().lower() == "live"


_REPORT_PRICE_CACHE: dict[str, str | None] = {}


def _lookup_onetime_price_id(*, product_name: str, unit_amount: int, currency: str = "usd") -> str | None:
    """
    Best-effort Stripe lookup for one-time report prices by Product name + amount.

    This is a safety net for misconfigured env vars; prefer explicit env vars in production.
    """
    cache_key = f"{product_name}|{unit_amount}|{currency}".lower()
    if cache_key in _REPORT_PRICE_CACHE:
        return _REPORT_PRICE_CACHE[cache_key]

    try:
        prices = stripe.Price.list(active=True, limit=100, expand=["data.product"])
        for p in (prices.get("data") or []):
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
            except Exception:
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
    tiers = ["scholar", "practitioner", "studio"]
    plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier.in_(tiers)).all()
    by_tier = {p.tier: p for p in plans}

    out = []
    checkout_global = _checkout_globally_enabled()
    for tier in tiers:
        p = by_tier.get(tier)
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
                    "price_monthly": float(p.price_monthly) if p.price_monthly is not None else None,
                    "price_annual": float(p.price_annual) if p.price_annual is not None else None,
                    "checkout_enabled_monthly": bool(p.stripe_price_id_monthly) and checkout_global,
                    "checkout_enabled_annual": bool(p.stripe_price_id_annual) and checkout_global,
                }
            )

    return {
        "plans": out,
        "sales_mode": str(getattr(settings, "SALES_MODE", "live")).strip().lower(),
        "checkout_globally_enabled": checkout_global,
    }

@router.post("/create-checkout-session")
async def create_checkout_session(request: CheckoutRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Create a Stripe Checkout Session.

    Supported Tiers:
    - One-time purchases:
      - 'single_reading': $20 (single chart unlock)
      - 'calibration': $27 (PDF)
      - 'full': $197 (Forensic Packet)

    - Subscriptions (B2B):
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
            raise HTTPException(status_code=400, detail="chart_request is required for one-time purchases")

        # Map tier -> Stripe Price ID (prefer env; fallback to product lookup).
        if tier == "single_reading":
            price_id = (getattr(settings, "STRIPE_PRICE_SINGLE_READING_ONETIME", "") or "").strip()
            if not price_id:
                price_id = _lookup_onetime_price_id(
                    product_name="Single Reading",
                    unit_amount=int(getattr(settings, "SINGLE_READING_PRICE_USD", 20)) * 100,
                )
            plan_tier = "SINGLE_READING"
        elif tier == "calibration":
            price_id = (getattr(settings, "STRIPE_PRICE_CALIBRATION_ONETIME", "") or "").strip()
            if not price_id:
                price_id = _lookup_onetime_price_id(product_name="Calibration Audit", unit_amount=2700)
            plan_tier = "CALIBRATION"
        else:
            price_id = (getattr(settings, "STRIPE_PRICE_FULL_ONETIME", "") or "").strip()
            if not price_id:
                price_id = _lookup_onetime_price_id(product_name="Full Forensic Audit + Agent Data", unit_amount=19700)
            plan_tier = "FULL"

        if not price_id:
            raise HTTPException(status_code=500, detail="Stripe one-time price is not configured")

        # Stripe expects a literal "{CHECKOUT_SESSION_ID}" placeholder in the final URL.
        final_success_url = request.success_url or ""
        if "{CHECKOUT_SESSION_ID}" not in final_success_url:
            sep = "&" if "?" in final_success_url else "?"
            final_success_url = f"{final_success_url}{sep}session_id={{CHECKOUT_SESSION_ID}}"

        # Minimal chart payload stored in metadata (keep Stripe metadata small).
        cr = request.chart_request.dict() if request.chart_request else {}
        chart_min = {
            "date": cr.get("date"),
            "time": cr.get("time"),
            "city": cr.get("city"),
            "state": cr.get("state"),
            "name": cr.get("name"),
        }

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{"price": price_id, "quantity": 1}],
                mode="payment",
                allow_promotion_codes=True,
                success_url=final_success_url,
                cancel_url=request.cancel_url,
                customer_email=user.email,
                client_reference_id=user.id,
                metadata={
                    "user_id": user.id,
                    "plan_tier": plan_tier,
                    "chart_data": json.dumps(chart_min),
                },
                invoice_creation={
                    "enabled": True,
                    "invoice_data": {"metadata": {"user_id": user.id, "plan_tier": plan_tier}},
                },
            )
            return {"sessionId": session.id, "url": session.url}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ----------------------------
    # Subscription tiers
    # ----------------------------
    if tier not in {"scholar", "practitioner", "studio"}:
        raise HTTPException(status_code=400, detail="Invalid tier")
        
    try:
        service = SubscriptionService(db)
        session = service.create_checkout_session(
            user=user,
            plan_tier=tier,
            annual=request.annual,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            chart_data=request.chart_request.dict() if request.chart_request else None
        )
        return {"sessionId": session.id, "url": session.url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/verify-checkout-session")
async def verify_checkout_session(session_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid Session ID")

    # Subscription checkouts with trials can complete without an immediate payment.
    if session.payment_status not in {"paid", "no_payment_required"}:
        raise HTTPException(status_code=400, detail="Payment not completed")

    user_id = session.metadata.get("user_id")
    plan_tier = session.metadata.get("plan_tier")
    
    if not user_id:
         raise HTTPException(status_code=400, detail="Invalid session metadata")

    # Sync DB status immediately (subscriptions only).
    is_subscription = bool(session.get("subscription")) or (str(session.get("mode") or "").lower() == "subscription")
    if is_subscription:
        service = SubscriptionService(db)
        service._process_subscription_success(session)  # Reuse webhook logic to be safe

    # Recover Chart Data
    chart_data = None
    chart_hash = f"user_{user_id}"
    if session.metadata.get("chart_data"):
        try:
            chart_data = json.loads(session.metadata.get("chart_data"))
        except (TypeError, ValueError):
            pass
    chart_hash = _chart_hash_from_chart_data(chart_data) or chart_hash

    # TRIGGER FULFILLMENT (Background Task) for report products only.
    if plan_tier in {"CALIBRATION", "FULL"} and chart_data and user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.email:
            background_tasks.add_task(
                FulfillmentService.fulfill_order,
                user_email=user.email,
                user_name=user.name or "User",
                chart_request=chart_data,
                tier=plan_tier or "practitioner"
            )
            
    # Create Token
    # We include user_id in data so get_current_user works
    access_token = create_access_token(
        chart_hash=chart_hash,
        tier=plan_tier,
        expires_days=30,
        data={"user_id": user_id, "chart_input": chart_data}
    )

    return {
        "verified": True,
        "access_token": access_token,
        "chart_hash": chart_hash,
        "chart_data": chart_data, # Return so frontend can repopulate if needed
        "tier": plan_tier
    }

@router.post("/cancel-subscription")
async def cancel_subscription(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Cancel the user's active subscription (auto-renew off).
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        service = SubscriptionService(db)
        sub = service.cancel_subscription(user, immediate=False)
        return {
            "success": True, 
            "message": "Auto-renewal turned off. Access continues until " + sub.current_period_end.strftime("%Y-%m-%d")
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")


@router.post("/start-trial")
async def start_trial(
    tier: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Start a no-card trial for an existing account.

    Allowed tiers: practitioner, studio.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    tier_norm = (tier or "").strip().lower()
    if tier_norm not in {"scholar", "practitioner", "studio"}:
        raise HTTPException(status_code=400, detail="Invalid tier")

    # Don't allow overwriting a Stripe-managed subscription.
    sub = user.subscription
    if sub and sub.stripe_subscription_id and sub.status in {"active", "trial"}:
        raise HTTPException(status_code=400, detail="Subscription already managed by Stripe. Use checkout instead.")

    service = SubscriptionService(db)
    try:
        updated = service.start_trial(user, tier_norm)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "success": True,
        "status": updated.status,
        "plan_tier": updated.plan.tier if updated.plan else tier_norm,
        "trial_end_date": updated.trial_end_date.isoformat() if updated.trial_end_date else None,
    }


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")
        
    service = SubscriptionService(db)
    service.handle_webhook(event)
    
    return {"status": "success"}
