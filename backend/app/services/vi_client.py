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


def _read_headers() -> dict[str, str]:
    """Headers for VI read endpoints — simple API key auth."""
    if settings.vi_api_key is None:
        raise RuntimeError("VI_API_KEY is not configured")
    key = settings.vi_api_key.get_secret_value()
    return {
        "Content-Type": "application/json",
        "X-API-Key": key,
        "Authorization": f"Bearer {key}",
    }


async def get_patient_diagnostics(sukra_id: str) -> dict[str, Any]:
    """Fetch an athlete's diagnostic data from VI by their Sukra patient ID.

    Uses the read-only VI_API_KEY (not HMAC) — VI uses separate auth for reads vs writes.
    """
    url = f"{settings.vi_base_url}{settings.vi_patient_path}/{sukra_id}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        res = await client.get(url, headers=_read_headers())
        res.raise_for_status()
        return res.json()


async def create_appointment(payload: dict[str, Any]) -> dict[str, Any]:
    """Create a VI appointment (ported from the Elixirs Node.js client)."""
    url = f"{settings.vi_base_url}{settings.vi_appointment_path}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        res = await client.post(url, json=payload, headers=_auth_headers(payload))
        res.raise_for_status()
        return res.json()
