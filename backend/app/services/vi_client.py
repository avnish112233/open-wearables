"""Vital Insights (VI) client — HMAC-SHA256 authenticated calls to vitaldev.vitalinsights.in.

Auth pattern mirrors the Elixirs integration: every request carries
  X-External-Signature: HMAC-SHA256(timestamp + "." + json(body))
  X-External-Timestamp: unix seconds
  X-Team-Name: bond
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any

import httpx

from app.config import settings


def _sign(timestamp: str, payload: dict[str, Any]) -> str:
    message = f"{timestamp}.{json.dumps(payload, separators=(',', ':'))}"
    return hmac.new(
        settings.vi_hmac_secret.get_secret_value().encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()


def _auth_headers(payload: dict[str, Any]) -> dict[str, str]:
    ts = str(int(time.time()))
    return {
        "Content-Type": "application/json",
        "X-External-Signature": _sign(ts, payload),
        "X-External-Timestamp": ts,
        "X-Team-Name": settings.vi_team_name,
    }


async def get_patient_diagnostics(sukra_id: str) -> dict[str, Any]:
    """Fetch an athlete's diagnostic data from VI by their Sukra patient ID.

    Endpoint path is configurable via VI_PATIENT_PATH once VI shares it.
    The payload shape mirrors the appointment API convention — VI uses the
    same HMAC auth for all endpoints.
    """
    url = f"{settings.vi_base_url}{settings.vi_patient_path}/{sukra_id}"
    payload: dict[str, Any] = {}
    async with httpx.AsyncClient(timeout=15.0) as client:
        res = await client.get(url, headers=_auth_headers(payload))
        res.raise_for_status()
        return res.json()


async def create_appointment(payload: dict[str, Any]) -> dict[str, Any]:
    """Create a VI appointment (ported from the Elixirs Node.js client)."""
    url = f"{settings.vi_base_url}{settings.vi_appointment_path}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        res = await client.post(url, json=payload, headers=_auth_headers(payload))
        res.raise_for_status()
        return res.json()
