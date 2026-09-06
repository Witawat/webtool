from __future__ import annotations

import time

from fastapi import APIRouter, Request

from core.config import settings
from core.errors import AppError
from core.rate_limit import get_client_ip, require_rate
from core.timeout import async_with_timeout
from core.validation import parse_host
from services.dns_lookup import DEFAULT_TYPES, VALID_TYPES, lookup_dns

from . import json_ok, render, templates

router = APIRouter()


@router.get("/tools/dns")
async def page(request: Request):
    return render(
        request,
        templates,
        "tools/dns.html",
        {"slug": "dns", "all_types": VALID_TYPES, "default_types": DEFAULT_TYPES},
    )


@router.post("/api/dns")
async def api_dns(request: Request):
    started = time.perf_counter()
    client_ip = get_client_ip(request)
    require_rate(client_ip, "dns", 30)
    try:
        body = await request.json()
    except Exception as exc:
        raise AppError("INVALID_INPUT", "INVALID_INPUT") from exc
    if not isinstance(body, dict):
        raise AppError("INVALID_INPUT", "INVALID_INPUT")
    host = parse_host(body.get("domain", ""))

    types = body.get("types")
    if types is None:
        types = list(DEFAULT_TYPES)
    elif isinstance(types, list) and types:
        types = [t.upper() for t in types]
        if not all(t in VALID_TYPES for t in types):
            raise AppError("INVALID_INPUT", "INVALID_INPUT", field="types")
    else:
        raise AppError("INVALID_INPUT", "INVALID_INPUT", field="types")

    try:
        data = await async_with_timeout(
            lookup_dns(host, types, settings.dns_timeout_s),
            settings.dns_timeout_s + 5.0,
        )
    except TimeoutError as exc:
        raise AppError("TIMEOUT", "TIMEOUT", status=504) from exc
    return json_ok(data, started)
