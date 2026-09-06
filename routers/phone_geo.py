from __future__ import annotations

import time

from fastapi import APIRouter, Request

from core.errors import AppError
from core.rate_limit import get_client_ip, require_rate
from services.phone_geo import lookup_phone

from . import json_ok, render, templates

router = APIRouter()


@router.get("/tools/phone")
async def page(request: Request):
    return render(request, templates, "tools/phone.html", {"slug": "phone"})


@router.post("/api/phone")
async def api_phone(request: Request):
    started = time.perf_counter()
    client_ip = get_client_ip(request)
    require_rate(client_ip, "phone", 20)
    try:
        body = await request.json()
    except Exception as exc:
        raise AppError("INVALID_INPUT", "INVALID_INPUT") from exc
    if not isinstance(body, dict):
        raise AppError("INVALID_INPUT", "INVALID_INPUT")

    number = str(body.get("number", "")).strip()
    if not number:
        raise AppError("INVALID_INPUT", "INVALID_INPUT", field="number")
    country = body.get("country")
    if country is not None:
        country = str(country).strip().upper() or None

    data = lookup_phone(number, country)
    return json_ok(data, started)
