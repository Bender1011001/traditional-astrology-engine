from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, JSON, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timezone
import uuid
from .core import Base

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, default="")
    password_hash = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime, nullable=True)
    

    # Verification
    email_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    
    # Password Reset
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)


    # Charts data (keeping as JSON for now for compatibility/simplicity as per notes)
    charts_saved = Column(JSON, default=list)

    # Relationships
    subscription = relationship("UserSubscription", back_populates="user", uselist=False)
    api_keys = relationship("ApiKey", back_populates="user")

    def to_dict(self):
        sub_data = {
            "status": "none",
            "plan_name": "Free",
            "current_period_end": None,
            "is_trial": False
        }
        if self.subscription:
            sub_data = {
                "status": self.subscription.status,
                "plan_name": self.subscription.plan.tier if self.subscription.plan else "Free",
                "current_period_end": self.subscription.current_period_end.isoformat() if self.subscription.current_period_end else None,
                "is_trial": self.subscription.status == "trial",
                "cancel_at_period_end": bool(self.subscription.cancel_at_period_end),
                "has_stripe_subscription": bool(self.subscription.stripe_subscription_id),
            }

        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "charts_saved": self.charts_saved or [],
            "subscription_details": sub_data
        }

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tier = Column(String(20), unique=True, nullable=False) # e.g., 'free', 'practitioner'
    chart_quota = Column(Integer, nullable=True) # None = unlimited
    api_quota = Column(Integer, nullable=True) # New: API calls per month
    price_monthly = Column(Numeric(10, 2), nullable=False)
    price_annual = Column(Numeric(10, 2), nullable=True) # New: Annual price
    stripe_price_id_monthly = Column(String)
    stripe_price_id_annual = Column(String) # New: Stripe Annual ID
    features = Column(JSON, default=dict)

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    plan_id = Column(String, ForeignKey("subscription_plans.id"))
    status = Column(String(20), default="active") # trial, active, past_due, canceled
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True) # New
    
    # Dates
    trial_start_date = Column(DateTime, nullable=True) # New
    trial_end_date = Column(DateTime, nullable=True) # New
    current_period_start = Column(DateTime, default=lambda: datetime.now(timezone.utc)) # New
    current_period_end = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, default=False) # New

    user = relationship("User", back_populates="subscription")
    plan = relationship("SubscriptionPlan")
    usage_records = relationship("UsageRecord", back_populates="subscription")
    invoices = relationship("Invoice", back_populates="subscription")

class UsageRecord(Base):
    __tablename__ = "usage_records"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    subscription_id = Column(String, ForeignKey("user_subscriptions.id"))
    user_id = Column(String, ForeignKey("users.id")) # Denormalized for query speed
    resource_type = Column(String, nullable=False) # 'chart_generation', 'api_call'
    resource_id = Column(String, nullable=True) # ID of the resource used
    cost_credits = Column(Integer, default=1)
    metadata_json = Column(JSON, default=dict) # 'metadata' is reserved in some SQL
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    subscription = relationship("UserSubscription", back_populates="usage_records")

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    subscription_id = Column(String, ForeignKey("user_subscriptions.id"))
    stripe_invoice_id = Column(String)
    amount_due = Column(Numeric(10, 2))
    amount_paid = Column(Numeric(10, 2))
    status = Column(String(20))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    pdf_url = Column(String)

    subscription = relationship("UserSubscription", back_populates="invoices")

class ApiKey(Base):
    __tablename__ = "api_keys"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    key_hash = Column(String, unique=True, nullable=False)
    name = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_used = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="api_keys")

class AstrologicalDelineation(Base):
    __tablename__ = "astrological_delineations"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    category = Column(String, nullable=False, index=True) # e.g., 'planets_in_signs'
    key = Column(String, nullable=False, index=True)      # e.g., 'SATURN_ARIES_DAY'
    content = Column(JSON, nullable=False)               # Stores text or structured JSON
    is_manual_override = Column(Boolean, default=False)  # Flag to prevent auto-overwrite
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Lead(Base):
    """
    Marketing lead capture (operational intake).

    Safety:
    - No birth data is stored here.
    - This is strictly for product/market fit and outreach operations.
    """

    __tablename__ = "leads"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, nullable=False, index=True)
    segment = Column(String, nullable=True, index=True)
    platform = Column(String, nullable=True)
    volume = Column(String, nullable=True)
    pain = Column(String, nullable=True)
    url = Column(String, nullable=True)
    ua = Column(String, nullable=True)
    ip = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class OutreachTarget(Base):
    """
    Outbound outreach targets (from research / manual compilation).

    This is not inbound "lead capture" from the website; it's a curated list
    of people/shops/platform identities we want to contact.
    """

    __tablename__ = "outreach_targets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    segment = Column(String, nullable=True, index=True)  # teacher | content_creator | pdf_seller | studio | unknown
    platform_primary = Column(String, nullable=True, index=True)  # etsy | substack | patreon | website | instagram | other
    primary_contact = Column(String, nullable=True)
    secondary_contact = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    source = Column(String, nullable=True)  # e.g., docs/research/... file name
    last_verified = Column(String, nullable=True)  # ISO date string (lightweight, avoids TZ issues)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class OutreachAttempt(Base):
    """
    Tracks outbound outreach attempts (email only for now).

    We intentionally separate this from inbound "Lead" capture:
    - OutreachTarget: who we plan to contact
    - OutreachAttempt: what we attempted/sent, and when
    """

    __tablename__ = "outreach_attempts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    target_id = Column(String, ForeignKey("outreach_targets.id"), index=True)

    channel = Column(String, nullable=False, default="email")  # email | etsy_message | instagram_dm | contact_form
    to_addr = Column(String, nullable=True, index=True)
    subject = Column(String, nullable=True)
    template_id = Column(String, nullable=True)  # e.g., teacher_v1

    status = Column(String, nullable=False, default="queued")  # queued | sent | failed | skipped
    error_message = Column(String, nullable=True)

    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    target = relationship("OutreachTarget")

class GuestRequest(Base):
    """
    Tracks free reading usage by IP address.
    """
    __tablename__ = "guest_requests"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ip_address = Column(String, index=True, nullable=False)
    request_type = Column(String, default="premium_guest") # 'basic', 'premium_guest'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class AsyncReportTask(Base):
    """
    Tracks background generation of premium reports.
    """
    __tablename__ = "async_report_tasks"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(String, default="pending") # pending, processing, completed, failed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    result_json = Column(JSON, nullable=True) # Store result or error
    
    # Metadata to re-identify the request
    request_meta = Column(JSON, default=dict) # {name, date, city...}
