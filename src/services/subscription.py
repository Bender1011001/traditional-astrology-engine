from datetime import datetime, timezone, timedelta
import logging
import stripe
from sqlalchemy.orm import Session
from src.database.models import User, UserSubscription, SubscriptionPlan, UsageRecord, Invoice
from src.core.config import settings
from src.services.notifications import AdminNotificationService

logger = logging.getLogger(__name__)

if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY

class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db

    def get_plan_by_tier(self, tier: str) -> SubscriptionPlan:
        return self.db.query(SubscriptionPlan).filter(SubscriptionPlan.tier == tier).first()

    def start_trial(self, user: User, plan_tier: str, trial_days: int = None):
        """
        Start a free trial without credit card.
        """
        if trial_days is None:
            trial_days = getattr(settings, "TRIAL_DAYS_DEFAULT", 14)
        plan = self.get_plan_by_tier(plan_tier)
        if not plan:
            raise ValueError(f"Plan {plan_tier} not found")

        # Check existing trial?
        # Logic: If they ever had a trial, maybe block?
        # For now, allow clean slate.
        
        now = datetime.now(timezone.utc)
        # For the free plan, we store an active baseline subscription (not a trial).
        is_free = plan.tier == "free"
        trial_end = None if is_free else (now + timedelta(days=trial_days))

        sub = user.subscription
        if not sub:
            sub = UserSubscription(user_id=user.id)
            self.db.add(sub)
        
        sub.plan_id = plan.id
        sub.status = "active" if is_free else "trial"
        sub.trial_start_date = None if is_free else now
        sub.trial_end_date = None if is_free else trial_end
        sub.current_period_start = now
        sub.current_period_end = None if is_free else trial_end
        sub.cancel_at_period_end = False
        
        # Reset quota usage for new period
        # We handle this by checking created_at >= current_period_start in quota middleware
        
        self.db.commit()
        return sub

    def create_checkout_session(self, user: User, plan_tier: str, annual: bool = False, success_url: str = "", cancel_url: str = "", chart_data: dict = None):
        plan = self.get_plan_by_tier(plan_tier)
        if not plan:
            raise ValueError("Invalid Plan")

        price_id = plan.stripe_price_id_annual if annual else plan.stripe_price_id_monthly
        if not price_id:
             raise ValueError("Plan not configured for this billing period")

        # Dynamically check price type to avoid mode mismatch (Subscription vs Payment)
        try:
            stripe_price = stripe.Price.retrieve(price_id)
            is_recurring = stripe_price.recurring is not None
        except Exception as e:
            logger.warning("Stripe price retrieval failed for %s, falling back to tier heuristic: %s", price_id, repr(e), exc_info=True)
            is_recurring = plan.tier not in ['onetime', 'CALIBRATION', 'FULL']

        metadata = {
            "user_id": user.id,
            "plan_tier": plan.tier,
            "annual": str(annual)
        }
        
        # Store chart data in metadata if provided (serialized)
        if chart_data:
            import json
            # Minimal data to save space
            minimal_data = {
                "date": str(chart_data.get("date") or "")[:20],
                "time": str(chart_data.get("time") or "")[:20],
                "city": str(chart_data.get("city") or "")[:100],
                "state": str(chart_data.get("state") or "")[:50],
                "name": str(chart_data.get("name") or "")[:100]
            }
            metadata["chart_data"] = json.dumps(minimal_data)

        # Mode MUST match the price type
        mode = 'subscription' if is_recurring else 'payment'

        # Stripe expects a literal "{CHECKOUT_SESSION_ID}" placeholder in the final URL.
        # Some callers may already include it; avoid double-appending.
        final_success_url = success_url or ""
        if "{CHECKOUT_SESSION_ID}" not in final_success_url:
            sep = "&" if "?" in final_success_url else "?"
            final_success_url = f"{final_success_url}{sep}session_id={{CHECKOUT_SESSION_ID}}"
        
        session_kwargs = {
            'payment_method_types': ['card'],
            'line_items': [{
                'price': price_id,
                'quantity': 1,
            }],
            'mode': mode,
            'allow_promotion_codes': True,
            'success_url': final_success_url,
            'cancel_url': cancel_url,
            'customer_email': user.email,
            'client_reference_id': user.id,
            'metadata': metadata,
        }

        if mode == 'subscription':
            session_kwargs['subscription_data'] = {
                "metadata": {
                    "user_id": user.id,
                    "plan_tier": plan.tier
                },
            }

            # If the user is currently on an internal trial for the same tier, align Stripe billing start to trial end.
            try:
                sub = user.subscription
                if sub and sub.status == "trial" and sub.trial_end_date and sub.trial_end_date > datetime.now(timezone.utc):
                    # Only apply if they are checking out the same tier they're trialing.
                    if sub.plan and sub.plan.tier == plan.tier:
                        session_kwargs['subscription_data']["trial_end"] = int(sub.trial_end_date.timestamp())
            except Exception as e:
                logger.warning("Trial alignment failed, proceeding with normal checkout: %s", repr(e), exc_info=True)
        else:
            # For one-time payments, we might want invoice creation enabled to track it easily
            session_kwargs['invoice_creation'] = {
                'enabled': True,
                'invoice_data': {
                    'metadata': metadata
                }
            }

        checkout_session = stripe.checkout.Session.create(**session_kwargs)
        return checkout_session

    def upgrade_plan(self, user: User, plan_tier: str, annual: bool = False):
        sub = user.subscription
        if not sub or not sub.stripe_subscription_id:
             raise ValueError("No active Stripe subscription to upgrade. Use checkout instead.")
        
        new_plan = self.get_plan_by_tier(plan_tier)
        if not new_plan:
             raise ValueError("Invalid Plan")

        price_id = new_plan.stripe_price_id_annual if annual else new_plan.stripe_price_id_monthly
        if not price_id:
             raise ValueError("Plan not configured for this billing period")

        # Get stripe sub to find item id
        # In a real app we might cache item_id or iterate items
        stripe_sub = stripe.Subscription.retrieve(sub.stripe_subscription_id)
        item_id = stripe_sub['items']['data'][0]['id']
        
        # Modify Subscription (Proration is default in Stripe)
        stripe.Subscription.modify(
            sub.stripe_subscription_id,
            items=[{
                'id': item_id,
                'price': price_id, 
            }]
        )
        
        # Local update
        sub.plan_id = new_plan.id
        self.db.commit()
        return sub

    def handle_webhook(self, event: dict):
        event_type = event['type']
        
        if event_type == 'checkout.session.completed':
            session = event['data']['object']
            self._process_subscription_success(session)
        elif event_type == 'invoice.payment_succeeded':
            invoice = event['data']['object']
            self._process_payment_succeeded(invoice)
        elif event_type == 'invoice.payment_failed':
            invoice = event['data']['object']
            self._process_payment_failed(invoice)
        elif event_type == 'customer.subscription.deleted':
            sub_data = event['data']['object']
            self._process_subscription_deleted(sub_data)
        elif event_type == 'customer.subscription.updated':
            sub_data = event['data']['object']
            self._process_subscription_updated(sub_data)

    def _process_subscription_success(self, session: dict):
        user_id = session.get("client_reference_id") or session.get("metadata", {}).get("user_id")
        if not user_id: return

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user: return

        plan_tier = session.get("metadata", {}).get("plan_tier")
        plan = self.get_plan_by_tier(plan_tier)
        if not plan: return

        stripe_sub_id = session.get("subscription")
        stripe_cust_id = session.get("customer")

        sub = user.subscription
        if not sub:
            sub = UserSubscription(user_id=user.id)
            self.db.add(sub)

        sub.plan_id = plan.id
        sub.stripe_customer_id = stripe_cust_id
        sub.stripe_subscription_id = stripe_sub_id
        
        # Stripe sub details
        if stripe_sub_id:
            stripe_sub = stripe.Subscription.retrieve(stripe_sub_id)
            sub.current_period_start = datetime.fromtimestamp(stripe_sub.current_period_start, tz=timezone.utc)
            sub.current_period_end = datetime.fromtimestamp(stripe_sub.current_period_end, tz=timezone.utc)

            # Preserve trial state if Stripe says we're trialing.
            stripe_status = stripe_sub.get("status")
            if stripe_status == "trialing":
                sub.status = "trial"
                trial_start = stripe_sub.get("trial_start")
                trial_end = stripe_sub.get("trial_end")
                sub.trial_start_date = datetime.fromtimestamp(trial_start, tz=timezone.utc) if trial_start else sub.trial_start_date
                sub.trial_end_date = datetime.fromtimestamp(trial_end, tz=timezone.utc) if trial_end else sub.trial_end_date
            else:
                sub.status = "active"
                sub.trial_start_date = None
                sub.trial_end_date = None
        else:
            # No subscription object (e.g., misconfigured checkout). Mark active to avoid lockouts.
            sub.status = "active"
            sub.trial_start_date = None
            sub.trial_end_date = None
        
        self.db.commit()

        # Notify Admin
        try:
            amount = session.get("amount_total", 0) / 100.0
            is_recurring = session.get("mode") == "subscription"
            AdminNotificationService.notify_purchase_completed(
                user_email=user.email,
                plan_tier=plan_tier,
                amount=amount,
                is_recurring=is_recurring
            )
        except Exception as e:
            logger.error("Failed to send admin notification for purchase: %s", repr(e), exc_info=True)

    def _process_payment_succeeded(self, invoice: dict):
        # Log invoice
        user_id = None
        # Try to find sub by stripe customer
        customer_id = invoice.get("customer")
        sub = self.db.query(UserSubscription).filter(UserSubscription.stripe_customer_id == customer_id).first()
        
        if sub:
            sub.status = "active"
            if invoice.get("period_end"):
                sub.current_period_end = datetime.fromtimestamp(invoice.get("period_end"), tz=timezone.utc)
            self.db.commit()
            
            # Notify Admin (recurring payment)
            try:
                user = sub.user
                plan_tier = sub.plan.tier if sub.plan else "unknown"
                amount = invoice.get("amount_paid", 0) / 100.0
                AdminNotificationService.notify_purchase_completed(
                    user_email=user.email,
                    plan_tier=plan_tier,
                    amount=amount,
                    is_recurring=True
                )
            except Exception as e:
                logger.error("Failed to send admin notification for recurring payment: %s", repr(e), exc_info=True)

            # Create Invoice Record
            new_inv = Invoice(
                user_id=sub.user_id,
                subscription_id=sub.id,
                stripe_invoice_id=invoice.get("id"),
                amount_due=(invoice.get("amount_due") or 0) / 100.0,
                amount_paid=(invoice.get("amount_paid") or 0) / 100.0,
                status=invoice.get("status"),
                pdf_url=invoice.get("invoice_pdf"),
                created_at=datetime.now(timezone.utc)
            )
            self.db.add(new_inv)
            self.db.commit()

    def _process_payment_failed(self, invoice: dict):
        customer_id = invoice.get("customer")
        sub = self.db.query(UserSubscription).filter(UserSubscription.stripe_customer_id == customer_id).first()
        if sub:
            sub.status = "past_due"
            self.db.commit()
            
            # Notify Admin
            try:
                user = sub.user
                plan_tier = sub.plan.tier if sub.plan else "unknown"
                error_obj = invoice.get("last_payment_error") or {}
                error_msg = error_obj.get("message", "Payment failed")
                AdminNotificationService.notify_payment_failed(
                    user_email=user.email,
                    plan_tier=plan_tier,
                    error_message=error_msg
                )
            except Exception as e:
                logger.error("Failed to send admin notification for payment failure: %s", repr(e), exc_info=True)

    def _process_subscription_deleted(self, sub_data: dict):
        stripe_id = sub_data.get("id")
        sub = self.db.query(UserSubscription).filter(UserSubscription.stripe_subscription_id == stripe_id).first()
        if sub:
            sub.status = "canceled"
            self.db.commit()
            
    def _process_subscription_updated(self, sub_data: dict):
        stripe_id = sub_data.get("id")
        sub = self.db.query(UserSubscription).filter(UserSubscription.stripe_subscription_id == stripe_id).first()
        if sub:
            period_end_ts = sub_data.get("current_period_end")
            if period_end_ts is not None:
                sub.current_period_end = datetime.fromtimestamp(period_end_ts, tz=timezone.utc)
            sub.cancel_at_period_end = sub_data.get("cancel_at_period_end")
            status = sub_data.get("status")
            if status == "active":
                sub.status = "active"
            elif status == "trialing":
                sub.status = "trial"
                trial_start = sub_data.get("trial_start")
                trial_end = sub_data.get("trial_end")
                if trial_start:
                    sub.trial_start_date = datetime.fromtimestamp(trial_start, tz=timezone.utc)
                if trial_end:
                    sub.trial_end_date = datetime.fromtimestamp(trial_end, tz=timezone.utc)
            elif status == "past_due":
                sub.status = "past_due"
            self.db.commit()

    def cancel_subscription(self, user: User, immediate: bool = False):
        sub = user.subscription
        if not sub or not sub.stripe_subscription_id:
             raise ValueError("No active Stripe subscription to cancel")

        if immediate:
            stripe.Subscription.delete(sub.stripe_subscription_id)
            sub.status = "canceled"
            sub.cancel_at_period_end = False
        else:
            stripe.Subscription.modify(
                sub.stripe_subscription_id,
                cancel_at_period_end=True
            )
            sub.cancel_at_period_end = True
        
        self.db.commit()
        return sub

    def get_usage_stats(self, user: User):
        sub = user.subscription
        if not sub:
            return {"charts": 0, "api": 0, "chart_limit": 1, "api_limit": 0}

        plan = sub.plan
        chart_period_start = sub.current_period_start or datetime.now(timezone.utc).replace(day=1)
        api_period_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        from sqlalchemy import func
        chart_usage = self.db.query(func.sum(UsageRecord.cost_credits)).filter(
            UsageRecord.subscription_id == sub.id,
            UsageRecord.resource_type == "chart",
            UsageRecord.created_at >= chart_period_start
        ).scalar() or 0

        api_usage = self.db.query(func.sum(UsageRecord.cost_credits)).filter(
            UsageRecord.subscription_id == sub.id,
            UsageRecord.resource_type == "api_call",
            UsageRecord.created_at >= api_period_start
        ).scalar() or 0

        return {
            "charts": int(chart_usage),
            "api": int(api_usage),
            "chart_limit": plan.chart_quota,
            "api_limit": plan.api_quota
        }
