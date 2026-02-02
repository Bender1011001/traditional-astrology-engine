"""
User Authentication Module for Codex Caelestis (SQLAlchemy Version).
Supports persistence via SQLite (default) or PostgreSQL.
"""

import os
import secrets
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
import bcrypt

from sqlalchemy.orm import Session
from src.database.core import SessionLocal, engine, Base
from src.database.models import User

# Initialize tables
Base.metadata.create_all(bind=engine)

class UserManager:
    """User management using SQLAlchemy."""
    
    def __init__(self):
        # Tables are created at module level, but we could do it here too.
        # Simple in-memory rate limiter: {key: [(timestamp, count)]}
        # Actually just store list of timestamps
        self._rate_limits: Dict[str, List[datetime]] = {}
        
    def _check_rate_limit(self, key: str, limit: int = 5, window: int = 60) -> bool:
        """
        Check if action is allowed for key.
        limit: max attempts
        window: seconds
        Returns True if allowed, False if blocked.
        """
        now = datetime.utcnow()
        if key not in self._rate_limits:
            self._rate_limits[key] = []
            
        # Prune old
        self._rate_limits[key] = [t for t in self._rate_limits[key] if (now - t).total_seconds() < window]
        
        if len(self._rate_limits[key]) >= limit:
            return False
            
        self._rate_limits[key].append(now)
        return True
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        # hashpw requires bytes, returns bytes. decoding to str for storage.
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify a password against stored hash."""
        # checkpw requires bytes.
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
    
    def create_user(self, email: str, password: str, name: str = "") -> Dict[str, Any]:
        """Create a new user account."""
        email = email.lower().strip()
        
        # Rate Limit: 3 attempts per hour per email (prevents spam registration)
        # Note: IP based limiting would be better here but we lack IP context
        if not self._check_rate_limit(f"create:{email}", limit=3, window=3600):
             return {"success": False, "message": "Too many account creation attempts. Please try again later."}
        
        if not email or "@" not in email or "." not in email.split("@")[-1]:
            return {"success": False, "message": "Invalid email address."}
        
        if len(password) < 8:
            return {"success": False, "message": "Password must be at least 8 characters."}
        
        db = SessionLocal()
        try:
            # Check existing
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                return {"success": False, "message": "An account with this email already exists."}
            
            hashed_password = self._hash_password(password)
            user_id = secrets.token_urlsafe(16)
            
            new_user = User(
                id=user_id,
                email=email,
                name=name.strip(),
                password_hash=hashed_password,
                salt="", # Deprecated/Unused with bcrypt
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                # subscription_tier="free", # Removed in v2 schema
                email_verified=False,
                verification_token=secrets.token_urlsafe(32),
                charts_saved=[]
            )
            
            # Auto-create free subscription (Phase 2 Requirement)
            from src.services.subscription import SubscriptionService
            service = SubscriptionService(db)
            service.start_trial(new_user, "free", trial_days=0) # Or just create free sub directly
            
            # Correction: start_trial creates the sub. But wait, create_user is sync?
            # SubscriptionService uses DB session. We can use it.
            # But start_trial logic assumes user has 'subscription' rel loaded?
            # Actually, `start_trial` creates the UserSubscription object attached to user.
            
            # Let's just create User first.
            db.add(new_user)
            db.commit() # Commit user first to get ID/ref
            
            # Now add subscription
            # Note: start_trial requires the user object to be part of session or re-queried?
            # It's attached to this session.
            
            # Subscription is already handled by start_trial (or will be added here properly if needed in future)
            # The previous code block here caused an IntegrityError by trying to insert a second subscription
            # for the same user_id. We rely on start_trial or the calling logic to handle this.

            
            db.refresh(new_user)
            
            logging.info(f"User created: {email}")
            
            return {
                "success": True, 
                "user": new_user.to_dict()
            }
        except Exception as e:
            db.rollback()
            logging.error(f"Create user error: {e}")
            return {"success": False, "message": "Database error during registration."}
        finally:
            db.close()
    
    def authenticate(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate a user."""
        email = email.lower().strip()
        
        # Rate Limit: 5 attempts per minute per email
        if not self._check_rate_limit(f"auth:{email}", limit=5, window=60):
            logging.warning(f"Rate limit exceeded for user: {email}")
            return {"success": False, "message": "Too many login attempts. Please try again later."}
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            
            if not user or not self._verify_password(password, user.password_hash):
                return {"success": False, "message": "Invalid email or password."}
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()
            
            logging.info(f"User authenticated: {email}")
            
            # Return dict with charts included
            user_data = user.to_dict()
            # Ensure charts_saved is a list (DB might return None)
            if user_data["charts_saved"] is None:
                user_data["charts_saved"] = []
                
            return {
                "success": True,
                "user": user_data
            }
        finally:
            db.close()
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        email = email.lower().strip()
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            return user.to_dict() if user else None
        finally:
            db.close()
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            return user.to_dict() if user else None
        finally:
            db.close()
    
    # update_subscription: DEPRECATED in v2. Use SubscriptionService.upgrade_plan.
    
    def save_chart(self, email: str, chart_hash: str, chart_meta: Dict[str, Any]) -> bool:
        email = email.lower().strip()
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                return False
            
            # Important: Copy list to trigger SQLAlchemy mutation detection
            charts = list(user.charts_saved) if user.charts_saved else []
            
            if not any(c.get("hash") == chart_hash for c in charts):
                entry = {
                    "hash": chart_hash,
                    "saved_at": datetime.utcnow().isoformat(),
                    **chart_meta
                }
                charts.append(entry)
                
                if len(charts) > 50:
                    charts = charts[-50:]
                
                user.charts_saved = charts
                user.updated_at = datetime.utcnow()
                
                # Flag modified just in case
                from sqlalchemy.orm.attributes import flag_modified
                flag_modified(user, "charts_saved")
                
                db.commit()
            return True
        except Exception as e:
            logging.error(f"Save chart error: {e}")
            return False
        finally:
            db.close()
    
    def change_password(self, email: str, old_password: str, new_password: str) -> Dict[str, Any]:
        email = email.lower().strip()
        
        # Verify first (this requires a DB check, reuse authenticate logic partially)
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                return {"success": False, "message": "User not found."}
                
            if not self._verify_password(old_password, user.password_hash):
                return {"success": False, "message": "Current password is incorrect."}
            
            if len(new_password) < 8:
                return {"success": False, "message": "New password must be at least 8 characters."}
            
            hashed = self._hash_password(new_password)
            user.password_hash = hashed
            # user.salt = salt # No salt needed for bcrypt context
            user.updated_at = datetime.utcnow()
            
            db.commit()
            return {"success": True, "message": "Password changed successfully."}
        finally:
            db.close()

# Singleton instance
_user_manager = None

def get_user_manager() -> UserManager:
    """Get or create the user manager singleton."""
    global _user_manager
    if _user_manager is None:
        _user_manager = UserManager()
    return _user_manager
