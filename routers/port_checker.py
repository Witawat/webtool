from __future__ import annotations

import time

from fastapi import APIRouter, Request

from core.config import settings
from core.errors import AppError
from core.rate_limit import get_client_ip, require_rate
from core.timeout import async_with_timeout
from core.validation import parse_host, parse_port
from services.port import check_port

from . import json_ok, render, templates

router = APIRouter()

COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 6379, 8080]


@router.get("/tools/port-checker")
async def page(request: Request):
    return render(
        request,
        templates,
        "tools/port-checker.html",
        {"slug": "port-checker", "common_ports": COMMON_PORTS},
    )


@router.post("/api/port-checker")
async def api_port_checker(request: Request):
    started = time.perf_counter()
    client_ip = get_client_ip(request)
    require_rate(client_ip, "port-checker", 10)
    try:
        body = await request.json()
    except Exception as exc:
        raise AppError("INVALID_INPUT", "INVALID_INPUT") from exc
    if not isinstance(body, dict):
        raise AppError("INVALID_INPUT", "INVALID_INPUT")
    host = parse_host(body.get("host", ""))
    port = parse_port(body.get("port"))
    try:
        data = await async_with_timeout(
            check_port(host, port, settings.port_timeout_s),
            settings.port_timeout_s + 5.0,
        )
    except TimeoutError as exc:
        raise AppError("TIMEOUT", "TIMEOUT", status=504) from exc
    return json_ok(data, started)
