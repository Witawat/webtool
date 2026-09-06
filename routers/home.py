from __future__ import annotations

from fastapi import APIRouter, Request

from core.config import TOOLS
from core.errors import AppError

from . import render, templates

router = APIRouter()


@router.get("/")
async def index(request: Request):
    return render(
        request,
        templates,
        "home.html",
        {"tools": TOOLS, "tool_count": len(TOOLS)},
    )


@router.get("/tools/{slug}")
async def tool_page(request: Request, slug: str):
    known = {tool["slug"] for tool in TOOLS}
    if slug not in known:
        raise AppError("NOT_FOUND", "NOT_FOUND", status=404)
    template_name = f"tools/{slug}.html"
    try:
        templates.env.get_template(template_name)
    except Exception as exc:  # noqa: BLE001 - template missing means not built yet
        raise AppError("NOT_FOUND", "NOT_FOUND", status=404) from exc
    return render(request, templates, template_name, {"slug": slug})


@router.get("/healthz")
async def healthz():
    return {"status": "ok"}
