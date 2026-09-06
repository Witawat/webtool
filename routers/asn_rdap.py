from __future__ import annotations

import ipaddress
import time

from fastapi import APIRouter, Request

from core.config import settings
from core.errors import AppError
from core.rate_limit import get_client_ip, require_rate
from core.timeout import async_with_timeout
from services.rdap_asn import lookup_asn, lookup_ip

from . import json_ok, render, templates

router = APIRouter()

MAX_ASN = 4294967295


@router.get("/tools/asn-rdap")
async def page(request: Request):
    return render(request, templates, "tools/asn-rdap.html", {"slug": "asn-rdap"})


@router.post("/api/asn-rdap")
async def api_asn_rdap(request: Request):
    started = time.perf_counter()
    client_ip = get_client_ip(request)
    require_rate(client_ip, "asn-rdap", 20)
    try:
        body = await request.json()
    except Exception as exc:
        raise AppError("INVALID_INPUT", "INVALID_INPUT") from exc
    if not isinstance(body, dict):
        raise AppError("INVALID_INPUT", "INVALID_INPUT")

    query = str(body.get("query", "")).strip()
    if not query:
        raise AppError("INVALID_INPUT", "INVALID_INPUT", field="query")

    try:
        ipaddress.ip_address(query)
    except ValueError:
        try:
            asn = int(query)
        except ValueError as exc:
            raise AppError("INVALID_INPUT", "INVALID_INPUT", field="query") from exc
        if not 1 <= asn <= MAX_ASN:
            raise AppError("INVALID_INPUT", "INVALID_INPUT", field="query") from None
        coro = lookup_asn(asn, settings.http_timeout_s)
    else:
        coro = lookup_ip(query, settings.http_timeout_s)

    try:
        data = await async_with_timeout(coro, settings.http_timeout_s + 5.0)
    except TimeoutError as exc:
        raise AppError("TIMEOUT", "TIMEOUT", status=504) from exc
    return json_ok(data, started)
