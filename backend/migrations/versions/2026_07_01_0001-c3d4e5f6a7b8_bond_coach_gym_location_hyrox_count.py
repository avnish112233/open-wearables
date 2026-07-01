"""Add gym_location and hyrox_athlete_count to bondcoach.

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-07-01 00:01:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("bondcoach", sa.Column("gym_location", sa.String(length=255), nullable=True))
    op.add_column("bondcoach", sa.Column("hyrox_athlete_count", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("bondcoach", "hyrox_athlete_count")
    op.drop_column("bondcoach", "gym_location")
