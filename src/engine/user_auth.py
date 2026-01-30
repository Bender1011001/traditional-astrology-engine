"""
User Authentication Module for Codex Caelestis.
Uses password hashing and JWT tokens for secure authentication.
Stores users in a simple JSON file (can be upgraded to a real database later).
"""

import os
import json
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path

# User database file location
USER_DB_PATH = os.getenv("USER_DB_PATH", os.path.join(os.path.dirname(__file__), "users.json"))

class UserManager:
    """Simple user management with file-based storage."""
    
    def __init__(self, db_path: str = USER_DB_PATH):
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self) -> None:
        """Create the database file if it doesn't exist."""
        if not os.path.exists(self.db_path):
            self._save_db({"users": {}, "meta": {"created": datetime.utcnow().isoformat()}})
    
    def _load_db(self) -> Dict[str, Any]:
        """Load the user database from disk."""
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"users": {}, "meta": {"created": datetime.utcnow().isoformat()}}
    
    def _save_db(self, db: Dict[str, Any]) -> None:
        """Save the user database to disk."""
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2)
    
    def _hash_password(self, password: str, salt: Optional[str] = None) -> tuple:
        """Hash a password using SHA-256 with salt."""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2-like approach with multiple rounds
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100k iterations for security
        ).hex()
        
        return hashed, salt
    
    def _verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Verify a password against stored hash and salt."""
        computed_hash, _ = self._hash_password(password, salt)
        return secrets.compare_digest(computed_hash, stored_hash)
    
    def create_user(self, email: str, password: str, name: str = "") -> Dict[str, Any]:
        """
        Create a new user account.
        
        Returns:
            Dict with 'success' boolean and 'message' or 'user' data.
        """
        email = email.lower().strip()
        
        # Validate email format
        if not email or "@" not in email or "." not in email.split("@")[-1]:
            return {"success": False, "message": "Invalid email address."}
        
        # Validate password strength
        if len(password) < 8:
            return {"success": False, "message": "Password must be at least 8 characters."}
        
        db = self._load_db()
        
        # Check if user already exists
        if email in db["users"]:
            return {"success": False, "message": "An account with this email already exists."}
        
        # Hash the password
        hashed_password, salt = self._hash_password(password)
        
        # Create user record
        user_id = secrets.token_urlsafe(16)
        user = {
            "id": user_id,
            "email": email,
            "name": name.strip(),
            "password_hash": hashed_password,
            "salt": salt,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "subscription_tier": "free",
            "subscription_expires": None,
            "charts_saved": [],
            "email_verified": False,
            "verification_token": secrets.token_urlsafe(32)
        }
        
        db["users"][email] = user
        self._save_db(db)
        
        logging.info(f"User created: {email}")
        
        # Return safe user data (exclude password info)
        return {
            "success": True,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "subscription_tier": user["subscription_tier"]
            }
        }
    
    def authenticate(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user with email and password.
        
        Returns:
            Dict with 'success' boolean and user data or error message.
        """
        email = email.lower().strip()
        
        db = self._load_db()
        
        if email not in db["users"]:
            # Use generic message to prevent email enumeration
            return {"success": False, "message": "Invalid email or password."}
        
        user = db["users"][email]
        
        if not self._verify_password(password, user["password_hash"], user["salt"]):
            return {"success": False, "message": "Invalid email or password."}
        
        # Update last login
        user["last_login"] = datetime.utcnow().isoformat()
        db["users"][email] = user
        self._save_db(db)
        
        logging.info(f"User authenticated: {email}")
        
        # Return safe user data
        return {
            "success": True,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "subscription_tier": user["subscription_tier"],
                "charts_saved": user.get("charts_saved", [])
            }
        }
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user data by email (excludes password info)."""
        email = email.lower().strip()
        db = self._load_db()
        
        if email not in db["users"]:
            return None
        
        user = db["users"][email]
        return {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "subscription_tier": user["subscription_tier"],
            "created_at": user["created_at"],
            "charts_saved": user.get("charts_saved", [])
        }
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user data by ID (excludes password info)."""
        db = self._load_db()
        
        for email, user in db["users"].items():
            if user["id"] == user_id:
                return {
                    "id": user["id"],
                    "email": user["email"],
                    "name": user["name"],
                    "subscription_tier": user["subscription_tier"],
                    "created_at": user["created_at"],
                    "charts_saved": user.get("charts_saved", [])
                }
        return None
    
    def update_subscription(self, email: str, tier: str, expires: Optional[str] = None) -> bool:
        """Update user's subscription tier."""
        email = email.lower().strip()
        db = self._load_db()
        
        if email not in db["users"]:
            return False
        
        db["users"][email]["subscription_tier"] = tier
        db["users"][email]["subscription_expires"] = expires
        db["users"][email]["updated_at"] = datetime.utcnow().isoformat()
        
        self._save_db(db)
        return True
    
    def save_chart(self, email: str, chart_hash: str, chart_meta: Dict[str, Any]) -> bool:
        """Save a chart reference to user's account."""
        email = email.lower().strip()
        db = self._load_db()
        
        if email not in db["users"]:
            return False
        
        charts = db["users"][email].get("charts_saved", [])
        
        # Avoid duplicates
        if not any(c.get("hash") == chart_hash for c in charts):
            charts.append({
                "hash": chart_hash,
                "saved_at": datetime.utcnow().isoformat(),
                **chart_meta
            })
            # Keep max 50 charts per user
            if len(charts) > 50:
                charts = charts[-50:]
            
            db["users"][email]["charts_saved"] = charts
            self._save_db(db)
        
        return True
    
    def change_password(self, email: str, old_password: str, new_password: str) -> Dict[str, Any]:
        """Change user's password."""
        email = email.lower().strip()
        
        # Verify current password
        auth_result = self.authenticate(email, old_password)
        if not auth_result["success"]:
            return {"success": False, "message": "Current password is incorrect."}
        
        # Validate new password strength
        if len(new_password) < 8:
            return {"success": False, "message": "New password must be at least 8 characters."}
        
        db = self._load_db()
        
        hashed_password, salt = self._hash_password(new_password)
        db["users"][email]["password_hash"] = hashed_password
        db["users"][email]["salt"] = salt
        db["users"][email]["updated_at"] = datetime.utcnow().isoformat()
        
        self._save_db(db)
        
        return {"success": True, "message": "Password changed successfully."}


# Singleton instance
_user_manager = None

def get_user_manager() -> UserManager:
    """Get or create the user manager singleton."""
    global _user_manager
    if _user_manager is None:
        _user_manager = UserManager()
    return _user_manager
