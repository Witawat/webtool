from __future__ import annotations

import time

from fastapi import APIRouter, Request

from core.errors import AppError
from core.rate_limit import get_client_ip, require_rate
from core.timeout import async_with_timeout
from services.my_ip import get_my_ip

from . import json_ok, render, templates

router = APIRouter()


@router.get("/tools/my-ip")
async def page(request: Request):
    return render(request, templates, "tools/my-ip.html", {"slug": "my-ip"})


@router.post("/api/my-ip")
async def api_my_ip(request: Request):
    started = time.perf_counter()
    ip = get_client_ip(request)
    require_rate(ip, "my-ip", 60)
    try:
        data = await async_with_timeout(get_my_ip(ip), 10.0)
    except TimeoutError as exc:
        raise AppError("TIMEOUT", "TIMEOUT", status=504) from exc
    return json_ok(data, started)
