from uuid import UUID

from sqlalchemy.orm import Mapped

from app.database import BaseDbModel
from app.mappings import Indexed, PrimaryKey, str_100, str_255


class BondAthlete(BaseDbModel):
    """Athlete record managed by Bond coaching platform."""

    id: Mapped[PrimaryKey[UUID]]
    name: Mapped[str_100]
    phone: Mapped[Indexed[str_100]]
    coach_id: Mapped[Indexed[str_255]]
    gym_id: Mapped[str_255 | None]
    access_granted: Mapped[bool]
    sukra_order_id: Mapped[str_255 | None]
    ow_user_id: Mapped[str_255 | None]
