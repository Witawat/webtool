from __future__ import annotations

import time

from fastapi import APIRouter, Request

from core.errors import AppError
from core.rate_limit import get_client_ip, require_rate
from core.timeout import async_with_timeout
from services.bulk import BULK_HANDLERS, run_bulk

from . import get_lang, json_ok, render, templates

router = APIRouter()


@router.get("/tools/bulk")
async def page(request: Request):
    return render(
        request,
        templates,
        "tools/bulk.html",
        {"slug": "bulk", "bulk_slugs": sorted(BULK_HANDLERS)},
    )


@router.post("/api/bulk")
async def api_bulk(request: Request):
    started = time.perf_counter()
    client_ip = get_client_ip(request)
    require_rate(client_ip, "bulk", 5)
    try:
        body = await request.json()
    except Exception as exc:
        raise AppError("INVALID_INPUT", "INVALID_INPUT") from exc
    if not isinstance(body, dict):
        raise AppError("INVALID_INPUT", "INVALID_INPUT")

    slug = str(body.get("slug", ""))
    values = body.get("values")
    if not isinstance(values, list):
        raise AppError("INVALID_INPUT", "INVALID_INPUT", field="values")

    lang = get_lang(request)
    try:
        data = await async_with_timeout(run_bulk(slug, values, lang), 90.0)
    except TimeoutError as exc:
        raise AppError("TIMEOUT", "TIMEOUT", status=504) from exc
    return json_ok(data, started)
