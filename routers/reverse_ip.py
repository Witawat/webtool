from __future__ import annotations

import ipaddress
import time

from fastapi import APIRouter, Request

from core.config import settings
from core.errors import AppError
from core.rate_limit import get_client_ip, require_rate
from core.timeout import async_with_timeout
from core.validation import is_forbidden_ip, parse_ip
from services.providers.reverse_ip import reverse_ip_lookup

from . import json_ok, render, templates

router = APIRouter()


@router.get("/tools/reverse-ip")
async def page(request: Request):
    return render(request, templates, "tools/reverse-ip.html", {"slug": "reverse-ip"})


@router.post("/api/reverse-ip")
async def api_reverse_ip(request: Request):
    started = time.perf_counter()
    client_ip = get_client_ip(request)
    require_rate(client_ip, "reverse-ip", 3)
    try:
        body = await request.json()
    except Exception as exc:
        raise AppError("INVALID_INPUT", "INVALID_INPUT") from exc
    if not isinstance(body, dict):
        raise AppError("INVALID_INPUT", "INVALID_INPUT")

    ip = str(parse_ip(body.get("ip", "")))
    if is_forbidden_ip(ipaddress.ip_address(ip)):
        raise AppError("SSRF_BLOCKED", "SSRF_BLOCKED", field="ip")

    try:
        data = await async_with_timeout(
            reverse_ip_lookup(
                ip, settings.http_timeout_s, settings.hackertarget_key
            ),
            settings.http_timeout_s + 5.0,
        )
    except TimeoutError as exc:
        raise AppError("TIMEOUT", "TIMEOUT", status=504) from exc
    return json_ok(data, started)
