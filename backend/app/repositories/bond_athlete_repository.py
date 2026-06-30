from uuid import UUID

from sqlalchemy import select

from app.database import DbSession
from app.models.bond_athlete import BondAthlete
from app.repositories.repositories import CrudRepository
from app.schemas.bond import BondAthleteCreateInternal, BondAthleteUpdateInternal


class BondAthleteRepository(CrudRepository[BondAthlete, BondAthleteCreateInternal, BondAthleteUpdateInternal]):
    def __init__(self, model: type[BondAthlete] = BondAthlete) -> None:
        super().__init__(model)

    def get_by_coach(self, db_session: DbSession, coach_id: str) -> list[BondAthlete]:
        stmt = select(self.model).where(self.model.coach_id == coach_id).order_by(self.model.created_at.desc())
        return list(db_session.execute(stmt).scalars().all())

    def get_by_phone(self, db_session: DbSession, phone: str) -> BondAthlete | None:
        stmt = select(self.model).where(self.model.phone == phone)
        return db_session.execute(stmt).scalars().first()
