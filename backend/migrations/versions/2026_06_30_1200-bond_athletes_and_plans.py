"""bond athletes and training plans

Revision ID: bond_a1b2c3d4e5f6
Revises: 9f0940493a9b
Create Date: 2026-06-30 12:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "bond_a1b2c3d4e5f6"
down_revision: str | None = "9f0940493a9b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "bond_athlete",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("coach_id", sa.String(100), nullable=False),
        sa.Column("gym_id", sa.String(100), nullable=True),
        sa.Column("access_granted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("sukra_order_id", sa.String(100), nullable=True),
        sa.Column("ow_user_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_bond_athlete_coach_id", "bond_athlete", ["coach_id"])

    op.create_table(
        "bond_training_plan",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("athlete_id", sa.UUID(), nullable=False),
        sa.Column("coach_id", sa.String(100), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        sa.Column("weeks", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_bond_training_plan_athlete_id", "bond_training_plan", ["athlete_id"])


def downgrade() -> None:
    op.drop_index("ix_bond_training_plan_athlete_id", table_name="bond_training_plan")
    op.drop_table("bond_training_plan")
    op.drop_index("ix_bond_athlete_coach_id", table_name="bond_athlete")
    op.drop_table("bond_athlete")
