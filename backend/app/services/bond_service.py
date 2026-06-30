from __future__ import annotations

from logging import getLogger
from uuid import UUID

from app.database import DbSession
from app.models.bond_athlete import BondAthlete
from app.models.bond_plan import BondPlan
from app.repositories.bond_athlete_repository import BondAthleteRepository
from app.repositories.bond_plan_repository import BondPlanRepository
from app.schemas.bond import (
    BondAthleteCreate,
    BondAthleteCreateInternal,
    BondAthleteUpdate,
    BondAthleteUpdateInternal,
    BondPlanCreate,
    BondPlanCreateInternal,
    BondPlanUpdate,
    BondPlanUpdateInternal,
)
from app.services.services import AppService

log = getLogger(__name__)


class BondAthleteService(AppService[BondAthleteRepository, BondAthlete, BondAthleteCreateInternal, BondAthleteUpdateInternal]):
    def __init__(self) -> None:
        super().__init__(crud_model=BondAthleteRepository, model=BondAthlete, log=log)
        self.crud: BondAthleteRepository

    def create(self, db_session: DbSession, creator: BondAthleteCreate) -> BondAthlete:
        internal = BondAthleteCreateInternal(**creator.model_dump())
        return super().create(db_session, internal)

    def update_athlete(
        self, db_session: DbSession, athlete_id: UUID, updater: BondAthleteUpdate
    ) -> BondAthlete | None:
        athlete = self.get(db_session, athlete_id)
        if not athlete:
            return None
        internal = BondAthleteUpdateInternal(**updater.model_dump(exclude_unset=True))
        return self.crud.update(db_session, athlete, internal)

    def list_by_coach(self, db_session: DbSession, coach_id: str) -> list[BondAthlete]:
        return self.crud.get_by_coach(db_session, coach_id)


class BondPlanService(AppService[BondPlanRepository, BondPlan, BondPlanCreateInternal, BondPlanUpdateInternal]):
    def __init__(self) -> None:
        super().__init__(crud_model=BondPlanRepository, model=BondPlan, log=log)
        self.crud: BondPlanRepository

    def create(self, db_session: DbSession, creator: BondPlanCreate) -> BondPlan:
        internal = BondPlanCreateInternal(**creator.model_dump())
        return super().create(db_session, internal)

    def update_plan(
        self, db_session: DbSession, plan_id: UUID, updater: BondPlanUpdate
    ) -> BondPlan | None:
        plan = self.get(db_session, plan_id)
        if not plan:
            return None
        internal = BondPlanUpdateInternal(**updater.model_dump(exclude_unset=True))
        return self.crud.update(db_session, plan, internal)

    def get_latest_for_athlete(self, db_session: DbSession, athlete_id: UUID) -> BondPlan | None:
        return self.crud.get_latest_for_athlete(db_session, athlete_id)

    def toggle_session(
        self, db_session: DbSession, plan_id: UUID, week_number: int, session_index: int
    ) -> BondPlan | None:
        plan = self.get(db_session, plan_id)
        if not plan:
            return None
        weeks = [dict(w) for w in (plan.weeks or [])]
        for week in weeks:
            if week.get("weekNumber") == week_number:
                sessions = list(week.get("sessions", []))
                if 0 <= session_index < len(sessions):
                    session = dict(sessions[session_index])
                    session["completed"] = not session.get("completed", False)
                    sessions[session_index] = session
                week["sessions"] = sessions
        internal = BondPlanUpdateInternal(weeks=weeks)
        return self.crud.update(db_session, plan, internal)


bond_athlete_service = BondAthleteService()
bond_plan_service = BondPlanService()
