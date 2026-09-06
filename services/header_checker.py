from __future__ import annotations

import httpx

from core.errors import AppError
from core.validation import validate_url_safe

SECURITY_HEADERS = (
    "strict-transport-security",
    "content-security-policy",
    "x-frame-options",
    "x-content-type-options",
    "referrer-policy",
    "permissions-policy",
)


async def check_headers(url: str, timeout_s: float) -> dict:
    await validate_url_safe(url)
    try:
        async with httpx.AsyncClient(
            timeout=timeout_s, follow_redirects=True, max_redirects=5
        ) as client:
            resp = await client.get(
                url, headers={"User-Agent": "WebTool/0.1"}
            )
    except httpx.HTTPError as exc:
        raise AppError("UPSTREAM_ERROR", "UPSTREAM_ERROR", status=502) from exc

    lower = {k.lower(): v for k, v in resp.headers.items()}
    security = {
        "hsts": {
            "present": "strict-transport-security" in lower,
            "value": lower.get("strict-transport-security"),
        },
        "csp": {"present": "content-security-policy" in lower},
        "x_frame_options": lower.get("x-frame-options"),
        "x_content_type_options": lower.get("x-content-type-options"),
        "referrer_policy": lower.get("referrer-policy"),
        "permissions_policy": lower.get("permissions-policy"),
    }
    score = sum(
        [
            security["hsts"]["present"],
            security["csp"]["present"],
            bool(security["x_frame_options"]),
            bool(security["x_content_type_options"]),
            bool(security["referrer_policy"]),
            bool(security["permissions_policy"]),
        ]
    )
    return {
        "url": url,
        "status": resp.status_code,
        "headers": {k: v for k, v in resp.headers.items()},
        "security": security,
        "score": score,
    }
