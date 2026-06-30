from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.database import AsyncDbSession as DbSession
from app.models.bond import BondAthlete, BondReferenceConfig, BondTrainingPlan
from app.services import ApiKeyDep
from app.services import vi_client

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


# ── Reference config ─────────────────────────────────────────────────────────

@router.get("/bond/reference-config")
async def get_reference_config(session: DbSession, _: ApiKeyDep) -> dict:
    """Return the active reference ranges and quadrant scoring config.

    Read-only — updated directly in Postgres by admins, never by coaches.
    Falls back to empty dict if the seed row hasn't been inserted yet.
    """
    row = await session.scalar(
        select(BondReferenceConfig).where(BondReferenceConfig.key == "default")
    )
    return row.data if row else {}


# ── VI Profile ────────────────────────────────────────────────────────────────

@router.get("/bond/athletes/{athlete_id}/vi-profile")
async def get_athlete_vi_profile(athlete_id: UUID, session: DbSession, _: ApiKeyDep) -> dict:
    """Fetch athlete record from Bond DB and enrich with VI diagnostic data."""
    athlete = await session.scalar(select(BondAthlete).where(BondAthlete.id == athlete_id))
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    vi_data = None
    if athlete.sukra_order_id:
        try:
            raw = await vi_client.get_all_reports(athlete.sukra_order_id)
            vi_data = _parse_vi_data(raw)
        except Exception:
            vi_data = None
    return {
        "id": str(athlete.id),
        "name": athlete.name,
        "phone": athlete.phone,
        "sukra_order_id": athlete.sukra_order_id,
        "access_granted": athlete.access_granted,
        "vi": vi_data,
    }


def _parse_vi_data(raw: dict) -> dict:
    """Extract structured profile/dexa/vo2max/strength from raw VI API response."""
    appt = raw.get("appointment") or {}
    reports = raw.get("reports") or []

    dexa_r = next((r for r in reports if r.get("report_type") == "DEXA"), None)
    vo2_r  = next((r for r in reports if r.get("report_type") == "VO2MAX"), None)
    str_r  = next((r for r in reports if r.get("report_type") == "STRENGTH"), None)

    profile: dict = {}
    if appt:
        profile = {
            "name": appt.get("patient_name"),
            "age": appt.get("age"),
            "sex": appt.get("sex"),
            "dob": appt.get("dob"),
            "height_cm": appt.get("height_cm"),
            "weight_kg": appt.get("weight_kg"),
            "last_tested": appt.get("appointment_date"),
        }

    dexa: dict | None = None
    if dexa_r:
        d = dexa_r.get("data") or {}
        dexa = {
            "date": dexa_r.get("report_date"),
            "fat_pct": d.get("fat_percentage"),
            "almi": d.get("almi"),
            "ffmi": d.get("ffmi"),
            "lean_mass_g": d.get("lean_mass_g"),
            "fat_mass_g": d.get("fat_mass_g"),
            "bmc_g": d.get("bmc_g"),
            "visceral_fat_score": d.get("visceral_fat_score"),
            "arm_asymmetry_pct": d.get("arm_asymmetry_pct"),
            "leg_asymmetry_pct": d.get("leg_asymmetry_pct"),
            "arm_left_lean_g": d.get("arm_left_lean_g"),
            "arm_right_lean_g": d.get("arm_right_lean_g"),
            "leg_left_lean_g": d.get("leg_left_lean_g"),
            "leg_right_lean_g": d.get("leg_right_lean_g"),
            "body_composition_zone": d.get("body_composition_zone"),
            "zone_description": d.get("zone_description"),
            "fracture_risk": d.get("fracture_risk"),
            "t_score": d.get("t_score"),
            "z_score": d.get("z_score"),
            "ag_ratio": d.get("ag_ratio"),
            "pdf_url": dexa_r.get("pdf_url"),
            "fat_description": d.get("fat_description"),
            "fracture_description": d.get("fracture_description"),
        }

    vo2max: float | None = None
    if vo2_r:
        vo2max = (vo2_r.get("data") or {}).get("vo2max")

    strength: dict | None = None
    if str_r:
        s = str_r.get("data") or {}
        strength = {
            "imtp_kg": s.get("imtp_kg"),
            "cmj_watts_per_kg": s.get("cmj_watts_per_kg"),
            "drop_jump_rsi": s.get("drop_jump_rsi"),
            "grip_left_kg": s.get("grip_left_kg"),
            "grip_right_kg": s.get("grip_right_kg"),
        }

    return {"profile": profile, "dexa": dexa, "vo2max": vo2max, "strength": strength}
