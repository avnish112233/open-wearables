"""
Vital Insights (VI) API client.

Read endpoints (patient diagnostics) use the VI_API_KEY header.
Write endpoints (appointment booking) use HMAC-SHA256 signing, matching
the Elixirs integration pattern documented in HANDOFF.md.
"""

import hashlib
import hmac
import json
import time
from typing import Any

import httpx

from app.config import settings


def _sign(timestamp: str, payload: dict[str, Any]) -> str:
    secret = settings.vi_hmac_secret.get_secret_value()
    message = f"{timestamp}.{json.dumps(payload, separators=(',', ':'))}"
    return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()


def _hmac_headers(payload: dict[str, Any]) -> dict[str, str]:
    ts = str(int(time.time()))
    return {
        "X-External-Signature": _sign(ts, payload),
        "X-External-Timestamp": ts,
        "X-Team-Name": settings.vi_team_name,
        "Content-Type": "application/json",
    }


def _read_headers() -> dict[str, str]:
    return {
        "x-api-key": settings.vi_api_key.get_secret_value(),
        "Content-Type": "application/json",
    }


async def get_all_reports(sukra_order_id: str) -> dict[str, Any]:
    """Fetch appointment + all diagnostic reports for a sukra_order_id."""
    url = f"{settings.vi_base_url}{settings.vi_patient_path}/{sukra_order_id}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        res = await client.get(url, headers=_read_headers())
        res.raise_for_status()
        return res.json()


async def create_appointment(payload: dict[str, Any]) -> dict[str, Any]:
    url = f"{settings.vi_base_url}{settings.vi_appointment_path}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        res = await client.post(url, json=payload, headers=_hmac_headers(payload))
        res.raise_for_status()
        return res.json()
