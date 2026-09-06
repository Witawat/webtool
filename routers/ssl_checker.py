from __future__ import annotations

import time

from fastapi import APIRouter, Request

from core.config import settings
from core.errors import AppError
from core.rate_limit import get_client_ip, require_rate
from core.timeout import async_with_timeout
from core.validation import parse_host, parse_port
from services.ssl_checker import check_ssl

from . import json_ok, render, templates

router = APIRouter()


@router.get("/tools/ssl")
async def page(request: Request):
    return render(
        request,
        templates,
        "tools/ssl.html",
        {"slug": "ssl", "default_port": 443},
    )


@router.post("/api/ssl")
async def api_ssl(request: Request):
    started = time.perf_counter()
    client_ip = get_client_ip(request)
    require_rate(client_ip, "ssl", 10)
    try:
        body = await request.json()
    except Exception as exc:
        raise AppError("INVALID_INPUT", "INVALID_INPUT") from exc
    if not isinstance(body, dict):
        raise AppError("INVALID_INPUT", "INVALID_INPUT")

    host = parse_host(body.get("host", ""))
    port = 443
    raw_port = body.get("port")
    if raw_port is not None:
        port = parse_port(raw_port)

    try:
        data = await async_with_timeout(
            check_ssl(host, port, settings.ssl_connect_timeout_s),
            settings.ssl_connect_timeout_s + 5.0,
        )
    except TimeoutError as exc:
        raise AppError("TIMEOUT", "TIMEOUT", status=504) from exc
    return json_ok(data, started)
