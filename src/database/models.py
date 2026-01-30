from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .core import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, default="")
    password_hash = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    subscription_tier = Column(String, default="free")
    subscription_expires = Column(DateTime, nullable=True)
    
    # Verification (from user_auth.py logic)
    email_verified = Column(JSON, default=False) # Boolean
    verification_token = Column(String, nullable=True)

    # For charts, we will use a separate table but we can also use a JSON column
    # if we want to strictly mimic the document store behavior.
    # Given the constraint of "50 charts max" and the existing logic, 
    # a JSON column is actually more aligned with the current "blob" logic 
    # and requires less migration logic for the code consuming it.
    # However, for a "REAL database", a separate table is better.
    # Let's use a JSON column called 'charts_data' for now to ensure 100% compatibility 
    # with the 'charts_saved' list of dicts structure without complex joining/serializing.
    # SQLite supports JSON type (as Text). Postgres supports JSONB.
    charts_saved = Column(JSON, default=list) 

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "subscription_tier": self.subscription_tier,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "charts_saved": self.charts_saved or []
        }
