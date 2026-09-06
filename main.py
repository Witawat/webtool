import logging
import sys

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.config import settings
from core.errors import AppError
from core.i18n import t
from core.paths import LOGS_DIR, STATIC_DIR, TEMPLATES_DIR
from routers import (
    asn_rdap,
    bulk,
    dns_lookup,
    email_dns,
    email_lookup,
    fetch_http,
    header_checker,
    home,
    my_ip,
    network_location,
    phone_geo,
    ping,
    port_checker,
    port_scan,
    reverse_ip,
    ssl_checker,
    subnet_calc,
    traceroute,
    whois,
)

ROUTER_MODULES = [
    asn_rdap,
    bulk,
    dns_lookup,
    email_dns,
    email_lookup,
    fetch_http,
    header_checker,
    my_ip,
    network_location,
    phone_geo,
    ping,
    port_checker,
    port_scan,
    reverse_ip,
    ssl_checker,
    subnet_calc,
    traceroute,
    whois,
]

logger = logging.getLogger("webtool")

_LOGGING_SETUP = False


def _setup_file_logging() -> None:
    global _LOGGING_SETUP
    if _LOGGING_SETUP:
        return
    if not getattr(sys, "frozen", False):
        return
    try:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(LOGS_DIR / "app.log", encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        )
        root = logging.getLogger()
        root.setLevel(logging.INFO)
        root.addHandler(handler)
        _LOGGING_SETUP = True
    except Exception:
        pass


_setup_file_logging()
logger.info("main imported (frozen=%s)", getattr(sys, "frozen", False))

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version=settings.version)

    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    for mod in ROUTER_MODULES:
        if hasattr(mod, "router"):
            app.include_router(mod.router)
    app.include_router(home.router)

    @app.exception_handler(AppError)
    async def _app_error_handler(request: Request, exc: AppError):
        from routers import get_lang

        return JSONResponse(
            status_code=exc.status,
            content={"ok": False, "error": exc.to_dict(get_lang(request))},
        )

    @app.exception_handler(Exception)
    async def _generic_error_handler(request: Request, exc: Exception):
        logger.exception(
            "Unhandled error on %s %s", request.method, request.url.path
        )
        from routers import get_lang

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": {
                    "code": "INTERNAL",
                    "message": t(get_lang(request), "err.INTERNAL"),
                },
            },
        )

    return app


app = create_app()


def _run() -> None:
    import argparse
    import os
    import threading
    import webbrowser

    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")  # noqa: SIM115
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")  # noqa: SIM115

    _setup_file_logging()
    logger.info("_run() called")

    parser = argparse.ArgumentParser(description="WebTool local server")
    parser.add_argument("--host", type=str, default=settings.host)
    parser.add_argument("--port", type=int, default=settings.port)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    if not args.no_browser and not args.headless:
        from contextlib import suppress

        def _open_browser() -> None:
            with suppress(Exception):
                webbrowser.open(f"http://127.0.0.1:{args.port}/")

        threading.Timer(1.0, _open_browser).start()

    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {"format": "%(asctime)s %(levelname)s %(message)s"},
            "access": {"format": "%(asctime)s %(levelname)s %(message)s"},
        },
        "handlers": {
            "default": {"class": "logging.StreamHandler", "formatter": "default"},
            "access": {"class": "logging.StreamHandler", "formatter": "access"},
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {"level": "INFO"},
            "uvicorn.access": {
                "handlers": ["access"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }
    if getattr(sys, "frozen", False):
        log_config["handlers"]["file"] = {
            "class": "logging.FileHandler",
            "filename": str(LOGS_DIR / "app.log"),
            "encoding": "utf-8",
            "formatter": "default",
        }
        log_config["loggers"]["uvicorn"]["handlers"].append("file")
        log_config["loggers"]["uvicorn.access"]["handlers"].append("file")

    import uvicorn

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info",
        log_config=log_config,
    )


if __name__ == "__main__":
    _run()
