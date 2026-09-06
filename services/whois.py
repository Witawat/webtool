from __future__ import annotations

import asyncio
from datetime import datetime

from core.errors import AppError

_PRIVACY_HINTS = ("privacy", "redacted", "data redacted")


def _as_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value]
    return [str(value)]


def _fmt_date(value) -> str | None:
    if isinstance(value, (list, tuple)):
        value = value[0] if value else None
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


async def lookup_whois(domain: str, timeout_s: float) -> dict:
    def _run() -> dict:
        import whois as whois_lib

        try:
            result = whois_lib.whois(domain)
        except Exception as exc:
            raise AppError("NOT_FOUND", "NOT_FOUND", field="domain") from exc

        raw = str(getattr(result, "text", "") or "")
        status = _as_list(getattr(result, "status", None))
        nameservers = _as_list(getattr(result, "name_servers", None))
        registrar = getattr(result, "registrar", None) or None
        expires = _fmt_date(getattr(result, "expiration_date", None))
        raw_lower = raw.lower()
        tld_privacy = any(h in raw_lower for h in _PRIVACY_HINTS) and not (
            registrar and expires
        )
        return {
            "domain": domain,
            "registrar": registrar,
            "created": _fmt_date(getattr(result, "creation_date", None)),
            "updated": _fmt_date(getattr(result, "updated_date", None)),
            "expires": expires,
            "status": status,
            "nameservers": nameservers,
            "raw_text": raw,
            "tld_privacy": tld_privacy,
        }

    return await asyncio.wait_for(asyncio.to_thread(_run), timeout=timeout_s)
