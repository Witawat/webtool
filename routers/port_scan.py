from __future__ import annotations

import math
import time

from fastapi import APIRouter, Request

from core.config import settings
from core.errors import AppError
from core.rate_limit import get_client_ip, require_rate
from core.timeout import async_with_timeout
from core.validation import parse_ip, parse_port
from services.port import scan_ports

from . import json_ok, render, templates

router = APIRouter()


@router.get("/tools/port-scan")
async def page(request: Request):
    return render(request, templates, "tools/port-scan.html", {"slug": "port-scan"})


@router.post("/api/port-scan")
async def api_port_scan(request: Request):
    started = time.perf_counter()
    client_ip = get_client_ip(request)
    require_rate(client_ip, "port-scan", 3)
    try:
        body = await request.json()
    except Exception as exc:
        raise AppError("INVALID_INPUT", "INVALID_INPUT") from exc
    if not isinstance(body, dict):
        raise AppError("INVALID_INPUT", "INVALID_INPUT")

    ip = str(parse_ip(body.get("ip", "")))
    start = parse_port(body.get("start_port"))
    end = parse_port(body.get("end_port"))
    if end < start:
        raise AppError("INVALID_INPUT", "INVALID_INPUT", field="end_port")
    count = end - start + 1
    if count > settings.scan_max_ports:
        raise AppError("INVALID_INPUT", "INVALID_INPUT", field="end_port")

    max_parallel = settings.scan_max_parallel
    outer_timeout = (
        math.ceil(count / max_parallel) * settings.scan_port_timeout_s + 10.0
    )
    try:
        data = await async_with_timeout(
            scan_ports(ip, start, end, settings.scan_port_timeout_s, max_parallel),
            outer_timeout,
        )
    except TimeoutError as exc:
        raise AppError("TIMEOUT", "TIMEOUT", status=504) from exc
    return json_ok(data, started)
