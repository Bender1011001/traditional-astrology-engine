from fastapi import APIRouter

# Base router for API V2
# This will be the home for any future breaking changes to the JSON contract.
v2_router = APIRouter()


@v2_router.get("/status")
async def get_status():
    return {"version": "v2.0.0-beta", "status": "active"}
