from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, JSON, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .core import Base

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, default="")
    password_hash = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Verification
    email_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)

    # Charts data (keeping as JSON for now for compatibility/simplicity as per notes)
    charts_saved = Column(JSON, default=list)

    # Relationships
    subscription = relationship("UserSubscription", back_populates="user", uselist=False)
    api_keys = relationship("ApiKey", back_populates="user")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "charts_saved": self.charts_saved or [],
            "subscription": self.subscription.status if self.subscription else "none"
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
    current_period_start = Column(DateTime, default=datetime.utcnow) # New
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
    created_at = Column(DateTime, default=datetime.utcnow)
    
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
    created_at = Column(DateTime, default=datetime.utcnow)
    pdf_url = Column(String)

    subscription = relationship("UserSubscription", back_populates="invoices")

class ApiKey(Base):
    __tablename__ = "api_keys"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    key_hash = Column(String, unique=True, nullable=False)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="api_keys")

class AstrologicalDelineation(Base):
    __tablename__ = "astrological_delineations"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    category = Column(String, nullable=False, index=True) # e.g., 'planets_in_signs'
    key = Column(String, nullable=False, index=True)      # e.g., 'SATURN_ARIES_DAY'
    content = Column(JSON, nullable=False)               # Stores text or structured JSON
    is_manual_override = Column(Boolean, default=False)  # Flag to prevent auto-overwrite
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
