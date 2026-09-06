from __future__ import annotations

import time

from fastapi import APIRouter, Request

from core.config import settings
from core.errors import AppError
from core.rate_limit import get_client_ip, require_rate
from core.timeout import async_with_timeout
from services.fetch_http import fetch_url

from . import json_ok, render, templates

router = APIRouter()

ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}


@router.get("/tools/fetch")
async def page(request: Request):
    return render(
        request,
        templates,
        "tools/fetch.html",
        {"slug": "fetch", "methods": sorted(ALLOWED_METHODS)},
    )


@router.post("/api/fetch")
async def api_fetch(request: Request):
    started = time.perf_counter()
    client_ip = get_client_ip(request)
    require_rate(client_ip, "fetch", 10)
    try:
        body = await request.json()
    except Exception as exc:
        raise AppError("INVALID_INPUT", "INVALID_INPUT") from exc
    if not isinstance(body, dict):
        raise AppError("INVALID_INPUT", "INVALID_INPUT")

    method = str(body.get("method", "GET")).upper()
    if method not in ALLOWED_METHODS:
        raise AppError("INVALID_INPUT", "INVALID_INPUT", field="method")
    url = str(body.get("url", "")).strip()
    headers = body.get("headers") or {}
    if not isinstance(headers, dict):
        raise AppError("INVALID_INPUT", "INVALID_INPUT", field="headers")
    headers = {str(k): str(v) for k, v in headers.items()}
    body_str = body.get("body")
    if body_str is not None and not isinstance(body_str, str):
        raise AppError("INVALID_INPUT", "INVALID_INPUT", field="body")
    follow = bool(body.get("follow_redirects", True))

    try:
        data = await async_with_timeout(
            fetch_url(
                method,
                url,
                headers,
                body_str,
                follow,
                settings.http_timeout_s,
                settings.http_max_body,
                settings.http_max_redirects,
            ),
            settings.http_timeout_s + 5.0,
        )
    except TimeoutError as exc:
        raise AppError("TIMEOUT", "TIMEOUT", status=504) from exc
    return json_ok(data, started)
