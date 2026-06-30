"""VI (Vital Insights) routes — pull athlete diagnostic data from Sukra via VI's API."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.services import ApiKeyDep
from app.services.vi_client import create_appointment, get_patient_diagnostics

router = APIRouter()


@router.get("/vi/patient/{sukra_id}")
async def get_vi_patient(sukra_id: str, _: ApiKeyDep) -> dict:
    """Fetch an athlete's VI diagnostics (DEXA, blood panel, VO₂ max) by Sukra ID."""
    try:
        return await get_patient_diagnostics(sukra_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"VI API error: {exc}",
        ) from exc


@router.post("/vi/appointment")
async def book_vi_appointment(payload: dict, _: ApiKeyDep) -> dict:
    """Create a VI appointment via the Elixirs-compatible endpoint."""
    try:
        return await create_appointment(payload)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"VI API error: {exc}",
        ) from exc
