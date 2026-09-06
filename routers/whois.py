from __future__ import annotations

import time

from fastapi import APIRouter, Request

from core.config import settings
from core.errors import AppError
from core.rate_limit import get_client_ip, require_rate
from core.timeout import async_with_timeout
from core.validation import parse_domain
from services.whois import lookup_whois

from . import json_ok, render, templates

router = APIRouter()


@router.get("/tools/whois")
async def page(request: Request):
    return render(request, templates, "tools/whois.html", {"slug": "whois"})


@router.post("/api/whois")
async def api_whois(request: Request):
    started = time.perf_counter()
    client_ip = get_client_ip(request)
    require_rate(client_ip, "whois", 10)
    try:
        body = await request.json()
    except Exception as exc:
        raise AppError("INVALID_INPUT", "INVALID_INPUT") from exc
    if not isinstance(body, dict):
        raise AppError("INVALID_INPUT", "INVALID_INPUT")

    domain = parse_domain(body.get("domain", ""))
    try:
        data = await async_with_timeout(
            lookup_whois(domain, settings.whois_timeout_s),
            settings.whois_timeout_s + 5.0,
        )
    except TimeoutError as exc:
        raise AppError("TIMEOUT", "TIMEOUT", status=504) from exc
    return json_ok(data, started)
