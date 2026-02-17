from fastapi import APIRouter
from src.api.v1.endpoints import charts, synastry, mundane, telemetry, forensic, billing, developer, owner, meta

api_router = APIRouter()

api_router.include_router(charts.router, tags=["charts"])
api_router.include_router(charts.router, prefix="/charts", tags=["charts"])
api_router.include_router(synastry.router, tags=["synastry"])
api_router.include_router(mundane.router, tags=["mundane"])
api_router.include_router(forensic.router, prefix="/forensic", tags=["forensic"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
api_router.include_router(telemetry.router, tags=["telemetry"])
api_router.include_router(developer.router, prefix="/developer", tags=["developer"])
api_router.include_router(owner.router, prefix="/owner", tags=["owner"])
api_router.include_router(meta.router, tags=["meta"])

from src.api.v1.endpoints import auth
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

from src.api.v1.endpoints import admin
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
