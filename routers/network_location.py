from __future__ import annotations

import ipaddress
import time

from fastapi import APIRouter, Request

from core.config import settings
from core.errors import AppError
from core.rate_limit import get_client_ip, require_rate
from core.timeout import async_with_timeout
from core.validation import is_forbidden_ip, parse_domain, resolve_host_ips
from services.providers.geoip import lookup as geoip_lookup

from . import json_ok, render, templates

router = APIRouter()


@router.get("/tools/network-location")
async def page(request: Request):
    return render(
        request,
        templates,
        "tools/network-location.html",
        {"slug": "network-location"},
    )


@router.post("/api/network-location")
async def api_network_location(request: Request):
    started = time.perf_counter()
    client_ip = get_client_ip(request)
    require_rate(client_ip, "network-location", 10)
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
        ip_obj = ipaddress.ip_address(query)
        if is_forbidden_ip(ip_obj):
            raise AppError("SSRF_BLOCKED", "SSRF_BLOCKED", field="query")
    except ValueError:
        domain = parse_domain(query)
        resolved = await resolve_host_ips(domain)
        for ip_str in resolved:
            if is_forbidden_ip(ipaddress.ip_address(ip_str)):
                raise AppError("SSRF_BLOCKED", "SSRF_BLOCKED", field="query") from None

    try:
        data = await async_with_timeout(
            geoip_lookup(query, settings.geoip_timeout_s),
            settings.geoip_timeout_s + 5.0,
        )
    except TimeoutError as exc:
        raise AppError("TIMEOUT", "TIMEOUT", status=504) from exc
    if data is None:
        raise AppError("NOT_FOUND", "NOT_FOUND", field="query")
    return json_ok(data, started)
