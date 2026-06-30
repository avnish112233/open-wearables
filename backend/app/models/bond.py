from typing import Annotated
from uuid import UUID, uuid4

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import BaseDbModel
from app.mappings import Indexed, PrimaryKey, str_100, str_255

str_50 = Annotated[str, mapped_column(String(50))]


class BondAthlete(BaseDbModel):
    """Athlete profile managed by a Bond coach."""

    __tablename__ = "bond_athlete"

    id: Mapped[PrimaryKey[UUID]] = mapped_column(default=uuid4)
    name: Mapped[str_100]
    phone: Mapped[str_50 | None]
    coach_id: Mapped[Indexed[str_100]]
    gym_id: Mapped[str_100 | None]
    access_granted: Mapped[bool] = mapped_column(Boolean, default=False)
    sukra_order_id: Mapped[str_100 | None]
    ow_user_id: Mapped[str_255 | None]


class BondTrainingPlan(BaseDbModel):
    """Weekly training plan prescribed by a Bond coach for an athlete."""

    __tablename__ = "bond_training_plan"

    id: Mapped[PrimaryKey[UUID]] = mapped_column(default=uuid4)
    athlete_id: Mapped[Indexed[UUID]]
    coach_id: Mapped[str_100]
    status: Mapped[str_50] = mapped_column(String(50), default="draft")
    weeks: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    title: Mapped[str_255 | None]


class BondReferenceConfig(BaseDbModel):
    """Named JSONB blobs for VO2/DEXA reference ranges and quadrant scoring config.

    Rows are keyed by `key`; only one row with key='default' is used by the app.
    Update via psql or the Railway console — coaches have no write access.
    """

    __tablename__ = "bond_reference_config"

    key: Mapped[str_100] = mapped_column(String(100), primary_key=True)
    data: Mapped[dict] = mapped_column(JSONB, default=dict)
