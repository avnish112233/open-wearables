from uuid import UUID

from sqlalchemy.orm import Mapped

from app.database import BaseDbModel
from app.mappings import Indexed, PrimaryKey, str_100, str_255


class BondCoach(BaseDbModel):
    """Coach registered on the Bond platform."""

    id: Mapped[PrimaryKey[UUID]]
    name: Mapped[str_100]
    phone: Mapped[Indexed[str_255]]
    email: Mapped[str_255 | None]
    gym_id: Mapped[str_255 | None]
    gym_name: Mapped[str_100 | None]
