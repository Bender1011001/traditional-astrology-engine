import sys
import os

# Ensure src is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging
import time

from src.core.config import settings
from src.api.v1.router import api_router as v1_router
from src.api.v2.router import v2_router
from src.engine.logger import configure_logging, ActivityLogger

# Initialize centralized logging
configure_logging()

app = FastAPI(
    title="Traditional Astrology Engine",
    description="A high-precision engine for pre-1700s Traditional Astrology.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- MIDDLEWARE ---

# Request Logging Middleware
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log Request
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        method = request.method
        path = request.url.path
        
        ActivityLogger.log_activity(
            "request_received", 
            ip=client_ip, 
            details={
                "method": method, 
                "path": path, 
                "user_agent": user_agent
            }
        )
        
        response = await call_next(request)
        
        # Log Response
        process_time = time.time() - start_time
        
        ActivityLogger.log_activity(
            "request_completed",
            ip=client_ip,
            details={
                "method": method, 
                "path": path, 
                "status_code": response.status_code,
                "duration_sec": round(process_time, 4)
            }
        )
        
        return response

# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://*.googletagmanager.com https://*.google-analytics.com https://*.google.com https://cdn.jsdelivr.net https://static.cloudflareinsights.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://*.googletagmanager.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https://*.googletagmanager.com https://*.google-analytics.com https://*.google.com https://*.doubleclick.net; connect-src 'self' https://photon.komoot.io https://*.google-analytics.com https://*.analytics.google.com https://*.googletagmanager.com https://*.doubleclick.net;"
        return response

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# CORS Configuration
_default_origins = [settings.SITE_BASE_URL, "http://localhost:8000", "http://127.0.0.1:8000"]
_env_origins = settings.CORS_ORIGINS.split(',')
_cors_origins = [o.strip() for o in _env_origins if o.strip()] or _default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GLOBAL EXCEPTION HANDLERS ---
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"success": False, "detail": str(exc.errors()), "body": str(exc.body)},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.exception(f"Unhandled Exception on {request.method} {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "detail": "Internal Server Error. Please contact support."},
    )

# --- ROUTER MOUNT ---
app.include_router(v1_router, prefix="/api/v1")
app.include_router(v2_router, prefix="/api/v2")

# --- STATIC FILES ---
from fastapi.staticfiles import StaticFiles

# Mount static files (HTML, CSS, JS)
# We mount at the root ("/") to serve index.html by default.
# NOTE: This must be mounted AFTER the API router to ensure API routes take precedence.
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
# Temporary legacy support or strict adherence? Plan says "No Legacy Support".
# But to test locally easily without changing frontend immediately, I might want to mount at /api too?
# Nah, let's stick to the plan.
