"""Bond coach authentication — phone + OTP → JWT session."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.database import DbSession
from app.repositories.bond_coach_repository import BondCoachRepository
from app.schemas.bond import BondCoachCreate, BondCoachRead, OtpRequest, OtpVerify, SessionResponse
from app.services.bond_service import bond_coach_service
from app.services.bond_otp_service import (
    create_session,
    generate_and_store_otp,
    revoke_session,
    send_otp_sms,
    verify_otp,
    verify_session,
)

router = APIRouter(prefix="/bond/auth")

_bearer = HTTPBearer(auto_error=False)
_coach_repo = BondCoachRepository()


def _get_bond_coach_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)] = None,
) -> str:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bond session token required")
    coach_id = verify_session(credentials.credentials)
    if not coach_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")
    return coach_id


BondCoachIdDep = Annotated[str, Depends(_get_bond_coach_id)]


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=BondCoachRead)
def register_coach(payload: BondCoachCreate, db: DbSession) -> BondCoachRead:
    """Self-service coach registration — creates the coach record and returns it."""
    existing = _coach_repo.get_by_phone(db, payload.phone)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A coach with this phone number is already registered.",
        )
    coach = bond_coach_service.create(db, payload)
    return BondCoachRead.model_validate(coach)


@router.post("/request-otp", status_code=status.HTTP_200_OK)
async def request_otp(payload: OtpRequest, db: DbSession) -> dict:
    """Send a 6-digit OTP to the coach's registered phone number."""
    coach = _coach_repo.get_by_phone(db, payload.phone)
    if not coach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phone number not registered. Contact your admin to be added.",
        )
    otp = generate_and_store_otp(payload.phone)
    await send_otp_sms(payload.phone, otp)
    return {"message": "OTP sent", "phone": payload.phone}


@router.post("/verify-otp", response_model=SessionResponse)
def verify_otp_and_login(payload: OtpVerify, db: DbSession) -> SessionResponse:
    """Verify OTP and return a 30-day session token."""
    if not verify_otp(payload.phone, payload.otp):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired OTP")
    coach = _coach_repo.get_by_phone(db, payload.phone)
    if not coach:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coach not found")
    token = create_session(str(coach.id))
    return SessionResponse(token=token, coach=BondCoachRead.model_validate(coach))


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)] = None) -> dict:
    if credentials:
        revoke_session(credentials.credentials)
    return {"message": "Logged out"}


@router.get("/me", response_model=BondCoachRead)
def me(coach_id: BondCoachIdDep, db: DbSession) -> BondCoachRead:
    coach = _coach_repo.get(db, coach_id)
    if not coach:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coach not found")
    return BondCoachRead.model_validate(coach)
