from __future__ import annotations

import time

from fastapi import APIRouter, Request

from core.errors import AppError
from core.rate_limit import get_client_ip, require_rate
from core.validation import parse_cidr
from services.subnet_calc import calculate_subnet

from . import json_ok, render, templates

router = APIRouter()


@router.get("/tools/subnet-calc")
async def page(request: Request):
    return render(request, templates, "tools/subnet-calc.html", {"slug": "subnet-calc"})


@router.post("/api/subnet-calc")
async def api_subnet_calc(request: Request):
    started = time.perf_counter()
    client_ip = get_client_ip(request)
    require_rate(client_ip, "subnet-calc", 60)
    try:
        body = await request.json()
    except Exception as exc:
        raise AppError("INVALID_INPUT", "INVALID_INPUT") from exc
    if not isinstance(body, dict):
        raise AppError("INVALID_INPUT", "INVALID_INPUT")
    net = parse_cidr(body.get("cidr", ""))
    data = calculate_subnet(net)
    return json_ok(data, started)
