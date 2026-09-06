from __future__ import annotations

import time

from fastapi import APIRouter, Request

from core.config import settings
from core.errors import AppError
from core.rate_limit import get_client_ip, require_rate
from core.timeout import async_with_timeout
from core.validation import parse_domain
from services.email_dns import analyze_email_dns

from . import json_ok, render, templates

router = APIRouter()


@router.get("/tools/email-dns")
async def page(request: Request):
    return render(request, templates, "tools/email-dns.html", {"slug": "email-dns"})


@router.post("/api/email-dns")
async def api_email_dns(request: Request):
    started = time.perf_counter()
    client_ip = get_client_ip(request)
    require_rate(client_ip, "email-dns", 30)
    try:
        body = await request.json()
    except Exception as exc:
        raise AppError("INVALID_INPUT", "INVALID_INPUT") from exc
    if not isinstance(body, dict):
        raise AppError("INVALID_INPUT", "INVALID_INPUT")

    domain = parse_domain(body.get("domain", ""))
    try:
        data = await async_with_timeout(
            analyze_email_dns(domain, settings.dns_timeout_s),
            settings.dns_timeout_s * 3 + 10.0,
        )
    except TimeoutError as exc:
        raise AppError("TIMEOUT", "TIMEOUT", status=504) from exc
    return json_ok(data, started)
