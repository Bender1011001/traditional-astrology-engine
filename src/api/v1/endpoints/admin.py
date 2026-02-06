from fastapi import APIRouter, HTTPException, Query
import sys
import os

# Ensure the src directory is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from src.scripts.apply_schema_patch import patch_database

router = APIRouter()

@router.get("/patch_db")
def trigger_patch_db(key: str = Query(..., description="Emergency Admin Key")):
    """
    Emergency endpoint to trigger database schema patch.
    """
    # Hardcoded emergency key as agreed in plan
    if key != "emergency_patch_2026":
        raise HTTPException(status_code=403, detail="Forbidden")
    
    try:
        patch_database()
        return {"success": True, "message": "Database patch applied successfully."}
    except Exception as e:
        return {"success": False, "message": f"Error patching database: {str(e)}"}
