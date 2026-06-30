"""Bond coaching platform routes — athlete and plan management."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.database import DbSession
from app.schemas.bond import (
    BondAthleteCreate,
    BondAthleteRead,
    BondAthleteUpdate,
    BondPlanCreate,
    BondPlanRead,
    BondPlanUpdate,
)
from app.services import ApiKeyDep
from app.services.bond_service import bond_athlete_service, bond_plan_service

router = APIRouter()


# ── Athletes ──────────────────────────────────────────────────────────────────

@router.get("/bond/athletes", response_model=list[BondAthleteRead])
def list_bond_athletes(coach_id: str, db: DbSession, _: ApiKeyDep) -> list[BondAthleteRead]:
    return bond_athlete_service.list_by_coach(db, coach_id)


@router.post("/bond/athletes", status_code=status.HTTP_201_CREATED, response_model=BondAthleteRead)
def create_bond_athlete(payload: BondAthleteCreate, db: DbSession, _: ApiKeyDep) -> BondAthleteRead:
    return bond_athlete_service.create(db, payload)


@router.get("/bond/athletes/{athlete_id}", response_model=BondAthleteRead)
def get_bond_athlete(athlete_id: UUID, db: DbSession, _: ApiKeyDep) -> BondAthleteRead:
    athlete = bond_athlete_service.get(db, athlete_id)
    if not athlete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found")
    return athlete


@router.patch("/bond/athletes/{athlete_id}", response_model=BondAthleteRead)
def update_bond_athlete(athlete_id: UUID, payload: BondAthleteUpdate, db: DbSession, _: ApiKeyDep) -> BondAthleteRead:
    athlete = bond_athlete_service.update_athlete(db, athlete_id, payload)
    if not athlete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Athlete not found")
    return athlete


# ── Plans ─────────────────────────────────────────────────────────────────────

@router.get("/bond/athletes/{athlete_id}/plan", response_model=BondPlanRead)
def get_athlete_plan(athlete_id: UUID, db: DbSession, _: ApiKeyDep) -> BondPlanRead:
    plan = bond_plan_service.get_latest_for_athlete(db, athlete_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No plan found for athlete")
    return plan


@router.post("/bond/plans", status_code=status.HTTP_201_CREATED, response_model=BondPlanRead)
def create_bond_plan(payload: BondPlanCreate, db: DbSession, _: ApiKeyDep) -> BondPlanRead:
    return bond_plan_service.create(db, payload)


@router.patch("/bond/plans/{plan_id}/status", response_model=BondPlanRead)
def set_plan_status(plan_id: UUID, payload: BondPlanUpdate, db: DbSession, _: ApiKeyDep) -> BondPlanRead:
    plan = bond_plan_service.update_plan(db, plan_id, payload)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return plan


@router.patch("/bond/plans/{plan_id}/sessions/{week_number}/{session_index}", response_model=BondPlanRead)
def toggle_plan_session(
    plan_id: UUID, week_number: int, session_index: int, db: DbSession, _: ApiKeyDep
) -> BondPlanRead:
    plan = bond_plan_service.toggle_session(db, plan_id, week_number, session_index)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return plan
