from __future__ import annotations

from core.config import settings
from core.errors import AppError


async def reverse_email_lookup(email: str, timeout_s: float) -> dict:
    if not settings.email_api_key:
        raise AppError("TOOL_DISABLED", "TOOL_DISABLED", status=503)
    return {
        "email": email,
        "provider": "Email provider API",
        "available": True,
        "result": None,
    }
