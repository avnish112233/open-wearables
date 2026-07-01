from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


# ── Coach ─────────────────────────────────────────────────────────────────────

class BondCoachCreate(BaseModel):
    name: str = Field(..., max_length=100)
    phone: str = Field(..., max_length=255)
    email: str | None = Field(None, max_length=255)
    gym_id: str | None = Field(None, max_length=255)
    gym_name: str | None = Field(None, max_length=100)


class BondCoachCreateInternal(BondCoachCreate):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BondCoachUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    email: str | None = Field(None, max_length=255)
    gym_id: str | None = None
    gym_name: str | None = Field(None, max_length=100)


class BondCoachRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    phone: str
    email: str | None = None
    gym_id: str | None = None
    gym_name: str | None = None
    created_at: datetime


# ── Auth ──────────────────────────────────────────────────────────────────────

class OtpRequest(BaseModel):
    phone: str = Field(..., description="E.164 format e.g. +919876543210")


class OtpVerify(BaseModel):
    phone: str
    otp: str = Field(..., min_length=6, max_length=6)


class SessionResponse(BaseModel):
    token: str
    coach: BondCoachRead


# ── Athlete ───────────────────────────────────────────────────────────────────

class BondAthleteCreate(BaseModel):
    name: str = Field(..., max_length=100)
    phone: str = Field(..., max_length=100)
    coach_id: str = Field(..., max_length=255)
    gym_id: str | None = Field(None, max_length=255)


class BondAthleteCreateInternal(BondAthleteCreate):
    id: UUID = Field(default_factory=uuid4)
    access_granted: bool = False
    sukra_order_id: str | None = None
    ow_user_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BondAthleteUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    access_granted: bool | None = None
    sukra_order_id: str | None = None
    ow_user_id: str | None = None
    gym_id: str | None = None


class BondAthleteUpdateInternal(BondAthleteUpdate):
    pass


class BondAthleteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    phone: str
    coach_id: str
    gym_id: str | None = None
    access_granted: bool
    sukra_order_id: str | None = None
    ow_user_id: str | None = None
    created_at: datetime


# ── Plan ─────────────────────────────────────────────────────────────────────

class BondPlanCreate(BaseModel):
    athlete_id: UUID
    coach_id: str = Field(..., max_length=100)
    title: str = Field("", max_length=100)
    status: str = Field("draft", max_length=50)
    weeks: list[dict[str, Any]] = Field(default_factory=list)


class BondPlanCreateInternal(BondPlanCreate):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BondPlanUpdate(BaseModel):
    title: str | None = Field(None, max_length=100)
    status: str | None = Field(None, max_length=50)
    weeks: list[dict[str, Any]] | None = None


class BondPlanUpdateInternal(BondPlanUpdate):
    pass


class BondPlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    athlete_id: UUID
    coach_id: str
    title: str
    status: str
    weeks: list[dict[str, Any]]
    created_at: datetime
