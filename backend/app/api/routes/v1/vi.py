from fastapi import APIRouter, HTTPException

from app.services import ApiKeyDep
from app.services.vi_client import create_appointment, get_patient_diagnostics

router = APIRouter()


@router.get("/vi/patient/{sukra_id}")
async def get_vi_patient(sukra_id: str, _: ApiKeyDep) -> dict:
    """Fetch patient diagnostic data from VI by sukra_id."""
    try:
        return await get_patient_diagnostics(sukra_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"VI API error: {exc}") from exc


@router.post("/vi/appointment")
async def book_vi_appointment(payload: dict, _: ApiKeyDep) -> dict:
    """Create an appointment in VI (HMAC-signed)."""
    try:
        return await create_appointment(payload)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"VI API error: {exc}") from exc
