from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from src.database.core import get_db
from src.api.v1.auth import get_current_user
from src.database.models import User
from src.api.v1.schemas import CheckoutRequest
from src.services.subscription import SubscriptionService
from src.core.config import settings
import stripe

router = APIRouter()

@router.post("/create-checkout-session")
async def create_checkout_session(request: CheckoutRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    try:
        service = SubscriptionService(db)
        session = service.create_checkout_session(
            user=user,
            plan_tier=request.tier, # 'tier' field from frontend
            annual=request.annual,
            success_url=request.success_url,
            cancel_url=request.cancel_url
        )
        return {"sessionId": session.id, "url": session.url}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
