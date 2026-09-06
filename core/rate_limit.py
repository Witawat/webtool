from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import Request

from .config import settings


class RateLimiter:
    """In-memory sliding window rate limiter (per ip + key)."""

    def __init__(self) -> None:
        self._hits: dict[tuple[str, str], deque[float]] = defaultdict(deque)

    def allow(self, ip: str, key: str, limit_per_min: int) -> bool:
        now = time.monotonic()
        dq = self._hits[(ip, key)]
        while dq and now - dq[0] > 60.0:
            dq.popleft()
        if len(dq) >= limit_per_min:
            return False
        dq.append(now)
        return True


rate_limiter = RateLimiter()


def get_client_ip(request: Request) -> str:
    if settings.trust_proxy:
        fwd = request.headers.get("x-forwarded-for")
        if fwd:
            return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def require_rate(ip: str, key: str, limit_per_min: int) -> None:
    from .errors import AppError

    if not rate_limiter.allow(ip, key, limit_per_min):
        raise AppError("RATE_LIMITED", "RATE_LIMITED", status=429)
