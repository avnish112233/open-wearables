"""bond_athlete_and_plan_tables

Revision ID: a1b2c3d4e5f6
Revises: 5aaff4551af6

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "5aaff4551af6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bondathlete",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=100), nullable=False),
        sa.Column("coach_id", sa.String(length=255), nullable=False),
        sa.Column("gym_id", sa.String(length=255), nullable=True),
        sa.Column("access_granted", sa.Boolean(), nullable=False),
        sa.Column("sukra_order_id", sa.String(length=255), nullable=True),
        sa.Column("ow_user_id", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_bondathlete_phone", "bondathlete", ["phone"])
    op.create_index("ix_bondathlete_coach_id", "bondathlete", ["coach_id"])

    op.create_table(
        "bondplan",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("athlete_id", sa.UUID(), nullable=False),
        sa.Column("coach_id", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("weeks", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_bondplan_athlete_id", "bondplan", ["athlete_id"])


def downgrade() -> None:
    op.drop_index("ix_bondplan_athlete_id", table_name="bondplan")
    op.drop_table("bondplan")
    op.drop_index("ix_bondathlete_coach_id", table_name="bondathlete")
    op.drop_index("ix_bondathlete_phone", table_name="bondathlete")
    op.drop_table("bondathlete")
