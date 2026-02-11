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


router = APIRouter()

@router.get("/plans")
async def list_public_plans(db: Session = Depends(get_db)):
    """
    Public plan metadata for frontend gating (does NOT return Stripe secret data).

    Purpose:
    - Frontend can hide/disable tiers whose Stripe Price IDs are not configured.
    """
    tiers = ["practitioner", "studio"]
    plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier.in_(tiers)).all()
    by_tier = {p.tier: p for p in plans}

    out = []
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
                "checkout_enabled_monthly": bool(p.stripe_price_id_monthly),
                "checkout_enabled_annual": bool(p.stripe_price_id_annual),
            }
        )

    return {"plans": out}

@router.post("/create-checkout-session")
async def create_checkout_session(request: CheckoutRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Create a Stripe Checkout Session for a specific subscription tier.

    Supported Tiers (B2B):
    - 'practitioner': $147/mo (unlimited calculations, 100 API calls/day, 100 saved charts)
    - 'studio': $497/mo (unlimited calculations, unlimited API, unlimited saved charts)
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    tier = (request.tier or "").strip().lower()
    if tier not in {"practitioner", "studio"}:
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
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Session ID")

    # Subscription checkouts with trials can complete without an immediate payment.
    if session.payment_status not in {"paid", "no_payment_required"}:
        raise HTTPException(status_code=400, detail="Payment not completed")

    user_id = session.metadata.get("user_id")
    plan_tier = session.metadata.get("plan_tier")
    
    if not user_id:
         raise HTTPException(status_code=400, detail="Invalid session metadata")

    # Sync DB status immediately
    service = SubscriptionService(db)
    service._process_subscription_success(session) # Reuse webhook logic to be safe

    # Recover Chart Data
    chart_data = None
    chart_hash = f"user_{user_id}"
    if session.metadata.get("chart_data"):
        try:
            chart_data = json.loads(session.metadata.get("chart_data"))
        except: 
            pass

    # TRIGGER FULFILLMENT (Background Task)
    if chart_data and user_id:
        user = service.db.query(User).filter(User.id == user_id).first()
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
    if tier_norm not in {"practitioner", "studio"}:
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
