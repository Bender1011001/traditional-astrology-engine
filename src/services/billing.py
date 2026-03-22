import stripe
from datetime import datetime, timezone, timezone, timedelta
from sqlalchemy.orm import Session
from src.core.config import settings
from src.database.models import User, UserSubscription, SubscriptionPlan
from typing import Optional

if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY

class BillingService:
    @staticmethod
    def create_checkout_session(db: Session, user: User, plan_id: str, success_url: str, cancel_url: str):
        # Find plan
        # We assume plan_id is the database ID or tier name?
        # Let's assume tier name since that's what frontend sends ("practitioner").
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == plan_id).first()
        if not plan:
            # Maybe it is a UUID
            plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
        
        if not plan:
            raise ValueError("Invalid Plan")

        if not plan.stripe_price_id_monthly:
             raise ValueError("Plan not configured for billing")

        final_success_url = success_url or ""
        if "{CHECKOUT_SESSION_ID}" not in final_success_url:
            sep = "&" if "?" in final_success_url else "?"
            final_success_url = f"{final_success_url}{sep}session_id={{CHECKOUT_SESSION_ID}}"

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': plan.stripe_price_id_monthly,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=final_success_url,
            cancel_url=cancel_url,
            customer_email=user.email,
            client_reference_id=user.id,
            metadata={
                "user_id": user.id,
                "plan_tier": plan.tier
            }
        )
        return checkout_session

    @staticmethod
    def handle_webhook(db: Session, event: dict):
        event_type = event['type']
        
        if event_type == 'checkout.session.completed':
            session = event['data']['object']
            BillingService.process_subscription_success(db, session)
        elif event_type == 'invoice.payment_succeeded':
            invoice = event['data']['object']
            BillingService.process_payment_succeeded(db, invoice)
    
    @staticmethod
    def process_subscription_success(db: Session, session: dict):
        user_id = session.get("client_reference_id")
        stripe_customer_id = session.get("customer")
        
        # Or from metadata
        if not user_id:
             user_id = session.get("metadata", {}).get("user_id")

        if not user_id:
            return 

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return

        # Get plan from metadata or infer? 
        # Ideally we track what they bought.
        # Simple: assume update to tier in metadata.
        plan_tier = session.get("metadata", {}).get("plan_tier")
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == plan_tier).first()
        
        if not plan:
            return

        # Update Subscription
        sub = user.subscription
        if not sub:
            sub = UserSubscription(user_id=user.id)
            db.add(sub)
            
        sub.plan_id = plan.id
        sub.stripe_customer_id = stripe_customer_id
        sub.status = "active"
        sub.current_period_end = datetime.now(timezone.utc) + timedelta(days=30) # Approximate, webhook should update
        
        db.commit()

    @staticmethod
    def process_payment_succeeded(db: Session, invoice: dict):
        stripe_pd = invoice.get("period_end")
        customer_id = invoice.get("customer")
        
        sub = db.query(UserSubscription).filter(UserSubscription.stripe_customer_id == customer_id).first()
        if sub:
            sub.status = "active"
            if stripe_pd:
                sub.current_period_end = datetime.fromtimestamp(stripe_pd)
            db.commit()
