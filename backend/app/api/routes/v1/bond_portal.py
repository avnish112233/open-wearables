"""Public athlete portal — no auth, accessed via secret UUID link."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.database import DbSession
from app.repositories.bond_athlete_repository import BondAthleteRepository
from app.repositories.bond_coach_repository import BondCoachRepository
from app.schemas.bond import BondAthleteUpdate

router = APIRouter(prefix="/bond/portal")

_athlete_repo = BondAthleteRepository()
_coach_repo = BondCoachRepository()


class AthletePortalRead(BaseModel):
    id: UUID
    name: str
    phone: str
    access_granted: bool
    ow_user_id: str | None = None
    coach_name: str | None = None
    gym_name: str | None = None


class ConsentPayload(BaseModel):
    granted: bool = True


class OwUserPayload(BaseModel):
    ow_user_id: str


@router.get("/{athlete_id}", response_model=AthletePortalRead)
def get_athlete_portal(athlete_id: UUID, db: DbSession) -> AthletePortalRead:
    """Public lookup — returns minimal athlete + coach info for the consent/home page."""
    athlete = _athlete_repo.get(db, athlete_id)
    if not athlete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found")

    try:
        coach = _coach_repo.get(db, UUID(athlete.coach_id)) if athlete.coach_id else None
    except (ValueError, AttributeError):
        coach = None

    return AthletePortalRead(
        id=athlete.id,
        name=athlete.name,
        phone=athlete.phone,
        access_granted=athlete.access_granted,
        ow_user_id=athlete.ow_user_id,
        coach_name=coach.name if coach else None,
        gym_name=coach.gym_name if coach else None,
    )


@router.post("/{athlete_id}/consent", status_code=status.HTTP_200_OK)
def grant_consent(athlete_id: UUID, payload: ConsentPayload, db: DbSession) -> dict:
    """Athlete grants (or revokes) coach access to their data."""
    athlete = _athlete_repo.get(db, athlete_id)
    if not athlete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found")
    _athlete_repo.update(db, athlete, BondAthleteUpdate(access_granted=payload.granted))
    return {"access_granted": payload.granted}


@router.patch("/{athlete_id}/ow-user", status_code=status.HTTP_200_OK)
def set_ow_user(athlete_id: UUID, payload: OwUserPayload, db: DbSession) -> dict:
    """Save the Open Wearables user ID so it persists across devices."""
    athlete = _athlete_repo.get(db, athlete_id)
    if not athlete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found")
    _athlete_repo.update(db, athlete, BondAthleteUpdate(ow_user_id=payload.ow_user_id))
    return {"ow_user_id": payload.ow_user_id}
