from __future__ import annotations

import time

from fastapi import APIRouter, Request

from core.config import settings
from core.errors import AppError
from core.rate_limit import get_client_ip, require_rate
from core.timeout import async_with_timeout
from services.header_checker import check_headers

from . import json_ok, render, templates

router = APIRouter()


@router.get("/tools/header")
async def page(request: Request):
    return render(request, templates, "tools/header.html", {"slug": "header"})


@router.post("/api/header")
async def api_header(request: Request):
    started = time.perf_counter()
    client_ip = get_client_ip(request)
    require_rate(client_ip, "header", 10)
    try:
        body = await request.json()
    except Exception as exc:
        raise AppError("INVALID_INPUT", "INVALID_INPUT") from exc
    if not isinstance(body, dict):
        raise AppError("INVALID_INPUT", "INVALID_INPUT")

    url = str(body.get("url", "")).strip()
    try:
        data = await async_with_timeout(
            check_headers(url, settings.http_timeout_s),
            settings.http_timeout_s + 5.0,
        )
    except TimeoutError as exc:
        raise AppError("TIMEOUT", "TIMEOUT", status=504) from exc
    return json_ok(data, started)
