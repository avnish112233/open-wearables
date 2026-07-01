"""Bond OTP authentication — send and verify phone OTPs via MSG91, issue JWT sessions."""

from __future__ import annotations

import logging
import random
import string
from datetime import datetime, timezone

import httpx
from jose import JWTError, jwt

from app.config import settings
from app.integrations.redis_client import get_redis_client

log = logging.getLogger(__name__)

_OTP_PREFIX = "bond:otp:"
_SESSION_PREFIX = "bond:session:"
_ALGORITHM = "HS256"


def _redis():
    return get_redis_client()


# ── OTP ───────────────────────────────────────────────────────────────────────

def _otp_key(phone: str) -> str:
    return f"{_OTP_PREFIX}{phone}"


def generate_and_store_otp(phone: str) -> str:
    otp = "".join(random.choices(string.digits, k=6))
    _redis().setex(_otp_key(phone), settings.bond_otp_ttl_seconds, otp)
    return otp


def verify_otp(phone: str, otp: str) -> bool:
    stored = _redis().get(_otp_key(phone))
    if not stored or stored != otp:
        return False
    _redis().delete(_otp_key(phone))
    return True


# ── SMS delivery (MSG91) ──────────────────────────────────────────────────────

async def send_otp_sms(phone: str, otp: str) -> None:
    """Send OTP via MSG91. Falls back to log-only if credentials are not configured."""
    if not settings.bond_msg91_auth_key or not settings.bond_msg91_template_id:
        log.warning("MSG91 not configured — OTP for %s: %s", phone, otp)
        return

    # MSG91 OTP API v5
    url = "https://control.msg91.com/api/v5/otp"
    payload = {
        "template_id": settings.bond_msg91_template_id,
        "mobile": phone.lstrip("+"),
        "authkey": settings.bond_msg91_auth_key.get_secret_value(),
        "otp": otp,
        "sender": settings.bond_msg91_sender_id,
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        res = await client.post(url, json=payload)
        if not res.is_success:
            log.error("MSG91 OTP send failed for %s: %s %s", phone, res.status_code, res.text)
            res.raise_for_status()


# ── JWT session ───────────────────────────────────────────────────────────────

def _session_key(token: str) -> str:
    return f"{_SESSION_PREFIX}{token}"


def create_session(coach_id: str) -> str:
    payload = {
        "sub": coach_id,
        "iat": int(datetime.now(timezone.utc).timestamp()),
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=_ALGORITHM)
    _redis().setex(_session_key(token), settings.bond_session_ttl_seconds, coach_id)
    return token


def verify_session(token: str) -> str | None:
    """Returns coach_id if the session is valid, else None."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[_ALGORITHM])
        coach_id = payload.get("sub")
    except JWTError:
        return None
    if not coach_id:
        return None
    # Also confirm it exists in Redis (allows server-side revocation)
    stored = _redis().get(_session_key(token))
    return stored if stored == coach_id else None


def revoke_session(token: str) -> None:
    _redis().delete(_session_key(token))
