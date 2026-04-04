import sys
import os

# Ensure project root is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, RedirectResponse
import logging
import time

from src.core.config import settings
from src.api.v1.router import api_router as v1_router
from src.api.v2.router import v2_router
from src.engine.logger import configure_logging, ActivityLogger

# Initialize centralized logging
configure_logging()

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.debug("Startup event triggered")
    logging.info("Starting up... Initializing database tables.")
    from src.database.core import engine, Base
    from src.database.models import User # Ensure models are loaded
    try:
        logging.debug("Calling create_all()...")
        Base.metadata.create_all(bind=engine)
        logging.debug("create_all() completed.")
        logging.info("Database tables initialized successfully.")
        
        # Auto-seed plans if missing (to prevent 'Plan free not found' errors)
        try:
            from src.services.db_seed import seed_plans
            seed_plans()
            logging.info("Database seeding checked/completed.")
        except Exception as seed_err:
            logging.error("Seeding during startup failed: %s", seed_err)
            
    except Exception as e:
        logging.error("Failed to initialize database tables: %s", e)
        # We don't exit here, let the app try to serve what it can 
        # (or fail specifically on DB routes with clear errors)
    yield
    # No specific shutdown logic implemented yet

app = FastAPI(
    title="Traditional Astrology Engine",
    description="A high-precision engine for pre-1700s Traditional Astrology.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
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

# Domain Canonicalization Middleware
class CanonicalDomainMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        host = request.headers.get("host", "")
        
        # Determine scheme, trusting X-Forwarded-Proto if present (for load balancers)
        scheme = request.headers.get("x-forwarded-proto", request.url.scheme)

        # Skip redirection for localhost to allow local development
        if "localhost" in host or "127.0.0.1" in host:
            return await call_next(request)
        # Skip for test/dev hosts (e.g. unit tests using base_url="http://test")
        if host in {"test", "testserver"} or "." not in host:
            return await call_next(request)
        # Skip for Cloud Run URLs — they handle HTTPS natively
        if host.endswith(".run.app"):
            return await call_next(request)

        # Redirect www.traditional-astrology.com and http to https://traditional-astrology.com
        if host.startswith("www.") or scheme == "http":
            canonical_host = host.replace("www.", "")
            url = f"https://{canonical_host}{request.url.path}"
            if request.url.query:
                url += f"?{request.url.query}"
            return RedirectResponse(url, status_code=301)
        return await call_next(request)

# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://*.googletagmanager.com https://*.google-analytics.com https://*.google.com https://cdn.jsdelivr.net https://static.cloudflareinsights.com https://js.stripe.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://*.googletagmanager.com https://cdn.jsdelivr.net; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https://*.googletagmanager.com https://*.google-analytics.com https://*.google.com https://*.doubleclick.net https://fastapi.tiangolo.com https://*.stripe.com; "
            "connect-src 'self' http://localhost:8000 http://127.0.0.1:8000 https://traditional-astrology.com https://*.run.app https://photon.komoot.io https://*.google-analytics.com https://*.analytics.google.com https://*.googletagmanager.com https://*.doubleclick.net https://*.google.com https://checkout.stripe.com https://api.stripe.com; "
            "frame-src https://checkout.stripe.com https://js.stripe.com; "
            "worker-src 'self'; "
            "manifest-src 'self'"
        )
        response.headers["Content-Security-Policy"] = csp
        return response

class CacheControlMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if request.method == "GET" and response.status_code == 200:
            path = request.url.path
            # Static assets cache aggressively
            if any(path.endswith(ext) for ext in [".js", ".css", ".png", ".jpg", ".jpeg", ".ico", ".svg", ".woff2", ".webp"]):
                response.headers["Cache-Control"] = "public, max-age=86400"
            # HTML pages and root revalidate
            elif path.endswith(".html") or path == "/" or path.startswith("/index"):
                response.headers["Cache-Control"] = "public, max-age=300, must-revalidate"
        return response

# CSRF Protection Middleware
from src.api.v1.middleware.csrf import CSRFProtectionMiddleware

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(CanonicalDomainMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CacheControlMiddleware)
app.add_middleware(CSRFProtectionMiddleware)

# CORS Configuration
_default_origins = [
    settings.SITE_BASE_URL, 
    "http://localhost:8000", 
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "null" # For file:// origins
]
_env_origins = settings.CORS_ORIGINS.split(',') if settings.CORS_ORIGINS else []
_cors_origins = list(set(_default_origins + [o.strip() for o in _env_origins if o.strip()]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GLOBAL EXCEPTION HANDLERS ---
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        # Return the actual array instead of stringified python dicts
        content={"success": False, "detail": exc.errors()},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.exception("Unhandled Exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"success": False, "detail": "Internal Server Error"},
    )

# --- ROUTER MOUNT ---
app.include_router(v1_router, prefix="/api/v1")
app.include_router(v2_router, prefix="/api/v2")

# --- HEALTH CHECK ---
_startup_time = time.time()

@app.get("/api/healthz", include_in_schema=False)
async def healthz():
    return {
        "status": "healthy",
        "version": app.version,
        "uptime_seconds": round(time.time() - _startup_time, 1),
    }

# --- LEGACY PAGE REDIRECTS ---
# All old B2B/auth/tool pages redirect to the main B2C index.
# Static files are mounted at "/" below; these routes must be declared first.
_LEGACY_REDIRECTS = [
    # B2B / SaaS pages
    "gig-economy.html", "developer.html", "developers.html",
    "documentation.html", "api-guide.html",
    # Auth pages
    "login.html", "register.html", "signup.html", "profile.html",
    "forgot-password.html", "reset-password.html",
    # Old misc pages
    "demo.html", "booking.html", "services.html", "pricing.html",
    "blog.html", "resources.html", "advanced.html",
    "preview.html",
    "how-we-audit.html", "owner.html", "status.html", "success.html",
]

for _page in _LEGACY_REDIRECTS:
    _route_path = f"/{_page}"
    def _make_redirect(page=_page):
        async def _redirect():
            return RedirectResponse(url="/#get-reading", status_code=301)
        _redirect.__name__ = f"redirect_{page.replace('.', '_').replace('-', '_')}"
        return _redirect
    app.get(_route_path, include_in_schema=False)(_make_redirect())

# Also catch dashboard paths
@app.get("/dashboard", include_in_schema=False)
async def legacy_dashboard_redirect():
    return RedirectResponse(url="/", status_code=301)

@app.get("/dashboard/", include_in_schema=False)
async def legacy_dashboard_slash_redirect():
    return RedirectResponse(url="/", status_code=301)

# --- STATIC FILES ---
from fastapi.staticfiles import StaticFiles

# Mount static files (HTML, CSS, JS)
# We mount at the root ("/") to serve index.html by default.
# NOTE: This must be mounted AFTER the API router to ensure API routes take precedence.
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
