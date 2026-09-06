from __future__ import annotations

import time

from fastapi import Request
from fastapi.templating import Jinja2Templates

from core.config import settings
from core.i18n import all_strings, t
from core.paths import TEMPLATES_DIR

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def get_lang(request: Request) -> str:
    q = request.query_params.get("lang")
    if q in ("th", "en"):
        return q
    return request.cookies.get("lang") or settings.default_lang


def render(
    request: Request, templates: Jinja2Templates, name: str, ctx: dict | None = None
):
    lang = get_lang(request)
    theme = request.cookies.get("theme", "light")
    context = {
        "request": request,
        "lang": lang,
        "theme": theme,
        "t": t,
        "all_strings": all_strings,
        **(ctx or {}),
    }
    return templates.TemplateResponse(request, name, context)


def json_ok(data, started: float | None = None) -> dict:
    duration_ms = 0
    if started is not None:
        duration_ms = int((time.perf_counter() - started) * 1000)
    return {"ok": True, "data": data, "duration_ms": duration_ms}
