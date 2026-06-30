from uuid import UUID

from sqlalchemy.orm import Mapped

from app.database import BaseDbModel
from app.mappings import Indexed, PrimaryKey, json_binary, str_100, str_50


class BondPlan(BaseDbModel):
    """Training plan created by a Bond coach for an athlete."""

    id: Mapped[PrimaryKey[UUID]]
    athlete_id: Mapped[Indexed[UUID]]
    coach_id: Mapped[str_100]
    title: Mapped[str_100]
    status: Mapped[str_50]
    weeks: Mapped[json_binary]
