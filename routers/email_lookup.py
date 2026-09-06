from __future__ import annotations

import time

from fastapi import APIRouter, Request

from core.config import settings
from core.errors import AppError
from core.rate_limit import get_client_ip, require_rate
from core.timeout import async_with_timeout
from core.validation import parse_email
from services.providers.email import reverse_email_lookup

from . import json_ok, render, templates

router = APIRouter()


@router.get("/tools/email-lookup")
async def page(request: Request):
    return render(
        request,
        templates,
        "tools/email-lookup.html",
        {
            "slug": "email-lookup",
            "email_enabled": bool(settings.email_api_key),
        },
    )


@router.post("/api/email-lookup")
async def api_email_lookup(request: Request):
    started = time.perf_counter()
    client_ip = get_client_ip(request)
    require_rate(client_ip, "email-lookup", 3)
    try:
        body = await request.json()
    except Exception as exc:
        raise AppError("INVALID_INPUT", "INVALID_INPUT") from exc
    if not isinstance(body, dict):
        raise AppError("INVALID_INPUT", "INVALID_INPUT")

    email = parse_email(body.get("email", ""))
    try:
        data = await async_with_timeout(
            reverse_email_lookup(email, 10.0), 15.0
        )
    except TimeoutError as exc:
        raise AppError("TIMEOUT", "TIMEOUT", status=504) from exc
    return json_ok(data, started)
