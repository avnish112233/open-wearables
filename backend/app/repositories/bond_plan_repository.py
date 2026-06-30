from uuid import UUID

from sqlalchemy import select

from app.database import DbSession
from app.models.bond_plan import BondPlan
from app.repositories.repositories import CrudRepository
from app.schemas.bond import BondPlanCreateInternal, BondPlanUpdateInternal


class BondPlanRepository(CrudRepository[BondPlan, BondPlanCreateInternal, BondPlanUpdateInternal]):
    def __init__(self, model: type[BondPlan] = BondPlan) -> None:
        super().__init__(model)

    def get_latest_for_athlete(self, db_session: DbSession, athlete_id: UUID) -> BondPlan | None:
        """Return the latest published plan, falling back to the latest draft."""
        for status in ("published", "draft"):
            stmt = (
                select(self.model)
                .where(self.model.athlete_id == athlete_id, self.model.status == status)
                .order_by(self.model.created_at.desc())
                .limit(1)
            )
            plan = db_session.execute(stmt).scalars().first()
            if plan:
                return plan
        return None
