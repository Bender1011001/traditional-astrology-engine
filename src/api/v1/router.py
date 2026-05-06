from fastapi import APIRouter
from src.api.v1.endpoints import charts, synastry, mundane, telemetry, forensic, billing, developer, owner, meta
import src.api.v1.endpoints.premium as premium_endpoint

api_router = APIRouter()

api_router.include_router(charts.router, prefix="/charts", tags=["charts"])
api_router.include_router(synastry.router, tags=["synastry"])
api_router.include_router(mundane.router, tags=["mundane"])
api_router.include_router(forensic.router, prefix="/forensic", tags=["forensic"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
api_router.include_router(telemetry.router, tags=["telemetry"])
api_router.include_router(developer.router, prefix="/developer", tags=["developer"])
api_router.include_router(owner.router, prefix="/owner", tags=["owner"])
api_router.include_router(meta.router, tags=["meta"])
api_router.include_router(premium_endpoint.router, prefix="/premium", tags=["premium"])

from src.api.v1.endpoints import guest_checkout
api_router.include_router(guest_checkout.router, prefix="/guest", tags=["guest"])

from src.api.v1.endpoints import auth
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

from src.api.v1.endpoints import admin
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

from src.api.v1.endpoints import daily
api_router.include_router(daily.router, prefix="/charts", tags=["daily-navigator"])

from src.api.v1.endpoints import horary
api_router.include_router(horary.router, tags=["horary"])

from src.api.v1.endpoints import electional
api_router.include_router(electional.router, prefix="/electional", tags=["electional"])

from src.api.v1.endpoints import medical
api_router.include_router(medical.router, prefix="/medical", tags=["medical"])

from src.api.v1.endpoints import content
api_router.include_router(content.router, prefix="/content", tags=["content"])
