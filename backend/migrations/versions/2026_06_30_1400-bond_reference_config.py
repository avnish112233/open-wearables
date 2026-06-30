"""bond reference config table with seed data

Revision ID: bond_ref_cfg_001
Revises: bond_a1b2c3d4e5f6
Create Date: 2026-06-30 14:00:00
"""
import json

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "bond_ref_cfg_001"
down_revision = "bond_a1b2c3d4e5f6"
branch_labels = None
depends_on = None

# ─── Seed data ────────────────────────────────────────────────────────────────
# camelCase keys match the TypeScript types in the frontend exactly.
# To update ranges: UPDATE bond_reference_config SET data = '<json>'::jsonb WHERE key = 'default';

_SEED = {
    # VO2 max percentile anchors (p20/40/60/80) — HYROX athletic population
    "vo2Refs": [
        {"minAge": 18, "maxAge": 29, "sex": "male",   "p20": 38, "p40": 44, "p60": 50, "p80": 58},
        {"minAge": 30, "maxAge": 39, "sex": "male",   "p20": 36, "p40": 42, "p60": 48, "p80": 55},
        {"minAge": 40, "maxAge": 49, "sex": "male",   "p20": 33, "p40": 38, "p60": 44, "p80": 52},
        {"minAge": 50, "maxAge": 59, "sex": "male",   "p20": 29, "p40": 34, "p60": 40, "p80": 47},
        {"minAge": 60, "maxAge": 69, "sex": "male",   "p20": 25, "p40": 30, "p60": 35, "p80": 42},
        {"minAge": 18, "maxAge": 29, "sex": "female", "p20": 33, "p40": 38, "p60": 43, "p80": 50},
        {"minAge": 30, "maxAge": 39, "sex": "female", "p20": 30, "p40": 35, "p60": 40, "p80": 46},
        {"minAge": 40, "maxAge": 49, "sex": "female", "p20": 27, "p40": 32, "p60": 37, "p80": 43},
        {"minAge": 50, "maxAge": 59, "sex": "female", "p20": 24, "p40": 28, "p60": 33, "p80": 39},
        {"minAge": 60, "maxAge": 69, "sex": "female", "p20": 20, "p40": 24, "p60": 29, "p80": 35},
    ],
    # DEXA — body fat % windows — ISSN position stand calibrated for HYROX
    "fatPctRefs": [
        {"minAge": 18, "maxAge": 29, "sex": "male",   "optimalLow": 6,  "optimalHigh": 13, "normalLow": 4,  "normalHigh": 18},
        {"minAge": 30, "maxAge": 39, "sex": "male",   "optimalLow": 7,  "optimalHigh": 14, "normalLow": 5,  "normalHigh": 19},
        {"minAge": 40, "maxAge": 49, "sex": "male",   "optimalLow": 8,  "optimalHigh": 15, "normalLow": 6,  "normalHigh": 20},
        {"minAge": 50, "maxAge": 59, "sex": "male",   "optimalLow": 9,  "optimalHigh": 17, "normalLow": 7,  "normalHigh": 22},
        {"minAge": 60, "maxAge": 69, "sex": "male",   "optimalLow": 10, "optimalHigh": 19, "normalLow": 8,  "normalHigh": 24},
        {"minAge": 18, "maxAge": 29, "sex": "female", "optimalLow": 14, "optimalHigh": 22, "normalLow": 10, "normalHigh": 28},
        {"minAge": 30, "maxAge": 39, "sex": "female", "optimalLow": 15, "optimalHigh": 23, "normalLow": 11, "normalHigh": 29},
        {"minAge": 40, "maxAge": 49, "sex": "female", "optimalLow": 16, "optimalHigh": 25, "normalLow": 12, "normalHigh": 30},
        {"minAge": 50, "maxAge": 59, "sex": "female", "optimalLow": 18, "optimalHigh": 27, "normalLow": 14, "normalHigh": 32},
        {"minAge": 60, "maxAge": 69, "sex": "female", "optimalLow": 19, "optimalHigh": 29, "normalLow": 15, "normalHigh": 34},
    ],
    # DEXA — ALMI (kg/m²) — ESPEN consensus + NHANES, calibrated for strength-endurance
    "almiRefs": [
        {"minAge": 18, "maxAge": 29, "sex": "male",   "optimalLow": 8.7, "optimalHigh": 10.8, "normalLow": 7.5, "normalHigh": 11.5},
        {"minAge": 30, "maxAge": 39, "sex": "male",   "optimalLow": 8.5, "optimalHigh": 10.5, "normalLow": 7.3, "normalHigh": 11.2},
        {"minAge": 40, "maxAge": 49, "sex": "male",   "optimalLow": 8.3, "optimalHigh": 10.3, "normalLow": 7.0, "normalHigh": 11.0},
        {"minAge": 50, "maxAge": 59, "sex": "male",   "optimalLow": 8.0, "optimalHigh": 10.0, "normalLow": 6.8, "normalHigh": 10.8},
        {"minAge": 60, "maxAge": 69, "sex": "male",   "optimalLow": 7.5, "optimalHigh": 9.5,  "normalLow": 6.5, "normalHigh": 10.5},
        {"minAge": 18, "maxAge": 29, "sex": "female", "optimalLow": 6.0, "optimalHigh": 7.8, "normalLow": 5.4, "normalHigh": 8.5},
        {"minAge": 30, "maxAge": 39, "sex": "female", "optimalLow": 5.9, "optimalHigh": 7.7, "normalLow": 5.3, "normalHigh": 8.3},
        {"minAge": 40, "maxAge": 49, "sex": "female", "optimalLow": 5.7, "optimalHigh": 7.5, "normalLow": 5.1, "normalHigh": 8.1},
        {"minAge": 50, "maxAge": 59, "sex": "female", "optimalLow": 5.5, "optimalHigh": 7.3, "normalLow": 4.9, "normalHigh": 7.9},
        {"minAge": 60, "maxAge": 69, "sex": "female", "optimalLow": 5.2, "optimalHigh": 7.0, "normalLow": 4.6, "normalHigh": 7.6},
    ],
    # 2×2 matrix algorithm config
    "quadrant": {
        # Y-axis weighting: how much each pillar contributes to overall capacity
        "weights": {
            "aerobic":        0.40,
            "strength":       0.45,
            "bodyComp":       0.15,
            "asymPenalty":    0.04,   # deducted per suboptimal asymmetry flag
            "eliteThreshold": 0.50,   # y >= this → "Elite" quadrant
        },
        # Population anchors for neuromuscular tests (HYROX age-group calibrated)
        "strengthAnchors": {
            "imtpBW": {"p20": 1.55, "p40": 1.85, "p60": 2.20, "p80": 2.60},
            "cmj":    {"p20": 30,   "p40": 38,   "p60": 45,   "p80": 54},
            "rsi":    {"p20": 0.35, "p40": 0.50, "p60": 0.70, "p80": 1.00},
        },
        # How IMTP, CMJ, RSI are combined into strengthScore
        "strengthWeights": {
            "imtp": 0.45,
            "cmj":  0.35,
            "rsi":  0.20,
        },
    },
}


def upgrade() -> None:
    op.create_table(
        "bond_reference_config",
        sa.Column("key", sa.String(100), primary_key=True, nullable=False),
        sa.Column("data", JSONB(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Seed the default config row
    op.execute(
        sa.text(
            "INSERT INTO bond_reference_config (key, data) VALUES (:key, :data::jsonb)"
        ).bindparams(key="default", data=json.dumps(_SEED))
    )


def downgrade() -> None:
    op.drop_table("bond_reference_config")
