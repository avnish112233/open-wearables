from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, update

from app.database import DbSession
from app.models.bond import BondAthlete, BondTrainingPlan
from app.services import ApiKeyDep

router = APIRouter()


# ── Schemas ──────────────────────────────────────────────────────────────────

class AthleteCreate(BaseModel):
    name: str
    phone: str | None = None
    coach_id: str
    gym_id: str | None = None

class AthleteUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    access_granted: bool | None = None
    sukra_order_id: str | None = None
    ow_user_id: str | None = None

class PlanUpsert(BaseModel):
    athlete_id: UUID
    coach_id: str
    title: str | None = None
    status: str = "draft"
    weeks: list[dict] = []

class PlanStatusUpdate(BaseModel):
    status: str


# ── Athletes ─────────────────────────────────────────────────────────────────

@router.get("/bond/athletes")
async def list_athletes(coach_id: str, session: DbSession, _: ApiKeyDep) -> list[dict]:
    rows = await session.execute(
        select(BondAthlete).where(BondAthlete.coach_id == coach_id)
    )
    athletes = rows.scalars().all()
    return [_athlete_dict(a) for a in athletes]


@router.post("/bond/athletes", status_code=201)
async def create_athlete(body: AthleteCreate, session: DbSession, _: ApiKeyDep) -> dict:
    athlete = BondAthlete(**body.model_dump())
    session.add(athlete)
    await session.commit()
    await session.refresh(athlete)
    return _athlete_dict(athlete)


@router.get("/bond/athletes/{athlete_id}")
async def get_athlete(athlete_id: UUID, session: DbSession, _: ApiKeyDep) -> dict:
    athlete = await session.get(BondAthlete, athlete_id)
    if not athlete:
        raise HTTPException(404, "Athlete not found")
    return _athlete_dict(athlete)


@router.patch("/bond/athletes/{athlete_id}")
async def update_athlete(athlete_id: UUID, body: AthleteUpdate, session: DbSession, _: ApiKeyDep) -> dict:
    athlete = await session.get(BondAthlete, athlete_id)
    if not athlete:
        raise HTTPException(404, "Athlete not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(athlete, field, value)
    await session.commit()
    await session.refresh(athlete)
    return _athlete_dict(athlete)


# ── Plans ─────────────────────────────────────────────────────────────────────

@router.post("/bond/plans", status_code=201)
async def upsert_plan(body: PlanUpsert, session: DbSession, _: ApiKeyDep) -> dict:
    """Create or replace the draft plan for an athlete."""
    existing = await session.execute(
        select(BondTrainingPlan).where(
            BondTrainingPlan.athlete_id == body.athlete_id,
            BondTrainingPlan.status == "draft",
        )
    )
    plan = existing.scalar_one_or_none()
    if plan:
        plan.weeks = body.weeks
        plan.title = body.title
        plan.coach_id = body.coach_id
    else:
        plan = BondTrainingPlan(**body.model_dump())
        session.add(plan)
    await session.commit()
    await session.refresh(plan)
    return _plan_dict(plan)


@router.patch("/bond/plans/{plan_id}/status")
async def set_plan_status(plan_id: UUID, body: PlanStatusUpdate, session: DbSession, _: ApiKeyDep) -> dict:
    plan = await session.get(BondTrainingPlan, plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")
    plan.status = body.status
    await session.commit()
    await session.refresh(plan)
    return _plan_dict(plan)


@router.get("/bond/athletes/{athlete_id}/plan")
async def get_athlete_plan(athlete_id: UUID, session: DbSession, _: ApiKeyDep) -> dict:
    """Get the published training plan for an athlete (used by athlete app)."""
    result = await session.execute(
        select(BondTrainingPlan).where(
            BondTrainingPlan.athlete_id == athlete_id,
            BondTrainingPlan.status == "published",
        )
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(404, "No published plan")
    return _plan_dict(plan)


@router.patch("/bond/plans/{plan_id}/sessions/{week_number}/{session_index}")
async def toggle_session(
    plan_id: UUID,
    week_number: int,
    session_index: int,
    session: DbSession,
    _: ApiKeyDep,
) -> dict:
    """Toggle a session's completed state (called from athlete app)."""
    plan = await session.get(BondTrainingPlan, plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")
    weeks = list(plan.weeks)
    week = next((w for w in weeks if w.get("weekNumber") == week_number), None)
    if not week or session_index >= len(week.get("sessions", [])):
        raise HTTPException(404, "Session not found")
    week["sessions"][session_index]["completed"] = not week["sessions"][session_index].get("completed", False)
    plan.weeks = weeks
    await session.commit()
    await session.refresh(plan)
    return _plan_dict(plan)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _athlete_dict(a: BondAthlete) -> dict:
    return {
        "id": str(a.id),
        "name": a.name,
        "phone": a.phone,
        "coach_id": a.coach_id,
        "gym_id": a.gym_id,
        "access_granted": a.access_granted,
        "sukra_order_id": a.sukra_order_id,
        "ow_user_id": a.ow_user_id,
        "created_at": a.created_at.isoformat(),
    }

def _plan_dict(p: BondTrainingPlan) -> dict:
    return {
        "id": str(p.id),
        "athlete_id": str(p.athlete_id),
        "coach_id": p.coach_id,
        "title": p.title,
        "status": p.status,
        "weeks": p.weeks,
        "created_at": p.created_at.isoformat(),
    }
