from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from src.database.core import get_db
from src.api.v1.auth import get_current_user, create_access_token
from src.database.models import User
from src.api.v1.schemas import CheckoutRequest
from src.services.subscription import SubscriptionService
from src.core.config import settings
import stripe
import json


router = APIRouter()

@router.post("/create-checkout-session")
async def create_checkout_session(request: CheckoutRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Create a Stripe Checkout Session for a specific subscription tier.
    
    Supported Tiers:
    - 'onetime': $197 Premium Dossier (B2C)
    - 'apprentice': $147/mo (5 reports, basic API)
    - 'practitioner': $397/mo (25 reports, priority API)
    - 'master': $797/mo (100 reports, dedicated API)
    - 'agency': $1297/mo (Unlimited reports, dedicated support)
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    try:
        service = SubscriptionService(db)
        session = service.create_checkout_session(
            user=user,
            plan_tier=request.tier, # 'tier' field from frontend
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
async def verify_checkout_session(session_id: str, db: Session = Depends(get_db)):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Session ID")

    if session.payment_status != "paid":
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
            # Generate a consistent hash from data? or just use user id?
            # For compatibility with frontend expecting chart_hash:
            # We'll use a dummy hash if we don't calculate it here.
            # But frontend uses it to key the token.
            pass 
        except: 
            pass

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
