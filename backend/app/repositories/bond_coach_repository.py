from sqlalchemy import select

from app.database import DbSession
from app.models.bond_coach import BondCoach
from app.repositories.repositories import CrudRepository
from app.schemas.bond import BondCoachCreateInternal, BondCoachUpdate


class BondCoachRepository(CrudRepository[BondCoach, BondCoachCreateInternal, BondCoachUpdate]):
    def __init__(self, model: type[BondCoach] = BondCoach) -> None:
        super().__init__(model)

    def get_by_phone(self, db_session: DbSession, phone: str) -> BondCoach | None:
        stmt = select(self.model).where(self.model.phone == phone)
        return db_session.execute(stmt).scalars().first()
