from __future__ import annotations

import time

from fastapi import APIRouter, Request

from core.config import settings
from core.errors import AppError
from core.rate_limit import get_client_ip, require_rate
from core.timeout import async_with_timeout
from core.validation import parse_host, parse_port
from services.traceroute import traceroute_host

from . import json_ok, render, templates

router = APIRouter()

MIN_HOPS = 3
MAX_HOPS = 30


@router.get("/tools/traceroute")
async def page(request: Request):
    return render(
        request,
        templates,
        "tools/traceroute.html",
        {"slug": "traceroute", "default_hops": settings.trace_max_hops},
    )


@router.post("/api/traceroute")
async def api_traceroute(request: Request):
    started = time.perf_counter()
    client_ip = get_client_ip(request)
    require_rate(client_ip, "traceroute", 3)
    try:
        body = await request.json()
    except Exception as exc:
        raise AppError("INVALID_INPUT", "INVALID_INPUT") from exc
    if not isinstance(body, dict):
        raise AppError("INVALID_INPUT", "INVALID_INPUT")

    host = parse_host(body.get("host", ""))
    max_hops = settings.trace_max_hops
    raw_hops = body.get("max_hops")
    if raw_hops is not None:
        max_hops = parse_port(str(raw_hops))
        if not MIN_HOPS <= max_hops <= MAX_HOPS:
            raise AppError("INVALID_INPUT", "INVALID_INPUT", field="max_hops")

    try:
        data = await async_with_timeout(
            traceroute_host(host, max_hops, settings.trace_hop_timeout_s),
            max_hops * settings.trace_hop_timeout_s + 35.0,
        )
    except TimeoutError as exc:
        raise AppError("TIMEOUT", "TIMEOUT", status=504) from exc
    return json_ok(data, started)
