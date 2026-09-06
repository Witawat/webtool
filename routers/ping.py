from __future__ import annotations

import time

from fastapi import APIRouter, Request

from core.config import settings
from core.errors import AppError
from core.rate_limit import get_client_ip, require_rate
from core.timeout import async_with_timeout
from core.validation import parse_host, parse_port
from services.ping import ping_host

from . import json_ok, render, templates

router = APIRouter()

MAX_PING_COUNT = 10


@router.get("/tools/ping")
async def page(request: Request):
    return render(
        request,
        templates,
        "tools/ping.html",
        {"slug": "ping", "default_count": settings.ping_count},
    )


@router.post("/api/ping")
async def api_ping(request: Request):
    started = time.perf_counter()
    client_ip = get_client_ip(request)
    require_rate(client_ip, "ping", 10)
    try:
        body = await request.json()
    except Exception as exc:
        raise AppError("INVALID_INPUT", "INVALID_INPUT") from exc
    if not isinstance(body, dict):
        raise AppError("INVALID_INPUT", "INVALID_INPUT")

    host = parse_host(body.get("host", ""))
    count = settings.ping_count
    raw_count = body.get("count")
    if raw_count is not None:
        count = parse_port(str(raw_count))
        if count > MAX_PING_COUNT:
            raise AppError("INVALID_INPUT", "INVALID_INPUT", field="count")

    try:
        data = await async_with_timeout(
            ping_host(host, count, settings.ping_timeout_s),
            count * settings.ping_timeout_s + 15.0,
        )
    except TimeoutError as exc:
        raise AppError("TIMEOUT", "TIMEOUT", status=504) from exc
    return json_ok(data, started)
