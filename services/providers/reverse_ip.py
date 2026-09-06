from __future__ import annotations

import httpx

from core.errors import AppError

HT_URL = "https://api.hackertarget.com/reverseiplookup/"


def is_upstream_error(text: str) -> bool:
    low = text.strip().lower()
    if not low:
        return True
    return (
        low.startswith("error")
        or "api count exceeded" in low
        or "host not found" in low
        or "not found" in low
    )


def parse_domains(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


async def reverse_ip_lookup(
    ip: str, timeout_s: float, api_key: str
) -> dict:
    params: dict[str, str] = {"q": ip}
    if api_key:
        params["key"] = api_key
    try:
        async with httpx.AsyncClient(
            timeout=timeout_s, follow_redirects=True
        ) as client:
            resp = await client.get(HT_URL, params=params)
            text = resp.text
    except httpx.HTTPError as exc:
        raise AppError("UPSTREAM_ERROR", "UPSTREAM_ERROR", status=502) from exc

    if is_upstream_error(text):
        raise AppError("UPSTREAM_ERROR", "UPSTREAM_ERROR", status=502)

    domains = parse_domains(text)
    return {
        "ip": ip,
        "domains": domains,
        "count": len(domains),
        "provider": "HackerTarget",
    }
