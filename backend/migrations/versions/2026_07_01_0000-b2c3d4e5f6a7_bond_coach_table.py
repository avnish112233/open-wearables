"""bond_coach_table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bondcoach",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("gym_id", sa.String(length=255), nullable=True),
        sa.Column("gym_name", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_bondcoach_phone", "bondcoach", ["phone"])


def downgrade() -> None:
    op.drop_index("ix_bondcoach_phone", table_name="bondcoach")
    op.drop_table("bondcoach")
