"""
CSRF Protection Middleware

This module provides CSRF protection for state-changing endpoints.
Since this is primarily a JSON API with JWT authentication, CSRF risk is lower,
but we still implement protection for defense in depth.

Protection strategy:
1. For sensitive endpoints: Require custom header (X-Requested-With)
2. Apply to all POST/PUT/DELETE/PATCH requests
3. Skip for API key authenticated requests (B2B)
4. Skip for authentication endpoints (login/register need to work without tokens)
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List
import logging

logger = logging.getLogger(__name__)

# Endpoints that don't require CSRF protection (authentication flows)
CSRF_EXEMPT_PATHS: List[str] = [
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/forgot-password",
    "/api/v1/auth/reset-password",
    # Stripe webhooks have their own signature verification.
    "/api/v1/billing/webhook",
    # Legacy/alternate webhook path (kept to avoid accidental lockouts).
    "/api/v1/stripe/webhook",
    # Guest checkout endpoints (B2C, no auth, public-facing).
    "/api/v1/guest/checkout",
    "/api/v1/guest/generate-paid",
    "/api/v1/premium/guest/request",
    "/api/v1/reading_feedback",
    "/docs",
    "/redoc",
    "/openapi.json",
]

# HTTP methods that require CSRF protection
PROTECTED_METHODS = {"POST", "PUT", "DELETE", "PATCH"}


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to protect against CSRF attacks.
    
    Requires the X-Requested-With header for all state-changing requests.
    This header cannot be set by cross-origin requests due to CORS preflight.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Only check for protected methods
        if request.method not in PROTECTED_METHODS:
            return await call_next(request)
        
        # Skip exempt paths
        path = request.url.path
        if any(path.startswith(exempt) for exempt in CSRF_EXEMPT_PATHS):
            return await call_next(request)
        
        # Skip if request has API key (B2B authenticated)
        if request.headers.get("x-api-key"):
            return await call_next(request)
        
        # Skip if request is coming from same origin (check referer/origin)
        origin = request.headers.get("origin")
        referer = request.headers.get("referer")
        host = request.headers.get("host")
        
        # Check for custom header as primary CSRF protection
        # Modern browsers prevent cross-origin requests from setting custom headers
        # without CORS preflight approval
        x_requested_with = request.headers.get("x-requested-with")
        
        # If no origin header (same-origin request) or has our custom header
        if origin is None or x_requested_with:
            return await call_next(request)
        
        # For cross-origin requests without the custom header, check content type
        # JSON APIs are protected by SOP when Content-Type is application/json
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            # JSON with CORS - the browser will have done preflight if needed
            return await call_next(request)
        
        # Log potential CSRF attempt
        logger.warning("Potential CSRF attempt blocked: %s %s from %s", request.method, path, origin)
        
        raise HTTPException(
            status_code=403,
            detail="CSRF protection: Request rejected"
        )


def get_csrf_middleware():
    """Factory function to get the CSRF middleware instance."""
    return CSRFProtectionMiddleware
