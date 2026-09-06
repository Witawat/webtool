from __future__ import annotations

import time

import httpx

from core.errors import AppError
from core.validation import validate_url_safe

REDIRECT_STATUSES = {301, 302, 303, 307, 308}


async def fetch_url(
    method: str,
    url: str,
    headers: dict,
    body: str | None,
    follow_redirects: bool,
    timeout_s: float,
    max_body: int,
    max_redirects: int,
) -> dict:
    await validate_url_safe(url)
    started = time.perf_counter()

    async with httpx.AsyncClient(
        timeout=timeout_s, follow_redirects=False
    ) as client:
        current = url
        redirects: list[str] = []
        for _ in range(max_redirects + 1):
            try:
                resp = await client.request(
                    method, current, headers=headers or None, content=body
                )
            except httpx.HTTPError as exc:
                raise AppError("UPSTREAM_ERROR", "UPSTREAM_ERROR", status=502) from exc

            if follow_redirects and resp.status_code in REDIRECT_STATUSES:
                location = resp.headers.get("location")
                if not location:
                    break
                next_url = httpx.URL(current).join(location)
                next_str = str(next_url)
                await validate_url_safe(next_str)
                redirects.append(next_str)
                current = next_str
                continue

            content = resp.content
            size_bytes = len(content)
            truncated = size_bytes > max_body
            return {
                "method": method,
                "url": url,
                "final_url": current,
                "status": resp.status_code,
                "reason": resp.reason_phrase,
                "headers": {k: v for k, v in resp.headers.items()},
                "body": content[:max_body].decode("utf-8", errors="replace"),
                "body_truncated": truncated,
                "size_bytes": size_bytes,
                "time_ms": int((time.perf_counter() - started) * 1000),
                "redirects": redirects,
            }

    raise AppError("UPSTREAM_ERROR", "UPSTREAM_ERROR", status=502)
